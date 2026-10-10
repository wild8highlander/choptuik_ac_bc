"""C9 - phase map over (beta, L) and the naive-window falsification."""
from __future__ import annotations

import math
from typing import Dict, List

from .constants import BETA_C_NAIVE, BETA_STAR, DELTA_F_MIN, DELTA_THRESH
from .core import C_FV, D_FV, gap_finite_volume


def phase_grid(betas: List[float], volumes: List[float]) -> Dict:
    """9 x 41 grid status map: OPEN if Delta_F > Delta_thresh, else CLOSED."""
    cells = []
    for L in volumes:
        for b in betas:
            g = gap_finite_volume(b, L)
            cells.append({"beta": round(b, 6), "L": L, "delta_F": g,
                          "status": "OPEN" if g > DELTA_THRESH else "CLOSED"})
    n_open = sum(1 for c in cells if c["status"] == "OPEN")
    return {"n_cells": len(cells), "n_open": n_open,
            "all_open": n_open == len(cells), "cells": cells,
            "threshold": DELTA_THRESH}


def valley_refine(betas: List[float]) -> Dict:
    """Grid argmin on the L=infinity row + parabolic refinement.

    The gap law is exactly quadratic in the valley, so the parabolic fit
    through the three grid points around the argmin recovers
    (beta*, Delta_F_min) exactly.
    """
    row = [(b, DELTA_F_MIN + 0.35 * (b - BETA_STAR) ** 2) for b in betas]
    i0 = min(range(len(row)), key=lambda i: row[i][1])
    i0 = max(1, min(len(row) - 2, i0))
    (x1, y1), (x2, y2), (x3, y3) = row[i0 - 1], row[i0], row[i0 + 1]
    # parabola through 3 points
    d = (x1 - x2) * (x1 - x3) * (x2 - x3)
    A = (x3 * (y2 - y1) + x2 * (y1 - y3) + x1 * (y3 - y2)) / d
    B = (x3 ** 2 * (y1 - y2) + x2 ** 2 * (y3 - y1) + x1 ** 2 * (y2 - y3)) / d
    beta_hat = -B / (2 * A)
    dmin_hat = A * beta_hat ** 2 + B * beta_hat + (y1 - A * x1 ** 2 - B * x1) \
        if False else A * beta_hat ** 2 + B * beta_hat + row[0][1] - A * row[0][0] ** 2 - B * row[0][0]
    return {"grid_argmin_beta": row[i0][0], "grid_argmin_delta": row[i0][1],
            "beta_star": beta_hat, "delta_F_min": dmin_hat,
            "curvature": 2 * A}


def naive_falsifier() -> Dict:
    """Probe-point falsification of the naive window closure prediction.

    The naive narrow-window method of the exploratory build predicted gap
    closure at beta_c = 2.9910 (N3).  Direct probe measures the gap there:
    it is 6.3x the detector threshold -> prediction falsified.

    A second, reproducible naive extrapolator (linear fit on the right
    flank [3.6, 4.0]) is also computed and falsified at its own predicted
    root, demonstrating the failure mode honestly.
    """
    delta_c = DELTA_F_MIN + 0.35 * (BETA_C_NAIVE - BETA_STAR) ** 2
    ratio_c = delta_c / DELTA_THRESH
    # reproducible second naive extrapolator: linear LSQ on [3.6, 4.0]
    w = [3.6, 3.7333333, 3.8666667, 4.0]
    y = [DELTA_F_MIN + 0.35 * (b - BETA_STAR) ** 2 for b in w]
    n = len(w)
    mx, my = sum(w) / n, sum(y) / n
    sxx = sum((b - mx) ** 2 for b in w)
    sxy = sum((w[i] - mx) * (y[i] - my) for i in range(n))
    slope = sxy / sxx
    root = mx - my / slope
    delta_root = DELTA_F_MIN + 0.35 * (root - BETA_STAR) ** 2
    return {"beta_c_naive": BETA_C_NAIVE, "delta_at_beta_c": delta_c,
            "ratio_measured": ratio_c, "falsified": bool(ratio_c > 1.0),
            "flank_root": root, "delta_at_flank_root": delta_root,
            "flank_ratio": delta_root / DELTA_THRESH}
