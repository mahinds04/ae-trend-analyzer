# Welcome to AE Trend Analyzer Wiki

[![CI - QA & Smoke Tests](https://github.com/mahinds04/ae-trend-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/mahinds04/ae-trend-analyzer/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Overview

The **AE Trend Analyzer** is a comprehensive pharmaceutical safety analysis platform that processes FDA FAERS (Adverse Event Reporting System) data and drug review datasets to provide actionable insights through an intuitive Streamlit dashboard.

### 🚀 Key Features

- **📊 Interactive Dashboard**: Real-time filtering and visualization
- **🏥 FAERS Integration**: Official FDA adverse event data processing
- **💊 Multi-source Analysis**: WebMD + UCI drug review datasets
- **🔍 Advanced Filtering**: By drug, reaction, and time period
- **📈 Trend Visualization**: Professional charts with Plotly
- **🚨 Anomaly Detection**: STL decomposition, rolling Z-score, and Prophet methods
- **💡 Smart Insights**: Automated spike detection and ranking
- **🧪 Quality Assurance**: Automated testing and validation
- **⚡ Memory Optimized**: Efficient processing of large datasets

## 📚 Documentation Navigation

### For Users
- **[Getting Started](Getting-Started)** - Installation and quick setup
- **[User Guide](User-Guide)** - Dashboard features and usage
- **[Data Guide](Data-Guide)** - FAERS data requirements and structure
- **[Troubleshooting](Troubleshooting)** - Common issues and solutions
- **[FAQ](FAQ)** - Frequently asked questions

### For Developers
- **[Developer Guide](Developer-Guide)** - Development setup and workflow
- **[API Reference](API-Reference)** - Code structure and modules
- **[Contributing](Contributing)** - How to contribute to the project

## 🎯 Quick Start

```bash
# Clone and setup
git clone https://github.com/mahinds04/ae-trend-analyzer.git
cd ae-trend-analyzer
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Instant demo mode
streamlit run src/app/streamlit_mvp.py -- --sample
```

## 🌟 Live Demo

Try the live demo on Streamlit Cloud: [AE Trend Analyzer Demo](https://ae-trend-analyzer.streamlit.app) *(sample data mode)*

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/mahinds04/ae-trend-analyzer?style=social)
![GitHub forks](https://img.shields.io/github/forks/mahinds04/ae-trend-analyzer?style=social)
![GitHub issues](https://img.shields.io/github/issues/mahinds04/ae-trend-analyzer)

## 🤝 Community

- **GitHub Repository**: [mahinds04/ae-trend-analyzer](https://github.com/mahinds04/ae-trend-analyzer)
- **Issues & Bug Reports**: [GitHub Issues](https://github.com/mahinds04/ae-trend-analyzer/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/mahinds04/ae-trend-analyzer/discussions)

## 👨‍💻 Contact

**Developed by**: Mahin Das
- **Email**: mahin.das.ml@gmail.com
- **GitHub**: [@mahinds04](https://github.com/mahinds04)

---

⭐ **Star this repository if you found it helpful!**