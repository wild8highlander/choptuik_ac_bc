# tests — the pin suite

Every committed number of the package is pinned here.  Run:

```bash
python3 -m pytest tests/ -q
```

| file | pins |
|---|---|
| `test_constants.py` | exact identities (correction quanta, b_Ch, Page fraction), the QCD/CMB contacts |
| `test_gap.py` | static chain block, b=0 Floquet identity, quadratic law on the committed window, T2 evenness/zero checks, per-sector hierarchy |
| `test_trio.py` | Gascheau verdict, wall shape, growth rate |
| `test_wu.py` | closed-form limits, anchor value, MC agreement |
| `test_bridge.py` | master-table geometry (15 x 23), both contacts, ladder shapes |
| `test_campaigns.py` | pin-verdicts: every headline number of C1–C5 against the committed JSON |
| `test_engine.py` | Kepler validation anchor, energy drift, ensemble determinism |
| `test_validate.py` | the 9/9 mpmath layer |
| `test_data.py` | byte-determinism of `scripts/rebuild_data.py` |


## v1.1.0 pins (C6-C8)

- `TestC6`: three branches present; the QCD contact matches T8
  (6.8140e10 kg); the order window 4.09; all four gates PASS; the
  per-branch honesty tags carried.
- `TestC7`: the regression gate dev 0.0 exactly; the free ladder
  monotone with sigma* = 0.05; the V0* boundary shrinks (>= x2 at
  every Omega); bound chaos without the wall (median > 0.1, share
  positive > 0.99).
- `TestC8`: the bitwise no-door check (r = 0.0); the RK4 order pinned
  (|p_eff - 4| < 0.05); the 50-digit cross-check (dev < 1e-9); the
  door stays and the shape moves (r_pair(lambda=100, alpha=0.9) >
  0.95); the T7-extension verdict carries NEGATIVE.

## v1.2.0 pins (C9-C11 + the vortex layer + the registry)

- `test_campaigns_v12.py` — 22 pins: every headline number of C9
  (the no-closure minimum, the valley, the refinement/N gates, the
  counterexample ratio), C10 (the causal shares, the exact braking
  zero, the evenness, the additivity, the forecast failure and the
  quartic residual power), C11 (the T11 spectrum and charpoly, the
  rigid rotation, the Aref manifold, the T13 V* threshold, the static
  cells, the oscillating complement).
- `test_vortex_claims.py` — the vortex-layer units (the exact omega,
  the equilateral separations, the Aref machine zeros, the exact
  linearization spectrum, the short-run invariant drifts) and the
  Evidence Engine registry (the schema, the validation, the status
  coverage, the uncertainty budgets, the honest-negative inventory).
- the twins' pins move 13/13 → 14/14 (the vortex Lagrange rate joins
  the block).
