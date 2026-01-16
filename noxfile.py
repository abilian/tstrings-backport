import nox

PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13", "3.14"]
DEFAULT_PYTHON = "3.12"

nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["check", "test"]


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """Run the test suite."""
    uv_sync(session)
    session.run("pytest", "tests", *session.posargs)


@nox.session(python=DEFAULT_PYTHON)
def check(session: nox.Session) -> None:
    """Run all checks (lint, typecheck, tests)."""
    uv_sync(session)

    # Lint
    session.run("ruff", "check")
    session.run("ruff", "format", "--check")

    # Type check
    session.run("ty", "check", "src")
    session.run("pyrefly", "check", "src")
    session.run("mypy", "src")
    # should be: session.run("mypy", "--strict", "src")


def uv_sync(session: nox.Session):
    session.run("uv", "sync", "--all-groups", "--all-extras", "--active", external=True)
