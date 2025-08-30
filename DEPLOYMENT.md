# Streamlit Cloud Deployment Guide

This guide walks through deploying the AE Trend Analyzer to Streamlit Cloud for public access.

## 🚀 Quick Deploy

### Option 1: One-Click Deploy
[![Deploy to Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/new?repository=https://github.com/mahinds04/ae-trend-analyzer)

### Option 2: Manual Deployment

1. **Fork/Clone Repository**
   ```bash
   git clone https://github.com/mahinds04/ae-trend-analyzer.git
   ```

2. **Push to Your GitHub**
   ```bash
   git remote set-url origin https://github.com/YOUR_USERNAME/ae-trend-analyzer.git
   git push origin master
   ```

3. **Deploy via Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Set main file path: `streamlit_app.py`
   - Click "Deploy!"

## 📋 Deployment Configuration

### Required Files for Streamlit Cloud

#### `streamlit_app.py` (Entry Point)
- Main entry point for Streamlit Cloud
- Automatically enables sample mode
- Handles path configuration for cloud environment

#### `requirements-cloud.txt` (Dependencies)
- Optimized dependencies for cloud deployment
- Excludes heavy development tools
- Comments out Prophet for faster builds

#### `.streamlit/config.toml` (Configuration)
- Theme customization
- Cloud-optimized settings
- Performance configurations

#### `packages.txt` (System Dependencies)
- Required system packages
- Build tools for compilation

### Sample Data Included
- `data/processed/_samples/` - Pre-loaded sample data
- Instant functionality without data setup
- ~50 rows per dataset for fast loading

## ⚡ Cloud Optimizations

### Performance Features
- **Sample Mode**: Lightweight datasets for instant loading
- **Optimized Dependencies**: Minimal required packages
- **Efficient Caching**: Streamlit caching for data operations
- **Responsive Design**: Works on mobile and desktop

### Resource Management
- **Memory Efficient**: Sample data uses <50MB RAM
- **Fast Startup**: <10 second cold start time
- **Bandwidth Optimized**: Minimal data transfer
- **CDN Ready**: Static assets cached globally

## 🎯 Demo Features Available

### Interactive Dashboard
- **Real-time Filtering**: Drug, reaction, and time filters
- **Anomaly Detection**: STL decomposition and rolling Z-score
- **Visual Insights**: Spike overlays and insights panel
- **Professional UI**: Gradient headers and modern styling

### Sample Data Coverage
- **Time Range**: 2013-2024 sample periods
- **Drugs**: Representative medication sample
- **Reactions**: Common adverse events
- **Geographic**: Multi-country data

## 🔧 Customization Options

### Theme Customization
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF6B6B"        # Accent color
backgroundColor = "#FFFFFF"     # Main background
secondaryBackgroundColor = "#F0F2F6"  # Sidebar background
textColor = "#262730"          # Text color
```

### Environment Variables
- `AE_SAMPLE=1`: Force sample mode (auto-enabled in cloud)
- `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`: Disable analytics

### Advanced Configuration
```toml
[server]
headless = true              # Required for cloud
enableCORS = false          # Security setting
maxUploadSize = 200         # File upload limit (MB)

[browser]
gatherUsageStats = false    # Privacy setting
```

## 🌐 Access & Sharing

### Public URL
Once deployed, your app will be available at:
```
https://YOUR_USERNAME-ae-trend-analyzer-streamlit-app-HASH.streamlit.app
```

### Custom Domain (Streamlit Pro)
For custom domains:
1. Upgrade to Streamlit Pro
2. Configure DNS settings
3. Add custom domain in dashboard

## 🔍 Monitoring & Analytics

### Built-in Metrics
- **Usage Statistics**: Visitor counts and session data
- **Performance Monitoring**: Load times and error rates
- **Resource Usage**: Memory and CPU utilization

### Custom Analytics
Add to `streamlit_app.py`:
```python
import streamlit as st

# Google Analytics (optional)
st.components.v1.html("""
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
""", height=0)
```

## 🛠️ Troubleshooting

### Common Issues

**❌ "Module not found" errors**
- Check `requirements-cloud.txt` includes all dependencies
- Verify import paths in `streamlit_app.py`

**❌ "File not found" errors**
- Ensure sample data files are committed to git
- Check `.gitignore` allows sample files

**❌ "Build timeout" errors**
- Comment out heavy dependencies (Prophet)
- Use `requirements-cloud.txt` instead of full requirements

**❌ "Memory exceeded" errors**
- Verify sample mode is enabled
- Check data file sizes in `_samples/`

### Performance Optimization

**Faster Cold Starts**
```python
@st.cache_data
def load_sample_data():
    # Cache data loading
    return pd.read_csv('data/processed/_samples/monthly_counts.sample.csv')
```

**Reduced Memory Usage**
```python
# Use efficient data types
df = df.astype({
    'count': 'int32',
    'ym': 'category'
})
```

## 🚀 Advanced Deployment

### Multi-Environment Setup
1. **Development**: Local with full data
2. **Staging**: Cloud with sample data  
3. **Production**: Cloud with optimized data

### CI/CD Integration
```yaml
# .github/workflows/deploy.yml
name: Deploy to Streamlit Cloud
on:
  push:
    branches: [master]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Trigger Streamlit deployment
        run: curl -X POST ${{ secrets.STREAMLIT_WEBHOOK_URL }}
```

### Environment-Specific Configuration
```python
import os
import streamlit as st

# Detect environment
is_cloud = 'STREAMLIT_SHARING' in os.environ or 'streamlit.app' in st.get_option('server.baseUrlPath', '')

if is_cloud:
    # Cloud-specific settings
    st.set_page_config(layout="wide")
    os.environ['AE_SAMPLE'] = '1'
```

## 📞 Support

### Documentation
- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Cloud Deployment**: [docs.streamlit.io/streamlit-cloud](https://docs.streamlit.io/streamlit-cloud)

### Community
- **Forum**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues**: Report deployment-specific issues

---

**Ready to Deploy?** Follow the steps above to get your AE Trend Analyzer live on Streamlit Cloud! 🎉
