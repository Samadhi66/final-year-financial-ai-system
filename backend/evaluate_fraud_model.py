import pandas as pd
import joblib

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score
)


# =========================
# Load Dataset
# =========================

data = pd.read_csv(
    "data/feature_engineered_transactions.csv"
)


print("Dataset Loaded")
print(data.head())



# =========================
# Load Fraud Model
# =========================

fraud_model = joblib.load(
    "models/fraud_model.pkl"
)



# =========================
# Select Features
# =========================

features = [

    "amount",
    "category",
    "merchant",
    "payment_method",
    "location"

]


X = data[features]


# Actual labels

y_true = data["is_fraud"]



# =========================
# Model Prediction
# =========================

prediction = fraud_model.predict(X)



# Isolation Forest:
# Normal = 1
# Fraud = -1

prediction = [

    1 if value == -1 else 0

    for value in prediction

]



# =========================
# Evaluation
# =========================


print("\nFraud Model Evaluation")
print("----------------------")


print(
    "Precision:",
    precision_score(
        y_true,
        prediction
    )
)


print(
    "Recall:",
    recall_score(
        y_true,
        prediction
    )
)


print(
    "F1 Score:",
    f1_score(
        y_true,
        prediction
    )
)



print("\nClassification Report")
print(
    classification_report(
        y_true,
        prediction
    )
)



print("\nConfusion Matrix")

print(
    confusion_matrix(
        y_true,
        prediction
    )
)