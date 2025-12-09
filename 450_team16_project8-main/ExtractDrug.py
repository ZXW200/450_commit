import pandas as pd
import matplotlib.pyplot as plt
import re
import os

os.makedirs("CleanedData", exist_ok=True)
os.makedirs("CleanedDataPlt", exist_ok=True)

df = pd.read_csv('CleanedData/cleaned_ictrp.csv')

# find trials about Chagas disease
chagas_df = df[
    df['standardised_condition'].str.contains('Chagas', case=False, na=False) |
    df['original_condition'].str.contains('Chagas', case=False, na=False) |
    df['study_title'].str.contains('Chagas', case=False, na=False)
].copy()

print(f"Found {len(chagas_df)} Chagas disease-related trials")

chagas_df.to_csv("CleanedData/chagas.csv", index=False, encoding='utf-8-sig')
print("Basic data saved successfully")

chagas_df['date_registration'] = pd.to_datetime(chagas_df['date_registration'], errors='coerce')
chagas_df['year'] = chagas_df['date_registration'].dt.year

chagas_df = chagas_df.dropna(subset=['year']).copy()
print(f"Trials with valid dates: {len(chagas_df)}")

drug_year_list = []

# go through each trial and extract drug names
for idx, row in chagas_df.iterrows():
    text = row['intervention']
    year = row['year']

    if pd.isna(text):
        continue

    drugs = re.findall(r'Drug:\s*([^;|\n]+)', str(text), flags=re.IGNORECASE)

    for drug in drugs:
        drug_clean = drug.strip()
        drug_year_list.append({'drug': drug_clean, 'year': int(year)})

drug_year_df = pd.DataFrame(drug_year_list)
print(f"Extracted {len(drug_year_df)} drug records")

# count how many times each drug appears
drug_counts = drug_year_df['drug'].value_counts()

print("\nTop 10 most common drugs:")
print(drug_counts.head(10))

drug_counts.to_csv("CleanedData/chagas_drugs.csv", header=['Count'], encoding='utf-8-sig')
print("Drug frequency data saved")

# get top 5 drugs for analysis
top_5_drugs = drug_counts.head(5).index.tolist()
print(f"\nAnalyzing trends for top 5 drugs: {top_5_drugs}")

drug_year_top5 = drug_year_df[drug_year_df['drug'].isin(top_5_drugs)]

trend_data = drug_year_top5.groupby(['year', 'drug']).size().reset_index(name='count')

trend_data.to_csv("CleanedData/chagas_drug_trends.csv", index=False, encoding='utf-8-sig')
print("Drug trend data saved successfully")

print("\nGenerating visualization...")

plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']

# draw line chart for drug trends over years
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

# draw pie chart for drug distribution
wedges, texts, autotexts = ax2.pie(
    values,
    labels=labels,
    autopct='%1.1f%%',
    colors=colors_pie,
    startangle=90,
    textprops={'fontsize': 13, 'weight': 'bold'},
    explode=[0.05]*5
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
