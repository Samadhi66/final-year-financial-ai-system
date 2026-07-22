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

    input_data = pd.DataFrame(
        [data.dict()]
    )


    # Correct feature order
    input_data = input_data[
        [
            "amount",
            "category",
            "merchant",
            "payment_method",
            "location"
        ]
    ]


    result = fraud_model.predict(
        input_data
    )


    reasons = []


    # Explainability Logic

    if data.amount > 30000:

        reasons.append(
            "Transaction amount is unusually high compared with normal transactions"
        )


    if data.payment_method == 2:

        reasons.append(
            "Payment method has higher risk behaviour"
        )


    if data.merchant > 20:

        reasons.append(
            "Merchant pattern is different from normal transactions"
        )


    if result[0] == -1:

        status = "Fraud Detected"

        if len(reasons) == 0:

            reasons.append(
                "Unusual transaction pattern detected by AI model"
            )


        risk_level = "High"


    else:

        status = "Normal"

        if len(reasons) == 0:

            reasons.append(
                "Transaction behaviour matches normal patterns"
            )


        risk_level = "Low"



    return {

        "fraud_status": status,

        "risk_level": risk_level,

        "risk_reasons": reasons

    }