PY_SRC=code-quality-tools/src

lint:
	flake8 .
	pylint $(PY_SRC)

typecheck:
	mypy .

security:
	bandit -c bandit.yaml -r $(PY_SRC)

test:
	pytest -q --maxfail=1 --disable-warnings

coverage:
	pytest -q --maxfail=1 --disable-warnings --cov=$(PY_SRC) --cov-report=term-missing --cov-report=xml:coverage.xml

all: lint typecheck security coverage

.PHONY: lint typecheck security test coverage all
