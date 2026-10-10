# Roadmap

- **C6 — the physical mapping. DONE (v1.1.0).**  The marked scale
  hypothesis (code-unit gap -> Hz through the QCD contact) is now a
  three-branch comparison: Lambda_QCD, the QCD crossover, and the
  electroweak scale, each with its own honesty note
  (`campaigns/run_c6.py`, `c6_verdict.json`).
- **C7 — anharmonic trio. DONE (v1.1.0).**  The softened Newtonian toy
  gained a confining-core potential (the linear Cornell-like term);
  the trap boundary V0*(Omega) SHRINKS by ~x7 as sigma goes 0 -> 0.02,
  and the free trio seals completely at sigma >= 0.05 — the first
  bridge toward QCD-like kinetics (`campaigns/run_c7.py`,
  `c7_verdict.json`).
- **C8 — the Wu door with pair-consuming kinetics. DONE (v1.1.0).**
  The linear mean field is replaced by pairwise annihilation; the door
  stays and the shape moves (the residual climbs past the linear
  alpha-limit toward the full imbalance; the T7 closed form is an
  exact structural negative — it does not extend)
  (`campaigns/run_c8.py`, `c8_verdict.json`).
- **C9 — the gap phase map. DONE (v1.2.0).**  The window law T3 is
  mapped over the whole searched (beta, q_pk) plane: no closure
  anywhere on the searched range (finite-range statement), the
  reproducible narrowing valley (beta* = 3.3583, reopens — quasi-energy
  band structure), and a machine-found counterexample to the naive
  quadratic extrapolation (`campaigns/run_c9.py`, `c9_verdict.json`).
- **C10 — the competing models. DONE (v1.2.0).**  The factorial sector
  ablation (the causal map A 91.95% / B 8.00% / C 0.049%, additive to
  1.3e-4), the exact braking-only invisibility, and the quantified
  out-of-window forecast failure (the quartic wing, residual power
  4.07) (`campaigns/run_c10.py`, `c10_verdict.json`).
- **C11 — the vortex anchor and the static barrier. DONE (v1.2.0).**
  The classical three-vortex layer (Kirchhoff 1876) implemented with
  the package's own code paths: T11 the stability contrast (the
  vortex triangle is NEUTRALLY stable where the Newtonian triangle is
  Gascheau-unstable — spectrum {0, 0, ±iω, ±iω}, symbolic charpoly
  dev 0), T12 the invariant wall (the Aref manifold bound without any
  wall), T13 the static barrier (escape EXACTLY impossible at
  V0 ≥ 1.6, Omega = 0; the oscillating seal is finite-time — the wall
  pumps energy) (`campaigns/run_c11.py`, `c11_verdict.json`).
- **Evidence Engine. DONE (v1.2.0).**  The claims registry
  (`results/claims_registry.json`, `results/CLAIMS.md`,
  `qhb/claims.py`): 27 claims, five statuses, five-field uncertainty
  budgets, pre-committed falsification criteria, build-pinned.
- **The independent audit IVP-11. DONE (v1.2.0).**  Three new hostile
  checks: the phase-map gate (fresh bisection), the competing-model
  gates (doubled Floquet resolution) and the vortex layer (SymPy
  charpoly dev 0, 50-digit Aref zeros) — 11/11 PASS.
- **Engine modernisation (open).**  Adaptive stepping at close
  encounters; the softened toy caps the slingshot — an AMR-style
  engine would sharpen the escape statistics the same way CHB's AMR
  goal attacks its mass floor.
- **Interactive delivery (open).**  The computational core is already
  pure functions; the download portal ships the package as-is, and an
  in-browser solver front-end remains the next step.
- **Adaptive experiment selection (open).**  The C9 valley locus is
  the natural seed for an adaptive refinement driver: spend the next
  CPU-hours where the uncertainty of the phase boundary is largest
  (the roadmap block C of the evidence program).
