# IVP-15 Results — Independent Verification of Collapse-Hawking Bridge 2.0.0

> ## 2.1.0 RELEASE-GATE NOTE (2026-10-09)
>
> The 2.1.0 edition completes the alignment this protocol asked for.
> Recommendation-by-recommendation status:
>
> 1. *Re-derive and re-commit the deep-grid A\* reference; update the
>    "1.06e-6 agreement" statements* — DONE at 2.0.1 (the remediation
>    ladder) and COMPLETED at 2.1.0: the monographs, every README, the
>    multilang twins' printed lines, the rendered figures (hq_13, hq_14)
>    and the floor-law animation now quote the honest ladder drift
>    (2.79e-3 over N800→N1600) everywhere; the retraction is explicit at
>    each former claim site.
> 2. *Re-run C3b-style fits with per-grid thresholds* — DONE at 2.0.1;
>    the 2.1.0 volumes quote the per-grid values (γ_eff = 0.041/0.060)
>    and drop the "stabilises ~0.12" narrative.
> 3. *Fix the C1 diagnostic* — the monitor fix (2.0.1) stands; the
>    underlying bookkeeping limitation remains documented as an engine
>    limitation, and the audit's suggested define-from-identity fix is
>    listed on the engine-upgrade path.
> 4. *Hygiene (openpyxl, out-of-tree path)* — DONE at 2.0.1.
> 5. *Promote the Julia/Rust/Go twins where toolchains exist* — their
>    printed control blocks are updated to the remediated values; the
>    twins remain honestly marked "portable source" on machines without
>    their toolchains.
>
> Beyond the recommendations, 2.1.0 adds **theorem T10 + campaign C6**,
> which upgrades the F-1 finding itself: the ladder drift is proven to
> be a necessary property of grid-sampled parabolic structures (exact
> lemmas, machine-verified) — `docs/scaling_law.md`,
> `results/scaling_drift/REPORT.md`,
> `campaigns/reference/c6_drift_verdict.json`.
>
> This file, its verdict JSONs and its logs remain the committed audit
> record of the 2.0.0 blind audit; they are preserved verbatim.

> ## 2.0.1 REMEDIATION ADDENDUM (2026-10-09)
>
> This suite is the independence record of the blind audit of 2.0.0
> (10 PASS / 2 PARTIAL / 3 FAIL).  The three FAIL findings were
> remediated in v2.0.1:
>
> * **F-1 (IVP-09)** — the stale reference `A*_N1600 = 0.0805333` is
>   retracted.  A high-precision remediation ladder (tol 5e-8, straddle
>   probes) is committed at `campaigns/reference/a_star_ladder.{json,csv}`:
>   A*_200 = 0.1051042795, A*_400 = 0.0882034349, A*_800 = 0.0805332422,
>   A*_1600 = 0.0777437258, A*_3200 = 0.0768211603.  This run's blind
>   N=1600 bisection (0.07774315) agrees with the remediated reference to
>   5.8e-7 < 2e-6.  NOTE: the pre-registered sub-check
>   `ladder_converged_N800_to_N1600` legitimately REMAINS FAILED — the
>   2.79e-3 drift is a real property of the fixed-grid threshold, now
>   committed honestly instead of papered over by a false agreement claim.
> * **F-2 (IVP-11)** — C3b regenerated with per-grid thresholds
>   (`a_star_per_grid` in the verdict): gamma_eff = 0.041 / 0.060 at
>   N=1600/3200, floor-dominated (r2 0.33/0.41).  The 2.0.0 values
>   (0.111/0.121) are retracted as eps-mislabeling artifacts.
> * **F-3 (IVP-08)** — the engine monitor now finite-gates the C1
>   residual, splits march vs center zones, and adds an integral
>   first-derivative form.  The underlying O(1) discrete C1 bookkeeping
>   violation on the Gaussian family is REAL and REMAINS OPEN (documented
>   engine limitation; the carried field c is dormant and cannot
>   contaminate the dynamics) — this sub-check legitimately remains
>   FAILED; the remediation fixes the REPORTING, not the physics.
>
> Release gate: `RUN_ALL.sh` re-run on the 2.0.1 tree; per-check outcomes
> are mapped to findings in `results/` (refreshed) — status changes vs
> the 2.0.0 audit are expected ONLY where a finding was remediated.

**Committed audit report** · release audited: `Collapse-Hawking-Bridge-2.0.0.zip`
· protocol version: IVP-15 (this directory)

---

## 1. Executive summary

The release archive was audited with a fifteen-point independent
verification protocol whose source of truth lies outside the project's
own committed results (see `PROTOCOL.md`, §2 Independence contract).
The baseline `pytest` suite passes (60/60); that result is confirmed.
Beyond it, the audit **confirms the core of the release** and
**localizes three specific defects** with full documentation.

Confirmed independently:

* archive identity and integrity (SHA-256 `2d7b178f…bb776b`, CRC-clean,
  221 entries, no traversal/symlinks/debris); version `2.0.0` consistent
  across all eight release surfaces;
* clean-room installation reproduces the full test suite and a
  bitwise-identical canonical numeric job on Python 3.12 **and** 3.13;
* the runtime dependency footprint is exactly the declared
  `{numpy, mpmath}` — no network access, no subprocess use, no
  out-of-tree reads anywhere in runtime/test/campaign code;
* every closed form (r_s, S_BH, T_H, P_H, t_evap, rho, kappa, Planck
  units, M_CMB) agrees with a 50-digit re-derivation to <= 5e-16;
* the Roberts-Oshiro solution satisfies the engine's full
  Einstein-scalar system **identically** (SymPy-exact residuals ≡ 0),
  and kappa = 8*pi*G = 2 is proven to be the *unique* normalization
  consistent with the exact solution;
* the engine's observed convergence order is p = 1.97–2.08 (RK2 as
  claimed), on a verifier-chosen window with verifier-own exact
  formulas;
* the committed shallow-grid critical amplitudes reproduce to
  <= 2.2e-6 (blind re-bisection);
* the 1/N mass-floor law is confirmed (measured exponent
  p = 0.879 ± 0.050, R² = 0.993);
* the multilang twins C/C++/JavaScript agree pairwise to 7.1e-13 and
  match a 50-digit reference within the printf budget.

Defects found (each documented in §4 below with evidence and impact):

1. **The committed N=1600 critical-amplitude reference does not
   reproduce.**  Blind re-bisection at N=1600 (corroborated by direct
   classification probes) locates the threshold at `A*_1600 ≈ 0.07774`,
   not the committed `0.0805333`; the ladder keeps drifting
   (|A*_1600 − A*_800| = 2.8e-3, |A*_3200 − A*_1600| = 9.2e-4).
2. **The C3b deep-grid gamma fits inherit that threshold shift.**
   Refitting the verifier's own masses with the committed (N=800)
   threshold labels reproduces the committed values (0.113 vs 0.111,
   0.104 vs 0.121) — with the true per-grid thresholds the same data
   give gamma ≈ 0.19–0.23.
3. **The C1 (uu-Einstein) constraint identity is violated at O(1) on
   Gaussian-family runs** and the violation does not shrink with
   resolution (the engine's own monitor reports the same values).  The
   affected field is a dormant diagnostic (no feedback path into the
   evolution); the dynamical sectors converge cleanly.

Two release-hygiene advisories (no scientific impact): an undeclared
`openpyxl` dependency and an out-of-tree absolute path in
`scripts/build_workbook.py`.

Overall: **11 of 15 checks PASS or PARTIAL; 3 FAIL (documented,
localized); 1 advisory.**  The committed audit trail (all verdict JSONs
and logs) ships in `results/`.

## 2. Verdict table

| IVP | Check | Verdict |
| :-- | :---- | :------ |
| IVP01 | Release identity & archive integrity | **PASS** |
| IVP02 | Clean-room installation (multi-interpreter) | **PART** |
| IVP03 | Dependency & provenance audit | **PASS** |
| IVP04 | Independent re-derivation of constants | **PASS** |
| IVP05 | Dimensional-analysis audit | **PASS** |
| IVP06 | Roberts symbolic residual test (SymPy) | **PASS** |
| IVP07 | Method-of-convergence test | **PASS** |
| IVP08 | Constraint-propagation audit | **FAIL** |
| IVP09 | Blind remeasurement of A* | **FAIL** |
| IVP10 | Threshold robustness / perturbation | **PASS** |
| IVP11 | Blind mass-scaling (gamma) measurement | **FAIL** |
| IVP12 | Resolution-floor law | **PASS** |
| IVP13 | Blind echo detector (Delta) | **PASS** |
| IVP14 | Delta*gamma falsification (procedure; anchor product = ANCHOR_ARITHMETIC since v2.2.0) | **PASS** |
| IVP15 | Cross-language agreement | **PART** |

Summary: PASS 9 · PARTIAL 3 · FAIL 3 · INCONCLUSIVE 0.

## 3. Audit environment

* Python 3.12.14 (numpy 2.1.3, mpmath 1.3.0, sympy 1.14.0,
  pytest 9.0.2); a second clean-room interpreter 3.13.5 for IVP-02.
* Toolchains present: gcc 14.2, g++ 14.2, node 24.21; absent:
  julia, rustc, go (their twins reported INCONCLUSIVE with reproduction
  commands).
* Single-core CPU machine; full-suite wall time ≈ 40 min
  (per-IVP wall times in each verdict JSON).
* Baseline at audit start: `pytest tests/ -q` → 60 passed.

## 4. Findings

### F-1 (IVP-09, FAIL): the committed N=1600 reference does not reproduce

Committed claim (c1_verdict.json, README, multilang twins): the N=800
threshold `A* = 0.08053436` agrees with an "independent high-resolution
reference 0.0805333 (N=1600)" to 1.06e-6.

The verifier's blind protocol (coarse scan at N=200 to bracket the
transition, then bisection to 2e-6 at each grid, no committed values
read) produced:

| N | IVP A*_N (blind) | committed | |diff| |
| --: | --: | --: | --: |
| 200 | 0.10510437 | 0.10510483 | 4.6e-7 |
| 400 | 0.08820335 | 0.08820114 | 2.2e-6 |
| 800 | 0.08053307 | 0.08053436 | 1.3e-6 |
| 1600 | **0.07774315** | 0.08053330 (ref) | **2.79e-3** |
| 3200 | **0.07682091** | — | — |

The shallow grids reproduce (within 5e-6).  At deep grids the ladder
keeps drifting: 2.79e-3 from N=800 to N=1600, then 9.2e-4 to N=3200
(effective order ≈ 1.6 — consistent with slow power-law convergence of
the fixed-grid threshold, not with a 1e-6-converged value).

Validity of the deep-grid bisection is corroborated by direct
classification probes (monotone, clean transition):
at N=1600, A=0.0777 → subcritical and A=0.0785 → supercritical;
at N=3200, A=0.0755 → subcritical and A=0.0770 → supercritical —
bracketing the verifier's bisected thresholds.

**Impact.**  Statements of the form "A*is converged to 1e-6 at N=800"
(README item 1's agreement line, multilang twin printout, c1 verdict
honest note) are not supported: the fixed-grid threshold at N=800 is
still ≈ 2.8e-3 away from the N=1600 threshold.  The A* *values
themselves* at N=200/400/800 are correct as fixed-grid quantities.

### F-2 (IVP-11, FAIL): the C3b deep-grid gamma fits inherit the F-1 threshold shift

C3b labels eps as `A − A*_N800` while running at N=1600/3200.  Given
F-1, the true distance to the *per-grid* threshold is
`eps_label + (A*_N800 − A*_Ntrue)` ≈ `eps_label + 3e-3` — the smallest
labeled eps rows actually sit thousands of times further above
threshold than labeled.

The verifier measured gamma blind, per grid, around its own A*_N:

| N | gamma_eff (verifier, own A*) | R² | floor_M | committed C3b |
| --: | --: | --: | --: | --: |
| 400 | 0.1382 ± 0.0033 | 0.998 | 2.57e-2 | — |
| 800 | −0.027 ± 0.021 | 0.11 | 1.62e-2 | — |
| 1600 | 0.034 ± 0.024 | 0.19 | 8.03e-3 | 0.1113 |
| 3200 | 0.041 ± 0.023 | 0.31 | 4.27e-3 | 0.1205 |

Forensic refit (comparison phase): relabeling the verifier's own masses
with the committed N=800 threshold (the C3b convention) reproduces the
committed numbers almost exactly —

| N | fit with TRUE threshold | fit with N=800 labels |
| --: | --: | --: |
| 1600 (n=5) | gamma = 0.225 ± 0.036, R² = 0.930 | gamma = 0.113 ± 0.005, R² = 0.994 |
| 3200 (n=3) | gamma = 0.187 ± 0.024, R² = 0.983 | gamma = 0.104 ± 0.001, R² = 1.000 |

**Impact.**  The committed C3b gamma_eff ≈ 0.11–0.12 values are
quantitatively explained as threshold-labeling artifacts; with true
per-grid thresholds the same data give systematically larger gamma
(~0.19–0.23) with fewer usable points.  In NO case is the literature
anchor gamma = 0.374 reached at any available resolution — this is
consistent with, and strengthens, the project's own honest negative
("fixed-grid gamma is NOT percent-measurable").  The verifier's best
power-law measurement is at N=400: gamma = 0.138 ± 0.003 (R² = 0.998).

### F-3 (IVP-08, FAIL): the C1 constraint identity is violated at O(1) on Gaussian runs

Verifier-own per-row monitoring (relative residuals, own stencils,
center-excluded mask r > 4 du) on the smooth subcritical run
(A = 0.05):

* C2 Goursat sandwich: max rel residual 1.4e-4 at N=800 (clean);
* Misner–Sharp mass definition: max 6.4e-5 at N=800, shrinking ~2x per
  grid doubling (clean);
* gauge consistency |c − d(ln alpha)/du| ≈ 1e-2 (the evolved c really
  is omega_u);
* **C1 identity** `r_uu = 2 c r_u − (kappa/2) r s²`: max relative
  residual 0.89 at N=800, 0.57 at N=1600, 1.03 at N=400 — O(1) and
  non-converging, localized to the pulse region (a kink in the p
  profile at a fixed u); the engine's own monitor reports the same
  values (0.874 at N=800 — verified by running it alongside).
* t-sandwich: O(1) confined to the single outer-edge cell (row-mean
  level converges).
* monitor_every in {1, 25, 100} → **bitwise identical** final physics
  (monitoring is passive), and AST analysis of `_slopes` shows zero
  loads of the evolved c field: **the C1 defect has no feedback path**
  into r, q, m, alpha², Phi.

**Impact.**  The dynamical sector whose residuals feed the observables
(q, m, alpha²) is clean and converging; r converges to exact solutions
at 2nd order (IVP-07); the committed results rest on those sectors.
But the C1 identity as printed by the engine's own monitor is not a
converging quantity on the Gaussian family, and any future use of the
c field (e.g. enabling the taylor/annulus closure paths reads
neighbouring diagnostics) should first fix C1 — the natural fix is to
define c from the identity each row (making C1 hold by construction)
or enforce it in the march.

### Advisory A-1 (IVP-03): undeclared dependency + out-of-tree path in build_workbook.py

`scripts/build_workbook.py` imports `openpyxl` (not declared in
`pyproject.toml` extras or `requirements.txt`) and hard-codes an
out-of-tree absolute path (`/home/z/my-project/skills/xlsx`) for a
`templates` package import.  The script cannot run outside the original
machine.  No committed scientific value depends on it (the workbook is
shipped pre-built; the data-regeneration path `scripts/rebuild_data.py`
is strictly within the declared deps — checked separately).  Suggested
fix: vendor the `templates` module, make the import optional, and add
`openpyxl` to a `[project.optional-dependencies] docs` extra.

## 5. Per-IVP results (committed run)

### IVP-01 — release identity: PASS

SHA-256 of the audited archive:
`2d7b178f491efee08f81d1db9587eb23dde18d27ff19c007091652badebb776b`
(39,115,088 bytes, 221 entries, uncompressed 46,774,643 bytes).  CRC
clean; no path traversal, symlinks, duplicates or debris.  Version
2.0.0 consistent in VERSION, pyproject.toml, Makefile, CITATION.cff,
CHANGELOG.md, README.md and all four committed verdicts.  Tree hygiene:
no symlinks.

### IVP-02 — clean-room installation: PARTIAL

Fresh venvs, declared deps only, `pip install --no-deps -e .`:

| interpreter | venv | pytest | canonical job |
| -- | -- | -- | -- |
| 3.12.14 | PASS | 60/60 | bitwise identical |
| 3.13.5 | PASS (via `--without-pip` + `pip --python`) | 60/60 | bitwise identical |
| 3.9 / 3.10 / 3.11 | INCONCLUSIVE — interpreter absent on audit machine | — | — |

The canonical numeric job (Roberts regression + flat space + Gaussian
observable, full 17-digit output) is **bit-identical across 3.12 and
3.13**.

### IVP-03 — dependency & provenance audit: PASS

Runtime third-party imports (chbridge + engine + campaigns) =
exactly `{numpy, mpmath}` (declared).  tests = `{numpy}`;
data-regeneration script = `{numpy}`.  No network-capable imports, no
subprocess invocations, no out-of-tree file reads/writes in runtime
code.  One advisory finding (A-1 above).  The audit suite itself
additionally requires `sympy` (declared in its own JSON).

### IVP-04 — constants re-derivation: PASS

All closed forms re-derived at mpmath dps=50 from CODATA-2018 exact
definitions and compared to chbridge float64 at three test masses
(1e12, 4.5016e22, 1.98892e30 kg): 26/26 comparisons within tolerance
(typical rel diff ≈ 1e-16, worst 5.0e-16).  Internal identities
verified at 1e-30: S_BH·T_H = Mc²/2 (first law), t_evap = Mc²/(3P_H),
T_H(M_CMB) = T_CMB round trip, rho·r_s³ = 3M/4pi.  Provenance note:
the project's solar input mass 1.98892e30 kg differs from the IAU-2015
nominal GM/G value (1.98841e30 kg) by 2.6e-4 — a declared input
choice, not an error; all comparisons were made at the project's own
input masses.

### IVP-05 — dimensional analysis: PASS

All eight SI closed forms reduce to the exact expected dimension
vectors (r_s → m, S_BH → J/K, T_H → K, P_H → W, t_evap → s, ...).
Engine normalization: 8pi/(4pi) = 2 exactly; `engine/solver.py`
declares KAPPA = 2 (12 uses); the "4 pi G = 1" normalization is
documented; and IVP-06 independently proves kappa = 2 is the unique
consistent normalization.

### IVP-06 — symbolic Roberts residual test: PASS

SymPy differentiation from scratch of the published Roberts-Oshiro
form; all five residuals (SC, UV, C1, C2, TH+MD) simplify to **exactly
0** (identically, not approximately) after reduction to sqrt-free
rational form.  With kappa as a free symbol, the C1 residual factors as
`sigma²·v²·(kappa − 2)/4` — nonzero at kappa = 3/2, zero at kappa = 2:
the engine normalization is forced by the exact solution.  30-digit
numeric spot check: worst residual exactly 0 on the sampled grid.

### IVP-07 — convergence order: PASS

Verifier-chosen window (sigma = 0.12, u ∈ (−0.25, 0.75), v ∈ (1.1, 1.9)
— deliberately different from the engine's own test window), verifier
own exact-solution class.  err_r ladder: 2.31e-4, 5.89e-5, 1.47e-5,
3.60e-6, 8.53e-7 at N = 100..1600; observed orders p = **1.97, 2.00,
2.03, 2.08** — all within the pre-registered [1.8, 2.3] band; monotone
decrease.  Committed engine validation numbers (different window) agree
in order and magnitude.

### IVP-08 — constraint propagation: FAIL (F-3)

See §4 F-3 for the full picture.  Clean: C2 sandwich (1.4e-4), mass
definition (6.4e-5), gauge consistency (1e-2), monitor_every invariance
(bitwise), supercritical pre-horizon dynamical sector.  Failing: C1
identity, O(1), non-converging.  Status FAIL reflects the
pre-registered falsification criterion on C1.

### IVP-09 — blind A*: FAIL (F-1)

See §4 F-1.  Shallow grids reproduce; the deep-grid reference does not;
ladder drift measured and probed.  Total blind-protocol wall time 271 s.

### IVP-10 — threshold robustness: PASS

All eight perturbation classifications correct at N=800
(eps = 1e-2 .. 1e-5, both sides), and at N=1600 for eps = 1e-3, 1e-4
(around the verifier's own blind A*_N).  The super/subcritical
classification is not an artifact of a single evaluation.

### IVP-11 — blind gamma: FAIL (F-2)

See §4 F-2.  The pre-registered fit-well-definedness criterion
(R² >= 0.9 on the deep-grid bands) is not met with true thresholds; the
forensic refit explains the committed values.  gamma = 0.374 is not
reached anywhere (consistent with the project's honest negative).

### IVP-12 — resolution floor: PASS

floor_M (smallest resolved mass, verifier-own scans + probes):
2.57e-2 / 1.62e-2 / 8.03e-3 / 4.27e-3 at N = 400/800/1600/3200.
Free-exponent fit: **p = 0.879 ± 0.050 (R² = 0.993)**, C = 5.27 —
independently confirming the 1/N grid-floor law (committed rule of
thumb "12/N": same law; the prefactor depends on the floor definition,
and the committed N=800 floor 0.0155 agrees with the verifier's
1.62e-2 to 5%).

### IVP-13 — blind echo detector: PASS (honest negative)

Per-row sampling (1599 samples per run — 40x denser than the
committed detector) at N=1600 around the verifier's own A*_1600,
verifier-own peak detector (relative prominence 5e-3, median smoothing,
regression estimator in log time): **2 peaks resolved** in every run
(eps = 1e-3, 3e-4, 1e-4).  Delta is therefore NOT measurable at this
resolution — a first-class negative result that *strengthens* the
project's own NOT-DSS verdict (committed detector resolved the same 2
peaks with 40x fewer samples; the denser sampling shows no third peak
exists to find at this prominence).

### IVP-14 — Delta·gamma falsification: PASS (procedure)

Three products separated: P_anchor = 3.44 × 0.374 = 1.28656 — anchor
arithmetic, within the 1.27 ± 0.05 target.  P_mixed and P_engine
honestly INCONCLUSIVE (Delta unmeasurable, F/IVP-13) — matching the
committed C3 verdict's own honest `None` products.  The invariant
Delta·gamma ≈ 1.27 therefore remains an anchor-level statement, not an
engine-measured one.

**v2.2.0 re-scoping (external audit, point 10).** The PASS of this check
is a PASS of the *procedure* (three products separated, unmeasurable
factors reported INCONCLUSIVE, never silent) — not a physics PASS of the
hypothesis.  The committed verdict token for P_anchor is now
`ANCHOR_ARITHMETIC` (+ `P_anchor_within_target`), and the target 1.27 ±
0.05 is frozen by `PREREGISTRATION.md`: it was chosen post hoc in v1.x
and cannot be retuned without a RETRO-LABEL CHANGELOG event.  Only
P_mixed / P_engine — products with measured factors — can carry
physics verdicts.

### IVP-15 — cross-language agreement: PARTIAL

C, C++ and JavaScript twins compiled/run; 12 numeric fields parsed per
twin; worst pairwise relative deviation **7.08e-13** (reproducing the
release's own cross-language claim), all within the 1e-11 pre-registered
tolerance; all closed-form fields agree with the verifier's 50-digit
re-derivation within the printf budget.  Julia / Rust / Go twins:
INCONCLUSIVE — toolchains absent on the audit machine (reproduction
commands recorded in the verdict JSON; the sources ship with the
release).

## 6. Reproducibility

Every number in this report is regenerable from the release tree:

```bash
IVP_ZIP=/path/to/Collapse-Hawking-Bridge-2.0.0.zip \
  bash independent_verification/RUN_ALL.sh
```

The committed machine verdicts (`results/*.json`), full console logs
(`results/logs/`) and the raw blind scan rows (`results/IVP11_rows.json`)
constitute the audit trail of the run documented here.  Re-running the
suite overwrites `results/` with the fresh trail; commit both if you
want a before/after comparison.

## 7. Recommendations (prioritized)

1. **Re-derive and re-commit the deep-grid A\* reference** (IVP-09
   protocol): either as a true N=1600 bisection, or reworded as the
   fixed-grid value it is; update the "1.06e-6 agreement" statements in
   `c1_verdict.json` honest notes, README item 1 and the multilang
   twins' printed line.
2. **Re-run C3b-style fits with per-grid thresholds** (or adopt the
   IVP-11 rows) and restate gamma_eff; keep the honest-negative framing
   — the anchor 0.374 remains out of reach at available resolution.
3. **Fix the C1 diagnostic** in the engine (define-from-identity or
   enforce-in-march), then re-enable it as a regression bound.
4. **Hygiene**: declare or drop `openpyxl` in build_workbook.py and
   remove the out-of-tree `templates` import path.
5. Promote the Julia/Rust/Go twins to "verified" wherever their
   toolchains exist (their outputs are diffable against
   `javascript/reference_output.txt` per the release's own protocol).
