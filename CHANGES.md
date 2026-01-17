# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub CI configuration based on nox
- SourceHut CI integration
- `py.typed` marker for PEP 561 compliance (thanks @NickCrews)
- Test for bogus format specifier error handling (thanks @NickCrews)
- `assert_templates_equal()` test helper function (thanks @NickCrews)
- Nox configuration for testing against multiple Python versions
- Type checkers (ty, pyrefly, mypy) to the development workflow

### Fixed
- Type errors in the codebase

## [0.1.2] - 2025-09-05

### Added
- GitHub Actions workflow for testing and building
- Clean target in Makefile to remove build artifacts and caches

### Changed
- Updated dependencies
- Improved Makefile organization

## [0.1.1] - 2025-08-05

### Added
- Makefile with test, build, format, check, and all targets
- Initial README with usage, features, examples, and contribution info
- MIT License
- Noxfile for running tests with nox

### Changed
- Replaced nox with uv for dependency management (thanks @NickCrews)
- Replaced isort with ruff for import sorting (thanks @NickCrews)
- Made `INTERPOLATION_RE` private (thanks @NickCrews)
- Enforced RUF checks in ruff (thanks @NickCrews)

### Fixed
- Made regex less greedy to fix parsing issues (thanks @NickCrews)
- Implemented `__hash__()` via `id(self)` for Template and Interpolation (thanks @NickCrews)
- Various fixes for debug specifier and multiline expression handling
- Fixed ruff warnings

## [0.1.0] - 2025-08-04

### Added
- Initial release
- `t()` function for creating template strings
- `Template` class emulating `string.templatelib.Template` from PEP 750
- `Interpolation` class emulating `string.templatelib.Interpolation` from PEP 750
- Support for f-string-like syntax with interpolations
- Support for conversion specifiers (`!r`, `!s`, `!a`)
- Support for format specifiers
- Support for debug specifier (`=`)
- Pytest-based test suite
