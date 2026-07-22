import pandas as pd
import os


# --------------------------------
# Load Dataset
# --------------------------------

input_file = "data/processed_transactions.csv"

data = pd.read_csv(input_file)


print("Original Dataset")
print(data.head())


# --------------------------------
# Feature 1: Weekend Transaction
# --------------------------------

data["is_weekend"] = data["day"].apply(
    lambda x: 1 if x in [5, 6] else 0
)


# --------------------------------
# Feature 2: Category Average Amount
# --------------------------------

category_avg = data.groupby("category")["amount"].mean()

data["category_avg_amount"] = data["category"].map(
    category_avg
)


# --------------------------------
# Feature 3: Merchant Transaction Frequency
# --------------------------------

merchant_frequency = data.groupby("merchant")["transaction_id"].transform(
    "count"
)

data["merchant_frequency"] = merchant_frequency


# --------------------------------
# Feature 4: Payment Method Impact
# --------------------------------

payment_impact = {
    0: 1.0,   # Card
    1: 1.2,   # Cash
    2: 1.5    # Online Transfer
}


data["payment_impact"] = data["payment_method"].map(
    payment_impact
)


# --------------------------------
# Feature 5: Amount Difference
# --------------------------------

output_file = "data/feature_engineered_transactions.csv"


data.to_csv(
    output_file,
    index=False
)


print("\nFeature Engineering Completed!")

print(data.head())


print("\nNew Features Added:")
print([
    "is_weekend",
    "category_avg_amount",
    "merchant_frequency",
    "payment_impact",
    "amount_difference"
])