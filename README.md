# AE Trend Analyzer

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
3. **Place files** in `data/raw/` following the structure in `data/README.md`

### Run the Application

```bash
# Process the data
python -m src.etl.build_all

# Launch dashboard
streamlit run src/app/streamlit_mvp.py
```

Open http://localhost:8501 in your browser!

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

## Contributing

To extend the functionality:
1. Add new modules to `src/etl/` or `src/analysis/`
2. Import and integrate in `build_all.py`
3. Follow the existing logging and error handling patterns
4. Add appropriate type hints and docstrings

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
