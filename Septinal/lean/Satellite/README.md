# `Satellite/`

[Septinal/lean](../README.md) · 

Library III — **the septinial braking satellite**: the dial-22 postulate, the Berry quantum, the symmetry-breaking cascade and the UNLOCK block of exact parameter-free theorems. Root: [`../Satellite.lean`](../Satellite.lean) · build: `lake build Satellite` · audit: `lake env lean Satellite/AxiomAudit.lean`.

## Files

| Module | Lines | Declarations |
|---|--:|---|
| [`AxiomAudit.lean`](AxiomAudit.lean) | 71 | 0 (—) |
| [`B1_BerryShift.lean`](B1_BerryShift.lean) | 94 | 10 (7 theorem · 3 def) |
| [`B2_Dial22.lean`](B2_Dial22.lean) | 55 | 12 (8 theorem · 4 def) |
| [`B2b_Chirality.lean`](B2b_Chirality.lean) | 80 | 14 (10 theorem · 4 def) |
| [`C2_Corrections.lean`](C2_Corrections.lean) | 90 | 14 (9 theorem · 5 def) |
| [`C3_Cascade.lean`](C3_Cascade.lean) | 127 | 16 (12 theorem · 4 def) |
| [`C4_Unlock.lean`](C4_Unlock.lean) | 96 | 10 (8 theorem · 2 def) |
| [`C5_Klein.lean`](C5_Klein.lean) | 63 | 10 (10 theorem) |

**Headline theorems.**
- [`Unlock.gamma_exact`](../Satellite/C4_Unlock.lean)
- [`Unlock.k_exact`](../Satellite/C4_Unlock.lean)
- [`Unlock.quanta`](../Satellite/C4_Unlock.lean) — - Physical admissibility of the Berry quantum.
- [`Dial.card_dial`](../Satellite/B2_Dial22.lean)
- [`Cascade.exactly_two_rotations`](../Satellite/C3_Cascade.lean)
- [`Berry.remainder_le`](../Satellite/B1_BerryShift.lean)

## Build

```bash
`lake build Satellite`
```

---

Back to the package: [Septinal/lean README](../README.md)
