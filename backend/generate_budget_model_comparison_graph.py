import os
import matplotlib.pyplot as plt

# ============================================================
# 1. OUTPUT FOLDER
# ============================================================

OUTPUT_DIR = "graphs/budget_model"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# 2. FINAL MODEL RESULTS
# ============================================================

models = [
    "Current Gradient Boosting",
    "Linear Regression",
    "Naive Forecast",
    "Feature-Engineered Candidate"
]

r2_scores = [
    0.599702,
    0.588478,
    0.580449,
    0.638648
]


# ============================================================
# 3. CREATE GRAPH
# ============================================================

plt.figure(
    figsize=(10, 6)
)

bars = plt.bar(
    models,
    r2_scores
)

plt.title(
    "Budget Prediction Model Comparison"
)

plt.xlabel(
    "Model"
)

plt.ylabel(
    "Test R² Score"
)

plt.ylim(
    0.50,
    0.68
)

plt.xticks(
    rotation=15,
    ha="right"
)


# ============================================================
# 4. ADD VALUES ABOVE BARS
# ============================================================

for bar, score in zip(
    bars,
    r2_scores
):
    plt.text(
        bar.get_x()
        + bar.get_width() / 2,
        bar.get_height() + 0.003,
        f"{score:.4f}",
        ha="center",
        va="bottom",
        fontweight="bold"
    )


# ============================================================
# 5. ADD CURRENT PRODUCTION REFERENCE LINE
# ============================================================

plt.axhline(
    y=0.599702,
    linestyle="--",
    linewidth=1.5,
    label="Current Production R²"
)

plt.legend()

plt.tight_layout()


# ============================================================
# 6. SAVE GRAPH
# ============================================================

output_path = os.path.join(
    OUTPUT_DIR,
    "model_comparison.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# 7. TERMINAL OUTPUT
# ============================================================

print("=" * 70)
print("BUDGET MODEL COMPARISON GRAPH CREATED")
print("=" * 70)

print(
    "\nSaved to:",
    output_path
)

print("\nModel Results:")

for model, score in zip(
    models,
    r2_scores
):
    print(
        f"{model:32s} R² = {score:.4f}"
    )

print(
    "\nBest Test R²:",
    max(r2_scores)
)

print(
    "Best Model:",
    models[
        r2_scores.index(
            max(r2_scores)
        )
    ]
)