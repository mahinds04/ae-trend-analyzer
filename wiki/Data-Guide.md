# Data Guide

This comprehensive guide covers FAERS data structure, requirements, processing, and management for the AE Trend Analyzer.

## 📊 Overview

The AE Trend Analyzer processes multiple data sources to provide comprehensive adverse event analysis:

- **FDA FAERS**: Primary adverse event reporting system data
- **Drug Reviews**: WebMD and UCI review datasets
- **Sample Data**: Built-in demonstration datasets

## 🏥 FAERS Data Structure

### **What is FAERS?**

The FDA Adverse Event Reporting System (FAERS) is a database containing adverse event reports, medication error reports, and product quality complaints submitted to FDA.

### **Quarterly Data Format**

FAERS data is released quarterly with the following structure:

```
data/raw/
├── faers_ascii_2024q1/
│   ├── ASCII/                    # Main data directory
│   │   ├── DEMO24Q1.txt         # Demographics (required)
│   │   ├── DRUG24Q1.txt         # Drug information (required)
│   │   ├── REAC24Q1.txt         # Reactions (required)
│   │   ├── INDI24Q1.txt         # Indications (optional)
│   │   ├── OUTC24Q1.txt         # Outcomes (optional)
│   │   ├── RPSR24Q1.txt         # Report sources (optional)
│   │   └── THER24Q1.txt         # Therapy dates (optional)
│   ├── FAQs.pdf                 # Documentation
│   └── Readme.pdf               # Release notes
```

### **Supported Naming Patterns**

The system automatically handles various FAERS naming conventions:

#### **Quarter Folder Names**
- `faers_ascii_2024q1` ✅
- `faers_ascii_2024Q1` ✅ (case insensitive)
- `faers_ascii_2013q4` ✅ (legacy format)
- `FAERS_ASCII_2024Q2` ✅

#### **ASCII Directory Names**
- `ASCII/` ✅ (standard)
- `ascii/` ✅ (lowercase)

#### **File Naming Patterns**

| File Type | 2024+ Format | Legacy Format | Purpose |
|-----------|--------------|---------------|---------|
| Demographics | `DEMO24Q1.txt` | `DEMO13Q4.txt` | Patient demographics |
| Drugs | `DRUG24Q1.txt` | `DRUG13Q4.txt` | Medication information |
| Reactions | `REAC24Q1.txt` | `REAC13Q4.txt` | Adverse events |
| Indications | `INDI24Q1.txt` | `INDI13Q4.txt` | Medical indications |
| Outcomes | `OUTC24Q1.txt` | `OUTC13Q4.txt` | Patient outcomes |
| Report Sources | `RPSR24Q1.txt` | `RPSR13Q4.txt` | Report origins |
| Therapy | `THER24Q1.txt` | `THER13Q4.txt` | Treatment dates |

## 📋 Required vs Optional Files

### **Required Files (Core Functionality)**
- **`DEMO*.txt`**: Patient demographics and case information
- **`DRUG*.txt`**: Medication details and dosing
- **`REAC*.txt`**: Adverse event descriptions

### **Optional Files (Enhanced Analysis)**
- **`INDI*.txt`**: Medical indications for drug use
- **`OUTC*.txt`**: Patient outcomes and severity
- **`RPSR*.txt`**: Report source tracking
- **`THER*.txt`**: Therapy start/end dates

### **Graceful Degradation**
Missing optional files will not prevent processing, but may limit analysis features:

```python
# The system automatically detects available files
if outc_file.exists():
    # Enhanced outcome analysis available
else:
    # Basic analysis only
```

## 🔄 Data Processing Pipeline

### **ETL Workflow**

#### **1. Discovery Phase**
```python
def discover_faers_quarters(data_path: Path) -> List[Path]:
    """Automatically discover FAERS quarter directories"""
    quarters = []
    for item in data_path.iterdir():
        if item.is_dir() and 'faers_ascii' in item.name.lower():
            quarters.append(item)
    return sorted(quarters)
```

#### **2. File Loading**
```python
def load_quarter_files(quarter_path: Path) -> Dict[str, pd.DataFrame]:
    """Load all available files for a quarter"""
    files = {}
    
    # Required files
    for file_type in ['DEMO', 'DRUG', 'REAC']:
        file_path = find_file(quarter_path, file_type)
        if file_path:
            files[file_type] = load_with_encoding_fallback(file_path)
    
    # Optional files
    for file_type in ['INDI', 'OUTC', 'RPSR', 'THER']:
        file_path = find_file(quarter_path, file_type)
        if file_path:
            files[file_type] = load_with_encoding_fallback(file_path)
    
    return files
```

#### **3. Column Standardization**
The system handles varying column names across FAERS versions:

| Standardized Column | FAERS Variations |
|-------------------|------------------|
| `case_id` | `PRIMARYID`, `CASEID` |
| `drug` | `DRUGNAME`, `MEDICINALPRODUCT` |
| `reaction_pt` | `PT`, `REACTIONMEDDRAPT` |
| `sex` | `SEX`, `PATIENTSEX` |
| `age` | `AGE`, `AGE_YRS` |
| `country` | `OCCUR_COUNTRY`, `COUNTRY` |
| `serious` | `SERIOUS`, `SERIOUSNESS` |
| `event_date` | `FDA_DT`, `INIT_FDA_DT` |

#### **4. Data Joining**
```python
def join_quarter_data(files: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Join multiple files into consolidated events"""
    
    # Start with demographics
    events = files['DEMO'].copy()
    
    # Join drugs
    events = events.merge(files['DRUG'], on='case_id', how='left')
    
    # Join reactions
    events = events.merge(files['REAC'], on='case_id', how='left')
    
    # Join optional files if available
    for file_type in ['INDI', 'OUTC']:
        if file_type in files:
            events = events.merge(files[file_type], on='case_id', how='left')
    
    return events
```

### **Memory Management**

#### **Chunked Processing**
For large datasets, the system uses chunked processing:

```python
def process_large_file(file_path: Path, chunk_size: int = 10000) -> pd.DataFrame:
    """Process large files in chunks to manage memory"""
    chunks = []
    
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        # Process chunk
        processed_chunk = process_chunk(chunk)
        chunks.append(processed_chunk)
    
    return pd.concat(chunks, ignore_index=True)
```

#### **Automatic Memory Optimization**
```python
def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Optimize DataFrame memory usage"""
    
    # Convert object columns to category where appropriate
    for col in df.select_dtypes(include=['object']):
        if df[col].nunique() / len(df) < 0.5:  # Less than 50% unique
            df[col] = df[col].astype('category')
    
    # Downcast numeric types
    df = df.select_dtypes(include=['int']).apply(pd.to_numeric, downcast='integer')
    df = df.select_dtypes(include=['float']).apply(pd.to_numeric, downcast='float')
    
    return df
```

### **Error Handling**

#### **Encoding Issues**
```python
ENCODING_FALLBACKS = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

def load_with_encoding_fallback(file_path: Path) -> pd.DataFrame:
    """Load file with multiple encoding attempts"""
    
    for encoding in ENCODING_FALLBACKS:
        try:
            return pd.read_csv(file_path, encoding=encoding, sep='$', low_memory=False)
        except UnicodeDecodeError:
            logger.warning(f"Encoding {encoding} failed for {file_path}")
            continue
        except Exception as e:
            logger.error(f"Failed to load {file_path} with {encoding}: {e}")
            break
    
    raise ValueError(f"Could not load {file_path} with any encoding")
```

#### **Malformed Data Handling**
```python
def clean_malformed_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean common data quality issues"""
    
    # Remove rows with all NaN values
    df = df.dropna(how='all')
    
    # Handle invalid dates
    df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
    
    # Clean text fields
    text_columns = df.select_dtypes(include=['object']).columns
    for col in text_columns:
        df[col] = df[col].str.strip()  # Remove whitespace
        df[col] = df[col].replace('', np.nan)  # Convert empty strings to NaN
    
    return df
```

## 📊 Output Data Schema

### **Primary Output: `faers_events.parquet`**

Consolidated adverse event data with standardized schema:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `case_id` | string | Unique case identifier | "12345678" |
| `event_date` | datetime | Report receive date | "2024-01-15" |
| `age` | float | Patient age in years | 45.0 |
| `sex` | string | Patient sex | "F" |
| `country` | string | Reporting country | "US" |
| `drug` | string | Medication name | "ASPIRIN" |
| `reaction_pt` | string | MedDRA preferred term | "HEADACHE" |
| `serious` | string | Serious event indicator | "Y" |
| `outcome` | string | Patient outcome | "RECOVERED" |

### **Aggregated Outputs**

#### **`monthly_counts.csv`**
Overall monthly adverse event counts:

| Column | Type | Description |
|--------|------|-------------|
| `month` | datetime | Month (first day) |
| `event_count` | int | Total events |
| `unique_drugs` | int | Distinct drugs |
| `unique_reactions` | int | Distinct reactions |

#### **`monthly_by_drug.csv`**
Drug-specific monthly aggregations:

| Column | Type | Description |
|--------|------|-------------|
| `month` | datetime | Month (first day) |
| `drug` | string | Medication name |
| `event_count` | int | Events for drug |
| `reaction_count` | int | Distinct reactions |

#### **`monthly_by_reaction.csv`**
Reaction-specific monthly aggregations:

| Column | Type | Description |
|--------|------|-------------|
| `month` | datetime | Month (first day) |
| `reaction_pt` | string | MedDRA preferred term |
| `event_count` | int | Events for reaction |
| `drug_count` | int | Distinct drugs |

## 🔍 Sample Data

### **Built-in Sample Datasets**

Located in `data/processed/_samples/`:

#### **`faers_events.sample.parquet`**
- **Size**: ~50 rows
- **Time Range**: 3-4 months of data
- **Purpose**: Dashboard demonstration
- **Coverage**: Representative drugs and reactions

#### **Sample Data Generation**
```python
def create_sample_data(full_data: pd.DataFrame, sample_size: int = 50) -> pd.DataFrame:
    """Create representative sample from full dataset"""
    
    # Stratified sampling
    sample_data = full_data.groupby(['drug', 'reaction_pt']).apply(
        lambda x: x.sample(min(len(x), 2))
    ).reset_index(drop=True)
    
    # Ensure minimum sample size
    if len(sample_data) < sample_size:
        additional = full_data.sample(sample_size - len(sample_data))
        sample_data = pd.concat([sample_data, additional]).drop_duplicates()
    
    return sample_data.head(sample_size)
```

### **Sample Mode Activation**

#### **Command Line**
```bash
streamlit run src/app/streamlit_mvp.py -- --sample
```

#### **Environment Variable**
```bash
export AE_SAMPLE=1
streamlit run src/app/streamlit_mvp.py
```

#### **Automatic Detection**
```python
def is_sample_mode() -> bool:
    """Check if sample mode should be enabled"""
    return (
        os.getenv('AE_SAMPLE', '0') == '1' or
        '--sample' in sys.argv or
        not processed_data_exists()
    )
```

## 💊 Drug Review Data

### **WebMD Drug Reviews**

#### **Expected Structure**
```
data/raw/WebMD Drug Reviews Dataset/
└── webmd.csv
```

#### **Schema**
| Column | Description |
|--------|-------------|
| `drug_name` | Medication name |
| `review` | Patient review text |
| `rating` | Effectiveness rating |
| `date` | Review date |

### **UCI ML Drug Review Dataset**

#### **Expected Structure**
```
data/raw/UCI ML Drug Review Dataset/
├── drugsComTrain_raw.csv
└── drugsComTest_raw.csv
```

#### **Schema**
| Column | Description |
|--------|-------------|
| `drugName` | Medication name |
| `review` | Patient review text |
| `rating` | Patient rating |
| `date` | Review date |
| `usefulCount` | Helpful votes |

### **Review Processing Pipeline**

#### **Adverse Event Extraction**
```python
AE_KEYWORDS = [
    'headache', 'nausea', 'dizziness', 'fatigue', 'insomnia',
    'weight gain', 'weight loss', 'anxiety', 'depression',
    'constipation', 'diarrhea', 'vomiting', 'drowsiness'
]

def extract_adverse_events(review_text: str) -> List[str]:
    """Extract AE keywords from review text"""
    found_aes = []
    text_lower = review_text.lower()
    
    for keyword in AE_KEYWORDS:
        if keyword in text_lower:
            found_aes.append(keyword)
    
    return found_aes
```

#### **MedDRA Mapping**
```python
MEDDRA_MAPPING = {
    'headache': 'HEADACHE',
    'nausea': 'NAUSEA',
    'dizziness': 'DIZZINESS',
    'fatigue': 'FATIGUE',
    # ... additional mappings
}

def map_to_meddra(ae_keywords: List[str]) -> List[str]:
    """Map keywords to MedDRA preferred terms"""
    return [MEDDRA_MAPPING.get(kw, kw.upper()) for kw in ae_keywords]
```

## 🛠️ Data Management

### **File Size Considerations**

#### **Typical FAERS Quarter Sizes**
- **DEMO files**: 50-100MB per quarter
- **DRUG files**: 100-200MB per quarter
- **REAC files**: 30-80MB per quarter
- **Total per quarter**: 200-400MB
- **Multi-year datasets**: 5-20GB

#### **Processed File Sizes**
- **`faers_events.parquet`**: 500MB-2GB (depending on years)
- **Monthly aggregations**: 1-10MB each
- **Sample files**: <1MB each

### **Storage Optimization**

#### **Parquet Format Benefits**
- **Compression**: 50-70% size reduction vs CSV
- **Fast Loading**: Columnar storage for analytics
- **Type Preservation**: Maintains data types
- **Partial Reading**: Column selection support

#### **Git LFS for Large Files**
```bash
# Track large data files with Git LFS
git lfs track "data/processed/*.parquet"
git lfs track "data/processed/*.csv"

# Add .gitattributes
echo "data/processed/*.parquet filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
```

### **Data Validation**

#### **Automated Quality Checks**
```python
def validate_faers_data(df: pd.DataFrame) -> Dict[str, bool]:
    """Comprehensive data validation"""
    checks = {}
    
    # Required columns present
    required_cols = ['case_id', 'event_date', 'drug', 'reaction_pt']
    checks['required_columns'] = all(col in df.columns for col in required_cols)
    
    # Data completeness
    checks['case_id_complete'] = df['case_id'].notna().all()
    checks['drug_complete'] = df['drug'].notna().sum() / len(df) > 0.8
    
    # Date validity
    checks['valid_dates'] = df['event_date'].notna().sum() / len(df) > 0.9
    
    # Reasonable data ranges
    checks['reasonable_ages'] = (df['age'] >= 0).all() if 'age' in df.columns else True
    
    return checks
```

#### **Data Freshness Monitoring**
```python
def check_data_freshness(data_path: Path) -> Dict[str, Any]:
    """Monitor data currency and completeness"""
    
    # Find latest quarter
    quarters = discover_faers_quarters(data_path)
    latest_quarter = max(quarters) if quarters else None
    
    # Check processing status
    processed_files = list(Path("data/processed").glob("*.csv"))
    
    return {
        'latest_quarter': latest_quarter.name if latest_quarter else None,
        'quarters_available': len(quarters),
        'processed_files': len(processed_files),
        'last_updated': max(f.stat().st_mtime for f in processed_files) if processed_files else None
    }
```

## 🔍 Troubleshooting Data Issues

### **Common Problems and Solutions**

#### **1. File Not Found Errors**
```
FileNotFoundError: DEMO24Q1.txt not found
```

**Solution**: Check directory structure and file naming
```bash
# Verify structure
ls -la data/raw/faers_ascii_2024q1/ASCII/

# Check for naming variations
find data/raw -name "*DEMO*" -type f
```

#### **2. Encoding Errors**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte
```

**Solution**: System automatically tries multiple encodings, but you can manually specify:
```python
# Force specific encoding
df = pd.read_csv(file_path, encoding='latin-1')
```

#### **3. Memory Errors**
```
MemoryError: Unable to allocate array
```

**Solutions**:
- **Increase available RAM**
- **Process data in chunks**
- **Use sample mode for development**
- **Close other applications**

#### **4. Column Mapping Issues**
```
KeyError: 'PRIMARYID' not found in columns
```

**Solution**: Check column standardization mapping:
```python
# Debug column names
print("Available columns:", df.columns.tolist())

# Update mapping if needed
COLUMN_MAPPING.update({'NEW_COLUMN': 'standard_name'})
```

### **Data Verification Tools**

#### **File Discovery**
```bash
# Check what quarters are available
python -c "
from src.etl.faers_loader import discover_faers_quarters
from pathlib import Path
quarters = discover_faers_quarters(Path('data/raw'))
print('Available quarters:', [q.name for q in quarters])
"
```

#### **Schema Inspection**
```bash
# Inspect file schemas
python -c "
import pandas as pd
df = pd.read_csv('data/raw/faers_ascii_2024q1/ASCII/DEMO24Q1.txt', sep='$', nrows=5)
print('Columns:', df.columns.tolist())
print('Sample data:')
print(df.head())
"
```

#### **Data Quality Report**
```bash
# Run comprehensive data checks
python src/analysis/smoke_checks.py
```

## 📈 Performance Optimization

### **Processing Speed Tips**

#### **1. Use Appropriate Data Types**
```python
# Optimize memory and speed
df = df.astype({
    'case_id': 'category',
    'drug': 'category', 
    'reaction_pt': 'category',
    'age': 'float32'  # vs float64
})
```

#### **2. Parallel Processing**
```python
from multiprocessing import Pool

def process_quarters_parallel(quarters: List[Path]) -> pd.DataFrame:
    """Process multiple quarters in parallel"""
    with Pool() as pool:
        quarter_dfs = pool.map(process_single_quarter, quarters)
    return pd.concat(quarter_dfs, ignore_index=True)
```

#### **3. Incremental Processing**
```python
def incremental_update(existing_data: pd.DataFrame, new_quarter: Path) -> pd.DataFrame:
    """Add new quarter to existing processed data"""
    new_data = process_single_quarter(new_quarter)
    return pd.concat([existing_data, new_data]).drop_duplicates('case_id')
```

### **Storage Optimization**

#### **Compression Settings**
```python
# Optimize Parquet compression
df.to_parquet(
    'faers_events.parquet',
    compression='snappy',  # Good balance of speed/compression
    index=False
)

# For maximum compression
df.to_parquet(
    'faers_events.parquet',
    compression='gzip',
    index=False
)
```

---

**Next**: Learn about troubleshooting in the [Troubleshooting Guide](Troubleshooting).