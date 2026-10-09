# Changelog — Collapse-Hawking Bridge

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.1.0] — 2026-10-09

The **IVP-15 alignment edition**: every surface of the package — the
two-volume bilingual monograph (8 documents), every README, the
multilang twins, the rendered figures/animations, the ledger — is
brought into exact agreement with the independent verification results
(audit of 2.0.0; findings F-1/F-2/F-3 remediated at 2.0.1), and the
question the audit left open — *why does one formula give different
values at different scales?* — is answered by a new theorem with its
own campaign.

### Added

- **Theorem T10 — the resolution-drift law** (why one formula gives
  different values at scalar-scaled grids): sampling parabolic
  structures flattens their peak by exactly `kappa h^2/8` (worst
  alignment; `kappa h^2/24` on average) and shortens the chord chain
  against the continuum arc — *parabolic structures stretch and
  compress under the curvature of their tension*; by the implicit
  function theorem `A*_N − A*_cont = kappa* alpha^2 h^2/(8s) > 0` —
  the drift EXISTS, is POSITIVE (approach from above), and its leading
  exact channel is O(h²).
- **Campaign C6** (`campaigns/run_c6_drift.py`, ~2 s, deterministic,
  committed inputs only): the drift verdict — ladder analysis
  (monotone drift, `p_eff = 1.140/1.459/1.596` climbing), the
  extrapolation stress test (two-term law REJECTED by its own p_eff
  trajectory ⇒ **no `A*_inf` claimable**), machine verification of the
  two exact lemmas (2.0e-9 / 1.9e-16), and the channel calibration
  (`kappa* = 2728.60` from the committed supercritical profile,
  `s = 413.8` from the C2 scan; exact-channel share 2.6e-3…9.1e-3 —
  sub-dominant; the dominant channel is a labeled hypothesis).
  Artifacts: `c6_drift_verdict.json` + 2 CSVs; Part-C constants
  mirrored; 3 pytest pins (63 tests total).
- `docs/scaling_law.md` — the full derivation of T10.
- `results/scaling_drift/` — the C6 verification report + 8 figures
  (`scripts/make_c6_figures.py`; en/ru × light/dark).
- `figures/logo/` — the package logo (`scripts/make_logo.py`):
  light/dark themes, PNG @ 600 dpi + SVG, drawn from the package's own
  mathematics (nested self-similar parabolas, the bridge arc, the
  photon-ringed horizon).
- `scripts/hires_figures.py --figs` — selective hires regeneration.
- Makefile targets `c6`; CITATION/version surfaces bumped to 2.1.0.

### Fixed

- **Monographs de-staled (the 2.0.0 volumes quoted retracted numbers).**
  The theorems volume now states T1–T10 (was T1–T9) with the remediated
  values; the appendix carries the five-grid ladder, the per-grid C3b
  results, a new part IV.5 (C6) and an audit-informed stage analysis;
  both volumes gained the IVP-15 reference and the expanded honesty
  register (8 items). All four DOCX regenerated (postcheck: 0 errors)
  and reconverted to PDF.
- **hq_13/hq_14 and anim_04 were still plotting pre-remediation
  values** (hard-coded `7.104e-3/3.842e-3` floors; gamma
  `0.1113→0.1205`). The generators now read the committed verdicts;
  the two hires figure types and the floor-law animation are
  regenerated (en/ru × light/dark).
- **multilang twins printed the retracted agreement line.** All six
  twins now print the honest F-1 ladder drift (`2.79e-3`) and the
  per-grid floors; JS/C/C++ re-compiled and re-run to verify.
- `chbridge/ladder.py`: the `bridge_constants.csv` row carried the
  retracted `agreement 1.06e-6` — replaced with the remediation
  statement (table regenerated via `make data`).
- `chbridge/validate.py`: version string hard-coded `v2.0.0` — now
  derived from the package version (single source: `constants.py`).
- Stale nested duplicate `collapse-hawking-bridge/results/` inside the
  archive removed (packaging artifact with pre-2.0.1 ledger copies).
- results/RESULTS.md rows 15 quoted stale floors with a false
  "v2.0.1 per-grid" tag — corrected to the F-2 values; the ledger is
  restructured at v2.1.0 (21 headline rows incl. the C6 results).

### Changed

- All four engine campaigns re-run at 2.1.0 (C1 48.3 s, C2 24.2 s,
  C3 13.9 s, C3b 333.7 s): **physics byte-identical to the committed
  values** (verified field-by-field; only wall-time metadata moved).
- All folder READMEs rewritten/updated to quote only remediated
  numbers; the T5 floor wording is restated honestly as the 1/N law
  with measured prefactor (13 ± 1)/N (the `12/N ± 7%` band inherited
  the pre-F-2 floors).
- README/README.ru: flagship rewrite — theme-aware logo, badge row,
  mermaid provenance flows, the IVP-15 verdict table, the drift-law
  section, collapsible audit details, and the honest 21-row headline
  table.

### Verification

- pytest: **63 passed**; mpmath battery: 7/7 PASS (dps=50); rebuild_data
  byte-stable; multilang twins (JS/C/C++) re-run OK; campaign re-run
  determinism confirmed.

## [2.0.1] — 2026-10-09

Remediation release: fixes for the three FAIL findings (F-1, F-2, F-3)
of the independent verification protocol IVP-15 (blind audit of 2.0.0,
10 PASS / 2 PARTIAL / 3 FAIL).  Physics claims are corrected to match
what the engine actually measures; the engine's constraint monitoring
is made honest.  All campaign verdicts regenerated at 2.0.1.

### Fixed

- **F-1 (IVP-09) — stale critical-amplitude reference retracted.**  The
  committed "independent high-resolution reference" A*_N1600 = 0.0805333
  did not reproduce under blind bisection (verifier's blind value:
  0.07774315).  A high-precision remediation ladder (tol 5e-8, straddle
  probes at every N) is now committed as campaigns/reference/
  a_star_ladder.{json,csv}: A*_200 = 0.1051042795, A*_400 = 0.0882034349,
  A*_800 = 0.0805332422, A*_1600 = 0.0777437258, A*_3200 = 0.0768211603.
  The threshold DRIFTS with resolution (N800->N1600: 2.79e-3) and is not
  converged at N=3200 — the 2.0.0 claim of 1.06e-6 agreement was wrong
  and is retracted everywhere (constants, bridge summary, docs, README).
- **F-2 (IVP-11) — C3b eps axis mislabeling corrected.**  campaigns/
  run_c3b.py reused A*_N800 as the amplitude base for the deep grids,
  so the committed "eps" was offset by +2.8e-3 at N=1600 and the fitted
  gamma_eff ~ 0.11 was an artifact.  The campaign now bisects the
  PER-GRID A*_N before each scan and commits a_star_per_grid with the
  verdict; the regenerated gamma ladder is the honest per-grid
  measurement (gamma_Ch = 0.374 remains an anchor, not a target).
- **F-3 (IVP-08) — C1 constraint monitoring made honest.**  The engine
  monitor blended three effects into one "C1 max" number: (i) junk
  (non-finite) cells during blow-up rows, (ii) the center reconstruction
  zone where c/d are closure-managed (not constraint evidence), and
  (iii) the genuine march-zone constraint bookkeeping.  _monitor now
  finite-gates all residuals, splits march vs center zone
  (R_zone = max(8 du, 1.2 R_heal)), and reports BOTH the pointwise
  carrier-vs-stencil form and a new integral first-derivative form
  (d p/du = 2 c p - (kappa/2) r s^2, no second differences).  On the
  Roberts regression both forms converge at 2nd order (c1: 6.4e-3 ->
  4.3e-4; c1_int: 1.1e-4 -> 7.2e-6 over N=200..800); on the Gaussian
  family the discrete solution violates C1 at O(1) in both forms —
  now explicitly reported and documented as a known limitation (the
  carried field c is dormant: it never feeds the evolution slopes).
- scripts/build_workbook.py: the undeclared openpyxl dependency is now
  declared (optional extra `workbook`) and the out-of-tree hard-coded
  style path was removed (audit advisory, IVP-03).

### Changed

- All four campaigns (C1, C2, C3, C3b) re-run at 2.0.1 with the honest
  monitor; verdict pins in tests updated accordingly (CHANGELOG event
  per tests/test_campaigns.py policy).
- Docs (validation.md, methods.md, README.md, README.ru.md, results/,
  campaigns/README.md, data/README.md) updated to the remediated ladder
  and the corrected C3b method statement.
- independent_verification/: the IVP-15 audit suite is retained as the
  independence record of the 2.0.0 audit; RESULTS.md carries a 2.0.1
  remediation addendum mapping every finding to its fix.
- monograph/ and animations/ are carried over from 2.0.0 unchanged and
  predate the remediation: their narrative text quotes the retracted
  2.0.0 A*-agreement and C3b gamma values; consult docs/ and
  campaigns/reference/ for the authoritative 2.0.1 numbers.

## [2.0.0] — 2026-10-07

Third public build: the encyclopedia edition. Physics unchanged from
1.1.0 (C1 re-run byte-identical); the release adds the dissemination
layer end to end.

### Added

- figures_hires/: 68 PNG at 600 dpi — 17 figure types x RU/EN x
  light/dark, one figure per measurement architecture of C1/C2/C3/C3b
  (scripts/hires_figures.py).
- animations/: four launch animations x RU/EN, MP4 (h264) + GIF —
  evaporation/Page transition, born bifurcation, critical slowdown,
  floor law (scripts/make_animations.py). Deterministic, committed
  data only, ~1.8 MB total.
- multilang/: the closed-form core in seven languages — verified twins
  (JavaScript, C++, C) executed and cross-checked line by line to a
  worst relative deviation of 7.1e-13; portable sources (Julia, Rust,
  Go) honestly marked as not executed at packaging time.
- tables/bridge_workbook.xlsx: the 13 data tables + an Overview sheet
  as a 14-sheet workbook (scripts/build_workbook.py, xlsx-validate:
  0 issues).
- monograph/: the encyclopedic appendix and the theorems volume, each
  in Russian and English, each as DOCX + PDF (8 documents; generators
  committed under monograph/src/, TOC placeholders + WPS-safe footers
  + postcheck 0 errors on all four).
- results/ROADMAP.md: staged plan (C4 ringdown difference-measurement,
  C5 multi-family universality, the AMR engine upgrade) with explicit
  v3.0 completion criteria.
- Web companion: Next.js interactive application (figure gallery with
  language/theme switches, animation shelf, theorem browser, data
  tables, roadmap, download center).

### Changed

- Version bump everywhere (VERSION, pyproject, CITATION, Makefile,
  chbridge.__version__, campaign runners and verdicts regenerated at
  2.0.0; C1 physics byte-identical to 1.1.0).
- README/README.ru: layout tree rewritten, dissemination-layer section,
  badges extended.

### Verification

- pytest: 60 passed; mpmath battery: 7/7 PASS (dps=50); rebuild_data
  md5 13/13 byte-stable; multilang cross-check 7.1e-13; all four DOCX
  pass postcheck with 0 errors.

## [1.1.0] — 2026-10-07

Second public build: the campaign trio completed — all three campaigns
(C1, C2, C3) plus the deep-grid follow-up C3b, every verdict re-run
fresh from the clean-slate engine.

### Added

- **Campaign C2 — the two branches around the threshold**
  (`campaigns/run_c2.py`, 26 engine runs, ~24 s): the subcritical
  dispersal branch (peak compactness `q_max` grows monotonically toward
  the horizon as `eps -> 0`; measured critical slowdown
  `v_qmax = 0.510 - 0.0334 ln(eps)`, r^2 = 0.71; echo accumulation
  `0.1909` peaks/e-fold against the `1/Delta = 0.2907` anchor) and the
  supercritical born bifurcation (`f~(eps)` table with `M_sat = 0.0352`
  measured on the scan; half-width `eps_half = 4.86e-3`).  Verdict
  `c2_verdict.json` + CSVs; subcritical runs that flip supercritical
  are kept verbatim (`flipped` flag).
- **Campaign C3b — concentrated resolution**
  (`campaigns/run_c3b.py`, 16 engine runs, ~97 s): deep grids
  (N = 1600/3200) spent on the critical window.  First-class result:
  the **floor ladder** `floor_M ~ 12/N` (0.0155 at N=800 -> 7.10e-3 at
  N=1600 -> 3.84e-3 at N=3200).  Honest negatives confirmed: the
  gamma fit stabilises near 0.12 (NOT the anchor 0.374 — the floor
  still governs the band), and no run resolved >= 3 echo peaks, so
  `P_engine_deep` stays null.  Verdict `c3b_verdict.json` + CSV.
- `data/bridge/` — three new derived tables (verdict rows verbatim):
  `campaign_c2_subcritical.csv`, `campaign_c2_bifurcation.csv`,
  `campaign_c3b_ladder.csv` (13 tables total).
- `fig_branches` — seventh figure (two panels: subcritical approach,
  born bifurcation), 28 PNGs total.
- `tests/test_campaigns.py` — 17 new tests pinning the committed
  verdicts (60 tests total).
- `constants.py` Part C — C2/C3b machine values mirrored next to the
  C1 ladder.

### Changed

- All four campaign verdicts re-run fresh at v1.1.0 (deterministic:
  C1 physics byte-identical to v1.0.0; C3 anchor PASS re-confirmed).
- `scripts/rebuild_data.py` — five-stage pipeline; campaign-table
  stage is verbatim and skips missing verdicts gracefully.
- Documentation, folder READMEs and the results ledger updated to the
  four-campaign reality; figure set 24 -> 28; test count 43 -> 60.

### Discipline

- Unchanged and re-affirmed: literature values are anchors for
  comparison, never fit targets; honest negatives (floor-dominated
  gamma, NOT-DSS delta, `P_engine_deep = null`) are first-class
  committed results carried with reasons.

## [1.0.0] — 2026-10-07

First public build. Initial release of the complete bridge study.

### Added

- `chbridge/` — the Python core: constants (single source of truth),
  closed-form Schwarzschild thermodynamics, the bridge mapping
  `f~(eps) -> M_BH(M_in)`, Page-curve ensembles with the Haar-averaging
  check, scale ladders, and a 50-digit `mpmath` verification layer.
- `engine/solver.py` — the double-null characteristic engine for
  spherical collapse of a massless scalar field (Goursat march,
  RK2-Heun, 4 pi G = 1; Roberts-Oshiro regression verified).
- `campaigns/` — campaign C1 (engine validation, A* grid-honesty
  ladder, amplitude scans, evolution profiles) and campaign C3 (the
  Delta*gamma ~ 1.27 invariant check: measured `gamma_eff`, measured
  `Delta_eff`, anchor/mixed/engine products). Committed reference
  verdicts in `campaigns/reference/`.
- `data/bridge/` — derived machine-readable tables: born spectrum,
  master bridge table, Page grid/members/Haar check, scale ladders,
  bridge constants.
- `docs/` — theory, methods and validation documents.
- `figures/` — publication-grade figures (RU/EN x light/dark), fully
  regenerable via `scripts/make_figures.py`.
- `tests/` — pytest suite covering constants, thermodynamics, bridge
  identity, Page model and ladders.
- Giga-READMEs: a deep README for every folder of the repository.

### Discipline

- Literature values are anchors for comparison, never fit targets.
- Honest negatives (fixed-grid mass floor, NOT-DSS verdict, unmeasured
  gamma at committed resolution) are first-class committed results.

[1.0.0]: https://example.invalid/chb/1.0.0
