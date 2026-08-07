# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Author:** Ishak Khamzatovich Isaev (Исаев Исхак Хамзатович) — aslan08_05@mail.ru
**Repository:** https://github.com/wild8highlander/choptuik_ac_bc

## [1.2.0] - 2026-08-07

### Added
- Python: modern `pyproject.toml` with ruff, mypy, pytest, coverage configuration
- Python: comprehensive pytest test suite (test_choptyuk.py) with 20+ tests
- Julia: test suite (runtests.jl) with Test.jl
- Jupyter notebook: interactive verification with plots (notebooks/choptyuk_verification.ipynb)
- README: Mermaid architecture diagram showing project structure
- README: Codecov badge
- CI: pytest + coverage + Codecov upload in ci.yml
- CI: Julia Pkg.test() in ci.yml
- Discussions: Welcome and Release Announcement discussions created
- CITATION.cff: updated to v1.1.0 with 2026-08-07 date
- .zenodo.json: updated to v1.1.0 with 2026 year

### Changed
- CITATION.cff version: 1.0.0 → 1.1.0
- .zenodo.json version: 1.0.0 → 1.1.0

### Fixed
- Scorecard workflow: moved `id-token: write` from top-level to job-level permissions
- Scorecard workflow: fixed `permissions: read-all` as top-level default
- README: removed duplicate DOI badge
- README: updated Zenodo DOI badge with placeholder for actual DOI

## [1.1.0] - 2026-08-07

### Changed
- License changed from MIT to Isaev Proprietary License
- Full authorship retention and attribution requirements
- Commercial use and redistribution prohibited without written permission

### Fixed
- Julia Project.toml: removed deprecated [targets] section
- Java SimulationService: added missing java.time.Instant import
- Java PlotService: fixed ambiguous List import (java.awt.List vs java.util.List)
- Python: fixed 157+ ruff linting errors (style, imports, type hints)
- CI workflow: generated package-lock.json for npm caching
- Greeting workflow: fixed actions/first-interaction version compatibility
- Labeler workflow: added required enable-versioned-regex input
- DOI badge: updated from pending placeholder to Zenodo search link
- License badge: changed from MIT to Isaev Proprietary

## [1.0.0] - 2024-01-01

### Added
- Complete verification of all monograph results
- Python implementation with interactive CLI menu
- Julia implementation with interactive REPL menu
- Java Spring Boot web application with REST API
- Next.js interactive visualization dashboard
- Multi-format report generation (DOCX, PDF, TXT, MD, CSV, HTML, JSON)
- High-resolution plot generation (600 DPI PNG + PDF/SVG)
- 64 spinor structure enumeration and analysis
- Bolza, Bring, and Macbeath surface comparisons
- LIGO/Virgo QNM predictions for GW150914, GW170104, GW170814, GW190521
- Custom hypothesis testing configuration
- Arbitrary-precision parameter customization
- Complete execution logging in all reports
- CI/CD pipeline with GitHub Actions
- Original monograph documents (EN/RU, DOCX/PDF)
