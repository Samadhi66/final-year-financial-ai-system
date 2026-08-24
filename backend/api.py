from pathlib import Path
from datetime import datetime
import io
import math

import joblib
import numpy as np
import pandas as pd
from PIL import Image

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ocr_service import parse_receipt_text
from transaction_store import (
    save_transaction,
    get_all_transactions,
    get_latest_transaction,
    get_transaction_summary,
    delete_transaction,
    update_transaction,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"


# ============================================================
# 1. FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI-Powered Financial Intelligence System",
    description=(
        "Smart Budget Prediction, Behavioral Fraud Detection, "
        "Amount Prediction, Receipt OCR and Transaction Management API"
    ),
    version="3.0",
)


# ============================================================
# 2. CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 3. RECEIPT OCR ENGINE
# ============================================================

try:
    import easyocr

    ocr_reader = easyocr.Reader(
        ["en"],
        gpu=False,
    )

    print("Receipt OCR engine loaded successfully.")

except Exception as error:
    ocr_reader = None

    print(
        "Warning: Receipt OCR engine could not be loaded."
    )
    print("Reason:", error)


# ============================================================
# 4. LOAD AMOUNT PREDICTION MODEL
# ============================================================

try:
    prediction_model = joblib.load(
        MODELS_DIR / "best_random_forest_model.pkl"
    )

    print(
        "Legacy amount prediction model loaded successfully."
    )

except Exception as error:
    prediction_model = None

    print(
        "Warning: Legacy amount prediction model "
        "is temporarily unavailable."
    )
    print("Reason:", error)


# ============================================================
# 5. LOAD FINAL BUDGET PREDICTION MODEL
# ============================================================

try:
    budget_model = joblib.load(
        MODELS_DIR / "final_gradient_boosting_budget_model.pkl"
    )

    budget_features = joblib.load(
        MODELS_DIR / "final_budget_model_features.pkl"
    )

    print(
        "Final Gradient Boosting budget model "
        "loaded successfully."
    )

except Exception as error:
    budget_model = None
    budget_features = None

    print(
        "Warning: Budget prediction model could not be loaded."
    )
    print("Reason:", error)


# ============================================================
# 6. LOAD FINAL FRAUD DETECTION MODEL
# ============================================================

try:
    fraud_model = joblib.load(
        MODELS_DIR / "final_fraud_model.pkl"
    )

    fraud_features = joblib.load(
        MODELS_DIR / "final_fraud_model_features.pkl"
    )

    fraud_threshold = joblib.load(
        MODELS_DIR / "fraud_threshold.pkl"
    )

    print("Final fraud model loaded successfully.")
    print("Fraud threshold:", fraud_threshold)

except Exception as error:
    fraud_model = None
    fraud_features = None
    fraud_threshold = None

    print(
        "Warning: Final fraud model could not be loaded."
    )
    print("Reason:", error)


# ============================================================
# 7. PYDANTIC INPUT MODELS
# ============================================================

class PredictionInput(BaseModel):
    category: int
    merchant: int
    payment_method: int
    location: int

    month: int
    day: int
    is_weekend: int

    category_avg_amount: float
    merchant_frequency: int
    payment_impact: float


class BudgetPredictionInput(BaseModel):
    week_sin: float
    week_cos: float

    current_week_spending: float

    spending_1_week_ago: float
    spending_2_weeks_ago: float
    spending_3_weeks_ago: float
    spending_4_weeks_ago: float

    previous_2_week_avg: float
    previous_4_week_avg: float
    previous_8_week_avg: float

    current_transaction_count: int
    current_avg_transaction_amount: float
    current_fraud_count: int

    previous_transaction_count: int
    previous_avg_transaction_amount: float

    spending_change: float
    spending_change_percentage: float


class FraudInput(BaseModel):
    amount: float
    category: int
    merchant: int
    payment_method: int
    location: int


class TransactionInput(BaseModel):
    merchant: str
    amount: float
    transaction_date: str
    category: str
    source: str = "Manual"
    raw_ocr_text: str | None = None


class TransactionUpdateInput(BaseModel):
    merchant: str
    amount: float
    transaction_date: str
    category: str
    source: str = "Manual"
    raw_ocr_text: str | None = None


class AutoFraudTransactionInput(BaseModel):
    amount: float
    category: str
    merchant: str
    payment_method: int = 0
    location: int = 0


# ============================================================
# TRANSACTION VALIDATION HELPERS
# ============================================================

ALLOWED_TRANSACTION_CATEGORIES = {
    "Food & Dining",
    "Groceries",
    "Transport",
    "Shopping",
    "Utilities",
    "Entertainment",
    "Healthcare",
    "Education",
    "Travel",
    "Other",
}

MAX_TRANSACTION_AMOUNT = 10_000_000.0
MIN_MERCHANT_LENGTH = 2
MAX_MERCHANT_LENGTH = 120


def normalize_text(value: str) -> str:
    return " ".join(str(value).strip().split())


def validate_transaction_fields(
    merchant: str,
    amount: float,
    transaction_date: str,
    category: str,
):
    merchant = normalize_text(merchant)
    transaction_date = normalize_text(transaction_date)
    category = normalize_text(category)

    if not merchant:
        raise HTTPException(
            status_code=400,
            detail="Merchant is required.",
        )

    if len(merchant) < MIN_MERCHANT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=(
                "Merchant name must contain at least "
                f"{MIN_MERCHANT_LENGTH} characters."
            ),
        )

    if len(merchant) > MAX_MERCHANT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=(
                "Merchant name is too long. "
                f"Maximum length is {MAX_MERCHANT_LENGTH} characters."
            ),
        )

    if not np.isfinite(float(amount)):
        raise HTTPException(
            status_code=400,
            detail="Transaction amount must be a finite number.",
        )

    if float(amount) <= 0:
        raise HTTPException(
            status_code=400,
            detail="Transaction amount must be greater than 0.",
        )

    if float(amount) > MAX_TRANSACTION_AMOUNT:
        raise HTTPException(
            status_code=400,
            detail=(
                "Transaction amount is unrealistically high. "
                f"Maximum accepted amount is Rs. {MAX_TRANSACTION_AMOUNT:,.2f}."
            ),
        )

    if not transaction_date:
        raise HTTPException(
            status_code=400,
            detail="Transaction date is required.",
        )

    try:
        parsed_date = datetime.strptime(
            transaction_date,
            "%d/%m/%Y",
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=(
                "Transaction date must use DD/MM/YYYY format "
                "and must be a valid calendar date."
            ),
        )

    if parsed_date.year < 2000 or parsed_date.year > 2100:
        raise HTTPException(
            status_code=400,
            detail=(
                "Transaction date year must be between "
                "2000 and 2100."
            ),
        )

    if not category:
        raise HTTPException(
            status_code=400,
            detail="Category is required.",
        )

    if category not in ALLOWED_TRANSACTION_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid category. Allowed categories are: "
                + ", ".join(
                    sorted(ALLOWED_TRANSACTION_CATEGORIES)
                )
                + "."
            ),
        )

    return {
        "merchant": merchant,
        "amount": round(float(amount), 2),
        "transaction_date": transaction_date,
        "category": category,
    }


# ============================================================
# FRAUD ENCODING HELPERS
# ============================================================

def category_to_code(category: str) -> int:
    category_map = {
        "food & dining": 1,
        "groceries": 2,
        "transport": 3,
        "shopping": 4,
        "utilities": 5,
        "entertainment": 6,
        "healthcare": 7,
        "education": 8,
        "travel": 9,
        "other": 0,
    }

    return category_map.get(
        str(category).strip().lower(),
        0,
    )


def merchant_to_code(merchant: str) -> int:
    """
    Convert merchant name into a stable numeric code.
    The same merchant name always produces the same code.

    IMPORTANT:
    This encoding should be aligned with the merchant encoding
    used during model training for production-quality predictions.
    """

    merchant = str(merchant).strip().lower()

    if not merchant:
        return 0

    return sum(ord(char) for char in merchant) % 100



# ============================================================
# AUTO BUDGET FEATURE HELPERS
# ============================================================

def parse_transaction_date(value):
    try:
        return datetime.strptime(
            str(value).strip(),
            "%d/%m/%Y",
        )
    except (TypeError, ValueError):
        return None


def start_of_week(value):
    return value.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    ) - pd.Timedelta(
        days=value.weekday()
    )


def _safe_average(values, fallback=0.0):
    cleaned = [
        float(value)
        for value in values
        if value is not None
        and np.isfinite(float(value))
    ]

    if not cleaned:
        return float(fallback)

    return float(
        sum(cleaned) / len(cleaned)
    )


def _transaction_fraud_flag(transaction):
    try:
        auto_input = AutoFraudTransactionInput(
            amount=float(
                transaction.get("amount", 0)
            ),
            category=str(
                transaction.get("category", "Other")
            ),
            merchant=str(
                transaction.get("merchant", "Unknown")
            ),
            payment_method=0,
            location=0,
        )

        result = auto_detect_fraud(
            auto_input
        )

        fraud_analysis = (
            result.get("fraud_analysis")
            if isinstance(result, dict)
            else None
        )

        if not fraud_analysis:
            return 0

        return int(
            fraud_analysis.get("fraud_status")
            == "Fraud Detected"
        )

    except Exception:
        return 0


def build_auto_budget_features():
    transactions = get_all_transactions()

    valid_transactions = []
    ignored_transaction_ids = []

    for transaction in transactions:
        parsed_date = parse_transaction_date(
            transaction.get("transaction_date")
        )

        try:
            amount = float(
                transaction.get("amount", 0)
            )
        except (TypeError, ValueError):
            amount = 0.0

        if (
            parsed_date is None
            or not np.isfinite(amount)
            or amount <= 0
        ):
            ignored_transaction_ids.append(
                transaction.get("id")
            )
            continue

        valid_transactions.append(
            {
                **transaction,
                "_date": parsed_date,
                "_amount": amount,
                "_week_start":
                    start_of_week(parsed_date),
            }
        )

    if not valid_transactions:
        return {
            "status": "Insufficient Data",
            "can_predict": False,
            "message": (
                "No valid saved transaction history is available "
                "for automatic budget forecasting."
            ),
            "features": None,
            "history": {
                "valid_transaction_count": 0,
                "ignored_transaction_ids":
                    ignored_transaction_ids,
                "observed_week_count": 0,
                "imputed_week_count": 0,
                "history_quality": "Insufficient",
            },
            "warnings": [
                (
                    "Save valid transactions with DD/MM/YYYY dates "
                    "before generating an automatic budget forecast."
                )
            ],
        }

    latest_date = max(
        item["_date"]
        for item in valid_transactions
    )

    reference_week = start_of_week(
        latest_date
    )

    weekly = {}

    for item in valid_transactions:
        week_start = item["_week_start"]

        if week_start not in weekly:
            weekly[week_start] = {
                "spending": 0.0,
                "count": 0,
                "amounts": [],
                "transactions": [],
            }

        weekly[week_start]["spending"] += item["_amount"]
        weekly[week_start]["count"] += 1
        weekly[week_start]["amounts"].append(item["_amount"])
        weekly[week_start]["transactions"].append(item)

    def week_bucket(offset):
        target_week = (
            reference_week
            - pd.Timedelta(weeks=offset)
        )
        return weekly.get(target_week)

    current_bucket = (
        week_bucket(0)
        or {
            "spending": 0.0,
            "count": 0,
            "amounts": [],
            "transactions": [],
        }
    )

    observed_historical_spending = [
        bucket["spending"]
        for week_start, bucket in weekly.items()
        if week_start < reference_week
    ]

    if observed_historical_spending:
        historical_fallback = _safe_average(
            observed_historical_spending
        )
    else:
        historical_fallback = float(
            current_bucket["spending"]
        )

    if historical_fallback <= 0:
        historical_fallback = 1.0

    imputed_offsets = []
    lag_spending = {}

    for offset in range(1, 9):
        bucket = week_bucket(offset)

        if bucket is None:
            lag_spending[offset] = historical_fallback
            imputed_offsets.append(offset)
        else:
            lag_spending[offset] = float(
                bucket["spending"]
            )

    current_spending = float(
        current_bucket["spending"]
    )

    current_transaction_count = int(
        current_bucket["count"]
    )

    current_avg_amount = _safe_average(
        current_bucket["amounts"],
        fallback=0.0,
    )

    previous_bucket = week_bucket(1)

    if previous_bucket is None:
        previous_transaction_count = 0
        previous_avg_amount = historical_fallback
    else:
        previous_transaction_count = int(
            previous_bucket["count"]
        )
        previous_avg_amount = _safe_average(
            previous_bucket["amounts"],
            fallback=historical_fallback,
        )

    current_fraud_count = sum(
        _transaction_fraud_flag(transaction)
        for transaction
        in current_bucket["transactions"]
    )

    previous_2_week_avg = _safe_average(
        [
            lag_spending[1],
            lag_spending[2],
        ],
        fallback=historical_fallback,
    )

    previous_4_week_avg = _safe_average(
        [
            lag_spending[1],
            lag_spending[2],
            lag_spending[3],
            lag_spending[4],
        ],
        fallback=historical_fallback,
    )

    previous_8_week_avg = _safe_average(
        [
            lag_spending[offset]
            for offset in range(1, 9)
        ],
        fallback=historical_fallback,
    )

    spending_change = (
        current_spending
        - lag_spending[1]
    )

    if lag_spending[1] == 0:
        spending_change_percentage = 0.0
    else:
        spending_change_percentage = (
            spending_change
            / lag_spending[1]
            * 100
        )

    iso_week = int(
        latest_date.isocalendar().week
    )

    seasonal_angle = (
        2 * math.pi * iso_week / 52.0
    )

    features = {
        "week_sin":
            round(math.sin(seasonal_angle), 6),
        "week_cos":
            round(math.cos(seasonal_angle), 6),

        "current_week_spending":
            round(current_spending, 2),

        "spending_1_week_ago":
            round(lag_spending[1], 2),
        "spending_2_weeks_ago":
            round(lag_spending[2], 2),
        "spending_3_weeks_ago":
            round(lag_spending[3], 2),
        "spending_4_weeks_ago":
            round(lag_spending[4], 2),

        "previous_2_week_avg":
            round(previous_2_week_avg, 2),
        "previous_4_week_avg":
            round(previous_4_week_avg, 2),
        "previous_8_week_avg":
            round(previous_8_week_avg, 2),

        "current_transaction_count":
            current_transaction_count,
        "current_avg_transaction_amount":
            round(current_avg_amount, 2),
        "current_fraud_count":
            int(current_fraud_count),

        "previous_transaction_count":
            previous_transaction_count,
        "previous_avg_transaction_amount":
            round(previous_avg_amount, 2),

        "spending_change":
            round(spending_change, 2),
        "spending_change_percentage":
            round(spending_change_percentage, 4),
    }

    observed_week_count = len(weekly)
    imputed_week_count = len(imputed_offsets)

    if observed_week_count >= 8:
        history_quality = "High"
    elif observed_week_count >= 4:
        history_quality = "Medium"
    else:
        history_quality = "Low"

    warnings = []

    if ignored_transaction_ids:
        warnings.append(
            (
                f"{len(ignored_transaction_ids)} saved transaction(s) "
                "were ignored because their date or amount was invalid."
            )
        )

    if imputed_week_count > 0:
        warnings.append(
            (
                f"{imputed_week_count} historical week(s) were missing. "
                "Those lag values were imputed using the average of "
                "available historical weekly spending. "
                "Forecast reliability will improve as more real "
                "transaction history is saved."
            )
        )

    return {
        "status": "Success",
        "can_predict": True,
        "message": (
            "Automatic budget features generated from "
            "saved transaction history."
        ),
        "features": features,
        "history": {
            "reference_week_start":
                reference_week.strftime("%d/%m/%Y"),
            "latest_transaction_date":
                latest_date.strftime("%d/%m/%Y"),
            "valid_transaction_count":
                len(valid_transactions),
            "ignored_transaction_ids":
                ignored_transaction_ids,
            "observed_week_count":
                observed_week_count,
            "imputed_week_count":
                imputed_week_count,
            "imputed_week_offsets":
                imputed_offsets,
            "history_quality":
                history_quality,
        },
        "warnings": warnings,
    }



# ============================================================
# AUTO AMOUNT PREDICTION HELPERS
# ============================================================

def build_auto_amount_features():
    """
    Build the legacy amount-prediction model features from the
    latest saved transaction plus saved transaction history.
    """

    latest = get_latest_transaction()
    transactions = get_all_transactions()

    if not latest:
        return {
            "status": "Insufficient Data",
            "can_predict": False,
            "message": (
                "No saved transaction is available for "
                "automatic amount prediction."
            ),
            "features": None,
            "transaction": None,
            "history": {
                "transaction_count": 0,
                "same_category_count": 0,
                "same_merchant_count": 0,
                "history_quality": "Insufficient",
            },
            "warnings": [
                "Save at least one valid transaction before running automatic amount prediction."
            ],
        }

    parsed_date = parse_transaction_date(
        latest.get("transaction_date")
    )

    if parsed_date is None:
        return {
            "status": "Insufficient Data",
            "can_predict": False,
            "message": (
                "The latest saved transaction does not have "
                "a valid DD/MM/YYYY date."
            ),
            "features": None,
            "transaction": latest,
            "history": {
                "transaction_count": len(transactions),
                "same_category_count": 0,
                "same_merchant_count": 0,
                "history_quality": "Insufficient",
            },
            "warnings": [
                "Edit the latest transaction and provide a valid DD/MM/YYYY date."
            ],
        }

    latest_category = str(
        latest.get("category", "Other")
    ).strip()

    latest_merchant = str(
        latest.get("merchant", "Unknown")
    ).strip()

    category_amounts = []
    same_merchant_count = 0

    for transaction in transactions:
        try:
            amount = float(
                transaction.get("amount", 0)
            )
        except (TypeError, ValueError):
            continue

        if not np.isfinite(amount) or amount <= 0:
            continue

        transaction_category = str(
            transaction.get("category", "Other")
        ).strip()

        transaction_merchant = str(
            transaction.get("merchant", "Unknown")
        ).strip()

        if (
            transaction_category.lower()
            == latest_category.lower()
        ):
            category_amounts.append(amount)

        if (
            transaction_merchant.lower()
            == latest_merchant.lower()
        ):
            same_merchant_count += 1

    if category_amounts:
        category_avg_amount = (
            sum(category_amounts)
            / len(category_amounts)
        )
    else:
        category_avg_amount = float(
            latest.get("amount", 0)
        )

    month = parsed_date.month
    day = parsed_date.day
    is_weekend = int(
        parsed_date.weekday() >= 5
    )

    # The current saved transaction schema does not yet store
    # payment method or location, so safe neutral defaults are used.
    payment_method = 0
    location = 0
    payment_impact = 1.0

    features = {
        "category": category_to_code(
            latest_category
        ),
        "merchant": merchant_to_code(
            latest_merchant
        ),
        "payment_method": payment_method,
        "location": location,
        "month": month,
        "day": day,
        "is_weekend": is_weekend,
        "category_avg_amount": round(
            float(category_avg_amount),
            2,
        ),
        "merchant_frequency": int(
            same_merchant_count
        ),
        "payment_impact": payment_impact,
    }

    valid_transaction_count = 0

    for transaction in transactions:
        try:
            amount = float(
                transaction.get("amount", 0)
            )
        except (TypeError, ValueError):
            continue

        if np.isfinite(amount) and amount > 0:
            valid_transaction_count += 1

    if valid_transaction_count >= 20:
        history_quality = "High"
    elif valid_transaction_count >= 5:
        history_quality = "Medium"
    else:
        history_quality = "Low"

    warnings = []

    if history_quality == "Low":
        warnings.append(
            (
                "Saved transaction history is currently limited. "
                "The automatic amount prediction should be treated "
                "as a preliminary estimate until more real transactions are saved."
            )
        )

    warnings.append(
        (
            "Payment method and location are not stored in the current "
            "transaction table, so neutral default codes are used for those features."
        )
    )

    return {
        "status": "Success",
        "can_predict": True,
        "message": (
            "Automatic amount-prediction features generated "
            "from the latest saved transaction and transaction history."
        ),
        "transaction": latest,
        "features": features,
        "history": {
            "transaction_count": valid_transaction_count,
            "same_category_count": len(category_amounts),
            "same_merchant_count": same_merchant_count,
            "history_quality": history_quality,
        },
        "warnings": warnings,
    }


# ============================================================
# 8. HOME ENDPOINT
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Financial AI API Running",
        "system": "AI-Powered Financial Intelligence System",
        "version": "3.0",
        "modules": [
            "Smart Budget Prediction",
            "Behavioral Fraud Detection",
            "Amount Prediction",
            "Receipt OCR Expense Entry",
            "Transaction Management",
            "Automatic Fraud Analysis",
            "Transaction Deletion",
            "Transaction Editing",
            "Advanced Input Validation",
            "Automatic Budget Forecasting",
            "Automatic Amount Prediction",
        ],
    }


# ============================================================
# 9. AMOUNT PREDICTION ENDPOINT
# ============================================================

@app.post("/predict_amount")
def predict_amount(data: PredictionInput):
    if prediction_model is None:
        return {
            "status": "Unavailable",
            "message": (
                "Legacy amount prediction model "
                "is temporarily unavailable."
            ),
        }

    try:
        input_data = pd.DataFrame(
            [data.model_dump()]
        )

        input_data = input_data[
            [
                "category",
                "merchant",
                "payment_method",
                "location",
                "month",
                "day",
                "is_weekend",
                "category_avg_amount",
                "merchant_frequency",
                "payment_impact",
            ]
        ]

        prediction = prediction_model.predict(
            input_data
        )

        return {
            "status": "Success",
            "predicted_amount": round(
                float(prediction[0]),
                2,
            ),
        }

    except Exception as error:
        return {
            "status": "Unavailable",
            "message": (
                "Legacy amount prediction could not be completed."
            ),
            "error": str(error),
        }



# ============================================================
# 10. AUTO AMOUNT FEATURES FROM SAVED TRANSACTIONS
# ============================================================

@app.get("/amount/auto-features")
def auto_amount_features():
    try:
        return build_auto_amount_features()

    except Exception as error:
        print(
            "Automatic amount feature error:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Automatic amount features could not be generated."
            ),
        )


# ============================================================
# 11. AUTO AMOUNT PREDICTION FROM LATEST SAVED TRANSACTION
# ============================================================

@app.post("/amount/auto-predict")
def auto_amount_prediction():
    if prediction_model is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Amount prediction model is temporarily unavailable."
            ),
        )

    try:
        feature_result = (
            build_auto_amount_features()
        )

        if not feature_result.get(
            "can_predict"
        ):
            return feature_result

        features = feature_result[
            "features"
        ]

        ordered_features = [
            "category",
            "merchant",
            "payment_method",
            "location",
            "month",
            "day",
            "is_weekend",
            "category_avg_amount",
            "merchant_frequency",
            "payment_impact",
        ]

        input_data = pd.DataFrame(
            [features]
        )[ordered_features]

        prediction = prediction_model.predict(
            input_data
        )

        predicted_amount = round(
            float(prediction[0]),
            2,
        )

        latest_amount = float(
            feature_result[
                "transaction"
            ].get("amount", 0)
        )

        difference = round(
            predicted_amount - latest_amount,
            2,
        )

        if latest_amount == 0:
            percentage_difference = 0.0
        else:
            percentage_difference = round(
                abs(difference)
                / latest_amount
                * 100,
                2,
            )

        if difference > 0:
            trend = "Higher Than Latest"
        elif difference < 0:
            trend = "Lower Than Latest"
        else:
            trend = "Similar To Latest"

        explanation = (
            "The predicted transaction amount was generated from "
            "the latest saved transaction together with category, "
            "merchant-frequency and calendar context."
        )

        if (
            feature_result["history"][
                "history_quality"
            ]
            == "Low"
        ):
            explanation += (
                " Transaction history is currently limited, "
                "so this result should be treated as a preliminary estimate."
            )

        return {
            "status": "Success",
            "message": (
                "Automatic amount prediction generated "
                "from saved transaction data."
            ),
            "source":
                "SQLite Saved Transactions",
            "predicted_amount":
                predicted_amount,
            "latest_transaction_amount":
                round(latest_amount, 2),
            "difference":
                difference,
            "percentage_difference":
                percentage_difference,
            "trend":
                trend,
            "explanation":
                explanation,
            "model":
                "Random Forest",
            "auto_features":
                features,
            "transaction":
                feature_result["transaction"],
            "history":
                feature_result["history"],
            "warnings":
                feature_result["warnings"],
        }

    except HTTPException:
        raise

    except Exception as error:
        print(
            "Automatic amount prediction error:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Automatic amount prediction could not be completed."
            ),
        )


# ============================================================
# 12. SMART BUDGET PREDICTION ENDPOINT
# ============================================================

@app.post("/predict_budget")
def predict_budget(data: BudgetPredictionInput):
    if (
        budget_model is None
        or budget_features is None
    ):
        return {
            "status": "Unavailable",
            "message": (
                "Budget prediction model "
                "is temporarily unavailable."
            ),
        }

    try:
        input_data = pd.DataFrame(
            [data.model_dump()]
        )

        input_data = input_data[
            budget_features
        ]

        prediction = budget_model.predict(
            input_data
        )

        predicted_budget = round(
            float(prediction[0]),
            2,
        )

        current_spending = (
            data.current_week_spending
        )

        difference = (
            predicted_budget
            - current_spending
        )

        if current_spending == 0:
            percentage_change = 0.0
        else:
            percentage_change = (
                abs(difference)
                / current_spending
                * 100
            )

        if difference > 0:
            trend = "Expected Increase"

            explanation = (
                "Next week's spending is predicted "
                f"to increase by approximately "
                f"{percentage_change:.2f}% compared "
                "with the current week."
            )

        elif difference < 0:
            trend = "Expected Decrease"

            explanation = (
                "Next week's spending is predicted "
                f"to decrease by approximately "
                f"{percentage_change:.2f}% compared "
                "with the current week."
            )

        else:
            trend = "Stable"

            explanation = (
                "Next week's spending is predicted "
                "to remain approximately stable."
            )

        return {
            "status": "Success",
            "predicted_next_week_spending":
                predicted_budget,
            "current_week_spending":
                round(current_spending, 2),
            "predicted_difference":
                round(difference, 2),
            "percentage_change":
                round(percentage_change, 2),
            "trend": trend,
            "explanation": explanation,
            "model": "Gradient Boosting",
            "model_r2": 0.5974,
            "model_mae": 4620.89,
            "model_rmse": 5457.08,
        }

    except Exception as error:
        return {
            "status": "Error",
            "message": (
                "Budget prediction could not be completed."
            ),
            "error": str(error),
        }



# ============================================================
# 13. AUTO BUDGET FEATURES FROM SAVED TRANSACTIONS
# ============================================================

@app.get("/budget/auto-features")
def auto_budget_features():
    try:
        return build_auto_budget_features()

    except Exception as error:
        print(
            "Automatic budget feature error:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Automatic budget features could not be generated."
            ),
        )


# ============================================================
# 14. AUTO BUDGET PREDICTION FROM SAVED TRANSACTIONS
# ============================================================

@app.post("/budget/auto-predict")
def auto_budget_prediction():
    if (
        budget_model is None
        or budget_features is None
    ):
        raise HTTPException(
            status_code=503,
            detail=(
                "Budget prediction model is temporarily unavailable."
            ),
        )

    try:
        feature_result = build_auto_budget_features()

        if not feature_result.get("can_predict"):
            return feature_result

        features = feature_result["features"]

        input_data = pd.DataFrame(
            [features]
        )

        missing_features = [
            feature
            for feature in budget_features
            if feature not in input_data.columns
        ]

        if missing_features:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Automatic budget feature generation "
                    "is missing required model features: "
                    + ", ".join(missing_features)
                ),
            )

        input_data = input_data[
            budget_features
        ]

        prediction = budget_model.predict(
            input_data
        )

        predicted_budget = round(
            float(prediction[0]),
            2,
        )

        current_spending = float(
            features["current_week_spending"]
        )

        difference = (
            predicted_budget
            - current_spending
        )

        if current_spending == 0:
            percentage_change = 0.0
        else:
            percentage_change = (
                abs(difference)
                / current_spending
                * 100
            )

        if difference > 0:
            trend = "Expected Increase"
            explanation = (
                "Based on saved transaction history, "
                "next week's spending is predicted to "
                f"increase by approximately "
                f"{percentage_change:.2f}%."
            )
        elif difference < 0:
            trend = "Expected Decrease"
            explanation = (
                "Based on saved transaction history, "
                "next week's spending is predicted to "
                f"decrease by approximately "
                f"{percentage_change:.2f}%."
            )
        else:
            trend = "Stable"
            explanation = (
                "Based on saved transaction history, "
                "next week's spending is predicted "
                "to remain approximately stable."
            )

        if (
            feature_result["history"]["history_quality"]
            == "Low"
        ):
            explanation += (
                " Historical coverage is currently low, "
                "so this forecast should be treated as "
                "a preliminary estimate."
            )

        return {
            "status": "Success",
            "message": (
                "Automatic budget forecast generated "
                "from saved transaction history."
            ),
            "source":
                "SQLite Saved Transactions",
            "predicted_next_week_spending":
                predicted_budget,
            "current_week_spending":
                round(current_spending, 2),
            "predicted_difference":
                round(difference, 2),
            "percentage_change":
                round(percentage_change, 2),
            "trend": trend,
            "explanation": explanation,
            "model":
                "Gradient Boosting",
            "model_r2": 0.5974,
            "model_mae": 4620.89,
            "model_rmse": 5457.08,
            "auto_features":
                features,
            "history":
                feature_result["history"],
            "warnings":
                feature_result["warnings"],
        }

    except HTTPException:
        raise

    except Exception as error:
        print(
            "Automatic budget prediction error:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Automatic budget prediction could not be completed."
            ),
        )


# ============================================================
# 15. FRAUD DETECTION ENDPOINT
# ============================================================

@app.post("/detect_fraud")
def detect_fraud(data: FraudInput):
    if (
        fraud_model is None
        or fraud_features is None
        or fraud_threshold is None
    ):
        return {
            "status": "Unavailable",
            "fraud_status": "Unavailable",
            "risk_level": "Unknown",
            "risk_reasons": [
                "Fraud detection model has not been loaded."
            ],
        }

    try:
        input_data = pd.DataFrame(
            [data.model_dump()]
        )

        # Temporary behavioral context
        input_data["month"] = 8
        input_data["day"] = 20
        input_data["is_weekend"] = 0

        input_data[
            "category_avg_amount"
        ] = data.amount

        input_data[
            "merchant_frequency"
        ] = 10

        input_data[
            "payment_impact"
        ] = 1.0

        input_data = input_data[
            fraud_features
        ]

        fraud_probability = (
            fraud_model
            .predict_proba(
                input_data
            )[0][1]
        )

        fraud_prediction = int(
            fraud_probability
            >= fraud_threshold
        )

        reasons = []

        if data.amount > 30000:
            reasons.append(
                "Transaction amount is unusually high "
                "compared with normal spending behaviour."
            )

        if data.payment_method == 2:
            reasons.append(
                "Payment method shows "
                "higher-risk behaviour."
            )

        if data.merchant > 20:
            reasons.append(
                "Merchant behaviour differs "
                "from normal transaction patterns."
            )

        if fraud_prediction == 1:
            fraud_status = "Fraud Detected"

            if fraud_probability >= 0.70:
                risk_level = "High"
            else:
                risk_level = "Medium"

            if len(reasons) == 0:
                reasons.append(
                    "The AI model detected unusual "
                    "transaction behaviour."
                )

        else:
            fraud_status = "Normal"
            risk_level = "Low"

            if len(reasons) == 0:
                reasons.append(
                    "Transaction behaviour matches "
                    "normal spending patterns."
                )

        return {
            "status": "Success",
            "fraud_status": fraud_status,
            "risk_level": risk_level,
            "fraud_probability": round(
                float(fraud_probability),
                4,
            ),
            "threshold": round(
                float(fraud_threshold),
                2,
            ),
            "risk_reasons": reasons,
            "model": "Random Forest Classifier",
        }

    except Exception as error:
        return {
            "status": "Error",
            "fraud_status": "Unavailable",
            "risk_level": "Unknown",
            "risk_reasons": [
                "Fraud detection could not be completed."
            ],
            "error": str(error),
        }


# ============================================================
# 16. AUTOMATIC FRAUD DETECTION FOR SAVED/OCR TRANSACTIONS
# ============================================================

@app.post("/auto_detect_fraud")
def auto_detect_fraud(
    data: AutoFraudTransactionInput
):
    try:
        category_code = category_to_code(
            data.category
        )

        merchant_code = merchant_to_code(
            data.merchant
        )

        fraud_input = FraudInput(
            amount=data.amount,
            category=category_code,
            merchant=merchant_code,
            payment_method=data.payment_method,
            location=data.location,
        )

        result = detect_fraud(
            fraud_input
        )

        if result.get("status") in {
            "Error",
            "Unavailable",
        }:
            return {
                "status": result.get(
                    "status",
                    "Error",
                ),
                "message": (
                    "Automatic fraud analysis "
                    "could not be completed."
                ),
                "transaction": {
                    "amount": data.amount,
                    "category": data.category,
                    "merchant": data.merchant,
                    "payment_method":
                        data.payment_method,
                    "location":
                        data.location,
                },
                "encoded_features": {
                    "category":
                        category_code,
                    "merchant":
                        merchant_code,
                },
                "fraud_analysis":
                    result,
            }

        return {
            "status": "Success",
            "message": (
                "Automatic fraud analysis "
                "completed successfully."
            ),
            "transaction": {
                "amount": data.amount,
                "category": data.category,
                "merchant": data.merchant,
                "payment_method":
                    data.payment_method,
                "location":
                    data.location,
            },
            "encoded_features": {
                "category":
                    category_code,
                "merchant":
                    merchant_code,
            },
            "fraud_analysis":
                result,
        }

    except Exception as error:
        print(
            "Automatic fraud analysis error:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Automatic fraud analysis failed."
            ),
        )


# ============================================================
# 17. RECEIPT OCR ENDPOINT
# ============================================================

@app.post("/ocr_receipt")
async def ocr_receipt(
    file: UploadFile = File(...)
):
    if ocr_reader is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Receipt OCR service is "
                "temporarily unavailable."
            ),
        )

    allowed_types = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid file type. "
                "Please upload a JPG, PNG or WEBP receipt image."
            ),
        )

    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Uploaded receipt image is empty."
                ),
            )

        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Receipt image is too large. "
                    "Maximum allowed size is 10 MB."
                ),
            )

        try:
            image = Image.open(
                io.BytesIO(contents)
            ).convert("RGB")

        except Exception:
            raise HTTPException(
                status_code=400,
                detail=(
                    "The uploaded file could not "
                    "be read as a valid image."
                ),
            )

        image_array = np.array(image)

        detected_lines = (
            ocr_reader.readtext(
                image_array,
                detail=0,
                paragraph=False,
            )
        )

        raw_text = "\n".join(
            detected_lines
        ).strip()

        if not raw_text:
            return {
                "status": "No Text Detected",
                "message": (
                    "No readable text could be detected "
                    "in the uploaded receipt."
                ),
                "filename": file.filename,
                "merchant": None,
                "amount": None,
                "date": None,
                "suggested_category": "Other",
                "raw_text": "",
                "requires_confirmation": True,
            }

        parsed_data = parse_receipt_text(
            raw_text
        )

        merchant = parsed_data.get("merchant")
        amount = parsed_data.get("amount")
        date = parsed_data.get("date")
        suggested_category = parsed_data.get(
            "suggested_category",
            "Other",
        )

        validation_warnings = []

        if not merchant:
            validation_warnings.append(
                "Merchant could not be detected reliably."
            )

        if (
            amount is None
            or not np.isfinite(float(amount))
            or float(amount) <= 0
        ):
            validation_warnings.append(
                "A valid transaction amount could not be detected."
            )

        if not date:
            validation_warnings.append(
                "Transaction date could not be detected."
            )
        else:
            try:
                datetime.strptime(
                    str(date).strip(),
                    "%d/%m/%Y",
                )
            except ValueError:
                validation_warnings.append(
                    "Detected date is not a valid DD/MM/YYYY date."
                )

        if (
            not suggested_category
            or suggested_category
            not in ALLOWED_TRANSACTION_CATEGORIES
        ):
            suggested_category = "Other"
            validation_warnings.append(
                "Category was uncertain and has been set to Other."
            )

        return {
            "status": "Success",
            "message": (
                "Receipt scanned successfully. "
                "Please confirm or edit the "
                "extracted information before saving."
            ),
            "filename": file.filename,
            "merchant": merchant,
            "amount": amount,
            "date": date,
            "suggested_category":
                suggested_category,
            "raw_text":
                parsed_data.get(
                    "raw_text",
                    raw_text,
                ),
            "requires_confirmation": True,
            "validation_warnings":
                validation_warnings,
            "is_complete":
                len(validation_warnings) == 0,
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Receipt OCR error:", error)

        raise HTTPException(
            status_code=500,
            detail=(
                "Receipt image could not be processed."
            ),
        )


# ============================================================
# 18. CREATE / SAVE TRANSACTION
# ============================================================

@app.post("/transactions")
def create_transaction(
    transaction: TransactionInput
):
    source = normalize_text(
        transaction.source
    )

    if not source:
        source = "Manual"

    validated = validate_transaction_fields(
        merchant=transaction.merchant,
        amount=transaction.amount,
        transaction_date=transaction.transaction_date,
        category=transaction.category,
    )

    try:
        save_result = save_transaction(
            merchant=validated["merchant"],
            amount=validated["amount"],
            transaction_date=validated[
                "transaction_date"
            ],
            category=validated["category"],
            source=source,
            raw_ocr_text=(
                transaction.raw_ocr_text
            ),
        )

        if save_result.get("duplicate"):
            return {
                "status": "Duplicate",
                "message": (
                    "This transaction already exists "
                    "and was not saved again."
                ),
                "duplicate": True,
                "transaction_id":
                    save_result.get(
                        "transaction_id"
                    ),
                "transaction":
                    save_result.get(
                        "transaction"
                    ),
            }

        return {
            "status": "Success",
            "message": (
                "Transaction saved successfully."
            ),
            "duplicate": False,
            "transaction_id":
                save_result.get(
                    "transaction_id"
                ),
        }

    except HTTPException:
        raise

    except Exception as error:
        print(
            "Transaction save error:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not save transaction."
            ),
        )


# ============================================================
# 19. GET ALL TRANSACTIONS
# ============================================================

@app.get("/transactions")
def list_transactions():
    try:
        transactions = (
            get_all_transactions()
        )

        return {
            "status": "Success",
            "count": len(transactions),
            "transactions": transactions,
        }

    except Exception as error:
        print(
            "Transaction retrieval error:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not retrieve transactions."
            ),
        )


# ============================================================
# 20. GET LATEST TRANSACTION
# ============================================================

@app.get("/transactions/latest")
def latest_transaction():
    try:
        transaction = (
            get_latest_transaction()
        )

        return {
            "status": "Success",
            "transaction": transaction,
        }

    except Exception as error:
        print(
            "Latest transaction error:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not retrieve latest transaction."
            ),
        )


# ============================================================
# 21. UPDATE TRANSACTION
# ============================================================

@app.put("/transactions/{transaction_id}")
def edit_transaction(
    transaction_id: int,
    transaction: TransactionUpdateInput
):
    if transaction_id <= 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Transaction ID must be "
                "greater than 0."
            ),
        )

    source = normalize_text(
        transaction.source
    )

    if not source:
        source = "Manual"

    validated = validate_transaction_fields(
        merchant=transaction.merchant,
        amount=transaction.amount,
        transaction_date=transaction.transaction_date,
        category=transaction.category,
    )

    try:
        result = update_transaction(
            transaction_id=transaction_id,
            merchant=validated["merchant"],
            amount=validated["amount"],
            transaction_date=validated[
                "transaction_date"
            ],
            category=validated["category"],
            source=source,
            raw_ocr_text=transaction.raw_ocr_text,
        )

        if not result.get("found"):
            raise HTTPException(
                status_code=404,
                detail="Transaction not found.",
            )

        if result.get("duplicate"):
            return {
                "status": "Duplicate",
                "message": (
                    "Another transaction already has "
                    "the same merchant, amount, date "
                    "and category. Update was not saved."
                ),
                "duplicate": True,
                "transaction":
                    result.get(
                        "duplicate_transaction"
                    ),
            }

        return {
            "status": "Success",
            "message": (
                "Transaction updated successfully."
            ),
            "duplicate": False,
            "transaction_id":
                result.get(
                    "transaction_id"
                ),
            "transaction":
                result.get(
                    "transaction"
                ),
        }

    except HTTPException:
        raise

    except Exception as error:
        print(
            "Transaction update error:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not update transaction."
            ),
        )


# ============================================================
# 22. DELETE TRANSACTION
# ============================================================

@app.delete("/transactions/{transaction_id}")
def remove_transaction(
    transaction_id: int
):
    if transaction_id <= 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Transaction ID must be "
                "greater than 0."
            ),
        )

    try:
        result = delete_transaction(
            transaction_id
        )

        if not result.get("found"):
            raise HTTPException(
                status_code=404,
                detail=(
                    "Transaction not found."
                ),
            )

        return {
            "status": "Success",
            "message": (
                "Transaction deleted successfully."
            ),
            "transaction_id":
                result.get(
                    "transaction_id"
                ),
            "transaction":
                result.get(
                    "transaction"
                ),
        }

    except HTTPException:
        raise

    except Exception as error:
        print(
            "Transaction delete error:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not delete transaction."
            ),
        )


# ============================================================
# 23. LATEST TRANSACTION FRAUD ANALYSIS
# ============================================================

@app.get("/transactions/latest/fraud")
def latest_transaction_fraud():
    try:
        latest = get_latest_transaction()

        if not latest:
            return {
                "status": "Success",
                "has_transaction": False,
                "transaction": None,
                "fraud_analysis": None,
            }

        auto_input = AutoFraudTransactionInput(
            amount=float(latest.get("amount", 0)),
            category=str(latest.get("category", "Other")),
            merchant=str(latest.get("merchant", "Unknown")),
            payment_method=0,
            location=0,
        )

        result = auto_detect_fraud(auto_input)

        return {
            "status": "Success",
            "has_transaction": True,
            "transaction_id": latest.get("id"),
            "transaction": latest,
            "encoded_features": result.get(
                "encoded_features"
            ),
            "fraud_analysis": result.get(
                "fraud_analysis"
            ),
        }

    except Exception as error:
        print(
            "Latest transaction fraud analysis error:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Latest transaction fraud analysis "
                "could not be completed."
            ),
        )


# ============================================================
# 24. TRANSACTION SUMMARY
# ============================================================

@app.get("/transactions/summary")
def transaction_summary():
    try:
        summary = (
            get_transaction_summary()
        )

        return {
            "status": "Success",
            **summary,
        }

    except Exception as error:
        print(
            "Transaction summary error:",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Could not generate transaction summary."
            ),
        )


# ============================================================
# 25. MODEL INFORMATION ENDPOINT
# ============================================================

@app.get("/model_info")
def model_info():
    return {
        "system":
            "AI-Powered Financial Intelligence System",

        "budget_prediction": {
            "status": (
                "Available"
                if budget_model is not None
                else "Temporarily Unavailable"
            ),
            "selected_model":
                "Gradient Boosting",
            "r2_score": 0.5974,
            "mae": 4620.89,
            "rmse": 5457.08,
            "feature_count": (
                len(budget_features)
                if budget_features is not None
                else 0
            ),
            "auto_transaction_features": True,
            "auto_features_endpoint":
                "/budget/auto-features",
            "auto_prediction_endpoint":
                "/budget/auto-predict",
        },

        "fraud_detection": {
            "status": (
                "Available"
                if fraud_model is not None
                else "Temporarily Unavailable"
            ),
            "selected_model":
                "Random Forest Classifier",
            "optimized_threshold": (
                round(
                    float(fraud_threshold),
                    2,
                )
                if fraud_threshold is not None
                else None
            ),
            "accuracy": 0.8467,
            "precision": 0.1860,
            "recall": 0.4211,
            "f1_score": 0.2581,
            "roc_auc": 0.6793,
            "explainable_alerts": True,
        },

        "amount_prediction": {
            "status": (
                "Available"
                if prediction_model is not None
                else "Temporarily Unavailable"
            ),
            "selected_model":
                "Random Forest",
            "auto_transaction_features": True,
            "auto_features_endpoint":
                "/amount/auto-features",
            "auto_prediction_endpoint":
                "/amount/auto-predict",
        },

        "receipt_ocr": {
            "status": (
                "Available"
                if ocr_reader is not None
                else "Temporarily Unavailable"
            ),
            "engine": "EasyOCR",
            "supported_formats": [
                "JPG",
                "PNG",
                "WEBP",
            ],
            "max_file_size_mb": 10,
            "confirmation_required": True,
        },

        "transaction_management": {
            "status": "Available",
            "database": "SQLite",
            "features": [
                "Save transaction",
                "List transactions",
                "Latest transaction",
                "Transaction summary",
                "Edit transaction",
                "Delete transaction",
                "Duplicate protection",
                "Date/category validation",
                "OCR completeness warnings",
            ],
        },
    }