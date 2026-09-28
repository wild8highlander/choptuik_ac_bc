# code

Standalone computation engines for the **Choptuik–QCD bridge** — the
nine-section study presented in the `monograph/` manuscripts — implemented
independently in three languages, plus a Next.js web application that
visualises all nine sections. This folder is deliberately separate from
`../python/` and `../julia/` (which verify the Klein-quartic spinor
corrections): here the verified object is the QCD-bridge computation chain
itself, and having the same engine written three times turns cross-language
agreement into part of the verification.

## What is inside

| Folder | Contents |
|--------|----------|
| `python/` | Canonical engine `qcd_bridge_engine.py` (NumPy), report writer `report_engine.py`, CLI `run.py`, figure/animation generators, and `web_runner.py` — the stdin/stdout bridge used by the web app |
| `java/` | Independent Java port `qcd_bridge_engine.java` of the same nine sections, with its own report writers |
| `julia/` | Independent Julia port `qcd_bridge_engine.jl` (module `QCDBridge`) with the same section functions and report generation |
| `web/` | Next.js + React dashboard (`src/app`, `src/components`, `src/lib/qcd/…`) that recomputes all nine sections client-side and can also dispatch the Python engine via API routes |

## The nine verified sections

| § | Computation | Function (Python source of truth) |
|---|-------------|-----------------------------------|
| 1 | O_chi operator construction and spectrum (28×28 = 22 K3 + 6 N_f) | `build_Ochi` |
| 2 | RMT universality sweep (GUE vs Poisson) across κ_T | `kappa_T_sweep` |
| 3 | Spectral staircase vs Wigner semicircle, spacing statistics | `folded_spacings` |
| 4 | N-scaling of ⟨λ⟩ → 0 (1/√N artifact) | `N_scaling_test` |
| 5 | τ_relax dynamics (CKM residual damping) | `tau_relax_dynamics` |
| 6 | κ_T physical estimate from lattice Dirac data | `kappa_T_physical_estimate` |
| 7 | Cabibbo angle coincidence | `cabibbo_coincidence` |
| 8 | CP 8-step solution chain | `cp_solution_chain` |
| 9 | Jet wake bridge (numerical relativity ↔ QCD topological sectors) | `jet_wake_bridge` |

## How to run

Each subfolder has its own README with exact commands. Quick reference:

```bash
# Python (canonical): full verification of all 9 sections
python3 code/python/run.py --mode verify_all --non-interactive

# Java port (requires the JAMA jar, see code/java/README.md)
javac -cp jama.jar code/java/qcd_bridge_engine.java
java  -cp .:jama.jar code/java/qcd_bridge_engine

# Julia port (requires JSON; writes reports to qcd_bridge/reports_julia)
julia code/julia/qcd_bridge_engine.jl

# Web dashboard
cd code/web && bun install && bun run dev
```

Generated artifacts land in `../qcd_bridge/`: `figures/` (3D/4D PNG, PDF,
SVG per section), `animations/` (MP4/GIF), `reports/` (Python reports),
`reports_java/` (Java reports), driven by the configs in
`../qcd_bridge/configs/`.

## Notes

- All three engines share the same physical constants taken from the
  monograph: δ_C = π/7, N_HILBERT = 28, κ_T lower bound 2.62 / best fit 8.45,
  τ_relax = 5.0·10⁻⁴¹ s, sin²θ_Cabibbo = 0.051.
- The Python engine is the reference implementation; the Java and Julia
  ports re-derive every number independently, and each writes its own report
  set so the outputs can be diffed.
- Seeds are fixed (e.g. seed 42 in the CLI and Java RNG) to keep every run
  reproducible.
