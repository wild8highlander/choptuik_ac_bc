# Phase 3 — Stability, Scaling, Universality (months 18–27)

> Goal: from "the critical solution exists" to "this is why every
> family of data sees the same γ and the same echoing".

## Objective

Linearize around the (now formal) critical solution, prove the spectral
core (gap G2), derive γ = 1/λ₀, and assemble universality plus the
echoing formula — the externally observable predictions.

## Tasks

| # | Task | Months | Output |
|---|---|---|---|
| P3.1 | Linearized operator: definition and `C¹` dependence | 18–21 | `Stability/Linearization` beyond scaffold |
| P3.2 | Spectral analysis: exactly one unstable mode, rest in the left half-plane, echo spacing 2π/Δ | 19–23 | `unique_unstable_mode` discharged |
| P3.3 | Scaling law: linear instability ⇒ M ∝ \|p−p\*\|^γ, γ = 1/λ₀ | 22–24 | `mass_scaling_law` discharged |
| P3.4 | Echoing formula: periodic decoration of period Δ in ln\|p−p\*\| | 23–25 | `echoing_formula` discharged |
| P3.5 | Universality across data families | 24–27 | `universality` discharged |

## Acceptance criteria

- [ ] `#print axioms Choptuik.Scaling.universality` ⊆ three standard axioms.
- [ ] Derived γ agrees with the calibrated `gammaChoptuik` to `< 10⁻³` (closes `gamma_close_to_published`).
- [ ] The Python service's `scaling_fit` on freshly generated data reproduces the formally derived γ within the certified interval — proof and numerics now check each other.

## Risks

*Spectral theory of unbounded operators in mathlib* — the deepest
dependency; mitigated by scoping to the concrete operator rather than a
general theory.  *Time-translation quotient* — uniqueness statements
must quotient carefully; handled inside P3.2.
