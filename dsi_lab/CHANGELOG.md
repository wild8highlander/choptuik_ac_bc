# Changelog — dsi_lab

All notable changes of the DSI laboratory package. The format follows
Keep a Changelog; statuses inside the package always distinguish
proved / verified / refuted / hypothesis.

## [2.0.0] — 2026-10-12

The professional-edition release: the package becomes a fully
self-contained laboratory with its own engine, identity, formalization
and cross-language core.

### Added

- **`dsilab/`** — the reusable, typed engine package: constants,
  the Kunz defect (`leavitt.py`), the {7,3} census (`census.py`),
  continued fractions (`convergents.py`) and the committed-verdict
  auditor (`dsilab.validate`, 13 checks).
- **`lean4/`** — Lean 4 + Mathlib formalization: the exact stratum
  (census, CF of 9/224, the e-ladder, 549/49) proved sorry-free;
  theorems A/B/C axiom-anchored to the numerical verification;
  corollary D derived from theorem A; axiom-audit file.
- **`multilang/`** — the ten-check exact core in six languages:
  C, C++, JavaScript verified byte-identical (committed
  `reference_output.txt`); Rust, Go, Julia sources.
- **`logo/`** — theme-aware logo (light/dark, PNG 600 dpi + SVG) and
  square avatars, generated deterministically by `scripts/make_logo.py`.
- **`animations/`** — four launch animations × en/ru × (MP4 + GIF),
  generated from the committed verdicts by `scripts/make_animations.py`.
- **`docs/`** — theory, the theorem layer (EN/RU), methods, and the
  claim ledger (27 rows with honesty statuses).
- **`monograph/`** — the EN and RU monographs (Tectonic PDFs + LaTeX
  sources) superseding the short reports as the citable form.
- **`logs/`** — logged verification runs (`scripts/run_logged.sh`,
  `make verify` output with hashes of the committed JSONs).
- **`pyproject.toml`** — ruff/black/mypy/pytest configuration;
  **CITATION.cff**, **VERSION**.

### Changed

- `Makefile` extended: `validate`, `figures`, `logo`, `animations`,
  `monograph`, `multilang`, `lint`, `lint-mypy` targets; `verify` now
  runs test + validate + run.
- `README.md` rewritten to the professional edition (badge wall,
  bilingual mirror `README.ru.md`, repository map, theorem table).
- Root repository map updated for the new subfolders.

### Verified

- 51 pytest checks (package + theorems + smoke), `dsilab.validate` 13/13,
  ruff/black/mypy clean, C/C++/JS outputs byte-identical.

## [1.0.0] — earlier history

The seven experiments, the bilingual figures, the reports and the
original README were assembled in the parent repository history; see
`git log` and the reports in `reports/` for the earlier state.
