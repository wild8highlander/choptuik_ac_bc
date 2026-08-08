# Changelog

All notable changes to the Choptuik AC/BC project are documented in this file. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-03-04

### Added

- **Enhanced verification suite** (`choptuik_ac_bc.verify_enhanced`): Interval-arithmetic based verification with certified error bounds, cross-module consistency checks, and three-level verification hierarchy (algebraic, interval-arithmetic, cross-module).
- **K3 surfaces module** (`choptuik_ac_bc.surfaces`): Computation of the intersection form on \(H^2(X, \mathbb{Z})\), Picard number, Néron–Severi lattice, and transcendental lattice for the Klein quartic K3 surface.
- **Hypothesis testing module** (`choptuik_ac_bc.hypothesis`): Bayesian model comparison between standard Kerr QNM predictions and spinor-corrected predictions, with support for LIGO–Virgo gravitational-wave event loading and ringdown extraction.
- **Report writer module** (`choptuik_ac_bc.report_writer`): Structured report generation in JSON, Markdown, CSV, and plain text formats from verification results and analysis outputs.
- **Interactive simulator** (`choptuik_ac_bc.simulator`): Full-featured interactive CLI menu with navigation for all modules, configurable precision, and color output.
- **Plotting module** (`choptuik_ac_bc.plots`): Visualization utilities for Dirac operator spectrum, spinor phases, ringdown comparison plots, and K3 lattice diagrams. Output in PNG, SVG, and PDF formats.
- **Parallel execution** support for enhanced verification: distribute independent checks across multiple CPU cores via `--parallel` flag or `n_workers` parameter.
- **Configuration file** support: `~/.choptuik/config.toml` for persisted settings (precision, solver, output format, etc.).

### Changed

- **Breaking**: Refactored `compute_phases()` return type from `list[float]` to `list[mpf]` for consistency with arbitrary-precision arithmetic throughout the package. Callers using standard `float` operations on the result must explicitly convert.
- **Breaking**: Renamed `DiracSpectrum.eigenvalues` to `DiracSpectrum.values` for consistency with the `SpectralData` naming convention.
- Improved `compute_critical_exponent()` performance by ~3× using Gauss–Legendre quadrature with adaptive node selection instead of fixed-order quadrature.
- Updated `compute_spectrum()` to support both `arnoldi` and `dense` solvers, with automatic selection based on matrix size.
- Enhanced `KleinQuartic` class with `is_on_curve()` method and automorphism generator enumeration.
- Minimum Python version increased from 3.9 to **3.10** for `match` statement support and improved type hint syntax.

### Fixed

- Corrected spinor-phase closure verification at precisions above 100 digits, where accumulated rounding in the modular reduction was causing spurious `WARN` results.
- Fixed `compute_spectrum()` returning eigenvalues in unsorted order when using the Arnoldi solver with `n_modes > 50`.
- Resolved memory leak in enhanced verification when running multiple successive checks within the same Python process (finalizer was not releasing `mpmath` context).
- Fixed `plot_spectrum()` crash on Windows when `output` path contained non-ASCII characters.

### Deprecated

- `compute_phases_float()` — use `compute_phases()` with explicit `float()` conversion instead. Will be removed in v3.0.0.
- `--old-report-format` CLI flag — use `--format json` or `--format markdown` instead. Will be removed in v3.0.0.

### Removed

- Removed Python 3.8 compatibility shims (f-strings, `typing_extensions` backports) that were deprecated in v1.5.0.
- Removed `legacy_verification` module (deprecated since v1.3.0). Use `verify_all` or `verify_enhanced` instead.

## [1.5.0] - 2024-09-15

### Added

- Initial LIGO event data loading support via `hypothesis` module.
- `tanh_sinh` integration method for Choptuik formula computation.

### Changed

- Improved documentation with mathematics section and LaTeX rendering.
- Updated `mpmath` dependency to >=1.3.0 for interval arithmetic support.

### Fixed

- Fixed precision loss in `compute_critical_exponent()` at very high precision (>200 digits).

## [1.0.0] - 2024-03-01

### Added

- Initial release with core modules: `choptyuk_formula`, `dirac_operator`, `klein_curve`, `spinor_phases`, `qnm`, `verify_all`.
- Standard verification suite with tolerance-based checks.
- Arbitrary-precision arithmetic via `mpmath` throughout all computation modules.
