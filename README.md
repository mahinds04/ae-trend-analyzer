# AE Trend Analyzer

[![CI - QA & Smoke Tests](https://github.com/mahinds04/ae-trend-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/mahinds04/ae-trend-analyzer/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An interactive **Adverse Event (AE) Trend Analyzer** that processes FDA FAERS (Adverse Event Reporting System) data and drug review datasets to provide comprehensive pharmaceutical safety insights through an intuitive Streamlit dashboard.

## 🚀 Features

- **📊 Interactive Dashboard**: Real-time filtering and visualization
- **🏥 FAERS Integration**: Official FDA adverse event data processing
- **💊 Multi-source Analysis**: WebMD + UCI drug review datasets
- **🔍 Advanced Filtering**: By drug, reaction, and time period
- **📈 Trend Visualization**: Professional charts with Plotly
- **🚨 Anomaly Detection**: STL decomposition, rolling Z-score, and Prophet methods
- **💡 Smart Insights**: Automated spike detection and ranking
- **🧪 Quality Assurance**: Automated testing and validation
- **⚡ Memory Optimized**: Efficient processing of large datasets

## 📸 Screenshots

*Dashboard screenshots coming soon*

## 🛠️ Quick Start

### Prerequisites
- Python 3.10+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/mahinds04/ae-trend-analyzer.git
cd ae-trend-analyzer

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Data Setup

1. **Download FAERS Data**: [FDA FAERS Quarterly Files](https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html)
2. **Download Review Datasets**: 
   - [WebMD Drug Reviews](https://www.kaggle.com/datasets/rohanharode07/webmd-drug-reviews-dataset)
   - [UCI ML Drug Reviews](https://www.kaggle.com/datasets/jessicali9530/kuc-hackathon-winter-2018)
3. **Place files** in `data/raw/` following the structure below:

**FAERS Directory Examples** (matching loader expectations):
```
data/raw/faers_ascii_2024q1/    # Quarters: 2024q1, 2024q2, 2024q3, 2024Q4
data/raw/faers_ascii_2013q1/    # Older format: 2013q1, 2013q2, 2013q3, 2013q4  
data/raw/faers_ascii_2023q4/    # Any year-quarter combination supported
```

**Required Files Per Quarter**:
- `ASCII/DEMO*.txt` (demographics)
- `ASCII/DRUG*.txt` (drug information) 
- `ASCII/REAC*.txt` (reactions)
- Plus: INDI, OUTC, RPSR, THER files

### Run the Application

**Option 1: Simple Scripts (Recommended)**
```bash
# Process the data
python run_etl.py

# Launch dashboard (full data)
python run_dashboard.py

# Launch dashboard (sample mode)
python run_dashboard.py --sample
```

**Option 2: Direct Module Execution**
```bash
# Process the data
python -m src.etl.build_all

# Launch dashboard
streamlit run src/app/streamlit_mvp.py
```

Open http://localhost:8501 in your browser!

### Instant Demo Mode

For quick testing without full datasets:
```bash
# Run with sample data (≈50 rows)
streamlit run src/app/streamlit_mvp.py -- --sample

# Or set environment variable
set AE_SAMPLE=1  # Windows
export AE_SAMPLE=1  # Linux/Mac
streamlit run src/app/streamlit_mvp.py
```

## 🔍 Anomaly Detection & Insights

The AE Trend Analyzer includes sophisticated anomaly detection capabilities to identify unusual spikes in adverse event reporting patterns.

### Detection Methods

#### 1. **STL Decomposition** (Recommended)
- **Best for**: Seasonal data with ≥12 months
- **Approach**: Separates trend, seasonal, and residual components
- **Advantages**: Handles seasonality, robust to outliers
- **Usage**: Default method in dashboard

#### 2. **Rolling Z-Score**
- **Best for**: Any time series length
- **Approach**: Statistical deviation from rolling mean
- **Advantages**: Simple, fast, works with short series
- **Usage**: Fallback method, good for trend-only data

#### 3. **Prophet** (Optional)
- **Best for**: Complex seasonality, ≥24 months
- **Approach**: Facebook's ML-based forecasting
- **Advantages**: Handles holidays, multiple seasonalities
- **Installation**: `pip install prophet` (optional dependency)

### Quick Example

```python
from src.analysis.anomaly import detect_anomalies, ensure_monthly_index
from src.analysis.insights import summarize_top_spikes_overall

# Load and process monthly data
import pandas as pd
df = pd.read_csv("data/processed/monthly_counts.csv")
series = ensure_monthly_index(df, 'ym', 'count')

# Detect anomalies using STL method
anomalies = detect_anomalies(series, method="stl", z_thresh=2.5)
print(f"Detected {anomalies['is_spike'].sum()} spikes")

# Get top 3 spikes with insights
insights = summarize_top_spikes_overall(method="stl", k=3)
print(f"Top spike: {insights['top_spikes'][0]['date']} with z-score {insights['top_spikes'][0]['z']:.2f}")
```

### Dashboard Integration

The Streamlit dashboard automatically:

1. **Analyzes Current Filters**: Shows spikes for selected drug/reaction
2. **Visual Overlays**: Red diamond markers on detected spike months
3. **Insights Panel**: Expandable section with top 3 spikes for:
   - Overall trends
   - Current drug (if selected)
   - Current reaction (if selected)
4. **Method Selection**: Choose detection method in sidebar

### Fallback Behavior

- **Insufficient Data**: STL requires ≥24 months; automatically falls back to rolling Z-score
- **Missing Libraries**: Prophet is optional; gracefully falls back to STL or rolling Z-score
- **Error Handling**: Robust error handling ensures dashboard always functions

### Performance Notes

- **STL**: Best balance of accuracy and performance
- **Rolling Z**: Fastest, suitable for real-time analysis
- **Prophet**: Most accurate but requires more computation time
- **Data Requirements**: Ideal performance with ≥12 months of continuous monthly data

## 🛠️ Troubleshooting

### Common Issues

**Pandas/Encoding Errors:**
```
UnicodeDecodeError: 'utf-8' codec can't decode
```
- **Solution**: FAERS files use different encodings. The loader automatically tries `latin-1` and `cp1252` fallbacks.

**Memory Issues:**
```
MemoryError or system slowdown with large files
```
- **Solution**: Large DRUG files (>100MB) trigger warnings. Consider processing quarters individually or increase system RAM.

**Date Parsing Warnings:**
```
UserWarning: Could not infer format, so each element will be parsed individually
```
- **Solution**: Normal for FAERS data with mixed date formats. The system handles YYYYMMDD, YYYY-MM-DD, and other variations.

**Missing File Errors:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/raw/...'
```
- **Solution**: Ensure FAERS quarters follow naming pattern `faers_ascii_YYYYqN/` and contain `ASCII/` subdirectory.

## Overview

This project provides a complete ETL pipeline to:

1. **Load FAERS Data**: Auto-detect and load FAERS ASCII tables per quarter (DEMO.txt, REAC.txt, DRUG.txt, etc.)
2. **Normalize Schemas**: Handle differences between years (2013 vs 2024 naming conventions)
3. **Build Time-indexed Dataset**: Create monthly counts overall, per drug, and per MedDRA PT
4. **Process Reviews**: Load WebMD + UCI review datasets and extract AE mentions using NLP
5. **Generate Insights**: Create visualizations and aggregated statistics

## Project Structure

```
ae-trend-analyzer/
├── data/
│   ├── raw/                    # FAERS quarters + review datasets
│   └── processed/              # Generated output files
├── reports/
│   └── figures/               # Generated plots
├── src/
│   ├── etl/
│   │   ├── faers_loader.py    # FAERS data loading and normalization
│   │   ├── reviews_loader.py  # Review data processing and AE extraction
│   │   └── build_all.py       # Main ETL orchestrator
│   └── analysis/
│       └── aggregate.py       # Monthly aggregations and plotting
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository
2. Install Python 3.10+
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

Run the complete ETL pipeline:

```bash
python -m src.etl.build_all
```

This will:
- Discover and process all FAERS quarterly folders in `data/raw/`
- Load and process review datasets
- Generate monthly aggregations
- Create trend visualizations
- Save all outputs to `data/processed/` and `reports/figures/`

### Quick QA

Run quality assurance checks on processed data:

**Automated Tests:**
```bash
# Run pytest smoke tests
pytest tests/test_smoke.py -v

# Quick test run
pytest -q
```

**Console QA Report:**
```bash
# Generate comprehensive QA report
python src/analysis/smoke_checks.py
```

This will display:
- File existence checks with pass/fail status
- Data quality metrics (row counts, date ranges)
- Top 10 drugs and reactions by report count
- Missing data warnings (flags if >5% data missing)
- Overall system health assessment

### Dashboard

Launch the interactive Streamlit dashboard:

```bash
streamlit run src/app/streamlit_mvp.py
```

**Dashboard Features:**
- **KPI Metrics**: Total AE reports, unique drugs/reactions, date coverage
- **Interactive Filters**: Filter by drug, reaction, and year
- **Trend Visualizations**: Overall trends and drug/reaction-specific trends
- **Top Rankings**: View top 10 drugs and reactions by report volume
- **Real-time Updates**: Automatically refreshes with filter changes

Access the dashboard at `http://localhost:8501`

### Output Files

**Data Files** (saved to `data/processed/`):
- `faers_events.parquet` - Consolidated FAERS events with columns: event_date, case_id, drug, reaction_pt, sex, age, country, serious
- `monthly_counts.csv` - Overall monthly event counts (ym, count)
- `monthly_by_reaction.csv` - Monthly counts by reaction (ym, reaction_pt, count)
- `monthly_by_drug.csv` - Monthly counts by drug (ym, drug, count)
- `reviews_extracted.csv` - Processed reviews with extracted AE terms (source, drug, raw_text, extracted_terms, mapped_pt, ym)

**Visualizations** (saved to `reports/figures/`):
- `overall_trend.png` - Overall AE trend over time (NEW: individual monthly plot)
- `top_reactions_bar.png` - Top 10 adverse reactions bar chart (NEW)
- `top_drugs_bar.png` - Top 10 drugs bar chart (NEW)
- `top_reactions_trend.png` - Top 10 adverse reactions trends (comprehensive)
- `top_drugs_trend.png` - Top 10 drugs with most AEs (comprehensive)
- `summary_statistics.png` - Statistical summary dashboard

## Data Requirements

### FAERS Data Structure
Place FAERS quarterly folders in `data/raw/` with the naming pattern:
```
data/raw/faers_ascii_2024q1/
├── ASCII/
│   ├── DEMO24Q1.txt
│   ├── REAC24Q1.txt
│   ├── DRUG24Q1.txt
│   └── ...
```

### Review Data Structure
Place review datasets in `data/raw/`:
```
data/raw/WebMD Drug Reviews Dataset/webmd.csv
data/raw/UCI ML Drug Review Dataset/drugsComTrain_raw.csv
data/raw/UCI ML Drug Review Dataset/drugsComTest_raw.csv
```

## Data Sources

This project integrates multiple data sources for comprehensive adverse event analysis:

### FDA FAERS Database
- **Source**: [FDA Adverse Event Reporting System (FAERS)](https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html)
- **Format**: ASCII quarterly dumps
- **Content**: Official adverse event reports submitted to FDA
- **Coverage**: 2013-2024 (extendable)
- **Access**: [FAERS Quarterly Data Files](https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html)

### WebMD Drug Reviews Dataset
- **Source**: [WebMD Drug Reviews Dataset](https://www.kaggle.com/datasets/rohanharode07/webmd-drug-reviews-dataset)
- **Format**: CSV with patient reviews
- **Content**: User-generated drug reviews and experiences
- **Access**: Available through Kaggle

### UCI ML Drug Review Dataset
- **Source**: [UCI Drug Review Dataset](https://www.kaggle.com/datasets/jessicali9530/kuc-hackathon-winter-2018)
- **Format**: Training and test CSV files
- **Content**: Drug reviews from Drugs.com with ratings and conditions
- **Access**: Available through Kaggle

## Key Features

### FAERS Processing
- **Auto-discovery**: Automatically finds quarterly folders
- **Schema normalization**: Handles column variations across years
- **Robust date parsing**: Supports multiple date formats (YYYYMMDD, YYYY-MM-DD, etc.)
- **Memory safety**: Handles large files with warnings and chunking capability
- **Data quality**: Removes duplicates and handles missing values

### Review Processing
- **Multi-source support**: WebMD and UCI datasets
- **AE term extraction**: Keyword-based extraction of adverse event mentions
- **MedDRA mapping**: Maps extracted terms to MedDRA Preferred Terms
- **Text normalization**: Cleans and standardizes review text

### Analysis & Visualization
- **Time series aggregation**: Monthly counts with proper date handling
- **Top N analysis**: Identifies most frequent reactions and drugs
- **Interactive plots**: Clear, publication-ready visualizations
- **Statistical summaries**: Comprehensive data overviews

## Column Mappings

The system automatically handles different column naming conventions:

| Standardized | FAERS Variations |
|-------------|------------------|
| case_id | PRIMARYID, CASEID |
| drug | DRUGNAME, MEDICINALPRODUCT |
| reaction_pt | PT, REACTIONMEDDRAPT |
| sex | SEX, PATIENTSEX |
| age | AGE, AGE_YRS |
| country | OCCUR_COUNTRY, COUNTRY |
| serious | SERIOUS, SERIOUSNESS |

## Customization

### New Plotting Functions (Added)

The system now includes enhanced plotting capabilities in `src/analysis/aggregate.py`:

#### Individual Plot Functions
```python
# Create a single monthly trend plot
plot_monthly(df, title="Custom Title", out_path="my_plot.png")

# Get top K items by count
top_reactions = top_k(monthly_reaction_df, column='reaction_pt', k=10)
top_drugs = top_k(monthly_drug_df, column='drug', k=5)

# Generate the three core trend plots
save_trend_plots(monthly_overall_df, monthly_reaction_df, monthly_drug_df, 
                 output_dir="plots/", top_n=10)
```

**Generated Plots:**
- `overall_trend.png` - Clean monthly trend line using matplotlib
- `top_reactions_bar.png` - Horizontal bar chart of top N reactions
- `top_drugs_bar.png` - Horizontal bar chart of top N drugs

### Adding New AE Keywords
Edit `AE_KEYWORDS` in `src/etl/reviews_loader.py`:
```python
AE_KEYWORDS = [
    'headache', 'nausea', 'dizziness',
    # Add your keywords here
    'new_symptom', 'another_ae'
]
```

### Extending MedDRA Mapping
Update `MEDDRA_MAPPING` in `src/etl/reviews_loader.py`:
```python
MEDDRA_MAPPING = {
    'headache': 'HEADACHE',
    # Add your mappings here
    'new_symptom': 'NEW_MEDDRA_PT'
}
```

## Error Handling

The pipeline includes comprehensive error handling:
- Missing files are logged but don't stop processing
- Invalid dates are converted to NaT and filtered out
- Encoding issues are handled with fallback strategies
- Large files trigger memory warnings
- Duplicate records are automatically removed

## Performance Notes

- **Memory usage**: Large FAERS files (>1GB) will trigger warnings
- **Processing time**: Expect 1-5 minutes per FAERS quarter depending on size
- **Storage**: Output files are compressed (Parquet) for efficiency

## 👨‍💻 Development

### Code Quality

This project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

**Configured Tools:**
- **black**: Code formatting
- **isort**: Import sorting  
- **flake8**: Style and error checking

### Contributing

To extend the functionality:
1. Add new modules to `src/etl/` or `src/analysis/`
2. Import and integrate in `build_all.py`
3. Follow the existing logging and error handling patterns
4. Add appropriate type hints and docstrings
5. Run pre-commit hooks before committing

## 👨‍💻 Author

**Mahin Das**
- 📧 Email: [mahinds04@gmail.com](mailto:mahinds04@gmail.com) | [dasmahin07@gmail.com](mailto:dasmahin07@gmail.com)
- 🐙 GitHub: [@mahinds04](https://github.com/mahinds04)
- 💼 LinkedIn: [Connect with me](https://linkedin.com/in/mahinds04)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FDA** for providing FAERS data
- **Kaggle contributors** for WebMD and UCI datasets
- **Streamlit team** for the amazing framework
- **Open source community** for the tools and libraries

## 📈 Project Stats

![GitHub stars](https://img.shields.io/github/stars/mahinds04/ae-trend-analyzer?style=social)
![GitHub forks](https://img.shields.io/github/forks/mahinds04/ae-trend-analyzer?style=social)
![GitHub issues](https://img.shields.io/github/issues/mahinds04/ae-trend-analyzer)

---
⭐ **Star this repository if you found it helpful!**
