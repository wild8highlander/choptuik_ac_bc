# Axiomatic Base of the Formal Choptuik Programme

> Rule of the house: the entire development must rest on Lean's three
> standard axioms — nothing else.  Every additional `axiom` declaration
> is a defect to be reported, not a convenience to be enjoyed.

## The three admissible axioms

| Axiom | Statement (essence) | Role in this programme |
|---|---|---|
| `Classical.choice` | every nonempty type admits a choice function | classical logic of the analysis layer: Hahn–Banach, open mapping, existence arguments in the IFT route (gap G1) |
| `propext` | logically equivalent propositions are equal | rewriting with `Iff` as equality; heavy use in the PDE bookkeeping |
| `Quot.sound` | quotients respect the defining relation | function spaces modulo equivalence; DSS fields up to scale covariance |

These are exactly the three axioms Lean's kernel ships with; `#print
axioms Choptuik.<theorem>` must therefore always report the subset
`[Classical.choice, propext, Quot.sound]` — the same minimal set used
by mathlib's PDE formalizations that this programme builds upon.

## Prohibited axioms

* No project-specific `axiom` may appear in `lean/Choptuik/**` theory
  modules.  (The example client `bridge/examples/LeanClient.lean`
  carries IO-side `axiom` contracts — that file is illustrative and
  excluded from the theory build.)
* No unchecked numerics may enter proofs: floats cross the bridge only
  as *certificates* (`interval_bound` enclosures), never as axioms.

## Enforcement

* CI greps `lean/Choptuik/**` for the token `axiom ` at declaration
  position and fails the build when a new one appears
  (see `ci/lean-ci.yml`).
* Milestone M2.3 ("existence assembly") requires the printed axiom set
  of `critical_solution_exists` to be recorded in its acceptance note.

## Why this matters

The credibility of a machine-checked physics theorem is exactly the
credibility of its axioms plus the kernel.  By freezing the three
standard axioms and refusing all others, the programme inherits the
same trust base as the rest of mathlib — and any future kernel or
mathlib audit automatically covers this development.  The only remaining
trust gap is the numerical bridge, which is why gap G5 (verified
interval arithmetic) is on the critical path: it converts the last
floating-point ingredient into checkable mathematics.
