# Technical Specification — formal_choptuik

> The blueprint of record.  Everything in `lean/`, `python/` and
> `bridge/` is an implementation of this document.

## 1. Language and environment

| Item | Decision |
|---|---|
| Proof assistant | **Lean 4** (decision record: `tooling_decision_matrix.md`) |
| Math library | mathlib, pinned release matching `lean/lean-toolchain` |
| Build system | Lake (`lake build`; artifacts: checked `.olean` modules) |
| Editor | VS Code + lean4 extension |
| Numerical service | Python ≥ 3.10, numpy; ZeroMQ optional extra |
| CI | GitHub Actions: `lake exe cache get!` + `lake build` + pytest (template in `ci/lean-ci.yml`) |

## 2. Module organization

Namespace `Choptuik.*`, one mathematical area per module (modular
library discipline: every module compiles independently against mathlib
plus its imports):

```
Choptuik.Geometry.Basic          spherical symmetry, double-null arena      gaps: —
Choptuik.Geometry.Curvature      Kretschmann/Weyl, isotropic singularity    gaps: G3
Choptuik.Analysis.HyperbolicPDE  Einstein–scalar system, well-posedness     gaps: G1
Choptuik.Analysis.Interval       interval arithmetic, soundness             gaps: G5
Choptuik.Existence.DSS           DSS covariance, critical solution          gaps: G1
Choptuik.Existence.ImplicitFunction  Banach IFT route                       gaps: G1
Choptuik.Stability.Linearization perturbation modes, linearized operator    gaps: G2
Choptuik.Stability.Spectrum      unique unstable mode, γ = 1/λ₀             gaps: G2
Choptuik.Scaling                 scaling law, echoing, universality         gaps: G2
```

The authoritative machine-readable mapping lives in `module_map.md`;
the obligation ledger is `gap_registry.csv`.

## 3. Integration with existing code

* The parent repository's Python computations are preserved as-is; this
  folder adds a **service wrapper** (`python/choptuik_service/`) and a
  **typed protocol** (`bridge/protocol.md`), not a rewrite.
* Architecture: Lean client ──FFI/C ABI──▶ ZeroMQ REQ ──▶ Python REP.
  The pattern follows the public `lean-python-bridge` prototype.
* The Lean side consumes only interval certificates; raw floats never
  enter the proof layer (see `axiomatic_base.md`).

## 4. Axiomatic policy

Exactly `Classical.choice + propext + Quot.sound` (details and CI
enforcement: `axiomatic_base.md`).

## 5. Quality workflow

1. **Prose before proof.** Every mathematical idea lands as a documented
   statement with a natural-language comment of its role in the proof
   tree, then the formalization.
2. **`sorry` is a ledger entry.** Each `sorry` in `lean/Choptuik/**`
   names a gap id (`G1…G6`) in a trailing comment; CI cross-checks the
   ids against `gap_registry.csv`.
3. **Regression-locked numerics.** `python -m pytest tests/` must stay
   green; the protocol changes only with paired tests (discipline
   inherited from the parent repository's verify-per-commit culture).
4. **Reproducibility.** All datasets/figures/animations regenerate from
   `python/scripts/` with fixed seed 1993.
5. **Honest caveats.** READMEs state scope explicitly: the shipped
   model is a calibrated laboratory, not a solution of the full system.

## 6. Out of scope (current revision)

* Full 1+1 D characteristic Einstein solver (belongs to the parent
  repository's `Einstein Direct` programme; consumed here as data).
* Kernel-level verification of floating-point rounding (covered by the
  interval layer at the specification level instead).
