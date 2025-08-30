"""
FAERS ASCII Data Loader Module

This module provides functionality to load and process FAERS ASCII quarterly data dumps,
normalize schemas across different years, and build consolidated adverse event datasets.
"""

import os
import re
import gc
import logging
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, date

import pandas as pd
import numpy as np
from tqdm import tqdm

# Import configuration
from ..config import (
    COLUMN_MAPPINGS, SEX_MAPPING, SERIOUS_MAPPING, 
    FAERS_CONFIG, LOGGING_CONFIG
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format']
)
logger = logging.getLogger(__name__)

def discover_quarters(raw_dir: Union[str, Path]) -> List[Path]:
    """
    Discover all FAERS quarterly folders in the raw data directory.
    
    Args:
        raw_dir: Path to the raw data directory
        
    Returns:
        List of Path objects for each quarter folder
    """
    raw_path = Path(raw_dir)
    quarter_folders = []
    
    if not raw_path.exists():
        logger.error(f"Raw data directory does not exist: {raw_path}")
        return quarter_folders
    
    # Look for folders matching FAERS quarterly patterns
    pattern = re.compile(FAERS_CONFIG['quarterly_pattern'], re.IGNORECASE)
    
    for folder in raw_path.iterdir():
        if folder.is_dir() and pattern.match(folder.name):
            quarter_folders.append(folder)
    
    quarter_folders.sort(key=lambda x: x.name.lower())
    logger.info(f"Discovered {len(quarter_folders)} FAERS quarterly folders")
    
    return quarter_folders

def _find_ascii_files(folder: Path) -> Dict[str, Optional[Path]]:
    """
    Find ASCII files in a quarter folder, handling case variations.
    
    Args:
        folder: Path to the quarter folder
        
    Returns:
        Dictionary mapping file types to their paths
    """
    ascii_files = {}
    file_types = ['DEMO', 'REAC', 'DRUG', 'OUTC', 'THER', 'INDI']
    
    # Look for ASCII subfolder (case insensitive)
    ascii_folder = None
    for subfolder in folder.iterdir():
        if subfolder.is_dir() and subfolder.name.lower() == 'ascii':
            ascii_folder = subfolder
            break
    
    if not ascii_folder:
        logger.warning(f"No ASCII folder found in {folder}")
        return {file_type: None for file_type in file_types}
    
    # Extract quarter info from folder name
    quarter_match = re.search(r'(\d{4})q([1-4])', folder.name, re.IGNORECASE)
    if not quarter_match:
        logger.warning(f"Could not extract quarter info from {folder.name}")
        return {file_type: None for file_type in file_types}
    
    year, quarter = quarter_match.groups()
    
    # Look for files with various naming patterns
    for file_type in file_types:
        file_path = None
        
        # Try different naming patterns
        patterns = [
            f"{file_type}{year[2:]}Q{quarter}.txt",  # DEMO24Q1.txt
            f"{file_type}{year[2:]}q{quarter}.txt",  # demo24q1.txt
            f"{file_type}{year}Q{quarter}.txt",     # DEMO2024Q1.txt
            f"{file_type}{year}q{quarter}.txt",     # demo2024q1.txt
        ]
        
        for pattern in patterns:
            potential_files = list(ascii_folder.glob(pattern))
            if potential_files:
                file_path = potential_files[0]
                break
            
            # Try case insensitive
            potential_files = list(ascii_folder.glob(pattern.lower()))
            if potential_files:
                file_path = potential_files[0]
                break
        
        ascii_files[file_type] = file_path
        if file_path:
            logger.debug(f"Found {file_type} file: {file_path}")
        else:
            logger.debug(f"No {file_type} file found in {ascii_folder}")
    
    return ascii_files

def _parse_date_robust(date_str: str) -> Optional[date]:
    """
    Robustly parse date strings from FAERS data.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Parsed date object or None if parsing fails
    """
    if pd.isna(date_str) or not date_str or date_str.strip() == '':
        return None
    
    date_str = str(date_str).strip()
    
    # Common date patterns in FAERS
    patterns = [
        r'(\d{4})(\d{2})(\d{2})',           # YYYYMMDD
        r'(\d{4})-(\d{2})-(\d{2})',         # YYYY-MM-DD
        r'(\d{2})/(\d{2})/(\d{4})',         # MM/DD/YYYY
        r'(\d{2})-(\d{2})-(\d{4})',         # MM-DD-YYYY
        r'(\d{4})/(\d{2})/(\d{2})',         # YYYY/MM/DD
    ]
    
    for pattern in patterns:
        match = re.match(pattern, date_str)
        if match:
            try:
                if pattern == patterns[0]:  # YYYYMMDD
                    year, month, day = map(int, match.groups())
                elif pattern in [patterns[1], patterns[4]]:  # YYYY-MM-DD or YYYY/MM/DD
                    year, month, day = map(int, match.groups())
                else:  # MM/DD/YYYY or MM-DD-YYYY
                    month, day, year = map(int, match.groups())
                
                return date(year, month, day)
            except ValueError:
                continue
    
    # Try pandas to_datetime as fallback
    try:
        parsed_date = pd.to_datetime(date_str, errors='coerce')
        if not pd.isna(parsed_date):
            return parsed_date.date()
    except:
        pass
    
    logger.debug(f"Could not parse date: {date_str}")
    return None

def _get_essential_columns(file_type: str) -> List[str]:
    """
    Get the essential columns needed for a specific file type to reduce memory usage.
    
    Args:
        file_type: FAERS file type (DEMO, REAC, DRUG, etc.)
        
    Returns:
        List of essential column names (case-insensitive patterns)
    """
    essential_cols = {
        'DEMO': ['PRIMARYID', 'CASEID', 'primaryid', 'caseid', 'AGE', 'age', 'SEX', 'sex', 
                'PATIENTSEX', 'patientsex', 'OCCUR_COUNTRY', 'occur_country', 'COUNTRY', 'country',
                'EVENT_DT', 'event_dt', 'RECEIPTDATE', 'receiptdate'],
        'REAC': ['PRIMARYID', 'CASEID', 'primaryid', 'caseid', 'PT', 'pt', 
                'REACTIONMEDDRAPT', 'reactionmeddrapt'],
        'DRUG': ['PRIMARYID', 'CASEID', 'primaryid', 'caseid', 'DRUGNAME', 'drugname', 
                'MEDICINALPRODUCT', 'medicinalproduct'],
        'OUTC': ['PRIMARYID', 'CASEID', 'primaryid', 'caseid', 'OUTC_COD', 'outc_cod'],
        'THER': ['PRIMARYID', 'CASEID', 'primaryid', 'caseid'],
        'INDI': ['PRIMARYID', 'CASEID', 'primaryid', 'caseid']
    }
    
    return essential_cols.get(file_type, ['PRIMARYID', 'CASEID', 'primaryid', 'caseid'])

def _read_large_file_chunked(file_path: Path, file_type: str, 
                           chunk_size: Optional[int] = None) -> pd.DataFrame:
    """
    Read a large TXT file in chunks to avoid memory issues.
    
    Args:
        file_path: Path to the file
        file_type: FAERS file type (DEMO, REAC, etc.)
        chunk_size: Number of rows per chunk (uses config default if None)
        
    Returns:
        Consolidated DataFrame with optimized memory usage
    """
    if chunk_size is None:
        chunk_size = FAERS_CONFIG['chunk_size']
    
    logger.info(f"Reading large file in chunks: {file_path.name} (chunk_size={chunk_size:,})")
    
    # Get essential columns for this file type
    essential_patterns = _get_essential_columns(file_type)
    
    chunks = []
    total_rows = 0
    
    try:
        # First, read just the header to identify available columns
        header_df = pd.read_csv(file_path, sep='\t', nrows=0, dtype=str, encoding='utf-8')
    except UnicodeDecodeError:
        logger.warning(f"UTF-8 decode failed for {file_path}, trying latin-1")
        header_df = pd.read_csv(file_path, sep='\t', nrows=0, dtype=str, encoding='latin-1')
    
    available_columns = [col.strip() for col in header_df.columns]
    
    # Find which essential columns actually exist (case-insensitive)
    columns_to_keep = []
    for pattern in essential_patterns:
        for col in available_columns:
            if col.lower() == pattern.lower():
                columns_to_keep.append(col)
                break
    
    if not columns_to_keep:
        logger.warning(f"No essential columns found in {file_path.name}, keeping all columns")
        columns_to_keep = None
    else:
        logger.info(f"Keeping {len(columns_to_keep)} essential columns from {len(available_columns)} total")
    
    # Read file in chunks
    try:
        chunk_reader = pd.read_csv(
            file_path, 
            sep='\t', 
            dtype=str, 
            encoding='utf-8',
            chunksize=chunk_size,
            na_values=['', 'NULL', 'null'], 
            keep_default_na=True,
            usecols=columns_to_keep
        )
    except UnicodeDecodeError:
        logger.warning(f"UTF-8 decode failed for chunked reading, trying latin-1")
        chunk_reader = pd.read_csv(
            file_path, 
            sep='\t', 
            dtype=str, 
            encoding='latin-1',
            chunksize=chunk_size,
            na_values=['', 'NULL', 'null'], 
            keep_default_na=True,
            errors='replace',
            usecols=columns_to_keep
        )
    
    # Process chunks
    for i, chunk in enumerate(tqdm(chunk_reader, desc=f"Reading {file_type} chunks")):
        # Clean column names
        chunk.columns = chunk.columns.str.strip()
        
        # Drop completely empty rows
        chunk = chunk.dropna(how='all')
        
        if not chunk.empty:
            chunks.append(chunk)
            total_rows += len(chunk)
        
        # Periodically collect garbage to manage memory
        if i % 10 == 0:
            gc.collect()
    
    if not chunks:
        logger.warning(f"No data found in {file_path.name}")
        return pd.DataFrame()
    
    logger.info(f"Concatenating {len(chunks)} chunks with {total_rows:,} total rows")
    
    # Concatenate all chunks
    df = pd.concat(chunks, ignore_index=True)
    
    # Clear chunks from memory
    del chunks
    gc.collect()
    
    # Memory optimization: convert object columns to category where beneficial
    for col in df.columns:
        if df[col].dtype == 'object':
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.5:  # If less than 50% unique values, convert to category
                df[col] = df[col].astype('category')
    
    logger.info(f"Chunked reading complete: {len(df):,} rows, {len(df.columns)} columns")
    return df

def _log_join_stats(before_count: int, after_count: int, join_type: str, 
                   table_name: str, join_method: str = "inner") -> None:
    """
    Log statistics about join operations including row loss warnings.
    
    Args:
        before_count: Number of rows before join
        after_count: Number of rows after join
        join_type: Description of the join (e.g., "DEMO with REAC")
        table_name: Name of the table being joined
        join_method: Type of join (inner, left, etc.)
    """
    if join_method == "inner":
        # For inner joins, calculate loss due to missing keys
        rows_lost = before_count - after_count
        if before_count > 0:
            loss_percent = (rows_lost / before_count) * 100
        else:
            loss_percent = 0.0
        
        logger.info(f"Join {join_type}:")
        logger.info(f"  Before: {before_count:,} rows")
        logger.info(f"  After:  {after_count:,} rows")
        logger.info(f"  Lost:   {rows_lost:,} rows ({loss_percent:.1f}%)")
        
        # Warning for high data loss
        high_threshold = FAERS_CONFIG.get('join_loss_warning_threshold', 20.0)
        moderate_threshold = FAERS_CONFIG.get('join_loss_moderate_threshold', 10.0)
        
        if loss_percent > high_threshold:
            logger.warning(f"HIGH DATA LOSS in {join_type}: {loss_percent:.1f}% of rows dropped due to missing keys in {table_name}")
        elif loss_percent > moderate_threshold:
            logger.warning(f"Moderate data loss in {join_type}: {loss_percent:.1f}% of rows dropped")
        elif rows_lost > 0:
            logger.info(f"Minor data loss in {join_type}: {loss_percent:.1f}% of rows dropped")
        else:
            logger.info(f"Perfect key match in {join_type}: No rows lost")
            
    elif join_method == "left":
        # For left joins, no rows should be lost from the left table
        if after_count != before_count:
            rows_gained = after_count - before_count
            if rows_gained > 0:
                logger.info(f"Left join {join_type}: {rows_gained:,} rows added (1-to-many relationship)")
            else:
                rows_lost = before_count - after_count
                logger.warning(f"Unexpected row loss in left join {join_type}: {rows_lost:,} rows lost")
        else:
            logger.info(f"Left join {join_type}: Row count preserved ({after_count:,} rows)")

def _analyze_key_overlap(left_df: pd.DataFrame, right_df: pd.DataFrame, 
                        key_col: str, left_name: str, right_name: str) -> None:
    """
    Analyze and log the overlap of join keys between two DataFrames.
    
    Args:
        left_df: Left DataFrame for join
        right_df: Right DataFrame for join
        key_col: Name of the key column
        left_name: Name of left table for logging
        right_name: Name of right table for logging
    """
    left_keys = set(left_df[key_col].dropna().unique())
    right_keys = set(right_df[key_col].dropna().unique())
    
    overlap_keys = left_keys.intersection(right_keys)
    left_only = left_keys - right_keys
    right_only = right_keys - left_keys
    
    overlap_percent = (len(overlap_keys) / len(left_keys)) * 100 if left_keys else 0
    
    logger.info(f"Key overlap analysis ({left_name} vs {right_name}):")
    logger.info(f"  {left_name} unique keys: {len(left_keys):,}")
    logger.info(f"  {right_name} unique keys: {len(right_keys):,}")
    logger.info(f"  Overlapping keys: {len(overlap_keys):,} ({overlap_percent:.1f}%)")
    logger.info(f"  {left_name} only: {len(left_only):,}")
    logger.info(f"  {right_name} only: {len(right_only):,}")
    
    overlap_warning_threshold = FAERS_CONFIG.get('key_overlap_warning_threshold', 80.0)
    if overlap_percent < overlap_warning_threshold:
        logger.warning(f"Low key overlap ({overlap_percent:.1f}%) between {left_name} and {right_name}")

def load_faers_ascii(folder: Path) -> Dict[str, pd.DataFrame]:
    """
    Load ASCII files from a FAERS quarterly folder.
    
    Args:
        folder: Path to the quarter folder
        
    Returns:
        Dictionary of DataFrames, keyed by file type
    """
    logger.info(f"Loading FAERS data from {folder}")
    
    ascii_files = _find_ascii_files(folder)
    dataframes = {}
    
    for file_type, file_path in ascii_files.items():
        if file_path is None or not file_path.exists():
            logger.warning(f"Missing {file_type} file in {folder}")
            continue
        
        try:
            # Check file size for memory safety
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            file_size_threshold = FAERS_CONFIG['max_file_size_mb']
            
            if file_size_mb > file_size_threshold:
                logger.info(f"Large file detected ({file_size_mb:.1f}MB): {file_path.name}")
                logger.info("Using chunked reading for memory efficiency")
                df = _read_large_file_chunked(file_path, file_type)
            else:
                # Use standard reading for smaller files
                try:
                    df = pd.read_csv(file_path, sep='\t', dtype=str, encoding='utf-8', 
                                   na_values=['', 'NULL', 'null'], keep_default_na=True)
                except UnicodeDecodeError:
                    logger.warning(f"UTF-8 decode failed for {file_path}, trying latin-1")
                    df = pd.read_csv(file_path, sep='\t', dtype=str, encoding='latin-1',
                                   na_values=['', 'NULL', 'null'], keep_default_na=True,
                                   errors='replace')
                
                # Clean column names
                df.columns = df.columns.str.strip()
                
                # Apply memory optimizations if enabled
                if FAERS_CONFIG.get('memory_optimization', True):
                    for col in df.columns:
                        if df[col].dtype == 'object':
                            unique_ratio = df[col].nunique() / len(df)
                            if unique_ratio < 0.5:  # Convert to category if < 50% unique
                                df[col] = df[col].astype('category')
            
            logger.info(f"Loaded {file_type}: {len(df):,} rows, {len(df.columns)} columns")
            dataframes[file_type] = df
            
        except Exception as e:
            logger.error(f"Failed to load {file_type} from {file_path}: {e}")
            continue
    
    return dataframes

def _normalize_column(df: pd.DataFrame, target_col: str, source_cols: List[str]) -> pd.Series:
    """
    Normalize a column by finding the first available source column.
    
    Args:
        df: Input DataFrame
        target_col: Target column name
        source_cols: List of possible source column names
        
    Returns:
        Normalized Series
    """
    for col in source_cols:
        if col in df.columns:
            return df[col].astype(str).str.strip()
    
    # Return empty series if no matching column found
    logger.debug(f"No source column found for {target_col} in {source_cols}")
    return pd.Series(index=df.index, dtype=str)

def normalize_faers_schema(df_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Normalize FAERS schema across different years and file formats.
    
    Args:
        df_dict: Dictionary of DataFrames from load_faers_ascii
        
    Returns:
        Dictionary of normalized DataFrames
    """
    normalized = {}
    
    for file_type, df in df_dict.items():
        if df is None or df.empty:
            continue
        
        logger.info(f"Normalizing {file_type} schema")
        norm_df = df.copy()
        
        # Normalize based on file type
        if file_type == 'DEMO':
            # Demographics normalization
            norm_df['case_id'] = _normalize_column(df, 'case_id', COLUMN_MAPPINGS['case_id'])
            norm_df['sex'] = _normalize_column(df, 'sex', COLUMN_MAPPINGS['sex'])
            norm_df['age'] = _normalize_column(df, 'age', COLUMN_MAPPINGS['age'])
            norm_df['country'] = _normalize_column(df, 'country', COLUMN_MAPPINGS['country'])
            norm_df['event_date'] = _normalize_column(df, 'event_date', COLUMN_MAPPINGS['event_date'])
            
            # Normalize sex values
            norm_df['sex'] = norm_df['sex'].map(SEX_MAPPING).fillna('UNK')
            
            # Normalize age to numeric
            norm_df['age'] = pd.to_numeric(norm_df['age'], errors='coerce')
            
            # Normalize country codes
            norm_df['country'] = norm_df['country'].str.upper().str.strip()
            
            # Parse event dates
            norm_df['event_date'] = norm_df['event_date'].apply(_parse_date_robust)
            
        elif file_type == 'REAC':
            # Reactions normalization
            norm_df['case_id'] = _normalize_column(df, 'case_id', COLUMN_MAPPINGS['case_id'])
            norm_df['reaction_pt'] = _normalize_column(df, 'reaction_pt', COLUMN_MAPPINGS['reaction_pt'])
            
            # Normalize reaction PT to uppercase
            norm_df['reaction_pt'] = norm_df['reaction_pt'].str.upper().str.strip()
            
        elif file_type == 'DRUG':
            # Drug normalization
            norm_df['case_id'] = _normalize_column(df, 'case_id', COLUMN_MAPPINGS['case_id'])
            norm_df['drug'] = _normalize_column(df, 'drug', COLUMN_MAPPINGS['drug'])
            
            # Normalize drug names
            norm_df['drug'] = (norm_df['drug'].str.upper()
                             .str.strip()
                             .str.replace(r'\s+', ' ', regex=True))
            
        elif file_type in ['OUTC', 'THER', 'INDI']:
            # Other files - just normalize case_id
            norm_df['case_id'] = _normalize_column(df, 'case_id', COLUMN_MAPPINGS['case_id'])
            
            # Add serious indicator if this is OUTC
            if file_type == 'OUTC':
                norm_df['serious'] = _normalize_column(df, 'serious', COLUMN_MAPPINGS['serious'])
                # Normalize serious flag
                norm_df['serious'] = norm_df['serious'].str.upper().map(SERIOUS_MAPPING).fillna(False)
        
        normalized[file_type] = norm_df
        logger.info(f"Normalized {file_type}: {len(norm_df)} rows")
    
    return normalized

def build_events(df_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Build consolidated adverse events dataset from normalized FAERS tables.
    
    Args:
        df_dict: Dictionary of normalized DataFrames
        
    Returns:
        Consolidated events DataFrame
    """
    if 'DEMO' not in df_dict or 'REAC' not in df_dict:
        logger.error("Missing required tables: DEMO and REAC are mandatory")
        return pd.DataFrame()
    
    logger.info("Building consolidated events dataset")
    
    # Start with demographics
    events = df_dict['DEMO'][['case_id', 'sex', 'age', 'country', 'event_date']].copy()
    initial_demo_count = len(events)
    
    # Join with reactions (required)
    reactions = df_dict['REAC'][['case_id', 'reaction_pt']].copy()
    logger.info(f"Input tables: DEMO ({initial_demo_count:,} rows), REAC ({len(reactions):,} rows)")
    
    # Analyze key overlap before join
    _analyze_key_overlap(events, reactions, 'case_id', 'DEMO', 'REAC')
    
    events = events.merge(reactions, on='case_id', how='inner')
    _log_join_stats(initial_demo_count, len(events), "DEMO with REAC", "REAC", "inner")
    
    # Join with drugs if available
    if 'DRUG' in df_dict and not df_dict['DRUG'].empty:
        drugs = df_dict['DRUG'][['case_id', 'drug']].copy()
        _analyze_key_overlap(events, drugs, 'case_id', 'EVENTS', 'DRUG')
        before_drug_join = len(events)
        events = events.merge(drugs, on='case_id', how='left')
        _log_join_stats(before_drug_join, len(events), "EVENTS with DRUG", "DRUG", "left")
    else:
        events['drug'] = 'UNKNOWN'
        logger.warning("No DRUG table available, setting drug to 'UNKNOWN'")
    
    # Join with outcomes for serious flag if available
    if 'OUTC' in df_dict and not df_dict['OUTC'].empty:
        outcomes = df_dict['OUTC'][['case_id', 'serious']].copy()
        # Take the most serious outcome per case
        outcomes_serious = outcomes.groupby('case_id')['serious'].max().reset_index()
        _analyze_key_overlap(events, outcomes_serious, 'case_id', 'EVENTS', 'OUTC')
        before_outcome_join = len(events)
        events = events.merge(outcomes_serious, on='case_id', how='left')
        _log_join_stats(before_outcome_join, len(events), "EVENTS with OUTC", "OUTC", "left")
    
    if 'serious' not in events.columns:
        events['serious'] = False
        logger.warning("No serious flag available, setting all to False")
    
    # Clean up the data
    before_cleanup = len(events)
    events = events.dropna(subset=['case_id', 'reaction_pt'])
    after_null_removal = len(events)
    
    if before_cleanup != after_null_removal:
        null_removed = before_cleanup - after_null_removal
        null_percent = (null_removed / before_cleanup) * 100
        logger.info(f"Removed {null_removed:,} records with null case_id or reaction_pt ({null_percent:.1f}%)")
    
    # Remove duplicates
    events = events.drop_duplicates(subset=['case_id', 'drug', 'reaction_pt', 'event_date'])
    after_dedup = len(events)
    
    if after_null_removal != after_dedup:
        duplicates_removed = after_null_removal - after_dedup
        dup_percent = (duplicates_removed / after_null_removal) * 100
        logger.info(f"Removed {duplicates_removed:,} duplicate records ({dup_percent:.1f}%)")
    
    # Overall data pipeline summary
    total_loss = initial_demo_count - after_dedup
    total_loss_percent = (total_loss / initial_demo_count) * 100 if initial_demo_count > 0 else 0
    
    logger.info("="*50)
    logger.info("DATA PIPELINE SUMMARY")
    logger.info("="*50)
    logger.info(f"Starting DEMO records:     {initial_demo_count:,}")
    logger.info(f"Final consolidated events: {after_dedup:,}")
    logger.info(f"Total records lost:        {total_loss:,} ({total_loss_percent:.1f}%)")
    
    high_threshold = FAERS_CONFIG.get('total_loss_high_threshold', 30.0)
    moderate_threshold = FAERS_CONFIG.get('total_loss_moderate_threshold', 15.0)
    
    if total_loss_percent > high_threshold:
        logger.warning(f"HIGH OVERALL DATA LOSS: {total_loss_percent:.1f}% of initial records lost")
    elif total_loss_percent > moderate_threshold:
        logger.warning(f"Moderate overall data loss: {total_loss_percent:.1f}% of initial records lost")
    else:
        logger.info(f"Acceptable data retention: {100-total_loss_percent:.1f}% of records preserved")
    
    logger.info("="*50)
    
    # Reorder columns
    column_order = ['event_date', 'case_id', 'drug', 'reaction_pt', 'sex', 'age', 'country', 'serious']
    events = events.reindex(columns=column_order)
    
    logger.info(f"Final events dataset ready: {len(events):,} records with {len(events.columns)} columns")
    
    return events

def load_quarter_data(quarter_folder: Path) -> pd.DataFrame:
    """
    Load and process data from a single FAERS quarter folder.
    
    Args:
        quarter_folder: Path to the quarter folder
        
    Returns:
        Processed events DataFrame for this quarter
    """
    try:
        # Load ASCII files
        df_dict = load_faers_ascii(quarter_folder)
        
        if not df_dict:
            logger.warning(f"No data loaded from {quarter_folder}")
            return pd.DataFrame()
        
        # Check for required files
        if 'REAC' not in df_dict:
            logger.warning(f"Missing REAC file in {quarter_folder}, skipping")
            return pd.DataFrame()
        
        # Normalize schema
        normalized_dict = normalize_faers_schema(df_dict)
        
        # Build events
        events = build_events(normalized_dict)
        
        return events
        
    except Exception as e:
        logger.error(f"Failed to process quarter {quarter_folder}: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        raw_dir = sys.argv[1]
    else:
        raw_dir = "data/raw"
    
    quarters = discover_quarters(raw_dir)
    
    for quarter in quarters[:1]:  # Process first quarter as example
        print(f"\nProcessing {quarter}")
        events = load_quarter_data(quarter)
        print(f"Loaded {len(events)} events")
        if not events.empty:
            print(events.head())
