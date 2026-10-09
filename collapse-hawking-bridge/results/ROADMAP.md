# Roadmap — Collapse-Hawking Bridge

Status line: **v2.1.0 — the IVP-15 alignment edition.** The four
engine campaigns (C1, C2, C3, C3b) plus the analytical drift campaign
C6 are committed; the independent audit IVP-15 is fully absorbed (all
three findings remediated and quoted correctly everywhere); the theorem
layer grew to T1–T10; the 600 dpi figure suite, the launch animations,
the multilang twins, the data workbook, the bilingual monograph and the
logo are shipped; the web companion is live.

---

## Where the project stands (stage analysis, v2.1.0)

### Stage 1 — Engine and its validation: COMPLETE

The double-null characteristic solver (Goursat problem, RK2-Heun
march, `engine/solver.py`) passes the Roberts–Oshiro self-test with
measured convergence orders **2.03 / 2.09** at N = 200→400→800. The
critical-amplitude ladder is pinned:

| N | A* | wall |
|---|----|------|
| 200 | 0.1051048278808594 | — |
| 400 | 0.0882011413574219 | — |
| 800 | 0.08053436279296877 | ~48 s for the full C1 sweep |
| 1600 (remediated ladder, v2.0.1 F-1) | 0.0777437257766724 | — |
| 3200 (remediated ladder, v2.0.1 F-1) | 0.07682116031646731 | — |

The ladder DRIFTS (2.79e-3 from N=800 to N=1600); the stale 2.0.0
claim of a 1.06e-6 agreement with a 0.0805333 reference did not
reproduce under blind bisection (audit IVP-09) and is retracted. The
drift itself — not an agreement claim — closes the "is the engine
trustworthy" question for the reachable band: every committed number
is the engine's own, at every resolution.

### Stage 2 — Measurement campaigns on the committed grid: COMPLETE

* **C1** (validation + born spectrum): complete, byte-deterministic,
  junk rows kept and flagged.
* **C2** (two branches): subcritical dispersal is monotone in
  q_max (0.0158 → 0.5845) with a measured slowdown law
  v = 0.510 − 0.0334 ln ε (r² = 0.71) and an echo accumulation rate
  0.1909/e-fold vs the critical anchor 0.2907; supercritical branch
  has a measured bifurcation curve f~(ε) with half-width
  ε½ = 4.86e-3.
* **C3** (Δ·γ): anchor-level **PASS** (1.28656 vs 1.27 ± 0.05,
  deviation 1.3%); engine-level honest negative committed with full
  diagnostics.
* **C3b** (concentrated grids N=1600/3200): the floor law
  **floor_M ≈ (13 ± 1)/N** is measured as a first-class result on
  the per-grid F-2 thresholds (0.0155 / 8.575e-3 / 4.245e-3); γ_eff =
  0.041/0.060, floor-dominated (anchor 0.374 not reachable by this
  instrument; the 2.0.0 "~0.12" was an eps-mislabeling artifact,
  retracted); Δ remains unmeasurable below 3 peaks. Both negatives
  re-confirmed at the v2.1.0 re-run.

### Stage 3 — The bridge itself: COMPLETE (model level)

The thermodynamic side (closed forms, CODATA-2018): T_H ∝ 1/M,
S_BH ∝ M², t_evap ∝ M³, photon-only luminosity, Page fraction
exactly 1 − 2^(−3/2), Haar audit of the unitary flux model at
max deviation 0.0042 bits, CMB contact mass 4.5016e22 kg. The mapping
M_BH = M_in · f~(ε) is applied over five input scales
(Planck … Solar) in 23 columns of `bridge_master.csv`.

### Stage 4½ — The drift law (NEW in v2.1.0): COMPLETE

Campaign C6 + theorem T10 close the question the F-1 remediation left
open: the A\* ladder drift is not a defect but a property of
grid-sampled parabolic structures — chord flattening κh²/8 (Lemma A)
and the chord-chain arc deficit (Lemma B), both machine-verified to
2.0e-9 / 1.9e-16; the threshold shift A\*_N − A\*_cont = κ\*h²/(8s) > 0
follows by the implicit function theorem with κ\* = 2728.60 and
s = 413.8 measured on committed artifacts. Honest negatives pinned:
no A\*_inf is claimable; the exact channel is sub-dominant
(share 2.6e-3…9.1e-3). Artifacts: `campaigns/reference/c6_drift_verdict.json`,
`docs/scaling_law.md`, `results/scaling_drift/`, 3 pytest pins.

### Stage 4 — Dissemination layer (COMPLETE, extended in v2.1.0)

* `figures_hires/` — 17 figure types × 2 languages × 2 themes at
  **600 dpi** (68 PNG, 23 MB), one figure per measurement
  architecture.
* `animations/` — 4 launch animations × 2 languages (MP4 + GIF).
* `multilang/` — 7 languages (3 verified twins, cross-checked to
  7.1e-13; 3 portable sources honestly flagged; Python reference).
* `tables/bridge_workbook.xlsx` — 13 data tables + overview, one file.
* `monograph/` — encyclopedic appendix, RU/EN, DOCX + PDF, plus the
  theorems volume RU/EN, DOCX + PDF (T1–T10, aligned to the audit).
* `figures/logo/` — the package logo (light/dark, PNG 600 dpi + SVG).
* `results/scaling_drift/` — the C6 report folder with 8 figures.
* Web companion (Next.js): figure gallery, animation shelf, theorem
  browser, table viewer, roadmap page, download center.

### Honest negatives that gate the next stage

1. **γ at engine level**: 0.374 requires ε below the reach of any
   fixed or concentrated grid governed by floor_M ≈ (13 ± 1)/N. The
   instrument, not the physics, is the limit.
2. **Δ (echo period)**: < 3 resolvable peaks at every depth up to
   N = 3200.
3. **v_qmax quantization**: 40 engine snapshots per run impose the
   staircase visible in the slowdown data.
4. **No continuum threshold**: per T10, the two-term extrapolation of
   the A\* ladder is rejected by its own p_eff trajectory — A\*_cont is
   not claimable from the committed band; the exact parabolic channel
   is measured and sub-dominant, and the dominant channel
   (march-error amplification under near-critical lingering) is a
   labeled hypothesis awaiting the AMR engine.

---

## Roadmap (post-2.1)

### C4 — QNM ringdown of the born ensemble (next campaign)

Test the septinial correction ω → ω(1 − 1/(1200π²)) on the l=2
fundamental mode against the born ensemble. The correction is
8.44343e-5 relative — 3.5 orders below the current frequency
resolution of the engine; the campaign must therefore be designed as
a *difference* measurement (two engines, same grid), not an absolute
one. Deliverables: c4_verdict.json, two new figures, one theorem
(promoted or rejected).

### C5 — Multi-family universality of f~(ε)

Second pulse profile (different σ and v_p in the family) to test
whether ε½ and the shape of f~ are universal or family-bound. This
converts the bifurcation curve from "a measurement" into "a
universality claim" — the difference between a table and a law.

### Engine upgrade path — beating the floor law

The explicit numeric target: an engine-level γ compatible with 0.374
and ≥ 3 resolved echo peaks. Two routes, in order of preference:

1. **True AMR** (adaptive mesh refinement) concentrated at the
   accumulation point r = 0 — the C3b ladder was concentrated but
   static; refinement must follow the collapsing pulse.
2. **Characteristic-double-null hybrid** with a moving inner
   boundary.

The floor law itself becomes the benchmark: any upgrade must move
floor_M(N) off the (13 ± 1)/N line, and the first figure of the upgrade
paper is the old line with three points off it. Per T10, the same AMR
engine would also collapse the threshold drift faster than any
fixed-grid N-scaling — one upgrade, two victories.

### Theorem pipeline

* T1 (exact Page fraction) and T2 (CMB contact uniqueness) are exact
  and closed — candidates for formal write-up.
* T5 (floor law) is numerically established on 3 grids; C3b on N=6400
  (if the wall budget allows ~6.5 min/run) would make it four.
* T10 (drift law) is analytically derived with measured coefficients;
  the AMR engine is its experimental test.
* T6 (Δ·γ anchor) is a comparison result; it will be either promoted
  by an engine-level measurement or retired by one — nothing in
  between.

### Dissemination

* v2.2/v3.0: monograph appendix gains a C4/C5 section if those
  campaigns run; web companion gains a per-figure deep-link mode.
* Archive mirror (Zenodo-style DOI) once C4 commits.

---

## What "done" means for v3.0

1. An engine whose floor is no longer (13 ± 1)/N — or a written proof
   that it cannot be beaten on this architecture.
2. C4 and C5 committed with the same verdict discipline as C1–C3b.
3. γ engine-level within 10% of 0.374 — or the honest negative
   documented with the same care as the current one.
