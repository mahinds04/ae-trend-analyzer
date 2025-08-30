"""
Aggregation Analysis Module

This module provides functionality to create monthly aggregations of adverse events
and generate visualization plots for trend analysis.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, date
import warnings

# Import configuration - handle both relative and absolute imports
try:
    from ..config import ANALYSIS_CONFIG, LOGGING_CONFIG
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import ANALYSIS_CONFIG, LOGGING_CONFIG

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format']
)
logger = logging.getLogger(__name__)

# Suppress matplotlib warnings
warnings.filterwarnings("ignore", category=UserWarning)

def monthly_overall(df: pd.DataFrame, date_col: str = 'event_date') -> pd.DataFrame:
    """
    Create monthly overall adverse event counts.
    
    Args:
        df: Events DataFrame with date column
        date_col: Name of the date column
        
    Returns:
        DataFrame with monthly counts (ym, count)
    """
    logger.info("Creating monthly overall aggregation")
    
    if df.empty:
        logger.warning("Empty DataFrame provided")
        return pd.DataFrame(columns=['ym', 'count'])
    
    # Ensure date column exists and is datetime
    if date_col not in df.columns:
        logger.error(f"Date column '{date_col}' not found in DataFrame")
        return pd.DataFrame(columns=['ym', 'count'])
    
    # Convert to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Remove rows with invalid dates
    initial_count = len(df)
    df_clean = df.dropna(subset=[date_col])
    final_count = len(df_clean)
    
    if initial_count != final_count:
        logger.info(f"Removed {initial_count - final_count} rows with invalid dates")
    
    if df_clean.empty:
        logger.warning("No valid dates found")
        return pd.DataFrame(columns=['ym', 'count'])
    
    # Create year-month column (first day of month)
    df_clean = df_clean.copy()
    df_clean['ym'] = df_clean[date_col].dt.to_period('M').dt.start_time
    
    # Count events per month
    monthly_counts = df_clean.groupby('ym').size().reset_index(name='count')
    
    # Sort by date
    monthly_counts = monthly_counts.sort_values('ym')
    
    logger.info(f"Created monthly aggregation: {len(monthly_counts)} months, "
                f"{monthly_counts['count'].sum()} total events")
    
    return monthly_counts

def monthly_by_reaction(df: pd.DataFrame, 
                       date_col: str = 'event_date',
                       reaction_col: str = 'reaction_pt') -> pd.DataFrame:
    """
    Create monthly adverse event counts by reaction type.
    
    Args:
        df: Events DataFrame with date and reaction columns
        date_col: Name of the date column
        reaction_col: Name of the reaction column
        
    Returns:
        DataFrame with monthly counts by reaction (ym, reaction_pt, count)
    """
    logger.info("Creating monthly by reaction aggregation")
    
    if df.empty:
        logger.warning("Empty DataFrame provided")
        return pd.DataFrame(columns=['ym', 'reaction_pt', 'count'])
    
    # Check required columns
    required_cols = [date_col, reaction_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.error(f"Missing columns: {missing_cols}")
        return pd.DataFrame(columns=['ym', 'reaction_pt', 'count'])
    
    # Convert to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Remove rows with invalid dates or missing reactions
    df_clean = df.dropna(subset=[date_col, reaction_col])
    
    if df_clean.empty:
        logger.warning("No valid data found")
        return pd.DataFrame(columns=['ym', 'reaction_pt', 'count'])
    
    # Create year-month column
    df_clean = df_clean.copy()
    df_clean['ym'] = df_clean[date_col].dt.to_period('M').dt.start_time
    
    # Count events per month by reaction
    monthly_reaction_counts = (df_clean.groupby(['ym', reaction_col])
                              .size()
                              .reset_index(name='count'))
    
    # Rename reaction column for consistency
    monthly_reaction_counts = monthly_reaction_counts.rename(columns={reaction_col: 'reaction_pt'})
    
    # Sort by date and count
    monthly_reaction_counts = monthly_reaction_counts.sort_values(['ym', 'count'], ascending=[True, False])
    
    unique_reactions = monthly_reaction_counts['reaction_pt'].nunique()
    logger.info(f"Created monthly by reaction aggregation: {len(monthly_reaction_counts)} records, "
                f"{unique_reactions} unique reactions")
    
    return monthly_reaction_counts

def monthly_by_drug(df: pd.DataFrame,
                   date_col: str = 'event_date',
                   drug_col: str = 'drug') -> pd.DataFrame:
    """
    Create monthly adverse event counts by drug.
    
    Args:
        df: Events DataFrame with date and drug columns
        date_col: Name of the date column
        drug_col: Name of the drug column
        
    Returns:
        DataFrame with monthly counts by drug (ym, drug, count)
    """
    logger.info("Creating monthly by drug aggregation")
    
    if df.empty:
        logger.warning("Empty DataFrame provided")
        return pd.DataFrame(columns=['ym', 'drug', 'count'])
    
    # Check required columns
    required_cols = [date_col, drug_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.error(f"Missing columns: {missing_cols}")
        return pd.DataFrame(columns=['ym', 'drug', 'count'])
    
    # Convert to datetime if needed
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # Remove rows with invalid dates or missing drugs
    df_clean = df.dropna(subset=[date_col, drug_col])
    
    if df_clean.empty:
        logger.warning("No valid data found")
        return pd.DataFrame(columns=['ym', 'drug', 'count'])
    
    # Create year-month column
    df_clean = df_clean.copy()
    df_clean['ym'] = df_clean[date_col].dt.to_period('M').dt.start_time
    
    # Count events per month by drug
    monthly_drug_counts = (df_clean.groupby(['ym', drug_col])
                          .size()
                          .reset_index(name='count'))
    
    # Rename drug column for consistency
    monthly_drug_counts = monthly_drug_counts.rename(columns={drug_col: 'drug'})
    
    # Sort by date and count
    monthly_drug_counts = monthly_drug_counts.sort_values(['ym', 'count'], ascending=[True, False])
    
    unique_drugs = monthly_drug_counts['drug'].nunique()
    logger.info(f"Created monthly by drug aggregation: {len(monthly_drug_counts)} records, "
                f"{unique_drugs} unique drugs")
    
    return monthly_drug_counts

def get_top_items(df: pd.DataFrame, 
                 group_col: str, 
                 top_n: int = 10) -> List[str]:
    """
    Get top N items by total count across all months.
    
    Args:
        df: Aggregated DataFrame
        group_col: Column to group by
        top_n: Number of top items to return
        
    Returns:
        List of top item names
    """
    if df.empty or group_col not in df.columns:
        return []
    
    top_items = (df.groupby(group_col)['count']
                .sum()
                .sort_values(ascending=False)
                .head(top_n)
                .index
                .tolist())
    
    return top_items

def save_plots(monthly_overall_df: pd.DataFrame,
              monthly_reaction_df: pd.DataFrame,
              monthly_drug_df: pd.DataFrame,
              output_dir: Union[str, Path],
              top_n: int = 10) -> None:
    """
    Generate and save trend analysis plots.
    
    Args:
        monthly_overall_df: Overall monthly counts DataFrame
        monthly_reaction_df: Monthly by reaction DataFrame
        monthly_drug_df: Monthly by drug DataFrame
        output_dir: Directory to save plots
        top_n: Number of top items to plot
    """
    logger.info(f"Generating plots and saving to {output_dir}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Set up matplotlib style
    plt.style.use('default')
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10
    
    # 1. Overall trend plot
    if not monthly_overall_df.empty:
        logger.info("Creating overall trend plot")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot overall trend
        ax.plot(monthly_overall_df['ym'], monthly_overall_df['count'], 
                marker='o', linewidth=2, markersize=4, color='steelblue')
        
        ax.set_title('Adverse Events Trend Over Time', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Number of Events', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_minor_locator(mdates.MonthLocator([1, 7]))
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plot_path = output_path / 'overall_trend.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Saved overall trend plot to {plot_path}")
    
    # 2. Top reactions plot
    if not monthly_reaction_df.empty:
        logger.info("Creating top reactions plot")
        
        top_reactions = get_top_items(monthly_reaction_df, 'reaction_pt', top_n)
        
        if top_reactions:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Filter data for top reactions
            top_reaction_data = monthly_reaction_df[
                monthly_reaction_df['reaction_pt'].isin(top_reactions)
            ]
            
            # Create pivot table for easier plotting
            pivot_data = top_reaction_data.pivot(index='ym', 
                                               columns='reaction_pt', 
                                               values='count').fillna(0)
            
            # Plot lines for each reaction
            colors = plt.cm.tab10(np.linspace(0, 1, len(top_reactions)))
            
            for i, reaction in enumerate(top_reactions[:top_n]):
                if reaction in pivot_data.columns:
                    ax.plot(pivot_data.index, pivot_data[reaction], 
                           marker='o', label=reaction, linewidth=2, 
                           markersize=3, color=colors[i])
            
            ax.set_title(f'Top {top_n} Adverse Reactions Trend', fontsize=16, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Number of Events', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Format x-axis dates
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            plot_path = output_path / 'top_reactions_trend.png'
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Saved top reactions plot to {plot_path}")
    
    # 3. Top drugs plot
    if not monthly_drug_df.empty:
        logger.info("Creating top drugs plot")
        
        top_drugs = get_top_items(monthly_drug_df, 'drug', top_n)
        
        if top_drugs:
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Filter data for top drugs
            top_drug_data = monthly_drug_df[
                monthly_drug_df['drug'].isin(top_drugs)
            ]
            
            # Create pivot table for easier plotting
            pivot_data = top_drug_data.pivot(index='ym', 
                                           columns='drug', 
                                           values='count').fillna(0)
            
            # Plot lines for each drug
            colors = plt.cm.tab20(np.linspace(0, 1, len(top_drugs)))
            
            for i, drug in enumerate(top_drugs[:top_n]):
                if drug in pivot_data.columns:
                    ax.plot(pivot_data.index, pivot_data[drug], 
                           marker='o', label=drug, linewidth=2, 
                           markersize=3, color=colors[i])
            
            ax.set_title(f'Top {top_n} Drugs Adverse Events Trend', fontsize=16, fontweight='bold')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Number of Events', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Format x-axis dates
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            plot_path = output_path / 'top_drugs_trend.png'
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Saved top drugs plot to {plot_path}")
    
    # 4. Summary statistics plot
    logger.info("Creating summary statistics plot")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Overall events bar chart (yearly)
    if not monthly_overall_df.empty:
        yearly_data = (monthly_overall_df.copy()
                      .assign(year=monthly_overall_df['ym'].dt.year)
                      .groupby('year')['count'].sum())
        
        ax1.bar(yearly_data.index, yearly_data.values, color='steelblue', alpha=0.7)
        ax1.set_title('Total Events by Year', fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Number of Events')
        ax1.grid(True, alpha=0.3)
    
    # Top reactions bar chart
    if not monthly_reaction_df.empty:
        top_reactions_total = (monthly_reaction_df.groupby('reaction_pt')['count']
                              .sum()
                              .sort_values(ascending=False)
                              .head(10))
        
        ax2.barh(range(len(top_reactions_total)), top_reactions_total.values, 
                color='lightcoral', alpha=0.7)
        ax2.set_yticks(range(len(top_reactions_total)))
        ax2.set_yticklabels(top_reactions_total.index, fontsize=8)
        ax2.set_title('Top 10 Adverse Reactions (Total)', fontweight='bold')
        ax2.set_xlabel('Number of Events')
        ax2.grid(True, alpha=0.3)
    
    # Top drugs bar chart
    if not monthly_drug_df.empty:
        top_drugs_total = (monthly_drug_df.groupby('drug')['count']
                          .sum()
                          .sort_values(ascending=False)
                          .head(10))
        
        ax3.barh(range(len(top_drugs_total)), top_drugs_total.values, 
                color='lightgreen', alpha=0.7)
        ax3.set_yticks(range(len(top_drugs_total)))
        ax3.set_yticklabels([drug[:20] + '...' if len(drug) > 20 else drug 
                            for drug in top_drugs_total.index], fontsize=8)
        ax3.set_title('Top 10 Drugs (Total Events)', fontweight='bold')
        ax3.set_xlabel('Number of Events')
        ax3.grid(True, alpha=0.3)
    
    # Monthly distribution boxplot
    if not monthly_overall_df.empty:
        monthly_counts = monthly_overall_df['count'].values
        ax4.boxplot(monthly_counts, vert=True)
        ax4.set_title('Monthly Event Count Distribution', fontweight='bold')
        ax4.set_ylabel('Number of Events')
        ax4.set_xticklabels(['All Months'])
        ax4.grid(True, alpha=0.3)
        
        # Add statistics text
        stats_text = f"Mean: {monthly_counts.mean():.0f}\nMedian: {np.median(monthly_counts):.0f}\nStd: {monthly_counts.std():.0f}"
        ax4.text(0.02, 0.98, stats_text, transform=ax4.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle('Adverse Events Analysis Summary', fontsize=18, fontweight='bold')
    plt.tight_layout()
    
    plot_path = output_path / 'summary_statistics.png'
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Saved summary statistics plot to {plot_path}")

def create_all_aggregations(events_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Create all monthly aggregations from events DataFrame.
    
    Args:
        events_df: FAERS events DataFrame
        
    Returns:
        Tuple of (monthly_overall, monthly_reaction, monthly_drug) DataFrames
    """
    logger.info("Creating all monthly aggregations")
    
    # Overall monthly counts
    monthly_overall_df = monthly_overall(events_df)
    
    # Monthly by reaction
    monthly_reaction_df = monthly_by_reaction(events_df)
    
    # Monthly by drug
    monthly_drug_df = monthly_by_drug(events_df)
    
    return monthly_overall_df, monthly_reaction_df, monthly_drug_df

def plot_monthly(df: pd.DataFrame, title: str, out_path: Union[str, Path]) -> None:
    """
    Create a monthly trend plot using matplotlib.
    
    Args:
        df: DataFrame with 'ym' (year-month) and 'count' columns
        title: Plot title
        out_path: Output file path for saving the plot
    """
    logger.info(f"Creating monthly plot: {title}")
    
    if df.empty:
        logger.warning("Empty DataFrame provided for plotting")
        return
    
    if 'ym' not in df.columns or 'count' not in df.columns:
        logger.error("DataFrame must have 'ym' and 'count' columns")
        return
    
    # Create the plot
    fig, ax = plt.subplots(figsize=ANALYSIS_CONFIG['plot_figsize'])
    
    # Plot the trend line
    ax.plot(df['ym'], df['count'], marker='o', linewidth=2, markersize=4, 
            color='steelblue', alpha=0.8)
    
    # Customize the plot
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Number of Events', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Format x-axis dates
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator([1, 7]))
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Add some statistics as text
    if len(df) > 0:
        total_events = df['count'].sum()
        avg_monthly = df['count'].mean()
        max_monthly = df['count'].max()
        
        stats_text = f"Total: {total_events:,}\nAvg/month: {avg_monthly:.0f}\nMax/month: {max_monthly:,}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Adjust layout and save
    plt.tight_layout()
    
    # Ensure output directory exists
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    plt.savefig(out_path, dpi=ANALYSIS_CONFIG['plot_dpi'], bbox_inches='tight')
    plt.close()
    
    logger.info(f"Saved monthly plot to {out_path}")

def top_k(df: pd.DataFrame, column: str, k: int = 10) -> pd.Series:
    """
    Get top K items by total count across all records.
    
    Args:
        df: DataFrame with the specified column and 'count' column
        column: Column name to group by and find top items
        k: Number of top items to return (default: 10)
        
    Returns:
        Series with top K items and their total counts, sorted descending
    """
    logger.info(f"Finding top {k} items in column '{column}'")
    
    if df.empty:
        logger.warning("Empty DataFrame provided")
        return pd.Series(dtype=int)
    
    if column not in df.columns:
        logger.error(f"Column '{column}' not found in DataFrame")
        return pd.Series(dtype=int)
    
    if 'count' not in df.columns:
        logger.error("DataFrame must have 'count' column")
        return pd.Series(dtype=int)
    
    # Group by the specified column and sum counts
    top_items = (df.groupby(column)['count']
                .sum()
                .sort_values(ascending=False)
                .head(k))
    
    logger.info(f"Found top {len(top_items)} items in '{column}'")
    
    return top_items

def save_trend_plots(monthly_overall_df: pd.DataFrame,
                    monthly_reaction_df: pd.DataFrame,
                    monthly_drug_df: pd.DataFrame,
                    output_dir: Union[str, Path],
                    top_n: int = 10) -> None:
    """
    Generate and save the three requested trend plots: overall, top reactions bar, top drugs bar.
    
    Args:
        monthly_overall_df: Overall monthly counts DataFrame
        monthly_reaction_df: Monthly by reaction DataFrame
        monthly_drug_df: Monthly by drug DataFrame
        output_dir: Directory to save plots
        top_n: Number of top items to include in bar plots (default: 10)
    """
    logger.info(f"Generating trend plots and saving to {output_dir}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Overall trend plot (PNG)
    if not monthly_overall_df.empty:
        overall_path = output_path / 'overall_trend.png'
        plot_monthly(monthly_overall_df, 'Adverse Events Trend Over Time', overall_path)
    
    # 2. Top 10 reactions bar chart
    if not monthly_reaction_df.empty:
        logger.info("Creating top reactions bar chart")
        
        top_reactions = top_k(monthly_reaction_df, 'reaction_pt', top_n)
        
        if not top_reactions.empty:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create horizontal bar chart
            y_pos = np.arange(len(top_reactions))
            bars = ax.barh(y_pos, top_reactions.values, color='lightcoral', alpha=0.8)
            
            # Customize the plot
            ax.set_yticks(y_pos)
            ax.set_yticklabels(top_reactions.index, fontsize=10)
            ax.set_xlabel('Total Number of Events', fontsize=12)
            ax.set_title(f'Top {top_n} Adverse Reactions (Total Events)', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')
            
            # Add value labels on bars
            for i, (bar, value) in enumerate(zip(bars, top_reactions.values)):
                ax.text(value + max(top_reactions.values) * 0.01, i, f'{value:,}', 
                       va='center', fontsize=9)
            
            # Invert y-axis to show highest values at top
            ax.invert_yaxis()
            
            plt.tight_layout()
            
            reactions_path = output_path / 'top_reactions_bar.png'
            plt.savefig(reactions_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Saved top reactions bar chart to {reactions_path}")
    
    # 3. Top 10 drugs bar chart
    if not monthly_drug_df.empty:
        logger.info("Creating top drugs bar chart")
        
        top_drugs = top_k(monthly_drug_df, 'drug', top_n)
        
        if not top_drugs.empty:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create horizontal bar chart
            y_pos = np.arange(len(top_drugs))
            bars = ax.barh(y_pos, top_drugs.values, color='lightgreen', alpha=0.8)
            
            # Customize the plot
            ax.set_yticks(y_pos)
            # Truncate long drug names for better display
            drug_labels = [drug[:25] + '...' if len(drug) > 25 else drug 
                          for drug in top_drugs.index]
            ax.set_yticklabels(drug_labels, fontsize=10)
            ax.set_xlabel('Total Number of Events', fontsize=12)
            ax.set_title(f'Top {top_n} Drugs (Total Adverse Events)', fontsize=16, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')
            
            # Add value labels on bars
            for i, (bar, value) in enumerate(zip(bars, top_drugs.values)):
                ax.text(value + max(top_drugs.values) * 0.01, i, f'{value:,}', 
                       va='center', fontsize=9)
            
            # Invert y-axis to show highest values at top
            ax.invert_yaxis()
            
            plt.tight_layout()
            
            drugs_path = output_path / 'top_drugs_bar.png'
            plt.savefig(drugs_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Saved top drugs bar chart to {drugs_path}")
    
    logger.info("All trend plots generated successfully")

if __name__ == "__main__":
    # Example usage
    
    # Create sample data for testing
    import pandas as pd
    from datetime import datetime, timedelta
    
    # Generate sample events data
    np.random.seed(42)
    
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    sample_data = []
    
    reactions = ['HEADACHE', 'NAUSEA', 'DIZZINESS', 'FATIGUE', 'RASH']
    drugs = ['ASPIRIN', 'IBUPROFEN', 'ACETAMINOPHEN', 'METFORMIN', 'LISINOPRIL']
    
    for _ in range(1000):
        sample_data.append({
            'event_date': np.random.choice(dates),
            'case_id': f"CASE_{np.random.randint(1, 10000)}",
            'drug': np.random.choice(drugs),
            'reaction_pt': np.random.choice(reactions),
            'sex': np.random.choice(['M', 'F', 'UNK']),
            'age': np.random.randint(18, 80),
            'country': 'US',
            'serious': np.random.choice([True, False])
        })
    
    sample_df = pd.DataFrame(sample_data)
    
    # Create aggregations
    monthly_overall_df, monthly_reaction_df, monthly_drug_df = create_all_aggregations(sample_df)
    
    print("Monthly Overall:")
    print(monthly_overall_df.head())
    print(f"\\nMonthly by Reaction ({len(monthly_reaction_df)} records):")
    print(monthly_reaction_df.head())
    print(f"\\nMonthly by Drug ({len(monthly_drug_df)} records):")
    print(monthly_drug_df.head())
    
    # Test new functions
    print("\\n" + "="*50)
    print("TESTING NEW FUNCTIONS")
    print("="*50)
    
    # Test top_k function
    print("\\nTop 3 reactions:")
    top_reactions = top_k(monthly_reaction_df, 'reaction_pt', k=3)
    print(top_reactions)
    
    print("\\nTop 3 drugs:")
    top_drugs = top_k(monthly_drug_df, 'drug', k=3)
    print(top_drugs)
    
    # Test plot_monthly function
    print("\\nCreating individual monthly plot...")
    plot_monthly(monthly_overall_df, 'Sample Overall Trend', 'sample_plots/individual_trend.png')
    
    # Test save_trend_plots function (the three requested plots)
    print("\\nCreating the three requested trend plots...")
    save_trend_plots(monthly_overall_df, monthly_reaction_df, monthly_drug_df, "sample_plots")
    
    # Also save the original comprehensive plots
    save_plots(monthly_overall_df, monthly_reaction_df, monthly_drug_df, "sample_plots")
    
    print("\\nAll sample plots saved to 'sample_plots' directory")
    print("Generated files:")
    print("  ✓ overall_trend.png (new plot_monthly function)")
    print("  ✓ top_reactions_bar.png (new top-10 reactions bar)")
    print("  ✓ top_drugs_bar.png (new top-10 drugs bar)")
    print("  ✓ individual_trend.png (demo of plot_monthly)")
    print("  ✓ Other comprehensive plots from save_plots()")
