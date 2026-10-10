# The Evidence Engine — the claims registry

The register of every load-bearing statement of the package at
**v1.2.0**, with its status marker, its verdict address, its
uncertainty budget and its pre-committed falsification criterion.
Machine source of truth: [claims_registry.json](claims_registry.json);
validator: `python3 -m qhb.claims`; build pin:
`tests/test_vortex_claims.py`.

The registry exists so that a **proof, a measurement, a comparison and
a hypothesis can never be silently mixed**.  Quoting a claim obliges
carrying its status and verdict address (the honesty discipline, part
of the LICENSE).

## Statuses

| status | meaning |
|---|---|
| `exact` | an exact fact of the committed model (machine and/or symbolic) |
| `measured-law` | a committed deterministic/seeded measurement treated as a law of the toy model |
| `honest-negative` | a negative result carried in the headline |
| `hypothesis` | a marked hypothesis (never a derivation) |
| `comparison` | a literature comparison, never a fit target |

## The registry at a glance (27 claims)

| id | status | one-line statement | verdict |
|---|---|---|---|
| CLM-01 | exact | the static gap `Delta_0 = 0.523004556028` | c1_verdict.json |
| CLM-02 | measured-law | the gap law `B2 = -5.49670294e-2`, r² = 0.99999982 (window [0, 0.2]) | c1_verdict.json |
| CLM-03 | measured-law | the sector hierarchy ~1865 : 1 | c1_verdict.json |
| CLM-04 | exact | T2 selection rules (machine zeros + the ab-cross data) | c1_verdict.json |
| CLM-05 | exact | T4 Gascheau: the Newtonian triangle is unstable | c2_verdict.json |
| CLM-06 | honest-negative | T5 the free trio unbinds (P_esc = 0.2433) | c2_verdict.json |
| CLM-07 | measured-law | T6 the oscillating wall seals; bound chaos | c2_verdict.json |
| CLM-08 | measured-law | T7 the Wu door closed form vs MC; the anchor 0.9 | c3_verdict.json |
| CLM-09 | honest-negative | the door's honest scale (x = 1.36e-9 for eta) | c3_verdict.json |
| CLM-10 | comparison | the QCD contact 6.8140e10 kg (0.68 × literature) | qhb/bridge.py |
| CLM-11 | honest-negative | the unresolved detector tail (beats 1.53 < 3) | c4_verdict.json |
| CLM-12 | measured-law | T10 the drift law C = +3.0089e-2, share −0.209 | c5_verdict.json |
| CLM-13 | honest-negative | `Delta_cont` NOT claimed | c5_verdict.json |
| CLM-14 | comparison | C6 the mapped gap quantum 81.1 MeV (ratio 4.09) | c6_verdict.json |
| CLM-15 | measured-law | C7 the regression gate 0.0; the flux tube seals | c7_verdict.json |
| CLM-16 | honest-negative | C8 the T7 form does not extend; the shape moves | c8_verdict.json |
| CLM-17 | measured-law | **C9 no closure on the whole searched map** (min 0.1244) | c9_verdict.json |
| CLM-18 | measured-law | **C9 the narrowing valley** (beta* = 3.3583, reproducible) | c9_verdict.json |
| CLM-19 | honest-negative | **C9 the naive-window counterexample** (6.3 × floor at beta_c) | c9_verdict.json |
| CLM-20 | measured-law | **C10 the causal map** (A 91.95 / B 8.00 / C 0.049%, additive) | c10_verdict.json |
| CLM-21 | honest-negative | **C10 the out-of-window forecast failure** (quartic wing, p = 4.07) | c10_verdict.json |
| CLM-22 | exact | **T13 the static barrier** (V* = 0.9359375; escape impossible) | c11_verdict.json |
| CLM-23 | measured-law | **T13 complement: the oscillating wall pumps energy** (finite-time seal) | c11_verdict.json |
| CLM-24 | exact | **T11 the stability contrast** ({0, 0, ±iω, ±iω}; charpoly dev 0) | c11_verdict.json |
| CLM-25 | measured-law | **T11 the rigid rotation** (1.5e-14 rigidity, ω dev 1.6e-14) | c11_verdict.json |
| CLM-26 | measured-law | **T12 the invariant wall** (Aref manifold bound without walls) | c11_verdict.json |
| CLM-27 | hypothesis | **THE CONFINEMENT MECHANISM IS A MARKED HYPOTHESIS** | README.md |

## The uncertainty budget

Every claim carries five explicit fields — `statistical`,
`discretization`, `solver`, `parameter`, `model` — each either a value
or an explicit `null` (a null is a claim that the component is ABSENT,
never that it is unknown).  The rule the registry enforces: **a
conclusion can never be marked exact because one error component is
zero** — the model-uncertainty field of every toy-model fact points at
the toy itself.

## Falsification discipline

Every claim names, in advance, the machine-checkable observation that
would force the package to retract it.  New campaigns update statuses
automatically in the sense that a failing gate must either change the
status of the claim it addresses or carry an honest negative of its
own.
