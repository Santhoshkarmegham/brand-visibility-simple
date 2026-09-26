"""Reproducible assignment answers and an honest source/coverage summary."""
from pathlib import Path

import pandas as pd

from eda import answer_eda_questions, business_insights


def cleaning_answers(df, r):
    profiles = r["input_profiles"]
    return [
        ("Dataset size", f"Input: {r['input_rows']} rows. Original input column counts: {[p['columns'] for p in profiles]}. Aligned columns: {r['input_columns']}. Output: {len(df)} rows, {len(df.columns)} columns."),
        ("Original data types", str([p['dtypes'] for p in profiles])),
        ("Numeric columns stored as text", str(r['numeric_text_columns'])),
        ("Columns containing missing values", str([p['missing_counts'] for p in profiles])),
        ("Missing percentages", str([p['missing_percent'] for p in profiles])),
        ("Handling missing price, rating and reviews", f"Price uses the keyword median then global median; {r['price_values_imputed']} retained prices were imputed. Unobserved ratings/reviews remain null and are excluded from means; they are not zero satisfaction/engagement."),
        ("Missing delivery", "Fill blank/missing delivery with Unknown."),
        ("Incorrect numeric types", f"Original numeric-as-text columns: {r['numeric_text_columns']}; final types: {r['output_dtypes']}"),
        ("Safe numeric conversion", "Strip currency symbols, grouping commas and whitespace; require a complete numeric value; parse with errors=coerce. Do not extract a misleading partial number from a monthly installment string."),
        ("Invalid text values", f"Not Available, many and other invalid numeric text become missing. Counts: {r['invalid_numeric_text']}"),
        ("Duplicate rows", f"Exact duplicates before cleaning: {r['exact_duplicate_rows']}."),
        ("Duplicate identity", "keyword + cleaned title + standardized platform + uncapped numeric price; retain the first occurrence. Different platform offers remain distinct."),
        ("Duplicate treatment", f"Removed {r['duplicate_rows_removed']} duplicate offers after normalization and before price capping."),
        ("Negative and zero prices", f"Found {r['non_positive_prices']}; treat them as missing, then apply the documented median policy."),
        ("Outlier detection", f"Use the 99th price percentile ({r['price_cap_99th_percentile']}); {r['outliers_capped']} prices exceed it."),
        ("Other invalid values", f"Invalid ratings: {r['invalid_ratings']}; reviews: {r['invalid_reviews']}; positions: {r['invalid_positions']}. Set invalid observations to null. Original price below selling price: {r['original_price_below_sale_price']}; exclude from discount calculations."),
        ("Price distribution", str(r['price_distribution_before_cap'])),
        ("Extreme prices", f"{r['outliers_capped']} values above the percentile cap. See price_before_cap for their original cleaned amounts."),
        ("Remove or cap outliers", "Cap price at the 99th percentile. Keep price_before_cap for audit. Discounts use observed pre-cap prices so capping does not invent a promotion. This pooled cap can compress legitimate expensive categories."),
        ("Title noise", f"{r['title_noise_rows']} input titles contain characters outside the allowed title character set."),
        ("Title standardization", "Remove punctuation noise such as !!!; collapse repeated spaces and trim. Preserve useful product punctuation and model numbers."),
        ("Text formatting inconsistencies", str(r['categorical_values_before'])),
        ("Platform consistency", "Trim/collapse whitespace and title-case names; normalize eBay and Best Buy spellings. amazon and AMAZON become Amazon."),
        ("Categorical normalization", "Keywords are lowercase; platforms and delivery use title case. Missing categories are Unknown."),
        ("Delivery consistency", f"Original delivery labels: {r['categorical_values_before']['delivery']}. Standardize case/whitespace; preserve the actual delivery claim."),
        ("Remaining missing values", str(r['remaining_missing_values']) + ". These unknown observations are intentional, not fabricated."),
        ("Numeric usability", "Prices and ratings are numeric; reviews and position are nullable integers. SQL stores absent values as NULL."),
        ("Business validity", f"Removed {r['rows_removed_missing_title_or_price']} rows without usable title/price. Retained prices are positive, ratings bounded 0-5, observed ranks positive integers, and discounts derived only from valid observed prices. Currency is not encoded in CSV; do not combine different currencies."),
        ("Unrated/unreviewed products", "Retain them for assortment analysis. Exclude missing observations from rating/review averages; report observed coverage. Never fabricate search positions."),
        ("Additional features", "Infer brand from known brand names or first title token; derive 100/position visibility, top-10 indicator, exact-boundary price/rating ranges, discount percentage, price_imputed and price_before_cap. Brand inference is heuristic."),
    ]


def render_value(value):
    if isinstance(value, (pd.DataFrame, pd.Series)):
        return "\n".join(line.rstrip() for line in value.to_string().splitlines())
    return str(value)


def export_reports(df, report, folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    provenance = (f"Sources: {report['sources']}. Rows: {len(df)}. Observed rankings: {report['ranked_rows']}. "
                  f"Known discounts: {report['discount_known_rows']}. Missing metrics are unavailable.\n")
    if set(report['sources']) == {'demo'}:
        provenance += "DEMO DATA: synthetic examples; not live market findings.\n"
    blocks = ["# Data cleaning - 30 answers", provenance]
    for i, (question, answer) in enumerate(cleaning_answers(df, report), 1):
        blocks.append(f"## {i:02d}. {question}\n\n{answer}\n")
    (folder / 'cleaning_answers.md').write_text('\n\n'.join(blocks))
    blocks = ["# EDA - 30 answers", provenance,
              "NaN, <NA>, or empty results mean insufficient observed data, not zero. Correlation does not establish causation. Lower position is better, so a negative position correlation indicates association with better ranking."]
    for key, value in answer_eda_questions(df).items():
        blocks.append(f"## {key.replace('_', ' ').title()}\n\n```text\n{render_value(value)}\n```\n")
    (folder / 'eda_answers.md').write_text('\n\n'.join(blocks))
    blocks = ["# Brand Visibility Intelligence - project report", provenance,
              "## Objective\nAnalyze product assortment, pricing, ratings and observed search visibility using a simple Streamlit app backed by SQLite.",
              "## Workflow\nCSV and Google Shopping results -> normalize and concatenate -> clean and engineer features -> cleaned CSV + SQLite -> six dashboard tabs + reports. One API request per keyword; no scheduled paid requests.",
              "## Results\n" + '\n'.join('- ' + insight for insight in business_insights(df)),
              "## Data quality\n" + f"{report['input_rows']} input rows; {report['duplicate_rows_removed']} duplicate offers removed; {report['price_values_imputed']} retained prices imputed; {report['outliers_capped']} prices capped at {report['price_cap_99th_percentile']}.",
              "## Limitations\nCurrency is unspecified unless established by the source. No cross-currency conversion is performed. Absent search ranks and original prices remain missing. Discount share uses only known discounts. Brands are inferred heuristically. Assortment count is not sales or market share. API extraction requires a user-provided key and is only live-verified when an actual request succeeds.",
              "## Deliverables\nSource code and tests; cleaned_products.csv; SQLite database; six-tab app; 30 cleaning answers; 30 EDA answers; generated Markdown report.",
              "## Reproduction\nSet the local CSV path, API key, currency and market in .env. Run python pipeline.py to combine both sources, then python -m streamlit run app.py.",
              "## API reference\nhttps://serpapi.com/google-shopping-api"]
    (folder / 'project_report.md').write_text('\n\n'.join(blocks))
