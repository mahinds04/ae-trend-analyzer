# Data Directory Structure

This directory contains raw pharmaceutical adverse event data and processed outputs for the AE Trend Analyzer.

## 📁 Directory Layout

```
data/
├── raw/                           # Input datasets (excluded from git)
│   ├── faers_ascii_YYYYqN/       # FDA FAERS quarterly data
│   ├── WebMD Drug Reviews Dataset/
│   └── UCI ML Drug Review Dataset/
├── processed/                     # Generated outputs 
│   ├── _samples/                  # Demo samples (~50 rows each)
│   ├── *.parquet                  # Main event dataset
│   └── *.csv                      # Aggregated monthly counts
└── README.md                      # This file
```

## 📊 Expected Raw Data Layouts

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
