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
    roc_auc_score,
    confusion_matrix
)


# ============================================================
# 1. LOAD DATASET
# ============================================================

data = pd.read_csv(
    "data/feature_engineered_transactions.csv"
)

print("=" * 70)
print("FRAUD DETECTION THRESHOLD TUNING")
print("=" * 70)

print("\nDataset Loaded")
print("Dataset Shape:", data.shape)


# ============================================================
# 2. FEATURES AND TARGET
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

X = data[features]
y = data[target]


# ============================================================
# 3. STRATIFIED TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining Samples:", len(X_train))
print("Testing Samples :", len(X_test))

print(
    "Testing Fraud Cases:",
    int(y_test.sum())
)


# ============================================================
# 4. TRAIN RANDOM FOREST
# ============================================================

model = RandomForestClassifier(
    n_estimators=500,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

print("\nTraining Random Forest...")

model.fit(
    X_train,
    y_train
)

print("Training Completed")


# ============================================================
# 5. FRAUD PROBABILITIES
# ============================================================

probabilities = model.predict_proba(
    X_test
)[:, 1]

roc_auc = roc_auc_score(
    y_test,
    probabilities
)


# ============================================================
# 6. THRESHOLDS TO TEST
# ============================================================

thresholds = [
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60
]


# ============================================================
# 7. TEST EACH THRESHOLD
# ============================================================

results = []


for threshold in thresholds:

    predictions = (
        probabilities >= threshold
    ).astype(int)


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


    cm = confusion_matrix(
        y_test,
        predictions
    )


    tn, fp, fn, tp = cm.ravel()


    results.append({

        "Threshold":
            threshold,

        "Accuracy":
            accuracy,

        "Precision":
            precision,

        "Recall":
            recall,

        "F1 Score":
            f1,

        "ROC AUC":
            roc_auc,

        "True Negatives":
            tn,

        "False Positives":
            fp,

        "False Negatives":
            fn,

        "True Positives":
            tp
    })


# ============================================================
# 8. CREATE RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(
    results
)


print("\n" + "=" * 110)
print("THRESHOLD COMPARISON")
print("=" * 110)

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# 9. SELECT BEST THRESHOLD
# ============================================================
# We prioritize F1 score first.
# If two thresholds are similar, higher recall is preferred.

ranking = results_df.sort_values(
    by=[
        "F1 Score",
        "Recall"
    ],
    ascending=False
).reset_index(drop=True)


best = ranking.iloc[0]


print("\n" + "=" * 70)
print("BEST FRAUD THRESHOLD")
print("=" * 70)

print(
    "Threshold:",
    round(
        best["Threshold"],
        2
    )
)

print(
    "Accuracy:",
    round(
        best["Accuracy"],
        4
    )
)

print(
    "Precision:",
    round(
        best["Precision"],
        4
    )
)

print(
    "Recall:",
    round(
        best["Recall"],
        4
    )
)

print(
    "F1 Score:",
    round(
        best["F1 Score"],
        4
    )
)

print(
    "ROC AUC:",
    round(
        best["ROC AUC"],
        4
    )
)

print(
    "False Negatives:",
    int(
        best["False Negatives"]
    )
)

print(
    "True Positives:",
    int(
        best["True Positives"]
    )
)


# ============================================================
# 10. SAVE THRESHOLD RESULTS
# ============================================================

results_df.to_csv(
    "data/fraud_threshold_results.csv",
    index=False
)


# ============================================================
# 11. SAVE BEST THRESHOLD
# ============================================================

os.makedirs(
    "models",
    exist_ok=True
)

joblib.dump(
    float(
        best["Threshold"]
    ),
    "models/fraud_threshold.pkl"
)


# ============================================================
# 12. SAVE FINAL RANDOM FOREST MODEL
# ============================================================

joblib.dump(
    model,
    "models/final_fraud_model.pkl"
)

joblib.dump(
    features,
    "models/final_fraud_model_features.pkl"
)


# ============================================================
# 13. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("FINAL FRAUD MODEL SAVED SUCCESSFULLY")
print("=" * 70)

print(
    "Model:",
    "models/final_fraud_model.pkl"
)

print(
    "Features:",
    "models/final_fraud_model_features.pkl"
)

print(
    "Threshold:",
    "models/fraud_threshold.pkl"
)

print(
    "Results:",
    "data/fraud_threshold_results.csv"
)