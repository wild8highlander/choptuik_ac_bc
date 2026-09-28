# julia

The Julia implementation of the verification and simulation suite — an
independent reimplementation of the Python stack (`../python/`) used for
cross-language verification. The same reference constants, formulas and
checks are coded from scratch against Julia's `LinearAlgebra`, so agreement
between the two stacks is itself evidence that the results are not artifacts
of one library or one implementation.

## What is inside

| Path | Contents |
|------|----------|
| `run.jl` | Entry point: parses CLI flags, activates the project, launches the interactive menu or the non-interactive runs |
| `Project.toml` | Project `ChoptyukSpinor`; dependencies: `LinearAlgebra`, `Dates`, `Printf`, `JSON`, `Plots`; test target with `Test` |
| `src/` | Module sources: `ChoptyukSpinor.jl` (umbrella module), `klein_curve.jl`, `spinor_phases.jl`, `dirac_operator.jl`, `choptyuk_formula.jl`, `surfaces.jl`, `hypothesis.jl`, `qnm.jl`, `enhanced_verification.jl`, `simulation.jl`, `visualization.jl`, `reporting.jl`, `interactive_menu.jl` |
| `test/runtests.jl` | Test suite comparing computed values against monograph reference constants |
| `config/default_config.json` | Default parameters: λ₁ = 3.838, R = −2, δ_C = π/7, tolerance, output dir, surface catalogue (Bolza, Klein, Bring, Macbeath), LIGO event table |
| `presets/standard.json` | Canonical Klein-curve preset with the unified formula spelled out: Δ_Ch = λ_{D²,triv} + δ_C²/2 + δ_C⁴/8 − δ_C⁵/22 + δ_C⁶/2 |

## How to run

```bash
cd julia
julia --project=. -e 'using Pkg; Pkg.instantiate()'   # first time only

julia run.jl                     # interactive mode (default)
julia run.jl --non-interactive   # full simulation run, then exit
julia run.jl --verify            # verification only
julia run.jl --output DIR        # custom output directory
julia run.jl --help              # help
```

Tests:

```bash
julia --project=. -e 'using Pkg; Pkg.test()'
```

`test/runtests.jl` checks the Klein curve fields (genus 3, automorphism
order 168, R ≈ −2, Hurwitz identity), the spinor phases, and the formula
outputs against the monograph reference values with strict tolerances
(10⁻⁶ strict / 10⁻³ loose):

| Reference constant | Value |
|--------------------|-------|
| Δ_bC | 3.438710 |
| Δ_Ch (base) | 3.437883 |
| Δ_Ch (full) | 3.447040 |
| b_Ch | 0.376510 |
| λ₁(D²) trivial Dirac | 3.338 |

## Verification content

- Klein quartic geometry and its Hurwitz property.
- Spinor phase enumeration from δ_A = π/2, δ_B = π/3, δ_C = π/7 (64
  structures, as in the Python stack).
- Dirac operator eigenvalue via the Lichnerowicz identity
  λ₁(D²_σ₀) = λ₁(Δ) + R/4.
- Unified formula evaluation, parameter sweeps (`n_sweep` points) and
  convergence analysis, plotted with `Plots`.
- Reports in the same multi-format layout as the Python engine, driven by
  `src/reporting.jl`.
- The interactive menu (`src/interactive_menu.jl`) mirrors the Python menu:
  parameter editing, hypothesis testing with custom spinor structures, and
  report generation.

## Notes

- Toolchain: Julia ≥ 1.9 (set by `[compat]` in `Project.toml`); third-party
  packages are limited to `JSON` and `Plots` — everything else is standard
  library, keeping the dependency surface auditable.
- Outputs go to the directory given with `--output` (default `output/`),
  containing plots, reports and logs in the same structure as the Python
  stack.
- The QCD-bridge companion engine has a separate Julia port in
  `../code/julia/qcd_bridge_engine.jl`; this folder is the Klein-quartic
  verification suite only.
- For a containerised environment with Julia preinstalled, see
  `../.devcontainer/` (Julia feature with `JULIA_PROJECT` preset).
