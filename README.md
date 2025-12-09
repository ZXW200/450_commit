# SCC451 Machine Learning Coursework

## Requirements

```
Python 3.10+
```

### Task 1
```
pip install numpy pandas matplotlib seaborn scikit-learn hdbscan
```

### Task 2
```
pip install torch torchvision timm umap-learn kagglehub
```

## How to Run

### Task 1: Basel Climate Dataset
```bash
cd task1
python main.py
```

**Output:** Results saved in `history/run_pipeline_<timestamp>/`
- `prep/clean_data.csv` - Preprocessed data
- `prep/figures/` - Correlation matrix, outlier boxplots
- `cluster/figures/` - Clustering visualizations (PCA, t-SNE)
- `cluster/cluster_res.json` - Clustering metrics

### Task 2: Image Classification
```bash
cd task2
python main.py
```

**Output:** Results saved in `history/run_pipeline_<timestamp>/`
- `figures/<dataset>/<model>/` - UMAP visualizations, confusion matrices
- `results/<dataset>/<model>/` - Classification metrics (accuracy, F1, etc.)

**Note:** Datasets (Cats vs Dogs, Food-101) will be downloaded automatically via kagglehub.

## File Structure

```
task1/
├── main.py          # Entry point
├── preprocessing.py # Data cleaning, scaling
├── cluster.py       # K-Means, HDBSCAN
└── utils.py         # Helper functions

task2/
├── main.py          # Entry point
├── preprocessing.py # Image loading, transforms
├── models.py        # ResNet50, DenseNet121, DinoV2
├── feature_extraction.py
├── dimensionality.py # UMAP
├── cluster.py       # K-Means clustering
├── classification.py # Linear classifier, KNN
└── utils.py         # Helper functions
```
