"""Batch entry point: python pipeline.py --csv path/to/products.csv [--api]."""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
runpy.run_module('brand_visibility.pipeline', run_name='__main__')
