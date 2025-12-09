from Mapping import COUNTRY_CODE
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import os

# Create output directories
# 创建输出文件夹
os.makedirs("CleanedData", exist_ok=True)
os.makedirs("CleanedDataPlt", exist_ok=True)

#读取数据 Load Data
# Read the cleaned clinical trial data
# 读取清洗后的临床试验数据
df = pd.read_csv("CleanedData/cleaned_ictrp.csv", encoding="utf-8")

# 构建网络图 Build Network Graph
# Initialize an empty undirected graph
# 初始化一个空的无向图
G = nx.Graph()
multi_country_trials = 0

# Iterate through each trial record
# 遍历每个试验记录
for idx, row in df.iterrows():
    # Skip if country_codes field is empty
    # 如果国家代码字段为空则跳过
    if pd.isna(row['country_codes']):
        continue
    
    # Extract and process country codes
    # 提取并处理国家代码
    codes_str = str(row['country_codes']).strip().upper()
    
    # Split multiple country codes separated by '|'
    # 分割由'|'分隔的多个国家代码
    if '|' in codes_str:
        codes = [c.strip() for c in codes_str.split('|')]
    else:
        codes = [codes_str]
    
    # Convert country codes to country names
    # 将国家代码转换为国家名称
    countries = []
    for code in codes:
        if code in COUNTRY_CODE:
            countries.append(COUNTRY_CODE[code])
    
    # If multiple countries are involved, it's a collaborative trial
    # 如果涉及多个国家，则为合作试验
    if len(countries) >= 2:
        multi_country_trials += 1
        
        # Establish connections between all country pairs
        # 在所有国家对之间建立连接
        for i in range(len(countries)):
            for j in range(i+1, len(countries)):
                # If edge already exists, increase weight; otherwise create new edge
                # 如果边已存在，增加权重；否则创建新边
                if G.has_edge(countries[i], countries[j]):
                    G[countries[i]][countries[j]]['weight'] += 1
                else:
                    G.add_edge(countries[i], countries[j], weight=1)

# Display network statistics
# 显示网络统计信息
print(f"Total multi-country trials: {multi_country_trials}")
print(f"Total countries in network: {G.number_of_nodes()}")
print(f"Total collaborative connections: {G.number_of_edges()}")

# 计算网络指标 Calculate Network Metrics
# Calculate degree (number of partners) for each country
# 计算每个国家的度（合作伙伴数量）
degree_dict = dict(G.degree())
# Calculate degree for each country
degree_dict = dict(G.degree())
# Calculate weighted degree (total number of collaborations)
# 计算加权度（总合作次数）
weighted_degree = {}
for node in G.nodes():
    total_weight = 0
    # Iterate through all neighbors and accumulate their weights
    # 遍历当前国家的所有邻居，并累加它们的权重
    for neighbor in G.neighbors(node):
        total_weight += G[node][neighbor]['weight']
    weighted_degree[node] = total_weight

# Calculate betweenness centrality (which country is the most central hub)
# 计算中介中心性（哪个国家是最核心的枢纽）
if len(G.nodes()) > 0:
    betweenness = nx.betweenness_centrality(G)
    
    # Create result table with network statistics
    # 创建包含网络统计信息的结果表
    network_stats = pd.DataFrame({
        'Country': list(G.nodes()),
        'Number of partners': [degree_dict[n] for n in G.nodes()],  # 合作伙伴数
        'Degree Centrality': [deg_centrality[n] for n in G.nodes()], #度中心性
        'Total number of partnerships': [weighted_degree[n] for n in G.nodes()],  # 总合作次数
        'Mediation centrality': [betweenness[n] for n in G.nodes()]  # 中介中心性
    })
    
    # Sort by number of partners in descending order
    # 按合作伙伴数降序排序
    network_stats = network_stats.sort_values('Number of partners', ascending=False)
    
    # Save results to CSV
    # 将结果保存为CSV文件
    network_stats.to_csv("CleanedData/network_statistics.csv", index=False, encoding="utf-8-sig")
    print("Network statistics saved successfully")

# 可视化网络图 Visualize Network 
print("\nGenerating network visualization...")

# Set plotting style
# 设置绘图样式
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Create figure with larger size for better visibility
# 创建较大尺寸的图形以提高可见性
fig, ax = plt.subplots(figsize=(20, 14))

# Use spring layout algorithm for node positioning
# 使用弹簧布局算法进行节点定位
# k: optimal distance between nodes / 节点间的最优距离
# iterations: number of optimization iterations / 优化迭代次数
# seed: random seed for reproducibility / 用于可重复性的随机种子
pos = nx.spring_layout(G, k=2.5, iterations=50, seed=42)

# Calculate node sizes based on degree (number of partners)
# 根据度（合作伙伴数量）计算节点大小
node_sizes = [degree_dict[node] * 200 for node in G.nodes()]

# Calculate node colors based on total collaborations (blue to red gradient)
# 根据总合作次数计算节点颜色（蓝色到红色渐变）
node_collaboration_counts = [weighted_degree[node] for node in G.nodes()]
max_collab = max(node_collaboration_counts) if node_collaboration_counts else 1
min_collab = min(node_collaboration_counts) if node_collaboration_counts else 0

# Normalize collaboration counts to 0-1 range for colormap
# 将合作次数归一化到0-1范围以用于颜色映射
if max_collab > min_collab:
    normalized_collabs = [(count - min_collab) / (max_collab - min_collab) 
                          for count in node_collaboration_counts]
else:
    normalized_collabs = [0.5] * len(node_collaboration_counts)

# Use colormap: blue (low collaboration) to red (high collaboration)
# 使用颜色映射：蓝色（低合作）到红色（高合作）
cmap =plt.get_cmap('coolwarm')  # Blue to Red colormap / 蓝到红的颜色映射
node_colors = [cmap(val) for val in normalized_collabs]

# Calculate edge widths based on collaboration weight
# 根据合作权重计算边的宽度
edge_widths = [G[u][v]['weight'] * 0.8 for u, v in G.edges()]

# Draw nodes with size and color based on collaborations
# 绘制节点，大小和颜色基于合作次数
nx.draw_networkx_nodes(
    G, pos, 
    node_size=node_sizes, 
    node_color=node_colors,  # Color based on collaboration count / 基于合作次数的颜色
    edgecolors='black', 
    linewidths=2, 
    alpha=0.9, 
    ax=ax
)

# Draw edges with width proportional to collaboration frequency
# 绘制边，宽度与合作频率成正比
nx.draw_networkx_edges(
    G, pos, 
    width=edge_widths, 
    alpha=0.3, 
    edge_color='gray', 
    ax=ax
)

# Draw country name labels
# 绘制国家名称标签
nx.draw_networkx_labels(
    G, pos, 
    font_size=10, 
    font_weight='bold', 
    ax=ax
)

# Set title and configure axes
# 设置标题并配置坐标轴
ax.set_title('International Collaboration Network in Clinical Trials', 
             fontsize=18, fontweight='bold', pad=20)
ax.axis('off')  # Hide axes / 隐藏坐标轴

# Add colorbar to show collaboration scale
# 添加颜色条以显示合作规模
sm = cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=min_collab, vmax=max_collab))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
cbar.set_label('Total Number of Collaborations', fontsize=12, fontweight='bold')

# Add legend explaining visualization
# 添加图例说明可视化
legend_text = (
    'Node size: Number of collaboration partners\n'
    'Node color: Total collaborations (Blue=Low, Red=High)\n'
    'Edge width: Frequency of collaborations'
)
ax.text(0.02, 0.98, legend_text, 
        transform=ax.transAxes, 
        fontsize=11, 
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Save figure with high resolution
# 以高分辨率保存图形
plt.tight_layout()
plt.savefig("CleanedDataPlt/network.jpg", dpi=300, bbox_inches='tight')
plt.close()

print("Network visualization completed successfully!")
print("Output file: CleanedDataPlt/collaboration_network.jpg")
print("\n All Network completed ")
