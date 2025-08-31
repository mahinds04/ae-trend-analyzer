# Developer Guide

This guide covers development setup, code structure, testing procedures, and contribution workflows for the AE Trend Analyzer project.

## 🛠️ Development Environment Setup

### **Prerequisites**
- **Python 3.10+**
- **Git**
- **Code Editor** (VS Code recommended)
- **GitHub Account** (for contributions)

### **Initial Setup**

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/ae-trend-analyzer.git
cd ae-trend-analyzer

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install black isort flake8 pre-commit pytest

# Setup pre-commit hooks
pre-commit install
```

### **Development Workflow**

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Changes**
   ```bash
   # Run unit tests
   pytest -q
   
   # Test with sample data
   streamlit run src/app/streamlit_mvp.py -- --sample
   
   # Run smoke tests
   python src/analysis/smoke_checks.py
   ```

4. **Code Quality Checks**
   ```bash
   # Format code
   black .
   isort .
   
   # Lint code
   flake8
   
   # Run all pre-commit hooks
   pre-commit run --all-files
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

## 📁 Project Structure

```
ae-trend-analyzer/
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI/CD
├── .streamlit/
│   └── config.toml               # Streamlit configuration
├── data/
│   ├── processed/
│   │   └── _samples/             # Sample datasets
│   ├── raw/                      # Input data (excluded from git)
│   └── README.md                 # Data structure guide
├── src/
│   ├── analysis/
│   │   ├── aggregate.py          # Data aggregation functions
│   │   └── smoke_checks.py       # QA validation tests
│   ├── app/
│   │   └── streamlit_mvp.py      # Main dashboard application
│   ├── etl/
│   │   ├── build_all.py          # ETL pipeline orchestrator
│   │   ├── faers_loader.py       # FAERS data processing
│   │   └── reviews_loader.py     # Review data processing
│   ├── config.py                 # Configuration management
│   └── __init__.py
├── tests/
│   ├── test_etl.py               # ETL pipeline tests
│   ├── test_analysis.py          # Analysis function tests
│   └── conftest.py               # Test configuration
├── wiki/                         # Wiki documentation
├── requirements.txt              # Python dependencies
├── requirements-cloud.txt        # Cloud deployment dependencies
├── .pre-commit-config.yaml       # Code quality hooks
├── .gitignore                    # Git ignore rules
└── README.md                     # Main documentation
```

## 🧩 Core Components

### **1. ETL Pipeline (`src/etl/`)**

#### **`build_all.py`**
Main ETL orchestrator that coordinates data processing:

```python
from src.etl.faers_loader import load_faers_data
from src.etl.reviews_loader import load_review_data
from src.analysis.aggregate import create_monthly_aggregations

def run_full_pipeline():
    """Run complete ETL pipeline"""
    # Load FAERS data
    faers_events = load_faers_data()
    
    # Load review data
    review_data = load_review_data()
    
    # Create aggregations
    create_monthly_aggregations(faers_events)
```

#### **`faers_loader.py`**
FAERS data processing with robust error handling:

```python
def load_faers_data(data_path: str = None) -> pd.DataFrame:
    """
    Load and process FAERS quarterly data
    
    Args:
        data_path: Optional custom data path
        
    Returns:
        Consolidated FAERS events DataFrame
    """
    # Implementation handles multiple file formats,
    # encoding issues, and column mapping
```

#### **`reviews_loader.py`**
Drug review data processing with AE keyword extraction:

```python
def extract_adverse_events(review_text: str) -> List[str]:
    """
    Extract adverse event keywords from review text
    
    Args:
        review_text: Raw review content
        
    Returns:
        List of detected adverse event terms
    """
    # Implementation uses keyword matching and
    # MedDRA term mapping
```

### **2. Dashboard Application (`src/app/`)**

#### **`streamlit_mvp.py`**
Main Streamlit application with modular design:

```python
def main():
    """Main dashboard application"""
    # Configuration
    setup_page_config()
    
    # Data loading
    data = load_dashboard_data()
    
    # UI rendering
    render_header()
    render_sidebar_filters()
    render_main_content(data)
    
    # Advanced features
    render_anomaly_detection()
    render_insights_panel()
```

Key functions:
- **`load_dashboard_data()`**: Smart data loading with sample mode support
- **`render_sidebar_filters()`**: Interactive filter controls
- **`create_monthly_trend_chart()`**: Primary trend visualization
- **`detect_anomalies()`**: Anomaly detection algorithms
- **`generate_insights()`**: Automated insight generation

### **3. Analysis Modules (`src/analysis/`)**

#### **`aggregate.py`**
Data aggregation and transformation functions:

```python
def create_monthly_aggregations(events_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Create monthly aggregated datasets
    
    Args:
        events_df: Raw events DataFrame
        
    Returns:
        Dictionary of aggregated DataFrames
    """
    # Creates monthly_counts.csv, monthly_by_drug.csv, etc.
```

#### **`smoke_checks.py`**
Data quality validation and testing:

```python
def run_all_smoke_tests() -> bool:
    """
    Run comprehensive data quality checks
    
    Returns:
        True if all tests pass, False otherwise
    """
    # Validates data completeness, consistency, and format
```

### **4. Configuration (`src/config.py`)**

Centralized configuration management:

```python
class Config:
    """Application configuration"""
    
    # Data paths
    DATA_RAW_PATH = Path("data/raw")
    DATA_PROCESSED_PATH = Path("data/processed")
    SAMPLES_PATH = DATA_PROCESSED_PATH / "_samples"
    
    # Processing settings
    CHUNK_SIZE = 10000
    ENCODING_FALLBACKS = ['utf-8', 'latin-1', 'cp1252']
    
    # Dashboard settings
    SAMPLE_MODE = os.getenv('AE_SAMPLE', '0') == '1'
    MAX_DISPLAY_ITEMS = 15
```

## 🧪 Testing Framework

### **Unit Tests (`tests/`)**

The project uses pytest for comprehensive testing:

#### **Test Structure**
```python
# tests/test_etl.py
def test_faers_data_loading():
    """Test FAERS data loading functionality"""
    # Test implementation

def test_column_mapping():
    """Test column name standardization"""
    # Test implementation

# tests/test_analysis.py
def test_monthly_aggregation():
    """Test monthly data aggregation"""
    # Test implementation

def test_anomaly_detection():
    """Test anomaly detection algorithms"""
    # Test implementation
```

#### **Running Tests**
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_etl.py

# Run tests with coverage
pytest --cov=src

# Run tests in quiet mode (CI)
pytest -q
```

### **Integration Tests**

#### **Smoke Tests**
```bash
python src/analysis/smoke_checks.py
```

Tests include:
- Data file existence and accessibility
- Data schema validation
- Processing pipeline integrity
- Dashboard functionality
- Sample data consistency

#### **End-to-End Tests**
```bash
# Test full pipeline
python -m src.etl.build_all

# Test dashboard with sample data
streamlit run src/app/streamlit_mvp.py -- --sample
```

## 🎨 Code Quality Standards

### **Formatting and Style**

#### **Black Code Formatter**
```bash
# Format all Python files
black .

# Check formatting without changes
black --check .

# Format specific file
black src/app/streamlit_mvp.py
```

#### **isort Import Sorting**
```bash
# Sort imports
isort .

# Check import sorting
isort --check-only .
```

#### **flake8 Linting**
```bash
# Lint all files
flake8

# Lint specific file
flake8 src/app/streamlit_mvp.py
```

### **Pre-commit Hooks**

Configuration in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --ignore=E203]
```

### **Coding Conventions**

#### **Function Documentation**
```python
def process_faers_quarter(quarter_path: Path) -> pd.DataFrame:
    """
    Process a single FAERS quarter directory.
    
    Args:
        quarter_path: Path to quarter directory (e.g., faers_ascii_2024q1)
        
    Returns:
        DataFrame with standardized columns and processed events
        
    Raises:
        FileNotFoundError: If required files are missing
        ValueError: If data format is invalid
        
    Example:
        >>> quarter_df = process_faers_quarter(Path("data/raw/faers_ascii_2024q1"))
        >>> print(quarter_df.shape)
        (15000, 8)
    """
    # Implementation
```

#### **Error Handling**
```python
def load_data_file(file_path: Path) -> pd.DataFrame:
    """Load data file with robust error handling."""
    try:
        return pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        logger.warning(f"UTF-8 failed for {file_path}, trying latin-1")
        try:
            return pd.read_csv(file_path, encoding='latin-1')
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise
```

#### **Logging**
```python
import logging

logger = logging.getLogger(__name__)

def process_data():
    """Process data with appropriate logging."""
    logger.info("Starting data processing")
    try:
        # Processing logic
        logger.info("Data processing completed successfully")
    except Exception as e:
        logger.error(f"Data processing failed: {e}")
        raise
```

## 🚀 Continuous Integration

### **GitHub Actions Workflow**

Configuration in `.github/workflows/ci.yml`:

```yaml
name: CI - QA & Smoke Tests

on:
  push:
    branches: [ master, main ]
  pull_request:
    branches: [ master, main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        cache: 'pip'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run tests
      run: pytest -q
    
    - name: Run smoke checks
      run: python src/analysis/smoke_checks.py

  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install linting tools
      run: pip install black isort flake8
    
    - name: Check code formatting
      run: |
        black --check .
        isort --check-only .
        flake8
```

### **Build Status**

The CI pipeline ensures:
- **Code Quality**: Formatting and linting standards
- **Test Coverage**: Unit and integration tests
- **Data Validation**: Smoke tests for data integrity
- **Build Success**: Application startup verification

## 🔧 Adding New Features

### **ETL Pipeline Extensions**

#### **Adding New Data Sources**
1. Create new loader in `src/etl/`
2. Implement standardized loading interface
3. Add to `build_all.py` orchestrator
4. Create corresponding tests
5. Update documentation

#### **Example: New Data Source**
```python
# src/etl/new_source_loader.py
def load_new_source_data() -> pd.DataFrame:
    """Load data from new source with standard schema."""
    # Implementation
    return standardized_df
```

### **Dashboard Enhancements**

#### **Adding New Visualizations**
1. Create visualization function in `streamlit_mvp.py`
2. Add to main dashboard layout
3. Include interactive controls
4. Test with sample data
5. Document in User Guide

#### **Example: New Chart Type**
```python
def create_scatter_plot(data: pd.DataFrame) -> None:
    """Create interactive scatter plot visualization."""
    fig = px.scatter(
        data, 
        x='column1', 
        y='column2',
        title="New Scatter Plot"
    )
    st.plotly_chart(fig, use_container_width=True)
```

### **Analysis Module Extensions**

#### **Adding New Algorithms**
1. Implement in `src/analysis/`
2. Follow existing function signatures
3. Add comprehensive tests
4. Document algorithm details
5. Integrate into dashboard

## 📚 Documentation Standards

### **Code Documentation**
- **Docstrings**: All functions and classes
- **Type Hints**: Function parameters and returns
- **Examples**: Usage examples in docstrings
- **Error Handling**: Document exceptions and edge cases

### **User Documentation**
- **Wiki Pages**: Comprehensive user guides
- **README Updates**: Keep main README current
- **API Documentation**: Document public interfaces
- **Changelog**: Track changes between versions

## 🤝 Contributing Guidelines

### **Pull Request Process**

1. **Fork Repository**: Create personal fork
2. **Create Branch**: Use descriptive branch names
3. **Make Changes**: Follow coding standards
4. **Add Tests**: Ensure test coverage
5. **Update Docs**: Keep documentation current
6. **Submit PR**: Use PR template
7. **Code Review**: Address reviewer feedback
8. **Merge**: Maintainer will merge when ready

### **PR Requirements Checklist**

- [ ] Code follows project coding standards
- [ ] Tests pass (`pytest tests/`)
- [ ] Documentation updated (if applicable)
- [ ] No breaking changes (or clearly documented)
- [ ] Sample mode works (`python run_dashboard.py --sample`)
- [ ] Pre-commit hooks pass
- [ ] Descriptive commit messages

### **Issue Reporting**

Use GitHub Issues for:
- **Bug Reports**: Include reproduction steps
- **Feature Requests**: Describe use case and benefits
- **Documentation Issues**: Specify unclear sections
- **Performance Problems**: Include profiling data

## 🔍 Debugging Guide

### **Common Development Issues**

#### **Data Loading Problems**
```python
# Debug data loading
import logging
logging.basicConfig(level=logging.DEBUG)

# Check file existence
from pathlib import Path
data_path = Path("data/raw/faers_ascii_2024q1")
print(f"Exists: {data_path.exists()}")
print(f"Contents: {list(data_path.glob('*'))}")
```

#### **Dashboard Issues**
```bash
# Run with debug output
streamlit run src/app/streamlit_mvp.py --logger.level=debug

# Check browser console for JavaScript errors
# Verify data files exist and are readable
```

#### **Test Failures**
```bash
# Run tests with verbose output
pytest -v -s

# Run specific failing test
pytest tests/test_etl.py::test_specific_function -v

# Debug with pdb
pytest --pdb tests/test_etl.py
```

### **Performance Optimization**

#### **Profiling Code**
```python
import cProfile
import pstats

# Profile function
pr = cProfile.Profile()
pr.enable()
your_function()
pr.disable()

# Analyze results
stats = pstats.Stats(pr)
stats.sort_stats('cumulative').print_stats(10)
```

#### **Memory Optimization**
```python
# Monitor memory usage
import tracemalloc

tracemalloc.start()
your_function()
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f} MB")
print(f"Peak: {peak / 1024 / 1024:.1f} MB")
```

---

**Next**: Learn about data requirements in the [Data Guide](Data-Guide).