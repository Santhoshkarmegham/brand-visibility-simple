from __future__ import annotations

import json
import shutil
from numbers import Integral
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from brand_visibility.analytics.eda import answer_eda_questions, business_insights
from brand_visibility.config import settings
from brand_visibility.data.database import filter_options, query_products
from brand_visibility.data.extract import extract_google_shopping
from brand_visibility.pipeline import build_dataset, run_pipeline

load_dotenv(settings.project_root / ".env")
st.set_page_config(page_title="Brand Visibility Intelligence", page_icon="◈", layout="wide")
DB_PATH = str(settings.database_path)
COLORS = ["#635BFF", "#15A99B", "#FFB547", "#ED718C", "#4D8BFF"]


def metric(label, value, digits=1):
    text = "N/A" if pd.isna(value) else (f"{value:,}" if isinstance(value, Integral) else (f"{value:,.{digits}f}" if isinstance(value, float) else str(value)))
    st.metric(label, text)


def cards(items):
    for column, (label, value) in zip(st.columns(len(items)), items):
        with column:
            metric(label, value)


def chart(data, kind, title, **kwargs):
    if data.empty:
        st.info(f"{title}: no observed values in this selection.")
        return
    figure = getattr(px, kind)(data, title=title, color_discrete_sequence=COLORS, **kwargs)
    figure.update_layout(height=350, margin={"l": 10, "r": 10, "t": 50, "b": 20}, legend_title_text="")
    st.plotly_chart(figure, use_container_width=True)


def best(series):
    values = series.dropna()
    return values.idxmax() if not values.empty else "N/A"


def discount_share(data):
    known = data.discount_pct.dropna()
    return f"{known.gt(0).mean() * 100:.1f}%" if len(known) else "N/A"


if not Path(DB_PATH).exists():
    snapshot = settings.project_root / "deliverables" / "brand_visibility.db"
    if snapshot.exists():
        Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(snapshot, DB_PATH)
    else:
        run_pipeline(None, [], False, DB_PATH)

with st.sidebar:
    st.title("◈ Brand Visibility")
    with st.expander("Load data"):
        st.caption("Upload CSV, fetch Google Shopping results, or combine both. API calls happen only when you click Load data.")
        upload = st.file_uploader("Product CSV", type="csv")
        use_api = st.checkbox("Include live SerpAPI results")
        keywords = st.text_input("Keywords (comma separated)", "laptop, phone")
        country = st.selectbox("API market", ["us", "in", "gb"])
        same_currency = st.checkbox("CSV prices use the same currency as the selected API market")
        if st.button("Load data", type="primary"):
            try:
                if upload is None and not use_api:
                    raise ValueError("Upload a CSV or select live API results")
                if upload is not None and use_api and not same_currency:
                    raise ValueError("Confirm a common currency before combining prices")
                frames = []
                if upload is not None:
                    csv = pd.read_csv(upload)
                    csv.attrs["source"] = "csv"
                    frames.append(csv)
                if use_api:
                    with st.spinner("Fetching Google Shopping results…"):
                        frames.append(extract_google_shopping(keywords.split(","), country=country))
                build_dataset(frames, DB_PATH)
                st.success("Dataset saved. All tabs now use the updated SQL data.")
            except (ValueError, TypeError, OSError, UnicodeDecodeError):
                st.error("Could not load data. Check CSV titles/prices, API key and quota, and the currency confirmation.")
        if st.button("Use demo data"):
            run_pipeline(None, [], False, DB_PATH)
            st.rerun()
    st.subheader("Filter products")
    opts = filter_options(DB_PATH)
    filters = {}
    for col, label in [("brand", "Brand"), ("platform", "Platform"), ("price_range", "Price range"),
                       ("rating_range", "Rating range"), ("keyword", "Keyword")]:
        filters[col] = st.multiselect(label, opts[col])
    all_products = query_products(DB_PATH)
    observed_positions = all_products.position.dropna()
    ranked_only = st.checkbox("Only products with known rankings", disabled=observed_positions.empty)
    if not observed_positions.empty:
        low, high = int(observed_positions.min()), int(observed_positions.max())
        if low < high:
            bounds = st.slider("Position (ranking)", low, high, (low, high))
            if ranked_only or bounds != (low, high):
                filters["position"] = bounds
        elif ranked_only:
            filters["position"] = (low, high)
    else:
        st.caption("Ranking filter unavailable: source data has no positions.")
    st.caption("All filters query the SQLite database.")

df = query_products(DB_PATH, filters)
st.title("Brand Visibility Intelligence")
st.caption("Product assortment · Pricing · Customer ratings · Search performance")
sources = ", ".join(all_products.source.dropna().unique())
if sources == "demo":
    st.info("Demo data: generated examples, not live market observations.")
else:
    st.caption(f"Data sources: {sources}. Prices are shown in source currency units; no currency conversion is applied.")
if df.empty:
    st.warning("No products match these filters. Clear a sidebar selection.")
    st.stop()
ranked = df[df.position.notna()].copy()
rated = df[df.rating.notna()].copy()
st.caption(f"{len(df):,} products · {len(ranked):,} with observed rankings · {len(rated):,} with ratings · {df.discount_pct.notna().sum():,} with known discounts")
if ranked.empty:
    st.warning("This dataset has no observed rankings. Visibility and ranking charts will become available when ranked API data is loaded.")

overview, brands, pricing, platforms, visibility, explorer = st.tabs(
    ["Overview", "Brand Insights", "Pricing Analysis", "Platform Analysis", "Visibility & Ranking", "Product Explorer"])
brand_stats = df.groupby("brand", as_index=False).agg(products=("title", "size"), rating=("rating", "mean"), visibility=("visibility_score", "mean"))
platform_stats = df.groupby("platform", as_index=False).agg(products=("title", "size"), price=("price", "mean"), rating=("rating", "mean"), position=("position", "mean"))

with overview:
    cards([("Total products", len(df)), ("Average price", df.price.mean()), ("Average rating", df.rating.mean()), ("Total observed reviews", df.reviews.sum(min_count=1))])
    left, right = st.columns(2)
    with left:
        chart(df, "histogram", "Price distribution", x="price", nbins=30)
        counts = df.keyword.value_counts().rename_axis("keyword").reset_index(name="products")
        chart(counts, "bar", "Products per keyword", x="keyword", y="products")
    with right:
        counts = df.platform.value_counts().rename_axis("platform").reset_index(name="products")
        chart(counts, "pie", "Platform share", names="platform", values="products", hole=.5)
        chart(df[df.reviews.notna()], "histogram", "Review distribution", x="reviews", nbins=30)
    st.subheader("Business insights")
    for insight in business_insights(df):
        st.write(f"• {insight}")

with brands:
    cards([("Top brand by listings", best(df.brand.value_counts())), ("Average visibility", df.visibility_score.mean()),
           ("Highest rated brand", best(df.groupby("brand").rating.mean()))])
    chart(brand_stats, "bar", "Products by brand", x="brand", y="products")
    left, right = st.columns(2)
    with left:
        chart(brand_stats.dropna(subset=["rating"]), "bar", "Average rating by brand", x="brand", y="rating")
    with right:
        top = ranked[ranked.position <= 10].brand.value_counts().rename_axis("brand").reset_index(name="products")
        chart(top, "bar", "Brands in top 10 positions", x="brand", y="products")

with pricing:
    cards([("Average price", df.price.mean()), ("Highest price", df.price.max()), ("Lowest price", df.price.min()), ("Discounted (known prices)", discount_share(df))])
    st.caption("Discount share uses products with both observed selling and valid original prices. Price outliers are capped; discounts use original uncapped prices.")
    left, right = st.columns(2)
    with left:
        chart(df, "histogram", "Price distribution by range", x="price", color="price_range", nbins=30)
        chart(rated, "scatter", "Price vs rating", x="price", y="rating", color="platform", hover_name="title")
        discounts = df.groupby("brand", as_index=False).discount_pct.mean().dropna()
        chart(discounts, "bar", "Average discount by brand", x="brand", y="discount_pct")
    with right:
        chart(ranked, "scatter", "Price vs ranking", x="price", y="position", color="platform", hover_name="title")
        counts = df.price_range.value_counts().rename_axis("price_range").reset_index(name="products")
        chart(counts, "bar", "Price range distribution", x="price_range", y="products")
        discounts = df.groupby("platform", as_index=False).discount_pct.mean().dropna()
        chart(discounts, "bar", "Average discount by platform", x="platform", y="discount_pct")

with platforms:
    cards([("Total platforms", df.platform.nunique()), ("Highest rated platform", best(df.groupby("platform").rating.mean())),
           ("Lowest average price", df.groupby("platform").price.mean().idxmin())])
    left, right = st.columns(2)
    for target, label, slot in [("products", "Product count", left), ("price", "Average price", right), ("rating", "Average rating", left), ("position", "Average ranking", right)]:
        with slot:
            chart(platform_stats.dropna(subset=[target]), "bar", f"{label} by platform", x="platform", y=target)
    counts = df.groupby(["platform", "brand"], as_index=False).size()
    chart(counts, "bar", "Brand distribution per platform", x="platform", y="size", color="brand")

with visibility:
    top_share = f"{ranked.position.le(10).mean() * 100:.1f}%" if len(ranked) else "N/A"
    cards([("Average position", ranked.position.mean()), ("Average visibility", ranked.visibility_score.mean()), ("Top 10 (ranked products)", top_share)])
    st.caption("Visibility = 100 / observed position. Lower positions and higher visibility scores are better. Missing ranks are excluded, never estimated.")
    left, right = st.columns(2)
    with left:
        chart(ranked, "histogram", "Ranking distribution", x="position", nbins=30)
        chart(ranked.dropna(subset=["reviews"]), "scatter", "Reviews vs ranking", x="reviews", y="position", size="visibility_score", color="brand", hover_name="title")
    with right:
        chart(ranked.dropna(subset=["rating"]), "scatter", "Rating vs ranking", x="rating", y="position", color="platform", hover_name="title")
        chart(brand_stats.dropna(subset=["visibility"]), "bar", "Visibility by brand", x="brand", y="visibility")

with explorer:
    search = st.text_input("Search product title", placeholder="Enter a product or brand name")
    products = query_products(DB_PATH, filters, search)
    cards([("Filtered products", len(products)), ("Average price", products.price.mean()), ("Average rating", products.rating.mean())])
    cols = ["title", "brand", "price", "rating", "reviews", "platform", "position", "discount_pct", "visibility_score", "link"]
    top = products[products.position.notna()].sort_values(["position", "rating", "reviews"], ascending=[True, False, False]).head(10)
    if not top.empty:
        st.subheader("Top 10 observed search placements")
        st.dataframe(top[cols], hide_index=True, use_container_width=True)
    st.subheader("All matching products")
    st.caption("Click any column header to sort. Missing values mean the source did not provide a usable observation.")
    st.dataframe(products[cols], hide_index=True, use_container_width=True, column_config={"link": st.column_config.LinkColumn("Product link")})
    st.download_button("Download filtered CSV", products.to_csv(index=False), "filtered_products.csv", "text/csv")
    left, right = st.columns(2)
    with left:
        chart(products.dropna(subset=["rating"]), "scatter", "Product rating vs price", x="price", y="rating", color="platform", hover_name="title")
    with right:
        chart(products.dropna(subset=["position", "reviews"]), "scatter", "Product reviews vs ranking", x="reviews", y="position", size="visibility_score", color="platform", hover_name="title")

with st.expander("Explore all 30 EDA answers"):
    answers = answer_eda_questions(df)
    question = st.selectbox("Analysis question", list(answers), format_func=lambda key: key.replace("_", " ").title())
    st.write(answers[question])
with st.expander("Data cleaning report"):
    report_path = settings.reports_dir / "cleaning_report.json"
    if report_path.exists():
        st.json(json.loads(report_path.read_text()))
