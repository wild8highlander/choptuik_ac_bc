# Phase 2 — Existence of the Critical Solution (months 6–18)

> Goal: the central blocker G1 falls.  By the end of this phase the
> repository contains a machine-checked statement that the Choptuik
> critical solution *exists*.

## Objective

Formalize the Einstein–scalar system, define DSS solutions exactly, and
assemble the existence proof following the Reiterer–Trubowitz strategy:
numeric profile + Newton correction + compact inverse + implicit
function theorem.

## Tasks

| # | Task | Months | Output |
|---|---|---|---|
| P2.1 | Einstein–scalar system in the double-null sector: explicit constraint + evolution equations | 6–9 | `Analysis/HyperbolicPDE` beyond scaffold |
| P2.2 | DSS definition and scale-covariance calculus | 8–10 | `Existence/DSS` exact |
| P2.3 | Numeric seed: high-precision profile from the service, packaged as Lean data | 9–11 | typed `evolve` consumption |
| P2.4 | Banach space of exponentially decaying sequences; residual map `Φ`; `C¹` regularity | 10–15 | `ImplicitFunction` infrastructure |
| P2.5 | Compact inverse of the linearized operator (the Reiterer–Trubowitz heart) | 12–16 | `DerivIsomorphism` instance |
| P2.6 | Existence assembly: IFT ⇒ exact critical solution; uniqueness up to scale/translation | 15–18 | `critical_solution_exists` discharged |

## Acceptance criteria

- [ ] `#print axioms Choptuik.Existence.critical_solution_exists` shows the three standard axioms only.
- [ ] Echoing period of the constructed solution matches the service's `echo_period` to the certified precision.
- [ ] Singularity geometry (gap G3) has at least the strong-singularity half proven.

## Risks

*Compact inverse in Lean* — the heaviest analysis lift; fallback is to
formalize the published inequalities as a self-contained operator theory
chapter.  *Numeric packaging* — mitigated by the interval certificate
path (G5), which is built in Phase 1 precisely for this.
