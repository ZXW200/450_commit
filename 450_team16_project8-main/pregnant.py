import pandas as pd
import matplotlib.pyplot as plt
import os

output = "CleanedDataPlt"
os.makedirs(output, exist_ok=True)

data_path = os.path.join("CleanedData", "cleaned_ictrp.csv")
df = pd.read_csv(data_path)

def classify_preg(row):
    """
    Classify trials based on whether they include pregnant participants.
    Returns INCLUDED if pregnant women are explicitly included, NOT_INCLUDED otherwise.
    """
    raw = str(row.get("pregnant_participants", "")).strip().upper()
    if raw == "INCLUDED":
        return "INCLUDED"
    else:
        return "NOT_INCLUDED"

# apply pregnancy inclusion classification
df["preg_status"] = df.apply(classify_preg, axis=1)

# calculate basic statistics
total = len(df)
included = (df["preg_status"] == "INCLUDED").sum()
not_included = (df["preg_status"] == "NOT_INCLUDED").sum()

print("=== Pregnancy inclusion summary ===")
print(f"Total trials: {total}")
print(f"Trials including pregnant women: {included}")
print(f"Trials NOT including pregnant women: {not_included}")
print(df["preg_status"].value_counts())
print()

statusCounts = df["preg_status"].value_counts()

# visualize overall pregnancy inclusion rates
fig1, ax1 = plt.subplots(figsize=(6, 6))
ax1.pie(
    statusCounts.values,
    labels=statusCounts.index,
    autopct="%1.1f%%",
    startangle=90
)
ax1.set_title("Pregnancy inclusion status (all trials)")
ax1.axis("equal")
plt.tight_layout()
pie_path = os.path.join(output, "pregnancy_inclusion.png")
plt.savefig(pie_path, dpi=300)
plt.close(fig1)

# filter to trials that include pregnant women for disease-specific analysis
df_included = df[df["preg_status"] == "INCLUDED"].copy()

disease_col = "standardised_condition"
disease_counts = (
    df_included[disease_col]
    .value_counts()
    .sort_values(ascending=False)
)

top_diseases = disease_counts.head(5)

print("---Trials including pregnant women by disease---")
print(top_diseases)
print()

# show which diseases most commonly include pregnant participants
fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.bar(top_diseases.index, top_diseases.values)
ax2.set_title(f"Number of trials including pregnant women by disease")
ax2.set_ylabel("Number of trials")
ax2.set_xlabel("Disease")

ax2.tick_params(axis="x", labelrotation=45)
for label in ax2.get_xticklabels():
    label.set_horizontalalignment("right")

plt.tight_layout()
bar_path = os.path.join(output, "inclusion_disease.png")
plt.savefig(bar_path, dpi=300)
plt.close(fig2)

phase_col = "phase"

# analyze how pregnancy inclusion varies across trial phases
phase_summary = (
    df.groupby(phase_col)
      .agg(
          total_trials=("preg_status", "size"),
          preg_included=("preg_status", lambda x: (x == "INCLUDED").sum())
      )
)

phase_summary["inclusion_rate"] = (
    phase_summary["preg_included"] / phase_summary["total_trials"]
)

# order phases logically from early to late stage
phase_order = [
    "PHASE I TRIAL",
    "PHASE I/II TRIAL",
    "PHASE II TRIAL",
    "PHASE II/III TRIAL",
    "PHASE III TRIAL",
    "PHASE IV TRIAL",
    "PHASE I/III TRIAL",
    "NOT APPLICABLE",
    "Unknown"
]

phase_summary = phase_summary.reindex(phase_order).dropna(how="all")

print("---Pregnancy inclusion by phase---")
print(phase_summary)
print()

# visualize trend: do later-stage trials include pregnant women more often?
fig3, ax3 = plt.subplots(figsize=(9, 5))
ax3.plot(
    phase_summary.index,
    phase_summary["inclusion_rate"] * 100,
    marker="o"
)
ax3.set_title("Proportion of trials including pregnant")
ax3.set_ylabel("Inclusion rate (%)")
ax3.set_xlabel("Trial phase")

ax3.tick_params(axis="x", labelrotation=45)
for label in ax3.get_xticklabels():
    label.set_horizontalalignment("right")

plt.tight_layout()
linePath = os.path.join(output, "inclusion_phase.png")
plt.savefig(linePath, dpi=300)
plt.close(fig3)

print(f"Plots saved to '{output}' directory")
