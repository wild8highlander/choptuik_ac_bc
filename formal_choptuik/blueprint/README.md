<p align="center">
  <img src="../assets/banners/banner_gaps.svg" alt="gap registry" width="100%">
</p>

# blueprint/ — the constitution of the programme

![spec](https://img.shields.io/badge/spec-v0.3-E8B44A?style=flat-square)
![gaps](https://img.shields.io/badge/gaps-G1..G6_ledger-E86A6A?style=flat-square)
![axioms](https://img.shields.io/badge/axioms-3_standard_only-8FB7A4?style=flat-square)
![verdict](https://img.shields.io/badge/verdict-Lean_4-9B8CDE?logo=lean&logoColor=white&style=flat-square)

Where decisions live so that code does not have to improvise: the
technical specification, the axiomatic base, the classified gap ledger,
the proof-assistant decision record, and the module map.

## Contents

| File | What it fixes |
|---|---|
| [`technical_specification.md`](technical_specification.md) | language, environment, module discipline, integration architecture, quality workflow |
| [`axiomatic_base.md`](axiomatic_base.md) | the three admissible axioms (`Classical.choice`, `propext`, `Quot.sound`), prohibition + CI enforcement of project axioms |
| [`gap_registry.csv`](gap_registry.csv) | **the obligation ledger**: G1–G6 with severity, dependencies, strategy, phase, status |
| [`tooling_decision_matrix.md`](tooling_decision_matrix.md) | Isabelle/HOL vs Coq/Rocq vs Lean 4 — scorecard, verdict, reopening conditions |
| [`module_map.md`](module_map.md) | module ↔ obligation ↔ gap ↔ phase; import graph; bridge consumption map |

## The two blockers, stated plainly

> **G1 — existence.**  No machine-checked proof yet exists that a smooth
> DSS solution of the spherically symmetric Einstein–scalar system exists.
> The Reiterer–Trubowitz result is computer-assisted, not machine-checked.
> Strategy: Newton correction in a Banach space of exponentially decaying
> sequences, compact inverse, implicit function theorem.  Phase II.

> **G2 — stability.**  No machine-checked proof that the linearized
> spectrum has exactly one positive eigenvalue with the rest in the left
> half-plane and echo spacing 2π/Δ.  Everything public about γ = 1/λ₀
> hangs on this spectrum.  Phase III.

Everything else (G3–G6) is enabling infrastructure.  A gap may be closed
only with: a discharged `sorry`, the printed axiom set, and the paired
test or numerical cross-check — recorded in the registry's `status`
column.

<p align="center">
  <img src="../assets/banners/divider_photon.svg" alt="" width="100%">
</p>
