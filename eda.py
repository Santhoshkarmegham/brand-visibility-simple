from __future__ import annotations

import pandas as pd


def answer_eda_questions(df: pd.DataFrame) -> dict[str, object]:
    """Return reproducible answers/data for every EDA question in the brief."""
    g_brand = df.groupby("brand", observed=True)
    g_platform = df.groupby("platform", observed=True)
    top = df[df["position"] <= 10]
    numeric = df[["price", "rating", "reviews", "position", "discount_pct"]].corr(numeric_only=True)
    return {
        "01_products_per_keyword": df["keyword"].value_counts(),
        "02_overall_average_price": df["price"].mean(),
        "03_price_distribution": df["price"].describe(),
        "04_average_rating": df["rating"].mean(),
        "05_review_distribution": df["reviews"].describe(),
        "06_most_frequent_brand": df["brand"].value_counts().idxmax(),
        "07_brand_highest_visibility": _best(g_brand["visibility_score"].mean()),
        "08_average_position_by_brand": g_brand["position"].mean().sort_values(),
        "09_brands_most_in_top_10": top["brand"].value_counts(),
        "10_brand_highest_rating": g_brand["rating"].mean().sort_values(ascending=False),
        "11_price_by_brand": g_brand["price"].describe(),
        "12_price_range_distribution": df["price_range"].value_counts(),
        "13_price_position_correlation": numeric.loc["price", "position"],
        "14_average_price_by_platform": g_platform["price"].mean().sort_values(),
        "15_highest_price_by_keyword": df.loc[df.groupby("keyword")["price"].idxmax(), ["keyword", "title", "price"]],
        "16_percent_discounted": 100 * df["discount_pct"].dropna().gt(0).mean(),
        "17_discounted_vs_ranking": df[df.discount_pct.notna()].groupby(df["discount_pct"] > 0)["position"].mean(),
        "18_brand_highest_discount": g_brand["discount_pct"].mean().sort_values(ascending=False),
        "19_platform_highest_discount": g_platform["discount_pct"].mean().sort_values(ascending=False),
        "20_discount_rating_correlation": numeric.loc["discount_pct", "rating"],
        "21_platform_most_products": df["platform"].value_counts(),
        "22_platform_highest_rating": g_platform["rating"].mean().sort_values(ascending=False),
        "23_platform_lowest_price": g_platform["price"].mean().sort_values(),
        "24_average_position_by_platform": g_platform["position"].mean().sort_values(),
        "25_brand_by_platform": pd.crosstab(df["platform"], df["brand"]),
        "26_position_distribution": df["position"].describe(),
        "27_highest_visibility_products": df[df.visibility_score.notna()].nlargest(10, "visibility_score")[["title", "brand", "visibility_score"]],
        "28_rating_position_correlation": numeric.loc["rating", "position"],
        "29_reviews_position_correlation": numeric.loc["reviews", "position"],
        "30_top_rank_factor_comparison": pd.DataFrame({
            "top_10_mean": top[["price", "rating", "reviews"]].mean(),
            "other_mean": df[df["position"] > 10][["price", "rating", "reviews"]].mean(),
        }),
    }


def _best(series: pd.Series) -> str:
    observed = series.dropna()
    return str(observed.idxmax()) if len(observed) else "Unavailable: no observed values"


def business_insights(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return ["No products match the current filters."]
    counts = df.brand.value_counts()
    insights = [f"{counts.idxmax()} has the most listings ({counts.max():,}; {counts.max()/len(df):.1%} of this selection). Compare its assortment before expanding competing products."]
    ratings = df.groupby("platform").rating.mean().dropna()
    if len(ratings):
        insights.append(f"{ratings.idxmax()} has the highest observed average rating ({ratings.max():.2f}/5). Review sample sizes and customer feedback before prioritizing that platform.")
    visibility = df.groupby("brand").visibility_score.mean().dropna()
    if len(visibility):
        insights.append(f"{visibility.idxmax()} leads average visibility ({visibility.max():.1f}). Inspect its top-ranked listings for merchandising ideas.")
    else:
        insights.append("Search positions are absent. Collect ranked API results before making visibility recommendations.")
    observed = df.dropna(subset=["discount_pct", "position"])
    groups = observed.groupby(observed.discount_pct.gt(0)).position.mean()
    if len(groups) == 2:
        insights.append(f"Average position is {groups[True]:.1f} for discounted versus {groups[False]:.1f} for non-discounted listings. This is an association, not evidence that discounts cause better ranking.")
    else:
        insights.append("Discount/ranking comparisons need observed prices and ranks in both discounted and non-discounted groups.")
    insights.append("Results describe the supplied listings, not sales, market share, or causal drivers of ranking.")
    return insights
