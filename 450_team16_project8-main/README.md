# NTD Clinical Trials Analysis

**Group 16 - Lancaster University**

## Data Sources

| File | Source |
|------|--------|
| `ictrp_data.csv` | Infectious Diseases Data Observatory (IDDO), University of Oxford |
| `countries.geo.json` | [geo-countries](https://github.com/datasets/geo-countries) - GitHub |

## Requirements

```bash
pip install pandas numpy scikit-learn matplotlib networkx geopandas
```

## Usage

```bash
python Main.py
```

## Scripts & Outputs

| Script | Output |
|--------|--------|
| `CleanData.py` | `CleanedData/cleaned_ictrp.csv` - Cleaned dataset<br>`CleanedData/published_trials.csv` - Published trials subset<br>`CleanedData/country_statistics.csv` - Trials by country<br>`CleanedData/country_Industry.csv` - Industry trials by country |
| `DataFit.py` | `CleanedData/logit_results.csv` - Regression coefficients<br>`CleanedDataPlt/coefficients.jpg` - Coefficient plot |
| `ExtractDrug.py` | `CleanedData/chagas_drugs.csv` - Drug frequency<br>`CleanedData/chagas_drug_trends.csv` - Drug temporal trends<br>`CleanedDataPlt/drug_trends.jpg` - Drug trend chart |
| `Network.py` | `CleanedData/network_statistics.csv` - Network metrics<br>`CleanedDataPlt/network.jpg` - Collaboration network |
| `visualization.py` | `CleanedDataPlt/sponsor_distribution.jpg` - Sponsor distribution<br>`CleanedDataPlt/industry_region.jpg` - Industry regional distribution<br>`CleanedDataPlt/world_heatmap.jpg` - World heatmap<br>`CleanedDataPlt/industry_burden.jpg` - Industry-burden alignment |
| `pregnant.py` | `CleanedDataPlt/pregnancy_inclusion.png` - Inclusion pie chart<br>`CleanedDataPlt/inclusion_disease.png` - Disease bar chart<br>`CleanedDataPlt/inclusion_phase.png` - Phase line chart |


