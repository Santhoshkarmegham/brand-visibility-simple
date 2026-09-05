import pandas as pd

from brand_visibility.data.transform import clean_and_engineer


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
