import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split

from sklearn.linear_model import LogisticRegression

from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier
)

from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

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
print("FRAUD DETECTION MODEL COMPARISON")
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


print("\nFraud Distribution:")
print(
    y.value_counts()
)

print(
    "\nFraud Percentage:",
    round(
        y.mean() * 100,
        2
    ),
    "%"
)


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
    "Training Fraud Cases:",
    int(
        y_train.sum()
    )
)

print(
    "Testing Fraud Cases :",
    int(
        y_test.sum()
    )
)


# ============================================================
# 4. MODELS
# ============================================================

models = {

    # --------------------------------------------------------
    # Logistic Regression
    # --------------------------------------------------------

    "Logistic Regression": Pipeline(
        [
            (
                "scaler",
                StandardScaler()
            ),

            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=42
                )
            )
        ]
    ),


    # --------------------------------------------------------
    # Random Forest
    # --------------------------------------------------------

    "Random Forest": RandomForestClassifier(
        n_estimators=500,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    ),


    # --------------------------------------------------------
    # Extra Trees
    # --------------------------------------------------------

    "Extra Trees": ExtraTreesClassifier(
        n_estimators=500,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    ),


    # --------------------------------------------------------
    # Gradient Boosting
    # --------------------------------------------------------

    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=2,
        random_state=42
    )
}


# ============================================================
# 5. TRAIN AND EVALUATE
# ============================================================

results = []


for model_name, model in models.items():

    print("\n" + "=" * 70)
    print("Training:", model_name)
    print("=" * 70)

    model.fit(
        X_train,
        y_train
    )


    # --------------------------------------------------------
    # Class predictions
    # --------------------------------------------------------

    predictions = model.predict(
        X_test
    )


    # --------------------------------------------------------
    # Fraud probability
    # --------------------------------------------------------

    probabilities = model.predict_proba(
        X_test
    )[:, 1]


    # --------------------------------------------------------
    # Evaluation metrics
    # --------------------------------------------------------

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

    roc_auc = roc_auc_score(
        y_test,
        probabilities
    )


    cm = confusion_matrix(
        y_test,
        predictions
    )


    if cm.shape == (2, 2):

        tn, fp, fn, tp = cm.ravel()

    else:

        tn = fp = fn = tp = 0


    results.append(
        {
            "Model":
                model_name,

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
        }
    )


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

    print(
        "ROC AUC  :",
        round(
            roc_auc,
            4
        )
    )

    print(
        "\nConfusion Matrix:"
    )

    print(
        cm
    )


# ============================================================
# 6. CREATE COMPARISON TABLE
# ============================================================

comparison = pd.DataFrame(
    results
)


# ============================================================
# 7. RANK MODELS
# ============================================================
# Fraud detection prioritizes:
# 1. F1 Score
# 2. Recall
# 3. ROC AUC

comparison = comparison.sort_values(
    by=[
        "F1 Score",
        "Recall",
        "ROC AUC"
    ],
    ascending=False
).reset_index(
    drop=True
)


print("\n" + "=" * 100)
print("FINAL FRAUD MODEL RANKING")
print("=" * 100)

print(
    comparison.to_string(
        index=False
    )
)


# ============================================================
# 8. BEST MODEL
# ============================================================

best_model = comparison.iloc[0]


print("\n" + "=" * 70)
print("BEST FRAUD DETECTION MODEL")
print("=" * 70)

print(
    "Model:",
    best_model["Model"]
)

print(
    "Accuracy:",
    round(
        best_model["Accuracy"],
        4
    )
)

print(
    "Precision:",
    round(
        best_model["Precision"],
        4
    )
)

print(
    "Recall:",
    round(
        best_model["Recall"],
        4
    )
)

print(
    "F1 Score:",
    round(
        best_model["F1 Score"],
        4
    )
)

print(
    "ROC AUC:",
    round(
        best_model["ROC AUC"],
        4
    )
)

print(
    "False Negatives:",
    int(
        best_model["False Negatives"]
    )
)

print(
    "True Positives:",
    int(
        best_model["True Positives"]
    )
)


# ============================================================
# 9. SAVE RESULTS
# ============================================================

comparison.to_csv(
    "data/fraud_model_comparison.csv",
    index=False
)


print("\nComparison Results Saved To:")

print(
    "data/fraud_model_comparison.csv"
)