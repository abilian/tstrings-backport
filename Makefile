.PHONY: all test build format check lint clean

all: check test

check: lint

lint:
	ruff check .

test:
	pytest
	nox -s tests

format:
	isort .
	ruff format .

clean:
	rm -rf .pytest_cache .nox .ruff_cache dist build __pycache__ .mypy_cache .coverage htmlcov .coverage.* *.egg-info

build: clean
	uv build

publish: build
	uv publish 
