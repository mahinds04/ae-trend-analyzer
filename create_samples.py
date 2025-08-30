#!/usr/bin/env python3
"""
Generate sample data files for demo mode.
Creates ~50 row samples from full processed datasets.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def create_samples():
    """Create sample files with ~50 rows each spanning 3-4 months."""
    
    processed_dir = Path("data/processed")
    samples_dir = processed_dir / "_samples"
    samples_dir.mkdir(exist_ok=True)
    
    print("Creating sample data files...")
    
    # Load full datasets
    try:
        # Main events dataset
        if (processed_dir / "faers_events.parquet").exists():
            df_events = pd.read_parquet(processed_dir / "faers_events.parquet")
            
            # Sample 50 rows across 3-4 months
            if len(df_events) > 50:
                # Get date range and sample across months
                df_events['event_date'] = pd.to_datetime(df_events['event_date'])
                df_sample = df_events.sample(n=min(50, len(df_events))).sort_values('event_date')
                df_sample.to_parquet(samples_dir / "faers_events.sample.parquet", index=False)
                print(f"✓ Created faers_events.sample.parquet ({len(df_sample)} rows)")
            else:
                print("✓ Using existing small dataset for faers_events.sample.parquet")
                df_events.to_parquet(samples_dir / "faers_events.sample.parquet", index=False)
        
        # Monthly counts
        if (processed_dir / "monthly_counts.csv").exists():
            df_monthly = pd.read_csv(processed_dir / "monthly_counts.csv")
            # Take recent months
            df_sample = df_monthly.tail(12)  # Last 12 months
            df_sample.to_csv(samples_dir / "monthly_counts.sample.csv", index=False)
            print(f"✓ Created monthly_counts.sample.csv ({len(df_sample)} rows)")
        
        # Monthly by drug
        if (processed_dir / "monthly_by_drug.csv").exists():
            df_drug = pd.read_csv(processed_dir / "monthly_by_drug.csv")
            # Get top drugs from recent months
            recent_months = df_drug['ym'].nlargest(6).values  # Last 6 months
            df_recent = df_drug[df_drug['ym'].isin(recent_months)]
            top_drugs = df_recent.groupby('drug')['count'].sum().nlargest(10).index
            df_sample = df_recent[df_recent['drug'].isin(top_drugs)]
            df_sample = df_sample.head(50)
            df_sample.to_csv(samples_dir / "monthly_by_drug.sample.csv", index=False)
            print(f"✓ Created monthly_by_drug.sample.csv ({len(df_sample)} rows)")
        
        # Monthly by reaction
        if (processed_dir / "monthly_by_reaction.csv").exists():
            df_reaction = pd.read_csv(processed_dir / "monthly_by_reaction.csv")
            # Get top reactions from recent months
            recent_months = df_reaction['ym'].nlargest(6).values  # Last 6 months
            df_recent = df_reaction[df_reaction['ym'].isin(recent_months)]
            top_reactions = df_recent.groupby('reaction_pt')['count'].sum().nlargest(10).index
            df_sample = df_recent[df_recent['reaction_pt'].isin(top_reactions)]
            df_sample = df_sample.head(50)
            df_sample.to_csv(samples_dir / "monthly_by_reaction.sample.csv", index=False)
            print(f"✓ Created monthly_by_reaction.sample.csv ({len(df_sample)} rows)")
        
        print(f"\n✅ Sample files created in {samples_dir}")
        
    except Exception as e:
        print(f"❌ Error creating samples: {e}")
        print("Creating minimal demo samples...")
        
        # Create minimal demo data if full datasets don't exist
        create_minimal_samples(samples_dir)

def create_minimal_samples(samples_dir):
    """Create minimal sample data for testing."""
    
    # Minimal events data
    events_data = {
        'event_date': pd.date_range('2024-01-01', periods=50, freq='D'),
        'case_id': [f'CASE_{i:05d}' for i in range(1, 51)],
        'drug': ['ASPIRIN', 'IBUPROFEN', 'ACETAMINOPHEN'] * 17 + ['NAPROXEN'],
        'reaction_pt': ['HEADACHE', 'NAUSEA', 'DIZZINESS', 'FATIGUE'] * 13 + ['RASH', 'VOMITING'],
        'sex': ['M', 'F'] * 25,
        'age': np.random.randint(18, 80, 50),
        'country': ['US'] * 35 + ['CA'] * 10 + ['UK'] * 5,
        'serious': ['N'] * 40 + ['Y'] * 10
    }
    
    df_events = pd.DataFrame(events_data)
    df_events.to_parquet(samples_dir / "faers_events.sample.parquet", index=False)
    
    # Monthly counts
    monthly_data = {
        'ym': ['2024-01', '2024-02', '2024-03', '2024-04'],
        'count': [1250, 1180, 1340, 1290]
    }
    pd.DataFrame(monthly_data).to_csv(samples_dir / "monthly_counts.sample.csv", index=False)
    
    # Monthly by drug  
    drug_data = {
        'ym': ['2024-01'] * 3 + ['2024-02'] * 3 + ['2024-03'] * 3,
        'drug': ['ASPIRIN', 'IBUPROFEN', 'ACETAMINOPHEN'] * 3,
        'count': [145, 132, 98, 156, 128, 104, 167, 139, 112]
    }
    pd.DataFrame(drug_data).to_csv(samples_dir / "monthly_by_drug.sample.csv", index=False)
    
    # Monthly by reaction
    reaction_data = {
        'ym': ['2024-01'] * 4 + ['2024-02'] * 4 + ['2024-03'] * 4,
        'reaction_pt': ['HEADACHE', 'NAUSEA', 'DIZZINESS', 'FATIGUE'] * 3,
        'count': [89, 76, 54, 43, 92, 71, 58, 47, 95, 78, 61, 51]
    }
    pd.DataFrame(reaction_data).to_csv(samples_dir / "monthly_by_reaction.sample.csv", index=False)
    
    print("✅ Created minimal demo samples")

if __name__ == "__main__":
    create_samples()
