"""
Build All ETL Pipeline

Main orchestrator script that combines FAERS data loading, review processing,
aggregation, and visualization into a complete pipeline.

Usage:
    python -m src.etl.build_all [options]
    
Options:
    --raw-dir PATH       Override raw data directory
    --proc-dir PATH      Override processed data directory  
    --fig-dir PATH       Override figures output directory
    --limit-quarters N   Process only the N most recent quarters
    --workers N          Number of worker processes (future use)
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from typing import Optional, List
import warnings

import pandas as pd
import numpy as np
from tqdm import tqdm

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import configuration and modules
from config import (
    RAW_DIR, PROC_DIR, FIG_DIR, OUTPUT_FILES, PLOT_FILES,
    REVIEW_CONFIG, LOGGING_CONFIG, ensure_directories
)
from etl.faers_loader import discover_quarters, load_quarter_data
from etl.reviews_loader import process_reviews
from analysis.aggregate import create_all_aggregations, save_plots, save_trend_plots

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format']
)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="AE Trend Analyzer ETL Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline with default settings
  python -m src.etl.build_all
  
  # Process only the 4 most recent quarters for quick testing
  python -m src.etl.build_all --limit-quarters 4
  
  # Use custom directories
  python -m src.etl.build_all --raw-dir /path/to/raw --proc-dir /path/to/processed
  
  # Limit quarters and use custom figure directory
  python -m src.etl.build_all --limit-quarters 2 --fig-dir /path/to/figures
        """
    )
    
    parser.add_argument(
        '--raw-dir',
        type=Path,
        help='Override raw data directory (default: from config.py)'
    )
    
    parser.add_argument(
        '--proc-dir', 
        type=Path,
        help='Override processed data directory (default: from config.py)'
    )
    
    parser.add_argument(
        '--fig-dir',
        type=Path, 
        help='Override figures output directory (default: from config.py)'
    )
    
    parser.add_argument(
        '--limit-quarters',
        type=int,
        metavar='N',
        help='Process only the N most recent quarters (useful for quick testing)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        metavar='N', 
        help='Number of worker processes for parallel processing (default: 1, future use)'
    )
    
    return parser.parse_args()

def setup_directories(args: argparse.Namespace) -> dict:
    """
    Set up and create necessary directories using configuration and CLI overrides.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Dictionary of directory paths
    """
    # Use CLI arguments if provided, otherwise use config defaults
    raw_dir = args.raw_dir if args.raw_dir else RAW_DIR
    proc_dir = args.proc_dir if args.proc_dir else PROC_DIR  
    fig_dir = args.fig_dir if args.fig_dir else FIG_DIR
    
    # Create directories if they don't exist
    for directory in [raw_dir, proc_dir, fig_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    dirs = {
        'raw': raw_dir,
        'processed': proc_dir,
        'reports': fig_dir.parent,
        'figures': fig_dir
    }
    
    logger.info("Directory configuration:")
    logger.info(f"  Raw data: {raw_dir}")
    logger.info(f"  Processed: {proc_dir}")
    logger.info(f"  Figures: {fig_dir}")
    
    return dirs

def process_faers_data(raw_dir: Path, proc_dir: Path, limit_quarters: Optional[int] = None) -> pd.DataFrame:
    """
    Process all FAERS quarterly data and create consolidated dataset.
    
    Args:
        raw_dir: Raw data directory
        proc_dir: Processed data directory
        limit_quarters: If specified, process only the N most recent quarters
    
    Returns:
        Consolidated FAERS events DataFrame
    """
    logger.info("Starting FAERS data processing")
    
    # Discover quarterly folders
    quarters = discover_quarters(raw_dir)
    
    if not quarters:
        logger.error("No FAERS quarterly folders found")
        return pd.DataFrame()
    
    # Apply quarter limiting if specified
    if limit_quarters is not None and limit_quarters > 0:
        if limit_quarters < len(quarters):
            # Sort quarters by name (which should be chronological) and take the most recent N
            quarters_sorted = sorted(quarters, key=lambda x: x.name.lower())
            quarters = quarters_sorted[-limit_quarters:]
            logger.info(f"Limited to {limit_quarters} most recent quarters: {[q.name for q in quarters]}")
        else:
            logger.info(f"Requested {limit_quarters} quarters, but only {len(quarters)} available - processing all")
    
    logger.info(f"Processing {len(quarters)} FAERS quarterly folders")
    
    # Process each quarter
    all_events = []
    
    for quarter in tqdm(quarters, desc="Processing FAERS quarters"):
        logger.info(f"Processing {quarter.name}")
        
        try:
            events = load_quarter_data(quarter)
            
            if not events.empty:
                # Add quarter info for tracking
                events['quarter'] = quarter.name
                all_events.append(events)
                logger.info(f"Loaded {len(events)} events from {quarter.name}")
            else:
                logger.warning(f"No events loaded from {quarter.name}")
                
        except Exception as e:
            logger.error(f"Failed to process {quarter.name}: {e}")
            continue
    
    if not all_events:
        logger.error("No FAERS data successfully processed")
        return pd.DataFrame()
    
    # Concatenate all quarters
    logger.info("Concatenating all quarterly data")
    combined_events = pd.concat(all_events, ignore_index=True)
    
    # Remove duplicates across quarters
    initial_count = len(combined_events)
    combined_events = combined_events.drop_duplicates(
        subset=['case_id', 'drug', 'reaction_pt', 'event_date']
    )
    final_count = len(combined_events)
    
    if initial_count != final_count:
        logger.info(f"Removed {initial_count - final_count} cross-quarter duplicates")
    
    # Sort by date
    combined_events = combined_events.sort_values('event_date')
    
    # Save consolidated events
    output_file = proc_dir / OUTPUT_FILES['faers_events']
    combined_events.to_parquet(output_file, index=False)
    logger.info(f"Saved consolidated FAERS events to {output_file}")
    
    # Print summary statistics
    logger.info(f"FAERS Processing Summary:")
    logger.info(f"  Total events: {len(combined_events):,}")
    
    # Handle date range calculation safely
    valid_dates = combined_events['event_date'].dropna()
    if len(valid_dates) > 0:
        logger.info(f"  Date range: {valid_dates.min()} to {valid_dates.max()}")
    else:
        logger.info("  Date range: No valid dates found")
    
    logger.info(f"  Unique drugs: {combined_events['drug'].nunique():,}")
    logger.info(f"  Unique reactions: {combined_events['reaction_pt'].nunique():,}")
    logger.info(f"  Serious events: {combined_events['serious'].sum():,} ({combined_events['serious'].mean()*100:.1f}%)")
    
    return combined_events

def process_reviews_data(raw_dir: Path, proc_dir: Path) -> pd.DataFrame:
    """
    Process drug review datasets and extract adverse event terms.
    
    Args:
        raw_dir: Raw data directory
        proc_dir: Processed data directory
    
    Returns:
        Processed reviews DataFrame
    """
    logger.info("Starting reviews data processing")
    
    # Define review file paths
    webmd_path = raw_dir / 'WebMD Drug Reviews Dataset' / 'webmd.csv'
    uci_train_path = raw_dir / 'UCI ML Drug Review Dataset' / 'drugsComTrain_raw.csv'
    uci_test_path = raw_dir / 'UCI ML Drug Review Dataset' / 'drugsComTest_raw.csv'
    
    # Check which files exist
    available_files = []
    if webmd_path.exists():
        available_files.append(f"WebMD: {webmd_path}")
    if uci_train_path.exists():
        available_files.append(f"UCI Train: {uci_train_path}")
    if uci_test_path.exists():
        available_files.append(f"UCI Test: {uci_test_path}")
    
    if not available_files:
        logger.warning("No review datasets found")
        return pd.DataFrame()
    
    logger.info("Available review files:")
    for file_info in available_files:
        logger.info(f"  {file_info}")
    
    # Process reviews
    try:
        processed_reviews = process_reviews(
            webmd_path=webmd_path if webmd_path.exists() else None,
            uci_train_path=uci_train_path if uci_train_path.exists() else None,
            uci_test_path=uci_test_path if uci_test_path.exists() else None
        )
        
        if processed_reviews.empty:
            logger.warning("No reviews processed")
            return pd.DataFrame()
        
        # Save processed reviews
        output_file = proc_dir / OUTPUT_FILES['review_events']
        processed_reviews.to_csv(output_file, index=False, encoding='utf-8')
        logger.info(f"Saved processed reviews to {output_file}")
        
        # Print summary statistics
        total_terms = processed_reviews['extracted_terms'].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        ).sum()
        total_pts = processed_reviews['mapped_pt'].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        ).sum()
        reviews_with_terms = processed_reviews['extracted_terms'].apply(
            lambda x: len(x) > 0 if isinstance(x, list) else False
        ).sum()
        
        logger.info(f"Reviews Processing Summary:")
        logger.info(f"  Total reviews: {len(processed_reviews):,}")
        logger.info(f"  Reviews with AE terms: {reviews_with_terms:,} ({reviews_with_terms/len(processed_reviews)*100:.1f}%)")
        logger.info(f"  Total extracted terms: {total_terms:,}")
        logger.info(f"  Total mapped MedDRA PTs: {total_pts:,}")
        logger.info(f"  Unique drugs: {processed_reviews['drug'].nunique():,}")
        
        return processed_reviews
        
    except Exception as e:
        logger.error(f"Failed to process reviews: {e}")
        return pd.DataFrame()

def create_monthly_aggregations(events_df: pd.DataFrame, proc_dir: Path) -> tuple:
    """
    Create and save monthly aggregation files.
    
    Args:
        events_df: FAERS events DataFrame
        proc_dir: Processed data directory
        
    Returns:
        Tuple of (monthly_overall, monthly_reaction, monthly_drug) DataFrames
    """
    logger.info("Creating monthly aggregations")
    
    if events_df.empty:
        logger.warning("No events data for aggregation")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    # Create aggregations
    monthly_overall_df, monthly_reaction_df, monthly_drug_df = create_all_aggregations(events_df)
    
    # Save aggregations
    if not monthly_overall_df.empty:
        output_file = proc_dir / OUTPUT_FILES['monthly_counts']
        monthly_overall_df.to_csv(output_file, index=False)
        logger.info(f"Saved monthly overall counts to {output_file}")
    
    if not monthly_reaction_df.empty:
        output_file = proc_dir / OUTPUT_FILES['monthly_by_reaction']
        monthly_reaction_df.to_csv(output_file, index=False)
        logger.info(f"Saved monthly by reaction counts to {output_file}")
    
    if not monthly_drug_df.empty:
        output_file = proc_dir / OUTPUT_FILES['monthly_by_drug']
        monthly_drug_df.to_csv(output_file, index=False)
        logger.info(f"Saved monthly by drug counts to {output_file}")
    
    # Print aggregation statistics
    logger.info(f"Aggregation Summary:")
    logger.info(f"  Monthly periods: {len(monthly_overall_df)}")
    if not monthly_overall_df.empty:
        logger.info(f"  Date range: {monthly_overall_df['ym'].min()} to {monthly_overall_df['ym'].max()}")
        logger.info(f"  Average monthly events: {monthly_overall_df['count'].mean():.0f}")
    logger.info(f"  Unique reactions tracked: {monthly_reaction_df['reaction_pt'].nunique() if not monthly_reaction_df.empty else 0}")
    logger.info(f"  Unique drugs tracked: {monthly_drug_df['drug'].nunique() if not monthly_drug_df.empty else 0}")
    
    return monthly_overall_df, monthly_reaction_df, monthly_drug_df

def generate_visualizations(monthly_overall_df: pd.DataFrame,
                          monthly_reaction_df: pd.DataFrame,
                          monthly_drug_df: pd.DataFrame,
                          fig_dir: Path) -> None:
    """
    Generate and save visualization plots.
    
    Args:
        monthly_overall_df: Monthly overall counts DataFrame
        monthly_reaction_df: Monthly by reaction DataFrame
        monthly_drug_df: Monthly by drug DataFrame
        fig_dir: Figures output directory
    """
    logger.info("Generating visualizations")
    
    try:
        # Generate the three specific trend plots requested
        save_trend_plots(
            monthly_overall_df=monthly_overall_df,
            monthly_reaction_df=monthly_reaction_df,
            monthly_drug_df=monthly_drug_df,
            output_dir=fig_dir,
            top_n=10
        )
        
        # Also generate comprehensive plots for additional analysis
        save_plots(
            monthly_overall_df=monthly_overall_df,
            monthly_reaction_df=monthly_reaction_df,
            monthly_drug_df=monthly_drug_df,
            output_dir=fig_dir,
            top_n=10
        )
        logger.info(f"All visualizations saved to {fig_dir}")
        
    except Exception as e:
        logger.error(f"Failed to generate visualizations: {e}")

def print_final_summary(proc_dir: Path, fig_dir: Path) -> None:
    """
    Print final summary of all generated outputs.
    
    Args:
        proc_dir: Processed data directory
        fig_dir: Figures directory
    """
    logger.info("="*60)
    logger.info("PIPELINE COMPLETION SUMMARY")
    logger.info("="*60)
    
    # Check generated files
    expected_files = [
        proc_dir / OUTPUT_FILES['faers_events'],
        proc_dir / OUTPUT_FILES['monthly_counts'],
        proc_dir / OUTPUT_FILES['monthly_by_reaction'],
        proc_dir / OUTPUT_FILES['monthly_by_drug'],
        proc_dir / OUTPUT_FILES['review_events'],
    ]
    
    expected_plots = [
        fig_dir / 'overall_trend.png',
        fig_dir / 'top_reactions_bar.png',
        fig_dir / 'top_drugs_bar.png',
        fig_dir / 'top_reactions_trend.png',
        fig_dir / 'top_drugs_trend.png', 
        fig_dir / 'summary_statistics.png',
    ]
    
    logger.info("Generated Data Files:")
    for file_path in expected_files:
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            logger.info(f"  ✓ {file_path.name} ({size_mb:.1f} MB)")
        else:
            logger.info(f"  ✗ {file_path.name} (missing)")
    
    logger.info("\\nGenerated Plots:")
    for plot_path in expected_plots:
        if plot_path.exists():
            logger.info(f"  ✓ {plot_path.name}")
        else:
            logger.info(f"  ✗ {plot_path.name} (missing)")
    
    logger.info("\\nNext Steps:")
    logger.info("  1. Review the generated visualizations in reports/figures/")
    logger.info("  2. Examine the processed data files in data/processed/")
    logger.info("  3. Use the monthly aggregations for further analysis")
    logger.info("  4. Consider extending the MedDRA mapping for reviews")
    
    logger.info("="*60)

def main():
    """
    Main pipeline execution function.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    logger.info("Starting AE Trend Analyzer ETL Pipeline")
    
    if args.limit_quarters:
        logger.info(f"Limiting processing to {args.limit_quarters} most recent quarters")
    if args.workers > 1:
        logger.info(f"Worker processes configured: {args.workers} (future feature)")
    
    try:
        # Setup directories using CLI arguments or config defaults
        dirs = setup_directories(args)
        
        # Process FAERS data
        logger.info("\\n" + "="*50)
        logger.info("STEP 1: PROCESSING FAERS DATA")
        logger.info("="*50)
        
        faers_events = process_faers_data(
            raw_dir=dirs['raw'],
            proc_dir=dirs['processed'], 
            limit_quarters=args.limit_quarters
        )
        
        # Process reviews data
        logger.info("\\n" + "="*50)
        logger.info("STEP 2: PROCESSING REVIEWS DATA")
        logger.info("="*50)
        
        reviews_data = process_reviews_data(
            raw_dir=dirs['raw'],
            proc_dir=dirs['processed']
        )
        
        # Create monthly aggregations
        logger.info("\\n" + "="*50)
        logger.info("STEP 3: CREATING MONTHLY AGGREGATIONS")
        logger.info("="*50)
        
        monthly_overall_df, monthly_reaction_df, monthly_drug_df = create_monthly_aggregations(
            events_df=faers_events,
            proc_dir=dirs['processed']
        )
        
        # Generate visualizations
        logger.info("\\n" + "="*50)
        logger.info("STEP 4: GENERATING VISUALIZATIONS")
        logger.info("="*50)
        
        generate_visualizations(
            monthly_overall_df=monthly_overall_df,
            monthly_reaction_df=monthly_reaction_df,
            monthly_drug_df=monthly_drug_df,
            fig_dir=dirs['figures']
        )
        
        # Print final summary
        logger.info("\\n" + "="*50)
        logger.info("STEP 5: PIPELINE COMPLETED")
        logger.info("="*50)
        
        print_final_summary(
            proc_dir=dirs['processed'],
            fig_dir=dirs['figures']
        )
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
