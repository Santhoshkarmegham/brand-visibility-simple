from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from brand_visibility.analytics.eda import business_insights
from brand_visibility.config import settings
from brand_visibility.data.database import filter_options, query_products
from brand_visibility.pipeline import run_pipeline


st.set_page_config(page_title="Brand Visibility Intelligence", page_icon="◈", layout="wide")
DB_PATH = str(settings.database_path)
COLORS = ["#6C63FF", "#18B6A4", "#FFB547", "#EF6A79", "#4D8BFF", "#A16AE8"]

st.markdown(
    """
    <style>
    .stApp {background: #f5f7fb; color: #172033}
    [data-testid="stSidebar"] {background: #111827}
    [data-testid="stSidebar"] * {color: #f8fafc}
    [data-testid="stMetric"] {background:white;border:1px solid #e6eaf2;border-radius:14px;padding:16px;box-shadow:0 7px 24px #16223b0b}
    div[data-testid="stPlotlyChart"] {background:white;border:1px solid #e6eaf2;border-radius:14px;padding:8px}
    .block-container {padding-top:1.5rem;max-width:1500px}
    h1,h2,h3 {letter-spacing:-.025em}
    .hero {background:linear-gradient(120deg,#10172a,#3430a0 65%,#635bff);padding:28px 34px;border-radius:18px;color:white;margin-bottom:16px}
    .hero h1 {margin:0;color:white}.hero p{margin:.45rem 0 0;color:#dfe3ff}
    .insight {background:#fff;border-left:4px solid #6C63FF;padding:12px 14px;margin:8px 0;border-radius:8px}
    </style>
    """,
    unsafe_allow_html=True,
)


def ensure_database() -> None:
    if not Path(DB_PATH).exists():
        run_pipeline(None, [], False, DB_PATH)


@st.cache_data(show_spinner=False)
def options(db_mtime: float) -> dict[str, list]:
    return filter_options(DB_PATH)


def card_row(items: list[tuple[str, str]]) -> None:
    for column, (label, value) in zip(st.columns(len(items)), items):
        column.metric(label, value)


def money(value: float) -> str:
    return f"${value:,.2f}" if pd.notna(value) else "-"


def base_layout(fig, height: int = 340):
    fig.update_layout(
        height=height, margin=dict(l=20, r=20, t=55, b=20), paper_bgcolor="white",
        plot_bgcolor="white", colorway=COLORS, legend_title_text="",
    )
    fig.update_xaxes(gridcolor="#eef1f6")
    fig.update_yaxes(gridcolor="#eef1f6")
    return fig


ensure_database()
opts = options(Path(DB_PATH).stat().st_mtime)

with st.sidebar:
    st.markdown("## ◈ Intelligence Hub")
    st.caption("SQL-connected global filters")
    selected_brand = st.multiselect("Brand", opts["brand"])
    selected_platform = st.multiselect("Platform", opts["platform"])
    selected_price_range = st.multiselect("Price range", opts["price_range"])
    selected_rating_range = st.multiselect("Rating range", opts["rating_range"])
    selected_keyword = st.multiselect("Keyword", opts["keyword"])
    position = st.slider("Position (ranking)", 1, 50, (1, 50))
    st.divider()
    st.caption("Every selection is translated into a parameterized SQLite query.")

filters = {
    "brand": selected_brand, "platform": selected_platform, "price_range": selected_price_range,
    "rating_range": selected_rating_range, "keyword": selected_keyword, "position": position,
}
df = query_products(DB_PATH, filters)

st.markdown(
    "<div class='hero'><h1>Brand Visibility Intelligence</h1><p>Search performance, pricing, customer trust and competitive position in one view.</p></div>",
    unsafe_allow_html=True,
)
if df.empty:
    st.warning("No products match these filters. Widen one or more sidebar selections.")
    st.stop()

overview, brands, pricing, platforms, visibility, explorer = st.tabs(
    ["Overview", "Brand Insights", "Pricing Analysis", "Platform Analysis", "Visibility & Ranking", "Product Explorer"]
)

with overview:
    card_row([
        ("Total products", f"{len(df):,}"), ("Average price", money(df.price.mean())),
        ("Average rating", f"{df.rating.mean():.2f} ★"), ("Total reviews", f"{df.reviews.sum():,.0f}"),
        ("Avg visibility", f"{df.visibility_score.mean():.1f}"),
    ])
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(base_layout(px.histogram(df, x="price", nbins=30, title="Price distribution", color_discrete_sequence=COLORS)), use_container_width=True)
        per_keyword = df.keyword.value_counts().rename_axis("keyword").reset_index(name="products")
        st.plotly_chart(base_layout(px.bar(per_keyword, x="keyword", y="products", title="Products per keyword", color="keyword", color_discrete_sequence=COLORS)), use_container_width=True)
    with c2:
        share = df.platform.value_counts().rename_axis("platform").reset_index(name="products")
        st.plotly_chart(base_layout(px.pie(share, names="platform", values="products", hole=.55, title="Platform share", color_discrete_sequence=COLORS)), use_container_width=True)
        reviews = df.assign(engagement=pd.cut(df.reviews, [-1, 100, 1000, 10000, float("inf")], labels=["Low", "Growing", "High", "Viral"]))
        engagement = reviews.engagement.value_counts().rename_axis("engagement").reset_index(name="products")
        st.plotly_chart(base_layout(px.bar(engagement, x="engagement", y="products", title="Review engagement distribution", color="engagement", color_discrete_sequence=COLORS)), use_container_width=True)
    st.subheader("What the data says")
    for insight in business_insights(df):
        st.markdown(f"<div class='insight'>{insight}</div>", unsafe_allow_html=True)

with brands:
    brand_stats = df.groupby("brand", as_index=False).agg(products=("title", "count"), avg_rating=("rating", "mean"), avg_visibility=("visibility_score", "mean"), avg_position=("position", "mean"))
    top_brand = brand_stats.loc[brand_stats.products.idxmax(), "brand"]
    rated_brand = brand_stats.loc[brand_stats.avg_rating.idxmax(), "brand"]
    visible_brand = brand_stats.loc[brand_stats.avg_visibility.idxmax(), "brand"]
    card_row([("Total brands", f"{df.brand.nunique():,}"), ("Top brand", top_brand), ("Highest rated", rated_brand), ("Best visibility", visible_brand)])
    c1, c2 = st.columns(2)
    c1.plotly_chart(base_layout(px.bar(brand_stats.nlargest(15, "products"), x="brand", y="products", title="Brand vs product count", color="products", color_continuous_scale="Purples")), use_container_width=True)
    c2.plotly_chart(base_layout(px.bar(brand_stats.nlargest(15, "avg_rating"), x="brand", y="avg_rating", title="Brand vs average rating", color="avg_rating", color_continuous_scale="Teal")), use_container_width=True)
    top10 = df[df.position <= 10].brand.value_counts().head(15).rename_axis("brand").reset_index(name="top_10_products")
    st.plotly_chart(base_layout(px.bar(top10, x="top_10_products", y="brand", orientation="h", title="Brands appearing most often in top 10", color="top_10_products", color_continuous_scale="Bluered")), use_container_width=True)

with pricing:
    high = df.loc[df.price.idxmax()]
    low = df.loc[df.price.idxmin()]
    card_row([("Average price", money(df.price.mean())), ("Highest price", money(high.price)), ("Lowest price", money(low.price)), ("Discounted products", f"{(df.discount_pct.gt(0).mean() * 100):.1f}%")])
    c1, c2 = st.columns(2)
    c1.plotly_chart(base_layout(px.histogram(df, x="price", nbins=30, color="price_range", title="Price distribution", color_discrete_sequence=COLORS)), use_container_width=True)
    c2.plotly_chart(base_layout(px.scatter(df, x="price", y="position", color="platform", hover_name="title", title="Price vs ranking", color_discrete_sequence=COLORS)), use_container_width=True)
    c1.plotly_chart(base_layout(px.scatter(df, x="price", y="rating", color="brand", hover_name="title", title="Price vs rating", color_discrete_sequence=COLORS)), use_container_width=True)
    ranges = df.price_range.value_counts().rename_axis("price_range").reset_index(name="products")
    c2.plotly_chart(base_layout(px.bar(ranges, x="price_range", y="products", title="Price range distribution", color="price_range", color_discrete_sequence=COLORS)), use_container_width=True)
    discounts = df.groupby("brand", as_index=False).discount_pct.mean().nlargest(15, "discount_pct")
    platform_discount = df.groupby("platform", as_index=False).discount_pct.mean()
    c1.plotly_chart(base_layout(px.bar(discounts, x="brand", y="discount_pct", title="Average discount by brand", color="discount_pct", color_continuous_scale="Purples")), use_container_width=True)
    c2.plotly_chart(base_layout(px.bar(platform_discount, x="platform", y="discount_pct", title="Average discount by platform", color="platform", color_discrete_sequence=COLORS)), use_container_width=True)

with platforms:
    stats = df.groupby("platform", as_index=False).agg(products=("title", "count"), avg_price=("price", "mean"), avg_rating=("rating", "mean"), avg_position=("position", "mean"))
    card_row([("Total platforms", str(len(stats))), ("Best platform", stats.loc[stats.avg_rating.idxmax(), "platform"]), ("Cheapest platform", stats.loc[stats.avg_price.idxmin(), "platform"]), ("Most products", stats.loc[stats.products.idxmax(), "platform"])])
    c1, c2 = st.columns(2)
    for target, title, slot in [("products", "Platform vs product count", c1), ("avg_rating", "Platform vs average rating", c2), ("avg_price", "Platform vs average price", c1), ("avg_position", "Platform vs average ranking", c2)]:
        slot.plotly_chart(base_layout(px.bar(stats, x="platform", y=target, title=title, color="platform", color_discrete_sequence=COLORS)), use_container_width=True)
    matrix = df.groupby(["platform", "brand"], as_index=False).size()
    st.plotly_chart(base_layout(px.bar(matrix, x="platform", y="size", color="brand", title="Brand distribution per platform", color_discrete_sequence=COLORS)), use_container_width=True)

with visibility:
    best = df.loc[df.position.idxmin(), "title"]
    card_row([("Average position", f"{df.position.mean():.1f}"), ("Best-ranked product", best), ("Avg visibility", f"{df.visibility_score.mean():.1f}"), ("Products in top 10", f"{df.top_10.mean() * 100:.1f}%")])
    c1, c2 = st.columns(2)
    c1.plotly_chart(base_layout(px.histogram(df, x="position", nbins=30, title="Ranking distribution", color_discrete_sequence=COLORS)), use_container_width=True)
    c2.plotly_chart(base_layout(px.scatter(df, x="rating", y="position", color="platform", hover_name="title", title="Rating vs ranking", color_discrete_sequence=COLORS)), use_container_width=True)
    c1.plotly_chart(base_layout(px.scatter(df, x="reviews", y="position", size="visibility_score", color="brand", hover_name="title", title="Reviews vs ranking", color_discrete_sequence=COLORS)), use_container_width=True)
    vis = df.groupby("brand", as_index=False).visibility_score.mean().nlargest(15, "visibility_score")
    c2.plotly_chart(base_layout(px.bar(vis, x="brand", y="visibility_score", title="Visibility score by brand", color="visibility_score", color_continuous_scale="Purples")), use_container_width=True)

with explorer:
    search = st.text_input("Search product title", placeholder="Try Apple, Pro, laptop...")
    products = query_products(DB_PATH, filters, search)
    card_row([("Filtered products", f"{len(products):,}"), ("Average price", money(products.price.mean())), ("Average rating", f"{products.rating.mean():.2f} ★")])
    if not products.empty:
        top_products = products.sort_values(["visibility_score", "rating", "reviews"], ascending=[False, False, False]).head(10)
        display_cols = ["title", "brand", "price", "rating", "reviews", "platform", "position", "discount_pct", "visibility_score", "link"]
        st.subheader("Top 10 products")
        st.dataframe(
            top_products[display_cols], use_container_width=True, hide_index=True,
            column_config={"price": st.column_config.NumberColumn(format="$%.2f"), "rating": st.column_config.ProgressColumn(min_value=0, max_value=5), "link": st.column_config.LinkColumn("Product link")},
        )
        c1, c2 = st.columns(2)
        c1.plotly_chart(base_layout(px.scatter(products, x="price", y="rating", color="platform", hover_name="title", title="Rating vs price", color_discrete_sequence=COLORS)), use_container_width=True)
        c2.plotly_chart(base_layout(px.scatter(products, x="reviews", y="position", size="visibility_score", color="platform", hover_name="title", title="Reviews vs ranking", color_discrete_sequence=COLORS)), use_container_width=True)
        st.download_button("Download filtered CSV", products.to_csv(index=False), "filtered_products.csv", "text/csv")
