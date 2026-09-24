from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest
import requests

from brand_visibility.analytics.eda import answer_eda_questions
from brand_visibility.data.database import query_products, save_products
from brand_visibility.data.extract import extract_google_shopping
from brand_visibility.data.sample_data import generate_sample_data
from brand_visibility.data.transform import clean_and_engineer


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
    from brand_visibility import pipeline
    monkeypatch.setattr(pipeline, 'settings', replace(pipeline.settings,
        processed_data_dir=tmp_path / 'processed', reports_dir=tmp_path / 'reports'))
    clean, report = pipeline.run_pipeline(None, [], False, str(tmp_path / 'products.db'))
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
    clean, _ = clean_and_engineer([raw])
    db = tmp_path / 'app.db'
    save_products(clean, db)
    monkeypatch.setenv('BRAND_DB_PATH', str(db))
    app = AppTest.from_file(str(Path(__file__).parents[1] / 'app.py')).run(timeout=30)
    assert not app.exception
    assert len(app.tabs) == 6
    app.sidebar.multiselect[0].select('Apple').run()
    assert not app.exception
    assert set(next(frame.value for frame in app.dataframe if 'title' in frame.value and 'link' in frame.value and len(frame.value) != 10).brand) == {'Apple'}
    next(item for item in app.text_input if item.label == 'Search product title').set_value('unfindable-product-zzzz').run()
    assert not app.exception
    assert next(frame.value for frame in app.dataframe if 'title' in frame.value and 'link' in frame.value and len(frame.value) != 10).empty
