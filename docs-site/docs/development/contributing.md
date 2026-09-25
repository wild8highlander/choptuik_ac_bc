# Contributing

See [CONTRIBUTING.md](https://github.com/wild8highlander/choptuik_ac_bc/blob/main/CONTRIBUTING.md)
in the repository root for the full contribution guidelines.

## Quick Workflow

1. **Fork** the repository on GitHub
2. **Branch**: `git checkout -b feature/my-feature`
3. **Commit** with conventional commit messages
4. **Push** and open a Pull Request
5. **CI** runs automatically — all checks must pass
6. **Review** — at least one approval required

## Code Style

- **Python**: `ruff` + `black` formatting, `mypy` type checking
- **Julia**: JuliaFormatter.jl
- **Java**: Google Java Format
- **TypeScript/React**: Prettier + ESLint

## Pre-commit Hooks

Install pre-commit hooks for automated quality checks:

```bash
pip install pre-commit
pre-commit install
```

This runs `ruff`, `mypy`, and formatters on every commit.
