# FAQ

Frequently Asked Questions about the AE Trend Analyzer.

## 🎯 General Questions

### **What is the AE Trend Analyzer?**

The AE Trend Analyzer is a comprehensive pharmaceutical safety analysis platform that processes FDA FAERS (Adverse Event Reporting System) data and drug review datasets to provide actionable insights through an interactive Streamlit dashboard.

### **Who should use this tool?**

- **Pharmacovigilance professionals**: Safety signal detection and trend analysis
- **Regulatory affairs**: Monitoring adverse event patterns
- **Data scientists**: Pharmaceutical data analysis and research
- **Healthcare researchers**: Studying drug safety patterns
- **Students**: Learning about pharmacovigilance and data analysis

### **Is this tool suitable for regulatory submissions?**

The AE Trend Analyzer is designed for exploratory analysis and research purposes. While it uses official FDA FAERS data, any findings should be validated through proper regulatory channels and additional analysis before use in regulatory submissions.

### **What makes this different from other FAERS analysis tools?**

- **Integrated pipeline**: End-to-end processing from raw FAERS data to insights
- **Multi-source analysis**: Combines FAERS with drug review datasets
- **Advanced anomaly detection**: Multiple statistical methods including STL, Z-score, and Prophet
- **Interactive dashboard**: Real-time filtering and visualization
- **Open source**: Transparent, customizable, and free to use

## 💾 Data Questions

### **Where do I get FAERS data?**

Download FAERS quarterly data from the [FDA FAERS website](https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html). The system supports data from 2013 onwards.

### **How much data can the system handle?**

**System Requirements**:
- **Memory**: 8GB+ RAM recommended for multi-year analysis
- **Storage**: 10-20GB free space for raw and processed data
- **Processing**: Modern multi-core processor recommended

**Data Volumes**:
- **Single quarter**: 200-400MB raw, processes in 5-15 minutes
- **Multi-year datasets**: 5-20GB raw, may take several hours
- **Sample mode**: <1MB, loads instantly

### **What data formats are supported?**

**FAERS Data**:
- ASCII text files (pipe-delimited: `$`)
- Standard FAERS quarterly structure
- Both modern (2014+) and legacy (2013-) formats

**Review Data**:
- WebMD Drug Reviews Dataset (CSV)
- UCI ML Drug Review Dataset (CSV)

### **Can I use my own data?**

Yes! The system is designed to be extensible:

1. **Custom data loaders**: Add new modules in `src/etl/`
2. **Standard schema**: Map your data to standard columns
3. **Integration**: Include in ETL pipeline

See the [Developer Guide](Developer-Guide) for implementation details.

### **What about data privacy and compliance?**

- **FAERS data**: Publicly available, de-identified FDA data
- **Processing**: All processing occurs locally on your system
- **Storage**: Data remains on your local machine
- **No transmission**: No data sent to external services (except in cloud deployment)

## 🚀 Usage Questions

### **How do I start without downloading large datasets?**

Use **Sample Mode** for instant exploration:

```bash
# Method 1: Command line flag
streamlit run src/app/streamlit_mvp.py -- --sample

# Method 2: Environment variable
export AE_SAMPLE=1
streamlit run src/app/streamlit_mvp.py
```

Sample mode includes ~50 representative adverse events for testing all features.

### **What's the difference between sample mode and full mode?**

| Feature | Sample Mode | Full Mode |
|---------|-------------|-----------|
| **Data Size** | ~50 events | Millions of events |
| **Loading Time** | <5 seconds | 30+ seconds |
| **Memory Usage** | <50MB | 1-8GB |
| **Date Range** | 3-4 months | Multiple years |
| **Anomaly Detection** | Basic | Full algorithms |
| **Prophet Forecasting** | Disabled | Available |

### **How often should I update the data?**

**FAERS Updates**: FDA releases new quarterly data approximately 3 months after quarter end.

**Update Process**:
1. Download new quarter from FDA
2. Place in `data/raw/` directory
3. Re-run ETL pipeline: `python -m src.etl.build_all`
4. Dashboard automatically uses updated data

### **Can I analyze specific drugs or reactions only?**

Yes! Use the interactive filters in the dashboard:

1. **Drug Filter**: Select specific medications from dropdown
2. **Reaction Filter**: Choose adverse events of interest
3. **Date Range**: Focus on specific time periods
4. **Combined Filtering**: Use multiple filters simultaneously

Filters apply to all visualizations and analyses in real-time.

### **What anomaly detection methods are available?**

The system includes three complementary methods:

#### **1. STL Decomposition**
- **Purpose**: Separate trend, seasonal, and irregular components
- **Best for**: Understanding underlying patterns
- **Use case**: Long-term trend analysis

#### **2. Rolling Z-Score**
- **Purpose**: Statistical outlier detection
- **Best for**: Identifying significant deviations
- **Use case**: Spike detection and investigation

#### **3. Prophet Forecasting** *(Full mode only)*
- **Purpose**: Time series forecasting with anomaly detection
- **Best for**: Future trend prediction
- **Use case**: Anticipating future patterns

## 🛠️ Technical Questions

### **What programming languages and frameworks are used?**

**Core Technologies**:
- **Python 3.10+**: Main programming language
- **Streamlit**: Web dashboard framework
- **Pandas**: Data processing and analysis
- **Plotly**: Interactive visualizations
- **Parquet**: Efficient data storage format

**Optional Dependencies**:
- **Prophet**: Time series forecasting (full mode)
- **Statsmodels**: Statistical analysis
- **Scikit-learn**: Machine learning utilities

### **Can I run this on different operating systems?**

Yes, the AE Trend Analyzer supports:

- **Windows 10/11**: Full support with PowerShell/CMD
- **macOS**: Full support (Intel and Apple Silicon)
- **Linux**: Full support (Ubuntu, CentOS, Debian, etc.)

See [Getting Started](Getting-Started) for platform-specific installation instructions.

### **What are the minimum system requirements?**

**Minimum (Sample Mode)**:
- 4GB RAM
- 2GB free disk space
- Python 3.10+
- Internet connection (for package installation)

**Recommended (Full Mode)**:
- 8GB+ RAM
- 20GB+ free disk space
- Multi-core processor
- SSD storage for better performance

### **Can I deploy this to the cloud?**

Yes! Multiple deployment options:

#### **Streamlit Cloud** *(Recommended)*
- Free hosting for public repositories
- Automatic deployment from GitHub
- Built-in sample mode support
- See [Deployment Guide](Deployment-Guide)

#### **Docker**
```bash
docker build -t ae-trend-analyzer .
docker run -p 8501:8501 ae-trend-analyzer
```

#### **Custom Cloud Platforms**
- AWS, GCP, Azure compatible
- Requires container or Python environment
- May need custom configuration

### **How do I customize the analysis?**

**Adding New Adverse Event Keywords**:
```python
# Edit src/etl/reviews_loader.py
AE_KEYWORDS = [
    'headache', 'nausea', 'dizziness',
    # Add your keywords here
    'new_symptom', 'another_ae'
]
```

**Extending MedDRA Mapping**:
```python
# Update mapping in src/etl/reviews_loader.py
MEDDRA_MAPPING = {
    'headache': 'HEADACHE',
    # Add your mappings here
    'new_symptom': 'NEW_MEDDRA_PT'
}
```

**Custom Visualizations**:
See [Developer Guide](Developer-Guide) for adding new charts and analysis methods.

## 🐛 Troubleshooting Questions

### **The dashboard shows "No data available"**

**Possible Causes**:
1. **Missing processed data**: Run ETL pipeline first
2. **Filter too restrictive**: Broaden date/drug/reaction filters
3. **Sample data missing**: Check `data/processed/_samples/` directory

**Solutions**:
```bash
# Process data
python -m src.etl.build_all

# Use sample mode
export AE_SAMPLE=1
streamlit run src/app/streamlit_mvp.py

# Check processed files
ls data/processed/
```

### **ETL pipeline fails with encoding errors**

The system automatically tries multiple encodings, but if issues persist:

**Manual Fix**:
```python
# Check file encoding
file -bi your_file.txt

# Try different encoding
df = pd.read_csv('file.txt', encoding='latin-1', sep='$')
```

### **Dashboard is very slow**

**Performance Optimizations**:
1. **Use sample mode** for development
2. **Apply filters early** to reduce data size
3. **Close other applications** to free memory
4. **Upgrade hardware** (more RAM, SSD storage)

See [Troubleshooting](Troubleshooting) for more detailed solutions.

### **Memory errors during processing**

**Solutions**:
```bash
# Reduce chunk size (edit src/config.py)
CHUNK_SIZE = 5000  # Default: 10000

# Use sample mode
export AE_SAMPLE=1

# Process fewer years at once
# Split large datasets into smaller periods
```

## 🤝 Development Questions

### **How can I contribute to the project?**

We welcome contributions! See [Developer Guide](Developer-Guide) for details:

1. **Fork the repository** on GitHub
2. **Create feature branch**: `git checkout -b feature/your-feature`
3. **Make changes** following coding standards
4. **Add tests** for new functionality
5. **Submit pull request** with clear description

### **What coding standards are used?**

**Code Quality Tools**:
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting and style checking
- **pre-commit**: Automated quality checks

**Setup**:
```bash
pip install black isort flake8 pre-commit
pre-commit install
pre-commit run --all-files
```

### **How do I add new data sources?**

**Implementation Steps**:
1. Create new loader module in `src/etl/`
2. Implement standard loading interface
3. Add column mapping to standard schema
4. Integrate into `build_all.py` pipeline
5. Add tests and documentation

**Example Structure**:
```python
def load_new_source_data() -> pd.DataFrame:
    """Load data from new source with standard schema"""
    # Implementation
    return standardized_df
```

### **Can I extend the anomaly detection methods?**

Yes! Add new algorithms in `src/app/streamlit_mvp.py`:

```python
def detect_anomalies_custom(data: pd.DataFrame) -> Dict[str, Any]:
    """Custom anomaly detection algorithm"""
    # Your implementation
    return {
        'anomalies': anomaly_indices,
        'scores': anomaly_scores,
        'metadata': algorithm_info
    }
```

## 🎓 Learning Questions

### **I'm new to pharmacovigilance. Where should I start?**

**Learning Path**:
1. **Start with sample mode** to explore the dashboard
2. **Review FAERS documentation** on FDA website
3. **Read about MedDRA** terminology system
4. **Explore the code** to understand data processing
5. **Join community discussions** for questions

**Key Concepts**:
- **Adverse Event**: Undesirable medical occurrence associated with medication
- **MedDRA**: Medical Dictionary for Regulatory Activities (standardized terminology)
- **FAERS**: FDA Adverse Event Reporting System (post-market safety database)
- **Signal Detection**: Statistical methods to identify potential safety issues

### **What statistical methods should I understand?**

**For Basic Usage**:
- **Descriptive statistics**: Counts, frequencies, trends
- **Time series analysis**: Temporal patterns and seasonality
- **Filtering and aggregation**: Data subset analysis

**For Advanced Analysis**:
- **STL Decomposition**: Seasonal trend decomposition
- **Z-score analysis**: Statistical outlier detection
- **Time series forecasting**: Prophet methodology
- **Anomaly detection**: Pattern recognition techniques

### **How reliable are FAERS data for safety decisions?**

**Important Considerations**:
- **Reporting bias**: Not all adverse events are reported
- **Causality**: Association doesn't imply causation
- **Data quality**: Varies by source and completeness
- **Context needed**: Requires medical and regulatory expertise

**Best Practices**:
- Use for **hypothesis generation**, not definitive conclusions
- **Combine with other data sources** (clinical trials, literature)
- **Consult healthcare professionals** for medical interpretation
- **Consider regulatory guidance** for decision-making

## 🌐 Deployment Questions

### **Can I use this for commercial purposes?**

Yes! The project uses the **MIT License**, which allows:
- Commercial use
- Modification and distribution
- Private use
- Patent use (within license terms)

**Requirements**:
- Include original license and copyright notice
- No warranty provided

### **How do I set up automatic data updates?**

**Automated Pipeline Setup**:
```bash
# Create update script
cat > update_data.sh << 'EOF'
#!/bin/bash
cd /path/to/ae-trend-analyzer
source .venv/bin/activate
python -m src.etl.build_all
EOF

# Schedule with cron (quarterly updates)
crontab -e
# Add: 0 2 1 1,4,7,10 * /path/to/update_data.sh
```

### **What about data backup and recovery?**

**Backup Strategy**:
```bash
# Backup processed data
tar -czf backup_$(date +%Y%m%d).tar.gz data/processed/

# Backup configuration and custom code
git bundle create backup.bundle HEAD

# Automated backup script
rsync -av data/processed/ backup_location/
```

### **Can I integrate this with other systems?**

**Integration Options**:
- **API endpoints**: Extend Streamlit app with API functionality
- **Database integration**: Export to SQL databases
- **Report generation**: Automated PDF/HTML reports
- **Alert systems**: Email/Slack notifications for anomalies

See [Developer Guide](Developer-Guide) for implementation examples.

## 📞 Support Questions

### **Where can I get help?**

**Community Support**:
- **GitHub Issues**: [Bug reports and feature requests](https://github.com/mahinds04/ae-trend-analyzer/issues)
- **GitHub Discussions**: [Questions and community help](https://github.com/mahinds04/ae-trend-analyzer/discussions)
- **Wiki Documentation**: Comprehensive guides and tutorials

**Direct Contact**:
- **Email**: mahin.das.ml@gmail.com
- **GitHub**: [@mahinds04](https://github.com/mahinds04)

### **How do I report bugs or request features?**

**Bug Reports**:
1. Search existing issues first
2. Include system information and error details
3. Provide steps to reproduce
4. Include screenshots for UI issues

**Feature Requests**:
1. Describe the use case and benefits
2. Provide examples or mockups
3. Consider implementation complexity
4. Discuss with community first

### **Is there a roadmap for future features?**

**Planned Enhancements**:
- Enhanced statistical methods
- Additional data source integrations
- Improved performance optimization
- API development for integration
- Advanced visualization options

Check [GitHub Issues](https://github.com/mahinds04/ae-trend-analyzer/issues) with "enhancement" label for detailed roadmap.

### **Can I get training or consulting?**

For training, consulting, or custom development:
- Contact: mahin.das.ml@gmail.com
- Services available for implementation, customization, and training
- Community workshops and presentations by arrangement

---

**Need more help?** Check our comprehensive documentation or reach out to the community!