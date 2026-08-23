from pathlib import Path
import io

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
    version="2.5",
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


class AutoFraudTransactionInput(BaseModel):
    amount: float
    category: str
    merchant: str
    payment_method: int = 0
    location: int = 0


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
# 8. HOME ENDPOINT
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Financial AI API Running",
        "system": "AI-Powered Financial Intelligence System",
        "version": "2.5",
        "modules": [
            "Smart Budget Prediction",
            "Behavioral Fraud Detection",
            "Amount Prediction",
            "Receipt OCR Expense Entry",
            "Transaction Management",
            "Automatic Fraud Analysis",
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
# 10. SMART BUDGET PREDICTION ENDPOINT
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
# 11. FRAUD DETECTION ENDPOINT
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
# 12. AUTOMATIC FRAUD DETECTION FOR SAVED/OCR TRANSACTIONS
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
# 13. RECEIPT OCR ENDPOINT
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

        return {
            "status": "Success",
            "message": (
                "Receipt scanned successfully. "
                "Please confirm or edit the "
                "extracted information."
            ),
            "filename": file.filename,
            "merchant":
                parsed_data.get("merchant"),
            "amount":
                parsed_data.get("amount"),
            "date":
                parsed_data.get("date"),
            "suggested_category":
                parsed_data.get(
                    "suggested_category",
                    "Other",
                ),
            "raw_text":
                parsed_data.get(
                    "raw_text",
                    raw_text,
                ),
            "requires_confirmation": True,
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
# 14. CREATE / SAVE TRANSACTION
# ============================================================

@app.post("/transactions")
def create_transaction(
    transaction: TransactionInput
):
    merchant = transaction.merchant.strip()
    transaction_date = (
        transaction.transaction_date.strip()
    )
    category = transaction.category.strip()
    source = transaction.source.strip()

    if not merchant:
        raise HTTPException(
            status_code=400,
            detail="Merchant is required.",
        )

    if transaction.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Transaction amount must be greater than 0."
            ),
        )

    if not transaction_date:
        raise HTTPException(
            status_code=400,
            detail="Transaction date is required.",
        )

    if not category:
        raise HTTPException(
            status_code=400,
            detail="Category is required.",
        )

    if not source:
        source = "Manual"

    try:
        save_result = save_transaction(
            merchant=merchant,
            amount=transaction.amount,
            transaction_date=transaction_date,
            category=category,
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
# 15. GET ALL TRANSACTIONS
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
# 16. GET LATEST TRANSACTION
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
# 17. TRANSACTION SUMMARY
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
# 18. MODEL INFORMATION ENDPOINT
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
            ],
        },
    }