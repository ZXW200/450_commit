import pandas as pd
import matplotlib.pyplot as plt
import re
import os

# Create output directories
# 创建输出文件夹
os.makedirs("CleanedData", exist_ok=True)
os.makedirs("CleanedDataPlt", exist_ok=True)

# 读取数据 Load Data 
# Read the cleaned clinical trial data
# 读取清洗后的临床试验数据
df = pd.read_csv('CleanedData/cleaned_ictrp.csv')

# 筛选Chagas病相关试验 Screen for Chagas Disease Trials 
# Filter Chagas disease 
# 筛选与Chagas病相关的试验：
chagas_df = df[
    df['standardised_condition'].str.contains('Chagas', case=False, na=False) |
    df['original_condition'].str.contains('Chagas', case=False, na=False) |
    df['study_title'].str.contains('Chagas', case=False, na=False)
].copy()

print(f"Found {len(chagas_df)} Chagas disease-related trials")

# 保存基本信息 Save Basic Information 
# Save the filtered Chagas trial data to CSV
# 将筛选后的Chagas试验数据保存为CSV
chagas_df.to_csv("CleanedData/chagas.csv", index=False, encoding='utf-8-sig')
print("Basic data saved successfully")

# 处理日期 Process Date 
# Convert registration date to datetime format and extract year
# 将注册日期转换为日期时间格式并提取年份
chagas_df['date_registration'] = pd.to_datetime(chagas_df['date_registration'], errors='coerce')
chagas_df['year'] = chagas_df['date_registration'].dt.year

# Remove records without valid dates
# 移除没有有效日期的记录
chagas_df = chagas_df.dropna(subset=['year']).copy()
print(f"Trials with valid dates: {len(chagas_df)}")

# 提取药物信息 Extract Drug Information 
drug_year_list = []

# Iterate through each trial record
# 遍历每条试验记录
for idx, row in chagas_df.iterrows():
    text = row['intervention']  # Get intervention text / 获取干预文本
    year = row['year']  # Get registration year / 获取注册年份
    
    # Skip if intervention field is empty
    # 如果干预字段为空则跳过
    if pd.isna(text):
        continue
    
    # Extract drug names using regex pattern 'Drug: [drug_name]'
    # 使用正则表达式模式'Drug: [药物名称]'提取药物名称
    drugs = re.findall(r'Drug:\s*([^;|\n]+)', str(text), flags=re.IGNORECASE)
    
    # Add each drug with its year to the list
    # 将每个药物及其年份添加到列表中
    for drug in drugs:
        drug_clean = drug.strip()  # Remove leading/trailing whitespace / 移除首尾空格
        drug_year_list.append({'drug': drug_clean, 'year': int(year)})

# Convert list to DataFrame
# 将列表转换为DataFrame
drug_year_df = pd.DataFrame(drug_year_list)
print(f"Extracted {len(drug_year_df)} drug records")

# 统计最常见的药物 Count Most Common Drugs 
# Count the frequency of each drug
# 统计每种药物的出现频率
drug_counts = drug_year_df['drug'].value_counts()

# Display top 10 drugs
# 显示前10种药物
print("\nTop 10 most common drugs:")
print(drug_counts.head(10))

# Save drug frequency data to CSV
# 将药物频率数据保存为CSV
drug_counts.to_csv("CleanedData/chagas_drugs.csv", header=['Count'], encoding='utf-8-sig')
print("Drug frequency data saved")

# 按年份统计趋势 Analyze Trends by Year
# Select top 5 most common drugs for trend analysis
# 选择前5种最常见的药物进行趋势分析
top_5_drugs = drug_counts.head(5).index.tolist()
print(f"\nAnalyzing trends for top 5 drugs: {top_5_drugs}")

# Filter data for these 5 drugs
# 筛选这5种药物的数据
drug_year_top5 = drug_year_df[drug_year_df['drug'].isin(top_5_drugs)]

# Group by year and drug, then count occurrences
# 按年份和药物分组，然后计数
trend_data = drug_year_top5.groupby(['year', 'drug']).size().reset_index(name='count')

# Save trend data to CSV
# 将趋势数据保存为CSV
trend_data.to_csv("CleanedData/chagas_drug_trends.csv", index=False, encoding='utf-8-sig')
print("Drug trend data saved successfully")

# 可视化 Visualization
print("\nGenerating visualization...")

# Set plotting style
# 设置绘图样式
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 创建组合图 Create Combined Figure
# Create figure with 1 row and 2 columns: left for trends, right for pie chart
# 创建1行2列的图形：左边是趋势图，右边是饼图
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

# 左图：时间趋势 Left: Temporal Trends 
# Define colors and markers for each drug
# 为每种药物定义颜色和标记
colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']


# Plot trend line for each drug
# 为每种药物绘制趋势线
for i, drug in enumerate(top_5_drugs):
    drug_data = trend_data[trend_data['drug'] == drug]
    ax1.plot(drug_data['year'], drug_data['count'], 
            color=colors[i], linewidth=3, 
            markersize=10, label=drug, alpha=0.85)

# Configure left plot
# 配置左图
ax1.set_xlabel('Year', fontsize=14, fontweight='bold')
ax1.set_ylabel('Number of Trials', fontsize=14, fontweight='bold')
ax1.set_title('Temporal Trends of Top 5 Drugs', 
             fontsize=16, fontweight='bold', pad=15)
ax1.legend(loc='best', fontsize=11, framealpha=0.95, edgecolor='black')
ax1.grid(alpha=0.3, linestyle='--')
ax1.tick_params(labelsize=11)

# 右图：饼图 Right: Pie Chart 
# Get top 5 drug counts 
# 获取前5种药物的计数
top_5 = drug_counts.head(5)
colors_pie = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']

# Extract values and labels from Series
# 从Series中提取值和标签
values = top_5.values  # Get the count values / 获取计数值
labels = top_5.index.tolist()  # Get the drug names / 获取药物名称

# Create pie chart (without shadow effect)
# 创建饼图（无阴影效果）
wedges, texts, autotexts = ax2.pie(
    values, 
    labels=labels,
    autopct='%1.1f%%',  # Show percentage / 显示百分比
    colors=colors_pie,
    startangle=90,  # Start angle / 起始角度
    textprops={'fontsize': 13, 'weight': 'bold'},
    explode=[0.05]*5  # Separate slices slightly / 稍微分离切片
)

# Style percentage text
# 设置百分比文本样式
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(14)
    autotext.set_weight('bold')

# Configure right plot
# 配置右图
ax2.set_title('Distribution of Top 5 Drugs', 
             fontsize=16, fontweight='bold', pad=15)

# 添加总标题 Add Overall Title
fig.suptitle('Chagas Disease Drug Analysis: Trends and Distribution', 
             fontsize=18, fontweight='bold', y=0.98)

# 保存图表 Save Figure 
plt.tight_layout()
plt.savefig("CleanedDataPlt/drug_trends.jpg", dpi=300, bbox_inches='tight')
plt.close()

print("\nVisualization completed successfully!")
print("Output file: CleanedDataPlt/drug_trends_and_pie.jpg")
print("\n All ExtractDrug completed ")
