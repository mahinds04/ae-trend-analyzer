#!/usr/bin/env python3
"""
Debug script to identify the join key overlap issue in FAERS data processing.

This script will manually load and normalize DEMO and REAC data to understand
why there's 0% key overlap between the tables.
"""

import sys
from pathlib import Path
import pandas as pd
import logging
from typing import Dict, List

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / 'src'))

from config import COLUMN_MAPPINGS, FAERS_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _normalize_column(df: pd.DataFrame, target_col: str, source_cols: List[str]) -> pd.Series:
    """
    Normalize a column by finding the first available source column.
    """
    for col in source_cols:
        if col in df.columns:
            logger.info(f"Found column '{col}' for {target_col}")
            series = df[col].astype(str).str.strip()
            logger.info(f"Sample values: {series.head(3).tolist()}")
            return series
    
    # Return empty series if no matching column found
    logger.warning(f"No source column found for {target_col} in {source_cols}")
    return pd.Series(index=df.index, dtype=str)

def debug_single_quarter(quarter_path: Path):
    """Debug a single quarter's data loading and normalization."""
    
    logger.info(f"=== Debugging {quarter_path.name} ===")
    
    # Find ascii directory (could be ASCII or ascii)
    ascii_dir = None
    for subdir in quarter_path.iterdir():
        if subdir.is_dir() and subdir.name.lower() == 'ascii':
            ascii_dir = subdir
            break
    
    if not ascii_dir:
        logger.error(f"No ASCII directory found in {quarter_path}")
        return
    
    # Load DEMO and REAC files
    demo_file = None
    reac_file = None
    
    for file in ascii_dir.iterdir():
        if file.name.startswith('DEMO') and file.name.endswith('.txt'):
            demo_file = file
        elif file.name.startswith('REAC') and file.name.endswith('.txt'):
            reac_file = file
    
    if not demo_file or not reac_file:
        logger.error(f"Missing DEMO or REAC files in {ascii_dir}")
        return
    
    logger.info(f"Loading DEMO: {demo_file.name}")
    logger.info(f"Loading REAC: {reac_file.name}")
    
    # Load raw data with chunked reading
    demo_chunks = []
    reac_chunks = []
    
    try:
        # Load DEMO in chunks
        chunk_iter = pd.read_csv(
            demo_file, 
            sep='$', 
            chunksize=50000,
            encoding='utf-8',
            on_bad_lines='skip',
            dtype=str
        )
        
        for i, chunk in enumerate(chunk_iter):
            if i == 0:  # First chunk
                logger.info(f"DEMO columns: {list(chunk.columns)}")
                logger.info(f"DEMO first row sample: {chunk.iloc[0].to_dict()}")
            demo_chunks.append(chunk)
            if i >= 2:  # Limit to first 3 chunks for debugging
                break
        
        demo_df = pd.concat(demo_chunks, ignore_index=True)
        logger.info(f"DEMO loaded: {len(demo_df):,} rows")
        
        # Load REAC in chunks
        chunk_iter = pd.read_csv(
            reac_file, 
            sep='$', 
            chunksize=50000,
            encoding='utf-8',
            on_bad_lines='skip',
            dtype=str
        )
        
        for i, chunk in enumerate(chunk_iter):
            if i == 0:  # First chunk
                logger.info(f"REAC columns: {list(chunk.columns)}")
                logger.info(f"REAC first row sample: {chunk.iloc[0].to_dict()}")
            reac_chunks.append(chunk)
            if i >= 2:  # Limit to first 3 chunks for debugging
                break
        
        reac_df = pd.concat(reac_chunks, ignore_index=True)
        logger.info(f"REAC loaded: {len(reac_df):,} rows")
        
    except Exception as e:
        logger.error(f"Error loading files: {e}")
        return
    
    # Normalize case_id columns
    logger.info("\n=== Normalizing case_id columns ===")
    
    demo_case_id = _normalize_column(demo_df, 'case_id', COLUMN_MAPPINGS['case_id'])
    reac_case_id = _normalize_column(reac_df, 'case_id', COLUMN_MAPPINGS['case_id'])
    
    # Analyze overlap
    logger.info("\n=== Analyzing key overlap ===")
    
    demo_keys = set(demo_case_id.dropna().unique())
    reac_keys = set(reac_case_id.dropna().unique())
    
    overlap_keys = demo_keys.intersection(reac_keys)
    
    logger.info(f"DEMO unique keys: {len(demo_keys):,}")
    logger.info(f"REAC unique keys: {len(reac_keys):,}")
    logger.info(f"Overlapping keys: {len(overlap_keys):,}")
    
    if len(demo_keys) > 0:
        overlap_percent = (len(overlap_keys) / len(demo_keys)) * 100
        logger.info(f"Overlap percentage: {overlap_percent:.1f}%")
    
    # Sample keys for comparison
    logger.info(f"Sample DEMO keys: {list(demo_keys)[:5]}")
    logger.info(f"Sample REAC keys: {list(reac_keys)[:5]}")
    
    if len(overlap_keys) > 0:
        logger.info(f"Sample overlapping keys: {list(overlap_keys)[:5]}")
    else:
        logger.warning("No overlapping keys found!")
        
        # Detailed analysis of why no overlap
        logger.info("Investigating key mismatch...")
        
        # Check data types and formats
        demo_sample = demo_case_id.dropna().head(10)
        reac_sample = reac_case_id.dropna().head(10)
        
        logger.info(f"DEMO sample case_ids: {demo_sample.tolist()}")
        logger.info(f"REAC sample case_ids: {reac_sample.tolist()}")
        
        # Check if any DEMO keys are close to REAC keys
        demo_sample_set = set(demo_sample)
        reac_sample_set = set(reac_sample)
        
        logger.info("Looking for similar keys...")
        for demo_key in list(demo_sample_set)[:5]:
            for reac_key in list(reac_sample_set)[:5]:
                if demo_key == reac_key:
                    logger.info(f"MATCH: {demo_key} == {reac_key}")
                elif str(demo_key).strip() == str(reac_key).strip():
                    logger.info(f"MATCH after strip: '{demo_key}' == '{reac_key}'")

def main():
    """Main debugging function."""
    
    logger.info("Starting FAERS join key debugging...")
    
    # Test with 2013Q1 data
    base_dir = Path("data/raw")
    
    quarter_dirs = [
        base_dir / "faers_ascii_2013q1"
    ]
    
    for quarter_dir in quarter_dirs:
        if quarter_dir.exists():
            debug_single_quarter(quarter_dir)
        else:
            logger.warning(f"Quarter directory not found: {quarter_dir}")

if __name__ == "__main__":
    main()
