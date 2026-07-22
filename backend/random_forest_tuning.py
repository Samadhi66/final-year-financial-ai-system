import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor

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


# -----------------------------
# Features
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

    "merchant_frequency",

    "payment_impact",

    "amount_difference"

]


X = data[features]


# Target

y = data["amount"]



# -----------------------------
# Split Data
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)



# -----------------------------
# Random Forest
# -----------------------------

rf = RandomForestRegressor(
    random_state=42
)



# -----------------------------
# Fast Parameter Grid
# -----------------------------

param_grid = {

    "n_estimators": [
        100,
        200
    ],

    "max_depth": [
        10,
        20
    ],

    "min_samples_split": [
        2
    ],

    "min_samples_leaf": [
        1
    ]

}



print("\nStarting Fast Hyperparameter Tuning...")



grid = GridSearchCV(
    estimator=rf,
    param_grid=param_grid,
    cv=3,
    scoring="r2",
    n_jobs=-1,
    verbose=1
)



grid.fit(
    X_train,
    y_train
)



# -----------------------------
# Best Model
# -----------------------------

best_model = grid.best_estimator_


print("\nBest Parameters")
print("----------------")
print(grid.best_params_)



# Prediction

prediction = best_model.predict(
    X_test
)



# Evaluation

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



print("\nTuned Random Forest Performance")
print("-------------------------------")

print("MAE :", mae)

print("MSE :", mse)

print("R2 Score :", r2)



# Save

if not os.path.exists("models"):
    os.makedirs("models")


joblib.dump(
    best_model,
    "models/best_random_forest_model.pkl"
)


print("\nTuned Random Forest Model Saved Successfully!")