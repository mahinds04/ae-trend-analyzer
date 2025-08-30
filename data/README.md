# Data Directory Structure Guide

This document explains the expected data layout for the AE Trend Analyzer and where processed outputs are generated.

## 📁 Directory Overview

```
data/
├── raw/                        # Input data (place your downloads here)
│   ├── faers_ascii_2024q1/     # FAERS quarterly data
│   ├── faers_ascii_2024q2/
│   ├── ...
│   ├── WebMD Drug Reviews Dataset/
│   └── UCI ML Drug Review Dataset/
├── processed/                  # Generated output files (automated)
│   ├── faers_events.parquet    # Consolidated adverse events
│   ├── monthly_counts.csv      # Overall monthly aggregations
│   ├── monthly_by_drug.csv     # Drug-specific monthly data
│   ├── monthly_by_reaction.csv # Reaction-specific monthly data
│   └── _samples/               # Sample data for demo mode
└── README.md                   # This file
```

## 🏥 FAERS Data Layout

### Expected Quarterly Structure

Each FAERS quarter should follow this structure:

```
data/raw/faers_ascii_2024q1/
├── ASCII/                      # Main data directory (case insensitive)
│   ├── DEMO24Q1.txt           # 📊 Demographics (REQUIRED)
│   ├── DRUG24Q1.txt           # 💊 Drug information (REQUIRED)
│   ├── REAC24Q1.txt           # ⚠️ Adverse reactions (REQUIRED)
│   ├── INDI24Q1.txt           # 🎯 Indications (optional)
│   ├── OUTC24Q1.txt           # 📈 Outcomes (optional)
│   ├── RPSR24Q1.txt           # 📋 Report sources (optional)
│   └── THER24Q1.txt           # 📅 Therapy dates (optional)
├── FAQs.pdf                   # Documentation
└── Readme.pdf                 # FDA documentation
```

### Supported Naming Patterns

#### Quarter Folder Names
- **Pattern**: `faers_ascii_YYYYqN`
- **Examples**:
  - `faers_ascii_2024q1` ✅
  - `faers_ascii_2024Q2` ✅ (case insensitive)
  - `faers_ascii_2013q4` ✅ (legacy format)
  - `faers_ascii_2025q1` ✅ (future quarters)

#### ASCII Directory
- **Options**: `ASCII/` or `ascii/` (case insensitive)
- **Both work**: Loader automatically detects correct case

#### File Names
- **Pattern**: `[TYPE][YEAR]Q[QUARTER].txt`
- **Examples**:
  - 2024 Q1: `DEMO24Q1.txt`, `DRUG24Q1.txt`, `REAC24Q1.txt`
  - 2013 Q4: `DEMO13Q4.txt`, `DRUG13Q4.txt`, `REAC13Q4.txt`
  - Alternative: `DEMO2024Q1.txt` (full year format also supported)

### File Contents & Importance

| File Type | Description | Importance | Used For |
|-----------|-------------|------------|----------|
| **DEMO** | Patient demographics, event dates | **REQUIRED** | Case linking, temporal analysis |
| **REAC** | Adverse reactions (MedDRA terms) | **REQUIRED** | Primary analysis target |
| **DRUG** | Drug names and details | **REQUIRED** | Drug-specific analysis |
| **OUTC** | Outcome classifications | Recommended | Serious event flagging |
| **INDI** | Indication/diagnosis codes | Optional | Therapeutic context |
| **THER** | Therapy start/stop dates | Optional | Treatment duration |
| **RPSR** | Report source information | Optional | Data provenance |

### Data Format Notes

- **Delimiter**: Files use `$` (dollar sign) as field separator
- **Encoding**: Usually UTF-8, with automatic fallback to latin-1
- **Headers**: First row contains column names
- **Size**: Individual files can range from MB to GB
- **Content**: Text format with standardized FDA field structures

## 💊 Review Datasets

### WebMD Drug Reviews
```
data/raw/WebMD Drug Reviews Dataset/
└── webmd.csv                  # User reviews from WebMD
```

### UCI ML Drug Reviews
```
data/raw/UCI ML Drug Review Dataset/
├── drugsComTrain_raw.csv      # Training dataset
└── drugsComTest_raw.csv       # Test dataset
```

## 📊 Processed Outputs

After running the ETL pipeline (`python run_etl.py`), these files are automatically generated:

### Primary Output Files

#### `faers_events.parquet`
- **Content**: Consolidated adverse event records from all quarters
- **Format**: Parquet (compressed, fast loading)
- **Columns**: `event_date`, `case_id`, `drug`, `reaction_pt`, `sex`, `age`, `country`, `serious`
- **Size**: Millions of records (55M+ in sample dataset)

#### `monthly_counts.csv`
- **Content**: Overall adverse event counts by month
- **Format**: CSV with columns `ym` (YYYY-MM), `count`
- **Usage**: Dashboard overall trend analysis
- **Example**:
  ```csv
  ym,count
  2013-01,2670
  2013-02,2180
  2013-03,2610
  ```

#### `monthly_by_drug.csv`
- **Content**: Monthly counts grouped by drug
- **Format**: CSV with columns `ym`, `drug`, `count`
- **Usage**: Drug-specific trend analysis
- **Example**:
  ```csv
  ym,drug,count
  2013-01,LIPITOR,45
  2013-01,ASPIRIN,32
  2013-02,LIPITOR,38
  ```

#### `monthly_by_reaction.csv`
- **Content**: Monthly counts grouped by adverse reaction
- **Format**: CSV with columns `ym`, `reaction_pt`, `count`
- **Usage**: Reaction-specific trend analysis
- **Example**:
  ```csv
  ym,reaction_pt,count
  2013-01,NAUSEA,156
  2013-01,HEADACHE,134
  2013-02,NAUSEA,142
  ```

### Sample Data (Demo Mode)

#### `_samples/` Directory
- **Purpose**: Lightweight data for testing and demos
- **Content**: 50-row samples of each main file
- **Usage**: Activated with `--sample` flag or `AE_SAMPLE=1` environment variable
- **Files**:
  - `monthly_counts.sample.csv`
  - `monthly_by_drug.sample.csv`
  - `monthly_by_reaction.sample.csv`

## 🔧 Data Processing Pipeline

### ETL Workflow
1. **Discovery**: Auto-detect FAERS quarters in `data/raw/`
2. **Loading**: Read and normalize each quarter's ASCII files
3. **Schema Harmonization**: Handle differences between years (2013 vs 2024 formats)
4. **Joining**: Link DEMO, REAC, DRUG tables by case ID
5. **Cleaning**: Remove duplicates, handle missing data
6. **Aggregation**: Generate monthly summaries
7. **Output**: Save to `data/processed/`

### Memory Management
- **Chunked Reading**: Large files (>100MB) processed in chunks
- **Optimized Joins**: Pre-filter data before expensive merge operations
- **Compression**: Parquet format for efficient storage
- **Progress Tracking**: Real-time progress indicators during processing

### Error Handling
- **Encoding Fallbacks**: UTF-8 → latin-1 → cp1252 if needed
- **Missing Files**: Graceful degradation if optional files absent
- **Malformed Data**: Skip bad lines with warnings
- **Memory Issues**: Automatic chunk size adjustment for large files

## 🚀 Quick Start

### 1. Download FAERS Data
1. Visit [FDA FAERS Downloads](https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html)
2. Download quarterly ASCII files (e.g., `faers_ascii_2024q1.zip`)
3. Extract to `data/raw/faers_ascii_2024q1/`
4. Repeat for additional quarters

### 2. Run ETL Pipeline
```bash
python run_etl.py
```

### 3. Launch Dashboard
```bash
# Full data
python run_dashboard.py

# Sample data (faster)
python run_dashboard.py --sample
```

## ❓ Troubleshooting

### Common Issues

**❌ "No FAERS quarterly folders found"**
- Check folder naming: `faers_ascii_YYYYqN`
- Ensure ASCII/ subdirectory exists
- Verify file permissions

**❌ "No ASCII directory found"**
- Look for `ASCII/` or `ascii/` folder inside quarter directory
- Check case sensitivity on Linux/Mac

**❌ "Missing DEMO or REAC files"**
- DEMO and REAC files are required for processing
- Check file naming patterns: `DEMO*.txt`, `REAC*.txt`
- Verify files aren't corrupted

**⚠️ "Delimiter parsing errors"**
- FAERS files use `$` delimiter (not tab or comma)
- System automatically handles this, but manual inspection may show dollar signs

**💾 "Memory or performance issues"**
- Large quarters (2024+) can be 500MB+ per file
- System uses chunked processing automatically
- Consider processing quarters individually if needed

### File Validation

Run this command to validate your data structure:
```bash
python -c "
import sys; sys.path.append('src')
from etl.faers_loader import discover_quarters
quarters = discover_quarters('data/raw')
print(f'Found {len(quarters)} valid quarters')
for q in quarters: print(f'  ✅ {q.name}')
"
```

## � Performance Tips

### For Large Datasets (10+ quarters)
- **Memory**: 8GB+ RAM recommended for full processing
- **Storage**: 2-3x source data size for processing workspace
- **Time**: 5-15 minutes per quarter depending on size

### For Quick Testing
- Use sample mode: `--sample` or `AE_SAMPLE=1`
- Process single quarter by temporarily moving others
- Check logs for processing progress and bottlenecks

## 📞 Support

- **Issues**: Check console output for specific error messages
- **Logs**: ETL pipeline provides detailed progress information
- **Validation**: Use built-in discovery tools to verify data structure
- **Community**: GitHub Issues for reproducible problems

### FAERS Quarterly Data

Each FAERS quarter should follow this structure:

```
data/raw/faers_ascii_2024q1/
├── FAQs.pdf                      # Documentation (optional)
├── Readme.pdf                    # Documentation (optional)  
└── ASCII/                        # Required: contains data files
    ├── DEMO24Q1.txt              # Demographics (required)
    ├── DRUG24Q1.txt              # Drug information (required)
    ├── REAC24Q1.txt              # Adverse reactions (required)
    ├── INDI24Q1.txt              # Indications (optional)
    ├── OUTC24Q1.txt              # Outcomes (optional)
    ├── RPSR24Q1.txt              # Report sources (optional)
    └── THER24Q1.txt              # Therapy dates (optional)
```

**Naming Patterns Supported:**
- **Modern**: `faers_ascii_2024q1/`, `faers_ascii_2024Q4/`
- **Legacy**: `faers_ascii_2013q1/`, `faers_ascii_2013q4/`
- **File Format**: `{TABLE}{YY}Q{N}.txt` (e.g., `DEMO24Q1.txt`, `DRUG13Q4.txt`)

**Minimal Required Files** (for basic functionality):
- `DEMO*.txt` - Patient demographics
- `DRUG*.txt` - Drug/product information  
- `REAC*.txt` - Reported adverse reactions

### Review Datasets

```
data/raw/WebMD Drug Reviews Dataset/
└── webmd.csv                     # Patient reviews from WebMD

data/raw/UCI ML Drug Review Dataset/
├── drugsComTrain_raw.csv         # Training set from Drugs.com
└── drugsComTest_raw.csv          # Test set from Drugs.com
```

## 📋 Sample File Listings

### Complete FAERS Quarter Example (2024 Q1)
```
data/raw/faers_ascii_2024q1/ASCII/
├── DEMO24Q1.txt    (50MB)    # 450K patient records
├── DRUG24Q1.txt    (180MB)   # 1.2M drug records  
├── REAC24Q1.txt    (85MB)    # 800K reaction records
├── INDI24Q1.txt    (25MB)    # 300K indication records
├── OUTC24Q1.txt    (8MB)     # 200K outcome records
├── RPSR24Q1.txt    (15MB)    # 250K reporter records
└── THER24Q1.txt    (12MB)    # 180K therapy records
```

### Legacy Quarter Example (2013 Q4)
```
data/raw/faers_ascii_2013q4/ascii/
├── DEMO13Q4.txt    (35MB)    # 320K patient records
├── DRUG13Q4.txt    (120MB)   # 900K drug records
├── REAC13Q4.txt    (60MB)    # 650K reaction records
├── INDI13Q4.txt    (18MB)    # 220K indication records
├── OUTC13Q4.txt    (6MB)     # 150K outcome records
├── RPSR13Q4.txt    (10MB)    # 180K reporter records
└── THER13Q4.txt    (8MB)     # 130K therapy records
```

## 📈 Generated Outputs

### Processed Data Files

After running the ETL pipeline, these files are created in `data/processed/`:

```
data/processed/
├── faers_events.parquet          # Master event dataset
├── monthly_counts.csv            # Overall monthly AE counts
├── monthly_by_drug.csv           # Monthly counts per drug
├── monthly_by_reaction.csv       # Monthly counts per reaction  
├── reviews_extracted.csv         # Processed reviews with AE terms
└── _samples/                     # Demo subset (≈50 rows each)
    ├── faers_events.sample.parquet
    ├── monthly_counts.sample.csv
    ├── monthly_by_drug.sample.csv
    └── monthly_by_reaction.sample.csv
```

### File Schemas

**faers_events.parquet** (Main Dataset):
```
Columns: event_date, case_id, drug, reaction_pt, sex, age, country, serious
Types:   datetime64, object, object, object, object, float64, object, object
Size:    ~50-200MB per year depending on reports
```

**monthly_counts.csv** (Overall Trends):
```
Columns: ym (YYYY-MM), count
Example: 2024-01, 125430
Size:    ~1-5KB (120+ rows for 10 years)
```

**monthly_by_drug.csv** (Drug-specific Trends):
```
Columns: ym, drug, count  
Example: 2024-01, LIPITOR, 245
Size:    ~5-50MB (depends on unique drugs)
```

**monthly_by_reaction.csv** (Reaction-specific Trends):
```
Columns: ym, reaction_pt, count
Example: 2024-01, HEADACHE, 1832
Size:    ~2-20MB (depends on unique reactions)
```

## 💾 Disk Usage Estimates

### Raw Data Storage
- **Single FAERS Quarter**: 300-500MB (compressed), 800MB-1.5GB (uncompressed)
- **10 Years of Quarters**: ~15-30GB total
- **Review Datasets**: ~200MB (WebMD + UCI combined)
- **Total Raw**: ~20-35GB for complete dataset

### Processed Data Storage  
- **Parquet Files**: ~80% compression vs raw
- **CSV Aggregations**: <100MB total
- **Sample Files**: <5MB total
- **Total Processed**: ~1-3GB

### Working Memory
- **ETL Processing**: 2-8GB RAM recommended for large quarters
- **Dashboard**: <500MB for sample mode, 1-2GB for full data
- **Large File Warning**: Triggered for DRUG files >100MB

## ⚠️ Important Notes

### Data Availability
- **Raw data is NOT included** in this repository due to size limits
- Download datasets manually from official sources
- See main README.md for download links

### File Encoding
- FAERS files may use `latin-1`, `cp1252`, or `utf-8` encoding
- Loader automatically tries multiple encodings
- Some special characters may require manual review

### Data Quality
- FAERS contains duplicate reports (automatically removed)
- Date formats vary across years (automatically normalized)  
- Missing values are common (~5-15% in some fields)
- Review datasets may contain informal medical terminology

### Performance Tips
- Process quarters individually for memory-constrained systems
- Use sample mode for development/testing
- Consider quarterly processing for systems with <8GB RAM
- Generated Parquet files load 10x faster than raw text files

---

For detailed usage instructions, see the main [README.md](../README.md) in the project root.
