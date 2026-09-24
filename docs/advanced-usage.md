> Historical setup notes. Use the root README for current commands and cleaning rules. Missing ratings and ranks now remain unknown.

# Brand Visibility Intelligence

A production-style e-commerce analytics project implementing API extraction, dirty-CSV integration, ETL, SQLite serving, 30 EDA questions and a six-tab Streamlit dashboard.

## Repository structure

```text
Brand/
├── config/                      # Runtime configuration
├── data/
│   ├── raw/                     # Immutable source extracts
│   ├── interim/                 # Transformation staging
│   ├── processed/               # Clean analysis-ready exports
│   └── database/                # SQLite serving database
├── docs/                        # Architecture notes
├── reports/                     # EDA and cleaning outputs
│   └── figures/                 # Exported charts/screenshots
├── scripts/                     # Operational entry points
├── src/brand_visibility/
│   ├── analytics/               # EDA and business insights
│   ├── dashboard/               # Streamlit UI
│   ├── data/                    # Extract, transform and persistence
│   ├── config.py                # Central settings
│   └── pipeline.py              # ETL orchestration
├── tests/                       # Automated tests
├── Makefile
└── pyproject.toml               # Package and tool configuration
```

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
make pipeline
make advanced-dashboard
```

The dashboard opens at `http://localhost:8501`. Without a CSV or API key, the pipeline creates deterministic demo data.

## Use a dirty CSV

```bash
python -m brand_visibility.pipeline --csv /path/to/brand_dirty_dataset.csv
```

## Combine CSV and live SerpAPI data

Copy `.env.example` to `.env`, supply `SERPAPI_KEY`, then run:

```bash
python -m brand_visibility.pipeline \
  --csv /path/to/brand_dirty_dataset.csv \
  --api \
  --keywords laptop phone headphones smartwatch
```

## EDA, tests and quality

```bash
make eda
make test
make lint
```

The EDA command writes all 30 answers to `reports/eda_answers.md`.

## Cleaning decisions

- Numeric strings are normalized safely; invalid values become missing.
- Missing numeric values use keyword-level medians, then overall medians.
- Unrated products remain because search visibility is still meaningful.
- Non-positive prices/rankings and ratings outside 0-5 are invalid.
- Prices are capped at the 99th percentile and the cap is recorded.
- Duplicate identity is `keyword + title + platform + price`.
- Visibility score is `100 / position`, making rank 1 equal to 100.

See [docs/architecture.md](architecture.md) for component boundaries and data flow.
