.PHONY: all test build format check lint clean

all: check test

check: lint

lint:
	ruff check .

test:
	pytest
	nox -s tests

build:
	uv build

format:
	isort .
	ruff format .

clean:
	rm -rf .pytest_cache .nox .ruff_cache dist build __pycache__ .mypy_cache .coverage htmlcov .coverage.* *.egg-info
