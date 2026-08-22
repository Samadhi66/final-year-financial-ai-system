import pandas as pd
import os
import joblib
import numpy as np

from sklearn.model_selection import (
    train_test_split,
    RandomizedSearchCV
)

from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# --------------------------------------------------
# 1. Load Dataset
# --------------------------------------------------

data = pd.read_csv(
    "data/feature_engineered_transactions.csv"
)

print("Dataset Loaded")
print("Dataset Shape:", data.shape)


# --------------------------------------------------
# 2. Select Features
# --------------------------------------------------

# amount_difference is intentionally NOT included
# because it is derived from the target variable (amount)
# and may cause target leakage.

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

    "payment_impact"
]


X = data[features]

# Target variable
y = data["amount"]


print("\nFeatures Used:")
print(features)

print("\nTarget:")
print("amount")


# --------------------------------------------------
# 3. Train-Test Split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


print("\nTraining Samples:", len(X_train))
print("Testing Samples :", len(X_test))


# --------------------------------------------------
# 4. Base Random Forest Model
# --------------------------------------------------

rf = RandomForestRegressor(
    random_state=42
)


# --------------------------------------------------
# 5. Hyperparameter Search Space
# --------------------------------------------------

param_distributions = {

    "n_estimators": [
        100,
        200,
        300,
        500
    ],

    "max_depth": [
        None,
        10,
        20,
        30,
        40
    ],

    "min_samples_split": [
        2,
        5,
        10
    ],

    "min_samples_leaf": [
        1,
        2,
        4
    ],

    "max_features": [
        "sqrt",
        "log2",
        None
    ]
}


# --------------------------------------------------
# 6. Randomized Hyperparameter Tuning
# --------------------------------------------------

print("\nStarting Advanced Random Forest Hyperparameter Tuning...")
print("This may take several minutes.\n")


random_search = RandomizedSearchCV(

    estimator=rf,

    param_distributions=param_distributions,

    n_iter=40,

    cv=5,

    scoring="r2",

    n_jobs=-1,

    verbose=2,

    random_state=42
)


random_search.fit(
    X_train,
    y_train
)


# --------------------------------------------------
# 7. Best Model and Parameters
# --------------------------------------------------

best_model = random_search.best_estimator_


print("\n======================================")
print("Best Hyperparameters")
print("======================================")

print(random_search.best_params_)


print("\nBest Cross-Validation R2 Score:")
print(random_search.best_score_)


# --------------------------------------------------
# 8. Prediction
# --------------------------------------------------

prediction = best_model.predict(
    X_test
)


# --------------------------------------------------
# 9. Model Evaluation
# --------------------------------------------------

mae = mean_absolute_error(
    y_test,
    prediction
)


mse = mean_squared_error(
    y_test,
    prediction
)


rmse = np.sqrt(mse)


r2 = r2_score(
    y_test,
    prediction
)


print("\n======================================")
print("Optimized Random Forest Performance")
print("======================================")

print("MAE      :", mae)

print("MSE      :", mse)

print("RMSE     :", rmse)

print("R2 Score :", r2)


# --------------------------------------------------
# 10. Save Best Model
# --------------------------------------------------

if not os.path.exists("models"):
    os.makedirs("models")


joblib.dump(
    best_model,
    "models/best_random_forest_model.pkl"
)


print(
    "\nOptimized Random Forest Model "
    "Saved Successfully!"
)

print(
    "Model Location: "
    "models/best_random_forest_model.pkl"
)