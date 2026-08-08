# CI/CD Pipeline

The Choptuik AC/BC project uses **GitHub Actions** for continuous integration and deployment. This document describes the pipeline configuration, triggered workflows, and deployment process.

## Pipeline Overview

The CI/CD pipeline consists of four workflows:

### 1. Test Workflow (`.github/workflows/test.yml`)

**Triggers**: Push to any branch, pull request to `main`

| Step | Description |
|------|-------------|
| Checkout | Clone the repository |
| Python setup | Install Python 3.10, 3.11, 3.12 (matrix) |
| Dependencies | `pip install -e ".[dev,test]"` |
| Lint | `ruff check src/ tests/` |
| Format check | `ruff format --check src/ tests/` |
| Type check | `mypy src/choptuik_ac_bc/ --strict` |
| Tests | `pytest tests/ -v --cov=choptuik_ac_bc` |
| Coverage gate | Fail if coverage < 95% |

The test matrix runs on **Ubuntu**, **macOS**, and **Windows** across all supported Python versions, ensuring cross-platform compatibility.

### 2. Verification Workflow (`.github/workflows/verify.yml`)

**Triggers**: Push to `main`, weekly schedule (Monday 00:00 UTC)

| Step | Description |
|------|-------------|
| Checkout | Clone the repository |
| Python setup | Install Python 3.12 |
| Dependencies | `pip install -e "."` |
| Standard verification | `python -m choptuik_ac_bc.verify_all --precision 30` |
| Enhanced verification | `python -m choptuik_ac_bc.verify_enhanced --precision 50 --parallel 4` |

This workflow runs the mathematical verification suite to catch any regressions in computed values. The weekly cron run ensures that verification is tested even during periods of low development activity.

### 3. Docs Workflow (`.github/workflows/docs.yml`)

**Triggers**: Push to `main`

| Step | Description |
|------|-------------|
| Checkout | Clone the repository |
| Python setup | Install Python 3.12 |
| Dependencies | `pip install -e ".[docs]"` |
| Build docs | `mkdocs build --strict` |
| Deploy docs | `mkdocs gh-deploy --force` (on `main` only) |

The documentation site is built with **MkDocs** using the **Material** theme and deployed to GitHub Pages. The `--strict` flag ensures that any broken links or missing references cause the build to fail.

### 4. Release Workflow (`.github/workflows/release.yml`)

**Triggers**: Push tag matching `v*.*.*`

| Step | Description |
|------|-------------|
| Checkout | Clone the repository |
| Python setup | Install Python 3.12 |
| Build distributions | `python -m build` (sdist + wheel) |
| Publish to PyPI | `twine upload dist/*` |
| Create GitHub release | Auto-generated from changelog |

See [Release Process](release.md) for the full release workflow.

## Branch Protection

The `main` branch is protected with the following rules:

- **Require pull request reviews** (1 approval from a maintainer)
- **Require status checks to pass** (test workflow, lint, type check)
- **Require up-to-date branch** before merging
- **Dismiss stale reviews** on push

## Caching

The CI pipelines use caching to speed up dependency installation:

- **pip cache**: Keyed on `pyproject.toml` hash; caches downloaded packages.
- **mypy cache**: Keyed on source hash; caches type-checking results.

Typical cold-start time is ~5 minutes; cached runs complete in ~2 minutes.

!!! note "Skipping CI"
    You can skip CI on a push by including `[skip ci]` in the commit message. Use this **only** for documentation-only changes or other non-code updates. Do not skip CI for code changes.

!!! warning "Secrets"
    The PyPI API token and other deployment secrets are stored as GitHub repository secrets. Never commit tokens or credentials to the repository.
