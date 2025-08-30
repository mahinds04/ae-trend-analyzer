"""
Example script showing how to run the AE Trend Analyzer pipeline.

This script demonstrates both individual module usage and the complete pipeline.
"""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def run_complete_pipeline():
    """Run the complete ETL pipeline."""
    print("Running complete AE Trend Analyzer pipeline...")
    print("="*60)
    
    try:
        # Import the main pipeline
        from etl.build_all import main
        
        # Run the pipeline
        main()
        
    except Exception as e:
        print(f"Pipeline error: {e}")
        print("\\nThis is expected if you don't have FAERS data in data/raw/")
        print("To run with real data:")
        print("1. Place FAERS quarterly folders in data/raw/")
        print("2. Place review datasets in data/raw/")
        print("3. Run: python -m src.etl.build_all")

def show_individual_usage():
    """Show how to use individual modules."""
    print("\\nIndividual module usage examples:")
    print("="*50)
    
    try:
        # FAERS loader example
        print("\\n1. FAERS Loader:")
        from etl.faers_loader import discover_quarters
        
        quarters = discover_quarters("data/raw")
        print(f"   Found {len(quarters)} quarterly folders")
        
        # Reviews loader example
        print("\\n2. Reviews Loader:")
        from etl.reviews_loader import AE_KEYWORDS, MEDDRA_MAPPING
        
        print(f"   Available AE keywords: {len(AE_KEYWORDS)}")
        print(f"   Sample keywords: {AE_KEYWORDS[:5]}")
        print(f"   MedDRA mappings: {len(MEDDRA_MAPPING)}")
        
        # Aggregation example
        print("\\n3. Aggregation Module:")
        from analysis.aggregate import monthly_overall
        
        print("   Functions available: monthly_overall, monthly_by_reaction, monthly_by_drug, save_plots")
        
        print("\\n✅ All modules loaded successfully!")
        
    except Exception as e:
        print(f"Error loading modules: {e}")

def main():
    """Main function."""
    print("AE TREND ANALYZER - USAGE EXAMPLES")
    print("="*60)
    
    # Show individual module usage
    show_individual_usage()
    
    # Try to run complete pipeline
    print("\\n" + "="*60)
    print("ATTEMPTING COMPLETE PIPELINE")
    print("="*60)
    
    run_complete_pipeline()
    
    print("\\n" + "="*60)
    print("USAGE SUMMARY")
    print("="*60)
    print("\\nTo run with your own data:")
    print("\\n1. Place FAERS data in data/raw/ following this structure:")
    print("   data/raw/faers_ascii_2024q1/ASCII/*.txt")
    print("   data/raw/faers_ascii_2024q2/ASCII/*.txt")
    print("   ... etc")
    print("\\n2. Place review datasets in data/raw/:")
    print("   data/raw/WebMD Drug Reviews Dataset/webmd.csv")
    print("   data/raw/UCI ML Drug Review Dataset/drugsComTrain_raw.csv")
    print("   data/raw/UCI ML Drug Review Dataset/drugsComTest_raw.csv")
    print("\\n3. Run the complete pipeline:")
    print("   python -m src.etl.build_all")
    print("\\n4. Or run the demo with sample data:")
    print("   python demo.py")
    print("\\nGenerated outputs will be in:")
    print("   📁 data/processed/ - Data files")
    print("   📁 reports/figures/ - Visualization plots")

if __name__ == "__main__":
    main()
