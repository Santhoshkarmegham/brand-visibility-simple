from __future__ import annotations

import os
from typing import Iterable

import pandas as pd


SERPAPI_URL = "https://serpapi.com/search.json"


def extract_google_shopping(
    keywords: Iterable[str], api_key: str | None = None, country: str = "us"
) -> pd.DataFrame:
    """Fetch Google Shopping results from SerpAPI and normalize product records."""
    key = api_key or os.getenv("SERPAPI_KEY")
    if not key:
        raise ValueError("SERPAPI_KEY is required for live extraction")
    try:
        import requests
    except ImportError as exc:
        raise RuntimeError("Install the requirements before using live API extraction") from exc
    records: list[dict] = []
    for keyword in keywords:
        response = requests.get(
            SERPAPI_URL,
            params={"engine": "google_shopping", "q": keyword, "gl": country, "hl": "en", "api_key": key},
            timeout=45,
        )
        response.raise_for_status()
        for item in response.json().get("shopping_results", []):
            records.append(
                {
                    "keyword": keyword,
                    "title": item.get("title"),
                    "price": item.get("extracted_price", item.get("price")),
                    "raw_price": item.get("extracted_old_price", item.get("old_price")),
                    "rating": item.get("rating"),
                    "reviews": item.get("reviews"),
                    "platform": item.get("source"),
                    "position": item.get("position"),
                    "delivery": item.get("delivery", item.get("shipping")),
                    "link": item.get("product_link", item.get("link")),
                    "thumbnail": item.get("thumbnail"),
                    "product_id": item.get("product_id"),
                    "source": "serpapi",
                }
            )
    return pd.DataFrame.from_records(records)
