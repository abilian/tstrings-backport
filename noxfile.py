import nox

@nox.session(python=["3.12"])
def tests(session):
    session.install(".[dev]")
    session.run("pytest", "tests", external=True)
