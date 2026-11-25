# `SeptinalYM/`

[Septinal/lean](../README.md) · 

Library II — **the septinal mass-gap programme**: from the 22-slot ring data (`Basic`) through the Jordan–Wigner reduction (`JW`) to the proved gap (`Gap`), the exact diagonalisation chain (`Slater → SlaterDiag → Stage4c → Stage4d`), and the isometric embedding into a Yang–Mills state space (`YMTarget`). Build: `lake build SeptinalYM SeptinalYM.Stage4d`.

## Files

| Module | Lines | Declarations |
|---|--:|---|
| [`Basic.lean`](Basic.lean) | 135 | 13 (6 theorem · 5 def · 2 abbrev) |
| [`Fourier.lean`](Fourier.lean) | 194 | 17 (14 theorem · 3 def) |
| [`Gap.lean`](Gap.lean) | 250 | 11 (10 theorem · 1 def) |
| [`JW.lean`](JW.lean) | 795 | 59 (48 theorem · 11 def) |
| [`JW_twist_addendum.lean`](JW_twist_addendum.lean) | 69 | 4 (3 theorem · 1 def) |
| [`MatrixAux.lean`](MatrixAux.lean) | 376 | 42 (30 theorem · 10 def · 2 abbrev) |
| [`Numeric.lean`](Numeric.lean) | 350 | 15 (15 theorem) |
| [`Ortho.lean`](Ortho.lean) | 257 | 9 (9 theorem) |
| [`Sector.lean`](Sector.lean) | 175 | 11 (11 theorem) |
| [`SeptinalYM_Slater.lean`](SeptinalYM_Slater.lean) | 343 | 13 (8 theorem · 5 def) |
| [`Slater.lean`](Slater.lean) | 343 | 13 (8 theorem · 5 def) |
| [`SlaterDiag.lean`](SlaterDiag.lean) | 1591 | 61 (54 theorem · 7 def) |
| [`SlaterDiag_v1.lean`](SlaterDiag_v1.lean) | 2039 | 82 (72 theorem · 10 def) |
| [`Stage4c.lean`](Stage4c.lean) | 126 | 9 (9 theorem) |
| [`Stage4d.lean`](Stage4d.lean) | 2710 | 98 (92 theorem · 6 def) |
| [`YMTarget.lean`](YMTarget.lean) | 84 | 7 (4 theorem · 2 def · 1 structure) |

**Headline theorems.**
- [`septinal_gap`](../SeptinalYM/Gap.lean)
- [`septinal_gap_jw_via_sectors`](../SeptinalYM/Gap.lean)
- [`cSept_eq_two_abs_cos`](../SeptinalYM/SeptinalYM_Slater.lean)
- [`slater_diag_odd`](../SeptinalYM/SlaterDiag_v1.lean)
- [`slater_diag_even_twist`](../SeptinalYM/SlaterDiag_v1.lean)
- [`slater_orth`](../SeptinalYM/SlaterDiag_v1.lean)
- [`septinal_embeds_in_ym`](../SeptinalYM/YMTarget.lean) — - Носитель: комплексное нормированное пространство состояний.
- [`septinal_gap_transports`](../SeptinalYM/YMTarget.lean)

## Build

```bash
`lake build SeptinalYM SeptinalYM.Stage4d`
```

---

Back to the package: [Septinal/lean README](../README.md)
