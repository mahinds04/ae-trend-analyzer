# API Reference

This reference documents the code structure, modules, classes, and functions in the AE Trend Analyzer.

## 📋 Module Overview

```
src/
├── config.py                 # Configuration management
├── app/
│   └── streamlit_mvp.py      # Dashboard application
├── etl/
│   ├── build_all.py          # ETL orchestrator
│   ├── faers_loader.py       # FAERS data processing
│   └── reviews_loader.py     # Review data processing
└── analysis/
    ├── aggregate.py          # Data aggregation
    └── smoke_checks.py       # Quality assurance
```

## ⚙️ Configuration (`src/config.py`)

### **Class: Config**

Central configuration management for the application.

```python
class Config:
    """Application configuration and constants"""
```

#### **Attributes**

| Attribute | Type | Description | Default |
|-----------|------|-------------|---------|
| `DATA_RAW_PATH` | Path | Raw data directory | `data/raw` |
| `DATA_PROCESSED_PATH` | Path | Processed data directory | `data/processed` |
| `SAMPLES_PATH` | Path | Sample data directory | `data/processed/_samples` |
| `CHUNK_SIZE` | int | Processing chunk size | `10000` |
| `ENCODING_FALLBACKS` | List[str] | Encoding attempts | `['utf-8', 'latin-1', 'cp1252']` |
| `SAMPLE_MODE` | bool | Enable sample mode | From `AE_SAMPLE` env var |
| `MAX_DISPLAY_ITEMS` | int | Dashboard display limit | `15` |

#### **Methods**

```python
@classmethod
def get_data_path(cls, filename: str) -> Path:
    """Get path to processed data file"""
    
@classmethod 
def is_sample_mode(cls) -> bool:
    """Check if application should run in sample mode"""
    
@classmethod
def get_sample_path(cls, filename: str) -> Path:
    """Get path to sample data file"""
```

#### **Usage Example**

```python
from src.config import Config

# Get data paths
data_file = Config.get_data_path("faers_events.parquet")
sample_file = Config.get_sample_path("faers_events.sample.parquet")

# Check mode
if Config.is_sample_mode():
    data = pd.read_parquet(sample_file)
else:
    data = pd.read_parquet(data_file)
```

## 🎛️ Dashboard Application (`src/app/streamlit_mvp.py`)

### **Main Functions**

#### **`main()`**
```python
def main() -> None:
    """Main dashboard application entry point"""
```
Orchestrates the entire dashboard application flow.

#### **`setup_page_config()`**
```python
def setup_page_config() -> None:
    """Configure Streamlit page settings"""
```
Sets up page title, layout, and styling.

#### **`load_dashboard_data()`**
```python
def load_dashboard_data() -> pd.DataFrame:
    """Load data for dashboard with sample mode support"""
```
Smart data loading with automatic fallback to sample data.

### **UI Rendering Functions**

#### **`render_header()`**
```python
def render_header() -> None:
    """Render dashboard header with gradient styling"""
```

#### **`render_sidebar_filters(data: pd.DataFrame)`**
```python
def render_sidebar_filters(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Render interactive filters in sidebar
    
    Args:
        data: Input DataFrame for filter options
        
    Returns:
        Dictionary containing filter selections
    """
```

#### **`render_kpi_cards(data: pd.DataFrame, filters: Dict[str, Any])`**
```python
def render_kpi_cards(data: pd.DataFrame, filters: Dict[str, Any]) -> None:
    """
    Display key performance indicator cards
    
    Args:
        data: Filtered DataFrame
        filters: Applied filters
    """
```

### **Visualization Functions**

#### **`create_monthly_trend_chart(data: pd.DataFrame)`**
```python
def create_monthly_trend_chart(data: pd.DataFrame) -> plotly.graph_objects.Figure:
    """
    Create monthly trend line chart
    
    Args:
        data: DataFrame with event_date column
        
    Returns:
        Plotly figure object
    """
```

#### **`create_top_drugs_chart(data: pd.DataFrame, n_top: int = 15)`**
```python
def create_top_drugs_chart(data: pd.DataFrame, n_top: int = 15) -> plotly.graph_objects.Figure:
    """
    Create horizontal bar chart of top drugs
    
    Args:
        data: DataFrame with drug column
        n_top: Number of top items to display
        
    Returns:
        Plotly figure object
    """
```

#### **`create_top_reactions_chart(data: pd.DataFrame, n_top: int = 15)`**
```python
def create_top_reactions_chart(data: pd.DataFrame, n_top: int = 15) -> plotly.graph_objects.Figure:
    """
    Create horizontal bar chart of top reactions
    
    Args:
        data: DataFrame with reaction_pt column
        n_top: Number of top items to display
        
    Returns:
        Plotly figure object
    """
```

### **Anomaly Detection Functions**

#### **`detect_anomalies_stl(data: pd.DataFrame)`**
```python
def detect_anomalies_stl(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform STL decomposition for anomaly detection
    
    Args:
        data: Time series data with monthly aggregation
        
    Returns:
        Dictionary containing decomposition components and anomalies
    """
```

#### **`detect_anomalies_zscore(data: pd.DataFrame, threshold: float = 2.0)`**
```python
def detect_anomalies_zscore(
    data: pd.DataFrame, 
    threshold: float = 2.0
) -> Dict[str, Any]:
    """
    Detect anomalies using rolling Z-score
    
    Args:
        data: Time series data
        threshold: Z-score threshold for anomaly detection
        
    Returns:
        Dictionary containing anomaly indicators and statistics
    """
```

#### **`detect_anomalies_prophet(data: pd.DataFrame)`**
```python
def detect_anomalies_prophet(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform Prophet-based anomaly detection and forecasting
    
    Args:
        data: Time series data in Prophet format
        
    Returns:
        Dictionary containing forecast and anomaly information
    """
```

### **Insight Generation**

#### **`generate_insights(data: pd.DataFrame, anomalies: Dict[str, Any])`**
```python
def generate_insights(
    data: pd.DataFrame, 
    anomalies: Dict[str, Any]
) -> List[str]:
    """
    Generate automated insights from data and anomalies
    
    Args:
        data: Input DataFrame
        anomalies: Anomaly detection results
        
    Returns:
        List of insight strings
    """
```

## 🔄 ETL Pipeline (`src/etl/`)

### **ETL Orchestrator (`build_all.py`)**

#### **`main()`**
```python
def main() -> None:
    """Run complete ETL pipeline"""
```

#### **`run_etl_pipeline(force_rebuild: bool = False)`**
```python
def run_etl_pipeline(force_rebuild: bool = False) -> None:
    """
    Execute full ETL pipeline
    
    Args:
        force_rebuild: Force reprocessing even if files exist
    """
```

### **FAERS Data Loader (`faers_loader.py`)**

#### **Core Functions**

#### **`load_faers_data(data_path: Optional[str] = None)`**
```python
def load_faers_data(data_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load and process all FAERS quarterly data
    
    Args:
        data_path: Optional custom data directory path
        
    Returns:
        Consolidated FAERS events DataFrame
        
    Raises:
        FileNotFoundError: If no FAERS quarters found
        ValueError: If data processing fails
    """
```

#### **`discover_faers_quarters(data_path: Path)`**
```python
def discover_faers_quarters(data_path: Path) -> List[Path]:
    """
    Automatically discover FAERS quarter directories
    
    Args:
        data_path: Path to search for quarters
        
    Returns:
        List of discovered quarter directory paths
    """
```

#### **`process_faers_quarter(quarter_path: Path)`**
```python
def process_faers_quarter(quarter_path: Path) -> pd.DataFrame:
    """
    Process a single FAERS quarter directory
    
    Args:
        quarter_path: Path to quarter directory
        
    Returns:
        Processed DataFrame for the quarter
        
    Raises:
        FileNotFoundError: If required files missing
        ValueError: If data format invalid
    """
```

#### **File Loading Functions**

#### **`load_faers_file(file_path: Path, file_type: str)`**
```python
def load_faers_file(file_path: Path, file_type: str) -> pd.DataFrame:
    """
    Load FAERS file with robust error handling
    
    Args:
        file_path: Path to FAERS file
        file_type: Type of file (DEMO, DRUG, REAC, etc.)
        
    Returns:
        Loaded DataFrame with standardized columns
    """
```

#### **`standardize_columns(df: pd.DataFrame, file_type: str)`**
```python
def standardize_columns(df: pd.DataFrame, file_type: str) -> pd.DataFrame:
    """
    Standardize column names across FAERS versions
    
    Args:
        df: Input DataFrame
        file_type: FAERS file type
        
    Returns:
        DataFrame with standardized column names
    """
```

#### **Data Processing Functions**

#### **`join_quarter_files(files: Dict[str, pd.DataFrame])`**
```python
def join_quarter_files(files: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Join multiple FAERS files into consolidated events
    
    Args:
        files: Dictionary of loaded file DataFrames
        
    Returns:
        Joined DataFrame with all available information
    """
```

#### **`clean_faers_data(df: pd.DataFrame)`**
```python
def clean_faers_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate FAERS data
    
    Args:
        df: Raw FAERS DataFrame
        
    Returns:
        Cleaned DataFrame
    """
```

### **Review Data Loader (`reviews_loader.py`)**

#### **`load_review_data(data_path: Optional[str] = None)`**
```python
def load_review_data(data_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load and process drug review datasets
    
    Args:
        data_path: Optional custom data directory path
        
    Returns:
        Combined review DataFrame with extracted adverse events
    """
```

#### **`load_webmd_reviews(file_path: Path)`**
```python
def load_webmd_reviews(file_path: Path) -> pd.DataFrame:
    """
    Load WebMD drug review dataset
    
    Args:
        file_path: Path to webmd.csv file
        
    Returns:
        Processed WebMD reviews DataFrame
    """
```

#### **`load_uci_reviews(train_path: Path, test_path: Path)`**
```python
def load_uci_reviews(train_path: Path, test_path: Path) -> pd.DataFrame:
    """
    Load UCI ML drug review datasets
    
    Args:
        train_path: Path to training data file
        test_path: Path to test data file
        
    Returns:
        Combined UCI reviews DataFrame
    """
```

#### **Adverse Event Extraction**

#### **`extract_adverse_events(review_text: str)`**
```python
def extract_adverse_events(review_text: str) -> List[str]:
    """
    Extract adverse event keywords from review text
    
    Args:
        review_text: Raw review content
        
    Returns:
        List of detected adverse event terms
    """
```

#### **`map_to_meddra(ae_keywords: List[str])`**
```python
def map_to_meddra(ae_keywords: List[str]) -> List[str]:
    """
    Map adverse event keywords to MedDRA preferred terms
    
    Args:
        ae_keywords: List of detected keywords
        
    Returns:
        List of MedDRA preferred terms
    """
```

#### **Constants**

```python
AE_KEYWORDS = [
    'headache', 'nausea', 'dizziness', 'fatigue', 'insomnia',
    'weight gain', 'weight loss', 'anxiety', 'depression',
    'constipation', 'diarrhea', 'vomiting', 'drowsiness',
    # ... additional keywords
]

MEDDRA_MAPPING = {
    'headache': 'HEADACHE',
    'nausea': 'NAUSEA', 
    'dizziness': 'DIZZINESS',
    # ... additional mappings
}
```

## 📊 Analysis Modules (`src/analysis/`)

### **Data Aggregation (`aggregate.py`)**

#### **`create_monthly_aggregations(events_df: pd.DataFrame)`**
```python
def create_monthly_aggregations(events_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Create monthly aggregated datasets
    
    Args:
        events_df: Raw events DataFrame with event_date column
        
    Returns:
        Dictionary containing:
        - 'monthly_counts': Overall monthly aggregation
        - 'monthly_by_drug': Drug-specific monthly data
        - 'monthly_by_reaction': Reaction-specific monthly data
    """
```

#### **`aggregate_monthly_counts(events_df: pd.DataFrame)`**
```python
def aggregate_monthly_counts(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create overall monthly event counts
    
    Args:
        events_df: Events DataFrame
        
    Returns:
        Monthly aggregation with columns:
        - month: First day of month
        - event_count: Number of events
        - unique_drugs: Number of distinct drugs
        - unique_reactions: Number of distinct reactions
    """
```

#### **`aggregate_monthly_by_drug(events_df: pd.DataFrame)`**
```python
def aggregate_monthly_by_drug(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create drug-specific monthly aggregations
    
    Args:
        events_df: Events DataFrame
        
    Returns:
        DataFrame with columns:
        - month: First day of month
        - drug: Medication name
        - event_count: Events for this drug
        - reaction_count: Distinct reactions
    """
```

#### **`aggregate_monthly_by_reaction(events_df: pd.DataFrame)`**
```python
def aggregate_monthly_by_reaction(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create reaction-specific monthly aggregations
    
    Args:
        events_df: Events DataFrame
        
    Returns:
        DataFrame with columns:
        - month: First day of month
        - reaction_pt: MedDRA preferred term
        - event_count: Events for this reaction
        - drug_count: Distinct drugs associated
    """
```

#### **`save_aggregations(aggregations: Dict[str, pd.DataFrame], output_path: Path)`**
```python
def save_aggregations(
    aggregations: Dict[str, pd.DataFrame], 
    output_path: Path
) -> None:
    """
    Save aggregated datasets to files
    
    Args:
        aggregations: Dictionary of aggregated DataFrames
        output_path: Directory to save files
    """
```

### **Quality Assurance (`smoke_checks.py`)**

#### **`run_all_smoke_tests()`**
```python
def run_all_smoke_tests() -> bool:
    """
    Run comprehensive data quality checks
    
    Returns:
        True if all tests pass, False otherwise
    """
```

#### **Data Validation Functions**

#### **`check_data_files_exist()`**
```python
def check_data_files_exist() -> bool:
    """Check if required data files exist"""
```

#### **`check_data_schema(df: pd.DataFrame)`**
```python
def check_data_schema(df: pd.DataFrame) -> bool:
    """
    Validate DataFrame schema
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if schema is valid
    """
```

#### **`check_data_completeness(df: pd.DataFrame)`**
```python
def check_data_completeness(df: pd.DataFrame) -> bool:
    """
    Check data completeness and quality
    
    Args:
        df: DataFrame to check
        
    Returns:
        True if data quality is acceptable
    """
```

#### **`check_date_ranges(df: pd.DataFrame)`**
```python
def check_date_ranges(df: pd.DataFrame) -> bool:
    """
    Validate date ranges in data
    
    Args:
        df: DataFrame with event_date column
        
    Returns:
        True if date ranges are reasonable
    """
```

#### **Application Tests**

#### **`test_dashboard_loading()`**
```python
def test_dashboard_loading() -> bool:
    """Test if dashboard can load successfully"""
```

#### **`test_sample_data_consistency()`**
```python
def test_sample_data_consistency() -> bool:
    """Verify sample data matches expected format"""
```

## 📚 Common Usage Patterns

### **Loading Data**

```python
from src.config import Config
from src.etl.faers_loader import load_faers_data
import pandas as pd

# Smart data loading
if Config.is_sample_mode():
    data = pd.read_parquet(Config.get_sample_path("faers_events.sample.parquet"))
else:
    data = load_faers_data()
```

### **Creating Visualizations**

```python
from src.app.streamlit_mvp import create_monthly_trend_chart
import streamlit as st

# Create and display chart
fig = create_monthly_trend_chart(filtered_data)
st.plotly_chart(fig, use_container_width=True)
```

### **Running ETL Pipeline**

```python
from src.etl.build_all import run_etl_pipeline

# Process all data
run_etl_pipeline()

# Force rebuild
run_etl_pipeline(force_rebuild=True)
```

### **Anomaly Detection**

```python
from src.app.streamlit_mvp import detect_anomalies_stl, detect_anomalies_zscore

# Detect anomalies using multiple methods
stl_results = detect_anomalies_stl(monthly_data)
zscore_results = detect_anomalies_zscore(monthly_data, threshold=2.5)
```

## 🔧 Extension Points

### **Adding New Data Sources**

1. **Create new loader module** in `src/etl/`
2. **Implement standard interface**:
   ```python
   def load_new_source_data() -> pd.DataFrame:
       """Load data with standardized schema"""
       pass
   ```
3. **Add to ETL pipeline** in `build_all.py`

### **Custom Anomaly Detection**

```python
def detect_anomalies_custom(data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """
    Custom anomaly detection algorithm
    
    Args:
        data: Time series data
        **kwargs: Algorithm-specific parameters
        
    Returns:
        Dictionary with anomaly results
    """
    # Implementation
    return {
        'anomalies': anomaly_indices,
        'scores': anomaly_scores,
        'metadata': algorithm_info
    }
```

### **New Visualization Types**

```python
def create_custom_chart(data: pd.DataFrame) -> plotly.graph_objects.Figure:
    """
    Create custom visualization
    
    Args:
        data: Input DataFrame
        
    Returns:
        Plotly figure object
    """
    # Implementation
    return fig
```

---

**Next**: Find answers to common questions in the [FAQ](FAQ).