.PHONY: install dev test lint type-check format build manifest clean api-run

install:
	pip install -e .

dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest --cov=moac_qmm --cov-report=term-missing

lint:
	ruff check src/ tests/ examples/ scripts/

format:
	ruff format src/ tests/ examples/ scripts/
	ruff check --fix src/ tests/ examples/ scripts/

type-check:
	mypy src/moac_qmm

manifest:
	python scripts/validate_manifest.py

build:
	python -m build

api-run:
	uvicorn moac_qmm.api:app --reload --port 8000

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/ htmlcov/ coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
