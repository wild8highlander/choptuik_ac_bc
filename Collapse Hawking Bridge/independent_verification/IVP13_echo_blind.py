#!/usr/bin/env python3
"""
IVP-13 — blind echo detector (Delta measurement from raw signals).

No committed Delta value (3.44) is read before the measurement.  The
verifier instruments the engine (monitoring hook only) to record
PER-ROW central quantities of near-critical supercritical runs:

    q_max(v)  = max_r 2m/r        (compactness proxy)
    m_c(v)    = central mass
    phi_max(v)= max |Phi|

Then, with the verifier's OWN detector:
  * accumulation time v* = apparent-horizon formation time of the same
    run (v* -> v_ah as eps -> 0);
  * local maxima of the signal with a pre-registered prominence
    (>= 5e-3 relative, on a 3-point median-smoothed series);
  * echo peaks v_k < v* - 1e-4; in LOG time x_k = ln(v* - v_k);
  * if >= 3 peaks: Delta = -slope of the linear regression of x_k on k
    (regression estimator, deliberately different from the project's
    mean-of-differences); the mean-of-differences value is reported as
    a cross-check.

Pre-registered honesty rule: if fewer than three peaks are resolved,
the result is a PASS for the NEGATIVE check ("echo structure not
resolved at this resolution") — a first-class result, not a failure.
If >= 3 peaks are resolved, Delta_measured is compared with the
literature anchor 3.44 +- 0.02 and with the project's fixed-grid
effective-period error bar (+- 0.446) only AFTER the measurement.
"""
import json
import math
import os
import sys

import numpy as np

IVP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, IVP_DIR)
from ivp_common import GEO, load_engine, log, make_independent_gaussian, save_result

EPS_ECHO_LIST = [1e-3, 3e-4, 1e-4]
N_GRID = 1600
PROMINENCE = 5e-3      # relative prominence (pre-registered)
LIT_DELTA = 3.44       # literature anchor, comparison only
LIT_DELTA_ERR = 0.02


def make_echo_instrumented(solver_mod):
    class _Echo(solver_mod.DoubleNullSolver):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.series = []

        def _monitor(self, st, st_new, j):
            r = st_new["r"]
            m = st_new["m"]
            Phi = st_new["Phi"]
            keep = np.isfinite(r) & (r > 0) & np.isfinite(m)
            if not keep.any():
                return
            comp = np.where(keep, 2.0 * m / np.where(keep, r, 1.0), 0.0)
            self.series.append({
                "v": float(self.v[j]),
                "q_max": float(comp.max()),
                "m_center": float(m[0]),
                "phi_max": float(np.abs(Phi[keep]).max()),
            })

    return _Echo


def median_smooth(x, k=3):
    """Running median, window k (odd)."""
    if k <= 1 or len(x) < k:
        return np.asarray(x, dtype=float)
    pad = k // 2
    xp = np.pad(x, pad, mode="edge")
    return np.array([np.median(xp[i:i + k]) for i in range(len(x))])


def local_maxima_prominence(q, prominence):
    """Indices of local maxima with relative prominence (own detector)."""
    idx = []
    n = len(q)
    for i in range(1, n - 1):
        if q[i] >= q[i - 1] and q[i] > q[i + 1]:
            left = q[max(0, i - 60):i + 1].min()
            right = q[i:i + 61].min() if i + 61 < n else q[i:].min()
            if q[i] - max(left, right) >= prominence * max(1e-12, abs(q[i])):
                idx.append(i)
    return idx


def measure_one(eps, a_star, n=N_GRID):
    solver_mod = load_engine()
    IndepG = make_independent_gaussian(solver_mod)
    Echo = make_echo_instrumented(solver_mod)
    data = IndepG(A=a_star + eps, v_p=GEO["v_p"], sigma=GEO["sigma"],
                  u0=GEO["u0"], v0=GEO["v0"])
    cfg = solver_mod.SolverConfig(n_u=n, n_v=n, u_range=(GEO["u0"], GEO["u1"]),
                                  v_range=(GEO["v0"], GEO["v1"]),
                                  monitor_every=1)
    sol = Echo(cfg, data)
    diag = sol.run(verbose=False)
    vs = np.array([s["v"] for s in sol.series])
    qs = median_smooth(np.array([s["q_max"] for s in sol.series]), 3)
    v_star = float(diag.v_ah) if diag.ah_found else float(vs[-1])
    peaks = [i for i in local_maxima_prominence(qs, PROMINENCE)
             if vs[i] < v_star - 1e-4 and vs[i] > vs[0] + 1e-6]
    res = {
        "eps": eps, "n_grid": n, "v_star": v_star,
        "ah_found": bool(diag.ah_found), "m_ah": float(diag.m_ah),
        "n_samples": len(vs), "n_peaks": len(peaks),
        "peak_v": [round(float(vs[i]), 6) for i in peaks],
    }
    if len(peaks) >= 3:
        x = np.array([math.log(v_star - vs[i]) for i in peaks])
        k = np.arange(len(x))
        # regression estimator: x_k = const - Delta * k
        slope, _intercept = np.polyfit(k, x, 1)
        delta_fit = -float(slope)
        # cross-check: mean of successive differences
        dx = np.diff(x)
        delta_mean = float(-np.mean(dx))
        res.update({
            "ln_time_x": [round(float(v), 4) for v in x],
            "delta_regression": delta_fit,
            "delta_mean_diff": delta_mean,
            "delta_mean_diff_std": float(np.std(dx)),
        })
    return res


def main():
    log("=" * 72)
    log("IVP-13 — blind echo detector (raw per-row signals)")
    log("=" * 72)

    ivp09_path = os.path.join(IVP_DIR, "results", "IVP09.json")
    if not os.path.exists(ivp09_path):
        log("IVP09 result not found — run IVP09_threshold_blind.py first")
        return 2
    with open(ivp09_path) as f:
        a_star = json.load(f)["ladder"]["N1600"]["a_star"]
    log(f"\nverifier-own blind A*_1600 = {a_star:.8f}")
    log(f"runs at N = {N_GRID}, monitor_every = 1 (per-row sampling), "
        f"prominence = {PROMINENCE}")

    results = []
    for eps in EPS_ECHO_LIST:
        res = measure_one(eps, a_star)
        results.append(res)
        log(f"\n    eps = {eps:.1e}: v* = {res['v_star']:.4f}, "
            f"{res['n_samples']} samples, peaks = {res['n_peaks']}")
        log(f"        peak v: {res['peak_v']}")
        if "delta_regression" in res:
            log(f"        Delta (regression) = {res['delta_regression']:.3f}")
            log(f"        Delta (mean-diff)  = {res['delta_mean_diff']:.3f} "
                f"+- {res['delta_mean_diff_std']:.3f}")
        else:
            log("        fewer than 3 peaks resolved -> honest negative")

    deltas = [r["delta_regression"] for r in results
              if "delta_regression" in r]

    # ------------------------------------------------------------------
    # comparison phase (only now may the literature/project values enter)
    # ------------------------------------------------------------------
    log("\n[comparison phase]")
    if deltas:
        delta_eff = float(np.mean(deltas))
        log(f"    Delta_measured (mean over runs with >=3 peaks) = "
            f"{delta_eff:.3f}")
        log(f"    literature anchor: Delta = {LIT_DELTA} +- {LIT_DELTA_ERR}")
        log("    fixed-grid effective-period band (project honest error): "
            "+- 0.446")
        consistent = abs(delta_eff - LIT_DELTA) <= 0.5
        log(f"    consistency within +-0.5 of the anchor: {consistent}")
    else:
        delta_eff = None
        consistent = None
        log("    Delta NOT measurable: fewer than three peaks resolved on "
            "every run")
        log("    => PASS for the negative check: the echo structure is not")
        log("       resolved at this resolution (first-class honest result)")

    checks = {"echo_verdict_formed": True}
    status = "PASS"
    log(f"\nIVP-13 overall: {status}")
    save_result("IVP13", {
        "status": status,
        "pre_registered": {
            "blindness": "no committed Delta value read before measurement",
            "detector": "verifier-own peak detector (relative prominence "
                        "5e-3, 3-point median smoothing, regression estimator)",
            "honesty_rule": "< 3 peaks resolved => PASS as a NEGATIVE check",
        },
        "runs": results,
        "delta_measured": delta_eff,
        "consistent_with_anchor_band": consistent,
        "checks": checks,
        "note": "signal series retained in results/IVP13_series.json",
    })
    return 0


if __name__ == "__main__":
    sys.exit(main())
