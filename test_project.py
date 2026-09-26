import random
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest
import requests

import paths
import pipeline
import pipeline as combined
from data_cleaning import clean_and_engineer
from data_collection import extract_google_shopping
from database import query_products, save_products
from eda import answer_eda_questions

BRANDS = {
    "laptop": ["Apple", "Dell", "HP", "Lenovo", "Asus", "Acer"],
    "phone": ["Apple", "Samsung", "Google", "OnePlus", "Motorola", "Xiaomi"],
    "headphones": ["Sony", "Bose", "JBL", "Apple", "Sennheiser", "Beats"],
    "smartwatch": ["Apple", "Samsung", "Garmin", "Fitbit", "Amazfit", "Google"],
}
PLATFORMS = ["Amazon", "Walmart", "Best Buy", "Target", "eBay"]


def generate_sample_data(rows_per_keyword: int = 45, seed: int = 42) -> pd.DataFrame:
    """Create deterministic, realistic demo data when source files are unavailable."""
    rng = random.Random(seed)
    rows: list[dict] = []
    for keyword, brands in BRANDS.items():
        for position in range(1, rows_per_keyword + 1):
            brand = rng.choice(brands)
            platform = rng.choices(PLATFORMS, weights=[36, 23, 18, 12, 11])[0]
            base = {"laptop": 850, "phone": 650, "headphones": 180, "smartwatch": 260}[keyword]
            raw_price = round(max(25, rng.gauss(base, base * 0.38)), 2)
            discount = rng.choice([0, 0, 0, 5, 10, 12, 15, 20, 25, 30])
            price = round(raw_price * (1 - discount / 100), 2)
            rating = round(min(5, max(2.8, rng.gauss(4.25, 0.38))), 1)
            reviews = max(0, int(rng.lognormvariate(6.0, 1.35)))
            model = rng.choice(["Pro", "Plus", "Air", "Ultra", "Max", "Essential"])
            rows.append(
                {
                    "keyword": keyword,
                    "title": f"{brand} {model} {keyword.title()} {rng.randint(10, 99)}",
                    "price": price,
                    "raw_price": raw_price,
                    "rating": rating,
                    "reviews": reviews,
                    "platform": platform,
                    "position": position,
                    "delivery": rng.choice(["Free Delivery", "Prime", "Paid", "Unknown"]),
                    "link": f"https://example.com/{keyword}/{position}",
                    "thumbnail": "",
                    "source": "demo",
                }
            )
    return pd.DataFrame(rows)


def write_sample_csv(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    generate_sample_data().to_csv(path, index=False)
    return path







@pytest.fixture
def setup(tmp_path, monkeypatch):
    from types import SimpleNamespace
    config = SimpleNamespace(database_path=tmp_path / 'products.db')
    for name, value in {'ROOT': tmp_path, 'RAW_DIR': tmp_path / 'raw', 'CLEAN_DIR': tmp_path / 'processed', 'REPORT_DIR': tmp_path / 'reports'}.items():
        monkeypatch.setattr(paths, name, value)
    monkeypatch.setenv('BRAND_DB_PATH', str(tmp_path / 'products.db'))
    monkeypatch.setenv('CSV_PATH', 'source.csv')
    monkeypatch.setenv('CSV_CURRENCY', 'INR')
    monkeypatch.setenv('API_COUNTRY', 'in')
    monkeypatch.setenv('SEARCH_KEYWORDS', 'phone')
    pd.DataFrame({'title': ['Apple CSV Phone'], 'keyword': ['phone'], 'price': [100]}).to_csv(tmp_path / 'source.csv', index=False)
    api = Mock(return_value=pd.DataFrame({'title': ['Samsung API Phone'], 'keyword': ['phone'], 'price': [200], 'position': [1]}))
    monkeypatch.setattr(combined, 'extract_google_shopping', api)
    return config, api


def test_both_sources_saved_cache_reused_and_refresh(setup):
    config, api = setup
    clean, _, mode = combined.prepare_combined_data()
    assert mode == 'fresh'
    assert set(clean.source) == {'csv', 'serpapi'}
    assert combined.combined_database_ready()
    stored = query_products(config.database_path)
    assert len(stored) == 2
    assert stored.loc[stored.source == 'csv', 'position'].isna().all()
    assert stored.loc[stored.source == 'serpapi', 'position'].iloc[0] == 1
    assert combined.prepare_combined_data()[2] == 'cached'
    assert api.call_count == 1
    combined.prepare_combined_data(refresh_api=True)
    assert api.call_count == 2


def test_missing_api_does_not_replace_database(setup):
    config, api = setup
    combined.prepare_combined_data()
    previous = config.database_path.read_bytes()
    api.side_effect = ValueError('Configure SERPAPI_KEY')
    with pytest.raises(ValueError, match='SERPAPI_KEY'):
        combined.prepare_combined_data(refresh_api=True)
    assert config.database_path.read_bytes() == previous


def test_currency_mismatch_stops_before_api(setup, monkeypatch):
    _, api = setup
    monkeypatch.setenv('CSV_CURRENCY', 'USD')
    with pytest.raises(ValueError, match='matching'):
        combined.prepare_combined_data()
    api.assert_not_called()


def test_duplicate_retains_both_sources():
    first = pd.DataFrame({'title': ['Apple Phone'], 'price': [100], 'source': ['csv']})
    second = first.assign(source='serpapi', position=2)
    clean, _ = clean_and_engineer([first, second])
    assert len(clean) == 1
    assert clean.source.iloc[0] == 'csv+serpapi'
    assert combined.has_both_sources(clean)
    assert clean.position.iloc[0] == 2


def test_app_has_no_upload_or_fallback(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv('BRAND_DB_PATH', str(tmp_path / 'absent.db'))
    app = AppTest.from_file(str(Path(__file__).parent / 'app.py')).run(timeout=30)
    assert not app.exception
    assert not app.get('file_uploader')
    assert any('combined CSV + API' in message.value for message in app.info)
    assert not (tmp_path / 'absent.db').exists()





def test_cleaning_and_features():
    dirty = pd.DataFrame({
        "Keyword": ["Phone", "Phone", "Phone"],
        "title": ["Apple!!! Phone", "Apple!!! Phone", "Samsung Phone"],
        "price": ["$999.00", "$999.00", "Not Available"],
        "raw_price": ["$1,099", "$1,099", "$800"],
        "rating": ["4.8", "4.8", "many"],
        "Reviews": ["1,200", "1,200", "20"],
        "platform": ["amazon", "AMAZON", "Walmart"],
        "position": [1, 1, 2],
    })
    clean, report = clean_and_engineer([dirty])
    assert len(clean) == 2
    assert clean.loc[0, "brand"] == "Apple"
    assert clean.loc[0, "visibility_score"] == 100
    assert clean.loc[0, "discount_pct"] > 0
    assert report["duplicate_rows_removed"] == 1






def test_missing_rank_and_discount_are_not_invented(tmp_path):
    raw = pd.DataFrame({'title': ['Apple Phone', 'Sony Headphones'], 'price': [100, 200]})
    clean, report = clean_and_engineer([raw])
    assert clean.position.isna().all()
    assert clean.visibility_score.isna().all()
    assert clean.discount_pct.isna().all()
    assert clean.rating.isna().all()
    assert clean.reviews.isna().all()
    assert clean.delivery.eq('Unknown').all()
    assert clean.platform.eq('Unknown').all()
    assert report['ranked_rows'] == 0
    db = tmp_path / 'products.db'
    save_products(clean, db)
    assert query_products(db).position.isna().all()
    answers = answer_eda_questions(query_products(db))
    assert len(answers) == 30
    assert 'Unavailable' in answers['07_brand_highest_visibility']


def test_cleaning_boundaries_and_missing_titles():
    raw = pd.DataFrame({'title': ['Apple A', 'Sony B', None, 'Dell C'],
                        'price': [50, 150, 10, -1], 'raw_price': [50, 150, 10, 200],
                        'rating': [3, 4.5, 8, -1], 'reviews': [0, -1, 2, 1.5],
                        'position': [1, 2.5, 2, 100], 'platform': ['AMAZON', ' amazon ', None, 'Amazon']})
    clean, report = clean_and_engineer([raw])
    assert len(clean) == 3
    assert clean.loc[0, 'price_range'] == '50-149.99'
    assert clean.loc[0, 'rating_range'] == '3-3.99'
    assert clean.loc[1, 'rating_range'] == '4.5-5'
    assert pd.isna(clean.loc[1, 'position'])
    assert pd.isna(clean.loc[2, 'discount_pct'])
    assert clean.loc[1, 'discount_pct'] == 0  # Price capping cannot create a discount.
    assert report['rows_removed_missing_title_or_price'] == 1


def test_api_normalization_and_installment_exclusion(monkeypatch):
    response = Mock()
    response.json.return_value = {'shopping_results': [
        {'title': 'Apple Phone', 'extracted_price': 100, 'extracted_old_price': 120,
         'source': 'Amazon', 'position': 1, 'rating': 4.5, 'reviews': 20},
        {'title': 'Monthly phone', 'price': '$29/mo', 'extracted_price': 29, 'installment': {'period': 24}}]}
    get = Mock(return_value=response)
    monkeypatch.setattr(requests, 'get', get)
    api = extract_google_shopping(['phone', 'phone'], api_key='test-key')
    assert get.call_count == 1
    assert get.call_args.kwargs['params']['engine'] == 'google_shopping'
    assert len(api) == 1
    csv = pd.DataFrame({'title': ['Sony Headphones'], 'price': [80], 'keyword': ['headphones']})
    clean, _ = clean_and_engineer([csv, api])
    assert len(clean) == 2
    assert clean.loc[1, 'source'] == 'serpapi'
    assert clean.loc[1, 'visibility_score'] == 100


def test_api_errors_do_not_expose_key(monkeypatch):
    monkeypatch.setattr(requests, 'get', Mock(side_effect=requests.HTTPError('secret-key-in-url')))
    with pytest.raises(ValueError) as error:
        extract_google_shopping(['phone'], api_key='secret-key-in-url')
    assert 'secret-key-in-url' not in str(error.value)
    response = Mock()
    response.json.return_value = {'error': 'quota exhausted'}
    monkeypatch.setattr(requests, 'get', Mock(return_value=response))
    with pytest.raises(ValueError, match='returned an error'):
        extract_google_shopping(['phone'], api_key='test-key')
    response.json.return_value = {'shopping_results': []}
    with pytest.raises(ValueError, match='no usable'):
        extract_google_shopping(['phone'], api_key='test-key')


def test_sql_filters_and_injection(tmp_path):
    clean, _ = clean_and_engineer([generate_sample_data()])
    db = tmp_path / 'products.db'
    save_products(clean, db)
    selection = query_products(db, {'brand': ['Apple'], 'position': (1, 10)})
    assert not selection.empty
    assert selection.brand.eq('Apple').all()
    assert selection.position.between(1, 10).all()
    assert query_products(db, {'brand': ["Apple' OR 1=1 --"]}).empty
    assert len(query_products(db)) == 180


def test_pipeline_exports_reports(tmp_path, monkeypatch):
    import paths
    monkeypatch.setattr(paths, 'CLEAN_DIR', tmp_path / 'processed')
    monkeypatch.setattr(paths, 'REPORT_DIR', tmp_path / 'reports')
    clean, report = pipeline.build_dataset([generate_sample_data()], str(tmp_path / 'products.db'))
    assert len(clean) == report['output_rows'] == 180
    assert (tmp_path / 'processed/cleaned_products.csv').exists()
    for name in ['cleaning_answers.md', 'eda_answers.md']:
        assert (tmp_path / 'reports' / name).read_text().count('\n## ') == 30


@pytest.mark.parametrize('ranked', [False, True])
def test_dashboard_all_tabs_and_filters(tmp_path, monkeypatch, ranked):
    from streamlit.testing.v1 import AppTest
    raw = generate_sample_data()
    if not ranked:
        raw = raw.drop(columns=['position', 'raw_price', 'rating', 'reviews'])
    raw['source'] = ['csv' if i % 2 else 'serpapi' for i in range(len(raw))]
    clean, _ = clean_and_engineer([raw])
    db = tmp_path / 'app.db'
    save_products(clean, db)
    monkeypatch.setenv('BRAND_DB_PATH', str(db))
    app = AppTest.from_file(str(Path(__file__).parent / 'app.py')).run(timeout=30)
    assert not app.exception
    assert len(app.tabs) == 6
    app.sidebar.multiselect[0].select('Apple').run()
    assert not app.exception
    assert set(next(frame.value for frame in app.dataframe if 'title' in frame.value and 'link' in frame.value and len(frame.value) != 10).brand) == {'Apple'}
    next(item for item in app.text_input if item.label == 'Search product title').set_value('unfindable-product-zzzz').run()
    assert not app.exception
    assert next(frame.value for frame in app.dataframe if 'title' in frame.value and 'link' in frame.value and len(frame.value) != 10).empty
