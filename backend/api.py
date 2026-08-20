from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd


# ============================================================
# 1. FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI-Powered Financial Intelligence System",
    description=(
        "Smart Budget Prediction and "
        "Behavioral Fraud Detection API"
    ),
    version="2.1"
)


# ============================================================
# 2. LOAD TRAINED MODELS
# ============================================================

# ------------------------------------------------------------
# Legacy Amount Prediction Model
# ------------------------------------------------------------

try:

    prediction_model = joblib.load(
        "models/best_random_forest_model.pkl"
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

    print(
        "Reason:",
        error
    )


# ------------------------------------------------------------
# Final Smart Budget Prediction Model
# ------------------------------------------------------------

try:

    budget_model = joblib.load(
        "models/final_gradient_boosting_budget_model.pkl"
    )

    budget_features = joblib.load(
        "models/final_budget_model_features.pkl"
    )

    print(
        "Final Gradient Boosting budget model "
        "loaded successfully."
    )

except Exception as error:

    budget_model = None
    budget_features = None

    print(
        "Warning: Budget prediction model "
        "could not be loaded."
    )

    print(
        "Reason:",
        error
    )


# ------------------------------------------------------------
# Final Fraud Detection Model
# ------------------------------------------------------------

try:

    fraud_model = joblib.load(
        "models/final_fraud_model.pkl"
    )

    fraud_features = joblib.load(
        "models/final_fraud_model_features.pkl"
    )

    fraud_threshold = joblib.load(
        "models/fraud_threshold.pkl"
    )

    print(
        "Final fraud model loaded successfully."
    )

    print(
        "Fraud threshold:",
        fraud_threshold
    )

except Exception as error:

    fraud_model = None
    fraud_features = None
    fraud_threshold = None

    print(
        "Warning: Final fraud model "
        "could not be loaded."
    )

    print(
        "Reason:",
        error
    )


# ============================================================
# 3. HOME ENDPOINT
# ============================================================

@app.get("/")
def home():

    return {

        "message":
            "Financial AI API Running",

        "system":
            "AI-Powered Financial Intelligence System",

        "version":
            "2.1",

        "modules": [
            "Smart Budget Prediction",
            "Behavioral Fraud Detection"
        ]
    }


# ============================================================
# 4. LEGACY AMOUNT PREDICTION INPUT
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


# ============================================================
# 5. LEGACY AMOUNT PREDICTION ENDPOINT
# ============================================================

@app.post("/predict_amount")
def predict_amount(
    data: PredictionInput
):

    if prediction_model is None:

        return {

            "status":
                "Unavailable",

            "message":
                "Legacy amount prediction model "
                "is temporarily unavailable."
        }


    try:

        input_data = pd.DataFrame(
            [
                data.model_dump()
            ]
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
                "payment_impact"
            ]
        ]


        prediction = prediction_model.predict(
            input_data
        )


        return {

            "status":
                "Success",

            "predicted_amount":
                round(
                    float(
                        prediction[0]
                    ),
                    2
                )
        }


    except Exception as error:

        return {

            "status":
                "Unavailable",

            "message":
                "Legacy amount prediction "
                "could not be completed.",

            "error":
                str(error)
        }


# ============================================================
# 6. SMART BUDGET PREDICTION INPUT
# ============================================================

class BudgetPredictionInput(BaseModel):

    # Seasonal information
    week_sin: float
    week_cos: float

    # Current week
    current_week_spending: float

    # Historical spending
    spending_1_week_ago: float
    spending_2_weeks_ago: float
    spending_3_weeks_ago: float
    spending_4_weeks_ago: float

    # Rolling averages
    previous_2_week_avg: float
    previous_4_week_avg: float
    previous_8_week_avg: float

    # Current transaction behaviour
    current_transaction_count: int
    current_avg_transaction_amount: float
    current_fraud_count: int

    # Previous transaction behaviour
    previous_transaction_count: int
    previous_avg_transaction_amount: float

    # Spending trend
    spending_change: float
    spending_change_percentage: float


# ============================================================
# 7. SMART BUDGET PREDICTION ENDPOINT
# ============================================================

@app.post("/predict_budget")
def predict_budget(
    data: BudgetPredictionInput
):

    if (
        budget_model is None
        or budget_features is None
    ):

        return {

            "status":
                "Unavailable",

            "message":
                "Budget prediction model "
                "is temporarily unavailable."
        }


    try:

        input_dict = data.model_dump()


        input_data = pd.DataFrame(
            [
                input_dict
            ]
        )


        # Keep exact training feature order
        input_data = input_data[
            budget_features
        ]


        prediction = budget_model.predict(
            input_data
        )


        predicted_budget = round(
            float(
                prediction[0]
            ),
            2
        )


        current_spending = (
            data.current_week_spending
        )


        difference = (
            predicted_budget
            -
            current_spending
        )


        # ----------------------------------------------------
        # Calculate percentage difference
        # ----------------------------------------------------

        if current_spending == 0:

            percentage_change = 0.0

        else:

            percentage_change = (

                abs(
                    difference
                )

                /

                current_spending

                *

                100
            )


        # ----------------------------------------------------
        # Generate explanation
        # ----------------------------------------------------

        if difference > 0:

            trend = "Expected Increase"

            explanation = (
                f"Next week's spending is predicted "
                f"to increase by approximately "
                f"{percentage_change:.2f}% compared "
                f"with the current week."
            )


        elif difference < 0:

            trend = "Expected Decrease"

            explanation = (
                f"Next week's spending is predicted "
                f"to decrease by approximately "
                f"{percentage_change:.2f}% compared "
                f"with the current week."
            )


        else:

            trend = "Stable"

            explanation = (
                "Next week's spending is predicted "
                "to remain approximately stable."
            )


        return {

            "status":
                "Success",

            "predicted_next_week_spending":
                predicted_budget,

            "current_week_spending":
                round(
                    current_spending,
                    2
                ),

            "predicted_difference":
                round(
                    difference,
                    2
                ),

            "percentage_change":
                round(
                    percentage_change,
                    2
                ),

            "trend":
                trend,

            "explanation":
                explanation,

            "model":
                "Gradient Boosting",

            "model_r2":
                0.5974,

            "model_mae":
                4620.89,

            "model_rmse":
                5457.08
        }


    except Exception as error:

        return {

            "status":
                "Error",

            "message":
                "Budget prediction "
                "could not be completed.",

            "error":
                str(error)
        }


# ============================================================
# 8. FRAUD DETECTION INPUT
# ============================================================

class FraudInput(BaseModel):

    amount: float

    category: int
    merchant: int
    payment_method: int
    location: int


# ============================================================
# 9. FRAUD DETECTION ENDPOINT
# ============================================================

@app.post("/detect_fraud")
def detect_fraud(
    data: FraudInput
):

    if (
        fraud_model is None
        or fraud_features is None
        or fraud_threshold is None
    ):

        return {

            "status":
                "Unavailable",

            "fraud_status":
                "Unavailable",

            "risk_level":
                "Unknown",

            "risk_reasons": [
                "Fraud detection model "
                "has not been loaded."
            ]
        }


    try:

        # ----------------------------------------------------
        # Basic API Input
        # ----------------------------------------------------

        input_data = pd.DataFrame(
            [
                data.model_dump()
            ]
        )


        # ----------------------------------------------------
        # Temporary Behavioral Context
        # ----------------------------------------------------
        # These values will later be calculated automatically
        # from the user's transaction history/database.
        # For the current API prototype, controlled values
        # are supplied here so the trained model receives
        # the same feature structure used during training.
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # Match exact training feature order
        # ----------------------------------------------------

        input_data = input_data[
            fraud_features
        ]


        # ----------------------------------------------------
        # Calculate Fraud Probability
        # ----------------------------------------------------

        fraud_probability = (
            fraud_model
            .predict_proba(
                input_data
            )[0][1]
        )


        # ----------------------------------------------------
        # Apply Optimized Threshold
        # ----------------------------------------------------

        fraud_prediction = int(

            fraud_probability
            >=
            fraud_threshold
        )


        # ----------------------------------------------------
        # Explainability
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # Risk Decision
        # ----------------------------------------------------

        if fraud_prediction == 1:

            fraud_status = (
                "Fraud Detected"
            )


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


        # ----------------------------------------------------
        # Final Response
        # ----------------------------------------------------

        return {

            "status":
                "Success",

            "fraud_status":
                fraud_status,

            "risk_level":
                risk_level,

            "fraud_probability":
                round(
                    float(
                        fraud_probability
                    ),
                    4
                ),

            "threshold":
                round(
                    float(
                        fraud_threshold
                    ),
                    2
                ),

            "risk_reasons":
                reasons,

            "model":
                "Random Forest Classifier"
        }


    except Exception as error:

        return {

            "status":
                "Error",

            "fraud_status":
                "Unavailable",

            "risk_level":
                "Unknown",

            "risk_reasons": [
                "Fraud detection "
                "could not be completed."
            ],

            "error":
                str(error)
        }


# ============================================================
# 10. MODEL INFORMATION ENDPOINT
# ============================================================

@app.get("/model_info")
def model_info():

    return {

        "system":
            "AI-Powered Financial Intelligence System",

        # ----------------------------------------------------
        # Budget Prediction Information
        # ----------------------------------------------------

        "budget_prediction": {

            "status":
                (
                    "Available"
                    if budget_model is not None
                    else "Temporarily Unavailable"
                ),

            "selected_model":
                "Gradient Boosting",

            "r2_score":
                0.5974,

            "mae":
                4620.89,

            "rmse":
                5457.08,

            "feature_count":
                (
                    len(
                        budget_features
                    )
                    if budget_features is not None
                    else 0
                )
        },


        # ----------------------------------------------------
        # Fraud Detection Information
        # ----------------------------------------------------

        "fraud_detection": {

            "status":
                (
                    "Available"
                    if fraud_model is not None
                    else "Temporarily Unavailable"
                ),

            "selected_model":
                "Random Forest Classifier",

            "optimized_threshold":
                (
                    round(
                        float(
                            fraud_threshold
                        ),
                        2
                    )
                    if fraud_threshold is not None
                    else None
                ),

            "accuracy":
                0.8467,

            "precision":
                0.1860,

            "recall":
                0.4211,

            "f1_score":
                0.2581,

            "roc_auc":
                0.6793,

            "explainable_alerts":
                True
        },


        # ----------------------------------------------------
        # Legacy Amount Prediction Information
        # ----------------------------------------------------

        "legacy_amount_prediction": {

            "status":
                (
                    "Available"
                    if prediction_model is not None
                    else "Temporarily Unavailable"
                )
        }
    }