from __future__ import annotations

import re
from collections.abc import Iterable

import numpy as np
import pandas as pd

BASE_COLUMNS = ["keyword", "title", "price", "raw_price", "rating", "reviews", "platform",
                "position", "delivery", "link", "thumbnail", "product_id", "source"]
KNOWN_BRANDS = ["Apple", "Samsung", "Google", "Dell", "HP", "Lenovo", "Asus", "Acer", "Sony", "Bose",
                "JBL", "Sennheiser", "Beats", "OnePlus", "Motorola", "Xiaomi", "Garmin", "Fitbit",
                "Amazfit", "Microsoft", "LG", "Logitech"]
ALIASES = {"search_term": "keyword", "product_title": "title", "name": "title", "sale_price": "price",
           "original_price": "raw_price", "old_price": "raw_price", "review_count": "reviews",
           "rank": "position", "shipping": "delivery", "product_link": "link", "image": "thumbnail"}
NUMERIC = ["price", "raw_price", "rating", "reviews", "position"]


def _numeric(series: pd.Series) -> pd.Series:
    # Accept a complete number with currency/group separators; reject partial text and monthly payments.
    text = series.astype("string").str.strip().str.replace(r"(?i)^(?:USD|INR|GBP|EUR)\s*", "", regex=True)
    text = text.str.replace(r"[$£€₹,\s]", "", regex=True)
    text = text.where(text.str.fullmatch(r"-?(?:\d+(?:\.\d*)?|\.\d+)"))
    return pd.to_numeric(text, errors="coerce").astype(float).replace([np.inf, -np.inf], np.nan)


def _clean_title(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s&+().,'/-]", " ", str(value))).strip()


def _brand_from_title(title: str) -> str:
    for brand in KNOWN_BRANDS:
        if re.search(rf"\b{re.escape(brand)}\b", title, re.IGNORECASE):
            return brand
    first = title.split(maxsplit=1)[0] if title else "Unknown"
    return first.title() if first.isalpha() else "Unknown"


def align_columns(frame: pd.DataFrame, source_name: str) -> pd.DataFrame:
    df = frame.copy()
    df.columns = [re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower()).strip("_") for c in df.columns]
    if df.columns.duplicated().any():
        raise ValueError("Duplicate column names after normalization")
    df = df.rename(columns={k: v for k, v in ALIASES.items() if k in df.columns and v not in df.columns})
    if "platform" not in df and "source" in df:
        df = df.rename(columns={"source": "platform"})
    if "source" not in df:
        df["source"] = frame.attrs.get("source", source_name)
    for column in BASE_COLUMNS:
        if column not in df:
            df[column] = pd.NA
    return df[BASE_COLUMNS]


def clean_and_engineer(frames: Iterable[pd.DataFrame]) -> tuple[pd.DataFrame, dict]:
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        raise ValueError("No product rows were supplied")
    profiles = [{"rows": len(f), "columns": len(f.columns), "dtypes": f.dtypes.astype(str).to_dict(),
                 "missing_counts": f.isna().sum().astype(int).to_dict(),
                 "missing_percent": (f.isna().mean() * 100).round(2).to_dict()} for f in frames]
    df = pd.concat([align_columns(f, f"input_{i + 1}") for i, f in enumerate(frames)], ignore_index=True)
    report = {"input_rows": len(df), "input_columns": len(df.columns), "input_profiles": profiles,
              "exact_duplicate_rows": int(df.duplicated().sum())}
    report["numeric_text_columns"] = [c for c in NUMERIC if not pd.api.types.is_numeric_dtype(df[c])]
    report["title_noise_rows"] = int(df.title.fillna("").astype(str).str.contains(r"[^\w\s&+().,'/-]", regex=True).sum())
    report["categorical_values_before"] = {c: sorted(df[c].dropna().astype(str).unique().tolist()) for c in ["platform", "delivery"]}
    report["invalid_numeric_text"] = {}
    for column in NUMERIC:
        parsed = _numeric(df[column])
        report["invalid_numeric_text"][column] = int((df[column].notna() & parsed.isna()).sum())
        df[column] = parsed
    report["non_positive_prices"] = int(df.price.le(0).sum())
    report["invalid_ratings"] = int((df.rating.notna() & ~df.rating.between(0, 5)).sum())
    report["invalid_reviews"] = int((df.reviews.notna() & ((df.reviews < 0) | (df.reviews % 1 != 0))).sum())
    report["invalid_positions"] = int((df.position.notna() & ((df.position < 1) | (df.position % 1 != 0))).sum())
    df["title"] = df.title.map(_clean_title)
    for column in ["keyword", "platform", "delivery", "source"]:
        df[column] = df[column].astype("string").str.strip().str.replace(r"\s+", " ", regex=True).replace("", pd.NA).fillna("Unknown")
    df["keyword"] = df.keyword.str.lower()
    df["platform"] = df.platform.str.title().replace({"Ebay": "eBay", "Bestbuy": "Best Buy"})
    df["delivery"] = df.delivery.str.title()
    for column in ["price", "raw_price"]:
        df.loc[df[column] <= 0, column] = np.nan
    df.loc[~df.rating.between(0, 5), "rating"] = np.nan
    df.loc[(df.reviews < 0) | (df.reviews % 1 != 0), "reviews"] = np.nan
    df.loc[(df.position < 1) | (df.position % 1 != 0), "position"] = np.nan
    # Only price is imputed. Ratings, review counts and ranks remain unknown when unobserved.
    df["price_imputed"] = df.price.isna()
    df["price"] = df.groupby("keyword").price.transform(lambda s: s.fillna(s.median()) if s.notna().any() else s)
    if df.price.notna().any():
        df["price"] = df.price.fillna(df.price.median())
    invalid = df.title.eq("") | df.price.isna()
    report["rows_removed_missing_title_or_price"] = int(invalid.sum())
    df = df.loc[~invalid].copy()
    if df.empty:
        raise ValueError("No usable products: provide titles and at least one positive numeric price")
    # Compare advertised prices before capping so outlier treatment cannot manufacture a discount.
    inconsistent = df.raw_price < df.price
    report["original_price_below_sale_price"] = int(inconsistent.sum())
    df.loc[inconsistent, "raw_price"] = np.nan
    df["discount_pct"] = ((df.raw_price - df.price) / df.raw_price * 100).round(2)
    df.loc[df.price_imputed, "discount_pct"] = np.nan
    before = len(df)
    df = df.drop_duplicates(subset=["keyword", "title", "platform", "price"], keep="first").copy()
    report["duplicate_rows_removed"] = before - len(df)
    cap = float(df.price.quantile(.99))
    report["price_distribution_before_cap"] = df.price.describe().round(2).to_dict()
    report["outliers_capped"] = int(df.price.gt(cap).sum())
    df["price_before_cap"] = df.price
    df["price"] = df.price.clip(upper=cap)
    df["brand"] = df.title.map(_brand_from_title)
    df["reviews"] = df.reviews.astype("Int64")
    df["position"] = df.position.astype("Int64")
    df["visibility_score"] = (100 / df.position).round(2).astype(float)
    df["top_10"] = df.position.le(10).astype("Int64")
    df["price_range"] = pd.cut(df.price, [0, 50, 150, 500, 1000, np.inf], right=False,
                                labels=["Under 50", "50-149.99", "150-499.99", "500-999.99", "1,000+"])
    df["rating_range"] = pd.cut(df.rating, [0, 3, 4, 4.5, 5.01], right=False,
                                 labels=["Under 3", "3-3.99", "4-4.49", "4.5-5"])
    df["rating_range"] = df.rating_range.cat.add_categories(["Unknown"]).fillna("Unknown")
    report.update({"output_rows": len(df), "price_cap_99th_percentile": round(cap, 2),
                   "price_values_imputed": int(df.price_imputed.sum()),
                   "remaining_missing_values": df[NUMERIC].isna().sum().astype(int).to_dict(),
                   "output_dtypes": df.dtypes.astype(str).to_dict(),
                   "sources": df.source.value_counts().to_dict(),
                   "ranked_rows": int(df.position.notna().sum()),
                   "discount_known_rows": int(df.discount_pct.notna().sum())})
    return df.reset_index(drop=True), report
