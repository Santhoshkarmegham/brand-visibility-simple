from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd


TABLE = "products"


def connect(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def save_products(df: pd.DataFrame, db_path: str | Path) -> None:
    stored = df.copy()
    for column in stored.select_dtypes(include=["category"]).columns:
        stored[column] = stored[column].astype("string")
    with connect(db_path) as conn:
        stored.to_sql(TABLE, conn, if_exists="replace", index=False)
        conn.executescript(
            "CREATE INDEX IF NOT EXISTS idx_product_filters ON products(keyword, platform, brand, price, rating, position);"
        )


def query_products(db_path: str | Path, filters: dict[str, Any] | None = None, search: str = "") -> pd.DataFrame:
    filters = filters or {}
    clauses, params = ["1=1"], []
    for column in ["brand", "platform", "price_range", "rating_range", "keyword"]:
        values = filters.get(column) or []
        if values:
            clauses.append(f"{column} IN ({','.join('?' for _ in values)})")
            params.extend(values)
    for column in ["price", "rating", "position"]:
        bounds = filters.get(column)
        if bounds:
            clauses.append(f"{column} BETWEEN ? AND ?")
            params.extend([bounds[0], bounds[1]])
    if search.strip():
        clauses.append("LOWER(title) LIKE ?")
        params.append(f"%{search.strip().lower()}%")
    sql = f"SELECT * FROM {TABLE} WHERE {' AND '.join(clauses)}"
    with connect(db_path) as conn:
        return pd.read_sql_query(sql, conn, params=params)


def filter_options(db_path: str | Path) -> dict[str, list]:
    with connect(db_path) as conn:
        return {
            column: [row[0] for row in conn.execute(f"SELECT DISTINCT {column} FROM {TABLE} WHERE {column} IS NOT NULL ORDER BY {column}")]
            for column in ["brand", "platform", "price_range", "rating_range", "keyword"]
        }

