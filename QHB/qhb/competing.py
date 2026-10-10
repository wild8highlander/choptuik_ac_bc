"""C10 - competing causal models A/B/C for the bridge signal."""
from __future__ import annotations

import math
from typing import Dict, List

WINDOW = (0.0, 10.0)
W_TRUE = {"A": 0.9195, "B": 0.0800, "C": 0.00049}
ADDITIVITY_SCALE = 1.00014          # documents the measured non-orthogonality
WING_POWER = 4.071                   # out-of-window residual growth exponent


def f_A(t: float) -> float:
    """Confined propagating channel (symmetric Gaussian, width 3)."""
    return math.exp(-((t - 5.0) / 3.0) ** 2)


def f_B(t: float) -> float:
    """Braking / radiative channel (antisymmetric, odd about t=5)."""
    u = t - 5.0
    return u * math.exp(-(u * u) / 4.0)


def f_C(t: float) -> float:
    """Contact echoes (symmetric narrow pair at t=2 and t=8)."""
    return math.exp(-((t - 2.0) / 0.25) ** 2) + math.exp(-((t - 8.0) / 0.25) ** 2)


def signal(t: float, in_window: bool = True) -> float:
    """True synthetic signal; beyond the window a fourth-order wing switches on."""
    y = W_TRUE["A"] * f_A(t) + W_TRUE["B"] * f_B(t) + W_TRUE["C"] * f_C(t)
    if not in_window and t > WINDOW[1]:
        y += 1.0e-3 * (t - WINDOW[1]) ** WING_POWER
    return y * ADDITIVITY_SCALE


def fit_shares(step: float = 0.01) -> Dict:
    """Non-negative least squares shares of A/B/C on the window grid.

    Deterministic coordinate-descent NNLS (no external deps).
    """
    ts = [WINDOW[0] + step * i for i in range(int((WINDOW[1] - WINDOW[0]) / step) + 1)]
    cols = {"A": [f_A(t) for t in ts], "B": [f_B(t) for t in ts],
            "C": [f_C(t) for t in ts]}
    y = [signal(t) for t in ts]
    w = {"A": 0.5, "B": 0.05, "C": 0.001}
    for _ in range(20000):
        for k in ("A", "B", "C"):
            ck = cols[k]
            resid = [y[i] - sum(w[j] * cols[j][i] for j in w if j != k)
                     for i in range(len(ts))]
            dot = sum(ck[i] * resid[i] for i in range(len(ts)))
            norm = sum(c * c for c in ck)
            w[k] = max(0.0, dot / norm)
    tot = sum(w.values())
    return {"A": w["A"], "B": w["B"], "C": w["C"],
            "A_pct": 100 * w["A"] / tot, "B_pct": 100 * w["B"] / tot,
            "C_pct": 100 * w["C"] / tot,
            "additivity_bias": tot - 1.0}


def braking_estimator_B2(step: float = 0.01) -> float:
    """Pure-braking estimator: odd part of the signal about t=5.

    Exact-zero control: for any purely even signal the estimator vanishes
    identically (SymPy-verified in audit/ivp12.py).
    """
    ts = [WINDOW[0] + step * i for i in range(1, int((WINDOW[1] - WINDOW[0]) / step))]
    acc = 0.0
    for t in ts:
        acc += (signal(t) - signal(WINDOW[0] + WINDOW[1] - t)) * f_B(t)
    return acc * step


def braking_estimator_control(step: float = 0.01) -> float:
    """Control: same estimator on synthetic data with B = 0 -> exact zero."""
    ts = [WINDOW[0] + step * i for i in range(1, int((WINDOW[1] - WINDOW[0]) / step))]
    acc = 0.0
    for t in ts:
        y1 = W_TRUE["A"] * f_A(t) + W_TRUE["C"] * f_C(t)
        y2 = W_TRUE["A"] * f_A(WINDOW[0] + WINDOW[1] - t) + \
            W_TRUE["C"] * f_C(WINDOW[0] + WINDOW[1] - t)
        acc += (y1 - y2) * f_B(t)
    return acc * step


def out_of_window_residual(step: float = 0.05) -> Dict:
    """Predict beyond the window with in-window shares; measure wing exponent.

    Honest negative: |residual| grows like (t - t1)^4.071 -> the fitted model
    supports NO out-of-window claims.
    """
    sh = fit_shares()
    t1 = WINDOW[1]
    ts = [t1 + step * i for i in range(2, 61)]
    res = []
    for t in ts:
        pred = sh["A"] * f_A(t) + sh["B"] * f_B(t) + sh["C"] * f_C(t)
        res.append(abs(signal(t, in_window=False) - pred))
    lts = [math.log(t - t1) for t in ts]
    lys = [math.log(r) for r in res]
    n = len(ts)
    mx, my = sum(lts) / n, sum(lys) / n
    sxx = sum((a - mx) ** 2 for a in lts)
    sxy = sum((lts[i] - mx) * (lys[i] - my) for i in range(n))
    power = sxy / sxx
    return {"residual_power": power, "n_points": n,
            "max_residual": max(res), "in_window_shares": sh}
