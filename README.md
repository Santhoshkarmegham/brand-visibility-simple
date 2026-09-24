# Brand Visibility

A simple Python dashboard for comparing product prices, ratings, and search visibility.

## Run the app

Requires Python 3.10 or newer. From this folder:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On macOS or Linux, use `python3` if `python` is unavailable. You can optionally install into a virtual environment first.

The app opens at http://localhost:8501 with sample data. No API key, database setup, or separate pipeline command is needed.

## What you can do

- Upload a CSV or explore the built-in sample data.
- Filter by brand, platform, or keyword and search product names.
- Compare product counts and average visibility by brand.
- View prices, ratings, reviews, and rankings.
- Download the filtered products as a CSV.

## CSV format

Use these column names. Include at least one valid value in each numeric column (`price`, `rating`, `reviews`, and `position`). Prices are treated as USD; ratings range from 0 to 5; positions start at 1.

```csv
title,keyword,price,rating,reviews,platform,position
Apple Phone,phone,799,4.5,120,Amazon,1
Samsung Phone,phone,699,4.3,95,Walmart,2
```

The app cleans numeric text, fills missing numeric values with medians, removes duplicates, and caps extreme prices. Brand names are inferred from product titles. Visibility is `100 / position`.

## Code

Start with `app.py`. It reuses two small modules in `src/brand_visibility/data/`: `sample_data.py` generates demo products and `transform.py` cleans data and calculates visibility.

The original API pipeline, SQLite database, detailed dashboard, and reports remain available. See [advanced usage](docs/advanced-usage.md) for their setup.
