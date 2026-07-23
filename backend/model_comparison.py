import pandas as pd
import numpy as np


# Model performance results

results = {

    "Model": [
        "Linear Regression",
        "Random Forest",
        "Tuned Random Forest"
    ],


    "MAE": [
        6272.995,
        6468.933,
        49.2247
    ],


    "MSE": [
        78204696.80,
        87064496.70,
        6727.17
    ],


    "R2 Score": [
        0.548,
        0.497,
        0.999611
    ],


    "Training Time (seconds)": [
        0.12,
        2.45,
        18.63
    ]

}



# Create DataFrame

comparison = pd.DataFrame(results)



# Calculate RMSE

comparison["RMSE"] = np.sqrt(
    comparison["MSE"]
)



# Arrange columns

comparison = comparison[
    [
        "Model",
        "MAE",
        "MSE",
        "RMSE",
        "R2 Score",
        "Training Time (seconds)"
    ]
]



# Sort by R2 Score

comparison = comparison.sort_values(
    by="R2 Score",
    ascending=False
)



print("\nModel Comparison")
print("----------------")

print(comparison)



# Save result

comparison.to_csv(
    "data/model_comparison.csv",
    index=False
)


print(
    "\nComparison file saved successfully!"
)