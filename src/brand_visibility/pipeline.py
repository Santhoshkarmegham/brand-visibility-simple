from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

try:
    from dotenv import load_dotenv
except ImportError:  # Optional convenience; environment variables still work without it.
    def load_dotenv() -> bool:
        return False

from brand_visibility.config import settings
from brand_visibility.data.database import save_products
from brand_visibility.data.extract import extract_google_shopping
from brand_visibility.data.sample_data import generate_sample_data
from brand_visibility.data.transform import clean_and_engineer


def run_pipeline(csv_path: str | None, keywords: list[str], use_api: bool, db_path: str) -> tuple[pd.DataFrame, dict]:
    frames: list[pd.DataFrame] = []
    if csv_path:
        frames.append(pd.read_csv(csv_path))
    if use_api:
        api_df = extract_google_shopping(keywords)
        settings.raw_data_dir.mkdir(parents=True, exist_ok=True)
        api_df.to_csv(settings.raw_data_dir / "api_products.csv", index=False)
        frames.append(api_df)
    if not frames:
        frames.append(generate_sample_data())
    clean, report = clean_and_engineer(frames)
    settings.processed_data_dir.mkdir(parents=True, exist_ok=True)
    clean.to_csv(settings.processed_data_dir / "cleaned_products.csv", index=False)
    save_products(clean, db_path)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    (settings.reports_dir / "cleaning_report.json").write_text(json.dumps(report, indent=2))
    return clean, report


if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Build the Brand Visibility Intelligence dataset")
    parser.add_argument("--csv", help="Path to brand_dirty_dataset.csv")
    parser.add_argument("--api", action="store_true", help="Also fetch live SerpAPI results")
    parser.add_argument("--keywords", nargs="+", default=["laptop", "phone", "headphones", "smartwatch"])
    parser.add_argument("--db", default=str(settings.database_path))
    args = parser.parse_args()
    result, diagnostics = run_pipeline(args.csv, args.keywords, args.api, args.db)
    print(f"Saved {len(result):,} cleaned rows to {args.db}")
    print(json.dumps(diagnostics, indent=2))
