# Phase 1 — Mathematical Foundation (months 0–6)

> Goal: the arena and the tools exist and are trusted.  Nothing about
> the critical solution is proven yet; everything about the stage on
> which it will be proven is ready.

## Objective

Build the mathematical substrate in Lean 4 + mathlib and the operational
bridge to the numerical service, so that Phase 2 can attack existence
without infrastructure work.

## Tasks

| # | Task | Months | Output |
|---|---|---|---|
| P1.1 | Environment: Lean 4, Lake, mathlib pin, VS Code, CI skeleton | 0–1 | `lake build` green on CI |
| P1.2 | Differential geometry review vs mathlib: manifolds, tensor fields, Christoffel/Riemann/Ricci | 0.5–3 | geometry layer beyond `Geometry.Basic` |
| P1.3 | Spherical symmetry: SO(3) action, reduction to the `(u,v)` sector, double-null ansatz | 2–4 | replaces scaffold defs in `Geometry/Basic.lean` |
| P1.4 | Analysis groundwork: Fréchet derivatives, Lebesgue integration, function spaces for the PDE layer | 2.5–5 | `Analysis/` beyond scaffold |
| P1.5 | Python bridge v1: ZeroMQ harness, typed client, pytest regression lock | 4–6 | `bridge/protocol.md` v1.x implemented |
| P1.6 | Interval arithmetic (gap G5): outward rounding, soundness proofs | 2–5 | `Interval.mul_sound` discharged |

## Acceptance criteria

- [ ] `lake build` passes with **zero** `sorry` outside `gap_registry.csv` ids G1–G4.
- [ ] `Interval.mul_sound` proved; `certificate_principle` used in one worked example.
- [ ] A Lean client round-trips `ping`/`spectrum`/`interval_bound` against the service.
- [ ] Axiom audit: `#print axioms` on every theorem ⊆ {`Classical.choice`, `propext`, `Quot.sound`}.

## Risks

*mathlib version churn* — pin + CI rebuild on bump.  *Geometry scope
creep* — only the spherical-sector layer is in scope; general relativity
formalization is not.
