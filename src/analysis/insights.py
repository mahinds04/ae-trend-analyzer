"""
Insights Module for AE Trend Analyzer

This module provides high-level functions to summarize anomaly detection results
and surface key insights about adverse event trends.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union
import warnings

from .anomaly import ensure_monthly_index, detect_anomalies, rank_spikes

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def summarize_top_spikes_overall(
    path: Union[str, Path] = "data/processed/monthly_counts.csv",
    method: str = "stl",
    k: int = 3
) -> Dict:
    """
    Summarize top spikes in overall adverse event counts.
    
    Args:
        path: Path to monthly counts CSV file
        method: Anomaly detection method ("stl", "rolling_z", or "prophet")
        k: Number of top spikes to return
        
    Returns:
        Dictionary with method, n_months, top_spikes list, and notes
    """
    try:
        # Load data
        df = pd.read_csv(path)
        
        if df.empty or len(df) < 2:
            return {
                "method": method,
                "n_months": 0,
                "top_spikes": [],
                "note": "Insufficient data available"
            }
        
        # Ensure monthly index
        series = ensure_monthly_index(df, 'ym', 'count')
        
        if series.empty or len(series) < 2:
            return {
                "method": method,
                "n_months": 0,
                "top_spikes": [],
                "note": "Insufficient data after processing"
            }
        
        # Detect anomalies
        anomaly_df = detect_anomalies(series, method=method)
        
        if anomaly_df.empty:
            return {
                "method": method,
                "n_months": len(series),
                "top_spikes": [],
                "note": f"No anomalies detected using {method} method"
            }
        
        # Rank spikes
        top_spikes_df = rank_spikes(anomaly_df, '', 'value', k=k)
        
        # Convert to list of dictionaries
        top_spikes = []
        for _, row in top_spikes_df.iterrows():
            top_spikes.append({
                "rank": int(row['rank']),
                "date": row['date'],
                "value": int(row['value']),
                "z": float(row['z'])
            })
        
        # Determine if fallback was used
        fallback_note = ""
        if method == "stl" and len(series) < 24:
            fallback_note = "Fallback to rolling Z-score (insufficient data for STL)"
        elif method == "prophet" and len(series) < 24:
            fallback_note = "Fallback to rolling Z-score (insufficient data for Prophet)"
        
        return {
            "method": method,
            "n_months": len(series),
            "top_spikes": top_spikes,
            "note": fallback_note if fallback_note else f"Anomaly detection using {method} method"
        }
        
    except Exception as e:
        return {
            "method": method,
            "n_months": 0,
            "top_spikes": [],
            "note": f"Error processing data: {str(e)}"
        }


def summarize_top_spikes_by_drug(
    path: Union[str, Path] = "data/processed/monthly_by_drug.csv",
    drug: Optional[str] = None,
    method: str = "stl",
    k: int = 3
) -> Dict:
    """
    Summarize top spikes for a specific drug.
    
    Args:
        path: Path to monthly by drug CSV file
        drug: Drug name to analyze (None for overall)
        method: Anomaly detection method ("stl", "rolling_z", or "prophet")
        k: Number of top spikes to return
        
    Returns:
        Dictionary with method, drug, n_months, top_spikes list, and notes
    """
    if not drug:
        return {
            "method": method,
            "drug": None,
            "n_months": 0,
            "top_spikes": [],
            "note": "No drug specified"
        }
    
    try:
        # Load data
        df = pd.read_csv(path)
        
        if df.empty:
            return {
                "method": method,
                "drug": drug,
                "n_months": 0,
                "top_spikes": [],
                "note": "No data available"
            }
        
        # Filter for specific drug
        drug_df = df[df['drug'] == drug].copy()
        
        if drug_df.empty:
            return {
                "method": method,
                "drug": drug,
                "n_months": 0,
                "top_spikes": [],
                "note": f"No data found for drug: {drug}"
            }
        
        # Ensure monthly index
        series = ensure_monthly_index(drug_df, 'ym', 'count')
        
        if series.empty or len(series) < 2:
            return {
                "method": method,
                "drug": drug,
                "n_months": 0,
                "top_spikes": [],
                "note": "Insufficient data after processing"
            }
        
        # Detect anomalies
        anomaly_df = detect_anomalies(series, method=method)
        
        if anomaly_df.empty:
            return {
                "method": method,
                "drug": drug,
                "n_months": len(series),
                "top_spikes": [],
                "note": f"No anomalies detected for {drug} using {method} method"
            }
        
        # Rank spikes
        top_spikes_df = rank_spikes(anomaly_df, '', 'value', k=k)
        
        # Convert to list of dictionaries
        top_spikes = []
        for _, row in top_spikes_df.iterrows():
            top_spikes.append({
                "rank": int(row['rank']),
                "date": row['date'],
                "value": int(row['value']),
                "z": float(row['z'])
            })
        
        # Determine if fallback was used
        fallback_note = ""
        if method == "stl" and len(series) < 24:
            fallback_note = "Fallback to rolling Z-score (insufficient data for STL)"
        elif method == "prophet" and len(series) < 24:
            fallback_note = "Fallback to rolling Z-score (insufficient data for Prophet)"
        
        return {
            "method": method,
            "drug": drug,
            "n_months": len(series),
            "top_spikes": top_spikes,
            "note": fallback_note if fallback_note else f"Anomaly detection for {drug} using {method} method"
        }
        
    except Exception as e:
        return {
            "method": method,
            "drug": drug,
            "n_months": 0,
            "top_spikes": [],
            "note": f"Error processing data for {drug}: {str(e)}"
        }


def summarize_top_spikes_by_reaction(
    path: Union[str, Path] = "data/processed/monthly_by_reaction.csv",
    reaction: Optional[str] = None,
    method: str = "stl",
    k: int = 3
) -> Dict:
    """
    Summarize top spikes for a specific reaction.
    
    Args:
        path: Path to monthly by reaction CSV file
        reaction: Reaction name to analyze (None for overall)
        method: Anomaly detection method ("stl", "rolling_z", or "prophet")
        k: Number of top spikes to return
        
    Returns:
        Dictionary with method, reaction, n_months, top_spikes list, and notes
    """
    if not reaction:
        return {
            "method": method,
            "reaction": None,
            "n_months": 0,
            "top_spikes": [],
            "note": "No reaction specified"
        }
    
    try:
        # Load data
        df = pd.read_csv(path)
        
        if df.empty:
            return {
                "method": method,
                "reaction": reaction,
                "n_months": 0,
                "top_spikes": [],
                "note": "No data available"
            }
        
        # Filter for specific reaction
        reaction_df = df[df['reaction_pt'] == reaction].copy()
        
        if reaction_df.empty:
            return {
                "method": method,
                "reaction": reaction,
                "n_months": 0,
                "top_spikes": [],
                "note": f"No data found for reaction: {reaction}"
            }
        
        # Ensure monthly index
        series = ensure_monthly_index(reaction_df, 'ym', 'count')
        
        if series.empty or len(series) < 2:
            return {
                "method": method,
                "reaction": reaction,
                "n_months": 0,
                "top_spikes": [],
                "note": "Insufficient data after processing"
            }
        
        # Detect anomalies
        anomaly_df = detect_anomalies(series, method=method)
        
        if anomaly_df.empty:
            return {
                "method": method,
                "reaction": reaction,
                "n_months": len(series),
                "top_spikes": [],
                "note": f"No anomalies detected for {reaction} using {method} method"
            }
        
        # Rank spikes
        top_spikes_df = rank_spikes(anomaly_df, '', 'value', k=k)
        
        # Convert to list of dictionaries
        top_spikes = []
        for _, row in top_spikes_df.iterrows():
            top_spikes.append({
                "rank": int(row['rank']),
                "date": row['date'],
                "value": int(row['value']),
                "z": float(row['z'])
            })
        
        # Determine if fallback was used
        fallback_note = ""
        if method == "stl" and len(series) < 24:
            fallback_note = "Fallback to rolling Z-score (insufficient data for STL)"
        elif method == "prophet" and len(series) < 24:
            fallback_note = "Fallback to rolling Z-score (insufficient data for Prophet)"
        
        return {
            "method": method,
            "reaction": reaction,
            "n_months": len(series),
            "top_spikes": top_spikes,
            "note": fallback_note if fallback_note else f"Anomaly detection for {reaction} using {method} method"
        }
        
    except Exception as e:
        return {
            "method": method,
            "reaction": reaction,
            "n_months": 0,
            "top_spikes": [],
            "note": f"Error processing data for {reaction}: {str(e)}"
        }


def get_spike_months(
    series: pd.Series,
    method: str = "stl"
) -> List[str]:
    """
    Get list of months identified as spikes for visualization overlay.
    
    Args:
        series: Time series data
        method: Anomaly detection method
        
    Returns:
        List of date strings (YYYY-MM-DD format) for spike months
    """
    try:
        if series.empty or len(series) < 2:
            return []
        
        # Detect anomalies
        anomaly_df = detect_anomalies(series, method=method)
        
        if anomaly_df.empty or 'is_spike' not in anomaly_df.columns:
            return []
        
        # Get spike dates
        spikes = anomaly_df[anomaly_df['is_spike']]
        
        if spikes.empty:
            return []
        
        # Format dates as strings
        spike_dates = pd.to_datetime(spikes.index).strftime('%Y-%m-%d').tolist()
        
        return spike_dates
        
    except Exception:
        return []


def format_spike_table(top_spikes: List[Dict]) -> pd.DataFrame:
    """
    Format top spikes list as a display-ready DataFrame.
    
    Args:
        top_spikes: List of spike dictionaries from summarize functions
        
    Returns:
        Formatted DataFrame ready for Streamlit display
    """
    if not top_spikes:
        return pd.DataFrame(columns=['Rank', 'Month', 'Count', 'Z-Score'])
    
    formatted_data = []
    for spike in top_spikes:
        formatted_data.append({
            'Rank': spike['rank'],
            'Month': spike['date'][:7],  # YYYY-MM format
            'Count': f"{spike['value']:,}",
            'Z-Score': f"{spike['z']:.2f}"
        })
    
    return pd.DataFrame(formatted_data)
