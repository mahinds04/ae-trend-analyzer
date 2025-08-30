# Lightweight Dockerfile for AE Trend Analyzer dashboard
# Usage:
#   docker build -t ae-trend-analyzer .
#   docker run -p 8501:8501 --env AE_SAMPLE=1 ae-trend-analyzer

FROM python:3.11-slim AS base

# Prevent Python from writing .pyc files and enable buffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Set work directory
WORKDIR /app

# System dependencies (add others as needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifest first (better layer caching)
COPY requirements.txt ./

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY src ./src
COPY run_dashboard.py ./
COPY data/processed/_samples ./data/processed/_samples
COPY README.md ./

# Expose Streamlit default port
EXPOSE 8501

# Default environment: demo mode
ENV AE_SAMPLE=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    PYTHONPATH=/app/src

# Create a non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Streamlit entrypoint
ENTRYPOINT ["python", "run_dashboard.py", "--sample"]
