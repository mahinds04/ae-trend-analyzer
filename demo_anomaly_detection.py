#!/usr/bin/env python3
"""
Anomaly Detection Demo Script

This script demonstrates the anomaly detection capabilities of the AE Trend Analyzer.
It shows how to use the different detection methods and interpret results.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from analysis.anomaly import (
    rolling_zscore, 
    stl_spikes, 
    detect_anomalies, 
    ensure_monthly_index,
    rank_spikes
)
from analysis.insights import (
    summarize_top_spikes_overall,
    summarize_top_spikes_by_drug,
    format_spike_table
)

def create_demo_data():
    """Create synthetic time series with known spikes for demonstration."""
    print("🔧 Creating synthetic demo data...")
    
    # Generate 3 years of monthly data
    dates = pd.date_range('2021-01-01', periods=36, freq='MS')
    
    # Base trend: growing from 100 to 300 events per month
    trend = np.linspace(100, 300, len(dates))
    
    # Seasonal pattern: higher in winter months
    seasonal = 30 * np.sin(2 * np.pi * (np.arange(len(dates)) + 3) / 12)
    
    # Random noise
    np.random.seed(42)  # For reproducible results
    noise = np.random.normal(0, 10, len(dates))
    
    # Combine components
    values = trend + seasonal + noise
    
    # Inject known spikes at specific months
    spike_months = [8, 15, 28]  # Sept 2021, April 2022, May 2023
    spike_descriptions = [
        "Sept 2021: Product recall event",
        "April 2022: New safety alert issued", 
        "May 2023: Regulatory investigation"
    ]
    
    for month_idx in spike_months:
        values[month_idx] += np.random.uniform(80, 120)  # Add significant spike
    
    # Create series
    series = pd.Series(values.astype(int), index=dates, name='adverse_events')
    
    print(f"✅ Generated {len(series)} months of data with {len(spike_months)} known spikes")
    print(f"📅 Date range: {series.index.min().strftime('%Y-%m')} to {series.index.max().strftime('%Y-%m')}")
    print(f"📊 Value range: {series.min():,} to {series.max():,} events")
    
    return series, spike_months, spike_descriptions

def demo_rolling_zscore(series):
    """Demonstrate rolling Z-score anomaly detection."""
    print("\n" + "="*60)
    print("🔍 ROLLING Z-SCORE ANOMALY DETECTION")
    print("="*60)
    
    # Test different parameters
    configs = [
        {"window": 6, "z_thresh": 2.0, "desc": "Standard (6-month window, z>2.0)"},
        {"window": 3, "z_thresh": 1.5, "desc": "Sensitive (3-month window, z>1.5)"},
        {"window": 12, "z_thresh": 2.5, "desc": "Conservative (12-month window, z>2.5)"}
    ]
    
    for config in configs:
        print(f"\n📋 {config['desc']}")
        result = rolling_zscore(series, window=config['window'], z_thresh=config['z_thresh'])
        
        spikes = result[result['is_spike']]
        print(f"   🎯 Detected: {len(spikes)} spikes")
        
        if len(spikes) > 0:
            top_spike = spikes.loc[spikes['z'].abs().idxmax()]
            print(f"   🔥 Strongest spike: {top_spike.name.strftime('%Y-%m')} "
                  f"(value: {top_spike['value']:,}, z-score: {top_spike['z']:.2f})")

def demo_stl_decomposition(series):
    """Demonstrate STL decomposition anomaly detection."""
    print("\n" + "="*60)
    print("🌊 STL DECOMPOSITION ANOMALY DETECTION")
    print("="*60)
    
    try:
        result = stl_spikes(series, period=12, z_thresh=2.0)
        
        spikes = result[result['is_spike']]
        print(f"🎯 Detected: {len(spikes)} spikes using STL method")
        
        if len(spikes) > 0:
            print(f"📈 Components analysis:")
            print(f"   • Trend range: {result['trend'].min():.0f} to {result['trend'].max():.0f}")
            print(f"   • Seasonal amplitude: ±{result['seasonal'].abs().max():.0f}")
            print(f"   • Residual std: {result['resid'].std():.1f}")
            
            # Show top 3 spikes
            top_spikes = spikes.nlargest(3, 'z')
            print(f"\n🏆 Top 3 spikes:")
            for i, (date, row) in enumerate(top_spikes.iterrows(), 1):
                print(f"   {i}. {date.strftime('%Y-%m')}: "
                      f"value={row['value']:,}, z-score={row['z']:.2f}")
        
    except ImportError:
        print("❌ STL method requires statsmodels library")
        print("   Install with: pip install statsmodels")

def demo_unified_interface(series):
    """Demonstrate the unified anomaly detection interface."""
    print("\n" + "="*60)
    print("🔧 UNIFIED ANOMALY DETECTION INTERFACE")
    print("="*60)
    
    methods = ["rolling_z", "stl"]
    
    for method in methods:
        print(f"\n🔍 Testing method: {method.upper()}")
        
        try:
            result = detect_anomalies(series, method=method, z_thresh=2.0)
            
            if not result.empty and 'is_spike' in result.columns:
                spikes = result[result['is_spike']]
                print(f"   ✅ Success: {len(spikes)} spikes detected")
                
                if len(spikes) > 0:
                    top_spike = spikes.loc[spikes['z'].abs().idxmax()]
                    print(f"   🎯 Top spike: {top_spike.name.strftime('%Y-%m')} "
                          f"(z-score: {top_spike['z']:.2f})")
            else:
                print("   ⚠️  No spikes detected")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def demo_spike_ranking(series):
    """Demonstrate spike ranking functionality."""
    print("\n" + "="*60)
    print("🏆 SPIKE RANKING AND INSIGHTS")
    print("="*60)
    
    # Get anomaly results
    result = detect_anomalies(series, method="rolling_z", z_thresh=1.8)
    
    if not result.empty:
        # Rank spikes
        top_spikes = rank_spikes(result, '', 'value', k=5)
        
        if not top_spikes.empty:
            print(f"📊 Top {len(top_spikes)} spikes ranked by z-score:")
            print()
            
            # Format as table
            formatted_table = format_spike_table(top_spikes.to_dict('records'))
            print(formatted_table.to_string(index=False))
        else:
            print("🔍 No significant spikes found with current threshold")
    else:
        print("❌ Could not perform spike ranking")

def demo_real_data_insights():
    """Demonstrate insights on real FAERS data if available."""
    print("\n" + "="*60)
    print("📊 REAL DATA INSIGHTS (if available)")
    print("="*60)
    
    data_files = [
        "data/processed/monthly_counts.csv",
        "data/processed/monthly_by_drug.csv", 
        "data/processed/monthly_by_reaction.csv"
    ]
    
    for file_path in data_files:
        if Path(file_path).exists():
            print(f"\n📁 Found: {file_path}")
            
            if "monthly_counts" in file_path:
                try:
                    insights = summarize_top_spikes_overall(
                        path=file_path, 
                        method="rolling_z", 
                        k=3
                    )
                    
                    print(f"   🔍 Method: {insights['method']}")
                    print(f"   📅 Months analyzed: {insights['n_months']}")
                    print(f"   🎯 Spikes found: {len(insights['top_spikes'])}")
                    
                    if insights['top_spikes']:
                        print(f"   🏆 Top spike: {insights['top_spikes'][0]['date']} "
                              f"({insights['top_spikes'][0]['value']:,} events, "
                              f"z={insights['top_spikes'][0]['z']:.2f})")
                    
                    if insights.get('note'):
                        print(f"   📝 Note: {insights['note']}")
                        
                except Exception as e:
                    print(f"   ❌ Error analyzing {file_path}: {e}")
        else:
            print(f"❌ Not found: {file_path}")

def main():
    """Main demonstration function."""
    print("🚀 AE TREND ANALYZER - ANOMALY DETECTION DEMO")
    print("=" * 60)
    print("This demo showcases the anomaly detection capabilities")
    print("of the AE Trend Analyzer system.\n")
    
    # Create demo data
    series, spike_months, spike_descriptions = create_demo_data()
    
    # Run demonstrations
    demo_rolling_zscore(series)
    demo_stl_decomposition(series)
    demo_unified_interface(series)
    demo_spike_ranking(series)
    demo_real_data_insights()
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETED")
    print("="*60)
    print("💡 Key takeaways:")
    print("   • Rolling Z-score: Fast, works with any data length")
    print("   • STL: Best for seasonal data, requires ≥24 months")
    print("   • Unified interface handles fallbacks automatically")
    print("   • Dashboard integrates all methods with visual overlays")
    print()
    print("🚀 Next steps:")
    print("   • Run your Streamlit dashboard: streamlit run src/app/streamlit_mvp.py")
    print("   • Try different anomaly detection methods in the sidebar")
    print("   • Explore the Insights panel for automated spike analysis")
    print(f"   • Dashboard URL: http://localhost:8502")

if __name__ == "__main__":
    main()
