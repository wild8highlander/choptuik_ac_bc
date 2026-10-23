# Module Map — Choptuik.* namespace

> Machine-checkable table of the theory: module → mathematical content →
> proof obligations → consuming artifacts.  `sorry` count is the honest
> debt ledger of the scaffold.

| Module | Content | Obligations (`sorry`) | Gap ids | Phase |
|---|---|---|---|---|
| `Choptuik.Geometry.Basic` | double-null arena, areal positivity, mass aspect | 0 | — | P1 |
| `Choptuik.Geometry.Curvature` | Kretschmann/Weyl profile, strong + isotropic singularity | 2 | G3 | P2–P3 |
| `Choptuik.Analysis.HyperbolicPDE` | Einstein–scalar system, constraints, well-posedness | 1 | G1 | P2 |
| `Choptuik.Analysis.Interval` | interval type, add/mul soundness, certificate principle | 1 | G5 | P1 |
| `Choptuik.Existence.DSS` | DSS covariance, critical solution, existence + uniqueness | 2 | G1 | P2 |
| `Choptuik.Existence.ImplicitFunction` | Banach IFT route, perturbation persistence | 2 | G1, G5 | P2 |
| `Choptuik.Stability.Linearization` | perturbation modes, linearized operator interface | 0 | — | P3 |
| `Choptuik.Stability.Spectrum` | unique unstable mode, γ = 1/λ₀, scaling law | 2 | G2 | P3 |
| `Choptuik.Scaling` | universality, echoing formula | 4 | G1, G2 | P3 |

Totals (scaffold v0.3): **14 proof obligations** across 6 modules,
5 modules clean.

## Import graph

```
Geometry.Basic ─┬─▶ Geometry.Curvature
                ├─▶ Analysis.HyperbolicPDE ─┬─▶ Existence.DSS ─┬─▶ Stability.Linearization ─▶ Stability.Spectrum ─┐
                └─▶ Analysis.Interval ─────▶ Existence.ImplicitFunction ─┘                                                   ├─▶ Scaling
                                                                                                                             │
                       (root re-exports: Choptuik.lean imports everything above) ◀───────────────────────────────────────────┘
```

## Bridge consumption map

| Python endpoint | Feeds |
|---|---|
| `evolve` | numeric seed for `existence_via_implicit_function` (G1) |
| `spectrum` | calibration target for `unique_unstable_mode` (G2) |
| `scaling_fit` | check against `mass_scaling_law` (G2 corollary) |
| `echo_period` | check against `echoingPeriod = ln 2` |
| `interval_bound` | strict bounds absorbed by `existence_persists_under_perturbation` (G5→G1) |
