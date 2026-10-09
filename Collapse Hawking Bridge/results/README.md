# results

The ledger folder of the **Collapse-Hawking Bridge**: `RESULTS.md`, the
one-page register of everything the project measured at v2.1.0 — every
line of it backed by a machine-readable verdict committed under
`campaigns/reference/` — plus the report folder of the C6 drift-law
campaign.

![version](https://img.shields.io/badge/version-2.1.0-8C6D1F)
![ledger](https://img.shields.io/badge/ledger-RESULTS.md-8C6D1F)
![C1](https://img.shields.io/badge/C1-45_runs_48.4_s-blue)
![C2](https://img.shields.io/badge/C2-26_runs_23.7_s-blue)
![C3](https://img.shields.io/badge/C3-P_anchor_1.28656_PASS-blue)
![C3b](https://img.shields.io/badge/C3b-16_runs_333.7_s-blue)
![C6](https://img.shields.io/badge/C6-вdrift_law_T10-C9A84C)
![tests](https://img.shields.io/badge/pytest-63_passed-brightgreen)
![audit](https://img.shields.io/badge/IVP--15-remediated_%2B_aligned-8C6D1F)

## TL;DR

- A "result" here is exactly two things: a committed verdict JSON in
  `campaigns/reference/` (the law) and a line in `RESULTS.md` (the
  prose). Both, or it is not a result.
- The headline table holds **21 numbers** at v2.1.0; several of them
  are honest negatives (γ and Δ unmeasurable at every committed depth,
  no claimable continuum threshold, the sub-dominant exact drift
  channel), stated with reasons, kept in the headline.
- Five campaigns: C1 (validation, born spectrum; 45 runs, 48.4 s),
  C2 (two branches; 26 runs, 23.7 s), C3 (Δ·γ; 31 runs, 13.7 s,
  P_anchor = 1.28656 → PASS), C3b (concentrated resolution with
  per-grid thresholds; 16 runs, 333.7 s, the floor law `(13 ± 1)/N`),
  C6 (the resolution-drift law of theorem T10; ~2 s, no engine march).
- All four engine campaigns were re-run at v2.1.0 with **physics
  byte-identical** to the committed values — the package's determinism
  claim is not a promise, it is a measured fact.
- The honesty register lists 8 standing caveats; none of them is hidden
  in a footnote.

## Contents

| entry | read it for |
|---|---|
| [RESULTS.md](RESULTS.md) | the 21-row headline register + verdict summaries + honesty register |
| [ROADMAP.md](ROADMAP.md) | the staged plan: what closed, what is open, what gates v3.0 |
| [scaling_drift/](scaling_drift/REPORT.md) | the C6 report: the two exact lemmas, the drift signature, the honest negatives |

## What counts as a result

The project keeps a strict two-part definition:

1. **A committed verdict.** A machine-readable JSON file under
   `campaigns/reference/`, produced by `campaigns/run_c1.py`,
   `run_c2.py`, `run_c3.py`, `run_c3b.py` or `run_c6_drift.py`,
   containing the full per-run payloads, the fit diagnostics and the
   honest notes. The verdict is the law: it is the only object the rest
   of the repository trusts.
2. **A ledger line.** A row in `RESULTS.md` — this folder's one-page
   summary — quoting that verdict in prose. The ledger is updated
   whenever a verdict changes; it never carries a number that the
   verdicts do not contain.

Derived artifacts (tables in `data/bridge/`, the figure suites, test
assertions) are downstream views of the verdicts, not results of their
own. If a number cannot be traced to `campaigns/reference/` through
this chain, it is not part of the record.

## Where the law lives

The verdicts do not sit in this folder. `results/` holds the prose
ledger; `campaigns/reference/` holds the machine-readable law:

| file (under `campaigns/reference/`) | role |
|---|---|
| `c1_verdict.json` | C1: engine validation, born spectra, honest notes. 45 runs, wall 48.4 s |
| `c2_verdict.json` | C2: the two branches — subcritical dispersal + born bifurcation. 26 runs, wall 23.7 s |
| `c3_verdict.json` | C3: Δ·γ products with honest nulls. 31 runs, wall 13.7 s |
| `c3b_verdict.json` | C3b: concentrated resolution, per-grid thresholds (F-2) — floor ladder, γ/Δ ladders. 16 runs, wall 333.7 s |
| `a_star_ladder.{json,csv}` | the F-1 remediation ladder: A\* at N=200…3200, tol 5e-8, straddle probes (committed artifact, unchanged since 2.0.1) |
| `c6_drift_verdict.json` | C6: the resolution-drift law (theorem T10) — ladder analysis, exact lemmas, channel calibration |
| `amplitude_scan_N400.csv` / `amplitude_scan_N800.csv` | born spectra at N=400/800 |
| `subcritical_scan.csv` / `bifurcation_ftilde.csv` | the two C2 branch scans |
| `c3b_gamma_ladder.csv` | the per-grid γ ladder (7 rows at N=1600 + 5 at N=3200) |
| `profiles_sub_supercritical.json` | 2m/r(r) snapshots of a sub- and a supercritical run |

The provenance chain, end to end:

```text
make c1 / c2 / c3 / c3b / c6   campaigns/run_c{1,2,3,3b}_*.py, run_c6_drift.py
        -> campaigns/reference/*.json, *.csv          (the law)
        -> scripts/rebuild_data.py                    (make data)
        -> data/bridge/*.csv, *_summary.json          (13 derived tables)
        -> figures/ + results/RESULTS.md              (views of the law)
```

## Verdict summaries (short form)

Full per-key tables live in [RESULTS.md](RESULTS.md). The one-paragraph
version:

- **C1** — Roberts–Oshiro orders 2.031/2.093; the born spectrum over
  four ε decades; the mass floor carried honestly; junk rows kept.
- **C2** — q_max strictly monotone (0.0158 → 0.5845); the slowdown law
  `v = 0.510 − 0.0334 ln ε`; the echo rate 0.1909/e-fold below the
  0.2907 anchor; the bifurcation half-width 4.86e-3.
- **C3** — the anchor product 1.28656 sits 1.3% from the 1.27 target
  (**PASS** at the anchor level); the engine-level products are
  committed nulls with reasons.
- **C3b** — per-grid thresholds bisected fresh (F-2); the floor ladder
  0.0155 / 8.575e-3 / 4.245e-3 (the 1/N law with prefactor 13 ± 1);
  γ_eff = 0.041/0.060, floor-dominated — the honest negative re-confirmed.
- **C6** — the drift is a theorem: chord flattening κh²/8 and the
  chord-chain arc deficit, both machine-verified; the coefficients
  κ\* = 2728.60 and s = 413.8 calibrated on committed artifacts; the
  ladder signature (monotone drift, p_eff climbing) committed; the two
  honest negatives (no `A*_inf`; the exact channel sub-dominant) pinned
  by tests.

## Updating the ledger and the verdicts

The direction of authority is one-way: **verdicts are the law, the
ledger is prose.** The update sequence:

```bash
# 1. refresh the law (overwrites campaigns/reference/ artifacts)
make c1 && make c2 && make c3 && make c3b && make c6

# 2. re-derive the tables from the new verdicts
make data

# 3. update the prose: edit the affected rows of results/RESULTS.md
#    so that it quotes the new verdict exactly

# 4. pin everything
make test      # 63 passed
make validate  # 7/7 PASS
```

Rules:

- Never hand-edit `campaigns/reference/*.json|csv` or `data/bridge/*`.
  A verdict is produced only by a campaign run; a table only by
  `scripts/rebuild_data.py`.
- Never let `RESULTS.md` carry a number that no committed verdict
  contains. Rewording ledger prose is free; changing a quoted number
  without a verdict behind it is forbidden.
- If a rerun moves a physics number beyond the last digit, stop and
  investigate before committing: the engine is deterministic at fixed
  grid, so a real movement is a bug or an environment difference, and
  the test suite is the first line of defense.

## Reproducing everything from scratch

| # | command | expected outcome | wall-time |
|---|---|---|---|
| 1 | `make install` | `chbridge` installed editable | seconds |
| 2 | `make c1` | rewrites `c1_verdict.json` + scan CSVs + profiles; ends with `DONE in ~48 s` | ~1 min |
| 3 | `make c2` | rewrites `c2_verdict.json` + 2 CSVs; prints the slowdown fit, echo rate, `M_sat = 0.03519`, `eps_half = 4.860e-03` | ~30 s |
| 4 | `make c3` | rewrites `c3_verdict.json`; prints `P_anchor = 1.28656 -> PASS` | ~15 s |
| 5 | `make c3b` | rewrites `c3b_verdict.json` + ladder CSV; bisects per-grid A\*_N first; prints γ_eff 0.0410/0.0605, floors 8.6e-3/4.2e-3, `P_engine_deep = None` | ~6 min |
| 6 | `make c6` | rewrites `c6_drift_verdict.json` + 2 CSVs; prints the ladder facts, the lemma precisions, the channel shares | ~2 s |
| 7 | `make data` | 13 tables in `data/bridge/`, byte-identical to the committed ones | ~2 s |
| 8 | `make figures` | 28 PNGs; last line `28 figures written (7 x 2 lang x 2 theme)` | ~15 s |
| 9 | `make test` then `make validate` | `63 passed`; `7/7 checks PASS (mpmath dps=50, chbridge v2.1.0)` | ~1 s |

After the sequence, `md5sum data/bridge/*` must agree with the
committed tables; if it does, the whole chain — engine, verdicts,
tables, figures — reproduces.

## FAQ

**Where do campaign outputs go?**
Into `campaigns/reference/` — five verdict JSONs, the two C1 scan CSVs,
the two C2 branch CSVs, the C3b ladder CSV, the C6 tables, the profiles
JSON and the F-1 ladder — all committed, all machine-readable. Nothing
lands in `results/` except the ledger and the C6 report folder, and
nothing derived lands anywhere until `make data` runs.

**What if I rerun and get a different last digit?**
You will not, for physics numbers: the double-null engine is
deterministic at fixed grid, `make data` reproduces the committed
tables byte-for-byte (pinned by
`tests/test_bridge.py::test_rebuild_determinism`), and at this release
the full campaign re-run was verified field-by-field identical. What
legitimately changes is run metadata — `wall_total_s` and the
timestamp — which the verdict keeps as metadata and nothing downstream
asserts on.

**Can I edit `RESULTS.md` without rerunning the campaigns?**
Only the prose. Every quoted number must already exist in a committed
verdict; if you want a different number, produce the verdict first,
then update the ledger to match.

**Why is C3 a PASS when γ and Δ are engine-unmeasurable?**
The PASS refers to the anchor-level product: P_anchor = 3.44 × 0.374 =
1.28656 against target 1.27 ± 0.05. The engine-level products are
committed as nulls with reasons (floor-flat γ fit, echo detector
resolving 2 peaks per run against a 3-peak minimum). Both facts live in
the same verdict — that is the point. C3b re-tested the engine level
with deep grids: the nulls survived; C6 explains *why* the fixed-grid
threshold itself must drift (theorem T10).

**What is a "junk row"?**
A scan row whose black-hole mass falls outside the physical scale
(M > 0.1 code units); the campaign flags it `sane = false`, relabels its
stop reason, and keeps it verbatim — 6 such rows in C1's two scans and
3 in C2's bifurcation. Dropping them would make the spectrum look
cleaner than the engine actually is.

**Which campaign owns the floor number?**
C3b owns the LAW (the 1/N scaling with prefactor 13 ± 1, three grids,
per-grid F-2 values); C1's `mass_floor_N800 = 0.0155` is the N=800
point of the same ladder.

**Which campaign owns the drift?**
The F-1 remediation run owns the committed ladder; C6 owns the LAW
(why it drifts, in which direction, through which exact channel, and
what cannot be claimed from it).

## See also

- [RESULTS.md — the living ledger](RESULTS.md)
- [scaling_drift/ — the C6 report folder](scaling_drift/REPORT.md)
- [ROADMAP.md — the staged plan](ROADMAP.md)
- [C1–C3b + C6 verdicts (the law)](../campaigns/reference/)
- [methods: engine, campaigns, idealisations](../docs/methods.md)
- [validation: what holds, what is honestly null](../docs/validation.md)
- [scripts: how tables and figures are derived](../scripts/README.md)
- [repository root README](../README.md)

## Краткое резюме (Russian)

Папка `results/` — журнал результатов проекта: реестр RESULTS.md
(21 заголовочное число, сводки вердиктов, регистр честности из 8
пунктов), роадмап ROADMAP.md и папка отчёта кампании C6
`scaling_drift/` (закон дрейфа с разрешением — теорема T10). Источник
каждого числа — машиночитаемый вердикт в `campaigns/reference/`:
вердикты — закон, журнал — проза. Все пять кампаний v2.1.0 прогнаны
свежими; четыре движковые дали физику, байт-идентичную зафиксированной.
Полное воспроизведение с нуля — таблица из девяти make-шагов выше;
таблицы воспроизводятся побайтово.
