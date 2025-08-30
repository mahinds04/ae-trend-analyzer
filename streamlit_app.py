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

# Set up paths
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Now execute the main streamlit app
if __name__ == "__main__":
    # Change to the source directory context
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(current_dir)
        
        # Execute the main app file
        with open("src/app/streamlit_mvp.py", "r", encoding="utf-8") as f:
            exec(f.read(), {"__file__": "src/app/streamlit_mvp.py"})
            
    except Exception as e:
        import streamlit as st
        st.error(f"Failed to load app: {e}")
        st.write("Debug info:")
        st.write(f"Current working directory: {os.getcwd()}")
        st.write(f"Original directory: {original_cwd}")
        st.write(f"Files in current dir: {list(Path('.').iterdir())}")
        
    finally:
        os.chdir(original_cwd)
else:
    # Direct execution context - execute the main app
    with open(current_dir / "src" / "app" / "streamlit_mvp.py", "r", encoding="utf-8") as f:
        exec(f.read())
