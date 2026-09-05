# Architecture

```text
CSV source ─┐
            ├─> extraction/alignment ─> cleaning/features ─> processed CSV
SerpAPI ────┘                                  │
                                              └─> SQLite ─> SQL filters ─> Streamlit
                                                            └─> EDA/report export
```

## Boundaries

- `brand_visibility.data`: I/O, schema alignment, cleaning, features and persistence.
- `brand_visibility.analytics`: reusable analysis and insight functions with no UI dependency.
- `brand_visibility.dashboard`: Streamlit and Plotly presentation layer.
- `brand_visibility.config`: environment settings and filesystem paths.
- `brand_visibility.pipeline`: orchestration; detailed behavior stays in focused modules.
- `scripts`: thin operational entry points.
- `tests`: automated checks separate from application code.

The dashboard reads the serving database and never performs live API calls. Ingestion failures therefore do not make the analytical UI unavailable.
