.PHONY: all test build format check lint clean

# This allows you to run tests/linting/etc. in different python versions, eg:
# `make test` runs in existing python version
# `make test python=3.10` runs in python 3.10
# `make test python=all` runs in all supported python versions
# KEEP THIS IN SYNC WITH .github/workflows/ci.yml
PYTHON_VERSIONS = 3.9 3.10 3.11 3.12 3.13 3.14
python ?=

all:
	@make test
	@make check

check: lint

lint:
ifeq ($(python),all)
	$(foreach ver,$(PYTHON_VERSIONS),uv run --python $(ver) ruff check . &&) true
	$(foreach ver,$(PYTHON_VERSIONS),uv run --python $(ver) ruff format . --check &&) true
	$(foreach ver,$(PYTHON_VERSIONS),uv run --python $(ver) ty check src &&) true
	$(foreach ver,$(PYTHON_VERSIONS),uv run --python $(ver) pyrefly check src &&) true
	$(foreach ver,$(PYTHON_VERSIONS),uv run --python $(ver) mypy src &&) true
else ifdef python
	uv run --python $(python) ruff check .
	uv run --python $(python) ruff format . --check
	uv run --python $(python) ty check src
	uv run --python $(python) pyrefly check src
	uv run --python $(python) mypy src
else
	uv run ruff check .
	uv run ruff format . --check
	uv run ty check src
	uv run pyrefly check src
	uv run mypy src
endif

format:
ifeq ($(python),all)
	$(foreach ver,$(PYTHON_VERSIONS),uv run --python $(ver) ruff format . &&) true
	$(foreach ver,$(PYTHON_VERSIONS),uv run --python $(ver) ruff check . --fix &&) true
	$(foreach ver,$(PYTHON_VERSIONS),uv run --python $(ver) ruff format . &&) true
else ifdef python
	uv run --python $(python) ruff format .
	uv run --python $(python) ruff check . --fix
	uv run --python $(python) ruff format .
else
	uv run ruff format .
	uv run ruff check . --fix
	uv run ruff format .
endif

test:
ifeq ($(python),all)
	$(foreach ver,$(PYTHON_VERSIONS),uv run --python $(ver) pytest &&) true
else ifdef python
	uv run --python $(python) pytest
else
	uv run pytest
endif

build: clean
ifeq ($(python),all)
	$(foreach ver,$(PYTHON_VERSIONS),uv build --python $(ver) &&) true
else ifdef python
	uv build --python $(python)
else
	uv build
endif

clean:
	rm -rf .pytest_cache .ruff_cache dist build __pycache__ .mypy_cache .coverage htmlcov .coverage.* *.egg-info

publish: build
	uv publish
