# Development

This section covers the development workflow for the Choptuik AC/BC project, including contribution guidelines, testing infrastructure, CI/CD pipeline, and release process.

## Project Structure

The repository is organized as follows:

```
choptuik-ac-bc/
├── src/
│   └── choptuik_ac_bc/       # Main package source
│       ├── __init__.py
│       ├── choptyuk_formula.py
│       ├── dirac_operator.py
│       ├── klein_curve.py
│       ├── spinor_phases.py
│       ├── qnm.py
│       ├── hypothesis.py
│       ├── surfaces.py
│       ├── enhanced_verification.py
│       ├── verify_all.py
│       ├── verify_enhanced.py
│       ├── simulator.py
│       ├── plots.py
│       └── report_writer.py
├── tests/                    # Test suite
├── docs-site/                # Documentation site (MkDocs)
├── pyproject.toml            # Project metadata and build config
└── .github/workflows/        # CI/CD pipelines
```

## Development Topics

| Topic | Description |
|-------|-------------|
| [Contributing](contributing.md) | How to set up a development environment and submit contributions |
| [Testing](testing.md) | Test suite structure, running tests, and coverage requirements |
| [CI/CD](ci-cd.md) | Continuous integration and deployment pipeline documentation |
| [Release Process](release.md) | Version numbering, changelog generation, and PyPI publishing |

## Getting Started

To start contributing to the project:

1. Fork the repository on GitHub.
2. Clone your fork and set up the development environment (see [Contributing](contributing.md)).
3. Create a feature branch and make your changes.
4. Run the test suite to ensure nothing is broken (see [Testing](testing.md)).
5. Submit a pull request with a clear description of your changes.

!!! tip "Code Style"
    The project follows **PEP 8** with line length 88 (Black default). All code must pass `ruff check` and `ruff format --check` before merging. Type annotations are required for all public functions.
