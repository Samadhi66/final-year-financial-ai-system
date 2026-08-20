import os
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# 1. LOAD DATASET
# ============================================================

data = pd.read_csv(
    "data/feature_engineered_transactions.csv"
)

print("=" * 60)
print("BEHAVIORAL FRAUD DETECTION MODEL TRAINING")
print("=" * 60)

print("\nDataset Loaded Successfully")
print("Dataset Shape:", data.shape)

print("\nColumns:")
print(data.columns.tolist())


# ============================================================
# 2. SELECT FRAUD FEATURES
# ============================================================

features = [
    "amount",
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

target = "is_fraud"


# ============================================================
# 3. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = features + [target]

missing_columns = [
    column
    for column in required_columns
    if column not in data.columns
]

if missing_columns:

    print("\nERROR: Missing columns:")

    for column in missing_columns:
        print("-", column)

    raise ValueError(
        "Required fraud detection columns are missing."
    )


# ============================================================
# 4. PREPARE X AND y
# ============================================================

X = data[features]

y = data[target]


print("\nFraud Class Distribution:")
print(y.value_counts())

print(
    "\nFraud Percentage:",
    round(
        y.mean() * 100,
        2
    ),
    "%"
)


# ============================================================
# 5. TRAIN / TEST SPLIT
# ============================================================
# stratify=y keeps fraud/non-fraud proportions similar
# in both training and testing datasets.

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\n" + "=" * 60)
print("TRAIN / TEST SPLIT")
print("=" * 60)

print("Training Samples:", len(X_train))
print("Testing Samples :", len(X_test))

print(
    "Training Fraud Cases:",
    int(y_train.sum())
)

print(
    "Testing Fraud Cases :",
    int(y_test.sum())
)


# ============================================================
# 6. CREATE RANDOM FOREST CLASSIFIER
# ============================================================
# class_weight="balanced" is important because fraud cases
# are much rarer than normal transactions.

fraud_model = RandomForestClassifier(
    n_estimators=500,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)


# ============================================================
# 7. TRAIN MODEL
# ============================================================

print("\nTraining Random Forest Fraud Classifier...")

fraud_model.fit(
    X_train,
    y_train
)

print("Model Training Completed Successfully")


# ============================================================
# 8. MAKE PREDICTIONS
# ============================================================

predictions = fraud_model.predict(
    X_test
)


# Fraud probability
probabilities = fraud_model.predict_proba(
    X_test
)[:, 1]


# ============================================================
# 9. EVALUATION METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    predictions
)

precision = precision_score(
    y_test,
    predictions,
    zero_division=0
)

recall = recall_score(
    y_test,
    predictions,
    zero_division=0
)

f1 = f1_score(
    y_test,
    predictions,
    zero_division=0
)


print("\n" + "=" * 60)
print("FRAUD MODEL PERFORMANCE")
print("=" * 60)

print(
    "Accuracy :",
    round(
        accuracy,
        4
    )
)

print(
    "Precision:",
    round(
        precision,
        4
    )
)

print(
    "Recall   :",
    round(
        recall,
        4
    )
)

print(
    "F1 Score :",
    round(
        f1,
        4
    )
)


# ============================================================
# 10. CLASSIFICATION REPORT
# ============================================================

print("\n" + "=" * 60)
print("CLASSIFICATION REPORT")
print("=" * 60)

print(
    classification_report(
        y_test,
        predictions,
        zero_division=0
    )
)


# ============================================================
# 11. CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    predictions
)

print("\n" + "=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)

print(cm)


if cm.shape == (2, 2):

    tn, fp, fn, tp = cm.ravel()

    print("\nTrue Negatives :", tn)
    print("False Positives:", fp)
    print("False Negatives:", fn)
    print("True Positives :", tp)


# ============================================================
# 12. FEATURE IMPORTANCE
# ============================================================

feature_importance = pd.DataFrame({

    "Feature":
        features,

    "Importance":
        fraud_model.feature_importances_
})


feature_importance = (
    feature_importance
    .sort_values(
        by="Importance",
        ascending=False
    )
    .reset_index(drop=True)
)


print("\n" + "=" * 60)
print("FRAUD FEATURE IMPORTANCE")
print("=" * 60)

print(
    feature_importance.to_string(
        index=False
    )
)


# ============================================================
# 13. SAVE TEST RESULTS
# ============================================================

test_results = X_test.copy()

test_results["actual_fraud"] = (
    y_test.values
)

test_results["predicted_fraud"] = (
    predictions
)

test_results["fraud_probability"] = (
    probabilities
)


os.makedirs(
    "data",
    exist_ok=True
)


test_results.to_csv(
    "data/fraud_model_test_results.csv",
    index=False
)


feature_importance.to_csv(
    "data/fraud_feature_importance.csv",
    index=False
)


# ============================================================
# 14. SAVE FINAL MODEL
# ============================================================

os.makedirs(
    "models",
    exist_ok=True
)


joblib.dump(
    fraud_model,
    "models/fraud_model.pkl"
)


# Save exact model feature order
joblib.dump(
    features,
    "models/fraud_model_features.pkl"
)


# ============================================================
# 15. SAVE METRICS
# ============================================================

metrics = pd.DataFrame(
    [
        {
            "Model":
                "Random Forest Classifier",

            "Accuracy":
                accuracy,

            "Precision":
                precision,

            "Recall":
                recall,

            "F1 Score":
                f1
        }
    ]
)


metrics.to_csv(
    "data/fraud_model_metrics.csv",
    index=False
)


# ============================================================
# 16. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("FRAUD MODEL SAVED SUCCESSFULLY")
print("=" * 60)

print(
    "\nModel:",
    "models/fraud_model.pkl"
)

print(
    "Features:",
    "models/fraud_model_features.pkl"
)

print(
    "Metrics:",
    "data/fraud_model_metrics.csv"
)

print(
    "Test Results:",
    "data/fraud_model_test_results.csv"
)

print(
    "Feature Importance:",
    "data/fraud_feature_importance.csv"
)