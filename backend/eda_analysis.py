import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# =========================
# Load Dataset
# =========================

data = pd.read_csv(
    "data/feature_engineered_transactions.csv"
)


print("Dataset Loaded")
print(data.head())


# =========================
# Basic Information
# =========================

print("\nDataset Information")
print(data.info())


print("\nClass Distribution")
print(data["is_fraud"].value_counts())


# =========================
# 1. Fraud Distribution
# =========================

plt.figure(figsize=(6,4))

sns.countplot(
    x="is_fraud",
    data=data
)

plt.title("Fraud vs Normal Transactions")

plt.xlabel("Fraud Status")
plt.ylabel("Number of Transactions")

plt.savefig(
    "fraud_distribution.png"
)

plt.close()



# =========================
# 2. Amount Distribution
# =========================

plt.figure(figsize=(7,4))

sns.histplot(
    data["amount"],
    bins=30,
    kde=True
)

plt.title("Transaction Amount Distribution")

plt.savefig(
    "amount_distribution.png"
)

plt.close()



# =========================
# 3. Box Plot - Amount Outliers
# =========================

plt.figure(figsize=(7,4))

sns.boxplot(
    y=data["amount"]
)

plt.title(
    "Transaction Amount Outliers"
)

plt.savefig(
    "amount_boxplot.png"
)

plt.close()



# =========================
# 4. Correlation Matrix
# =========================

plt.figure(figsize=(10,8))

correlation = data.corr()

sns.heatmap(
    correlation,
    annot=True,
    cmap="coolwarm"
)

plt.title(
    "Feature Correlation Matrix"
)

plt.savefig(
    "correlation_matrix.png"
)

plt.close()



# =========================
# 5. Category Fraud Analysis
# =========================

plt.figure(figsize=(8,5))

sns.countplot(
    x="category",
    hue="is_fraud",
    data=data
)

plt.title(
    "Fraud Distribution by Category"
)

plt.savefig(
    "category_fraud_analysis.png"
)

plt.close()



print("\nEDA Completed Successfully!")