import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


# Load dataset

data = pd.read_csv(
    "data/processed_transactions.csv"
)


# Features

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


# Parameters to test

n_estimators_list = [
    50,
    100,
    200,
    300
]


contamination_list = [
    0.01,
    0.03,
    0.05,
    0.10
]


results = []


# Training loop

for trees in n_estimators_list:

    for contamination in contamination_list:


        model = IsolationForest(
            n_estimators=trees,
            contamination=contamination,
            random_state=42
        )


        model.fit(X)


        prediction = model.predict(X)


        # Convert output
        prediction = pd.Series(prediction).replace({
            1:0,
            -1:1
        })


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


        results.append([
            trees,
            contamination,
            accuracy,
            precision,
            recall,
            f1
        ])



# Create result table

result_df = pd.DataFrame(
    results,
    columns=[
        "n_estimators",
        "contamination",
        "accuracy",
        "precision",
        "recall",
        "f1_score"
    ]
)


# Sort by F1 score

result_df = result_df.sort_values(
    by="f1_score",
    ascending=False
)


print("\nHyperparameter Tuning Results")
print(result_df)


# Save results

result_df.to_csv(
    "data/hyperparameter_results.csv",
    index=False
)


print("\nTuning Completed Successfully!")