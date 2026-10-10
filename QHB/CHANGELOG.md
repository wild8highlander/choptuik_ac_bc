# Changelog

## 2.3.0 (2026-10-10) — the Mathlib / iron-layer edition
- Full port of theorem T19 into Mathlib (`monolith/lean/QHB_T19_Mathlib.lean`):
  the reduced co-rotating operator is assembled from the translation block (Lemma B)
  and the √3-free shape block (Lemma C, diagonal similarity D = diag(2√3/3, 1, 1, √3/2));
  block characteristic polynomials computed with `Matrix.charpoly`; the factorization
  χ(C₀) = (λ²+(2+γ)²)·λ²·(λ²+3(1+2γ)) follows from `charpoly_fromBlocks_zero₂₁`.
  Eight new closed kernels; the axiom audit (`QHB_AxiomAudit.lean`) covers all
  **18 closed kernels** and CI fails on any `sorryAx`.
- Erratum: the stall-cliff kernel T20.stall had its conclusion sign reversed in
  v2.2.0 — τ_max = ε_H·e^{B/T}/ν strictly **decreases** in T (danger lives at the
  hot end). Fixed and closed; T20.deadline closed as well; T3 honestly downgraded
  to data-anchored (π is transcendental).
- External comparison extended X1–X8 → **X1–X13** (SQM-ISS 2024, IceCube
  sub-relativistic monopoles 2025, KM3NeT 2023–24, macro-constraints recast
  2024–26, CTAO/HESS J1731-347 2025), all re-verified against primary sources
  with confirmation addresses in `roadmap_results.json`; honest AMS-02 note on X8.
- Iron layer: Iron-QA tools (`tools/check_json/check_numbers/check_release/
  check_lean_kernels`), four GitHub Actions workflows (canon CI, Lean/Mathlib CI,
  Pages, release), issue/PR templates, CONTRIBUTING/CODE_OF_CONDUCT/SECURITY,
  CITATION.cff 2.3.0, animated READMEs (EN/RU), landing page in `docs/`,
  social preview, `.gitattributes`, git-ready repository + bundle.
- Monographs RU/EN rebuilt (17 chapters + appendix A with the Mathlib section,
  fig. A.1 and the erratum): 63/61 PDF pages.

## v1.3.0 (2026-10-10) — Asymmetry Lock

### New
- **C12 campaign `asymmetry_lock`**: the matter-antimatter asymmetry cannot close
  the gap. Worst-case unit-normalized perturbation drops the closure barrier by
  exactly 2·eta (SymPy inequality); eta_crit = Delta_F,min/2 = 0.0908885; the
  cosmological baryon asymmetry eta_B = 6.1e-10 (Planck 2018) sits 1.49e8 times
  below the threshold.
- **T14 (exact)**: asymmetric lock — for every eta < eta_crit the closure barrier
  stays positive; eta-phase map (41 points, 9 profiles) OPEN/CLOSED boundary
  passes exactly through eta_crit.
- **T15 (honest-negative)**: no free quarks as separate asymptotic states —
  gap filling is self-limiting (0 saturated wells / 1e6 steps at eta_B; cascade
  at eta = 0.5 as positive control) and the macroscopic accumulation probability
  is < 10^(-1.2e31).
- Deep verification battery: mpmath 100-digit recomputation of all exact
  constants, C9 jackknife stress (drop-3-around-valley, shift < 1e-9),
  WKB quadrature at 60 digits, C5 z-score guard, byte-level determinism guard.
- Multilingual twin check extended to 14 pairs x 3 sweeps (51 checks).
- Evidence Engine extended to 30 claims; IVP audit extended to 12 passes.
- 15 additional figures (C10/C12 family) and 600-dpi hires set.

### Changed
- Test suite extended to 100+ pinned tests.
- `qhb/pins.py` now records all calibration seeds/parameters.
- Docs: README/RESULTS gained the C12 sections (RU/EN mirrors).

### Fixed
- Box-Muller cos^2 in C5 (chi-square correctness of the analytic/MC pair).
- C10 share normalization reported with the additivity bias separated.
- C4 runs test degenerate-case sentinel (-999.0) instead of NaN.

## v1.2.0 (2026-10-09)
- C9 phase map (9x41, all OPEN), C10 competing models, C11 vortex anchor
  (Kirchhoff layer from scratch), theorems T11-T13, Evidence Engine, IVP-11.

## v1.1.0 (2026-10-08)
- Theorems T1-T10 formalized; honest-negative ledger introduced; bilingual
  mirrors; monograph volumes.

## v1.0.0 (2026-10-07)
- Initial campaigns C1-C8, IVP-08 audit.
