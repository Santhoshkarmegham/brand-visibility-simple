"""Local folders used by the assignment scripts."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / 'data' / 'raw'
CLEAN_DIR = ROOT / 'data' / 'processed'
REPORT_DIR = ROOT / 'reports'


def database_path():
    configured = Path(os.getenv('BRAND_DB_PATH', 'data/database/brand_visibility.db')).expanduser()
    return configured if configured.is_absolute() else ROOT / configured
