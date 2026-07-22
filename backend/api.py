from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd


app = FastAPI(
    title="Financial AI Prediction System",
    version="1.0"
)


# =========================
# Load Trained Models
# =========================

prediction_model = joblib.load(
    "models/best_random_forest_model.pkl"
)

fraud_model = joblib.load(
    "models/fraud_model.pkl"
)



# =========================
# Home API
# =========================

@app.get("/")
def home():

    return {
        "message": "Financial AI API Running"
    }




# =========================
# Amount Prediction Input
# =========================

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
    amount_difference: float




# =========================
# Amount Prediction API
# =========================

@app.post("/predict_amount")
def predict_amount(data: PredictionInput):


    input_data = pd.DataFrame(
        [data.dict()]
    )


    # Keep same feature order used during training

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
            "amount_difference"
        ]
    ]


    prediction = prediction_model.predict(
        input_data
    )


    return {

        "predicted_amount":
        round(float(prediction[0]), 2)

    }





# =========================
# Fraud Detection Input
# =========================

class FraudInput(BaseModel):

    amount: int
    category: int
    merchant: int
    payment_method: int
    location: int





# =========================
# Fraud Detection API
# =========================

@app.post("/detect_fraud")
def detect_fraud(data: FraudInput):


    # Same features used while training Isolation Forest

    input_data = pd.DataFrame(
        [[
            data.amount,
            data.category,
            data.merchant,
            data.payment_method,
            data.location
        ]],
        columns=[
            "amount",
            "category",
            "merchant",
            "payment_method",
            "location"
        ]
    )


    prediction = fraud_model.predict(
        input_data
    )



    # =========================
    # Explainability Logic
    # =========================

    reasons = []


    if data.amount > 30000:

        reasons.append(
            "Transaction amount is unusually high"
        )


    if data.payment_method == 2:

        reasons.append(
            "Online payment method requires additional verification"
        )


    if data.merchant > 20:

        reasons.append(
            "Merchant pattern is different from normal transactions"
        )



    # =========================
    # Final Fraud Decision
    # =========================

    if prediction[0] == -1:


        status = "Fraud Detected"


        if len(reasons) == 0:

            reasons.append(
                "Unusual transaction pattern detected"
            )


    else:


        status = "Normal"

        reasons = [

            "Transaction behaviour matches normal patterns"

        ]



    return {

        "fraud_status": status,

        "risk_reasons": reasons

    }