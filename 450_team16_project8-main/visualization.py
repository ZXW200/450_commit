import pandas as pd
import matplotlib.pyplot as plt
import os
from Mapping import COUNTRY_CODE, HIGH_BURDEN_COUNTRIES
import geopandas as gpd
from scipy.stats import chi2_contingency
# 创建输出文件夹 Create output folder
os.makedirs("CleanedDataPlt", exist_ok=True)

# 读取数据 Read Data
df = pd.read_csv("CleanedData/cleaned_ictrp.csv", encoding="utf-8")
print(f"Total trials: {len(df)}")

# 筛选已发表的试验 Selected published 
published_df = df[df["results_posted"] == True]
print(f"Published: {len(published_df)}")
print(f"Unpublished: {len(df) - len(published_df)}\n")

# 统计赞助商类别  Statistics on sponsor categories
all_sponsor_counts = df["sponsor_category"].value_counts()
published_sponsor_counts = published_df["sponsor_category"].value_counts()

# 指定类别颜色 Specify category color
color_map = {
    'Industry': '#3498db',
    'Non-profit': '#e74c3c',
    'Government': '#2ecc71',
    'Other': '#95a5a6'
}

# 绘制对比图 Draw a comparison chart
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

for data, ax, title in [(all_sponsor_counts, ax1, 'All Trials'),
                        (published_sponsor_counts, ax2, 'Published Trials')]:

    # 根据类别获取对应颜色 Obtain corresponding colors based on categories
    colors = [color_map[cat] for cat in data.index]

    wedges, texts, autotexts = ax.pie(
        data.values,
        labels=data.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 10}
    )

    for autotext in autotexts:
        autotext.set_color('white')

    labels = [f'{cat}: {count}' for cat, count in zip(data.index, data.values)]
    ax.legend(labels, loc='upper left', fontsize=9)
    ax.set_title(title, fontsize=13, fontweight='bold')

fig.suptitle('Sponsor Category Distribution', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('CleanedDataPlt/sponsor_distribution.jpg', dpi=300, bbox_inches='tight')
plt.close()

industry_stats = pd.read_csv("CleanedData/country_Industry.csv", encoding="utf-8-sig")

# 添加负担分类列 Add burden classification column
industry_stats['burden_level'] = industry_stats['country'].apply(
    lambda x: 'High Burden' if x in HIGH_BURDEN_COUNTRIES else 'Normal'
)

# 保存更新后的文件 Save
industry_stats.to_csv("CleanedData/country_Industry_HighBurden.csv",
                      index=False, encoding="utf-8-sig")
burden_sum = industry_stats.groupby('burden_level')['count'].sum() # count burden level

# 画图 plt
fig, ax = plt.subplots(figsize=(10, 7))
ax.pie(burden_sum.values, labels=burden_sum.index, autopct='%1.1f%%',
       colors=['#e74c3c', '#3498db'], startangle=90)
ax.set_title('Industry Trials by Region', fontsize=14, fontweight='bold')
plt.savefig('CleanedDataPlt/industry_region.jpg', dpi=300, bbox_inches='tight')
plt.close()
print("Figure saved successfully!")

# 创建世界地图热力图 Create world map heatmap
country_stats = pd.read_csv("CleanedData/country_statistics.csv", encoding="utf-8-sig")

# 反转映射：国家名 -> ISO代码 Reverse mapping: country name -> ISO code
name_to_code = {v: k for k, v in COUNTRY_CODE.items()}
country_stats['iso_alpha'] = country_stats['country'].map(name_to_code)

# 读取地理数据 Read geographic data
world = gpd.read_file('countries.geo.json')

# 合并数据 Merge data
world = world.merge(country_stats, left_on='id', right_on='iso_alpha', how='left')

# 绘制地图 Plot map
fig, ax = plt.subplots(1, 1, figsize=(20, 10))
world.plot(column='count', ax=ax, legend=True, cmap='YlOrRd',
           missing_kwds={'color': 'lightgrey', 'label': 'No data'},
           edgecolor='black', linewidth=0.5,
           legend_kwds={'label': 'Number of NTD Clinical Trials', 'shrink': 0.5})
ax.set_title('World Map: Number of NTD Clinical Trials by Country',
             fontsize=16, fontweight='bold', pad=20)
ax.axis('off')

# 保存JPG Save JPG
plt.savefig('CleanedDataPlt/world_heatmap.jpg', dpi=300, bbox_inches='tight')
plt.close()
print("World heatmap saved as CleanedDataPlt/world_heatmap.jpg")

# ============================================================================
# 新增：产业界资助与高负担国家关系分析 
# NEW: Industry funding vs high burden countries analysis
# ============================================================================
print("\nAnalyzing Industry funding alignment with high burden countries...")

# 提取产业界试验的国家 Extract countries from Industry trials
industry_df = df[df['sponsor_category'] == 'Industry'].copy()
industry_countries = []
for codes in industry_df['country_codes'].dropna():
    codes_str = str(codes).strip().upper()
    if '|' in codes_str:
        codes_list = [c.strip() for c in codes_str.split('|')]
    else:
        codes_list = [codes_str]
    for code in codes_list:
        if code in COUNTRY_CODE:
            industry_countries.append(COUNTRY_CODE[code])

from collections import Counter
industry_country_counts = Counter(industry_countries)

# 提取所有试验的国家 Extract all countries
all_countries = []
for codes in df['country_codes'].dropna():
    codes_str = str(codes).strip().upper()
    if '|' in codes_str:
        codes_list = [c.strip() for c in codes_str.split('|')]
    else:
        codes_list = [codes_str]
    for code in codes_list:
        if code in COUNTRY_CODE:
            all_countries.append(COUNTRY_CODE[code])

all_country_counts = Counter(all_countries)

# 计算高负担国家的统计 Calculate high burden statistics
high_burden_stats = []
for country in HIGH_BURDEN_COUNTRIES:
    total = all_country_counts.get(country, 0)
    industry = industry_country_counts.get(country, 0)
    if total > 0:
        pct = (industry / total) * 100
        high_burden_stats.append({
            'country': country,
            'total': total,
            'industry': industry,
            'percentage': pct
        })

burden_df = pd.DataFrame(high_burden_stats).sort_values('industry', ascending=False)

# 计算总体比例 Calculate overall proportions
total_industry = sum(industry_country_counts.values())
total_all = sum(all_country_counts.values())
high_burden_industry = sum(row['industry'] for row in high_burden_stats)
high_burden_all = sum(row['total'] for row in high_burden_stats)

# 保存统计数据 Save statistics
burden_df.to_csv("CleanedData/industry_burden.csv", index=False, encoding="utf-8-sig")

# 获取所有国家的产业界资助比例（包括非高负担国家的前几名）
# Get Industry funding % for all countries (including top non-high-burden countries)
all_country_stats = []
for country, total in all_country_counts.most_common(15):  # 取前15个国家
    industry = industry_country_counts.get(country, 0)
    if total > 0:
        pct = (industry / total) * 100
        is_high_burden = country in HIGH_BURDEN_COUNTRIES
        all_country_stats.append({
            'country': country,
            'total': total,
            'industry': industry,
            'percentage': pct,
            'is_high_burden': is_high_burden
        })

all_burden_df = pd.DataFrame(all_country_stats).sort_values('industry', ascending=True)

# 绘制单一图表：产业界资助比例（红色=高负担，蓝色=其他）
# Plot single chart: Industry funding % (Red=High Burden, Blue=Other)
fig, ax = plt.subplots(1, 1, figsize=(12, 8))

if len(all_burden_df) > 0:
    # 根据是否为高负担国家设置颜色 Set colors based on high burden status
    colors = ['#e74c3c' if row['is_high_burden'] else '#3498db' 
              for _, row in all_burden_df.iterrows()]
    
    bars = ax.barh(all_burden_df['country'], all_burden_df['percentage'], 
                   color=colors, edgecolor='black', linewidth=1, alpha=0.85)
    
    for bar, pct in zip(bars, all_burden_df['percentage']):
        ax.text(bar.get_width() + 0.5,bar.get_y() + bar.get_height() / 2,f'{pct:.1f}%',va='center', ha='left',fontsize=9)
        
    ax.set_xlabel('Industry Funding %', fontsize=13, fontweight='bold')
    ax.set_ylabel('Country', fontsize=13, fontweight='bold')
    ax.set_title('Industry Funding Percentage by Country', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # 添加图例 Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#e74c3c', edgecolor='black', label='High Burden Countries ', alpha=0.85),
        Patch(facecolor='#3498db', edgecolor='black', label='Other Countries ', alpha=0.85)
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11, 
              framealpha=0.95, edgecolor='black')
    
    # 添加平均线 Add average line for high burden countries
    high_burden_avg = burden_df['percentage'].mean() if len(burden_df) > 0 else 0
    ax.axvline(high_burden_avg, color='red', linestyle='--', linewidth=2, 
               alpha=0.6, label=f'High Burden Avg: {high_burden_avg:.1f}%')

plt.tight_layout()
plt.savefig('CleanedDataPlt/industry_burden.jpg', dpi=300, bbox_inches='tight')
plt.close()

# 计算统计数据用于打印 Calculate statistics for printing
high_burden_count = sum(industry_country_counts.get(c, 0) for c in HIGH_BURDEN_COUNTRIES)
other_count = total_industry - high_burden_count
high_burden_all_count = sum(all_country_counts.get(c, 0) for c in HIGH_BURDEN_COUNTRIES)
other_all_count = total_all - high_burden_all_count
# Chi-square test for independence
table = [
    [high_burden_count, other_count],
    [high_burden_all_count - high_burden_count, other_all_count - other_count]
]

# calculate chi-square
chi2, p, _, _ = chi2_contingency(table)
# 打印统计信息 Print statistics
print(f"\nIndustry funding analysis / 产业界资助分析:")
print(f"  Total Industry trials: {len(industry_df)} ({len(industry_df)/len(df)*100:.2f}%)")
print(f"  High burden countries: {high_burden_count}/{high_burden_all_count} ({high_burden_count/high_burden_all_count*100:.2f}%)")
print(f"  Other countries: {other_count}/{other_all_count} ({other_count/other_all_count*100:.2f}%)")
print(f"  Alignment gap: {(high_burden_count/high_burden_all_count*100) - (other_count/other_all_count*100):.2f} percentage points")
print("Industry-burden alignment analysis saved!")

print("\n All visualizations completed ")
