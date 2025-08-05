.PHONY: all test build format check lint

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
