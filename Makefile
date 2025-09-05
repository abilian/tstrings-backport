.PHONY: all test build format check lint clean

all: check test

check: lint

lint:
	ruff check .
	ruff format . --check

format:
	ruff check . --fix
	ruff format .

test:
	uv run --python 3.9 pytest
	uv run --python 3.10 pytest
	uv run --python 3.11 pytest
	uv run --python 3.12 pytest
	uv run --python 3.13 pytest
	uv run --python 3.14 pytest

build: clean
	uv build

clean:
	rm -rf .pytest_cache .ruff_cache dist build __pycache__ .mypy_cache .coverage htmlcov .coverage.* *.egg-info

publish: build
	uv publish 
