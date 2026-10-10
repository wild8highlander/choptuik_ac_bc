# Roadmap

## Executed (v2.1.0, chapter 14)
- **R1 — continuum stress**: ladder L = 4…10^6; order p = 0.99998; residual 2e-16.
- **R2 — anisotropic vortices**: branch laws nu_tr = (2+gamma)/2pi, nu_int = sqrt(3(1+2gamma))/2pi
  (dev 5e-9); Re = 0 (same-sign); Synge threshold 0.5.
- **R3 — thermal lock**: eta_crit(T) linear; T_death(10^12) = 0.003414 = T_c/25.9.
- **R4 — tail shape**: negative T5 invulnerable; f_crit = 0.1929.
- **R5 — external comparison**: table X1–X8 (comparison status).
- **R6 — Lean 4**: Section 7 (T16–T18); closed kernels 2 -> 7.
- **R7 — twins**: JS/C/C++ 14/14 PASS byte-for-byte; Go/Rust/Julia static audit.

## Executed (v2.2.0, chapters 15–17)
- **Analytic proof of the R2 branch laws (T19)**: chi(C0) factorization dev 0.0;
  lab spectrum chi(J0); circulation dispersion law (50 digits, dev 1.5e-16);
  Jordan block at the zero pair; Synge as a sign corollary.
- **Cosmological cooling below T_death**: deadline 673·t_c (alpha = 1/2);
  closed-form survival integral with hot dominance (78.5%); dynamic deadline
  t_lim = 4.04e-11 (N-independent); stall cliff across 22 orders; race MC <= 1.2 sigma.
- **Five convergence ladders to infinity**: time (1/T), step (p = 4.0956),
  volume (three-rung continuum 0–5.6e-17), budget (1/ln N), sample (n^-1/2).

## Executed (v2.3.0, appendix A + the iron layer)
- **Full T19 port into Mathlib**: 8 closed kernels over Matrix.charpoly +
  charpoly_fromBlocks_zero₂₁; axiom audit across 18 closed kernels; Lean/Mathlib CI.
- **Erratum T20.stall**: stall-cliff monotonicity sign fixed and kernel closed;
  T20.deadline closed; T3 downgraded to data-anchored (honest status policy).
- **External bounds X1–X8 -> X1–X13** with 2024–2026 primary-source verification.
- **Iron-QA layer**: four static gates + CI workflows + SHA256SUMS + git bundle;
  animated READMEs (EN/RU), landing page, social preview.

## Next candidates (not started, no promises)
- Executable verification of Go/Rust/Julia once a toolchain is available.
- Closing the standard-basis similarity anchor (lemma B/C) as a Lean kernel.
- New X-rows as publications appear.

## Falsification-first policy
Any roadmap item starts from the falsifier of the corresponding claim, not
from the confirmation.
