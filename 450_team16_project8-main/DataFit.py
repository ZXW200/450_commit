import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

os.makedirs("CleanedDataPlt", exist_ok=True)

df = pd.read_csv("CleanedData/cleaned_ictrp.csv")

features = ["phase", "study_type", "sponsor_category", "income_level"]
X = df[features]
y = df["results_posted"].astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# build model and train it
model = Pipeline([
    ("encoder", ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), features)
    ])),
    ("logit", LogisticRegression(max_iter=2000, class_weight='balanced',random_state=42))
]).fit(X_train, y_train)

# get feature names and their coefficients
feature_names = model.named_steps["encoder"].get_feature_names_out()
coefficients = model.named_steps["logit"].coef_[0]

results = pd.DataFrame({
    "feature": feature_names,
    "coefficient": coefficients
}).sort_values("coefficient", ascending=False)

results.to_csv("CleanedData/logit_results.csv", index=False, encoding="utf-8-sig")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Logistic Regression Coefficients (Balanced Model)',
             fontsize=16, fontweight='bold')

# draw plot for each feature type
groups = {
    'Phase': 'cat__phase_',
    'Study Type': 'cat__study_type_',
    'Sponsor': 'cat__sponsor_category_',
    'Income Level': 'cat__income_level_'
}

for i, (title, prefix) in enumerate(groups.items()):
    ax = axes.flatten()[i]

    group_data = results[results['feature'].str.startswith(prefix)].copy()

    if len(group_data) == 0:
        continue

    group_data['short_name'] = group_data['feature'].str.replace(prefix, '', regex=False)
    group_data = group_data.sort_values('coefficient')

    colors = ['#d62728' if x < 0 else '#2ecc71' for x in group_data['coefficient']]
    ax.barh(group_data['short_name'], group_data['coefficient'],
            color=colors, alpha=0.75, edgecolor='black', linewidth=0.5)
    ax.axvline(0, color='black', linestyle='--', linewidth=1.5)
    ax.set_xlabel('Coefficient', fontsize=11)
    ax.set_title(title, fontweight='bold', fontsize=12)
    ax.grid(axis='x', alpha=0.3)

    if i == 0:
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#2ecc71', alpha=0.75, label='Positive'),
            Patch(facecolor='#d62728', alpha=0.75, label='Negative')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

plt.tight_layout()
plt.savefig("CleanedDataPlt/coefficients.jpg", dpi=300, bbox_inches='tight')
plt.close()

y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]


print(" Model Evaluation (Balanced)")


print(f"\nTrain Accuracy: {model.score(X_train, y_train):.4f}")
print(f" Test Accuracy: {model.score(X_test, y_test):.4f}")
print(f"AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")

print("\n Class Distribution:")
print(f"train: {y_train.value_counts().to_dict()}")
print(f"test: {y_test.value_counts().to_dict()}")

print("\n Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(cm)
print(f"  -> predit 0 (No Results): {cm[:, 0].sum()}")
print(f"  -> predit 1 (Results Posted): {cm[:, 1].sum()}")

print("\n Classification Report:")
print(classification_report(y_test, y_pred, target_names=['No Results (0)', 'Results Posted (1)'],zero_division=0))
print("\n All DataFit completed ")
