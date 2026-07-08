import pandas as pd
import joblib

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# -----------------------------
# Load Dataset
# -----------------------------

data = pd.read_csv(
    "data/processed_transactions.csv"
)


print("Dataset Loaded")


# -----------------------------
# Load Trained Model
# -----------------------------

model = joblib.load(
    "models/fraud_model.pkl"
)


print("Model Loaded")


# -----------------------------
# Select Features
# -----------------------------

features = [
    "amount",
    "category",
    "merchant",
    "payment_method",
    "location"
]


X = data[features]


# Actual fraud values

y_true = data["is_fraud"]


# -----------------------------
# Model Prediction
# -----------------------------

prediction = model.predict(X)


# Convert:
# Normal = 0
# Fraud = 1

prediction = pd.Series(prediction).replace({
    1:0,
    -1:1
})


# -----------------------------
# Evaluation
# -----------------------------

accuracy = accuracy_score(
    y_true,
    prediction
)


precision = precision_score(
    y_true,
    prediction,
    zero_division=0
)


recall = recall_score(
    y_true,
    prediction,
    zero_division=0
)


f1 = f1_score(
    y_true,
    prediction,
    zero_division=0
)


print("\nModel Performance")
print("----------------------")

print("Accuracy :", accuracy)
print("Precision:", precision)
print("Recall   :", recall)
print("F1 Score :", f1)


print("\nConfusion Matrix")
print(confusion_matrix(
    y_true,
    prediction
))


print("\nClassification Report")
print(
    classification_report(
        y_true,
        prediction,
        zero_division=0
    )
)