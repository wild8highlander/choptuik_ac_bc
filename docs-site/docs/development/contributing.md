# Contributing Guide

Thank you for your interest in contributing to the Choptuik AC/BC project! This guide covers the development environment setup, code style requirements, and pull request process.

## Development Environment Setup

### Prerequisites

- **Python 3.10+** (3.12 recommended)
- **Git** 2.30+
- **Make** (optional, for convenience targets)

### Step 1 — Fork and Clone

Fork the repository on GitHub, then clone your fork:

```bash
git clone https://github.com/YOUR-USERNAME/choptuik-ac-bc.git
cd choptuik-ac-bc
git remote add upstream https://github.com/original/choptuik-ac-bc.git
```

### Step 2 — Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

### Step 3 — Install in Development Mode

```bash
pip install -e ".[dev,test,docs,ligo]"
```

This installs the package in editable mode along with all development dependencies (linters, formatters, test tools, and documentation builders).

### Step 4 — Verify the Setup

Run the test suite to confirm everything is working:

```bash
python -m pytest tests/ -v
```

## Code Style and Quality

The project enforces the following quality standards:

### Formatting

All code is formatted with **Black** (line length 88) and **isort** for import ordering. Check formatting before committing:

```bash
ruff format src/ tests/
ruff check --fix src/ tests/
```

### Type Checking

All public functions must include **complete type annotations**. Run `mypy` to verify:

```bash
mypy src/choptuik_ac_bc/ --strict
```

### Docstrings

Use **Google-style** docstrings for all public functions and classes:

```python
def compute_critical_exponent(precision: int = 30) -> mpf:
    """Compute the Choptuik critical exponent to the given precision.

    Args:
        precision: Number of decimal digits for arbitrary-precision
            arithmetic. Must be a positive integer.

    Returns:
        The critical exponent γ as an mpmath mpf value.

    Raises:
        ValueError: If precision is not a positive integer.

    Example:
        >>> gamma = compute_critical_exponent(precision=50)
        >>> float(gamma)
        0.3558024155217529
    """
```

## Pull Request Process

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes** with clear, atomic commits.

3. **Run the full quality suite**:
   ```bash
   ruff format src/ tests/
   ruff check src/ tests/
   mypy src/choptuik_ac_bc/ --strict
   pytest tests/ -v --cov=choptuik_ac_bc
   ```

4. **Push to your fork** and open a pull request against `main`.

5. **Respond to review feedback** and update your branch as needed.

### PR Checklist

Before submitting, verify:

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Code coverage does not decrease (`pytest --cov`)
- [ ] Type checking passes (`mypy --strict`)
- [ ] Linting passes (`ruff check`)
- [ ] New public functions have docstrings and type annotations
- [ ] Changes to public API are documented in the changelog

!!! warning "Breaking Changes"
    If your PR introduces a breaking change to the public API, it must be discussed in an issue **before** the PR is submitted. Breaking changes require a deprecation period of at least one minor version release.

## Reporting Bugs

When reporting bugs, please include:

1. The Python version and operating system.
2. The installed package version (`pip show choptuik-ac-bc`).
3. A **minimal reproducible example**—the smallest possible code snippet that triggers the bug.
4. The full traceback (if applicable).
5. Any relevant configuration (precision, solver, etc.).
