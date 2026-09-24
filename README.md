# Brand Visibility Intelligence

A simple-to-run, six-tab Streamlit dashboard backed by SQLite. It covers product assortment, prices, ratings, platforms, search visibility, and product exploration from the assignment brief.

## Run

Requires Python 3.10 or newer (Python 3.12 recommended).

```bash
python -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://localhost:8501. The included cleaned CSV snapshot loads automatically on a fresh checkout; you can choose demo data in the sidebar. The previous one-page version remains at `simple_app.py`.

## Current data and remaining inputs

The local `brand_visibility.csv` found in Downloads was used for this delivery: **1,320 input rows -> 1,226 cleaned rows**. Confirm that this is the intended assignment dataset; the brief names `brand_dirty_dataset.csv`, which was not attached.

This CSV has **no search positions or original prices**. Ranking, visibility and discount metrics therefore correctly show **N/A**. Ratings/reviews remain unknown where absent. Currency is unspecified, so prices use source units without a dollar symbol.

**Live extraction is implemented and tested with controlled API responses, but a real API run has not been verified: no SerpAPI key was configured.** Set the key locally to finish that requirement; never commit it.

## Load CSV and/or API data

Expand **Load data** in the sidebar. Upload a CSV, optionally select live SerpAPI results, choose keywords and API market, then click **Load data**. CSV and API prices must use the same currency. Changing filters never triggers paid API requests.

For live extraction, copy `.env.example` to `.env` and set `SERPAPI_KEY` from your own account. See the [SerpAPI Google Shopping documentation](https://serpapi.com/google-shopping-api).

A batch entry point also exports the clean CSV, database and reports:

```bash
python pipeline.py --csv /path/to/products.csv
# Only combine sources with the same currency (batch defaults to US API results):
python pipeline.py --csv /path/to/usd-products.csv --api --keywords laptop phone
```

One API page is requested per keyword. API errors are reported without revealing the key. Monthly installment offers are excluded. Ranking is never inferred from CSV row order.

## Deliverables

- [Cleaned dataset](deliverables/cleaned_products.csv) and [SQLite database](deliverables/brand_visibility.db)
- [Project report PDF](output/pdf/brand_visibility_project_report.pdf)
- [30 cleaning answers](reports/cleaning_answers.md) and [30 EDA answers](reports/eda_answers.md)
- [Cleaning diagnostics](reports/cleaning_report.json)
- [Dashboard screenshots](deliverables/screenshots)
- [Requirement coverage](docs/task-completion.md)

The `deliverables/` files are a dated snapshot of the CSV run. New loads update `data/processed/`, `data/database/` and `reports/`; refresh the snapshot and PDF before a later submission.

## Design and assumptions

`app.py` starts the app; `pipeline.py` runs a batch. Reusable code is in `src/brand_visibility/` (data cleaning, API extraction, SQL, analytics, dashboard). Filtering uses parameterized SQL queries. Product Explorer includes every matching product, sorting, search, top observed placements and CSV download.

Missing prices use keyword medians then an overall median. Duplicates use keyword/title/platform/uncapped price. Prices are capped at the 99th percentile with uncapped values retained. Discounts use observed uncapped selling/original prices. Missing ratings, reviews, ranks and discounts remain null. Price/rating buckets have exact boundaries. Brands are inferred heuristically. See the cleaning report for limitations and counts.

## Verify

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
```

Nine tests cover cleaning edge cases, API responses/errors, CSV/API merging, SQL filtering, report exports, and six-tab interactions with and without ranked data. GitHub Actions runs the same tests. These tests do not spend API credits.

To rebuild the PDF, install `reportlab` and run `python scripts/build_project_report.py`. That script contains the dated submission narrative; update its source/verification notes if the inputs change.
