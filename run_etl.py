#!/usr/bin/env python3
"""
Simple runner script for the AE Trend Analyzer ETL pipeline.
This script handles the import path setup and runs the main ETL process.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def main():
    """Run the ETL pipeline."""
    try:
        # Import and run the main ETL process
        from etl.build_all import main as etl_main
        etl_main()
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("Please ensure you're running from the project root directory.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Error running ETL pipeline: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
