# Task datasets

- `source_products.csv`: original CSV input.
- `raw/`: cached Google Shopping API results and their search settings.
- `processed/cleaned_products.csv`: merged and cleaned dataset.
- `database/brand_visibility.db`: SQLite database for the dashboard.

Run `python pipeline.py` from the project folder. Analysis answers are written to the root `reports/` folder. A CSV-only database is not shown as a combined result.
