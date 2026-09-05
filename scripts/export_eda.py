from __future__ import annotations

from pathlib import Path

from brand_visibility.analytics.eda import answer_eda_questions
from brand_visibility.config import settings
from brand_visibility.data.database import query_products


def main() -> None:
    answers = answer_eda_questions(query_products(settings.database_path))
    out = settings.reports_dir / "eda_answers.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    blocks = ["# Brand Visibility - 30 EDA Answers\n"]
    for key, value in answers.items():
        title = key.replace("_", " ").title()
        blocks.append(f"## {title}\n\n```text\n{value}\n```\n")
    out.write_text("\n".join(blocks))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
