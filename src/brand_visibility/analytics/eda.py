from __future__ import annotations

import numpy as np
import pandas as pd


def answer_eda_questions(df: pd.DataFrame) -> dict[str, object]:
    """Return reproducible answers/data for every EDA question in the brief."""
    g_brand = df.groupby("brand", observed=True)
    g_platform = df.groupby("platform", observed=True)
    discounted = df[df["discount_pct"] > 0]
    top = df[df["position"] <= 10]
    numeric = df[["price", "rating", "reviews", "position", "discount_pct"]].corr(numeric_only=True)
    return {
        "01_products_per_keyword": df["keyword"].value_counts(),
        "02_overall_average_price": df["price"].mean(),
        "03_price_distribution": df["price"].describe(),
        "04_average_rating": df["rating"].mean(),
        "05_review_distribution": df["reviews"].describe(),
        "06_most_frequent_brand": df["brand"].value_counts().idxmax(),
        "07_brand_highest_visibility": g_brand["visibility_score"].mean().idxmax(),
        "08_average_position_by_brand": g_brand["position"].mean().sort_values(),
        "09_brands_most_in_top_10": top["brand"].value_counts(),
        "10_brand_highest_rating": g_brand["rating"].mean().sort_values(ascending=False),
        "11_price_by_brand": g_brand["price"].describe(),
        "12_price_range_distribution": df["price_range"].value_counts(),
        "13_price_position_correlation": numeric.loc["price", "position"],
        "14_average_price_by_platform": g_platform["price"].mean().sort_values(),
        "15_highest_price_by_keyword": df.loc[df.groupby("keyword")["price"].idxmax(), ["keyword", "title", "price"]],
        "16_percent_discounted": 100 * (df["discount_pct"] > 0).mean(),
        "17_discounted_vs_ranking": df.groupby(df["discount_pct"] > 0)["position"].mean(),
        "18_brand_highest_discount": g_brand["discount_pct"].mean().sort_values(ascending=False),
        "19_platform_highest_discount": g_platform["discount_pct"].mean().sort_values(ascending=False),
        "20_discount_rating_correlation": numeric.loc["discount_pct", "rating"],
        "21_platform_most_products": df["platform"].value_counts(),
        "22_platform_highest_rating": g_platform["rating"].mean().sort_values(ascending=False),
        "23_platform_lowest_price": g_platform["price"].mean().sort_values(),
        "24_average_position_by_platform": g_platform["position"].mean().sort_values(),
        "25_brand_by_platform": pd.crosstab(df["platform"], df["brand"]),
        "26_position_distribution": df["position"].describe(),
        "27_highest_visibility_products": df.nlargest(10, "visibility_score")[["title", "brand", "visibility_score"]],
        "28_rating_position_correlation": numeric.loc["rating", "position"],
        "29_reviews_position_correlation": numeric.loc["reviews", "position"],
        "30_top_rank_factor_comparison": pd.DataFrame({
            "top_10_mean": top[["price", "rating", "reviews"]].mean(),
            "other_mean": df[df["position"] > 10][["price", "rating", "reviews"]].mean(),
        }),
    }


def business_insights(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return ["No products match the current filters."]
    top_brand = df["brand"].value_counts().idxmax()
    best_platform = df.groupby("platform")["rating"].mean().idxmax()
    visible_brand = df.groupby("brand")["visibility_score"].mean().idxmax()
    discount_rank = df.groupby(df["discount_pct"] > 0)["position"].mean()
    rank_note = "better" if len(discount_rank) == 2 and discount_rank.get(True, np.inf) < discount_rank.get(False, np.inf) else "not better"
    return [
        f"{top_brand} has the broadest assortment in the selected market.",
        f"{visible_brand} has the strongest average search visibility.",
        f"{best_platform} has the highest average customer rating.",
        f"Discounted products have {rank_note} average rankings than non-discounted products.",
    ]

