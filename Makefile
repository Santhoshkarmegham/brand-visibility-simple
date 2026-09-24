.PHONY: install pipeline dashboard eda test lint clean

install:
	python -m pip install -e ".[dev]"
pipeline:
	python -m brand_visibility.pipeline
dashboard:
	python -m streamlit run app.py
advanced-dashboard:
	python -m streamlit run src/brand_visibility/dashboard/app.py
eda:
	python scripts/export_eda.py
test:
	pytest -q
lint:
	ruff check src tests scripts
clean:
	python -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__') if '.venv' not in p.parts]"
