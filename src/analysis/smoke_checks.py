"""
Console QA Report for AE Trend Analyzer.

This script provides a comprehensive quality assurance report for the processed data,
including row counts, date ranges, top drugs/reactions, and data quality warnings.
"""

import pandas as pd
from pathlib import Path
import sys
from datetime import datetime


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


def print_status(check_name, status, value=None):
    """Print a check status with pass/fail marker."""
    marker = "✓ PASS" if status else "✗ FAIL"
    if value:
        print(f"{marker:<8} {check_name}: {value}")
    else:
        print(f"{marker:<8} {check_name}")


def check_file_exists(filepath):
    """Check if file exists and return status."""
    return filepath.exists()


def analyze_faers_data(filepath):
    """Analyze FAERS events data and return summary statistics."""
    if not filepath.exists():
        return None
    
    try:
        df = pd.read_parquet(filepath)
        
        # Basic stats
        total_rows = len(df)
        date_range = None
        if 'event_date' in df.columns and not df['event_date'].isnull().all():
            min_date = df['event_date'].min()
            max_date = df['event_date'].max()
            date_range = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
        
        # Top drugs and reactions
        top_drugs = df['drug'].value_counts().head(10) if 'drug' in df.columns else None
        top_reactions = df['reaction_pt'].value_counts().head(10) if 'reaction_pt' in df.columns else None
        
        # Data quality checks
        missing_event_date_pct = (df['event_date'].isnull().sum() / total_rows * 100) if 'event_date' in df.columns else 0
        missing_sex_pct = (df['sex'].isnull().sum() / total_rows * 100) if 'sex' in df.columns else 0
        missing_reaction_pct = (df['reaction_pt'].isnull().sum() / total_rows * 100) if 'reaction_pt' in df.columns else 0
        
        return {
            'total_rows': total_rows,
            'date_range': date_range,
            'top_drugs': top_drugs,
            'top_reactions': top_reactions,
            'missing_event_date_pct': missing_event_date_pct,
            'missing_sex_pct': missing_sex_pct,
            'missing_reaction_pct': missing_reaction_pct
        }
    except Exception as e:
        print(f"Error analyzing FAERS data: {e}")
        return None


def analyze_monthly_data(filepath):
    """Analyze monthly aggregation files."""
    if not filepath.exists():
        return None
    
    try:
        df = pd.read_csv(filepath)
        return {
            'total_rows': len(df),
            'columns': list(df.columns),
            'has_ym': 'ym' in df.columns,
            'ym_null_count': df['ym'].isnull().sum() if 'ym' in df.columns else 0
        }
    except Exception as e:
        print(f"Error analyzing {filepath.name}: {e}")
        return None


def run_smoke_checks():
    """Run comprehensive smoke checks and generate console report."""
    
    print_header("AE TREND ANALYZER - QA SMOKE CHECK REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define file paths
    data_dir = Path("data/processed")
    faers_file = data_dir / "faers_events.parquet"
    monthly_counts_file = data_dir / "monthly_counts.csv"
    monthly_reaction_file = data_dir / "monthly_by_reaction.csv"
    monthly_drug_file = data_dir / "monthly_by_drug.csv"
    reviews_file = data_dir / "review_events.csv"
    
    # File existence checks
    print_section("FILE EXISTENCE CHECKS")
    print_status("FAERS Events Data", check_file_exists(faers_file), str(faers_file))
    print_status("Monthly Counts", check_file_exists(monthly_counts_file), str(monthly_counts_file))
    print_status("Monthly by Reaction", check_file_exists(monthly_reaction_file), str(monthly_reaction_file))
    print_status("Monthly by Drug", check_file_exists(monthly_drug_file), str(monthly_drug_file))
    print_status("Review Events", check_file_exists(reviews_file), str(reviews_file))
    
    # FAERS data analysis
    print_section("FAERS DATA ANALYSIS")
    faers_stats = analyze_faers_data(faers_file)
    if faers_stats:
        print(f"Total Records: {faers_stats['total_rows']:,}")
        if faers_stats['date_range']:
            print(f"Date Coverage: {faers_stats['date_range']}")
        else:
            print("Date Coverage: No valid dates found")
        
        print("\nTop 10 Drugs by Report Count:")
        if faers_stats['top_drugs'] is not None:
            for i, (drug, count) in enumerate(faers_stats['top_drugs'].items(), 1):
                print(f"  {i:2d}. {drug:<30} ({count:,} reports)")
        else:
            print("  No drug data available")
        
        print("\nTop 10 Reactions by Report Count:")
        if faers_stats['top_reactions'] is not None:
            for i, (reaction, count) in enumerate(faers_stats['top_reactions'].items(), 1):
                print(f"  {i:2d}. {reaction:<30} ({count:,} reports)")
        else:
            print("  No reaction data available")
    else:
        print("Unable to analyze FAERS data")
    
    # Data quality warnings
    print_section("DATA QUALITY CHECKS")
    if faers_stats:
        print_status(
            "Event Date Completeness", 
            faers_stats['missing_event_date_pct'] < 5.0,
            f"{faers_stats['missing_event_date_pct']:.1f}% missing (threshold: <5%)"
        )
        print_status(
            "Sex Completeness", 
            faers_stats['missing_sex_pct'] < 5.0,
            f"{faers_stats['missing_sex_pct']:.1f}% missing (threshold: <5%)"
        )
        print_status(
            "Reaction Completeness", 
            faers_stats['missing_reaction_pct'] < 5.0,
            f"{faers_stats['missing_reaction_pct']:.1f}% missing (threshold: <5%)"
        )
    
    # Monthly data checks
    print_section("MONTHLY AGGREGATION CHECKS")
    
    monthly_files = [
        ("Monthly Counts", monthly_counts_file),
        ("Monthly by Reaction", monthly_reaction_file),
        ("Monthly by Drug", monthly_drug_file)
    ]
    
    for name, filepath in monthly_files:
        stats = analyze_monthly_data(filepath)
        if stats:
            print(f"\n{name}:")
            print(f"  Rows: {stats['total_rows']:,}")
            print(f"  Columns: {', '.join(stats['columns'])}")
            print_status(f"  YM Column Present", stats['has_ym'])
            if stats['has_ym']:
                print_status(f"  YM Data Quality", stats['ym_null_count'] == 0, 
                           f"{stats['ym_null_count']} null values")
        else:
            print(f"\n{name}: Unable to analyze")
    
    print_section("SUMMARY")
    
    # Count passed/failed checks
    all_files_exist = all([
        check_file_exists(faers_file),
        check_file_exists(monthly_counts_file),
        check_file_exists(monthly_reaction_file),
        check_file_exists(monthly_drug_file)
    ])
    
    data_quality_ok = True
    if faers_stats:
        data_quality_ok = (
            faers_stats['missing_event_date_pct'] < 5.0 and
            faers_stats['missing_sex_pct'] < 5.0 and
            faers_stats['missing_reaction_pct'] < 5.0
        )
    
    print_status("All Required Files Present", all_files_exist)
    print_status("Data Quality Within Thresholds", data_quality_ok)
    
    if faers_stats and faers_stats['total_rows'] > 0:
        print_status("FAERS Data Available", True, f"{faers_stats['total_rows']:,} records")
    else:
        print_status("FAERS Data Available", False)
    
    overall_status = all_files_exist and data_quality_ok and (faers_stats and faers_stats['total_rows'] > 0)
    print_status("Overall System Health", overall_status)
    
    print(f"\n{'='*60}")
    
    return overall_status


if __name__ == "__main__":
    success = run_smoke_checks()
    sys.exit(0 if success else 1)
