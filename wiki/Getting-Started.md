# Getting Started

This guide will help you set up and run the AE Trend Analyzer on your system.

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher**
- **Git**
- **At least 8GB RAM** (recommended for full FAERS data processing)
- **10GB+ free disk space** (for FAERS data storage)

## 📥 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/mahinds04/ae-trend-analyzer.git
cd ae-trend-analyzer
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

Run the application in sample mode to verify everything is working:

```bash
streamlit run src/app/streamlit_mvp.py -- --sample
```

This should open your web browser to `http://localhost:8501` with the dashboard running on sample data.

## 🚀 Quick Demo (Sample Mode)

The fastest way to explore the AE Trend Analyzer is using the built-in sample data:

### Option 1: Command Line Flag
```bash
streamlit run src/app/streamlit_mvp.py -- --sample
```

### Option 2: Environment Variable
```bash
# Windows
set AE_SAMPLE=1
streamlit run src/app/streamlit_mvp.py

# Linux/Mac
export AE_SAMPLE=1
streamlit run src/app/streamlit_mvp.py
```

### What You'll See
- **50 sample adverse events** spanning multiple months
- **Interactive filtering** by drug and reaction
- **Trend visualization** with monthly aggregations
- **Anomaly detection** features
- **Professional dashboard UI**

## 📊 Full Data Setup

For complete functionality with real FAERS data, follow these steps:

### 1. Download FAERS Data

Visit the [FDA FAERS Quarterly Files](https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html) and download quarterly data files.

### 2. Organize Data Structure

Create the following directory structure in `data/raw/`:

```
data/raw/
├── faers_ascii_2024q1/
│   ├── ASCII/
│   │   ├── DEMO24Q1.txt
│   │   ├── DRUG24Q1.txt
│   │   ├── REAC24Q1.txt
│   │   ├── INDI24Q1.txt
│   │   ├── OUTC24Q1.txt
│   │   ├── RPSR24Q1.txt
│   │   └── THER24Q1.txt
├── faers_ascii_2024q2/
├── faers_ascii_2024q3/
└── faers_ascii_2024q4/
```

**Note**: The system supports various naming patterns. See the [Data Guide](Data-Guide) for complete details.

### 3. Add Review Datasets (Optional)

For enhanced analysis, add drug review datasets:

```
data/raw/
├── WebMD Drug Reviews Dataset/
│   └── webmd.csv
└── UCI ML Drug Review Dataset/
    ├── drugsComTrain_raw.csv
    └── drugsComTest_raw.csv
```

### 4. Run ETL Pipeline

Process the raw data:

```bash
python -m src.etl.build_all
```

This will create processed files in `data/processed/`:
- `faers_events.parquet`
- `monthly_counts.csv`
- `monthly_by_drug.csv`
- `monthly_by_reaction.csv`

### 5. Launch Dashboard

```bash
streamlit run src/app/streamlit_mvp.py
```

## 🧪 Quality Assurance

Run built-in tests to verify your setup:

### Unit Tests
```bash
pytest -q
```

### Data Validation
```bash
python src/analysis/smoke_checks.py
```

### Code Quality (Development)
```bash
# Install development tools
pip install black isort flake8 pre-commit

# Setup pre-commit hooks
pre-commit install

# Run quality checks
pre-commit run --all-files
```

## 🐳 Docker Alternative

For a containerized setup:

```bash
# Build Docker image
docker build -t ae-trend-analyzer .

# Run container
docker run -p 8501:8501 ae-trend-analyzer
```

## ⚡ Performance Tips

### For Large Datasets
- **Use SSD storage** for faster file I/O
- **Increase available RAM** (16GB+ recommended for multi-year FAERS data)
- **Process data in chunks** (handled automatically)

### For Development
- **Use sample mode** for rapid iteration
- **Enable caching** in Streamlit for faster reloads
- **Run ETL pipeline once** and reuse processed files

## 🔍 Next Steps

Once you have the application running:

1. **Explore the Dashboard**: See [User Guide](User-Guide) for feature details
2. **Understand the Data**: Review [Data Guide](Data-Guide) for data structure
3. **Customize Analysis**: Check [Developer Guide](Developer-Guide) for customization
4. **Report Issues**: Use [GitHub Issues](https://github.com/mahinds04/ae-trend-analyzer/issues) for problems

## 🆘 Need Help?

- **Installation Issues**: See [Troubleshooting](Troubleshooting)
- **Data Problems**: Check [Data Guide](Data-Guide)
- **General Questions**: Browse [FAQ](FAQ)
- **Bug Reports**: Open a [GitHub Issue](https://github.com/mahinds04/ae-trend-analyzer/issues)

---

**Next**: Continue to [User Guide](User-Guide) to learn about dashboard features.