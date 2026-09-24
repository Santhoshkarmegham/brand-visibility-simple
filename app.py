"""Start the complete dashboard: python -m streamlit run app.py."""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
runpy.run_path(str(ROOT / "src/brand_visibility/dashboard/app.py"), run_name="__main__")
