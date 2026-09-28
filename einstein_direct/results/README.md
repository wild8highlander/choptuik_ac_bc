# results/ — Machine-Readable Results of All Verification Campaigns

This folder contains the JSON outputs of every machine in the parent folder.
Each JSON is written by the machine that produced it and is re-read by the
pytest suite (`../tests/test_einstein_direct.py`), so every headline number in
the documentation is traceable to a file here.

## What is inside

| File | Produced by | Content |
|---|---|---|
| `derivation_results.json`, `derivation_log.txt` | `sympy_derivation.py` | machine verification of the Hilbert-action derivation (Roberts–Oshiro residuals) |
| `roberts_test.json` | `roberts_test.py` | exact-solution regression of the solver |
| `choptuik_scaling.json` | `choptuik_scaling.py` | fixed-grid bisection, critical amplitude, mass-scaling floor |
| `zoom_campaign.json` | `zoom_campaign.py` | prototype zoom campaign |
| `zoom_campaign_regular.json` | `zoom_campaign_regular.py` | regular center closure protocol + spinor wall diagnostics |
| `zoom_campaign_taylor.json` | `zoom_campaign_taylor.py` | central Taylor patch campaign |
| `center_hierarchy.json`, `center_modes.json` | `sympy_center.py`, `center_modes.py` | machine-derived center hierarchy; CSS fixed-point clock |
| `center_o6_nsolve.json` | `sympy_center_o6_nsolve.py` | nsolve verdict on the truncated O6+ tower |
| `spinor_analysis.json` | `spinor_analysis.py` | π/15, π/30 exponent diagnostics |
| `spinor_corrections.json`, `spinor_corrections_one_brick.json` | `sympy_spinor_corrections.py` | b-C / a-C / a-B corrections embedded in the towers |
| `spinor_ladder.json` | `spinor_ladder.py` | spinor ladder relations |
| `spectrum_tau_star.json` | `sympy_spectrum_tau_star.py` | exact spectrum of the corrected system at the critical scale |
| `grid_machine_annulus.json` | `grid_machine_annulus.py` | annulus-parity machine: echo-aware fits, percent-level τ* |
| `grid_machine_hexcheck.json` | `grid_machine_hexcheck.py` | hexcheck campaign: κ = ln(64/9), W2/t0² ladder |
| `grid_machine_mirror.json` | `grid_machine_mirror.py` | mirror-ring pair measurement of W2/t0² |
| `probe_channel_eps1e-03.json` | `probe_channel_trace.py` | line-by-line trace of the stage-death channel |
| `hexcycle.json` | `sympy_hexcycle.py` | hexagonal transformation cycle books |
| `hexcycle_dae.json` | `hexcycle_dae.py` | figure cycle embedded in the nonlinear DAE tower |
| `dae_nonlinear.json`–related: `march_dae_nonlinear.json` | `march_dae_nonlinear.py` | nonlinear DAE march (flat-line verdict) |
| `march_delta_mono.json` | `march_delta_mono.py` | δ_mono measured by two independent marches |
| `dd_closure.json` | `sympy_dd_closure.py` | independent dd-evolution law, prolongation closure |
| `third_order_tables.json` | `sympy_third_order.py` | third-order tables, weight rule |
| `second_flows_exact.json`, `second_flows_verified.json`, `second_flows_limit_cycle.json` | second-flows machines | second flows as limit-cycle variables |
| `p4_einstein_hilbert.json` | `sympy_p4_einstein_hilbert.py` | P4 closure in Einstein and Hilbert equations |
| `clock_closure_t1c.json` | `clock_closure_t1c.py` | clock closure through the one-brick T1c source form |
| `brick_scan_tick.json` | `brick_scan_tick.py` | intermediate bricks: tick obstruction vs δ |
| `global_static_search.json` | `global_static_search.py` | exhaustive global static census |
| `_m2_B_*.npy`, `_m2_basis_*.npy` | march machinery | cached march operators (baseline and one-brick) |

## Conventions

- JSON files are UTF-8, `ensure_ascii=False`; booleans, verdict strings and
  `honest_notes` arrays are part of the schema — the pytest suite asserts on
  them, so they must not be hand-edited.
- Files with a leading underscore are caches; they can be deleted and are
  rebuilt on the next march run.
- The large campaign JSONs are self-describing: each carries its `config`
  block (all input constants, including the no-fit anchors) next to its
  `verdicts` and `honest_notes`.
