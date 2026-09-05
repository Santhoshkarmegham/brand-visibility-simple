.PHONY: install pipeline dashboard eda test lint clean

install:
	python -m pip install -e ".[dev]"
pipeline:
	python -m brand_visibility.pipeline
dashboard:
	streamlit run src/brand_visibility/dashboard/app.py
eda:
	python scripts/export_eda.py
test:
	pytest -q
lint:
	ruff check src tests scripts
clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
