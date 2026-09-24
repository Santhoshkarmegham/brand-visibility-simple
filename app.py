"""Run with: python -m streamlit run app.py"""

import pandas as pd
import streamlit as st

from src.brand_visibility.data.sample_data import generate_sample_data
from src.brand_visibility.data.transform import clean_and_engineer

st.set_page_config(page_title="Brand Visibility", layout="wide")
st.title("Brand Visibility")
st.write("Compare product prices, ratings, and search visibility across brands.")
uploaded = st.sidebar.file_uploader("Upload a product CSV", type="csv")
st.sidebar.caption("Leave this empty to explore sample data.")
try:
    raw = pd.read_csv(uploaded) if uploaded is not None else generate_sample_data()
    products, report = clean_and_engineer([raw])
except (ValueError, TypeError, pd.errors.ParserError, UnicodeDecodeError):
    st.error("Could not read these products. Check the CSV format and include title, price, rating, reviews, and position columns with valid values.")
    st.stop()

if uploaded is None:
    st.info("Showing generated sample data. Upload a CSV to explore your own products.")
for column, label in [("brand", "Brand"), ("platform", "Platform"), ("keyword", "Keyword")]:
    selected = st.sidebar.multiselect(label, sorted(products[column].dropna().unique()))
    if selected:
        products = products[products[column].isin(selected)]
search = st.text_input("Search products", placeholder="Enter part of a product name")
if search:
    products = products[products.title.str.contains(search, case=False, regex=False, na=False)]
if products.empty:
    st.info("No products match. Clear the search or change your filters.")
    st.stop()

count, price, rating, visibility = st.columns(4)
count.metric("Products", f"{len(products):,}")
price.metric("Average price", f"${products.price.mean():,.2f}")
rating.metric("Average rating", f"{products.rating.mean():.1f} / 5")
visibility.metric("Average visibility", f"{products.visibility_score.mean():.1f}")
left, right = st.columns(2)
with left:
    st.subheader("Products by brand")
    st.bar_chart(products.brand.value_counts().rename("Products"))
with right:
    st.subheader("Visibility by brand")
    st.bar_chart(products.groupby("brand").visibility_score.mean().rename("Visibility"))
st.caption("Visibility = 100 ÷ search position. Higher scores mean better search placement.")
st.subheader("Products")
columns = ["title", "brand", "platform", "keyword", "price", "rating", "reviews", "position", "visibility_score"]
table = products.sort_values("position")[columns]
st.dataframe(table, hide_index=True, use_container_width=True)
st.download_button("Download filtered CSV", table.to_csv(index=False), "products.csv", "text/csv")
with st.expander("How the data is cleaned"):
    st.write("Numeric text is converted to numbers, missing values use medians, duplicates are removed, and extreme prices are capped at the 99th percentile. Brands are inferred from product titles.")
    st.write(f"Loaded {report['input_rows']} rows; removed {report['duplicate_rows_removed']} duplicates.")
