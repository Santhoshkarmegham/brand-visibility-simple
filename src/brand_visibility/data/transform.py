from __future__ import annotations

import re
from typing import Iterable

import numpy as np
import pandas as pd


BASE_COLUMNS = [
    "keyword", "title", "price", "raw_price", "rating", "reviews", "platform",
    "position", "delivery", "link", "thumbnail", "product_id", "source",
]
KNOWN_BRANDS = [
    "Apple", "Samsung", "Google", "Dell", "HP", "Lenovo", "Asus", "Acer",
    "Sony", "Bose", "JBL", "Sennheiser", "Beats", "OnePlus", "Motorola",
    "Xiaomi", "Garmin", "Fitbit", "Amazfit", "Microsoft", "LG", "Logitech",
]
ALIASES = {
    "search_term": "keyword", "product_title": "title", "name": "title",
    "sale_price": "price", "original_price": "raw_price", "old_price": "raw_price",
    "review_count": "reviews", "source": "platform", "rank": "position",
    "shipping": "delivery", "product_link": "link", "image": "thumbnail",
}


def _numeric(series: pd.Series) -> pd.Series:
    cleaned = series.astype("string").str.replace(r"[^0-9.\-]", "", regex=True)
    return pd.to_numeric(cleaned.replace({"": pd.NA, ".": pd.NA, "-": pd.NA}), errors="coerce")


def _clean_title(value: object) -> str:
    text = re.sub(r"[^\w\s&+().,'/-]", " ", str(value or ""))
    return re.sub(r"\s+", " ", text).strip()


def _brand_from_title(title: str) -> str:
    lower = title.casefold()
    for brand in KNOWN_BRANDS:
        if re.search(rf"\b{re.escape(brand.casefold())}\b", lower):
            return brand
    first = title.split(maxsplit=1)[0] if title else "Unknown"
    return first.title() if first.isalpha() else "Unknown"


def align_columns(frame: pd.DataFrame, source_name: str) -> pd.DataFrame:
    df = frame.copy()
    df.columns = [re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower()).strip("_") for c in df.columns]
    df = df.rename(columns={k: v for k, v in ALIASES.items() if k in df.columns and v not in df.columns})
    if "source" not in df.columns:
        df["source"] = source_name
    for column in BASE_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA
    return df[BASE_COLUMNS]


def clean_and_engineer(frames: Iterable[pd.DataFrame]) -> tuple[pd.DataFrame, dict]:
    aligned = [align_columns(frame, f"input_{i + 1}") for i, frame in enumerate(frames) if not frame.empty]
    if not aligned:
        raise ValueError("No product rows were supplied")
    df = pd.concat(aligned, ignore_index=True)
    report = {"input_rows": len(df), "input_columns": len(df.columns)}
    for column in ["price", "raw_price", "rating", "reviews", "position"]:
        df[column] = _numeric(df[column])
    df["title"] = df["title"].map(_clean_title)
    df["keyword"] = df["keyword"].astype("string").str.strip().str.lower().fillna("unknown")
    df["platform"] = df["platform"].astype("string").str.strip().str.title().replace({"<NA>": "Unknown", "": "Unknown"})
    df["delivery"] = df["delivery"].astype("string").str.strip().replace({"<NA>": "Unknown", "": "Unknown"})
    df.loc[df["price"] <= 0, "price"] = np.nan
    df.loc[~df["rating"].between(0, 5), "rating"] = np.nan
    df.loc[df["reviews"] < 0, "reviews"] = np.nan
    df.loc[df["position"] <= 0, "position"] = np.nan
    df["raw_price"] = df["raw_price"].fillna(df["price"])
    df.loc[df["raw_price"] < df["price"], "raw_price"] = df["price"]
    # Retain unrated products; medians make aggregate analysis usable without inventing extremes.
    for column in ["price", "rating", "reviews", "position"]:
        df[column] = df.groupby("keyword")[column].transform(lambda s: s.fillna(s.median()))
        df[column] = df[column].fillna(df[column].median())
    price_cap = float(df["price"].quantile(0.99))
    df["price"] = df["price"].clip(upper=price_cap)
    df["raw_price"] = df["raw_price"].clip(upper=max(price_cap, float(df["raw_price"].quantile(0.99))))
    before = len(df)
    df = df.drop_duplicates(subset=["keyword", "title", "platform", "price"], keep="first")
    df["brand"] = df["title"].map(_brand_from_title)
    df["visibility_score"] = (100 / df["position"].clip(lower=1)).round(2)
    df["discount_pct"] = np.where(
        df["raw_price"] > 0, ((df["raw_price"] - df["price"]) / df["raw_price"] * 100).clip(0, 100), 0,
    ).round(2)
    bins = [-np.inf, 50, 150, 500, 1000, np.inf]
    df["price_range"] = pd.cut(df["price"], bins=bins, labels=["Under $50", "$50-$149", "$150-$499", "$500-$999", "$1,000+"])
    df["rating_range"] = pd.cut(df["rating"], bins=[-np.inf, 3, 4, 4.5, np.inf], labels=["Under 3", "3-3.9", "4-4.4", "4.5+"])
    df["top_10"] = (df["position"] <= 10).astype(int)
    df["reviews"] = df["reviews"].round().astype(int)
    df["position"] = df["position"].round().astype(int)
    report.update({
        "duplicate_rows_removed": before - len(df), "output_rows": len(df),
        "price_cap_99th_percentile": round(price_cap, 2),
        "remaining_missing_values": int(df[["price", "rating", "reviews", "position"]].isna().sum().sum()),
    })
    return df.reset_index(drop=True), report

