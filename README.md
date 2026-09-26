# Brand Visibility — assignment project

This project follows the PDF tasks: Google Shopping API extraction, CSV integration, cleaning, feature engineering, SQL storage, 30 EDA questions, business insights, and a six-tab Streamlit dashboard.

## Task-based structure

```text
BrandVisibility/
├── data_collection.py   # Task 1: get Google Shopping API products
├── data_cleaning.py     # Tasks 2–5: align, merge, clean, derive features
├── database.py          # Task 6: save and query SQLite
├── eda.py               # Task 7: answer 30 EDA questions and generate insights
├── app.py               # Task 8: six-tab Streamlit dashboard
├── report.py            # Task 9: cleaning answers and project findings
├── pipeline.py          # Run the CSV + API steps in order
├── paths.py             # Local file locations
├── data/                # Original CSV, API cache, clean CSV and database
├── reports/             # Cleaning/EDA answers and project report
├── screenshots/         # Dashboard screenshots required by the PDF
├── test_project.py      # Optional checks, in one file
├── requirements.txt
├── .env.example
└── README.md
```

No package installation, framework scaffolding or CI setup is required.

## Setup in VS Code

Open this folder, then open Terminal → New Terminal:

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Your CSV belongs at `data/source_products.csv` (already present locally).
Open `.env` (copy `.env.example` on a new computer) and set:

- `SERPAPI_KEY`: your SerpAPI key.
- `CSV_CURRENCY` / `API_COUNTRY`: match the actual CSV currency: `INR`/`in`, `USD`/`us`, or `GBP`/`gb`.
- Optional `SEARCH_KEYWORDS`: comma-separated search terms; otherwise the first three CSV keywords are used.

## Run the assignment

```bash
python pipeline.py
python -m streamlit run app.py
```

Open http://localhost:8501.

Both the fixed CSV and API results are combined automatically. There is no upload screen. API results are cached to avoid repeated requests. Run `python pipeline.py --refresh-api` for fresh API data (one request per keyword). Filters do not make API calls.

The pipeline produces:

- `data/processed/cleaned_products.csv`
- `data/database/brand_visibility.db`
- `reports/cleaning_report.json`
- `reports/cleaning_answers.md` — all 30 cleaning questions
- `reports/eda_answers.md` — all 30 EDA questions
- `reports/project_report.md` — findings and limitations

The included PDF and screenshots are the earlier 24 September CSV-only evidence. They are retained because the brief requires a report and screenshots; refresh them after the live combined run. They do not prove successful API collection. Missing product ranks/ratings/original prices remain unknown.

**Pending:** add your API key and actual CSV currency to run and verify live combined data. No live API success is claimed. Input CSVs, API caches and credentials stay local.

## Optional verification

```bash
python -m pip install pytest
python -m pytest test_project.py -q
```
