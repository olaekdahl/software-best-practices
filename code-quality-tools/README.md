# Code Quality Tools

Hands-on demos for improving and enforcing code quality across four areas:

- Static code analysis: find bugs, vulnerabilities, and code smells without running code
- Linting: enforce style and prevent common mistakes (flake8, Pylint)
- Code coverage: measure how much your tests exercise your code
- Automated code reviews: run quality gates on pull requests and get an AI summary

## Quick start

```bash
# From repo root
python3 -m venv .venv && source .venv/bin/activate
pip install -r code-quality-tools/requirements-dev.txt

# Run everything
make -C code-quality-tools all
```

Key commands (all runnable via the Makefile):

```bash
# Lint
flake8 .
pylint code-quality-tools/src

# Type checks
mypy .

# Security static analysis
bandit -c code-quality-tools/bandit.yaml -r .

# Tests + coverage
pytest -q --maxfail=1 --disable-warnings \
  --cov=code-quality-tools/src --cov-report=term-missing --cov-report=xml:coverage.xml
```

## What’s included

- Config: `.flake8`, `pylintrc`, `mypy.ini`, `.coveragerc`, `bandit.yaml`
- Demo code in `src/` intentionally includes some patterns that tools flag
- Tests in `tests/` for coverage demonstration
- GitHub Actions workflow in `.github/workflows/code-quality.yml`

## Static code analysis

Run tools that parse code ASTs / patterns without executing your program:

```bash
bandit -c code-quality-tools/bandit.yaml -r code-quality-tools/src
``` 

Bandit will highlight insecure uses (e.g., `eval`, weak hash algorithms). Our demo avoids real vulnerabilities but shows how to run the tool.

## Linting

Style & correctness:

```bash
flake8 code-quality-tools/src
pylint code-quality-tools/src
```

Try intentionally adding unused imports or broad exceptions and watch tools flag issues.

## Code coverage

Measure tested lines vs total:

```bash
pytest --cov=code-quality-tools/src --cov-report=term-missing
```

Review the missing lines to guide where more tests add value (avoid chasing 100% blindly).

## Automated code reviews (GitHub Models: gpt-4o)

The workflow posts an AI code review comment on pull requests using GitHub Models (`gpt-4o`).

Notes:
- Requires repository access to GitHub Models. If unavailable, the step is skipped.
- Uses the built-in `GITHUB_TOKEN`; no extra secrets required.

Open a PR changing Python files; the job will:
1. Run lint, type checks, security, tests & coverage.
2. Collect the diff for changed Python files.
3. Send a prompt to the model to summarize issues & suggest improvements.
4. Comment the AI review back onto the PR.

## Makefile targets

```bash
make -C code-quality-tools lint      # flake8 + pylint
make -C code-quality-tools typecheck # mypy
make -C code-quality-tools security  # bandit
make -C code-quality-tools test      # pytest
make -C code-quality-tools coverage  # pytest with coverage reports
make -C code-quality-tools all       # run all quality gates
```

Extend these gates (e.g., add `safety`, `pip-audit`) as your project matures.
