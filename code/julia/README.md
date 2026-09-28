# code/julia

Independent Julia implementation of the Choptuik–QCD bridge engine: a port
of `../python/qcd_bridge_engine.py` exposing the same nine monograph
sections as the module `QCDBridge`. Like the Java port, it exists for
cross-language verification — the numbers for every section are recomputed
with Julia's `LinearAlgebra` and compared against the canonical Python and
Java reports.

## What is inside

| File | Contents |
|------|----------|
| `qcd_bridge_engine.jl` | Module `QCDBridge` (~37 KB) exporting all section functions: `build_Ochi`, `folded_spacings`, `gue_spacing_pdf`, `poisson_spacing_pdf`, `bayes_factor_gue_poisson`, `classify_BF`, `kappa_T_sweep`, `N_scaling_test`, `tau_relax_dynamics`, `kappa_T_physical_estimate`, `cabibbo_coincidence`, `cp_solution_chain`, `jet_wake_bridge`, plus `QCDBridgeConfig`, `run_all`, `generate_report` |

## How to run

The file is runnable as a script; a CLI block at the bottom parses the same
flags as the other engines:

```bash
# all 9 sections (default mode)
julia qcd_bridge_engine.jl

# selected sections
julia qcd_bridge_engine.jl --section 1,3,5

# custom kappa_T (default 8.45)
julia qcd_bridge_engine.jl --custom 8.45
```

Each run prints the generated report paths and elapsed time. Reports are
written to `../../qcd_bridge/reports_julia/` in all seven formats
(`json`, `txt`, `md`, `html`, `csv`, `pdf`, `docx`).

## Verification content

The exported section functions correspond one-to-one to the Python engine:

| § | Computation | Exported function |
|---|-------------|-------------------|
| 1 | O_chi operator and spectrum (28×28) | `build_Ochi` |
| 2 | RMT universality sweep across κ_T | `kappa_T_sweep`, `bayes_factor_gue_poisson`, `classify_BF` |
| 3 | Spectral staircase and spacing statistics | `folded_spacings`, `gue_spacing_pdf`, `poisson_spacing_pdf` |
| 4 | N-scaling of ⟨λ⟩ → 0 | `N_scaling_test` |
| 5 | τ_relax dynamics | `tau_relax_dynamics` |
| 6 | κ_T physical estimate | `kappa_T_physical_estimate` |
| 7 | Cabibbo angle coincidence | `cabibbo_coincidence` |
| 8 | CP 8-step solution chain | `cp_solution_chain` |
| 9 | Jet wake bridge | `jet_wake_bridge` |

## Notes

- Dependencies: standard library plus `JSON` (imported at the top of the
  module). Julia ≥ 1.9 with `LinearAlgebra`, `Random`, `Statistics`, `Dates`,
  `Printf` covers everything else.
- The module can also be used as a library: `include` the file, then call
  `QCDBridge.run_all(QCDBridgeConfig(...))` directly from a REPL or notebook.
- Constants mirror the Python and Java engines exactly (δ_C = π/7,
  N_HILBERT = 28, κ_T 2.62/8.45, τ_relax = 5.0e-41 s) so outputs are directly
  comparable across the three languages.
- This engine is separate from the Klein-quartic verification suite in
  `../../julia/` (`ChoptyukSpinor`); that one checks the spinor corrections,
  this one checks the QCD bridge.
