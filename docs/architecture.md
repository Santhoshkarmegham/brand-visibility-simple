# Architecture

`app.py` -> six-tab Streamlit dashboard -> parameterized SQLite queries.

`pipeline.py` or the app's Load data panel -> CSV / SerpAPI -> align and concatenate -> clean and engineer -> SQLite + clean CSV + reports.

- `data/extract.py`: authenticated Google Shopping requests; safe errors; excludes installment offers.
- `data/transform.py`: shared cleaning rules and provenance/coverage diagnostics.
- `data/database.py`: SQLite persistence and SQL filters. SQL NULL becomes numeric NaN after reads.
- `analytics/eda.py`: all 30 analyses and descriptive business insights.
- `analytics/reporting.py`: 30 cleaning answers, 30 EDA answers and report narrative.
- `dashboard/app.py`: six tabs, CSV/API loading, observed coverage, SQL-backed controls and download.

Absent observations remain missing. Loading demo data is explicit. API requests happen only on load; filter changes do not call the API. All tabs share the current local database. This is a local single-user application, not a multi-tenant service.

The checked-in deliverables are a dated snapshot. Runtime changes do not automatically rewrite that snapshot or its PDF. Legacy Word guides and Windows documentation predate this version; use the root README and task-completion checklist as the current instructions.
