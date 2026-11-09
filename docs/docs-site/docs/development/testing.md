# Testing & Coverage

## Running Tests

```bash
# All tests
cd python/
python -m pytest tests/ -v

# Specific test markers
python -m pytest tests/ -m math -v        # Mathematical correctness tests
python -m pytest tests/ -m verification   # Verification tests
python -m pytest tests/ -m "not slow"     # Skip slow tests
```

## Coverage

```bash
# Generate coverage report
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=xml

# HTML report
python -m pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

## Codecov Integration

Coverage reports are automatically uploaded to [Codecov](https://codecov.io/gh/wild8highlander/choptuik_ac_bc)
on every push to `main` and every pull request.

The coverage threshold is set to **80%** minimum. Pull requests that
drop coverage below this threshold will fail CI.

## Coverage Configuration

See `pyproject.toml` for the coverage configuration:

```toml
[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "*/__init__.py"]

[tool.coverage.report]
show_missing = true
fail_under = 80
```
