import pandas as pd
from sklearn.preprocessing import LabelEncoder
import os
import numpy as np


# -----------------------------
# Load Dataset
# -----------------------------

input_file = "data/transactions.csv"

data = pd.read_csv(input_file)

# =========================
# Missing Data Handling
# =========================

print("\nMissing Values Before Cleaning")
print(data.isnull().sum())


# Numerical columns

numeric_columns = data.select_dtypes(
    include=['int64','float64']
).columns


for column in numeric_columns:

    data[column] = data[column].fillna(
        data[column].median()
    )



# Categorical columns

categorical_columns = data.select_dtypes(
    include=['object']
).columns


for column in categorical_columns:

    data[column] = data[column].fillna(
        "Unknown"
    )



# Remove duplicate records

data.drop_duplicates(
    inplace=True
)



# Remove invalid transaction amounts

data = data[
    data["amount"] >= 0
]


print("\nMissing Values After Cleaning")
print(data.isnull().sum())

print("\nData Cleaning Completed")

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