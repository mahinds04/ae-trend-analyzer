#!/usr/bin/env python3
"""
Simple debug script to check FAERS join keys.
"""

import pandas as pd
from pathlib import Path

def main():
    print("=== FAERS Join Key Debug ===")
    
    # Load a small sample of DEMO and REAC
    demo_path = Path("data/raw/faers_ascii_2013q1/ascii/DEMO13Q1.txt")
    reac_path = Path("data/raw/faers_ascii_2013q1/ascii/REAC13Q1.txt")
    
    print("Loading DEMO sample...")
    demo_df = pd.read_csv(demo_path, sep='$', nrows=1000, dtype=str, on_bad_lines='skip')
    print(f"DEMO columns: {list(demo_df.columns)}")
    print(f"DEMO rows: {len(demo_df)}")
    
    print("\nLoading REAC sample...")
    reac_df = pd.read_csv(reac_path, sep='$', nrows=1000, dtype=str, on_bad_lines='skip')
    print(f"REAC columns: {list(reac_df.columns)}")
    print(f"REAC rows: {len(reac_df)}")
    
    # Extract key columns
    demo_primaryid = demo_df['primaryid'].dropna().unique()
    demo_caseid = demo_df['caseid'].dropna().unique()
    reac_primaryid = reac_df['primaryid'].dropna().unique()
    reac_caseid = reac_df['caseid'].dropna().unique()
    
    print(f"\nDEMO primaryid unique values: {len(demo_primaryid)}")
    print(f"DEMO caseid unique values: {len(demo_caseid)}")
    print(f"REAC primaryid unique values: {len(reac_primaryid)}")
    print(f"REAC caseid unique values: {len(reac_caseid)}")
    
    # Check overlap using primaryid
    demo_primaryid_set = set(demo_primaryid)
    reac_primaryid_set = set(reac_primaryid)
    primaryid_overlap = demo_primaryid_set.intersection(reac_primaryid_set)
    
    print(f"\nPrimaryID overlap: {len(primaryid_overlap)} out of {len(demo_primaryid_set)}")
    print(f"Overlap percentage: {len(primaryid_overlap)/len(demo_primaryid_set)*100:.1f}%")
    
    # Check overlap using caseid
    demo_caseid_set = set(demo_caseid)
    reac_caseid_set = set(reac_caseid)
    caseid_overlap = demo_caseid_set.intersection(reac_caseid_set)
    
    print(f"\nCaseID overlap: {len(caseid_overlap)} out of {len(demo_caseid_set)}")
    print(f"Overlap percentage: {len(caseid_overlap)/len(demo_caseid_set)*100:.1f}%")
    
    # Sample values
    print(f"\nSample DEMO primaryid: {list(demo_primaryid)[:5]}")
    print(f"Sample REAC primaryid: {list(reac_primaryid)[:5]}")
    print(f"Sample DEMO caseid: {list(demo_caseid)[:5]}")
    print(f"Sample REAC caseid: {list(reac_caseid)[:5]}")
    
    if len(primaryid_overlap) > 0:
        print(f"\nSample overlapping primaryids: {list(primaryid_overlap)[:5]}")
    if len(caseid_overlap) > 0:
        print(f"Sample overlapping caseids: {list(caseid_overlap)[:5]}")

if __name__ == "__main__":
    main()
