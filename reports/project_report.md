# Brand Visibility Intelligence - project report

Sources: {'csv': 1226}. Rows: 1226. Observed rankings: 0. Known discounts: 0. Missing metrics are unavailable.


## Objective
Analyze product assortment, pricing, ratings and observed search visibility using a simple Streamlit app backed by SQLite.

## Workflow
CSV and Google Shopping results -> normalize and concatenate -> clean and engineer features -> cleaned CSV + SQLite -> six dashboard tabs + reports. One API request per keyword; no scheduled paid requests.

## Results
- HP has the most listings (157; 12.8% of this selection). Compare its assortment before expanding competing products.
- Croma has the highest observed average rating (3.83/5). Review sample sizes and customer feedback before prioritizing that platform.
- Search positions are absent. Collect ranked API results before making visibility recommendations.
- Discount/ranking comparisons need observed prices and ranks in both discounted and non-discounted groups.
- Results describe the supplied listings, not sales, market share, or causal drivers of ranking.

## Data quality
1320 input rows; 94 duplicate offers removed; 207 retained prices imputed; 13 prices capped at 383160.0.

## Limitations
Currency is unspecified unless established by the source. No cross-currency conversion is performed. Absent search ranks and original prices remain missing. Discount share uses only known discounts. Brands are inferred heuristically. Assortment count is not sales or market share. API extraction requires a user-provided key and is only live-verified when an actual request succeeds.

## Deliverables
Source code and tests; cleaned_products.csv; SQLite database; six-tab app; 30 cleaning answers; 30 EDA answers; generated Markdown report.

## Reproduction
Set the local CSV path, API key, currency and market in .env. Run python pipeline.py to combine both sources, then python -m streamlit run app.py.

## API reference
https://serpapi.com/google-shopping-api