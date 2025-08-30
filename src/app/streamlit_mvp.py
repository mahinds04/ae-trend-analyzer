"""
Streamlit MVP Dashboard for Adverse Event Trend Analyzer.

This dashboard provides interactive visualization of adverse event trends
with filtering capabilities for drugs, reactions, and time periods.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import numpy as np


# Page configuration
st.set_page_config(
    page_title="AE Trend Analyzer MVP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data
def load_data():
    """Load all required data files with caching."""
    data_dir = Path("data/processed")
    
    try:
        # Load monthly aggregations
        monthly_counts = pd.read_csv(data_dir / "monthly_counts.csv")
        monthly_reaction = pd.read_csv(data_dir / "monthly_by_reaction.csv")
        monthly_drug = pd.read_csv(data_dir / "monthly_by_drug.csv")
        
        # Convert ym to datetime for better plotting
        for df in [monthly_counts, monthly_reaction, monthly_drug]:
            if 'ym' in df.columns:
                df['date'] = pd.to_datetime(df['ym'], format='%Y-%m', errors='coerce')
        
        return monthly_counts, monthly_reaction, monthly_drug
    
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}")
        st.error("Please run the ETL pipeline first to generate processed data files.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()


def calculate_kpis(monthly_counts, monthly_reaction, monthly_drug):
    """Calculate KPI metrics for the dashboard."""
    try:
        # Total AE reports
        total_reports = monthly_counts['count'].sum() if 'count' in monthly_counts.columns else 0
        
        # Unique drugs and reactions
        unique_drugs = len(monthly_drug['drug'].unique()) if 'drug' in monthly_drug.columns else 0
        unique_reactions = len(monthly_reaction['reaction_pt'].unique()) if 'reaction_pt' in monthly_reaction.columns else 0
        
        # Date coverage
        all_dates = []
        for df in [monthly_counts, monthly_reaction, monthly_drug]:
            if 'date' in df.columns:
                valid_dates = df['date'].dropna()
                if len(valid_dates) > 0:
                    all_dates.extend(valid_dates)
        
        if all_dates:
            min_date = min(all_dates)
            max_date = max(all_dates)
            date_range = f"{min_date.strftime('%Y-%m')} to {max_date.strftime('%Y-%m')}"
        else:
            date_range = "No valid dates"
        
        return total_reports, unique_drugs, unique_reactions, date_range
    
    except Exception as e:
        st.error(f"Error calculating KPIs: {e}")
        return 0, 0, 0, "Error"


def create_overall_trend_chart(monthly_counts):
    """Create overall monthly trend chart."""
    if 'date' not in monthly_counts.columns or 'count' not in monthly_counts.columns:
        st.warning("Missing required columns for overall trend chart")
        return None
    
    # Remove rows with null dates
    df_clean = monthly_counts.dropna(subset=['date'])
    
    if len(df_clean) == 0:
        st.warning("No valid data for overall trend chart")
        return None
    
    fig = px.line(
        df_clean,
        x='date',
        y='count',
        title='Overall Monthly Adverse Event Reports',
        labels={'count': 'Number of Reports', 'date': 'Month'},
        line_shape='spline'
    )
    
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Reports",
        hovermode='x unified'
    )
    
    return fig


def create_filtered_trend_chart(data, filter_type, filter_value, value_col='count'):
    """Create filtered trend chart for specific drug or reaction."""
    if filter_value == "<ALL>":
        # Aggregate all values by date
        if 'date' not in data.columns or value_col not in data.columns:
            st.warning(f"Missing required columns for {filter_type} trend chart")
            return None
        
        df_agg = data.groupby('date')[value_col].sum().reset_index()
        title = f"All {filter_type.title()}s - Monthly Trend"
    else:
        # Filter for specific value
        filter_col = 'drug' if filter_type == 'drug' else 'reaction_pt'
        if filter_col not in data.columns:
            st.warning(f"Missing {filter_col} column")
            return None
        
        df_filtered = data[data[filter_col] == filter_value]
        if len(df_filtered) == 0:
            st.warning(f"No data found for {filter_type}: {filter_value}")
            return None
        
        df_agg = df_filtered.groupby('date')[value_col].sum().reset_index()
        title = f"{filter_value} - Monthly Trend"
    
    # Remove rows with null dates
    df_agg = df_agg.dropna(subset=['date'])
    
    if len(df_agg) == 0:
        st.warning("No valid data for filtered trend chart")
        return None
    
    fig = px.line(
        df_agg,
        x='date',
        y=value_col,
        title=title,
        labels={value_col: 'Number of Reports', 'date': 'Month'},
        line_shape='spline'
    )
    
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Reports",
        hovermode='x unified'
    )
    
    return fig


def main():
    """Main dashboard application."""
    
    # Enhanced Header with custom styling
    st.markdown(
        """
        <style>
        .main-header {
            background: linear-gradient(90deg, #1f77b4 0%, #2ca02c 50%, #ff7f0e 100%);
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
        }
        .main-title {
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .main-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        .metric-container {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #1f77b4;
            margin: 0.5rem 0;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            padding: 0px 24px;
            background-color: #f0f2f6;
            border-radius: 10px 10px 0px 0px;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1f77b4;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <div class="main-header">
            <div class="main-title">📊 Adverse Event Trend Analyzer</div>
            <div class="main-subtitle">Interactive dashboard for analyzing FDA FAERS adverse event trends</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Add a loading animation while data loads
    with st.spinner("🔄 Loading pharmaceutical safety data..."):
        monthly_counts, monthly_reaction, monthly_drug = load_data()
    
    # Calculate KPIs
    total_reports, unique_drugs, unique_reactions, date_range = calculate_kpis(
        monthly_counts, monthly_reaction, monthly_drug
    )
    
    # Enhanced KPI Metrics Row
    st.markdown("## 📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            f"""
            <div class="metric-container">
                <h3 style="color: #1f77b4; margin: 0;">📊 Total AE Reports</h3>
                <h2 style="color: #333; margin: 0.5rem 0;">{total_reports:,}</h2>
                <p style="color: #666; margin: 0; font-size: 0.9em;">Adverse event records</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="metric-container">
                <h3 style="color: #2ca02c; margin: 0;">💊 Unique Drugs</h3>
                <h2 style="color: #333; margin: 0.5rem 0;">{unique_drugs:,}</h2>
                <p style="color: #666; margin: 0; font-size: 0.9em;">Different medications</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div class="metric-container">
                <h3 style="color: #ff7f0e; margin: 0;">⚠️ Unique Reactions</h3>
                <h2 style="color: #333; margin: 0.5rem 0;">{unique_reactions:,}</h2>
                <p style="color: #666; margin: 0; font-size: 0.9em;">Adverse event types</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            f"""
            <div class="metric-container">
                <h3 style="color: #d62728; margin: 0;">📅 Date Coverage</h3>
                <h2 style="color: #333; margin: 0.5rem 0; font-size: 1.5rem;">{date_range}</h2>
                <p style="color: #666; margin: 0; font-size: 0.9em;">Data timespan</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Enhanced Sidebar Filters
    st.sidebar.markdown(
        """
        <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h2 style="color: #1f77b4; margin: 0;">🔍 Filter Options</h2>
            <p style="margin: 0.5rem 0; color: #666;">Customize your analysis by selecting specific drugs, reactions, or time periods</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Add filter tips
    with st.sidebar.expander("� Filter Tips"):
        st.markdown("""
        - **<ALL>** shows aggregated data across all categories
        - **Drug Filter**: Focus on specific medications
        - **Reaction Filter**: Analyze particular adverse events
        - **Year Filter**: Compare trends across time periods
        - Use multiple filters for detailed insights
        """)
    
    st.sidebar.markdown("### 💊 Drug Selection")
    # Drug filter
    drug_options = ["<ALL>"] + sorted(monthly_drug['drug'].unique().tolist()) if 'drug' in monthly_drug.columns else ["<ALL>"]
    selected_drug = st.sidebar.selectbox("Choose a drug:", drug_options)
    
    st.sidebar.markdown("### ⚠️ Reaction Selection")
    # Reaction filter
    reaction_options = ["<ALL>"] + sorted(monthly_reaction['reaction_pt'].unique().tolist()) if 'reaction_pt' in monthly_reaction.columns else ["<ALL>"]
    selected_reaction = st.sidebar.selectbox("Choose a reaction:", reaction_options)
    
    st.sidebar.markdown("### 📅 Time Period")
    # Year filter
    all_years = set()
    for df in [monthly_counts, monthly_reaction, monthly_drug]:
        if 'date' in df.columns:
            years = df['date'].dt.year.dropna().unique()
            all_years.update(years)
    
    year_options = ["<ALL>"] + sorted([int(year) for year in all_years if not pd.isna(year)])
    selected_year = st.sidebar.selectbox("Choose a year:", year_options)
    
    # Add data summary in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Stats")
    if 'drug' in monthly_drug.columns and 'reaction_pt' in monthly_reaction.columns:
        st.sidebar.info(f"""
        **Available Data:**
        - 🏥 {len(monthly_drug['drug'].unique())} unique drugs
        - ⚠️ {len(monthly_reaction['reaction_pt'].unique())} unique reactions
        - 📅 {len(monthly_counts)} monthly periods
        """)
    
    # Add download section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Export Data")
    if st.sidebar.button("📊 Download Summary CSV"):
        # Create a summary for download
        summary_data = {
            'Metric': ['Total Reports', 'Unique Drugs', 'Unique Reactions', 'Date Range'],
            'Value': [total_reports, unique_drugs, unique_reactions, date_range]
        }
        summary_df = pd.DataFrame(summary_data)
        csv = summary_df.to_csv(index=False)
        st.sidebar.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"ae_summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Apply year filter to all datasets
    if selected_year != "<ALL>":
        monthly_counts = monthly_counts[monthly_counts['date'].dt.year == selected_year] if 'date' in monthly_counts.columns else monthly_counts
        monthly_reaction = monthly_reaction[monthly_reaction['date'].dt.year == selected_year] if 'date' in monthly_reaction.columns else monthly_reaction
        monthly_drug = monthly_drug[monthly_drug['date'].dt.year == selected_year] if 'date' in monthly_drug.columns else monthly_drug
    
    # Enhanced Main Content Area
    st.markdown("## 📊 Trend Analysis & Insights")
    
    # Add filter status indicator
    if selected_drug != "<ALL>" or selected_reaction != "<ALL>" or selected_year != "<ALL>":
        filter_status = []
        if selected_drug != "<ALL>":
            filter_status.append(f"Drug: **{selected_drug}**")
        if selected_reaction != "<ALL>":
            filter_status.append(f"Reaction: **{selected_reaction}**")
        if selected_year != "<ALL>":
            filter_status.append(f"Year: **{selected_year}**")
        
        st.info(f"🎯 **Active Filters:** {' | '.join(filter_status)}")
    
    # Create enhanced tabs with icons
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌍 Overall Trends", 
        "💊 Drug Analysis", 
        "⚠️ Reaction Analysis", 
        "📋 Data Tables"
    ])
    
    with tab1:
        st.markdown("### 🌍 Overall Monthly Adverse Event Reports")
        st.markdown("*Comprehensive view of all adverse event reports over time*")
        
        fig_overall = create_overall_trend_chart(monthly_counts)
        if fig_overall:
            st.plotly_chart(fig_overall, use_container_width=True)
            
            # Add insights
            if not monthly_counts.empty and 'count' in monthly_counts.columns:
                total_reports_filtered = monthly_counts['count'].sum()
                avg_monthly = monthly_counts['count'].mean()
                max_month = monthly_counts.loc[monthly_counts['count'].idxmax(), 'date'].strftime('%Y-%m') if 'date' in monthly_counts.columns else "N/A"
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total Reports", f"{total_reports_filtered:,}")
                with col2:
                    st.metric("📈 Monthly Average", f"{avg_monthly:,.0f}")
                with col3:
                    st.metric("🔥 Peak Month", max_month)
        else:
            st.error("❌ Unable to create overall trend chart")
    
    with tab2:
        st.markdown("### 💊 Drug-Specific Trends")
        if selected_drug != "<ALL>":
            st.markdown(f"*Analyzing adverse events for: **{selected_drug}***")
        else:
            st.markdown("*Comprehensive drug analysis across all medications*")
        
        fig_drug = create_filtered_trend_chart(monthly_drug, "drug", selected_drug)
        if fig_drug:
            st.plotly_chart(fig_drug, use_container_width=True)
        else:
            st.error("❌ Unable to create drug trend chart")
        
        # Enhanced top drugs table
        if 'drug' in monthly_drug.columns and 'count' in monthly_drug.columns:
            st.markdown("### 🏆 Top 10 Drugs by Total Reports")
            top_drugs = monthly_drug.groupby('drug')['count'].sum().sort_values(ascending=False).head(10)
            top_drugs_df = pd.DataFrame({
                'Rank': range(1, len(top_drugs) + 1),
                'Drug Name': top_drugs.index,
                'Total Reports': top_drugs.values,
                'Percentage': [(count/top_drugs.sum()*100) for count in top_drugs.values]
            })
            
            # Color-code the table
            styled_df = top_drugs_df.style.format({
                'Total Reports': '{:,}',
                'Percentage': '{:.1f}%'
            }).background_gradient(subset=['Total Reports'], cmap='Blues')
            
            st.dataframe(styled_df, use_container_width=True)
    
    with tab3:
        st.markdown("### ⚠️ Reaction-Specific Trends")
        if selected_reaction != "<ALL>":
            st.markdown(f"*Analyzing reports for: **{selected_reaction}***")
        else:
            st.markdown("*Comprehensive reaction analysis across all adverse events*")
        
        fig_reaction = create_filtered_trend_chart(monthly_reaction, "reaction", selected_reaction)
        if fig_reaction:
            st.plotly_chart(fig_reaction, use_container_width=True)
        else:
            st.error("❌ Unable to create reaction trend chart")
        
        # Enhanced top reactions table
        if 'reaction_pt' in monthly_reaction.columns and 'count' in monthly_reaction.columns:
            st.markdown("### 🏆 Top 10 Reactions by Total Reports")
            top_reactions = monthly_reaction.groupby('reaction_pt')['count'].sum().sort_values(ascending=False).head(10)
            top_reactions_df = pd.DataFrame({
                'Rank': range(1, len(top_reactions) + 1),
                'Reaction': top_reactions.index,
                'Total Reports': top_reactions.values,
                'Percentage': [(count/top_reactions.sum()*100) for count in top_reactions.values]
            })
            
            # Color-code the table
            styled_df = top_reactions_df.style.format({
                'Total Reports': '{:,}',
                'Percentage': '{:.1f}%'
            }).background_gradient(subset=['Total Reports'], cmap='Reds')
            
            st.dataframe(styled_df, use_container_width=True)
    
    with tab4:
        st.markdown("### 📋 Raw Data Tables")
        st.markdown("*Explore the underlying data powering the visualizations*")
        
        # Sub-tabs for different data types
        data_tab1, data_tab2, data_tab3 = st.tabs(["Monthly Counts", "Drug Data", "Reaction Data"])
        
        with data_tab1:
            st.markdown("#### 📅 Monthly Overall Counts")
            if not monthly_counts.empty:
                st.dataframe(monthly_counts.head(20), use_container_width=True)
                st.markdown(f"*Showing first 20 of {len(monthly_counts)} total records*")
            else:
                st.warning("No monthly counts data available")
        
        with data_tab2:
            st.markdown("#### 💊 Monthly Drug Data")
            if not monthly_drug.empty:
                st.dataframe(monthly_drug.head(20), use_container_width=True)
                st.markdown(f"*Showing first 20 of {len(monthly_drug)} total records*")
            else:
                st.warning("No drug data available")
        
        with data_tab3:
            st.markdown("#### ⚠️ Monthly Reaction Data")
            if not monthly_reaction.empty:
                st.dataframe(monthly_reaction.head(20), use_container_width=True)
                st.markdown(f"*Showing first 20 of {len(monthly_reaction)} total records*")
            else:
                st.warning("No reaction data available")
    
    # Footer with enhanced styling
    st.markdown("---")
    
    # Data Sources Section
    st.markdown("### 📚 Data Sources")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 4px solid #1f77b4;">
            <h4 style="color: #1f77b4; margin-top: 0;">🏛️ FDA FAERS</h4>
            <p><a href="https://fis.fda.gov/extensions/FPD-QDE-FAERS/FPD-QDE-FAERS.html" target="_blank" style="text-decoration: none;">FDA Adverse Event Reporting System (FAERS) Quarterly Data</a></p>
            <small>Official FDA adverse event reports</small>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            """
            <div style="background-color: #f0f8f0; padding: 15px; border-radius: 10px; border-left: 4px solid #2ca02c;">
            <h4 style="color: #2ca02c; margin-top: 0;">💊 WebMD Reviews</h4>
            <p><a href="https://www.kaggle.com/datasets/rohanharode07/webmd-drug-reviews-dataset" target="_blank" style="text-decoration: none;">WebMD Drug Reviews Dataset</a></p>
            <small>Patient-generated drug reviews</small>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            """
            <div style="background-color: #fff8f0; padding: 15px; border-radius: 10px; border-left: 4px solid #ff7f0e;">
            <h4 style="color: #ff7f0e; margin-top: 0;">🎓 UCI ML Dataset</h4>
            <p><a href="https://www.kaggle.com/datasets/jessicali9530/kuc-hackathon-winter-2018" target="_blank" style="text-decoration: none;">UCI ML Drug Review dataset</a></p>
            <small>Drugs.com review dataset</small>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Contact and Attribution Section
    st.markdown("### 👨‍💻 About & Contact")
    
    contact_col1, contact_col2 = st.columns([2, 1])
    
    with contact_col1:
        st.markdown(
            """
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #dee2e6;">
            <h4 style="color: #495057; margin-top: 0;">📧 Mahin Das</h4>
            <p style="margin: 5px 0;"><strong>Email:</strong> 
            <a href="mailto:mahinds04@gmail.com">mahinds04@gmail.com</a> | 
            <a href="mailto:dasmahin07@gmail.com">dasmahin07@gmail.com</a></p>
            <p style="margin: 5px 0;"><strong>GitHub:</strong> 
            <a href="https://github.com/mahinds04" target="_blank">https://github.com/mahinds04</a></p>
            <p style="margin: 5px 0; color: #6c757d;"><em>Adverse Event Trend Analyzer - Transforming drug safety data into actionable insights</em></p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with contact_col2:
        st.markdown(
            """
            <div style="text-align: center; padding: 20px;">
            <h4>⚡ Tech Stack</h4>
            <p>🐍 Python | 📊 Streamlit</p>
            <p>📈 Plotly | 🗃️ Pandas</p>
            <p>🏥 FAERS | 🤖 NLP</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: #6c757d; font-size: 0.9em;">
        <strong>Last Updated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')} | 
        <strong>Powered by:</strong> Streamlit & Plotly | 
        <strong>Version:</strong> 1.0
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
