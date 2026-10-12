# Independent Verification Protocol (IVP-15)

**Collapse-Hawking Bridge v2.0.0 — release audit suite**

This directory contains a self-contained verification protocol that
audits the release **independently of the project's own committed
results**.  It complements the pytest suite (which largely checks
internal consistency) with checks whose source of truth lies *outside*
the repository's own verdict files.

---

## 1. Why this exists

`pytest PASS` demonstrates that the package agrees with itself.  It does
not by itself demonstrate that:

* the artifact being inspected is the artifact that was released;
* the closed-form physics is right (rather than consistently wrong);
* the numerical engine solves the equations it claims to solve;
* the committed campaign numbers can be *re-derived* by someone who
  refuses to look at them first.

IVP-15 is designed around that distinction.  Every check states its
**independent source of truth** before it runs, and every check reports
its verdict honestly, including `FAIL` and `INCONCLUSIVE`.

## 2. Independence contract

1. **No expected scientific values from the release.**  While measuring,
   no script reads `campaigns/reference/*` (verdicts or CSVs) or any
   value derived from them.  Committed machine outputs may be loaded
   *only* in an explicit, labelled **comparison phase** at the very end
   of a script, and only to be compared against values the script has
   already measured on its own.
2. **Closed forms are re-implemented, not imported.**  All physical
   formulas used by the suite come from its own CODATA-2018 mpmath
   block (`ivp_common.py`) or from SymPy differentiation performed from
   scratch (IVP-06).  `chbridge` enters only at comparison time.
3. **Exact solutions are re-implemented.**  The numerical IVPs evolve
   the suite's own Roberts-Oshiro / Gaussian-pulse classes (own
   formulas), which subclass the engine's dataclasses only so the
   engine's `isinstance` dispatch accepts them.
4. **Inputs are specifications, not outputs.**  The initial-data family
   geometry (`u0 = -1`, `v_p = 0.5`, `sigma = 0.1`, box `(-1, 1.05) x
   (0, 1)`) is part of the model specification documented in
   `docs/methods.md`; it is an input, not a measured result.
5. **Instrumentation never touches evolution.**  Where the suite
   monitors the engine row by row, it subclasses the solver and
   overrides *only* the monitoring hook; the evolution step is the
   shipped code, unmodified.
6. **Pre-registered criteria.**  Every script states its acceptance
   criteria in its docstring and in its verdict JSON *before* comparing
   against anything committed.  Criteria are never moved after seeing
   the outcome; where a criterion proved miscalibrated, the JSON says
   so explicitly.

## 3. The fifteen checks

| IVP | Level | Check | Independent source of truth |
| :-- | :---- | :---- | :-------------------------- |
| 01 | Artifact | Release identity: SHA-256, archive integrity, version consistency | cryptography + file census |
| 02 | Artifact | Clean-room install per Python interpreter (venv, declared deps only) | fresh environment |
| 03 | Artifact | Dependency & provenance audit (import graph, network/subprocess/out-of-tree scan) | AST of every source file |
| 04 | Physics | Re-derivation of all constants and closed forms at 50 digits | verifier's own mpmath block |
| 05 | Physics | Dimensional analysis of every closed form; engine normalization kappa = 8*pi*G = 2 | exact dimension algebra |
| 06 | Engine | Symbolic residual test: Roberts-Oshiro solution vs the full Einstein-scalar system | SymPy, from scratch |
| 07 | Engine | Method-of-convergence: observed order p_N = log2(E_N/E_2N) on the verifier's own window | N -> 2N ladder |
| 08 | Engine | Constraint propagation: verifier-own per-row residuals, monitor-frequency invariance | own monitor + own stencils |
| 09 | Campaign | Blind remeasurement of the critical amplitude A*_N (coarse scan + bisection, no committed values) | re-derived threshold |
| 10 | Campaign | Threshold robustness: A*(1 +/- eps) must classify correctly for eps = 1e-2..1e-5 | falsification |
| 11 | Campaign | Blind mass-scaling exponent gamma at four grid depths | own regression |
| 12 | Campaign | Resolution-floor law: floor_M = C/N^p with p measured, not assumed | multi-resolution fit |
| 13 | Campaign | Blind echo detector on per-row raw signals (own peak detector, own estimator) | signal processing |
| 14 | Campaign | Delta*gamma falsification: P_anchor / P_mixed / P_engine separated | independent products |
| 15 | Implementation | Cross-language agreement of the multilang twins + 50-digit reference | C/C++/JS/Julia/Rust/Go |

## 4. Verdicts

Each script writes `results/IVPnn.json` with one overall status:

* **PASS** — all pre-registered criteria met;
* **PARTIAL** — all available checks met, but some part of the protocol
  could not be executed in the audit environment (e.g. missing
  interpreter or compiler), reported per-item as INCONCLUSIVE;
* **INCONCLUSIVE** — the check could not be executed or its outcome is
  undetermined (this is a first-class result, never silently skipped);
* **FAIL** — at least one pre-registered criterion violated.  Every
  FAIL carries a finding description and an impact analysis in its JSON
  and in `RESULTS.md`.

A `FAIL` in this suite is not an accusation; it is the difference
between internal consistency and external verifiability, made
measurable.  The project's own honesty discipline ("honest negatives
are first-class results") is exactly the standard applied here.

## 5. How to run

```bash
# full suite (~35-45 min, single core)
bash independent_verification/RUN_ALL.sh

# fast pass (static + physics + engine checks only)
IVP_FAST=1 bash independent_verification/RUN_ALL.sh

# point IVP-01 at the release archive (recommended)
IVP_ZIP=/path/to/Collapse-Hawking-Bridge-2.0.0.zip \
  bash independent_verification/RUN_ALL.sh
```

Requirements: Python >= 3.9 with `numpy`, `mpmath` (declared runtime
deps), `pytest` (dev), and optionally `sympy` for IVP-06 (falls back to
a numeric mode without it).  IVP-02 needs one or more of `python3.9
.. python3.13` on PATH; IVP-15 uses whatever toolchains exist
(`gcc`, `g++`, `node`, and optionally `julia`, `rustc`, `go`).

Individual checks can be run directly:

```bash
python3 independent_verification/IVP07_convergence.py
python3 independent_verification/IVP15_cross_language.py
```

## 6. Outputs

```text
independent_verification/
├── PROTOCOL.md              this document
├── RESULTS.md               committed audit report of the v2.0.0-IVP run
├── RUN_ALL.sh               one-command orchestration
├── summarize.py             rebuilds the verdict table from results/
├── ivp_common.py            shared infrastructure + independence contract
├── IVP01..IVP15             one standalone script per check
└── results/
    ├── IVP01.json ... IVP15.json   machine verdicts (committed audit trail)
    ├── IVP11_rows.json             full blind scan rows
    ├── SUMMARY.md                  verdict table
    └── logs/                       full console logs of the committed run
```

## 7. Scope and limits

* The suite audits the **shipped artifact**, not the authors or the
  history; it can establish that results reproduce (or not) under the
  declared protocol, and localize where they do not.
* Compute-bound checks (IVP-09..13) run at the resolutions documented
  in each script; `INCONCLUSIVE` outcomes there are statements about
  resolution, not about correctness.
* The audit environment (single machine, one core, specific OS) is
  recorded in every verdict JSON under `environment`.
