import nox

PYTHONS = ["3.9", "3.10", "3.11", "3.12", "3.13"]


@nox.session(python=PYTHONS)
def tests(session):
    session.install(".[dev]")
    session.run("pytest", "tests", external=True)
