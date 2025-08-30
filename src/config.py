"""
Configuration module for AE Trend Analyzer

This module contains centralized configuration constants including file paths,
directories, and other configurable parameters used throughout the project.
"""

from pathlib import Path
from typing import Dict, List

# Base project directory (parent of src/)
BASE_DIR = Path(__file__).parent.parent

# Core directory paths
RAW_DIR = BASE_DIR / 'data' / 'raw'
PROC_DIR = BASE_DIR / 'data' / 'processed'
FIG_DIR = BASE_DIR / 'reports' / 'figures'
REPORTS_DIR = BASE_DIR / 'reports'

# Ensure directories exist
def ensure_directories():
    """Create all necessary directories if they don't exist."""
    directories = [RAW_DIR, PROC_DIR, FIG_DIR, REPORTS_DIR]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# FAERS-specific configuration
FAERS_CONFIG = {
    'required_files': ['DEMO', 'REAC'],  # Minimum required files
    'optional_files': ['DRUG', 'OUTC', 'THER', 'INDI'],
    'quarterly_pattern': r'faers_ascii_\d{4}q[1-4]',  # Regex for quarter folders
    'max_file_size_mb': 1024,  # Warning threshold for large files (1GB)
    'chunk_size': 50000,       # Rows per chunk for large file reading
    'memory_optimization': True,  # Enable memory optimizations
    'join_loss_warning_threshold': 20.0,  # % loss to trigger HIGH warning
    'join_loss_moderate_threshold': 10.0,  # % loss to trigger moderate warning
    'key_overlap_warning_threshold': 80.0,  # % overlap below which to warn
    'total_loss_high_threshold': 30.0,     # % total loss for HIGH warning
    'total_loss_moderate_threshold': 15.0,  # % total loss for moderate warning
}

# Review datasets configuration
REVIEW_CONFIG = {
    'webmd_path': RAW_DIR / 'WebMD Drug Reviews Dataset' / 'webmd.csv',
    'uci_train_path': RAW_DIR / 'UCI ML Drug Review Dataset' / 'drugsComTrain_raw.csv',
    'uci_test_path': RAW_DIR / 'UCI ML Drug Review Dataset' / 'drugsComTest_raw.csv',
}

# Output file names
OUTPUT_FILES = {
    'faers_events': PROC_DIR / 'faers_events.parquet',
    'monthly_counts': PROC_DIR / 'monthly_counts.csv',
    'monthly_by_reaction': PROC_DIR / 'monthly_by_reaction.csv',
    'monthly_by_drug': PROC_DIR / 'monthly_by_drug.csv',
    'reviews_extracted': PROC_DIR / 'reviews_extracted.csv',
}

# Plot file names
PLOT_FILES = {
    'overall_trend': FIG_DIR / 'overall_trend.png',
    'top_reactions_bar': FIG_DIR / 'top_reactions_bar.png',
    'top_drugs_bar': FIG_DIR / 'top_drugs_bar.png',
    'top_reactions_trend': FIG_DIR / 'top_reactions_trend.png',
    'top_drugs_trend': FIG_DIR / 'top_drugs_trend.png',
    'summary_statistics': FIG_DIR / 'summary_statistics.png',
}

# Column mapping configuration
COLUMN_MAPPINGS = {
    'case_id': ['PRIMARYID', 'CASEID', 'primaryid', 'caseid'],
    'drug': ['DRUGNAME', 'MEDICINALPRODUCT', 'drugname', 'medicinalproduct'],
    'reaction_pt': ['PT', 'REACTIONMEDDRAPT', 'pt', 'reactionmeddrapt'],
    'sex': ['SEX', 'PATIENTSEX', 'sex', 'patientsex'],
    'age': ['AGE', 'AGE_YRS', 'age', 'age_yrs'],
    'country': ['OCCUR_COUNTRY', 'COUNTRY', 'occur_country', 'country'],
    'serious': ['SERIOUS', 'SERIOUSNESS', 'serious', 'seriousness'],
    'event_date': ['EVENT_DT', 'RECEIPTDATE', 'event_dt', 'receiptdate']
}

# Sex normalization mapping
SEX_MAPPING = {
    'M': 'M', 'MALE': 'M', 'm': 'M', 'male': 'M',
    'F': 'F', 'FEMALE': 'F', 'f': 'F', 'female': 'F',
    'U': 'UNK', 'UNKNOWN': 'UNK', 'UNK': 'UNK'
}

# Serious flag normalization mapping
SERIOUS_MAPPING = {
    '1': True, 'Y': True, 'YES': True, 'TRUE': True,
    '0': False, 'N': False, 'NO': False, 'FALSE': False
}

# Analysis configuration
ANALYSIS_CONFIG = {
    'top_n_default': 10,  # Default number of top items in analyses
    'plot_dpi': 300,      # Plot resolution
    'plot_figsize': (12, 8),  # Default figure size
}

# Adverse event keywords for review processing
AE_KEYWORDS = [
    'headache', 'nausea', 'dizziness', 'rash', 'fatigue', 'insomnia', 
    'diarrhea', 'constipation', 'vomiting', 'pain', 'cough', 'fever',
    'drowsy', 'sleepy', 'tired', 'weak', 'dizzy', 'lightheaded',
    'stomach', 'belly', 'abdominal', 'cramps', 'bloating', 'gas',
    'dry mouth', 'thirsty', 'blurred vision', 'blurry', 'vision',
    'weight gain', 'weight loss', 'appetite', 'hungry', 'swelling',
    'swollen', 'edema', 'shortness of breath', 'breathing', 'chest',
    'palpitations', 'racing heart', 'irregular heartbeat', 'anxiety',
    'depression', 'mood', 'irritable', 'angry', 'sad', 'crying',
    'skin', 'itchy', 'itch', 'hives', 'allergic', 'reaction',
    'memory', 'confusion', 'brain fog', 'concentration', 'focus',
    'muscle', 'joint', 'ache', 'sore', 'stiff', 'numbness', 'tingling'
]

# MedDRA PT mapping for reviews
MEDDRA_MAPPING = {
    'headache': 'HEADACHE',
    'nausea': 'NAUSEA',
    'dizziness': 'DIZZINESS',
    'dizzy': 'DIZZINESS',
    'lightheaded': 'DIZZINESS',
    'rash': 'RASH',
    'fatigue': 'FATIGUE',
    'tired': 'FATIGUE',
    'weak': 'FATIGUE',
    'insomnia': 'INSOMNIA',
    'sleepy': 'SOMNOLENCE',
    'drowsy': 'SOMNOLENCE',
    'diarrhea': 'DIARRHOEA',
    'constipation': 'CONSTIPATION',
    'vomiting': 'VOMITING',
    'pain': 'PAIN',
    'cough': 'COUGH',
    'fever': 'PYREXIA',
    'stomach': 'ABDOMINAL PAIN',
    'belly': 'ABDOMINAL PAIN',
    'abdominal': 'ABDOMINAL PAIN',
    'cramps': 'ABDOMINAL PAIN',
    'bloating': 'ABDOMINAL DISTENSION',
    'gas': 'FLATULENCE',
    'dry mouth': 'DRY MOUTH',
    'thirsty': 'THIRST',
    'blurred vision': 'VISION BLURRED',
    'blurry': 'VISION BLURRED',
    'vision': 'VISUAL IMPAIRMENT',
    'weight gain': 'WEIGHT INCREASED',
    'weight loss': 'WEIGHT DECREASED',
    'appetite': 'APPETITE DISORDER',
    'hungry': 'INCREASED APPETITE',
    'swelling': 'SWELLING',
    'swollen': 'SWELLING',
    'edema': 'OEDEMA',
    'shortness of breath': 'DYSPNOEA',
    'breathing': 'DYSPNOEA',
    'chest': 'CHEST PAIN',
    'palpitations': 'PALPITATIONS',
    'racing heart': 'TACHYCARDIA',
    'irregular heartbeat': 'ARRHYTHMIA',
    'anxiety': 'ANXIETY',
    'depression': 'DEPRESSION',
    'mood': 'MOOD ALTERED',
    'irritable': 'IRRITABILITY',
    'angry': 'ANGER',
    'sad': 'DEPRESSED MOOD',
    'crying': 'CRYING',
    'skin': 'SKIN DISORDER',
    'itchy': 'PRURITUS',
    'itch': 'PRURITUS',
    'hives': 'URTICARIA',
    'allergic': 'ALLERGY',
    'reaction': 'DRUG HYPERSENSITIVITY',
    'memory': 'MEMORY IMPAIRMENT',
    'confusion': 'CONFUSIONAL STATE',
    'brain fog': 'COGNITIVE DISORDER',
    'concentration': 'DISTURBANCE IN ATTENTION',
    'focus': 'DISTURBANCE IN ATTENTION',
    'muscle': 'MYALGIA',
    'joint': 'ARTHRALGIA',
    'ache': 'PAIN',
    'sore': 'PAIN',
    'stiff': 'MUSCLE RIGIDITY',
    'numbness': 'HYPOAESTHESIA',
    'tingling': 'PARAESTHESIA'
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

def get_all_paths() -> Dict[str, Path]:
    """
    Get all configured paths as a dictionary.
    
    Returns:
        Dictionary of path names to Path objects
    """
    paths = {
        'BASE_DIR': BASE_DIR,
        'RAW_DIR': RAW_DIR,
        'PROC_DIR': PROC_DIR,
        'FIG_DIR': FIG_DIR,
        'REPORTS_DIR': REPORTS_DIR,
    }
    
    # Add output files
    paths.update({f'OUTPUT_{k.upper()}': v for k, v in OUTPUT_FILES.items()})
    
    # Add plot files
    paths.update({f'PLOT_{k.upper()}': v for k, v in PLOT_FILES.items()})
    
    return paths

def print_config():
    """Print current configuration for debugging."""
    print("="*60)
    print("AE TREND ANALYZER CONFIGURATION")
    print("="*60)
    
    print(f"Base Directory: {BASE_DIR}")
    print(f"Raw Data: {RAW_DIR}")
    print(f"Processed Data: {PROC_DIR}")
    print(f"Figures: {FIG_DIR}")
    
    print(f"\\nOutput Files:")
    for name, path in OUTPUT_FILES.items():
        print(f"  {name}: {path.name}")
    
    print(f"\\nPlot Files:")
    for name, path in PLOT_FILES.items():
        print(f"  {name}: {path.name}")
    
    print(f"\\nReview Datasets:")
    for name, path in REVIEW_CONFIG.items():
        exists = "✓" if path.exists() else "✗"
        print(f"  {exists} {name}: {path}")

if __name__ == "__main__":
    # When run directly, print configuration and ensure directories
    ensure_directories()
    print_config()
