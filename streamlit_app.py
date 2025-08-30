"""
Streamlit Cloud Entry Point for AE Trend Analyzer

This file serves as the main entry point for Streamlit Cloud deployment.
It automatically runs in sample mode to provide instant demo functionality.
"""

import os
import sys
from pathlib import Path

# Force sample mode for cloud deployment
os.environ['AE_SAMPLE'] = '1'

# Ensure proper path setup for cloud environment
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import and run the main dashboard
from src.app.streamlit_mvp import *
