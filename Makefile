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
    -Remove-Item -Recurse -Force __pycache__ -ErrorAction SilentlyContinue
    -Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
    -Get-ChildItem -Recurse -File -Filter *.pyc | Remove-Item -Force
