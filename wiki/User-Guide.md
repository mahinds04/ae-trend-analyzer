# User Guide

This guide explains how to use the AE Trend Analyzer dashboard to analyze adverse event trends and extract insights from pharmaceutical safety data.

## 🎯 Dashboard Overview

The AE Trend Analyzer provides an interactive Streamlit dashboard for exploring adverse event patterns, drug safety profiles, and temporal trends in pharmaceutical data.

### 🚀 Accessing the Dashboard

**Local Installation:**
```bash
streamlit run src/app/streamlit_mvp.py
```

**Sample Mode:**
```bash
streamlit run src/app/streamlit_mvp.py -- --sample
```

**Live Demo:**
[AE Trend Analyzer on Streamlit Cloud](https://ae-trend-analyzer.streamlit.app)

## 📊 Dashboard Features

### 1. **Header & Navigation**
- **Project Title**: AE Trend Analyzer with gradient styling
- **Status Indicators**: Data mode (Full/Sample), record counts
- **Contact Information**: Developer details and GitHub links

### 2. **Key Performance Indicators (KPIs)**
The dashboard displays four main KPI cards:

| KPI | Description | Insight |
|-----|-------------|---------|
| **Total Events** | Number of adverse event reports | Overall data volume |
| **Unique Drugs** | Number of distinct medications | Drug diversity |
| **Unique Reactions** | Number of distinct adverse events | AE diversity |
| **Date Range** | Time span of data | Temporal coverage |

### 3. **Interactive Filters**

#### **Drug Filter**
- **Location**: Left sidebar
- **Function**: Filter data by specific medications
- **Features**:
  - Searchable dropdown with all available drugs
  - Multi-select capability
  - Real-time data filtering
  - Shows drug count in current dataset

#### **Reaction Filter**
- **Location**: Left sidebar
- **Function**: Filter data by adverse event types
- **Features**:
  - Searchable dropdown with all reactions
  - Multi-select capability
  - MedDRA term compatibility
  - Dynamic reaction suggestions

#### **Date Range Filter**
- **Location**: Left sidebar
- **Function**: Filter data by time period
- **Features**:
  - Interactive date picker
  - Start and end date selection
  - Automatic data range validation
  - Monthly aggregation alignment

### 4. **Visualization Panels**

#### **Monthly Trends Chart**
- **Purpose**: Shows temporal patterns in adverse event reporting
- **Features**:
  - Interactive Plotly line chart
  - Hover tooltips with exact values
  - Zoom and pan capabilities
  - Responsive design
- **Insights**: Identify seasonal patterns, reporting spikes, or declining trends

#### **Top Drugs Analysis**
- **Purpose**: Ranks medications by adverse event frequency
- **Features**:
  - Horizontal bar chart
  - Top 15 drugs by default
  - Interactive drug selection
  - Color-coded bars
- **Insights**: Identify high-risk medications or reporting patterns

#### **Top Reactions Analysis**
- **Purpose**: Ranks adverse events by frequency
- **Features**:
  - Horizontal bar chart
  - Top 15 reactions by default
  - MedDRA term display
  - Severity indicators
- **Insights**: Common safety concerns across medications

## 🔍 Advanced Features

### 🚨 **Anomaly Detection**

The dashboard includes sophisticated anomaly detection capabilities:

#### **STL Decomposition**
- **Method**: Seasonal and Trend decomposition using Loess
- **Purpose**: Separates trend, seasonal, and residual components
- **Visualization**: Multi-panel time series plots
- **Insights**: Identify underlying trends vs. seasonal variations

#### **Rolling Z-Score Analysis**
- **Method**: Statistical anomaly detection using rolling statistics
- **Threshold**: Configurable Z-score thresholds (default: ±2)
- **Visualization**: Overlay on trend charts with anomaly markers
- **Insights**: Detect statistical outliers in reporting patterns

#### **Prophet Forecasting** *(Full mode only)*
- **Method**: Facebook Prophet time series forecasting
- **Features**: Trend forecasting with confidence intervals
- **Visualization**: Extended timeline with predictions
- **Insights**: Predict future adverse event patterns

### 💡 **Smart Insights Panel**

The insights panel provides automated analysis:

#### **Spike Detection**
- Identifies significant increases in adverse event reporting
- Ranks spikes by magnitude and statistical significance
- Provides contextual information about timing

#### **Trend Analysis**
- Calculates month-over-month growth rates
- Identifies accelerating or decelerating trends
- Highlights notable pattern changes

#### **Data Quality Metrics**
- Completeness indicators
- Data freshness information
- Coverage statistics

## 🎨 User Interface Elements

### **Professional Styling**
- **Gradient Headers**: Blue-to-purple gradient styling
- **KPI Cards**: Clean metric displays with icons
- **Responsive Layout**: Adapts to different screen sizes
- **Color Scheme**: Professional blue/purple theme

### **Interactive Elements**
- **Hover Tooltips**: Detailed information on charts
- **Clickable Legends**: Toggle data series
- **Zooming**: Chart zoom and pan functionality
- **Real-time Updates**: Filters update visualizations instantly

## 📈 Workflow Examples

### **Example 1: Drug Safety Analysis**

1. **Select Drug**: Use drug filter to select "ASPIRIN"
2. **Review KPIs**: Note total events and date range
3. **Analyze Trends**: Examine monthly trend chart for patterns
4. **Check Reactions**: Review top reactions for selected drug
5. **Detect Anomalies**: Use anomaly detection to find reporting spikes
6. **Generate Insights**: Review automated insights panel

### **Example 2: Reaction Pattern Analysis**

1. **Select Reaction**: Filter by "HEADACHE" or "NAUSEA"
2. **Time Range**: Set specific date range of interest
3. **Drug Association**: Identify drugs most associated with reaction
4. **Temporal Patterns**: Look for seasonal or trending patterns
5. **Comparative Analysis**: Compare multiple reactions side-by-side

### **Example 3: Temporal Trend Investigation**

1. **Full Date Range**: Set broad date range for comprehensive view
2. **No Filters**: Remove drug/reaction filters for overall trends
3. **Anomaly Detection**: Enable all anomaly detection methods
4. **Spike Investigation**: Identify and investigate significant spikes
5. **Forecast Analysis**: Use Prophet for future trend prediction

## 🎯 Best Practices

### **Data Exploration**
- **Start Broad**: Begin with full dataset, then apply filters
- **Use Sample Mode**: For quick exploration and testing
- **Compare Periods**: Use date filters to compare time periods
- **Cross-Reference**: Combine drug and reaction filters for specific analysis

### **Anomaly Investigation**
- **Multiple Methods**: Use different anomaly detection methods
- **Context Matters**: Consider external factors (seasons, regulations)
- **Statistical Significance**: Focus on statistically significant anomalies
- **Validate Findings**: Cross-check with multiple data sources

### **Performance Optimization**
- **Filter Early**: Apply filters before complex analysis
- **Sample Mode**: Use for development and quick checks
- **Cache Results**: Leverage Streamlit caching for faster loads
- **Reasonable Ranges**: Avoid overly broad date ranges for large datasets

## 🔧 Customization Options

### **Environment Variables**
```bash
# Force sample mode
export AE_SAMPLE=1

# Disable Prophet forecasting
export AE_DISABLE_PROPHET=1

# Set custom data path
export AE_DATA_PATH=/custom/path/to/data
```

### **URL Parameters**
- `?sample=true` - Enable sample mode
- `?drug=ASPIRIN` - Pre-select drug filter
- `?reaction=HEADACHE` - Pre-select reaction filter

## 🆘 Troubleshooting

### **Common Issues**

#### **Slow Loading**
- **Cause**: Large dataset or complex filters
- **Solution**: Use sample mode or apply filters early

#### **Empty Charts**
- **Cause**: Overly restrictive filters
- **Solution**: Broaden filters or check data availability

#### **Missing Data**
- **Cause**: Incomplete data processing
- **Solution**: Re-run ETL pipeline or check data structure

### **Getting Help**
- **Error Messages**: Check browser console for detailed errors
- **Log Files**: Review application logs for processing issues
- **GitHub Issues**: Report bugs with reproduction steps
- **Community**: Use GitHub Discussions for questions

---

**Next**: Learn about data requirements in the [Data Guide](Data-Guide).