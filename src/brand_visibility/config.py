from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    """Centralized filesystem and environment configuration."""

    project_root: Path = PROJECT_ROOT
    raw_data_dir: Path = PROJECT_ROOT / "data" / "raw"
    interim_data_dir: Path = PROJECT_ROOT / "data" / "interim"
    processed_data_dir: Path = PROJECT_ROOT / "data" / "processed"
    database_dir: Path = PROJECT_ROOT / "data" / "database"
    reports_dir: Path = PROJECT_ROOT / "reports"

    @property
    def database_path(self) -> Path:
        configured = os.getenv("BRAND_DB_PATH")
        return Path(configured).expanduser() if configured else self.database_dir / "brand_visibility.db"


settings = Settings()
