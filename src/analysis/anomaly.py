"""
Anomaly Detection Module for AE Trend Analyzer

This module provides robust spike detection utilities using various methods:
- Rolling Z-score for trend-based anomaly detection
- STL decomposition for seasonal anomaly detection  
- Prophet for advanced time series anomaly detection (optional)

Methods handle missing data gracefully and provide consistent output schemas.
"""

import pandas as pd
import numpy as np
from typing import Optional, Union
import warnings
from datetime import datetime

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


def ensure_monthly_index(df: pd.DataFrame, date_col: str, value_col: str) -> pd.Series:
    """
    Ensure continuous monthly DatetimeIndex series with missing months filled as 0.
    
    Args:
        df: DataFrame with date and value columns
        date_col: Name of the date column
        value_col: Name of the value column
        
    Returns:
        Series indexed by monthly start dates with continuous timeline
    """
    if df.empty:
        return pd.Series(dtype=float, name=value_col)
    
    # Convert date column to datetime and extract month start
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df['month_start'] = df[date_col].dt.to_period('M').dt.start_time
    
    # Group by month and sum values (in case of duplicates)
    monthly_data = df.groupby('month_start')[value_col].sum()
    
    # Create continuous monthly range
    if len(monthly_data) > 0:
        full_range = pd.date_range(
            start=monthly_data.index.min(),
            end=monthly_data.index.max(),
            freq='MS'  # Month start frequency
        )
        
        # Reindex to fill missing months with 0
        monthly_data = monthly_data.reindex(full_range, fill_value=0)
    
    return monthly_data


def rolling_zscore(series: pd.Series, window: int = 6, z_thresh: float = 2.0) -> pd.DataFrame:
    """
    Compute rolling Z-score anomaly detection.
    
    Args:
        series: Time series data (should be indexed by dates)
        window: Rolling window size in months (default: 6)
        z_thresh: Z-score threshold for spike detection (default: 2.0)
        
    Returns:
        DataFrame with columns [value, mean, std, z, is_spike]
    """
    if series.empty or len(series) < window:
        return pd.DataFrame(columns=['value', 'mean', 'std', 'z', 'is_spike'])
    
    # Compute rolling statistics
    rolling_mean = series.rolling(window=window, min_periods=1).mean()
    rolling_std = series.rolling(window=window, min_periods=1).std()
    
    # Handle case where std is 0 (no variation)
    rolling_std = rolling_std.fillna(0)
    rolling_std = rolling_std.replace(0, np.nan)
    
    # Compute Z-scores
    z_scores = (series - rolling_mean) / rolling_std
    z_scores = z_scores.fillna(0)  # Fill NaN with 0 (no anomaly)
    
    # Identify spikes
    is_spike = np.abs(z_scores) > z_thresh
    
    result = pd.DataFrame({
        'value': series,
        'mean': rolling_mean,
        'std': rolling_std.fillna(0),
        'z': z_scores,
        'is_spike': is_spike
    }, index=series.index)
    
    return result


def stl_spikes(series: pd.Series, period: int = 12, z_thresh: float = 2.5) -> pd.DataFrame:
    """
    Compute STL decomposition-based anomaly detection.
    
    Args:
        series: Time series data (should be indexed by dates)
        period: Seasonal period (default: 12 for monthly data)
        z_thresh: Z-score threshold for spike detection (default: 2.5)
        
    Returns:
        DataFrame with columns [value, trend, seasonal, resid, z, is_spike]
    """
    if series.empty or len(series) < period * 2:
        return pd.DataFrame(columns=['value', 'trend', 'seasonal', 'resid', 'z', 'is_spike'])
    
    try:
        from statsmodels.tsa.seasonal import STL
        
        # Perform STL decomposition
        stl = STL(series, period=period, robust=True)
        decomposition = stl.fit()
        
        # Extract components
        trend = decomposition.trend
        seasonal = decomposition.seasonal
        resid = decomposition.resid
        
        # Compute Z-scores on residuals
        resid_mean = resid.mean()
        resid_std = resid.std()
        
        if resid_std == 0 or np.isnan(resid_std):
            z_scores = pd.Series(0, index=series.index)
        else:
            z_scores = (resid - resid_mean) / resid_std
        
        # Identify spikes
        is_spike = np.abs(z_scores) > z_thresh
        
        result = pd.DataFrame({
            'value': series,
            'trend': trend,
            'seasonal': seasonal,
            'resid': resid,
            'z': z_scores,
            'is_spike': is_spike
        }, index=series.index)
        
        return result
        
    except ImportError:
        raise ImportError(
            "statsmodels is required for STL decomposition. "
            "Install with: pip install statsmodels"
        )
    except Exception as e:
        # Fallback to empty result if STL fails
        return pd.DataFrame(columns=['value', 'trend', 'seasonal', 'resid', 'z', 'is_spike'])


def prophet_spikes(series: pd.Series, z_thresh: float = 2.5) -> pd.DataFrame:
    """
    Compute Prophet-based anomaly detection (optional).
    
    Args:
        series: Time series data (should be indexed by dates)
        z_thresh: Z-score threshold for spike detection (default: 2.5)
        
    Returns:
        DataFrame with columns [value, trend, seasonal, resid, z, is_spike]
        
    Raises:
        ImportError: If Prophet is not installed
    """
    if series.empty or len(series) < 24:  # Need at least 2 years for Prophet
        return pd.DataFrame(columns=['value', 'trend', 'seasonal', 'resid', 'z', 'is_spike'])
    
    try:
        from prophet import Prophet
        
        # Prepare data for Prophet
        df_prophet = pd.DataFrame({
            'ds': series.index,
            'y': series.values
        })
        
        # Fit Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode='additive'
        )
        
        # Suppress Prophet logging
        import logging
        logging.getLogger('prophet').setLevel(logging.WARNING)
        
        model.fit(df_prophet)
        
        # Make predictions
        forecast = model.predict(df_prophet)
        
        # Extract components
        trend = pd.Series(forecast['trend'].values, index=series.index)
        seasonal = pd.Series(forecast['yearly'].values, index=series.index)
        predicted = pd.Series(forecast['yhat'].values, index=series.index)
        
        # Compute residuals
        resid = series - predicted
        
        # Compute Z-scores on residuals
        resid_mean = resid.mean()
        resid_std = resid.std()
        
        if resid_std == 0 or np.isnan(resid_std):
            z_scores = pd.Series(0, index=series.index)
        else:
            z_scores = (resid - resid_mean) / resid_std
        
        # Identify spikes
        is_spike = np.abs(z_scores) > z_thresh
        
        result = pd.DataFrame({
            'value': series,
            'trend': trend,
            'seasonal': seasonal,
            'resid': resid,
            'z': z_scores,
            'is_spike': is_spike
        }, index=series.index)
        
        return result
        
    except ImportError:
        raise ImportError(
            "Prophet is required for Prophet-based anomaly detection. "
            "Install with: pip install prophet"
        )
    except Exception as e:
        # Fallback to empty result if Prophet fails
        return pd.DataFrame(columns=['value', 'trend', 'seasonal', 'resid', 'z', 'is_spike'])


def rank_spikes(df: pd.DataFrame, date_col: str, value_col: str, k: int = 3) -> pd.DataFrame:
    """
    Rank and return top-k spikes from anomaly detection results.
    
    Args:
        df: DataFrame with anomaly detection results
        date_col: Name of date column (or use index if empty string)
        value_col: Name of value column
        k: Number of top spikes to return (default: 3)
        
    Returns:
        DataFrame with columns [rank, date, value, z] for top-k spikes
    """
    if df.empty or 'is_spike' not in df.columns or 'z' not in df.columns:
        return pd.DataFrame(columns=['rank', 'date', 'value', 'z'])
    
    # Filter to spikes only
    spikes_df = df[df['is_spike']].copy()
    
    if spikes_df.empty:
        return pd.DataFrame(columns=['rank', 'date', 'value', 'z'])
    
    # Sort by absolute Z-score (descending)
    spikes_df['abs_z'] = np.abs(spikes_df['z'])
    spikes_df = spikes_df.sort_values('abs_z', ascending=False)
    
    # Take top k
    top_spikes = spikes_df.head(k).copy()
    
    # Prepare output
    if date_col and date_col in top_spikes.columns:
        dates = top_spikes[date_col]
    else:
        dates = top_spikes.index
    
    result = pd.DataFrame({
        'rank': range(1, len(top_spikes) + 1),
        'date': dates,
        'value': top_spikes[value_col],
        'z': top_spikes['z']
    })
    
    # Format dates as strings for display
    result['date'] = pd.to_datetime(result['date']).dt.strftime('%Y-%m-%d')
    
    return result.reset_index(drop=True)


def detect_anomalies(series: pd.Series, method: str = "stl", **kwargs) -> pd.DataFrame:
    """
    Unified anomaly detection interface with automatic fallbacks.
    
    Args:
        series: Time series data
        method: Detection method ("stl", "rolling_z", or "prophet")
        **kwargs: Additional parameters for the chosen method
        
    Returns:
        DataFrame with anomaly detection results and fallback notes
    """
    if series.empty:
        return pd.DataFrame(columns=['value', 'z', 'is_spike'])
    
    method = method.lower()
    
    try:
        if method == "stl":
            return stl_spikes(series, **kwargs)
        elif method == "rolling_z":
            return rolling_zscore(series, **kwargs)
        elif method == "prophet":
            return prophet_spikes(series, **kwargs)
        else:
            # Default to STL
            return stl_spikes(series, **kwargs)
            
    except ImportError as e:
        # Fallback to rolling Z-score if library not available
        return rolling_zscore(series, **kwargs)
    except Exception as e:
        # Fallback to rolling Z-score if method fails
        return rolling_zscore(series, **kwargs)
