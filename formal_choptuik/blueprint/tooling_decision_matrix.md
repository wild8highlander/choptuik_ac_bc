# Tooling Decision Matrix — Isabelle/HOL vs Coq/Rocq vs Lean 4

> Strategic decision record.  Verdict: **Lean 4**.  Rationale below.

## Scorecard

| Criterion | Isabelle/HOL | Coq / Rocq | Lean 4 |
|---|---|---|---|
| Foundational logic | HOL (simple type theory) | CIC (dependent types) | CIC (dependent types) |
| Trusted kernel | small LCF kernel | small LCF kernel | small LCF kernel |
| Library for analysis / PDEs | AFP (solid but scattered) | math-comp/analysis (growing) | **mathlib: topology, Banach/Hilbert, measure, manifolds, De Giorgi–Nash–Moser precedent** |
| Automation | **Sledgehammer (external ATP/SMT) — best-in-class** | SSReflect + tactics | native meta-programming (`grind`, `aesop`, `polyrith`) |
| Readability of proofs | **Isar — the readability standard** | good (SSReflect style is dense) | good (structured + tactic hybrid) |
| Dependent types | ✗ (limits expressiveness) | ✓ | ✓ |
| Python / FFI integration | limited | limited | **mature FFI (C ABI) + public ZeroMQ bridge prototype** |
| Community trajectory | stable | stable | **fast-growing, major funding, Tao's extensional use** |
| Fit to Choptuik programme | good automation, weaker analysis stack | algebra-first, analysis gap | **best coverage of exactly the needed mathematics + keeps Python code alive** |

## Why Lean 4

1. **The mathematics already exists.** The formalization needs real
   analysis (Banach/Hilbert spaces, spectral notions, differential
   geometry, measure/integration).  mathlib carries the university
   curriculum and has demonstrated the hard-PDE use case with the De
   Giorgi–Nash–Moser effort — the closest public precedent to the
   regularity analysis the Reiterer–Trubowitz proof requires.
2. **The existing Python code survives.** The parent repository's
   numerical stack is an asset.  Lean's FFI + the ZeroMQ client pattern
   let the proof layer *drive* the numerics instead of replacing them
   (architecture: `figures/fig_architecture.png`).
3. **Classical mathematics without guilt.** Lean's `Classical.choice`
   default matches working mathematicians' style; no constructive
   straightjacket, same three-axiom trust base as mathlib
   (`axiomatic_base.md`).

## When the verdict would be revisited

* If the Phase-2 bottleneck turns out to be *algebra-heavy* rather than
  analysis-heavy (unlikely: the Newton argument is analysis), Coq +
  MathComp re-enters consideration.
* If Sledgehammer-style external automation proves decisive for the
  spectral layer, an Isabelle side-formalization of auxiliary lemmas is
  acceptable — but never the main line (loses mathlib and the bridge).
