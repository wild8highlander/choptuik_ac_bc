#!/usr/bin/env python3
"""
IVP-12 — resolution-scaling / numerical-floor test.

The claimed mass floor is verified INDEPENDENTLY.  Using the verifier's
own scans (IVP-11 rows) plus dedicated direct probes, the smallest
resolved final mass floor_M(N) is measured at N = 400 / 800 / 1600 / 3200
and fitted two ways:

    fit A :  floor_M = C / N
    fit B :  floor_M = C / N^p     (p measured, not assumed)

Pre-registered criterion: p in [0.7, 1.3] independently evidences a
1/N grid floor.  The committed '12/N' rule is compared only in the
final comparison phase.
"""
import json
import os
import sys

import numpy as np

IVP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, IVP_DIR)
from ivp_common import (
    log,
    run_gaussian,
    save_result,
    worst_status,
)

PROBE_EPS = [1e-3, 3e-4]
GRIDS = [400, 800, 1600, 3200]


def power_fit(n_vals, m_vals):
    """Own fit: log M = log C - p log N."""
    x = np.log10(np.asarray(n_vals, dtype=float))
    y = np.log10(np.asarray(m_vals, dtype=float))
    (minus_p, logC), cov = np.polyfit(x, y, 1, cov=True)
    p = -float(minus_p)
    p_err = float(np.sqrt(cov[0][0]))
    yhat = logC - p * x
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return p, float(10 ** logC), p_err, float(r2)


def main():
    log("=" * 72)
    log("IVP-12 — numerical-floor law (multi-resolution fit)")
    log("=" * 72)

    # --- floors from the IVP-11 scans (verifier-own measurements) --------
    ivp11_rows_path = os.path.join(IVP_DIR, "results", "IVP11_rows.json")
    floors = {}
    if os.path.exists(ivp11_rows_path):
        with open(ivp11_rows_path) as f:
            scans = json.load(f)
        for n in GRIDS:
            key = f"N{n}"
            if key in scans and scans[key].get("floor_M"):
                floors[n] = {"floor_M": scans[key]["floor_M"],
                             "source": "IVP-11 scan minimum"}

    # --- dedicated direct probes (independent confirmation) --------------
    log("\n[A] direct probes at fixed eps (verifier-own A* from IVP-09)")
    ivp09_path = os.path.join(IVP_DIR, "results", "IVP09.json")
    if not os.path.exists(ivp09_path):
        log("IVP09 result not found — run IVP09_threshold_blind.py first")
        return 2
    with open(ivp09_path) as f:
        ladder = json.load(f)["ladder"]
    probes = {}
    for n in GRIDS:
        a_star = ladder[f"N{n}"]["a_star"]
        probes[n] = {}
        for eps in PROBE_EPS:
            diag, _ = run_gaussian(a_star + eps, n)
            ok = diag.ah_found and np.isfinite(diag.m_ah) and 0 < diag.m_ah < 0.1
            probes[n][eps] = float(diag.m_ah) if ok else None
            log(f"    N={n:<5} eps={eps:.0e}: M = "
                f"{probes[n][eps] if probes[n][eps] is None else format(probes[n][eps], '.5e')}")
    # the probe floor at each N: the smaller of the two probe masses
    for n in GRIDS:
        vals = [v for v in probes[n].values() if v is not None]
        if vals and n not in floors:
            floors[n] = {"floor_M": min(vals), "source": "direct probe"}

    log("\n[B] floor_M(N) table (verifier-own)")
    for n in GRIDS:
        if n in floors:
            log(f"    N={n:<5} floor_M = {floors[n]['floor_M']:.5e} "
                f"({floors[n]['source']})   12/N = {12.0/n:.5e}")

    # --- fits -------------------------------------------------------------
    n_vals = [n for n in GRIDS if n in floors]
    m_vals = [floors[n]["floor_M"] for n in n_vals]
    checks = {}
    fitA = fitB = None
    if len(n_vals) >= 3:
        # fit A: M = C/N  -> check residuals
        C_A = float(np.mean([m * n for m, n in zip(m_vals, n_vals)]))
        resA = max(abs(m - C_A / n) / m for m, n in zip(m_vals, n_vals))
        fitA = {"C_over_N": C_A, "max_rel_residual": resA}
        # fit B: free exponent
        p, C_B, p_err, r2 = power_fit(n_vals, m_vals)
        fitB = {"p": p, "C": C_B, "p_err": p_err, "r2": r2}
        log(f"\n[C] fit A (M = C/N):    C = {C_A:.5e}, max rel residual = {resA:.3f}")
        log(f"    fit B (M = C/N^p):  p = {p:.3f} +- {p_err:.3f} "
            f"(R^2 = {r2:.4f}), C = {C_B:.5e}")
        checks["floor_law_p_in_[0.7,1.3]"] = bool(0.7 <= p <= 1.3)
    else:
        log("\n[C] not enough grids with floors for a fit")
        checks["floor_law_p_in_[0.7,1.3]"] = False

    # --- comparison phase --------------------------------------------------
    log("\n[D] comparison phase — committed floor values")
    try:
        sys.path.insert(0, os.path.dirname(IVP_DIR))
        from chbridge.constants import CAMPAIGN as CAMP  # comparison only
        comp = {
            "committed_floor_N800": CAMP["mass_floor_N800"],
            "committed_floor_N1600_c3b": CAMP["floor_M_N1600_c3b"],
            "committed_floor_N3200_c3b": CAMP["floor_M_N3200_c3b"],
        }
        for k, v in comp.items():
            log(f"    {k} = {v:.5e}")
        if 800 in floors:
            rd = abs(floors[800]["floor_M"] - comp["committed_floor_N800"]) \
                / comp["committed_floor_N800"]
            log(f"    |IVP - committed| at N=800: rel = {rd:.2f} "
                "(floor depends on the scan band; agreement expected in "
                "magnitude, not in digits)")
    except Exception as e:
        log(f"    (committed floor comparison skipped: {e})")

    status = worst_status(["PASS" if v else "FAIL" for v in checks.values()])
    log(f"\nIVP-12 overall: {status}")
    save_result("IVP12", {
        "status": status,
        "pre_registered": {
            "method": "floor_M(N) from verifier-own scans + direct probes; "
                      "two fits (C/N and C/N^p)",
            "criterion": "measured exponent p in [0.7, 1.3]",
        },
        "floors": {str(k): v for k, v in floors.items()},
        "probes": {str(k): {str(kk): vv for kk, vv in v.items()}
                   for k, v in probes.items()},
        "fit_A": fitA, "fit_B": fitB,
        "checks": checks,
    })
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
