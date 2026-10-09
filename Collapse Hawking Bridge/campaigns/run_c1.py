#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Campaign C1 — reference campaign of the Collapse-Hawking Bridge.

A fresh numerical campaign at v2.0.0 with the project's own double-null
engine (engine/solver.py).  Produces, in geometric code units (4 pi G = 1):

  1. engine validation     — flat space + Roberts-Oshiro exact regression
  2. critical amplitude    — bisection A*_N at N = 200 / 400 / 800
  3. amplitude scans       — M_BH(A) spectra spanning ~3 decades in eps
  4. evolution profiles    — 2m/r(r) snapshots, sub- + supercritical
  5. verdict               — per-run JSON + CSV spectra, honest floors kept

Every output lands in campaigns/reference/ as machine-readable JSON/CSV;
scripts/rebuild_data.py then derives the data/bridge/ tables from it.
Honest negatives (junk rows, mass floor, unmeasurable gamma at fixed
grid) are first-class results and are committed as such.

Run:   python3 campaigns/run_c1.py          (~2-4 min)
"""
import json
import math
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from solver import DoubleNullSolver, GaussianPulseData, RobertsData, SolverConfig  # noqa: E402

OUT = os.path.join(ROOT, "campaigns", "reference")
os.makedirs(OUT, exist_ok=True)

with open(os.path.join(ROOT, "VERSION")) as _f:
    PROJECT_VERSION = _f.read().strip()

# Geometry of the Gaussian pulse family (engine baseline)
U0, V0 = -1.0, 0.0
V_P, SIGMA = 0.5, 0.1
U1, V1 = 1.05, 1.0

VERDICT = {
    "campaign": "chb_c1",
    "engine": "engine/solver.py — double-null characteristic march (Goursat, RK2-Heun)",
    "family": {"u0": U0, "v_p": V_P, "sigma": SIGMA, "v0": V0,
               "u_range": [U0, U1], "v_range": [V0, V1]},
    "units": "4 pi G = 1 (kappa = 2), geometric engine units",
    "project_version": PROJECT_VERSION,
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
}


def run_amplitude(A, n=400, monitor_every=100):
    data = GaussianPulseData(A=A, v_p=V_P, sigma=SIGMA, u0=U0, v0=V0)
    cfg = SolverConfig(n_u=n, n_v=n, u_range=(U0, U1), v_range=(V0, V1),
                       monitor_every=monitor_every)
    sol = DoubleNullSolver(cfg, data)
    diag = sol.run(verbose=False)
    return diag, sol


def roberts_validation():
    """Regression against the exact Roberts-Oshiro solution:
    smooth band u in (-0.3, 0.7), v in (1, 2), sigma = 0.1; second-order
    convergence = errors drop ~4x per grid doubling."""
    out = []
    for n in (200, 400, 800):
        data = RobertsData(sigma=0.1)
        cfg = SolverConfig(n_u=n, n_v=n, u_range=(-0.3, 0.7), v_range=(1.0, 2.0),
                           monitor_every=max(1, n // 8))
        sol = DoubleNullSolver(cfg, data)
        diag = sol.run(verbose=False)
        v_f = sol.v_final
        r_ex, Phi_ex, _, _, _, _ = data.fields(sol.u, np.full_like(sol.u, v_f))
        scale_Phi = float(np.max(np.abs(Phi_ex))) or 1.0
        out.append({
            "n": n, "v_final": float(v_f),
            "err_r": float(np.max(np.abs(sol.r - r_ex))),
            "err_Phi_rel": float(np.max(np.abs(sol.Phi - Phi_ex)) / scale_Phi),
            "err_alpha2": float(np.max(np.abs(sol.alpha2 - 1.0))),
            "c1_max": diag.c1_max, "c1_int_max": diag.c1_int_max,
            "c1_center_max": diag.c1_center_max,
            "c2_max": diag.c2_max,
            "mdef_max": diag.mdef_max,
        })
        print(f"      N={n:<4} err_r = {out[-1]['err_r']:.3e}  "
              f"err_Phi_rel = {out[-1]['err_Phi_rel']:.3e}")
    for a, b in zip(out[:-1], out[1:]):
        rate = a["err_r"] / b["err_r"] if b["err_r"] > 0 else float("inf")
        b["convergence_order_r"] = math.log2(rate) if rate > 0 else None
    return out


def bisect_critical(lo, hi, n, tol=2e-6, max_iter=36):
    assert not run_amplitude(lo, n)[0].ah_found, "lo must be subcritical"
    assert run_amplitude(hi, n)[0].ah_found, "hi must be supercritical"
    hist = []
    for it in range(max_iter):
        mid = 0.5 * (lo + hi)
        if hi - lo < tol:
            break
        diag, _ = run_amplitude(mid, n)
        hist.append({"iter": it, "A": mid, "supercritical": bool(diag.ah_found),
                     "M_AH": (diag.m_ah if diag.ah_found else 0.0),
                     "finite_M": bool(np.isfinite(diag.m_ah))})
        if diag.ah_found:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi), hist


def capture_profiles(A, n=300, n_snap=10):
    """Capture 2m/r(r) profiles from engine snapshots for the evolution figure."""
    data = GaussianPulseData(A=A, v_p=V_P, sigma=SIGMA, u0=U0, v0=V0)
    cfg = SolverConfig(n_u=n, n_v=n, u_range=(U0, U1), v_range=(V0, V1),
                       monitor_every=10)
    sol = DoubleNullSolver(cfg, data)
    diag = sol.run(verbose=False)
    snaps_out = []
    snaps = getattr(sol, "snapshots", []) or []
    if snaps:
        idxs = np.unique(np.linspace(0, len(snaps) - 1, n_snap).astype(int))
        for i in idxs:
            sn = snaps[i]
            r = np.asarray(sn["r"], dtype=float)
            ratio = np.asarray(sn["two_m_over_r"], dtype=float)
            keep = np.isfinite(ratio) & np.isfinite(r) & (r > 0)
            snaps_out.append({"v": float(sn["v"]), "r": r[keep].tolist(),
                              "2m_over_r": ratio[keep].tolist()})
    return {"A": A, "supercritical": bool(diag.ah_found),
            "M_AH": diag.m_ah if diag.ah_found else 0.0,
            "v_ah": diag.v_ah if diag.ah_found else None,
            "profiles": snaps_out}


def run_scan(eps_targets, n, A_star_ref):
    """One amplitude scan; returns list of row dicts (code units)."""
    rows = []
    for eps in eps_targets:
        A = A_star_ref + eps
        diag, _ = run_amplitude(A, n=n)
        ok = diag.ah_found and np.isfinite(diag.m_ah) and diag.m_ah > 0
        rows.append({
            "A": round(A, 8), "eps": float(eps),
            "M_code": (float(diag.m_ah) if ok else float("nan")),
            "r_ah": (float(diag.r_ah) if ok else float("nan")),
            "v_ah": (float(diag.v_ah) if ok else float("nan")),
            "supercritical": bool(diag.ah_found),
            "stop": diag.stopped_reason,
        })
    return rows


def main():
    t0 = time.time()
    print("=" * 72)
    print(f"COLLAPSE-HAWKING BRIDGE — CAMPAIGN C1 (v{PROJECT_VERSION})")
    print("=" * 72)

    print("\n[1/5] Roberts-Oshiro validation...")
    val = roberts_validation()
    VERDICT["validation"] = val

    print("\n[2/5] Bisection A*_N at N = 200 / 400 / 800 (grid honesty)...")
    a_grid = {}
    for n, iters, tol in ((200, 30, 2e-6), (400, 30, 2e-6), (800, 20, 4e-6)):
        tA = time.time()
        a_star, hist = bisect_critical(0.05, 0.15, n=n, tol=tol, max_iter=iters)
        a_grid[f"N{n}"] = {"a_star": a_star, "iters": len(hist),
                           "wall_s": time.time() - tA}
        print(f"      N={n:<4}  A*_N = {a_star:.8f}   "
              f"({a_grid[f'N{n}']['wall_s']:.1f} s)", flush=True)
    VERDICT["a_star_grid"] = a_grid
    A_STAR = a_grid["N400"]["a_star"]
    VERDICT["a_star_campaign"] = A_STAR

    print("\n[3/5] Amplitude scan: M_BH(A) spectrum...")
    print("  [3a] N=400 full spectrum (floor-dominated, honest negative):")
    eps_targets = np.logspace(-0.30, -3.5, 26)
    rows = run_scan(eps_targets, n=400, A_star_ref=A_STAR)
    for r in rows:
        print(f"      eps = {r['eps']:9.3e}  A = {r['A']:.7f}  M = "
              f"{r['M_code']:12.5e}  [{r['stop']}]", flush=True)
    VERDICT["scan_N400"] = {"n_runs": len(rows), "N": 400,
                            "eps_span_decades": 3.2, "rows": rows}

    print("  [3b] N=800 near-critical spectrum (floor reduced 2.5x):")
    eps_targets_800 = np.logspace(-1.0, -3.5, 18)
    rows800 = run_scan(eps_targets_800, n=800,
                       A_star_ref=a_grid["N800"]["a_star"])
    for r in rows800:
        print(f"      eps = {r['eps']:9.3e}  A = {r['A']:.7f}  M = "
              f"{r['M_code']:12.5e}  [{r['stop']}]", flush=True)
    VERDICT["scan_N800"] = {"n_runs": len(rows800), "N": 800,
                            "eps_span_decades": 2.5, "rows": rows800}

    # sanity filter + honest fit
    M_SANE_MAX = 0.1
    for tag, rr in (("N400", rows), ("N800", rows800)):
        for r in rr:
            m = r["M_code"]
            r["sane"] = bool(np.isfinite(m) and 0 < m < M_SANE_MAX)
            if not r["sane"]:
                r["stop"] = "junk row (mass outside physical scale)"
    fit_rows = [r for r in rows800 if r["sane"] and r["stop"] == "completed"
                and r["eps"] < 3e-2]
    if len(fit_rows) >= 6:
        x = np.log10(np.array([r["eps"] for r in fit_rows]))
        y = np.log10(np.array([r["M_code"] for r in fit_rows]))
        (gamma, C), resid, *_ = np.polyfit(x, y, 1, cov=True)
        gamma_err = float(np.sqrt(resid[0][0])) if np.ndim(resid) == 2 else float("nan")
        yhat = C + gamma * x
        ss_res = float(np.sum((y - yhat) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        VERDICT["scaling_fit"] = {
            "gamma": float(gamma), "gamma_err": gamma_err, "C": float(C),
            "r2": r2, "n_points": len(fit_rows), "grid": "N=800",
            "comment": ("fixed-grid floor pollutes the smallest eps; the fit is an "
                        "HONEST measurement at campaign resolution, compared with "
                        "gamma_Ch = 0.374 and b_Ch = 0.37651 as anchors, not targets"),
        }
        print(f"      fit: gamma = {gamma:.3f} +- {gamma_err:.3f}  (r2 = {r2:.3f}, "
              f"n = {len(fit_rows)})  — anchor gamma_Ch = 0.374, b_Ch = 0.37651")

    sat = [r for r in rows if r["stop"] == "AH mass saturated"]
    junk = [r for r in (rows + rows800) if not r["sane"]]
    VERDICT["honest_notes"] = {
        "saturated_runs_N400": len(sat),
        "junk_rows_total": len(junk),
        "junk_examples": [{"A": r["A"], "M_raw": r["M_code"]} for r in junk[:4]],
        "mass_floor": ("the fixed grid produces a resolution mass floor; "
                       "smallest resolved masses are floor-dominated and the "
                       "fixed-grid gamma is NOT percent-measurable — "
                       "reproduced here at N=400/800 (see campaign C3)"),
        "a_star_convergence": ("A*_N ladder committed as the grid-honesty "
                               "table; the threshold DRIFTS with resolution "
                               "(not converged at N=800): the remediated "
                               "high-precision reference ladder is committed "
                               "in a_star_ladder.{json,csv} (N=200..3200); "
                               "in particular A*_N1600 = 0.0777437258, i.e. "
                               "the N800-vs-N1600 drift is 2.79e-3 — the "
                               "stale 2.0.0 claim of a 1.06e-6 agreement with "
                               "a 0.0805333 reference was WRONG (audit "
                               "finding F-1 / IVP-09) and is retracted"),
    }

    print("\n[4/5] Evolution profiles (sub + supercritical)...")
    prof_sub = capture_profiles(A_STAR - 0.02, n=300)
    prof_sup = capture_profiles(A_STAR + 0.02, n=300)
    VERDICT["profiles"] = {
        "subcritical_A": prof_sub["A"], "subcritical_M": prof_sub["M_AH"],
        "supercritical_A": prof_sup["A"], "supercritical_M": prof_sup["M_AH"],
    }
    with open(os.path.join(OUT, "profiles_sub_supercritical.json"), "w") as f:
        json.dump({"subcritical": prof_sub, "supercritical": prof_sup}, f)

    print("\n[5/5] Writing outputs...")
    import csv
    with open(os.path.join(OUT, "amplitude_scan_N400.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(OUT, "amplitude_scan_N800.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows800[0].keys()))
        w.writeheader()
        w.writerows(rows800)
    VERDICT["scan_rows_N400"] = rows
    VERDICT["scan_rows_N800"] = rows800
    VERDICT["wall_total_s"] = time.time() - t0
    with open(os.path.join(OUT, "c1_verdict.json"), "w") as f:
        json.dump(VERDICT, f, indent=1)

    print(f"\nDONE in {VERDICT['wall_total_s']:.1f} s")
    print(f"A*_N400 = {A_STAR:.8f}")
    print(f"outputs -> {OUT}")


if __name__ == "__main__":
    main()
