from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

BRANDS = {
    "laptop": ["Apple", "Dell", "HP", "Lenovo", "Asus", "Acer"],
    "phone": ["Apple", "Samsung", "Google", "OnePlus", "Motorola", "Xiaomi"],
    "headphones": ["Sony", "Bose", "JBL", "Apple", "Sennheiser", "Beats"],
    "smartwatch": ["Apple", "Samsung", "Garmin", "Fitbit", "Amazfit", "Google"],
}
PLATFORMS = ["Amazon", "Walmart", "Best Buy", "Target", "eBay"]


def generate_sample_data(rows_per_keyword: int = 45, seed: int = 42) -> pd.DataFrame:
    """Create deterministic, realistic demo data when source files are unavailable."""
    rng = random.Random(seed)
    rows: list[dict] = []
    for keyword, brands in BRANDS.items():
        for position in range(1, rows_per_keyword + 1):
            brand = rng.choice(brands)
            platform = rng.choices(PLATFORMS, weights=[36, 23, 18, 12, 11])[0]
            base = {"laptop": 850, "phone": 650, "headphones": 180, "smartwatch": 260}[keyword]
            raw_price = round(max(25, rng.gauss(base, base * 0.38)), 2)
            discount = rng.choice([0, 0, 0, 5, 10, 12, 15, 20, 25, 30])
            price = round(raw_price * (1 - discount / 100), 2)
            rating = round(min(5, max(2.8, rng.gauss(4.25, 0.38))), 1)
            reviews = max(0, int(rng.lognormvariate(6.0, 1.35)))
            model = rng.choice(["Pro", "Plus", "Air", "Ultra", "Max", "Essential"])
            rows.append(
                {
                    "keyword": keyword,
                    "title": f"{brand} {model} {keyword.title()} {rng.randint(10, 99)}",
                    "price": price,
                    "raw_price": raw_price,
                    "rating": rating,
                    "reviews": reviews,
                    "platform": platform,
                    "position": position,
                    "delivery": rng.choice(["Free Delivery", "Prime", "Paid", "Unknown"]),
                    "link": f"https://example.com/{keyword}/{position}",
                    "thumbnail": "",
                    "source": "demo",
                }
            )
    return pd.DataFrame(rows)


def write_sample_csv(path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    generate_sample_data().to_csv(path, index=False)
    return path

