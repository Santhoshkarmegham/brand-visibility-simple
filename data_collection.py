from __future__ import annotations

import os
from collections.abc import Iterable

import pandas as pd
import requests

SERPAPI_URL = "https://serpapi.com/search.json"


def extract_google_shopping(keywords: Iterable[str], api_key: str | None = None, country: str = "us") -> pd.DataFrame:
    """Fetch one Google Shopping results page per keyword (one request/credit each).

    Monthly installment listings are excluded because they are not outright product prices.
    """
    key = api_key or os.getenv("SERPAPI_KEY")
    if not key or key == "replace_with_your_key":
        raise ValueError("Configure SERPAPI_KEY in .env before fetching live data")
    terms = list(dict.fromkeys(term.strip() for term in keywords if term.strip()))
    if not terms:
        raise ValueError("Supply at least one search keyword")
    records = []
    for keyword in terms:
        try:
            response = requests.get(SERPAPI_URL, params={"engine": "google_shopping", "q": keyword,
                                    "gl": country, "hl": "en", "api_key": key}, timeout=45)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError):
            # Requests exceptions can contain the request URL, including the secret key.
            raise ValueError("SerpAPI request failed. Check your key, quota and network connection.") from None
        if payload.get("error") or payload.get("search_metadata", {}).get("status") == "Error":
            raise ValueError("SerpAPI returned an error. Check your account quota and search settings.")
        for item in payload.get("shopping_results", []):
            if item.get("installment") or "/mo" in str(item.get("price", "")).lower():
                continue
            records.append({"keyword": keyword, "title": item.get("title"),
                            "price": item.get("extracted_price", item.get("price")),
                            "raw_price": item.get("extracted_old_price", item.get("old_price")),
                            "rating": item.get("rating"), "reviews": item.get("reviews"),
                            "platform": item.get("source"), "position": item.get("position"),
                            "delivery": item.get("delivery", item.get("shipping")),
                            "link": item.get("product_link", item.get("link")),
                            "thumbnail": item.get("thumbnail"), "product_id": item.get("product_id"),
                            "source": "serpapi"})
    if not records:
        raise ValueError("SerpAPI returned no usable shopping products; try another keyword")
    return pd.DataFrame.from_records(records)
