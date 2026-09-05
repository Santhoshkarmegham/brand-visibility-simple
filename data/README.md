# Data zones

- `raw/`: immutable API and supplied source extracts.
- `interim/`: optional transformation staging.
- `processed/`: cleaned, analysis-ready exports.
- `database/`: SQLite serving layer used by the dashboard.

Generated data is ignored by Git; keep only approved fixtures in version control.
