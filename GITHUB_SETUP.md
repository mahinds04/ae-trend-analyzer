# GitHub Setup Guide for AE Trend Analyzer

This guide will help you upload your AE Trend Analyzer project to GitHub.

## Prerequisites

1. **Git installed** on your system
2. **GitHub account** created
3. **GitHub CLI** (optional but recommended) or Git Bash

## Step 1: Initialize Git Repository

```bash
cd "C:\Users\Mahin Das\OneDrive\ae-trend-analyzer"
git init
```

## Step 2: Add and Commit Files

```bash
# Add all files (respects .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: AE Trend Analyzer with Streamlit dashboard

Features:
- FAERS data processing pipeline
- Interactive Streamlit dashboard
- Automated QA testing
- Enhanced visualizations
- Professional UI/UX"
```

## Step 3: Create GitHub Repository

### Option A: Using GitHub Web Interface
1. Go to https://github.com/mahinds04
2. Click "New Repository"
3. Name: `ae-trend-analyzer`
4. Description: `Interactive dashboard for analyzing FDA FAERS adverse event trends`
5. Keep it **Public** (to showcase your work)
6. **Don't** initialize with README (we already have one)
7. Click "Create Repository"

### Option B: Using GitHub CLI
```bash
gh repo create ae-trend-analyzer --public --description "Interactive dashboard for analyzing FDA FAERS adverse event trends"
```

## Step 4: Connect and Push

```bash
# Add GitHub remote
git remote add origin https://github.com/mahinds04/ae-trend-analyzer.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 5: Verify Upload

1. Visit https://github.com/mahinds04/ae-trend-analyzer
2. Check that all source code files are present
3. Verify README.md displays correctly
4. Confirm data directories are present (but empty due to .gitignore)

## Repository Structure (What Gets Uploaded)

```
ae-trend-analyzer/
├── .gitignore                 # Git ignore rules
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── src/                       # Source code
│   ├── __init__.py
│   ├── config.py             # Centralized configuration
│   ├── app/
│   │   └── streamlit_mvp.py  # Dashboard application
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── build_all.py      # Main ETL pipeline
│   │   ├── faers_loader.py   # FAERS data processing
│   │   └── reviews_loader.py # Review data processing
│   └── analysis/
│       ├── __init__.py
│       ├── aggregate.py      # Data aggregation
│       └── smoke_checks.py   # QA validation
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_smoke.py         # Smoke tests
├── data/                     # Data directories (empty)
│   ├── README.md             # Data documentation
│   ├── raw/.gitkeep          # Raw data placeholder
│   └── processed/.gitkeep    # Processed data placeholder
└── reports/                  # Reports and figures
    ├── README.md             # Reports documentation
    └── figures/.gitkeep      # Figures placeholder
```

## What's Excluded (via .gitignore)

- Virtual environment files (`.venv/`)
- Python cache files (`__pycache__/`)
- Large data files (`data/raw/`, `data/processed/`)
- Temporary test files
- IDE configuration files
- Log files

## Post-Upload Steps

1. **Add Repository Description**: Add topics like `python`, `streamlit`, `data-analysis`, `healthcare`, `fda-faers`
2. **Enable GitHub Pages** (optional): For hosting documentation
3. **Add License**: Consider adding MIT or Apache 2.0 license
4. **Create Releases**: Tag versions of your project

## Cloning Instructions (for others)

```bash
# Clone the repository
git clone https://github.com/mahinds04/ae-trend-analyzer.git
cd ae-trend-analyzer

# Set up Python environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Add data files (follow data/README.md instructions)
# Run ETL pipeline
python -m src.etl.build_all

# Launch dashboard
streamlit run src/app/streamlit_mvp.py
```

## Tips for GitHub

- **Regular commits**: Commit changes frequently with descriptive messages
- **Branch strategy**: Use feature branches for major changes
- **Issues**: Use GitHub Issues to track bugs and enhancements
- **Documentation**: Keep README.md updated with any changes
- **Portfolio**: Pin this repository to showcase your work
