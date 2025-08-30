"""
Streamlit Cloud Entry Point for AE Trend Analyzer
Simple, direct implementation for cloud deployment.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import numpy as np
import os
import sys

# Force sample mode for cloud deployment
os.environ['AE_SAMPLE'] = '1'

# Page configuration
st.set_page_config(
    page_title="AE Trend Analyzer MVP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_sample_data():
    """Load sample data for cloud demo."""
    try:
        # Load sample data directly
        base_path = Path(__file__).parent / "data" / "processed" / "_samples"
        
        monthly_counts = pd.read_csv(base_path / "monthly_counts.sample.csv")
        monthly_reaction = pd.read_csv(base_path / "monthly_by_reaction.sample.csv")
        monthly_drug = pd.read_csv(base_path / "monthly_by_drug.sample.csv")
        
        # Convert ym to datetime for better plotting
        for df in [monthly_counts, monthly_reaction, monthly_drug]:
            if 'ym' in df.columns:
                df['date'] = pd.to_datetime(df['ym'], format='%Y-%m', errors='coerce')
        
        return monthly_counts, monthly_reaction, monthly_drug
    
    except Exception as e:
        st.error(f"Error loading sample data: {e}")
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
    """Create overall trend chart."""
    try:
        if monthly_counts.empty or 'date' not in monthly_counts.columns:
            st.warning("No data available for overall trend chart")
            return None
            
        fig = px.line(
            monthly_counts, 
            x='date', 
            y='count',
            title='📈 Overall Adverse Event Trends Over Time',
            labels={'count': 'Number of AE Reports', 'date': 'Date'}
        )
        
        fig.update_layout(
            height=400,
            hovermode='x unified'
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating overall trend chart: {e}")
        return None

def create_top_drugs_chart(monthly_drug):
    """Create top drugs chart."""
    try:
        if monthly_drug.empty or 'drug' not in monthly_drug.columns:
            return None
            
        top_drugs = monthly_drug.groupby('drug')['count'].sum().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=top_drugs.values,
            y=top_drugs.index,
            orientation='h',
            title='💊 Top 10 Drugs by Total AE Reports',
            labels={'x': 'Total AE Reports', 'y': 'Drug Name'}
        )
        
        fig.update_layout(height=400)
        return fig
    except Exception as e:
        st.error(f"Error creating top drugs chart: {e}")
        return None

def create_top_reactions_chart(monthly_reaction):
    """Create top reactions chart."""
    try:
        if monthly_reaction.empty or 'reaction_pt' not in monthly_reaction.columns:
            return None
            
        top_reactions = monthly_reaction.groupby('reaction_pt')['count'].sum().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=top_reactions.values,
            y=top_reactions.index,
            orientation='h',
            title='⚠️ Top 10 Adverse Reactions by Total Reports',
            labels={'x': 'Total AE Reports', 'y': 'Adverse Reaction'}
        )
        
        fig.update_layout(height=400)
        return fig
    except Exception as e:
        st.error(f"Error creating top reactions chart: {e}")
        return None

# Main App
def main():
    """Main application logic."""
    
    # Header with demo notice
    st.markdown("""
    <div style="background: linear-gradient(90deg, #FF6B6B, #4ECDC4); padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; text-align: center; margin: 0;">
            📊 AE Trend Analyzer - Live Demo
        </h1>
        <p style="color: white; text-align: center; margin: 0.5rem 0 0 0;">
            🚀 Interactive Pharmaceutical Adverse Event Analysis Platform
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo mode notice
    st.info("🚀 **Demo Mode**: Using sample data (~50 rows) for instant preview. Full datasets available for local installation.")
    
    # Load data
    monthly_counts, monthly_reaction, monthly_drug = load_sample_data()
    
    # Calculate KPIs
    total_reports, unique_drugs, unique_reactions, date_range = calculate_kpis(monthly_counts, monthly_reaction, monthly_drug)
    
    # Display KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total AE Reports", f"{total_reports:,}")
    
    with col2:
        st.metric("💊 Unique Drugs", f"{unique_drugs:,}")
    
    with col3:
        st.metric("⚠️ Unique Reactions", f"{unique_reactions:,}")
    
    with col4:
        st.metric("📅 Date Range", date_range)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Drug filter
    if not monthly_drug.empty and 'drug' in monthly_drug.columns:
        all_drugs = ['All'] + sorted(monthly_drug['drug'].unique().tolist())
        selected_drug = st.sidebar.selectbox("Select Drug", all_drugs)
    else:
        selected_drug = 'All'
    
    # Reaction filter
    if not monthly_reaction.empty and 'reaction_pt' in monthly_reaction.columns:
        all_reactions = ['All'] + sorted(monthly_reaction['reaction_pt'].unique().tolist())
        selected_reaction = st.sidebar.selectbox("Select Adverse Reaction", all_reactions)
    else:
        selected_reaction = 'All'
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📈 Trends", "💊 Top Drugs", "⚠️ Top Reactions"])
    
    with tab1:
        st.subheader("📈 Adverse Event Trends")
        
        # Overall trend
        fig_overall = create_overall_trend_chart(monthly_counts)
        if fig_overall:
            st.plotly_chart(fig_overall, use_container_width=True)
        
        # Filtered trends
        if selected_drug != 'All':
            drug_data = monthly_drug[monthly_drug['drug'] == selected_drug]
            if not drug_data.empty:
                fig_drug = px.line(
                    drug_data, x='date', y='count',
                    title=f'📊 Trend for {selected_drug}',
                    labels={'count': 'Number of AE Reports', 'date': 'Date'}
                )
                st.plotly_chart(fig_drug, use_container_width=True)
        
        if selected_reaction != 'All':
            reaction_data = monthly_reaction[monthly_reaction['reaction_pt'] == selected_reaction]
            if not reaction_data.empty:
                fig_reaction = px.line(
                    reaction_data, x='date', y='count',
                    title=f'📊 Trend for {selected_reaction}',
                    labels={'count': 'Number of AE Reports', 'date': 'Date'}
                )
                st.plotly_chart(fig_reaction, use_container_width=True)
    
    with tab2:
        st.subheader("💊 Top Drugs Analysis")
        fig_drugs = create_top_drugs_chart(monthly_drug)
        if fig_drugs:
            st.plotly_chart(fig_drugs, use_container_width=True)
    
    with tab3:
        st.subheader("⚠️ Top Adverse Reactions Analysis")
        fig_reactions = create_top_reactions_chart(monthly_reaction)
        if fig_reactions:
            st.plotly_chart(fig_reactions, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **👨‍💻 AE Trend Analyzer** | Built with Streamlit | 
    [GitHub Repository](https://github.com/mahinds04/ae-trend-analyzer) | 
    [Full Documentation](https://github.com/mahinds04/ae-trend-analyzer/blob/master/README.md)
    """)

if __name__ == "__main__":
    main()
