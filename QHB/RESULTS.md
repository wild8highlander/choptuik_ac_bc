# QHB v1.3.0 — Results / Результаты (EN)

Consolidated results registry. Claim ids match `data/claims.json`.

| ID | Status | Result |
|----|--------|--------|
| T1 | exact | Finite-volume gap positive over the whole explored region; threshold 0.0363485 |
| T2 | measured-law | Wilson law exact in the model class; sigma(beta) = 0.25 (Delta/Delta_min)^1.5 |
| T3 | exact | Spin corrections pi^2/8, pi^5/704 verified at 100 digits |
| T4 | measured-law | Bridge temperature correction +11.28% at beta* |
| T5 | honest-negative | Detector tail beyond E_max = 2.5 unresolved; amplitude bound only |
| T6 | honest-negative | Free three-body escape P_esc = 0.2433 ± 0.0043 |
| T7 | exact | Y-string vertex is the Fermat point (120 degrees, SymPy) |
| T8 | measured-law | Y-string spectrum minimized by the equilateral shape |
| T9 | measured-law | Tunneling window closed: T(0) = 9.21e-13; open only for E < 0.0059 |
| T10 | measured-law | Bootstrap bias 0.0046 (0.38 boot_se); jackknife 0.0016 |
| T11 | exact | Vortex spectrum {0, 0, ±iω, ±iω}; charpoly λ²(4π²λ²+9)²/(16π⁴) |
| T12 | measured-law | Aref boundedness r_max = 2.7654 < 2√I; rotation dev 2.3e-15 |
| T13 | measured-law | Static barrier V* = 0.9359375; 0/300 escapes |
| T14 | exact | Asymmetry lock: eta_crit = 0.0908885 = Delta_F,min/2; worst loss exactly 2 eta |
| T15 | honest-negative | No free quarks: 0 saturated wells at eta_B; nugget bound < 10^(−1.2e31) |
| C1-RES | measured-law | C1 9×9 grid all OPEN; min 0.174490 at (3.45625, 6) |
| C1-NEG | honest-negative | Continuum gap Delta_cont NOT claimed (finite-volume only) |
| C4-NEG | honest-negative | Tail shape not established; upper bound only |
| C9-VALLEY | measured-law | Valley floor (3.3583, 0.181777) by parabolic refinement |
| C9-FALS | honest-negative | Naive closure at beta_c = 2.9910 falsified: measured 6.3x threshold |
| C9-ALL | measured-law | 9×41 phase map: all 369 cells OPEN (finite-range statement) |
| C10-SHARES | measured-law | Causal shares 91.95 / 8.00 / 0.049 %; additivity bias 1.3e-4 |
| C10-B2 | exact | Pure-braking control B2 = 0 exactly (even sector annihilated) |
| C10-NEG | honest-negative | Out-of-window invalid; residual power 4.071 |
| C12-GRID | measured-law | eta-map OPEN for all eta < 0.0908885; boundary exact |
| C12-FILL | honest-negative | Cascade only at eta = 0.5; zero at eta_B |
| C12-EXP | comparison | Nugget searches: n < ~1e-27 per nucleon; model predicts zero |
| HYPO-CONT | hypothesis | Continuum gap exists — hypothesis, never asserted |
| AUDIT | exact | IVP-12: 12/12 PASS (symbolic + 100-digit + quadrature) |
| DETERM | honest-negative | No nondeterminism: byte-identical rebuild |

## Status ledger

- **exact** — SymPy/mpmath symbolic or 100-digit verified.
- **measured-law** — measured inside the pinned model class; interpolation outside
  the window is not claimed.
- **honest-negative** — the negative statement itself is the result.
- **hypothesis** — stated, never asserted.
- **comparison** — external literature value; not evidence for the model.


## v2.3.0 — the Mathlib / iron-layer edition (appendix A, chapters 14–17 unchanged)

- T19 ported into Mathlib: 8 new closed kernels (block charpolys via
  `Matrix.charpoly`, factorization via `charpoly_fromBlocks_zero₂₁`); the axiom
  audit covers 18 closed kernels and CI fails on any `sorryAx`.
- Erratum: T20.stall monotonicity sign fixed (τ_max strictly decreases in T);
  T20.deadline closed; T3 honestly downgraded to data-anchored.
- External bounds X1–X8 → X1–X13 (SQM-ISS, IceCube monopoles, KM3NeT, macro
  recast, CTAO/HESS J1731-347); AMS-02 note recorded on X8.
- Iron layer: Iron-QA gates, four CI workflows, animated READMEs, landing page,
  SHA256SUMS, git bundle; monographs 63/61 PDF pages.
