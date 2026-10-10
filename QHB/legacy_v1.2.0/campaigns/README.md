# campaigns — measurements, not simulations

![v1.2.0](https://img.shields.io/badge/version-1.2.0-8C6D1F) ![C1](https://img.shields.io/badge/C1-gap_law_T2%2FT3-blue) ![C2](https://img.shields.io/badge/C2-trap_T4--T6-blue) ![C3](https://img.shields.io/badge/C3-Wu_door_T7-blue) ![C4](https://img.shields.io/badge/C4-floor_T9-blue) ![C5](https://img.shields.io/badge/C5-drift_T10-C9A84C) ![C9](https://img.shields.io/badge/C9-phase_map-C9A84C) ![C10](https://img.shields.io/badge/C10-competing_models-C9A84C) ![C11](https://img.shields.io/badge/C11-vortex_barrier-C9A84C)

**TL;DR**

- A campaign is a measurement protocol: a script drives the engine
  through a committed ladder and writes a self-describing JSON verdict.
  Console output is a courtesy; the verdict is the law.
- **C1** — the gap law: static block, rigid-trio scan, per-sector
  scans, T2 evenness/zero checks, M-convergence (~1 s).
- **C2** — the trap: Gascheau verdict, escape grid 9x4, V0* boundary,
  Lyapunov free vs trapped (~3.5 min).
- **C3** — the Wu door: 6x5 residual grid at 200k MC per cell,
  anchor arithmetic, eta comparison (~1 s).
- **C4** — the floor law: period-sampled Floquet spectroscopy over
  T_sim in {20..320}, envelope 2/N, honest negatives (~1 s).
- **C5** — the drift law: N-ladder 32..512, p_eff, exact-channel
  share, Lemma A machine check (~1 s).

- **C9** — the gap phase map: the 9x41 (q_pk, beta) grid against the
  2/N detector floor, the narrowing-valley bisections, the naive-window
  counterexample, the gates P1–P4 (~11 s).
- **C10** — the competing models: the 8-configuration factorial sector
  ablation, the additivity gate, the out-of-window forecast ladder (~4 s).
- **C11** — the vortex anchor and the static barrier: the classical
  Kirchhoff layer (rigid rotation, the exact linearization spectrum,
  the Aref manifold) and the committed-engine barrier cells with the
  exact radius bound (~35 s).

Runbook:

```bash
make c1 c2 c3 c4 c5 c6 c7 c8 c9 c10 c11              # fresh verdicts
make data                                            # rebuild data/qhb
make claims                                          # validate the registry
```

All verdicts live in `reference/` and are committed; the package works
offline from them without any recomputation.


## v1.1.0 — the roadmap block

| campaign | script | wall time | verdict | the one-line result |
|---|---|---|---|---|
| C6 | `run_c6.py` | ~1 s | `reference/c6_verdict.json` | three-branch mapping; E_gap(QCD) = 81.1 MeV; round trip 1.4e-16 |
| C7 | `run_c7.py` | ~5 min | `reference/c7_verdict.json` | sigma-gate dev 0.0; P_esc 0.2433 -> 0.0033; V0* shrinks x7.1/x7.6; bound chaos 0.264 |
| C8 | `run_c8.py` | ~10 s | `reference/c8_verdict.json` | r(alpha=0) = 0.0 bitwise; p_eff 3.987; mpmath 3.9e-16; door -> 0.988 (shape moves) |

Honest negatives of the block: the T7 closed form does NOT extend to
pairwise kinetics (C8, exact structural negative); the anharmonic runs
carry an engine-level hypothesis mark (the Kepler anchor validates the
engine only at sigma = 0, C7); the Lambda_QCD branch is a renorma-
lisation scale and the electroweak branch a VEV — neither is a
temperature (C6).
