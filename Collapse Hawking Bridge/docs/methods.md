# Methods — how every number of the project is produced

Nothing in this repository is asserted that cannot be re-run.  This
document is the computational counterpart of `docs/theory.md`: the
discretisation, the protocols, the filters, and the honesty rules.

---

## 1. The double-null engine (`engine/solver.py`)

**Formulation.** Spherical Einstein-scalar system in double-null
coordinates `ds^2 = -alpha(u,v)^2 du dv + r(u,v)^2 dOmega^2`, with
`omega = ln(alpha)` and the Misner-Sharp mass
`m = (r/2)(1 + 4 r_u r_v / alpha^2)`:

```text
(SC)  Phi_uv = -(r_u Phi_v + r_v Phi_u) / r
(UV)  r_uv   = -(r_u r_v + alpha^2/4) / r
(C1)  r_uu   = 2 omega_u r_u - (kappa/2) r Phi_u^2
(C2)  r_vv   = 2 omega_v r_v - (kappa/2) r Phi_v^2
(TH)  omega_uv = alpha^2 m / (2 r^3) - (kappa/2) Phi_u Phi_v
```

The system is closed by regularity identities that make the march
well-defined down to the centre `r = 0`:
`(r^2)_uv = -alpha^2/2`, `P_v = -alpha^2/4` with `P = r r_u`, and the
Misner-Sharp transport identities for `m_u, m_v`.

**Units.** `4 pi G = 1`, i.e. `kappa = 8 pi G = 2` (Burko normalisation).
All campaign data stay in these code units; physical mapping happens
downstream in `chbridge` only.

**Integration.** Characteristic march over `v`-rows (Goursat problem),
second-order Heun predictor-corrector with a half-step predictor,
vectorised over `u` with NumPy.  Constraints are monitored on every row:
Hamiltonian `c1`, momentum `c2`, and the mass-definition identity
`mdef`; their running maxima are part of every verdict.

**Horizon finding.** The compactness `q = r_v`; capture when `q`
vanishes from above (`q < 0`); the apparent-horizon mass is `m` at the
`q = 0` point (there `m = r/2`).  On saturation (mass beyond the pulse
total) the run stops with the honest `AH mass saturated` reason.

## 2. Validation protocol

The exact Roberts (1989) solution with `sigma = 0.1`, smooth band
`u in (-0.3, 0.7)`, `v in (1, 2)`, is the regression target.  Three
grids (N = 200/400/800) must show clean second-order convergence of
`max|r - r_exact|`; the measured orders are committed to the verdict
(2.03 and 2.09 at v1.0.0).  `tests/test_engine.py` re-runs the N=200
regression on every `pytest` invocation.

## 3. Critical amplitude: bisection and the grid-honesty ladder

`A*` is bracketed between a subcritical and a supercritical run and
bisected to tolerance.  Crucially, the bisection is repeated at
N = 200/400/800 and **all three values are committed**:

```text
A*_200 = 0.1051048278808594
A*_400 = 0.0882011413574219
A*_800 = 0.08053436279296877
A*_1600 = 0.0777437257766724     (remediated ladder, v2.0.1, F-1)
A*_3200 = 0.07682116031646731
```

The threshold DRIFTS with resolution and is not converged at N=3200
(`2.79e-3` from N=800 to N=1600) — the stale 2.0.0 claim of a `1.06e-6`
agreement with a `0.0805333` reference was an audit finding (F-1/IVP-09)
and is retracted. The drift between grids *is the floor statement in
disguise*: a fixed grid cannot resolve the critical point to better
than its own scale.  This is why the ladder, not a single number, is
the committed result.

## 4. Amplitude scans, sane filter, mass floor

Scans run over `eps = A - A*` on a log ladder (~3 decades at N=400,
2.5 decades at N=800).  A row is **sane** iff the run found a horizon,
the mass is finite and `0 < M_code < 0.1` (the family's total mass
scale).  Rows outside this window are junk (numerical overflow) and are
*kept and flagged*, never dropped: the committed verdict contains the
junk examples verbatim.  The smallest sane resolved mass at N=800 is
`1.55e-2` code units — the fixed-grid mass floor.

## 5. Measuring gamma: protocol and floor

The supercritical spectrum is fitted as `log10 M = log10 C + gamma
log10 eps` over sane, non-junk rows with `eps < 3e-2`.  At committed
resolution the fit comes out **flat** (`gamma_eff = 0.005 +- 0.035`,
`r^2 = 0.003` at N=800): the floor dominates the smallest masses and
the saturation cap the largest, and between them the mass varies by
~30% while `eps` varies by 3 decades.  The honest statement — *gamma is
not percent-measurable at fixed grid* — is itself the committed result
(`gamma_campaign: null` in constants, with the verdict carrying the
full fit row set).  The literature anchor `gamma_Ch = 0.374` is used
for comparison only.

## 6. Measuring Delta: the log-time echo detector

DSS predicts echo peaks at `v* - v_k = C exp(-k Delta)`; the estimator
is the spacing of `x_k = ln(v* - v_k)` between successive local maxima
of the compactness proxy `q(v) = max_r(2m/r)`, recorded every row
(`monitor_every = 1`).  The accumulation time `v*` is proxied by the
apparent-horizon formation time `v_ah` of the same run.  At v1.0.0 the
detector resolves **fewer than three peaks per run** — fewer than the
minimum for an estimate — so `Delta_eff` is committed as *not
measurable* at fixed grid, with per-run peak tables in
`campaigns/reference/c3_verdict.json`.  The anchor `Delta = 3.44 +-
0.02` (Gundlach-Hodgson; engine-family data) is used for comparison
only.

## 7. Campaign C2: the two branches (v1.1.0)

C1 locates the threshold; C2 measures what happens on both sides of
it, at N=800 with the committed `A*_800`:

- **Branch S (subcritical, `A = A*_800 - eps`, eps in [10^-1.2,
  10^-4.2]; the upper bound keeps `A > 0`, so the pulse family is the
  same — negative-amplitude runs are excluded by construction).**
  Per run: `q_max = max(2m/r)` over 40 engine snapshots, the snapshot
  time of that peak (`v_qmax`), the count of local maxima of `q(v)`
  (echo counter), and the residual compactness `q_final/q_max`.
  Fitted: the critical slowdown `v_qmax = a + b ln(eps)` (DSS
  logarithmic approach; committed `b = -0.0334, r^2 = 0.714`) and the
  echo accumulation rate `dN_peaks/dln(1/eps)` (committed `0.1909`,
  compared with the anchor `1/Delta = 0.2907`, never fitted to it).
- **Branch X (supercritical, `A = A*_800 + eps`, eps in [10^-0.5,
  10^-4.0]).**  Per run: `M_code`, then `f~ = M/M_sat` with `M_sat =
  max sane M` of THIS scan (committed `0.03518979`).  Summarised by
  `eps_half = 4.8598e-3`, the log-eps interpolation of the `f~ = 0.5`
  crossing — a floor-robust width indicator.  The exponent fit is
  deliberately NOT repeated: it is C3's committed measurement.
- A subcritical run that forms an apparent horizon is kept verbatim
  with `flipped = true`; at the committed range there are zero flips
  (the mechanism was exercised and is tested by the flag's plumbing).

Outputs: `c2_verdict.json`, `subcritical_scan.csv`,
`bifurcation_ftilde.csv`; derived tables in `data/bridge/` copy the
verdict rows verbatim.

## 8. Campaign C3b: concentrated resolution (v1.1.0)

The honest definition of "adaptive" in this project: the engine is
NOT rewritten; resolution is CONCENTRATED on the critical window.
Deep grids (N = 1600, 3200) are spent on (a) a narrow supercritical
eps band around each grid's OWN threshold `A*_N` (v2.0.1 F-2
remediation: the 2.0.0 release based the deep grids on `A*_800`,
mislabeling eps by +2.8e-3 at N=1600) and (b) echo runs nearest
threshold.  The motivating probe: the mass floor DROPS with
resolution, so C3's "gamma unmeasurable" is a floor statement, and
the floor is a knob.

- **gamma ladder:** log-log fit per grid over the narrow band;
  committed (v2.0.1) `0.0410 +- 0.0262` (N=1600, r²=0.33) and
  `0.0605 +- 0.0417` (N=3200, r²=0.41).  The fits are floor-dominated
  and honestly weak — the anchor 0.374 is NOT approached within reach
  of this instrument.  (The 2.0.0 values `0.1113 / 0.1205` with r²
  0.82/0.96 were artifacts of the mislabeled eps axis; retracted.)
- **floor ladder (the first-class result):** smallest resolved mass
  per grid, `0.0155 (N=800) > 8.574765e-3 (N=1600) > 4.244867e-3
  (N=3200)`.
- **delta ladder:** the C3 echo detector re-run at depth; 1-2 peaks
  per run — no run resolves >= 3 peaks, `delta_eff` stays null, and
  `P_engine_deep = null` is committed with reason strings.

## 9. Page-curve construction

For each input scale and member the model integrates `dM/dt = -P_H`
in the photon-only approximation analytically, giving
`M(t) = M0 (1 - t/t_evap)^{1/3}` and `S_BH(t) = S0 (1 - t/t_evap)^{2/3}`
(`S0 = S_BH(M0)/k_B`).  The radiation entropy is
`S_rad = min(S_BH, S0 - S_BH)` — equivalently the two-branch rule of
`docs/theory.md` — with the kink at the Page time, where both branches
equal `S0/2` exactly (`tests/test_page.py::test_curve_structure`).

## 10. Haar averaging check

The exact Page/Sen averaged-entropy formula for dimensions `m <= n`,

```text
S(m, n) = ( sum_{k=n+1}^{mn} 1/k  -  (m-1)/(2n) ) / ln 2 ,
```

is verified against Haar-random pure states on `C^{2^N}` (seeded
`default_rng(20260101)`, 3000 samples per partition, `N <= 6`;
1200 for `N = 7`): 18 partitions, maximum deviation `0.0042 bits`
(committed in `data/bridge/page_haar_check.csv`).

## 11. The 50-digit verification layer (`chbridge/validate.py`)

Every closed-form constant is recomputed in 50-digit `mpmath`
arithmetic and compared to the float values shipped in `constants.py`:
identities (`b_Ch`, `PAGE_FRACTION`), power laws, the CMB contact
round-trip, Planck-unit cross-consistency, the `Delta*gamma` anchor
product, and the Kretschmann scale law.  `7/7 PASS` is required by
`tests/test_ladder.py::test_validate_all_pass`.

## 12. Determinism and reproducibility

- `scripts/rebuild_data.py` is a pure function of the committed
  verdicts; `tests/test_bridge.py::test_rebuild_determinism` re-runs it
  twice into temporary directories and compares bytes.
- Monte-Carlo is seeded; seeds are committed next to the code that
  consumes them.
- Every campaign verdict records wall-time, engine string, family
  geometry, units and the project version — a verdict is a
  self-describing artifact.

## 13. Known limitations (v1.1.0)

- Fixed grid: the mass floor and the saturated-stop band bracket the
  resolvable spectrum.  C3b measured the floor law (`floor_M ~ 12/N`)
  and confirmed both engine-level negatives at N=1600/3200; true AMR
  (refinement near the accumulation point) remains the roadmap path
  to an engine-level gamma.
- Photon-only evaporation: greybody factors and species thresholds
  (electron, muon, pion...) are out of scope; lifetimes are lower
  bounds in the idealised sense.
- The echo detector is a peak-spacing estimator, not a matched-filter
  DSS analysis; it under-counts echoes at moderate resolution, and 40
  snapshots per run bound the countable peaks at every committed depth.
- C2's slowdown/echo fits are measured on the dispersing side of a
  fixed grid; they demonstrate the logarithmic approach but are not
  precision determinations of the DSS constants.
