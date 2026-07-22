import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# -----------------------------
# Load Dataset
# -----------------------------

data = pd.read_csv(
    "data/feature_engineered_transactions.csv"
)



print("Dataset Loaded")
print(data.columns)


# -----------------------------
# Select Features
# -----------------------------

features = [
"category",
"merchant",
"payment_method",
"location",
"month",
"day",
"is_weekend",
"category_avg_amount",
"merchant_frequency"
]


X = data[features]


# Target variable
# Predict transaction amount

y = data["amount"]


# -----------------------------
# Train Test Split
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# -----------------------------
# Create Linear Regression Model
# -----------------------------

model = LinearRegression()


# -----------------------------
# Train Model
# -----------------------------

model.fit(
    X_train,
    y_train
)


print("\nModel Training Completed")


# -----------------------------
# Prediction
# -----------------------------

prediction = model.predict(
    X_test
)


# -----------------------------
# Evaluation
# -----------------------------

mae = mean_absolute_error(
    y_test,
    prediction
)


mse = mean_squared_error(
    y_test,
    prediction
)


r2 = r2_score(
    y_test,
    prediction
)


print("\nModel Performance")
print("----------------------")

print("MAE :", mae)
print("MSE :", mse)
print("R2 Score :", r2)


# -----------------------------
# Save Model
# -----------------------------

if not os.path.exists("models"):
    os.makedirs("models")


joblib.dump(
    model,
    "models/prediction_model.pkl"
)


print("\nPrediction Model Saved Successfully!")