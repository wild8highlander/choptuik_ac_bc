# IVP-11 — the independent verification protocol

The package carries its own hostile audit.  The source of truth of the
protocol lies OUTSIDE the committed results: fresh interpreters, its own
50-digit code paths, symbolic algebra, dimension gates and hash
stability.  Eleven checks (the v1.2.0 additions are IVP09–IVP11):

| IVP | check | source of truth |
|---|---|---|
| IVP01 | release integrity | existence + sha256 of the committed verdicts |
| IVP02 | canonical job | a fresh interpreter recomputes the canonical gap block from scratch and must match the verdict exactly |
| IVP03 | dependency audit | ast-scan of every import vs the declared dependency set |
| IVP04 | 50-digit rederivation | own mpmath code paths for every closed-form constant |
| IVP05 | dimensions audit | SI-size gates on the contacts and thermodynamics |
| IVP06 | symbolic layer | SymPy: the Gascheau characteristic equation + Lemma A in exact rationals |
| IVP07 | convergence orders | the committed p_eff ladders must climb to 2 |
| IVP08 | seed determinism | the MC cell bit-identical across runs |
| IVP09 | the phase-map gate | fresh map cells above the 2/N floor + an independent valley bisection matching the committed beta* |
| IVP10 | the competing-model gates | doubled Floquet resolution: the braking-only zero, the C-spectator bound, the evenness machine zeros |
| IVP11 | the vortex layer | SymPy: the exact charpoly lambda^2(lambda^2+omega^2)^2; mpmath: the Aref invariants are machine zeros; the numeric eigenvalue gate |

Run everything:

```bash
bash independent_verification/RUN_ALL.sh
```

Verdicts are written to `results/IVP0X.json`; the prose report is
`RESULTS.md`.
