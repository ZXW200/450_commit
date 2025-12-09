import pandas as pd
import matplotlib.pyplot as plt
import re
import os

os.makedirs("CleanedData", exist_ok=True)
os.makedirs("CleanedDataPlt", exist_ok=True)

df = pd.read_csv('CleanedData/cleaned_ictrp.csv')

# Filter for Chagas disease trials by checking multiple fields
# Search is case-insensitive and checks condition names and titles
chagas_df = df[
    df['standardised_condition'].str.contains('Chagas', case=False, na=False) |
    df['original_condition'].str.contains('Chagas', case=False, na=False) |
    df['study_title'].str.contains('Chagas', case=False, na=False)
].copy()

print(f"Found {len(chagas_df)} Chagas disease-related trials")

chagas_df.to_csv("CleanedData/chagas.csv", index=False, encoding='utf-8-sig')
print("Basic data saved successfully")

# Parse registration dates and extract year for temporal analysis
chagas_df['date_registration'] = pd.to_datetime(chagas_df['date_registration'], errors='coerce')
chagas_df['year'] = chagas_df['date_registration'].dt.year

# remove trials with missing dates
chagas_df = chagas_df.dropna(subset=['year']).copy()
print(f"Trials with valid dates: {len(chagas_df)}")

drug_year_list = []

# Extract drug names from intervention field using regex pattern
# Pattern: "Drug: [drug name]" where drug name ends at semicolon, pipe, or newline
for idx, row in chagas_df.iterrows():
    text = row['intervention']
    year = row['year']

    if pd.isna(text):
        continue

    # find all drugs mentioned in the intervention text
    drugs = re.findall(r'Drug:\s*([^;|\n]+)', str(text), flags=re.IGNORECASE)

    for drug in drugs:
        drug_clean = drug.strip()
        drug_year_list.append({'drug': drug_clean, 'year': int(year)})

drug_year_df = pd.DataFrame(drug_year_list)
print(f"Extracted {len(drug_year_df)} drug records")

# Calculate drug usage frequency
drug_counts = drug_year_df['drug'].value_counts()

print("\nTop 10 most common drugs:")
print(drug_counts.head(10))

drug_counts.to_csv("CleanedData/chagas_drugs.csv", header=['Count'], encoding='utf-8-sig')
print("Drug frequency data saved")

# focus on top 5 most frequently studied drugs
top_5_drugs = drug_counts.head(5).index.tolist()
print(f"\nAnalyzing trends for top 5 drugs: {top_5_drugs}")

drug_year_top5 = drug_year_df[drug_year_df['drug'].isin(top_5_drugs)]

# aggregate by year and drug to see temporal trends
trend_data = drug_year_top5.groupby(['year', 'drug']).size().reset_index(name='count')

trend_data.to_csv("CleanedData/chagas_drug_trends.csv", index=False, encoding='utf-8-sig')
print("Drug trend data saved successfully")

print("\nGenerating visualization...")

# configure font settings for plot
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# create side-by-side visualization: trends over time and overall distribution
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']

# Left plot: line chart showing how drug usage changed over years
for i, drug in enumerate(top_5_drugs):
    drug_data = trend_data[trend_data['drug'] == drug]
    ax1.plot(drug_data['year'], drug_data['count'],
            color=colors[i], linewidth=3,
            markersize=10, label=drug, alpha=0.85)

ax1.set_xlabel('Year', fontsize=14, fontweight='bold')
ax1.set_ylabel('Number of Trials', fontsize=14, fontweight='bold')
ax1.set_title('Temporal Trends of Top 5 Drugs',
             fontsize=16, fontweight='bold', pad=15)
ax1.legend(loc='best', fontsize=11, framealpha=0.95, edgecolor='black')
ax1.grid(alpha=0.3, linestyle='--')
ax1.tick_params(labelsize=11)

top_5 = drug_counts.head(5)
colors_pie = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']

values = top_5.values
labels = top_5.index.tolist()

# Right plot: pie chart showing relative proportion of each drug
wedges, texts, autotexts = ax2.pie(
    values,
    labels=labels,
    autopct='%1.1f%%',
    colors=colors_pie,
    startangle=90,
    textprops={'fontsize': 13, 'weight': 'bold'},
    explode=[0.05]*5  # slightly separate each slice
)

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(14)
    autotext.set_weight('bold')

ax2.set_title('Distribution of Top 5 Drugs',
             fontsize=16, fontweight='bold', pad=15)

fig.suptitle('Chagas Disease Drug Analysis: Trends and Distribution',
             fontsize=18, fontweight='bold', y=0.98)

plt.tight_layout()
plt.savefig("CleanedDataPlt/drug_trends.jpg", dpi=300, bbox_inches='tight')
plt.close()

print("\nVisualization completed successfully!")
print("Output file: CleanedDataPlt/drug_trends_and_pie.jpg")
print("\n All ExtractDrug completed ")
