"""
Drug Reviews Loader Module

This module provides functionality to load drug review datasets (WebMD and UCI),
extract adverse event terms using NLP techniques, and map them to MedDRA preferred terms.
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
from datetime import datetime

import pandas as pd
import numpy as np
from tqdm import tqdm

# Import configuration - handle both relative and absolute imports
try:
    from ..config import AE_KEYWORDS, MEDDRA_MAPPING, LOGGING_CONFIG
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import AE_KEYWORDS, MEDDRA_MAPPING, LOGGING_CONFIG

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format']
)
logger = logging.getLogger(__name__)

def load_webmd(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Load WebMD drug reviews dataset.
    
    Args:
        file_path: Path to the WebMD CSV file
        
    Returns:
        DataFrame with standardized columns
    """
    logger.info(f"Loading WebMD reviews from {file_path}")
    
    try:
        # Fix pandas compatibility - use on_bad_lines instead of errors for newer pandas
        try:
            df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
        except TypeError:
            # Fallback for older pandas versions
            df = pd.read_csv(file_path, encoding='utf-8', error_bad_lines=False, warn_bad_lines=False)
        
        # Standardize column names (adjust based on actual WebMD schema)
        column_mapping = {
            'drugName': 'drug',
            'Drug': 'drug',
            'drug_name': 'drug',
            'review': 'review_text',
            'Review': 'review_text',
            'comment': 'review_text',
            'text': 'review_text',
            'date': 'review_date',
            'Date': 'review_date',
            'reviewDate': 'review_date',
            'condition': 'condition',
            'Condition': 'condition',
            'indication': 'condition',
            'rating': 'rating',
            'Rating': 'rating',
            'overall_rating': 'rating'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Ensure required columns exist
        required_cols = ['drug', 'review_text']
        for col in required_cols:
            if col not in df.columns:
                logger.warning(f"Required column '{col}' not found in WebMD data")
                df[col] = ''
        
        # Clean text data
        if 'review_text' in df.columns:
            df['review_text'] = df['review_text'].astype(str).str.lower().str.strip()
        
        if 'drug' in df.columns:
            df['drug'] = df['drug'].astype(str).str.upper().str.strip()
        
        # Add source identifier
        df['source'] = 'WebMD'
        
        # Parse dates if available
        if 'review_date' in df.columns:
            df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')
        
        logger.info(f"Loaded {len(df)} WebMD reviews")
        return df
        
    except Exception as e:
        logger.error(f"Failed to load WebMD data: {e}")
        return pd.DataFrame()

def load_uci(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Load UCI drug reviews dataset.
    
    Args:
        file_path: Path to the UCI CSV file (train or test)
        
    Returns:
        DataFrame with standardized columns
    """
    logger.info(f"Loading UCI reviews from {file_path}")
    
    try:
        # Fix pandas compatibility - use on_bad_lines instead of errors for newer pandas
        try:
            df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
        except TypeError:
            # Fallback for older pandas versions
            df = pd.read_csv(file_path, encoding='utf-8', error_bad_lines=False, warn_bad_lines=False)
        
        # UCI dataset typical columns: drugName, condition, review, rating, date, usefulCount
        column_mapping = {
            'drugName': 'drug',
            'Drug': 'drug',
            'review': 'review_text',
            'Review': 'review_text',
            'condition': 'condition',
            'Condition': 'condition',
            'rating': 'rating',
            'Rating': 'rating',
            'date': 'review_date',
            'Date': 'review_date',
            'usefulCount': 'useful_count'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Ensure required columns exist
        required_cols = ['drug', 'review_text']
        for col in required_cols:
            if col not in df.columns:
                logger.warning(f"Required column '{col}' not found in UCI data")
                df[col] = ''
        
        # Clean text data
        if 'review_text' in df.columns:
            df['review_text'] = df['review_text'].astype(str).str.lower().str.strip()
        
        if 'drug' in df.columns:
            df['drug'] = df['drug'].astype(str).str.upper().str.strip()
        
        # Add source identifier
        df['source'] = 'UCI'
        
        # Parse dates if available
        if 'review_date' in df.columns:
            df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')
        
        logger.info(f"Loaded {len(df)} UCI reviews")
        return df
        
    except Exception as e:
        logger.error(f"Failed to load UCI data: {e}")
        return pd.DataFrame()

def extract_terms(df: pd.DataFrame, keywords: List[str] = None) -> pd.DataFrame:
    """
    Extract adverse event terms from review text using keyword matching.
    
    Args:
        df: DataFrame with review_text column
        keywords: List of AE keywords to search for (default: AE_KEYWORDS)
        
    Returns:
        DataFrame with extracted_terms column added
    """
    if keywords is None:
        keywords = AE_KEYWORDS
    
    logger.info(f"Extracting AE terms from {len(df)} reviews using {len(keywords)} keywords")
    
    df = df.copy()
    extracted_terms = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Extracting terms"):
        review_text = str(row.get('review_text', ''))
        if not review_text or review_text == 'nan':
            extracted_terms.append([])
            continue
        
        # Clean and normalize text
        clean_text = re.sub(r'[^\w\s]', ' ', review_text.lower())
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Find matching keywords
        found_terms = set()
        
        for keyword in keywords:
            # Simple substring matching
            if keyword.lower() in clean_text:
                found_terms.add(keyword.lower())
            
            # Handle multi-word keywords
            if ' ' in keyword:
                if keyword.lower() in clean_text:
                    found_terms.add(keyword.lower())
            
            # Handle variations (simple stemming)
            variations = _get_keyword_variations(keyword)
            for variation in variations:
                if variation.lower() in clean_text:
                    found_terms.add(keyword.lower())  # Store original keyword
        
        extracted_terms.append(list(found_terms))
    
    df['extracted_terms'] = extracted_terms
    
    # Count statistics
    total_terms = sum(len(terms) for terms in extracted_terms)
    reviews_with_terms = sum(1 for terms in extracted_terms if terms)
    
    logger.info(f"Extracted {total_terms} terms from {reviews_with_terms}/{len(df)} reviews")
    
    return df

def _get_keyword_variations(keyword: str) -> List[str]:
    """
    Generate simple variations of a keyword for better matching.
    
    Args:
        keyword: Base keyword
        
    Returns:
        List of keyword variations
    """
    variations = [keyword]
    
    # Add plural/singular variations
    if keyword.endswith('s') and len(keyword) > 3:
        variations.append(keyword[:-1])  # Remove 's'
    elif not keyword.endswith('s'):
        variations.append(keyword + 's')  # Add 's'
    
    # Add common suffixes
    suffixes = ['ing', 'ed', 'er', 'ly']
    for suffix in suffixes:
        if keyword.endswith(suffix):
            variations.append(keyword[:-len(suffix)])
        else:
            variations.append(keyword + suffix)
    
    # Handle common word variations
    word_variations = {
        'pain': ['painful', 'aching', 'hurt', 'hurting'],
        'tired': ['exhausted', 'fatigued', 'weary'],
        'sick': ['ill', 'unwell', 'nauseous'],
        'dizzy': ['lightheaded', 'vertigo'],
        'sad': ['depressed', 'down', 'blue'],
        'anxious': ['worried', 'nervous', 'stressed']
    }
    
    if keyword in word_variations:
        variations.extend(word_variations[keyword])
    
    return list(set(variations))

def map_terms_to_pt(df: pd.DataFrame, meddra_lookup: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Map extracted terms to MedDRA Preferred Terms.
    
    Args:
        df: DataFrame with extracted_terms column
        meddra_lookup: Dictionary mapping terms to MedDRA PTs (default: MEDDRA_MAPPING)
        
    Returns:
        DataFrame with mapped_pt column added
    """
    if meddra_lookup is None:
        meddra_lookup = MEDDRA_MAPPING
    
    logger.info(f"Mapping terms to MedDRA PTs for {len(df)} reviews")
    
    df = df.copy()
    mapped_pts = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Mapping to MedDRA"):
        extracted_terms = row.get('extracted_terms', [])
        if not extracted_terms:
            mapped_pts.append([])
            continue
        
        # Map each term to MedDRA PT
        pts = set()
        for term in extracted_terms:
            # Direct mapping
            if term in meddra_lookup:
                pts.add(meddra_lookup[term])
            
            # Fuzzy matching for compound terms
            for key, pt in meddra_lookup.items():
                if key in term or term in key:
                    pts.add(pt)
        
        mapped_pts.append(list(pts))
    
    df['mapped_pt'] = mapped_pts
    
    # Count statistics
    total_mapped = sum(len(pts) for pts in mapped_pts)
    reviews_with_mapped = sum(1 for pts in mapped_pts if pts)
    
    logger.info(f"Mapped {total_mapped} PTs from {reviews_with_mapped}/{len(df)} reviews")
    
    return df

def add_year_month(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add year-month column for time series analysis.
    
    Args:
        df: DataFrame with review_date column
        
    Returns:
        DataFrame with ym (year-month) column added
    """
    df = df.copy()
    
    if 'review_date' in df.columns:
        # Convert to first day of month
        df['ym'] = df['review_date'].dt.to_period('M').dt.start_time
    else:
        # If no date available, set to NaT
        df['ym'] = pd.NaT
        logger.warning("No review_date column found, setting ym to NaT")
    
    return df

def load_all_reviews(webmd_path: Optional[Union[str, Path]] = None,
                    uci_train_path: Optional[Union[str, Path]] = None,
                    uci_test_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """
    Load all review datasets and combine them.
    
    Args:
        webmd_path: Path to WebMD CSV file
        uci_train_path: Path to UCI training CSV file
        uci_test_path: Path to UCI test CSV file
        
    Returns:
        Combined DataFrame with all reviews
    """
    dfs = []
    
    # Load WebMD data
    if webmd_path and Path(webmd_path).exists():
        webmd_df = load_webmd(webmd_path)
        if not webmd_df.empty:
            dfs.append(webmd_df)
    
    # Load UCI training data
    if uci_train_path and Path(uci_train_path).exists():
        uci_train_df = load_uci(uci_train_path)
        if not uci_train_df.empty:
            dfs.append(uci_train_df)
    
    # Load UCI test data
    if uci_test_path and Path(uci_test_path).exists():
        uci_test_df = load_uci(uci_test_path)
        if not uci_test_df.empty:
            dfs.append(uci_test_df)
    
    if not dfs:
        logger.warning("No review data loaded")
        return pd.DataFrame()
    
    # Combine all datasets
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Remove duplicates based on drug and review text
    initial_count = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['drug', 'review_text'])
    final_count = len(combined_df)
    
    if initial_count != final_count:
        logger.info(f"Removed {initial_count - final_count} duplicate reviews")
    
    logger.info(f"Combined dataset: {len(combined_df)} reviews from {len(dfs)} sources")
    
    return combined_df

def process_reviews(webmd_path: Optional[Union[str, Path]] = None,
                   uci_train_path: Optional[Union[str, Path]] = None,
                   uci_test_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """
    Complete pipeline to load, extract terms, and map reviews.
    
    Args:
        webmd_path: Path to WebMD CSV file
        uci_train_path: Path to UCI training CSV file
        uci_test_path: Path to UCI test CSV file
        
    Returns:
        Processed DataFrame with extracted and mapped terms
    """
    logger.info("Starting review processing pipeline")
    
    # Load all reviews
    df = load_all_reviews(webmd_path, uci_train_path, uci_test_path)
    
    if df.empty:
        logger.error("No review data to process")
        return pd.DataFrame()
    
    # Extract terms
    df = extract_terms(df)
    
    # Map to MedDRA PTs
    df = map_terms_to_pt(df)
    
    # Add time component
    df = add_year_month(df)
    
    # Reorder columns
    output_cols = ['source', 'drug', 'review_text', 'extracted_terms', 'mapped_pt', 'ym']
    # Include additional columns if they exist
    for col in ['condition', 'rating', 'review_date']:
        if col in df.columns:
            output_cols.append(col)
    
    df = df.reindex(columns=[col for col in output_cols if col in df.columns])
    
    logger.info(f"Completed review processing: {len(df)} reviews")
    
    return df

if __name__ == "__main__":
    # Example usage
    import sys
    
    # Example paths (adjust as needed)
    webmd_path = "data/raw/WebMD Drug Reviews Dataset/webmd.csv"
    uci_train_path = "data/raw/UCI ML Drug Review Dataset/drugsComTrain_raw.csv"
    uci_test_path = "data/raw/UCI ML Drug Review Dataset/drugsComTest_raw.csv"
    
    # Process reviews
    processed_df = process_reviews(webmd_path, uci_train_path, uci_test_path)
    
    if not processed_df.empty:
        print(f"Processed {len(processed_df)} reviews")
        print(processed_df.head())
        
        # Show some statistics
        total_terms = processed_df['extracted_terms'].apply(len).sum()
        total_pts = processed_df['mapped_pt'].apply(len).sum()
        print(f"Total extracted terms: {total_terms}")
        print(f"Total mapped PTs: {total_pts}")
