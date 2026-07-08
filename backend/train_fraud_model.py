import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os


# -----------------------------
# Load Processed Dataset
# -----------------------------

data = pd.read_csv(
    "data/processed_transactions.csv"
)


print("Dataset Loaded")
print(data.head())


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


# -----------------------------
# Create Isolation Forest Model
# -----------------------------

model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)


# -----------------------------
# Train Model
# -----------------------------

model.fit(X)


# -----------------------------
# Predict Fraud
# -----------------------------

data["fraud_prediction"] = model.predict(X)


# Convert result

# 1 = Normal
# -1 = Fraud

data["fraud_prediction"] = data[
    "fraud_prediction"
].replace({
    1: 0,
    -1: 1
})


print("\nFraud Prediction Result")
print(data.head())


# -----------------------------
# Save Model
# -----------------------------

if not os.path.exists("models"):
    os.makedirs("models")


joblib.dump(
    model,
    "models/fraud_model.pkl"
)


print("\nFraud Detection Model Saved Successfully!")