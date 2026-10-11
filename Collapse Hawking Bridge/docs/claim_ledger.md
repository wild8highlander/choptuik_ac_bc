# Claim ledger — every surface claim mapped to its artifact

**Purpose.** The external audit's cheapest and most defensible check was
the correspondence table: *does every claim the package makes about
itself have a machine-readable address in the package?* This file is
that check, committed. Rule of the package: **machine-readable or it
did not happen** — a claim without an artifact address below is a bug;
report it.

**Companion documents:** [PREREGISTRATION.md](../PREREGISTRATION.md)
(frozen falsification criteria), [RESULTS.md](../results/RESULTS.md)
(the ledger prose), [validation.md](validation.md) (per-check numbers).

## 1. Badge claims (top of README.md / README.ru.md)

| claim | artifact that makes it true | pinning test |
|---|---|---|
| version 2.2.0 | `VERSION`, `chbridge/constants.py::__version__`, `pyproject.toml` | `tests/test_constants.py::test_package_version_pin` |
| pytest 69 passed | `tests/` (the suite itself); count pinned in `tests/README.md` | the suite run |
| validate 7/7 PASS | `chbridge/validate.py::run_all` output | `tests/test_ladder.py::test_validate_all_pass` |
| audit IVP-15 remediated + aligned | `independent_verification/results/*.json`, `independent_verification/RESULTS.md` | `tests/test_preregistration.py` (token discipline) |
| theorem T10 drift law | `campaigns/reference/c6_drift_verdict.json`, `docs/scaling_law.md` | `tests/test_campaigns.py::test_c6_*` (3 pins) |
| figures_hires 68 @600dpi | `figures_hires/` — 68 PNG files (17 architectures × RU/EN × light/dark) | `scripts/hires_figures.py --all` |
| multilang 7 | Python + `multilang/{javascript,c,cpp,julia,rust,go}` | `multilang/README.md` matrix |

## 2. Headline result rows (README.md §Headline results ↔ RESULTS.md)

| # | claim | verdict address | pin |
|---|---|---|---|
| 1–2 | A*_N800 = 0.0805332422; five-grid ladder | `campaigns/reference/a_star_ladder.{json,csv}` | `test_ladder.py` ordering pins |
| 3–4 | drift N800→N1600 = 2.79e-3; p_eff 1.140/1.459/1.596 | `campaigns/reference/c6_drift_verdict.json` | `test_c6_ladder_facts` |
| 5 | Roberts–Oshiro orders 2.03/2.09 | `c1_verdict.json` | `test_constants.py::test_campaign_astar_ladder` + engine regression |
| 6 | born members f~ 0.2877/0.2684/1.0 | `data/bridge/collapse_verdict_summary.json` | `test_bridge.py` |
| 7–9 | CMB contact 4.5016e22 kg; Page fraction; Haar 0.0042 bits | `chbridge/hawking.py`, `data/bridge/page_haar_check.csv` | `test_hawking.py`, `test_page.py` |
| 10–11 | b_Ch exact; gap \|γ_Ch − b_Ch\|/b_Ch = 0.67% (γ_Ch is the LITERATURE side; b_Ch is the project's own constant — the former "b_Ch_lit" label is removed at v2.2.0) | `chbridge/validate.py::check_b_Ch` | `test_constants.py::test_b_ch_*` |
| 12 | Δ·γ anchor product 1.28656 vs 1.27 — **ANCHOR_ARITHMETIC** (not a measurement; engine level INCONCLUSIVE) | `c3_verdict.json::products` | `test_campaigns.py::test_c3_verdict_semantics`, `test_preregistration.py` |
| 13–16 | C2 branches (compactness, slowdown, echo rate, ε½) | `c2_verdict.json` | `test_campaigns.py::test_c2_*` |
| 17–18 | floor law (13±1)/N; γ, Δ honestly unmeasurable to N=3200 | `c3b_verdict.json` | `test_c3b_floor_ladder_sinks`, `test_c3b_gamma_fit_floor_biased`, `test_c3b_delta_honest_negative` |
| 19–20 | T10 channel κ*=2728.60, s=413.8, sub-dominant; NO A*_inf | `c6_drift_verdict.json` | `test_c6_honest_negatives_and_channel` |
| 21 | 50-digit layer 7/7 | `chbridge.validate` | `test_validate_all_pass` |

## 3. Structural claims

| claim | address | verified by |
|---|---|---|
| bridge_master.csv = 15 rows × 23 columns | `data/bridge/bridge_master.csv` | `test_bridge.py` geometry pins |
| 13 byte-deterministic data tables | `data/bridge/` (13 files) | `test_rebuild_is_deterministic` |
| 28 figures @300dpi; 68 @600dpi; 16 animation files (4 × RU/EN × MP4/GIF); workbook 14 sheets | `figures/`, `figures_hires/`, `animations/`, `tables/bridge_workbook.xlsx` | rebuild scripts |
| monograph: 2 volumes × RU/EN × DOCX+PDF, T1–T10 | `monograph/` | monograph README runbook |

## 4. Claims this package does NOT make

The audit checked the parent repository's README against this package's
contents. For the record, the Collapse–Hawking Bridge package **does
not** claim any of the following (these live, if at all, in other
projects of the parent repository and are not backed by anything here):

- a "solution to the Choptuik problem" — the package measures fixed-grid
  observables and honestly does not reach the continuum threshold;
- a "solution of the strong CP problem";
- QNM predictions for GW150914 / GW170104 / GW170814 / GW190521 — the
  package carries a Schwarzschild l=2 ringdown formula and a labeled
  septinial *correction hypothesis* (relative shift 8.44e-5, campaign
  C4 is future work), not event predictions;
- "machine verification at 1e-41" — the machine layer here is
  byte-determinism, 50-digit mpmath checks, and order-2 engine
  convergence, none of which is a 1e-41 statement;
- a "58/58 tests" count — the count pinned by this package's own README
  is the pytest total of `tests/` (see badge; verified by running the
  suite).

The Russian mirror of this document: [claim_ledger.ru.md](claim_ledger.ru.md).
