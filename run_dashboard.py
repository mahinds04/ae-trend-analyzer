#!/usr/bin/env python3
"""
Simple runner script for the Streamlit dashboard with sample mode support.
Usage: python run_dashboard.py [--sample]
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run the Streamlit dashboard."""
    # Add src directory to Python path
    src_dir = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_dir))
    
    # Check for sample mode
    sample_mode = "--sample" in sys.argv
    
    # Build streamlit command
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        str(src_dir / "app" / "streamlit_mvp.py")
    ]
    
    if sample_mode:
        cmd.append("--")
        cmd.append("--sample")
    
    # Set environment variable for sample mode
    env = {}
    if sample_mode:
        env["AE_SAMPLE"] = "1"
    
    try:
        print("🚀 Starting AE Trend Analyzer Dashboard...")
        if sample_mode:
            print("📊 Running in sample mode with demo data")
        
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    main()
