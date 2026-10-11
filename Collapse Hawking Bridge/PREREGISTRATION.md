# Preregistration — falsification criteria committed BEFORE the next run

**Status:** committed at **v2.2.0**, before the next engine run
(the AMR engine upgrade, campaign C7). This file is the package's
answer to the single governance finding of the external audit:
*a criterion for refusing a hypothesis must be written down before the
data that could refuse it exist.*

**The rule this file installs**

> Every criterion below is frozen as of v2.2.0. A criterion may be
> changed only by a new CHANGELOG entry that says in its first line
> `RETRO-LABEL: criterion changed after data were seen` — and the
> previously committed verdicts keep the old criterion's name in their
> provenance. Silent retuning is a violation of the honesty discipline.

**Honest provenance of the frozen numbers.** The target
`Δ·γ = 1.27 ± 0.05` and the anchors `γ_Ch = 0.374`, `Δ_lit = 3.44 ± 0.02`
were introduced in v1.x **after** the anchor product `3.44 × 0.374 =
1.28656` was already known to sit 1.3% from 1.27 — the tolerance was
chosen with the answer in hand. That is why the anchor comparison was
reclassified at v2.2.0 as **anchor arithmetic** (a consistency statement
about the project's own constants, `ANCHOR_ARITHMETIC`), never a
physics test. From v2.2.0 the numbers below are frozen: they can no
longer be tuned to fit whatever the engine produces next.

---

## 0. What the anchor arithmetic is and is not

| object | class | what it can and cannot show |
|---|---|---|
| `P_anchor = 3.44 × 0.374 = 1.28656` | **ANCHOR_ARITHMETIC** | consistency of two project anchors with the frozen target; **not** evidence for the hypothesis |
| `P_mixed = Δ_eff(measured) × γ_Ch` | physics verdict (PASS / OUT-OF-TOLERANCE / INCONCLUSIVE) | a real test of the Δ side alone |
| `P_engine = Δ_eff(measured) × γ_eff(measured)` | physics verdict (PASS / OUT-OF-TOLERANCE / INCONCLUSIVE) | the only full physical test of the hypothesis |

No verdict file, README row, figure caption or monograph sentence may
present `P_anchor` as a passed measurement. The committed verdicts
carry the token `ANCHOR_ARITHMETIC` and a boolean
`P_anchor_within_target`; neither may be rendered as "PASS" anywhere.

## 1. Engine-level γ (campaign C7, AMR upgrade)

A γ measurement counts only if the instrument, not the floor, governs
the band:

- **Data requirements (all mandatory):**
  - the fit band spans ≥ 1.5 decades in ε **below** the floor:
    `floor_M(N) < 0.1 × M(ε_min)` for every fit row;
  - ≥ 8 sane fit rows, no junk rows in the fit set (junk stays committed
    verbatim, as everywhere);
  - ε measured from the **per-grid** `A*_N` (the F-2 lesson is permanent);
  - fit reported with `r²`, standard error, and the floor value.
- **Compatible (survives):** `|γ_eff − 0.374| ≤ 0.02` with `r² ≥ 0.99`.
- **Refuted (for this instrument/initial-data family):** the fit
  satisfies the data requirements but lands outside the band.
- **Still unmeasurable:** if any data requirement fails, the verdict is
  `INCONCLUSIVE` — the floor law statement of C3b stands and the
  engine-upgrade target remains open. An INCONCLUSIVE verdict is a
  result about resolution, not a failure of the protocol.

## 2. Engine-level Δ (echoes)

- **Data requirements:** ≥ 3 resolved echo peaks in ≥ 2 adjacent
  near-critical ε values of the same run family; peak detection by the
  committed prominence rule (`docs/methods.md`); `v*` taken as the
  apparent-horizon formation time; spacing measured in **log time**.
- **Compatible:** `Δ_eff = mean(log-spacings)` with
  `std/mean < 0.15` and `|Δ_eff − 3.44| ≤ 0.10`.
- **Refuted (effective-period sense):** requirements met but
  `Δ_eff` outside the band — the family's effective echoing period is
  not the Gundlach–Hodgson anchor.
- **Still unmeasurable:** fewer than 3 peaks → `INCONCLUSIVE` (the
  committed state up to N=3200).

## 3. The Δ·γ product

- `P_engine` (and `P_mixed`) are computed **only** from measured
  factors. Substituting an anchor for an unmeasured factor and calling
  the result a test is prohibited — that substitution is exactly what
  the audit rejected.
- **Compatible:** `|P_engine − 1.27| ≤ 0.05` (the frozen tolerance).
- **Refuted:** requirements of §1 AND §2 met, product outside the band.
- Any future change of `DGAMMA_TARGET`/`DGAMMA_TOL` in
  `chbridge/constants.py` is a RETRO-LABEL CHANGELOG event by the rule
  above.

## 4. The floor law

- Committed: `floor_M(N) ≈ (13 ± 1)/N` (C1 + C3b, per-grid floors).
- **Survives:** new grids (N = 6400/12800 or AMR-equivalent) give
  `c = floor_M(N)·N` inside `[10, 16]`.
- **Law revised:** `c` outside the band, or a measured local exponent
  `|p − 1| > 0.15` over ≥ 2 grid doublings. The revision is a result,
  not a defect — the floor law is an instrument statement.

## 5. The drift law T10

- The exact lemmas (κh²/8 worst-case flattening, chord < arc) are
  machine-verified identities — they cannot be refuted by new runs.
- **Pre-asymptotic narrative (the climbing `p_eff`):** if two
  consecutive grid doublings at N ≥ 6400 produce `p_eff` that *drops*
  (instead of climbing toward 2), the "pre-asymptotic transition"
  narrative is falsified as stated; T10 then survives only as the exact
  sub-dominant channel (its share stays measured and reported).
- **No `A*_inf`:** remains non-claimable unless a future ladder passes
  its own extrapolation stress test (the fitted-law `p_eff` trajectory
  must MATCH the measured one in sign of slope — the criterion that
  rejected the five-point two-term fit).

## 6. What does not count (permanent prohibitions)

1. Post-hoc tolerance or target changes without a RETRO-LABEL entry.
2. Replacing an unmeasured factor with an anchor inside a product that
   is then called a test.
3. Dropping junk rows from committed verdicts (they are results).
4. Reusing a coarse-grid threshold as the ε-origin of a deeper scan
   (the F-2 artifact mechanism).
5. Reporting console output as an artifact ("machine-readable or it
   did not happen" stays the package rule).

## 7. Sign-off

| item | value |
|---|---|
| Committed at | v2.2.0, before any C7/AMR run |
| Frozen constants | `DGAMMA_TARGET = 1.27`, `DGAMMA_TOL = 0.05`, `γ_Ch = 0.374`, `Δ_lit = 3.44 ± 0.02`, floor band `[10, 16]`·N⁻¹, Δ band `3.44 ± 0.10`, γ band `0.374 ± 0.02` |
| Change protocol | CHANGELOG first line `RETRO-LABEL: criterion changed after data were seen` |
| Machine pins | `tests/test_preregistration.py` (existence, frozen values, token discipline) |

The Russian mirror of this document: [PREREGISTRATION.ru.md](PREREGISTRATION.ru.md).
