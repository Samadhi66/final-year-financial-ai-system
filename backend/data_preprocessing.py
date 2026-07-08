import pandas as pd
from sklearn.preprocessing import LabelEncoder
import os


# -----------------------------
# Load Dataset
# -----------------------------

input_file = "data/transactions.csv"

data = pd.read_csv(input_file)


print("Original Dataset")
print(data.head())

print("\nDataset Shape:")
print(data.shape)


# -----------------------------
# Check Missing Values
# -----------------------------

print("\nMissing Values:")
print(data.isnull().sum())


# -----------------------------
# Date Processing
# -----------------------------

data["date"] = pd.to_datetime(data["date"])

data["year"] = data["date"].dt.year
data["month"] = data["date"].dt.month
data["day"] = data["date"].dt.day


# Remove original date column

data.drop(
    "date",
    axis=1,
    inplace=True
)


# -----------------------------
# Encode Categorical Columns
# -----------------------------

encoder = LabelEncoder()


categorical_columns = [
    "category",
    "merchant",
    "payment_method",
    "location"
]


for column in categorical_columns:

    data[column] = encoder.fit_transform(
        data[column]
    )


# -----------------------------
# Save Processed Dataset
# -----------------------------

output_file = "data/processed_transactions.csv"


data.to_csv(
    output_file,
    index=False
)


print("\nPreprocessing Completed Successfully!")

print("Processed Dataset:")
print(data.head())