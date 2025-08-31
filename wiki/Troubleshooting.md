# Troubleshooting

This guide helps you diagnose and resolve common issues with the AE Trend Analyzer.

## 🚨 Common Issues

### **Installation Problems**

#### **1. Python Version Errors**
```
ERROR: Python 3.10 or higher is required
```

**Solution**: Upgrade Python
```bash
# Check current version
python --version

# Windows: Download from python.org
# Linux: Update via package manager
sudo apt update && sudo apt install python3.10

# Mac: Use Homebrew
brew install python@3.10
```

#### **2. Virtual Environment Issues**
```
'venv' is not recognized as an internal command
```

**Solutions**:
```bash
# Windows: Use python -m venv instead
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac: Install venv if missing
sudo apt install python3-venv  # Ubuntu/Debian
python3 -m venv .venv
source .venv/bin/activate
```

#### **3. Dependency Installation Failures**
```
ERROR: Failed building wheel for package
```

**Solutions**:
```bash
# Update pip first
python -m pip install --upgrade pip

# Install build tools (Windows)
pip install wheel setuptools

# Install system dependencies (Linux)
sudo apt install python3-dev build-essential

# Try alternative installation
pip install --no-cache-dir -r requirements.txt
```

### **Data Loading Issues**

#### **1. File Not Found Errors**
```
FileNotFoundError: No such file or directory: 'data/raw/faers_ascii_2024q1'
```

**Diagnosis**:
```bash
# Check directory structure
ls -la data/raw/
find data/raw -type d -name "*faers*"
```

**Solutions**:
- Verify FAERS data is downloaded and extracted correctly
- Check directory naming matches expected patterns
- Ensure case sensitivity (Windows vs Linux)

#### **2. Empty Data Directory**
```
No FAERS quarters found in data/raw
```

**Solutions**:
```bash
# Create proper directory structure
mkdir -p data/raw/faers_ascii_2024q1/ASCII

# Verify downloads
ls -la data/raw/

# Use sample mode for testing
export AE_SAMPLE=1
streamlit run src/app/streamlit_mvp.py
```

#### **3. Encoding Issues**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x92
```

**Automatic Handling**: The system tries multiple encodings automatically

**Manual Fix**:
```python
# Force specific encoding in custom loader
import pandas as pd
df = pd.read_csv('problematic_file.txt', encoding='latin-1', sep='$')
```

### **Dashboard Problems**

#### **1. Dashboard Won't Start**
```
streamlit: command not found
```

**Solutions**:
```bash
# Verify installation
pip list | grep streamlit

# Reinstall if missing
pip install streamlit

# Check PATH issues
which streamlit  # Linux/Mac
where streamlit  # Windows
```

#### **2. Port Already in Use**
```
OSError: [Errno 48] Address already in use
```

**Solutions**:
```bash
# Use different port
streamlit run src/app/streamlit_mvp.py --server.port 8502

# Kill existing process (Linux/Mac)
lsof -ti:8501 | xargs kill -9

# Kill existing process (Windows)
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

#### **3. Empty Dashboard**
```
No data available for visualization
```

**Diagnosis**:
```python
# Check if processed data exists
import os
print("Processed files:", os.listdir("data/processed/"))

# Check sample data
print("Sample files:", os.listdir("data/processed/_samples/"))
```

**Solutions**:
- Run ETL pipeline: `python -m src.etl.build_all`
- Use sample mode: `streamlit run src/app/streamlit_mvp.py -- --sample`
- Verify data processing completed successfully

### **Memory and Performance Issues**

#### **1. Out of Memory Errors**
```
MemoryError: Unable to allocate 2.3 GiB
```

**Solutions**:
```bash
# Use sample mode
export AE_SAMPLE=1

# Process data in smaller chunks
# Edit chunk_size in src/config.py
CHUNK_SIZE = 5000  # Reduce from 10000

# Close other applications
# Add more RAM to system
```

#### **2. Slow Dashboard Loading**
```
Dashboard takes >30 seconds to load
```

**Optimizations**:
```python
# Enable Streamlit caching
@st.cache_data
def load_data():
    return pd.read_parquet("data/processed/faers_events.parquet")

# Use sample mode for development
export AE_SAMPLE=1

# Reduce data size
# Filter data to recent years only
```

#### **3. ETL Pipeline Timeouts**
```
Processing stopped after 30 minutes
```

**Solutions**:
```bash
# Process smaller date ranges
python -c "
from src.etl.faers_loader import process_date_range
process_date_range('2023-01-01', '2023-12-31')
"

# Use parallel processing
# Increase system resources
# Process quarters individually
```

## 🔧 Diagnostic Tools

### **Environment Check**
```bash
# Create diagnostic script
cat > check_environment.py << 'EOF'
import sys
import pandas as pd
import streamlit as st
import plotly
from pathlib import Path

print(f"Python version: {sys.version}")
print(f"Pandas version: {pd.__version__}")
print(f"Streamlit version: {st.__version__}")
print(f"Plotly version: {plotly.__version__}")

# Check data directories
data_raw = Path("data/raw")
data_processed = Path("data/processed")
print(f"Raw data dir exists: {data_raw.exists()}")
print(f"Processed data dir exists: {data_processed.exists()}")

if data_raw.exists():
    print(f"Raw data contents: {list(data_raw.iterdir())}")
if data_processed.exists():
    print(f"Processed data contents: {list(data_processed.iterdir())}")
EOF

python check_environment.py
```

### **Data Validation**
```bash
# Run built-in smoke tests
python src/analysis/smoke_checks.py

# Check specific data file
python -c "
import pandas as pd
try:
    df = pd.read_parquet('data/processed/faers_events.parquet')
    print(f'Data shape: {df.shape}')
    print(f'Columns: {df.columns.tolist()}')
    print(f'Date range: {df.event_date.min()} to {df.event_date.max()}')
except Exception as e:
    print(f'Error loading data: {e}')
"
```

### **Network and Permissions**
```bash
# Check file permissions
ls -la data/
ls -la data/processed/

# Check disk space
df -h .

# Test network connectivity (for cloud deployment)
curl -I https://streamlit.io
```

## 🐛 Debugging Techniques

### **Enable Debug Logging**
```python
# Add to top of problematic file
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add debug statements
logger.debug(f"Processing file: {file_path}")
logger.debug(f"Data shape after processing: {df.shape}")
```

### **Streamlit Debug Mode**
```bash
# Run with debug output
streamlit run src/app/streamlit_mvp.py --logger.level=debug

# Check browser console (F12) for JavaScript errors
# Look for Python traceback in terminal
```

### **Interactive Debugging**
```python
# Add to problematic code section
import pdb; pdb.set_trace()

# Or use iPython debugger
import IPython; IPython.embed()

# Run with debugging
python -m pdb src/etl/build_all.py
```

### **Memory Profiling**
```python
# Install memory profiler
pip install memory-profiler

# Profile function
@profile
def problematic_function():
    # Your code here
    pass

# Run with profiling
python -m memory_profiler your_script.py
```

## 🌐 Platform-Specific Issues

### **Windows Specific**

#### **1. Path Separator Issues**
```python
# Use Path objects instead of string concatenation
from pathlib import Path
data_path = Path("data") / "raw" / "faers_ascii_2024q1"

# Not: "data/raw/faers_ascii_2024q1"  # Fails on Windows
```

#### **2. Long Path Names**
```
FileNotFoundError: [Errno 2] The filename or extension is too long
```

**Solution**: Enable long path support or use shorter directory names
```bash
# Registry edit (admin required)
# Computer\HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem
# Set LongPathsEnabled to 1
```

#### **3. Virtual Environment Activation**
```bash
# Use full path if activation fails
C:\path\to\project\.venv\Scripts\activate.bat

# Or use Python directly
C:\path\to\project\.venv\Scripts\python.exe -m streamlit run src/app/streamlit_mvp.py
```

### **macOS Specific**

#### **1. Permission Denied Errors**
```bash
# Fix permissions
chmod +x .venv/bin/activate
chmod -R 755 data/

# Use sudo for system-wide packages (not recommended)
# Better: use virtual environment
```

#### **2. SSL Certificate Issues**
```bash
# Update certificates
/Applications/Python\ 3.10/Install\ Certificates.command

# Or install certificates manually
pip install --upgrade certifi
```

### **Linux Specific**

#### **1. Missing System Dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-dev python3-pip python3-venv build-essential

# CentOS/RHEL
sudo yum install python3-devel python3-pip gcc

# Arch Linux
sudo pacman -S python python-pip base-devel
```

#### **2. Permission Issues**
```bash
# Fix ownership
sudo chown -R $USER:$USER /path/to/project

# Fix permissions
chmod -R 755 data/
chmod +x scripts/*
```

## 🚀 Cloud Deployment Issues

### **Streamlit Cloud**

#### **1. Build Failures**
```
ERROR: Package installation failed
```

**Solutions**:
- Check `requirements-cloud.txt` is present
- Ensure all dependencies are available on PyPI
- Remove problematic packages (like Prophet for faster builds)

#### **2. Memory Limits**
```
Your app has exceeded the memory limit
```

**Solutions**:
- Force sample mode: Add `AE_SAMPLE=1` to secrets
- Optimize data loading and caching
- Reduce dataset size

#### **3. Startup Timeouts**
```
Your app is taking too long to load
```

**Solutions**:
- Use pre-processed sample data
- Optimize imports and data loading
- Add loading indicators

### **Docker Deployment**

#### **1. Container Build Failures**
```bash
# Check Dockerfile syntax
docker build --no-cache -t ae-trend-analyzer .

# Debug build process
docker build --progress=plain -t ae-trend-analyzer .
```

#### **2. Port Binding Issues**
```bash
# Check port mapping
docker run -p 8501:8501 ae-trend-analyzer

# Use different host port
docker run -p 8080:8501 ae-trend-analyzer
```

## 📊 Performance Optimization

### **Data Processing**

#### **1. Reduce Memory Usage**
```python
# Use chunked processing
chunk_size = 5000  # Reduce if needed

# Optimize data types
df = df.astype({
    'case_id': 'category',
    'drug': 'category',
    'reaction_pt': 'category'
})

# Process only necessary columns
df = df[['case_id', 'event_date', 'drug', 'reaction_pt']]
```

#### **2. Speed Up Loading**
```python
# Use Parquet instead of CSV
df.to_parquet('output.parquet', compression='snappy')

# Enable parallel processing
import multiprocessing
n_cores = multiprocessing.cpu_count()
```

### **Dashboard Performance**

#### **1. Optimize Caching**
```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    return pd.read_parquet("data.parquet")

@st.cache_data
def process_filters(data, drug_filter, reaction_filter):
    return data[data.drug.isin(drug_filter)]
```

#### **2. Reduce Computations**
```python
# Pre-compute aggregations
monthly_data = data.groupby(['month', 'drug']).size().reset_index()

# Use session state for expensive operations
if 'expensive_computation' not in st.session_state:
    st.session_state.expensive_computation = compute_expensive_thing()
```

## 🆘 Getting Help

### **Before Reporting Issues**

1. **Search Existing Issues**: Check [GitHub Issues](https://github.com/mahinds04/ae-trend-analyzer/issues)
2. **Try Sample Mode**: Verify issue persists with sample data
3. **Check System Requirements**: Ensure minimum requirements are met
4. **Update Dependencies**: Run `pip install -r requirements.txt --upgrade`

### **When Reporting Bugs**

Include the following information:

#### **System Information**
```bash
# Run diagnostic script
python -c "
import sys, platform
print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'Architecture: {platform.machine()}')
"

pip list | grep -E "(streamlit|pandas|plotly)"
```

#### **Error Details**
- Full error message and traceback
- Steps to reproduce the issue
- Expected vs actual behavior
- Screenshots (for UI issues)

#### **Environment Details**
- Operating system and version
- Python version
- Virtual environment setup
- Data size and source

### **Community Resources**

- **GitHub Issues**: [Report bugs and request features](https://github.com/mahinds04/ae-trend-analyzer/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/mahinds04/ae-trend-analyzer/discussions)
- **Documentation**: [Browse Wiki pages](https://github.com/mahinds04/ae-trend-analyzer/wiki)
- **Email Support**: mahin.das.ml@gmail.com

### **Emergency Workarounds**

#### **If Nothing Works**
```bash
# Start fresh with sample mode
git clone https://github.com/mahinds04/ae-trend-analyzer.git
cd ae-trend-analyzer
python -m venv fresh_env
fresh_env\Scripts\activate  # Windows
pip install streamlit pandas plotly
export AE_SAMPLE=1
streamlit run src/app/streamlit_mvp.py
```

#### **Quick Demo Without Installation**
- Try the [live demo on Streamlit Cloud](https://ae-trend-analyzer.streamlit.app)
- Use GitHub Codespaces for cloud development environment

---

**Next**: Learn about the code structure in [API Reference](API-Reference).