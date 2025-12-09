import pandas as pd
import matplotlib.pyplot as plt
import os

#创建保存图片的目录 Create directory to save plots
output = "CleanedDataPlt"
os.makedirs(output, exist_ok=True)

#清洗后的数据读取 Read cleaned data
data_path = os.path.join("CleanedData", "cleaned_ictrp.csv")
df = pd.read_csv(data_path)

#分类孕妇纳入情况 Classify pregnancy inclusion status
def classify_preg(row):
    raw = str(row.get("pregnant_participants", "")).strip().upper()
    if raw == "INCLUDED":
        return "INCLUDED"
    else:
        return "NOT_INCLUDED"

df["preg_status"] = df.apply(classify_preg, axis=1)

#打印总体情况 Print summary statistics
total = len(df)
included = (df["preg_status"] == "INCLUDED").sum()
not_included = (df["preg_status"] == "NOT_INCLUDED").sum()

print("=== Pregnancy inclusion summary ===")
print(f"Total trials: {total}")
print(f"Trials including pregnant women: {included}")
print(f"Trials NOT including pregnant women: {not_included}")
print(df["preg_status"].value_counts())
print()

#整体孕妇纳入情况饼图 Overall pregnancy inclusion pie chart
statusCounts = df["preg_status"].value_counts()

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
#保存图片Save plot
pie_path = os.path.join(output, "pregnancy_inclusion.png")
plt.savefig(pie_path, dpi=300)
plt.close(fig1) 

#按疾病统计的柱状图 Bar chart: inclusion by disease
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

fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.bar(top_diseases.index, top_diseases.values)
ax2.set_title(f"Number of trials including pregnant women by disease")
ax2.set_ylabel("Number of trials")
ax2.set_xlabel("Disease")

ax2.tick_params(axis="x", labelrotation=45)
for label in ax2.get_xticklabels():
    label.set_horizontalalignment("right")

plt.tight_layout()
#保存图片 Save plot
bar_path = os.path.join(output, "inclusion_disease.png")
plt.savefig(bar_path, dpi=300)
plt.close(fig2)

#各试验阶段孕妇纳入比例折线图 Inclusion rate by phase Line chart
phase_col = "phase"

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
#保存图片Save plot
linePath = os.path.join(output, "inclusion_phase.png")
plt.savefig(linePath, dpi=300)
plt.close(fig3)


print(f"Plots saved to '{output}' directory")
