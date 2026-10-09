# The scaling law: why one formula gives different values at different scales

**The resolution-drift theory of the fixed-grid threshold (theorem T10).**

Status: **analytically derived** (two exact lemmas, machine-verified) +
**numerically established** (channel magnitudes measured on committed
artifacts). Verdict of record:
`campaigns/reference/c6_drift_verdict.json` (campaign C6, v2.1.0).
Companion report with figures: [`results/scaling_drift/REPORT.md`](../results/scaling_drift/REPORT.md).

---

## 1. The question

After the independent audit IVP-15 and the F-1 remediation, the package
commits a critical-amplitude **ladder** — the same threshold formula,
bisected at five grid resolutions:

| N | A*_N (committed, tol 5e-8) | drift per doubling |
|---:|---:|---:|
| 200 | 0.1051042795 | — |
| 400 | 0.0882034349 | 1.690084e-2 |
| 800 | 0.0805332422 | 7.670193e-3 |
| 1600 | 0.0777437258 | 2.789516e-3 |
| 3200 | 0.0768211603 | 9.225655e-4 |

One formula — *classify `A` as supercritical iff an apparent horizon
forms* — evaluated at scalar-scaled grids returns different numbers.
Is the drift a defect? The answer of this document is **no**: the drift
is a theorem. The classification operator does not act on the continuum
family; it acts on the grid-*sampled* family, and sampled parabolic
structures carry a different peak and a different tension than their
continuum originals. Rescaling the grid stretches and compresses those
structures, so the measured threshold must move. What follows makes
this precise, proves the two lemmas that force it, derives the drift
law, and measures every coefficient from committed artifacts only.

## 2. Setup

Near the accumulation point the compactness profile of the pulse is,
to second order in the deviation from its maximum, a **parabola**:

$$q(x) \;=\; q_{\mathrm{pk}} \;-\; \frac{\kappa}{2}\,(x - x_0)^2, \qquad \kappa > 0,$$

where `x` is the local coordinate along the profile, `q_pk` the peak
value and `kappa` the **tension** of the structure — the curvature of
the profile at its peak, i.e. the coefficient that controls how the
gradient energy `(~q')^2` is stored in the pulse. On a grid of `N`
cells over a window of width `w` the sampling spacing is `h = w/N`,
and the engine's classification sees only the node values of `q`.
Three exact facts about this sampled parabola force the drift.

## 3. Lemma A (chord flattening) — *exact*

**Statement.** Let the parabola above be sampled at nodes `x_i` with
spacing `h`, and let the sampled family be the piecewise-linear
(chord) interpolant. Then:

1. the sampled peak is `q(x_j)` at the node `x_j` nearest `x_0`, hence
   the deficit is `kappa * delta^2 / 2` with `delta = dist(x_0, grid) <= h/2`;
2. **worst alignment**: `delta = h/2` and the deficit is *exactly*
   `kappa h^2 / 8`;
3. **mean over alignments**: for `x_0` uniform in a cell, `E[delta^2] = h^2/12`
   and the mean deficit is *exactly* `kappa h^2 / 24`;
4. equivalently, the chord spanning `x_0` has its midpoint at
   `q(x_0) - kappa h^2/8`: the classical statement that a chord pair of
   a parabola sags below the tangency by `kappa h^2/8`.

**Proof.** (1) A parabola is concave here, so the chord interpolant lies
below the curve and its maximum over a cell sits at an endpoint, i.e.
at a node; evaluating `q` at the nearest node gives the stated deficit.
(2) maximize `delta` over alignments. (3) `delta` is uniform on
`[-h/2, h/2]` as `x_0` sweeps a cell, so `E[delta^2] = h^2/12`. (4) the
chord through `(x_0 +/- h/2, q)` has midpoint value
`q(x_0) - (kappa/2)(h/2)^2 = q(x_0) - kappa h^2/8`. QED.

Machine verification: `c6_parabola_check.csv` reproduces (2) and (3)
for `N = 200..3200` to `2.0e-9` relative (float64 representation floor
of the tiny deficit) — the check is exact arithmetic, not a fit.

**Consequence.** The grid does not see the pulse; it sees a *flattened*
pulse whose peak sits lower by a known, `h^2`-scaling amount. Under
grid refinement the sampled peak **inflates back** toward the continuum
value: the parabolic structure *stretches* as the scale is rescaled.

## 4. Lemma B (tension: stretch and compress) — *exact*

**Statement.** Let `L` be the arc length of the parabola over the
window and `L_h` the length of the chord chain through the uniform
samples. Then, *exactly*,

$$L_h \;=\; h \sum_{i=0}^{N-1} \sqrt{1 + \kappa^2 \xi_i^2}, \qquad \xi_i = x_i + \tfrac{h}{2},$$

because a parabola's secant slope over `[x_i, x_i+h]` equals its
derivative at the cell midpoint (`Delta q_i = -kappa h xi_i`).  Hence
`L_h` is the **midpoint rule** applied to the strictly convex arc
integrand `f(x) = sqrt(1 + kappa^2 x^2)`, and therefore

$$L - L_h \;=\; \sum_i \int_{x_i}^{x_i+h} \bigl(f(x)-f(\xi_i)\bigr)\,dx \;>\; 0, \qquad L - L_h \;\le\; \frac{w\,h^2}{24}\,\max_x f''(x) \;=\; \frac{w\,h^2}{24}\,\frac{\kappa^2}{(1+\kappa^2 w^2/4)^{3/2}}.$$

**Proof.** The secant-slope identity is one line of algebra for a
quadratic. Convexity of `f` gives the sign; Taylor at the midpoint
gives the bound with `f''(x) = kappa^2 (1 + kappa^2 x^2)^{-3/2}`. The
closed form of `L` is elementary:
`S(x) = x*sqrt(1+k^2 x^2)/2 + asinh(k x)/(2k)`, `L = S(w/2) - S(-w/2)`.
QED.

Machine verification: the chord chain matches the closed-form midpoint
sum to `1.9e-16` relative at every committed `N`
(`c6_parabola_check.csv`).

**Consequence — the mechanism named in the title.** At fixed geometry,
the discrete structure is **shorter** than the continuum arc: sampling
*compresses* the structure. At fixed discrete geometry, the continuum
arc is longer: refining the grid *stretches* the structure. And since
the gradient (tension) energy of the discrete pulse is carried by the
chord slopes `Delta q_i / h = -kappa xi_i`, the discrete tension the
dynamics actually feels is the *midpoint-sampled* tension — a
different function of the scale than the continuum one. **Parabolic
structures stretch and compress under the curvature of their tension
when the scale is rescaled — exactly as the mechanism hypothesis of
this release states.** One formula, applied to a family whose peak and
tension move with `h`, cannot return one number.

## 5. Theorem T10 (the threshold shift) — *derived*

**Statement.** Let the continuum threshold be defined by the level
condition `F(A, q_pk(A)) = q_crit` with sensitivity
`s = dq_pk/dA > 0` at threshold, and let the profile tension at
threshold be `kappa*`. Then the fixed-grid threshold exists, is unique
for small `h`, and satisfies

$$A^*_N - A^*_{\mathrm{cont}} \;=\; \frac{\kappa^* \alpha^2 h^2}{8\,s} \;+\; O(h^3) \;>\; 0,$$

with `alpha` the stencil half-width in cells (`alpha = 1` for node
sampling). The drift is **positive**: every fixed-grid threshold sits
*above* the continuum one, and the ladder `A*_N` approaches the
continuum value **from above** as `N` grows.

**Proof.** The classification operator applied to the grid family is
the continuum classification of the flattened family
`q_pk -> q_pk - kappa* alpha^2 h^2/8` (Lemma A). Apply the implicit
function theorem to `F(A, q_pk - delta(h)) = q_crit` at
`(A*_cont, q_crit)`: `dA = delta(h) * (dq_pk/dA)^{-1}`, the sign
follows from `delta > 0`, `s > 0`. Monotonicity in `h` follows from
`delta(h) = kappa* alpha^2 h^2/8` being strictly decreasing in `N`.
QED.

**What the theorem does and does not claim.** It proves: the drift
*exists* (one formula, different values — necessarily); its direction
(from above); and an exact leading `h^2` channel with measurable
coefficients. It does *not* claim that this channel dominates at the
reachable `N` — see §7: at `N <= 3200` it does not.

## 6. What the committed ladder measures

Per-doubling drifts and local effective orders
`p_eff = log2(drift_k / drift_{k+1})` of the committed ladder:

| N pair | drift | p_eff |
|---|---:|---:|
| 200 -> 400 | 1.690084e-2 | 1.140 |
| 400 -> 800 | 7.670193e-3 | 1.459 |
| 800 -> 1600 | 2.789516e-3 | 1.596 |
| 1600 -> 3200 | 9.225655e-4 | — |

Three measured facts, committed in the C6 verdict: every drift is
positive (approach **from above**, as T10 requires); `p_eff > 1`
everywhere (decay **faster** than `1/N`); and `p_eff` **climbs**
monotonically (1.140 -> 1.459 -> 1.596) toward the second-order limit
of the RK2-Heun instrument. The ladder is a transition in progress,
not a converged asymptotics.

## 7. Channel decomposition — measured, with an honest negative

**Extrapolation stress test (honest negative).** The two-term
power-law model `A*_N = A_inf + a/N + b/N^2` fits all five committed
points with `R^2 = 0.99925` (`A_inf = 0.07514952, a = 4.1919,
b = 361.8`) — and is nevertheless **REJECTED** as an extrapolation
law: any positive `(a, b)` pair drives the model's own `p_eff` *down*
with `N` (fitted: 1.316 -> 1.188 -> 1.104), while the measured
`p_eff` climbs. The fit is descriptive, not predictive (its
out-of-sample error at `N = 400` is `1.7e-3`, at `N = 200` `1.9e-2`).
**Consequence: no continuum threshold `A_inf` is claimable from this
ladder** — every `A*_N` is a fixed-grid observable, exactly as the
F-1 remediation committed.

**Exact-channel calibration.** Both coefficients of T10 are measured
from committed artifacts only:

* `kappa* = 2728.60` — local quadratic regression on the committed
  supercritical compaction profile nearest the apparent-horizon time
  (`profiles_sub_supercritical.json`, `v = 0.5853` against
  `v_ah = 0.5987`);
* `s = 413.8` — `dq_max/dA` from the two deepest-`eps` sane rows of the
  committed C2 subcritical scan (at `eps_mid = 8.4e-5`);
* `h_r = 9.287e-4` — the committed profile's `r`-spacing at `N = 800`,
  scaled as `800/N`.

| N | observed drift | T10 exact channel `kappa* h^2/(8 s)` | share |
|---:|---:|---:|---:|
| 200 | 1.690084e-2 | 1.5360e-4 | 9.09e-3 |
| 400 | 7.670193e-3 | 3.8401e-5 | 5.01e-3 |
| 800 | 2.789516e-3 | 9.6002e-6 | 3.44e-3 |
| 1600 | 9.225655e-4 | 2.4001e-6 | 2.60e-3 |

The exact channel is real, has the right sign and the right scaling,
but is **sub-dominant**: it carries between `2.6e-3` and `9.1e-3` of
the observed drift. The dominant, monotone channel is attributed —
**labeled hypothesis, not a theorem** — to march-error amplification
under near-critical lingering: a near-threshold run spends
`~ |b^{-1}| ln(1/eps)` null time inside the critical zone (the
measured slowdown, T7), during which the `O(h^2)` local march error
accumulates and acts back on the classification as an effective
amplitude shift. This is the threshold-side twin of the mass-floor law
(T5: `floor_M ~ 12/N`) and is the explicit target of the AMR engine
upgrade on the roadmap. The share of the exact channel *shrinks* with
`N` while `p_eff` climbs toward 2 — both signatures of a transition
toward the second-order asymptotics that the current ladder does not
reach.

## 8. What this closes, and what stays open

Closed by T10 + C6:

* the "one formula, different values" observation is a **theorem-backed
  property** of the instrument, with direction, leading law and
  machine-verified lemmas — not a defect and not a surprise;
* the refusal to print any `A*_N` as "the" threshold (and the IVP-15
  retraction of the `1.06e-6` agreement) is now *proven* correct
  methodology: the ladder drift is forced by the sampling of parabolic
  structures and cannot be refined away at fixed grid.

Open (roadmap):

* the dominant-channel hypothesis (march-error amplification under
  lingering) needs an engine upgrade to test: true AMR near the
  accumulation point would shrink `h` locally and collapse the drift
  faster than any fixed-grid `N`-scaling;
* a continuum `A*_cont` requires either that upgrade or a convergence
  analysis beyond two terms — both out of scope of the committed
  instrument, by design.

## 9. Reproduction

```bash
python3 campaigns/run_c6_drift.py     # ~2 s, no engine march; rewrites the verdict + 2 CSVs
python3 scripts/make_c6_figures.py    # report figures (results/scaling_drift/figures/)
```

Inputs are committed artifacts (`a_star_ladder.csv`,
`profiles_sub_supercritical.json`, `subcritical_scan.csv`); the run is
deterministic (no RNG — the alignment average is analytic). Test pins:
`tests/test_campaigns.py` (C6 block).
