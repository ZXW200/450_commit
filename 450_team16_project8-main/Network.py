from Mapping import COUNTRY_CODE
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import os

os.makedirs("CleanedData", exist_ok=True)
os.makedirs("CleanedDataPlt", exist_ok=True)

df = pd.read_csv("CleanedData/cleaned_ictrp.csv", encoding="utf-8")

G = nx.Graph()
multi_country_trials = 0

# go through each trial to build network
for idx, row in df.iterrows():
    if pd.isna(row['country_codes']):
        continue

    codes_str = str(row['country_codes']).strip().upper()

    if '|' in codes_str:
        codes = [c.strip() for c in codes_str.split('|')]
    else:
        codes = [codes_str]

    countries = []
    for code in codes:
        if code in COUNTRY_CODE:
            countries.append(COUNTRY_CODE[code])

    # if trial involves multiple countries, create connections
    if len(countries) >= 2:
        multi_country_trials += 1

        for i in range(len(countries)):
            for j in range(i+1, len(countries)):
                if G.has_edge(countries[i], countries[j]):
                    G[countries[i]][countries[j]]['weight'] += 1
                else:
                    G.add_edge(countries[i], countries[j], weight=1)

print(f"Total multi-country trials: {multi_country_trials}")
print(f"Total countries in network: {G.number_of_nodes()}")
print(f"Total collaborative connections: {G.number_of_edges()}")

degree_dict = dict(G.degree())

# calculate weighted degree for each country
weighted_degree = {}
for node in G.nodes():
    total_weight = 0
    for neighbor in G.neighbors(node):
        total_weight += G[node][neighbor]['weight']
    weighted_degree[node] = total_weight

if len(G.nodes()) > 0:
    betweenness = nx.betweenness_centrality(G)
    deg_centrality = nx.degree_centrality(G)

    # create result table with network statistics
    network_stats = pd.DataFrame({
        'Country': list(G.nodes()),
        'Number of partners': [degree_dict[n] for n in G.nodes()],
        'Degree Centrality': [deg_centrality[n] for n in G.nodes()],
        'Total number of partnerships': [weighted_degree[n] for n in G.nodes()],
        'Mediation centrality': [betweenness[n] for n in G.nodes()]
    })

    network_stats = network_stats.sort_values('Number of partners', ascending=False)

    network_stats.to_csv("CleanedData/network_statistics.csv", index=False, encoding="utf-8-sig")
    print("Network statistics saved successfully")

print("\nGenerating network visualization...")

plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(20, 14))

# use spring layout to position nodes
pos = nx.spring_layout(G, k=2.5, iterations=50, seed=42)

# node size based on number of partners
node_sizes = [degree_dict[node] * 200 for node in G.nodes()]

# calculate node colors based on collaboration count
node_collaboration_counts = [weighted_degree[node] for node in G.nodes()]
max_collab = max(node_collaboration_counts) if node_collaboration_counts else 1
min_collab = min(node_collaboration_counts) if node_collaboration_counts else 0

if max_collab > min_collab:
    normalized_collabs = [(count - min_collab) / (max_collab - min_collab)
                          for count in node_collaboration_counts]
else:
    normalized_collabs = [0.5] * len(node_collaboration_counts)

cmap =plt.get_cmap('coolwarm')
node_colors = [cmap(val) for val in normalized_collabs]

# edge width based on collaboration weight
edge_widths = [G[u][v]['weight'] * 0.8 for u, v in G.edges()]

# draw nodes
nx.draw_networkx_nodes(
    G, pos,
    node_size=node_sizes,
    node_color=node_colors,
    edgecolors='black',
    linewidths=2,
    alpha=0.9,
    ax=ax
)

# draw edges
nx.draw_networkx_edges(
    G, pos,
    width=edge_widths,
    alpha=0.3,
    edge_color='gray',
    ax=ax
)

# draw labels
nx.draw_networkx_labels(
    G, pos,
    font_size=10,
    font_weight='bold',
    ax=ax
)

ax.set_title('International Collaboration Network in Clinical Trials',
             fontsize=18, fontweight='bold', pad=20)
ax.axis('off')

sm = cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=min_collab, vmax=max_collab))
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
cbar.set_label('Total Number of Collaborations', fontsize=12, fontweight='bold')

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

plt.tight_layout()
plt.savefig("CleanedDataPlt/network.jpg", dpi=300, bbox_inches='tight')
plt.close()

print("Network visualization completed successfully!")
print("Output file: CleanedDataPlt/collaboration_network.jpg")
print("\n All Network completed ")
