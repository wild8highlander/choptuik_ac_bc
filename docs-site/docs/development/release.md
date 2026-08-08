# Release Process

This document describes the release process for the Choptuik AC/BC package, including version numbering, changelog management, and PyPI publishing.

## Version Numbering

The project follows **Semantic Versioning** (SemVer):

\[
\text{version} = \text{MAJOR}.\text{MINOR}.\text{PATCH}
\]

| Component | Incremented When |
|-----------|-----------------|
| **MAJOR** | Breaking changes to the public API |
| **MINOR** | New features that are backward-compatible |
| **PATCH** | Bug fixes that are backward-compatible |

Pre-release versions use the format `MAJOR.MINOR.PATCH-alpha.N` or `MAJOR.MINOR.PATCH-beta.N` for alpha and beta releases respectively.

## Release Checklist

### 1. Prepare the Release Branch

```bash
git checkout main
git pull upstream main
git checkout -b release/vX.Y.Z
```

### 2. Update Version

Edit the version in `pyproject.toml` and `src/choptuik_ac_bc/__init__.py`:

```toml
# pyproject.toml
[project]
version = "X.Y.Z"
```

```python
# src/choptuik_ac_bc/__init__.py
__version__ = "X.Y.Z"
```

### 3. Update the Changelog

Add a new section to `CHANGELOG.md` following the [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- Description of new features

### Changed
- Description of changed behavior

### Fixed
- Description of bug fixes

### Deprecated
- Features scheduled for removal in the next major release
```

### 4. Run the Full Verification Suite

```bash
# Standard verification
python -m choptuik_ac_bc.verify_all --precision 50

# Enhanced verification
python -m choptuik_ac_bc.verify_enhanced --precision 100 --parallel 4

# Full test suite
pytest tests/ -v --cov=choptuik_ac_bc
```

All checks must pass before proceeding.

### 5. Build and Inspect the Distribution

```bash
python -m build
```

This creates `dist/choptuik_ac_bc-X.Y.Z-py3-none-any.whl` and `dist/choptuik_ac_bc-X.Y.Z.tar.gz`. Inspect the contents:

```bash
tar -tzf dist/choptuik_ac_bc-X.Y.Z.tar.gz
```

Verify that all source files, license, and README are included.

### 6. Commit and Tag

```bash
git add -A
git commit -m "Release vX.Y.Z"
git tag -a vX.Y.Z -m "Release vX.Y.Z"
```

### 7. Push and Publish

```bash
git push upstream release/vX.Y.Z --tags
```

The tag push triggers the [release workflow](ci-cd.md) which automatically:

1. Builds the distributions.
2. Publishes to **PyPI** (production).
3. Creates a **GitHub Release** with auto-generated release notes from the changelog.

### 8. Merge the Release Branch

After confirming the PyPI package is available:

```bash
pip install choptuik-ac-bc==X.Y.Z
python -c "import choptuik_ac_bc; print(choptuik_ac_bc.__version__)"
```

Merge the release branch into `main` and delete it:

```bash
git checkout main
git merge release/vX.Y.Z
git push upstream main
git branch -d release/vX.Y.Z
```

## Hotfix Process

For urgent bug fixes against the current release:

1. Branch from the release tag: `git checkout -b hotfix/X.Y.Z+1 vX.Y.Z`
2. Apply the minimal fix and update the PATCH version.
3. Follow steps 4–8 above with the new version number.

!!! warning "Breaking Changes"
    Never include breaking changes in a PATCH or MINOR release. If a fix requires a breaking API change, it must go in the next MAJOR release with a proper deprecation cycle.

!!! note "Pre-Releases"
    For beta testing new features, publish to [TestPyPI](https://test.pypi.org/) first:
    ```bash
    twine upload --repository testpypi dist/*
    ```
    Users can install from TestPyPI for testing:
    ```bash
    pip install --index-url https://test.pypi.org/simple/ choptuik-ac-bc
    ```
