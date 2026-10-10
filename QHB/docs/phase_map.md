# Phase map C9 — the gap never closes (finite-range statement)

Method: 9 volumes (L = 6..32) × 41 couplings (β = 2.80..4.55, step 0.04375).
Status OPEN iff Δ_F(β, L) > Δ_thresh = 0.0363485 (N3).

Result: **369/369 cells OPEN**. The valley floor is refined parabolically to
(β*, Δ_F,min) = (3.3583, 0.181777) with curvature 0.7 (exact for the quadratic
profile). The valley is interior: the gap grows on both sides.

Falsification of the naive window: the narrow-window extrapolator of the
exploratory build predicted closure at β_c = 2.9910. Direct probe measures
Δ_F(β_c) = 0.228995 = 6.3·Δ_thresh — falsified. A reproducible second naive
extrapolator (linear LSQ on the right flank [3.6, 4.0]) predicts a root at
β̂ = 2.9661 with the measured ratio 6.48 — also falsified. Lesson: narrow-window
extrapolation across a curved valley produces phantom closure points.

Jackknife stress (deep checks): dropping any 3 points around the valley and
refitting recovers β* to < 1e-9 — the refinement does not depend on the valley
neighborhood.

See `data/c9_phase_grid.json`, `data/c9_valley.json`,
`data/c9_naive_falsifier.json`, figures `fig_phase_map_*`.
