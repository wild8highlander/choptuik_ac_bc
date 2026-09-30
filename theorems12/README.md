# theorems12 — The Twelve Theorems cycle, extended edition (20 theorems)

This folder is the load-bearing monograph layer of the repository: **twenty separate
monographs**, each fixing **one rigorous machine theorem** of the direct solution
programme for the Choptuik problem as a self-contained document — **every theorem in
English first (`monographs_en/`), then the complete Russian set (`monographs_ru/`)**,
80 files in all (DOCX + PDF × 20 × 2 languages).

Monographs No. 1–12 are the canonical **Twelve Theorems cycle** (the exact symbolic
layer, No. 1–6, and the machine-certified layer, No. 7–12). Monographs No. 13–20 are
the **supplementary series** extracted from the remaining machine verdicts of the
repository (spinor corrections, the figure cycle, the second flows, the annulus
record, the Roberts validation, the center hierarchy, the P4 Einstein–Hilbert
closure, and the machine-verified Hilbert derivation).

Every document follows the same academic standard: a cover, an abstract, a table of
contents, eight numbered sections (introduction, notation, formal statement, machine
proof sketch, numerical tables straight from the JSON verdicts, corollaries, honest
caveats, reproduction protocol) and a reference list. Nothing is fitted; every
number is traceable to a machine output.

## Layout

```text
theorems12/
├── monographs_en/          No. 1–20 (EN): theorem_01..20_*.docx + *.pdf  (40 files)
├── monographs_ru/          No. 1–20 (RU): theorem_01..20_*.docx + *.pdf  (40 files)
├── assets/formulas/        PNG formulas (mathtext, 300 dpi) for the hard cases
├── push_theorems.sh        auto-push to wild8highlander/choptuik_ac_bc via PAT
└── README.md               this file
```

## The table of the twenty theorems

| № | Theorem | One-line statement | Machine | Verdict JSON | EN | RU |
|---|---|---|---|---|---|---|
| 1 | The clock-pair theorem | GCD of the books = `T0h²(4T0h²−27)/4`, τ* = **27/4**; brick: τ* = **1323/(196−π²)** — one common root, book defect 0.0 | `clock_closure_t1c.py` | `clock_closure_t1c.json` | [pdf](monographs_en/theorem_01_clock_pair_EN.pdf) | [pdf](monographs_ru/theorem_01_clock_pair_RU.pdf) |
| 2 | The brick-ladder theorem | τ*(δ) = **27/(4−δ²)** = 27k²/(4k²−π²) exactly on **12/12** rungs δ_k = π/k; the clock is brick-invariant, the tick does not select | `brick_scan_tick.py` | `brick_scan_tick.json` | [pdf](monographs_en/theorem_02_brick_ladder_EN.pdf) | [pdf](monographs_ru/theorem_02_brick_ladder_RU.pdf) |
| 3 | The static factorization theorem | `UV_ξ3 = 2·R1h·Mdef_ξ5` identically; **S∩C = {R1h=0} ∪ {T0h=0} ∪ {T0h=T0h*}**; census G1–G3: 0 new branches | `global_static_search.py` | `global_static_search.json` | [pdf](monographs_en/theorem_03_factorization_EN.pdf) | [pdf](monographs_ru/theorem_03_factorization_RU.pdf) |
| 4 | The weight-rule theorem | Tables factor as `(λ+p)…(λ+p+n−1)F` (12/12, the dd-coefficient 1 derived); **M3ᵀM3 = (1+λ²)M2ᵀM2**, char3 = (1+λ²)⁹·char2, ±i are phantoms | `sympy_third_order.py` | `third_order_tables.json` | [pdf](monographs_en/theorem_04_weight_rule_EN.pdf) | [pdf](monographs_ru/theorem_04_weight_rule_RU.pdf) |
| 5 | The dd-closure theorem | rank Uk = 9 **exactly** (Q(√3)) — the closure is unique; **B = [[0, −350/61], [0, 0]]**, B² = 0 — a Jordan-2 nilpotent, δ_mono = 0 | `sympy_dd_closure.py` | `dd_closure.json` | [pdf](monographs_en/theorem_05_dd_closure_EN.pdf) | [pdf](monographs_ru/theorem_05_dd_closure_RU.pdf) |
| 6 | The flat-line theorem | The unique solution manifold through x* is the flat line: F = r = V = 0 exactly; b2 is static but the flow leaves S: **\|DrV\| = (39.2±0.2)·A** | `march_dae_nonlinear.py` | `march_dae_nonlinear.json` | [pdf](monographs_en/theorem_06_flat_line_EN.pdf) | [pdf](monographs_ru/theorem_06_flat_line_RU.pdf) |
| 7 | The holonomy theorem | Holonomy is admissible only diagonal (κ_C1 = κ_C2, κ_C2 = κ_TH); the exact family **τ*(κ) = 27/(2κ)**; the station ladder is holonomy-invariant; Berry closes ln τ* to **+0.062%** | `sympy_spectrum_tau_star.py` + `sympy_spinor_corrections.py` | `spectrum_tau_star.json` | [pdf](monographs_en/theorem_07_holonomy_EN.pdf) | [pdf](monographs_ru/theorem_07_holonomy_RU.pdf) |
| 8 | The identity + soft-pole theorem | **τ*(δ_C) = τ*_T1c = 1323/(196−π²)** — two routes, one number; the 45/8 pole is simple, coincides **exactly** with the char(2) root, the linear level stays finite | `sympy_center_o7.py` + `puiseux_soft_pole.py` | `q5_center_o7.json` + `q6_puiseux_soft_pole.json` | [pdf](monographs_en/theorem_08_identity_pole_EN.pdf) | [pdf](monographs_ru/theorem_08_identity_pole_RU.pdf) |
| 9 | The certified Krawczyk census | Interval census: 1 IN-box per convention point ([2.59806, 2.61861]; [2.66607, 2.66779]), 511 OUT-boxes; the 2D slice: **OUT 100.00%** — 0 new isolated branches | `krawczyk_census.py` | `q9_krawczyk_census.json` | [pdf](monographs_en/theorem_09_krawczyk_EN.pdf) | [pdf](monographs_ru/theorem_09_krawczyk_RU.pdf) |
| 10 | The structural barrier theorem | The elimination ideal of the books = {0}; a PSLQ null with positive controls; π/7 transcendental ⇒ **the algebraic books cannot select π/7** | `brick_selection.py` | `q1_brick_selection.json` | [pdf](monographs_en/theorem_10_barrier_EN.pdf) | [pdf](monographs_ru/theorem_10_barrier_RU.pdf) |
| 11 | The depth-wall theorem | The wall is window-policy sensitive: z 1.78 → 7.20 → **8.56** (root anchor, +19%); [F1]–[F4] — the wall is topological; the 4th echo peak reached | `deep_echo_v21.py` + `deep_echo_v22.py` | `v21_deep_echo.json` + `v22_v_budget.json` | [pdf](monographs_en/theorem_11_depth_wall_EN.pdf) | [pdf](monographs_ru/theorem_11_depth_wall_RU.pdf) |
| 12 | The honest-negative cluster | Δ_eff = 0.611 ± 0.446 — **NOT DSS** (3.44 excluded at 6.3σ); γ = 0.109 ± 0.105 against 0.374 — the mass floor M ≈ 4·du; p not measurable; the certificate Π = I + B·T to z = 30 | `choptuik_scaling.py` + `amplitude_ladder.py` + `depth_z30.py` | `choptuik_scaling.json` + `v20b_depth_z30.json` + `v22_v_budget.json` | [pdf](monographs_en/theorem_12_honest_negatives_EN.pdf) | [pdf](monographs_ru/theorem_12_honest_negatives_RU.pdf) |
| 13 | The spinor-corrections theorem | Exact quanta **bC = π²/98, aC = π⁵/369754**; no κ-leaks in the geometry; diagonal holonomy or dead; phantom hits ≤ **3.10%** of kπ/30 (screening off) | `sympy_spinor_corrections.py` | `spinor_corrections.json` | [pdf](monographs_en/theorem_13_spinor_corrections_EN.pdf) | [pdf](monographs_ru/theorem_13_spinor_corrections_RU.pdf) |
| 14 | The figure-cycle predictor theorem | The pyramid–cone–bowl cycle carries **36 compensated states inside S** (F = r = 0); 12/12 + 6/6 station landings; return defect 0.064, period 6 | `hexcycle_dae.py` | `hexcycle_dae.json` | [pdf](monographs_en/theorem_14_hexcycle_EN.pdf) | [pdf](monographs_ru/theorem_14_hexcycle_RU.pdf) |
| 15 | The second-flows theorem | char degree 22 = 9λ⁴·Q18; **0 genuine modes at the baseline**, 1 on the brick (the clock root itself) — the limit-cycle variables add no linear dynamics | `second_flows_exact.py` + `second_flows_verify.py` | `second_flows_exact.json` + `second_flows_verified.json` | [pdf](monographs_en/theorem_15_second_flows_EN.pdf) | [pdf](monographs_ru/theorem_15_second_flows_RU.pdf) |
| 16 | The annulus record theorem | The multi-zoom machine reaches **z = 9.3536** (7 Q-peaks); the torner binding M3/(R1·t0²) = 0.6687 vs 2/3 seen in data; τ* honestly unmeasured | `grid_machine_annulus.py` | `grid_machine_annulus.json` | [pdf](monographs_en/theorem_16_annulus_EN.pdf) | [pdf](monographs_ru/theorem_16_annulus_RU.pdf) |
| 17 | The Roberts validation theorem | The double-null solver reproduces the exact Roberts (1984) solution with **second-order convergence** (errors ÷4 per grid doubling, 0.82 s total) | `roberts_test.py` | `roberts_test.json` | [pdf](monographs_en/theorem_17_roberts_EN.pdf) | [pdf](monographs_ru/theorem_17_roberts_RU.pdf) |
| 18 | The center hierarchy theorem | The O1–O5 ladder derives every central amplitude; residual orders fixed per equation; **χ-corrections vanish at χ = 0** — the flat chain is the χ = 0 slice | `sympy_center.py` | `center_hierarchy.json` | [pdf](monographs_en/theorem_18_center_hierarchy_EN.pdf) | [pdf](monographs_ru/theorem_18_center_hierarchy_RU.pdf) |
| 19 | The P4 Einstein–Hilbert closure theorem | The shape cycle lives inside **G = κT** (all station equations ∝ components, factor −2/r); the ring 4/3 and the clock 1/3 derived, not postulated; the frozen point is not an attractor | `sympy_p4_einstein_hilbert.py` | `p4_einstein_hilbert.json` | [pdf](monographs_en/theorem_19_p4_einstein_hilbert_EN.pdf) | [pdf](monographs_ru/theorem_19_p4_einstein_hilbert_RU.pdf) |
| 20 | The Hilbert derivation theorem | The whole double-null Einstein–scalar system derived from the **Hilbert action** in one SymPy pass (1.9 s); the Hilbert identity exact; Roberts residual 4×10⁻⁴¹ | `sympy_derivation.py` | `derivation_results.json` | [pdf](monographs_en/theorem_20_hilbert_derivation_EN.pdf) | [pdf](monographs_ru/theorem_20_hilbert_derivation_RU.pdf) |

## Reading order

```text
Canonical cycle:
  Exact symbolic layer:   T1 (clock pair) → T2 (ladder) → T3 (factorization)
                          → T4 (weight rule) → T5 (dd-closure) → T6 (flat line)
  Machine-certified:      T7 (holonomy) → T8 (identity + pole) → T9 (Krawczyk census)
                          → T10 (barrier) → T11 (depth wall) → T12 (honest negatives)
Supplementary series:
  Foundations:            T20 (Hilbert derivation) → T17 (Roberts validation) → T18 (center hierarchy)
  Structure:              T19 (P4 EH closure) → T13 (spinor corrections) → T15 (second flows)
  Global + depth:         T14 (figure cycle) → T16 (annulus record)
Cross links: T1⇔T7 (books & holonomy), T2⇒T10 (ladder ⇒ barrier), T3⇒T6 (factorization ⇒ march),
T5⇒T12 (Jordan-2 ⇒ linear certificate), T20⇒T19 (derivation ⇒ closure), T18⇒T19 (hierarchy ⇒ ring/clock),
T14⇒T6 (figure cycle globalizes the flat line), T17⇒T11/T16 (validation ⇒ depth campaigns)
```

## How to verify

```bash
# from the repository root
python3 -m pytest tests/ -q                 # 58 passed
cd einstein_direct
python3 clock_closure_t1c.py                # theorem 1
python3 brick_scan_tick.py                  # theorem 2
python3 global_static_search.py             # theorem 3
python3 sympy_third_order.py                # theorem 4
python3 sympy_dd_closure.py                 # theorem 5
python3 march_dae_nonlinear.py              # theorem 6
python3 sympy_spectrum_tau_star.py          # theorem 7
python3 sympy_center_o7.py                  # theorem 8
python3 krawczyk_census.py                  # theorem 9
python3 brick_selection.py                  # theorem 10
python3 deep_echo_v21.py --phase all        # theorem 11
python3 choptuik_scaling.py --n-bisect 1200 # theorem 12
python3 sympy_spinor_corrections.py         # theorem 13
python3 hexcycle_dae.py                     # theorem 14
python3 second_flows_exact.py               # theorem 15
python3 grid_machine_annulus.py             # theorem 16
python3 roberts_test.py                     # theorem 17
python3 sympy_center.py                     # theorem 18
python3 sympy_p4_einstein_hilbert.py        # theorem 19
python3 sympy_derivation.py                 # theorem 20
```

## Publishing

Push to the repository from a phone or a PC: `bash push_theorems.sh` (the PAT is
taken from the `GH_PAT` environment variable or prompted hidden). The script runs a
GitHub API preflight, commits the `theorems12/` folder together with the updated
root README, and verifies the push via `ls-remote`.

## The honesty of the cycle

Every monograph carries an honest-caveats section: truncated towers, Puiseux
branches at the soft pole, census boundaries, the status of comparison anchors
(γ_Ch = 0.374, Δ ≈ 3.44, π/30) and the symbolic-versus-numerical boundary are fixed
inside the document itself, not in a ledger footnote. Negative results (the π/7
barrier, the not-DSS quartet, the mass floor, the unmeasured τ* of the annulus
record) hold the same standing as the exact theorems — the repository rule, applied
without exceptions.

## Authorship and license

The author of all twenty monographs and of the machines is **Isahk Khamzatovich
Isaev** (GitHub: [@wild8highlander], sole author and maintainer). License: Isaev
Proprietary (see LICENSE at the repository root). Cycle date: 2026-09-30.
