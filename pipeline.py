"""Combine CSV and API data, clean it, save SQL/CSV, and generate analysis."""
import argparse
import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

import paths
from data_cleaning import clean_and_engineer
from data_collection import extract_google_shopping
from database import query_products, save_products


def has_both_sources(frame: pd.DataFrame) -> bool:
    sources = set(frame.source.dropna().astype(str).str.split('+').explode())
    return {'csv', 'serpapi'}.issubset(sources)


def prepare_combined_data(refresh_api: bool = False):
    load_dotenv(paths.ROOT / '.env')
    csv_path = Path(os.getenv('CSV_PATH', 'data/source_products.csv')).expanduser()
    if not csv_path.is_absolute():
        csv_path = paths.ROOT / csv_path
    if not csv_path.exists():
        raise ValueError(f'Place your original CSV at {csv_path}, or set CSV_PATH in .env.')
    csv = pd.read_csv(csv_path)
    if csv.empty:
        raise ValueError('The CSV has no product rows.')
    csv['source'] = 'csv'
    country = os.getenv('API_COUNTRY', 'in').lower()
    currency = os.getenv('CSV_CURRENCY', '').upper()
    expected = {'in': 'INR', 'us': 'USD', 'gb': 'GBP'}
    if country not in expected or currency != expected[country]:
        raise ValueError('Set CSV_CURRENCY and API_COUNTRY in .env to matching values: INR/in, USD/us or GBP/gb.')
    configured = os.getenv('SEARCH_KEYWORDS', '')
    keyword_column = next((c for c in csv if c.strip().lower() == 'keyword'), None)
    keywords = [k.strip() for k in configured.split(',') if k.strip()]
    if not keywords and keyword_column:
        keywords = csv[keyword_column].dropna().astype(str).str.strip().drop_duplicates().head(3).tolist()
    if not keywords:
        raise ValueError('Set comma-separated SEARCH_KEYWORDS in .env.')
    signature = {'country': country, 'keywords': keywords}
    cache = paths.RAW_DIR / 'api_products.csv'
    metadata = paths.RAW_DIR / 'api_products.json'
    matches = False
    if cache.exists() and metadata.exists():
        try:
            matches = json.loads(metadata.read_text()) == signature
        except (ValueError, OSError):
            pass
    if matches and not refresh_api:
        api = pd.read_csv(cache)
        api_mode = 'cached'
    else:
        api = extract_google_shopping(keywords, country=country)
        cache.parent.mkdir(parents=True, exist_ok=True)
        api.to_csv(cache, index=False)
        metadata.write_text(json.dumps(signature, indent=2))
        api_mode = 'fresh'
    if api.empty:
        raise ValueError('API data is empty. Run python pipeline.py --refresh-api.')
    api['source'] = 'serpapi'
    # Validate both sources survive cleaning before replacing an existing dataset.
    preview, _ = clean_and_engineer([csv, api])
    if not has_both_sources(preview):
        raise ValueError('Both CSV and API must contain usable products; the previous dataset was preserved.')
    clean, report = build_dataset([csv, api], str(paths.database_path()))
    return clean, report, api_mode


def combined_database_ready() -> bool:
    if not paths.database_path().exists():
        return False
    try:
        return has_both_sources(query_products(paths.database_path()))
    except (ValueError, OSError, pd.errors.DatabaseError):
        return False


def build_dataset(frames: list[pd.DataFrame], db_path: str) -> tuple[pd.DataFrame, dict]:
    clean, report = clean_and_engineer(frames)
    paths.CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    clean.to_csv(paths.CLEAN_DIR / "cleaned_products.csv", index=False)
    save_products(clean, db_path)
    paths.REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (paths.REPORT_DIR / "cleaning_report.json").write_text(json.dumps(report, indent=2))
    from report import export_reports
    export_reports(clean, report, paths.REPORT_DIR)
    return clean, report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Combine the local CSV and SerpAPI products')
    parser.add_argument('--refresh-api', action='store_true', help='Fetch new API results instead of reusing the cache')
    args = parser.parse_args()
    try:
        clean, report, mode = prepare_combined_data(args.refresh_api)
    except (ValueError, OSError) as error:
        parser.exit(1, f'{error}\n')
    print(f'Saved {len(clean):,} combined products. API data: {mode}. Sources: {report["sources"]}')
    print('Start the dashboard: python -m streamlit run app.py')
