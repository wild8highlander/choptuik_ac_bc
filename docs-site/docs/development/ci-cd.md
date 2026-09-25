# CI/CD Pipelines

## Workflows

| Workflow | Trigger | Description |
|---|---|---|
| `ci.yml` | Push to main, PR | Full test suite with coverage + Codecov upload |
| `lint.yml` | Push, PR | ruff + mypy + black check |
| `pages.yml` | Push to main | Build & deploy MkDocs to GitHub Pages |
| `release.yml` | Tag `v*` | Build artifacts + sigstore signing + GitHub Release |

## CI Workflow Details

The `ci.yml` workflow runs on:

- **Python**: 3.10, 3.11, 3.12
- **OS**: ubuntu-latest, macos-latest, windows-latest

Steps:
1. Checkout repository
2. Install Python + dependencies
3. Run `ruff check`
4. Run `mypy`
5. Run `pytest --cov`
6. Upload coverage to Codecov
7. Run verification in non-interactive mode

## Pages Deployment

The `pages.yml` workflow:

1. Installs MkDocs Material + plugins
2. Builds the documentation site
3. Deploys to `gh-pages` branch
4. Available at: https://wild8highlander.github.io/choptuik_ac_bc/

## Release Signing

Release artifacts are signed with [sigstore](https://sigstore.dev/):

1. Python sdist and wheel are built
2. Each artifact is signed using `sigstore sign`
3. Signatures and certificates are uploaded as release assets
4. Verification: `sigstore verify --certificate-identity=aslan08_05@mail.ru`
