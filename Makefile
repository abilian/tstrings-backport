.PHONY: all test build format check lint

all: format check test build

test:
	nox -s tests

build:
	uv build

format:
	ruff format .
	isort .

check: lint

lint:
	ruff check .
	isort --check-only .
