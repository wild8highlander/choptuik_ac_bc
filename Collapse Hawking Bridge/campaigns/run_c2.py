#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Campaign C2 — the two branches around the threshold.

C1 found the threshold (A* ladder) and the born spectrum on the
supercritical side.  C3 tested the Delta*gamma invariant.  C2 completes
the trio by measuring BOTH branches around the committed A*_800 with
the same engine, the same pulse family, the same units:

  Branch S (subcritical,  A = A* - eps): the field disperses.
      Measured per run: peak compactness q_max = max(2m/r), the time of
      the peak v_qmax (critical slowdown), the number of q(v) peaks
      (echo counter on the dispersing side), residual compactness
      q_final/q_max.
      Fitted: slowdown  v_qmax = a + b*ln(eps)   (DSS logarithmic
      approach: v -> v* as eps -> 0), and the echo accumulation rate
      dN_peaks/dln(1/eps)  (DSS predicts ~ 1/Delta per e-fold).

  Branch X (supercritical, A = A* + eps): the born bifurcation.
      Measured per run: M_code, f~(eps) = M/M_sat with M_sat measured
      ON THIS SCAN (largest eps).  Summarised by eps_half — the
      distance from threshold where f~ crosses 0.5 (a floor-robust
      width of the bifurcation window).
      The exponent fit is deliberately NOT repeated here: it is C3's
      committed measurement; C2 maps the SHAPE of the bifurcation.

Everything runs fresh, from the clean-slate build: no external data,
no prefitted inputs except the committed A*_800 of campaign C1 (same
convention as C3: campaigns must stay commensurable).

Run:   python3 campaigns/run_c2.py            (~1 min, 26 engine runs)
       python3 campaigns/run_c2.py --N 400    (cheaper ladder)
"""
import argparse
import csv
import json
import math
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, os.path.join(ROOT, "chbridge"))
from solver import DoubleNullSolver, GaussianPulseData, SolverConfig  # noqa: E402

OUT = os.path.join(ROOT, "campaigns", "reference")

with open(os.path.join(ROOT, "VERSION")) as _f:
    PROJECT_VERSION = _f.read().strip()

U0, V0 = -1.0, 0.0
V_P, SIGMA = 0.5, 0.1
U1, V1 = 1.05, 1.0

M_SANE_MAX = 0.1          # sanity bound for born masses (same as C1)
Q_SANE_MAX = 2.0          # compactness cannot physically exceed 1 for a BH


def run_amplitude(A, n=800, monitor_every=100):
    data = GaussianPulseData(A=A, v_p=V_P, sigma=SIGMA, u0=U0, v0=V0)
    cfg = SolverConfig(n_u=n, n_v=n, u_range=(U0, U1), v_range=(V0, V1),
                       monitor_every=monitor_every)
    sol = DoubleNullSolver(cfg, data)
    diag = sol.run(verbose=False)
    return diag, sol


def load_a_star():
    """A* from the committed C1 verdict (N=800); re-bisect if absent."""
    p = os.path.join(OUT, "c1_verdict.json")
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)["a_star_grid"]["N800"]["a_star"]
    raise SystemExit("c1_verdict.json not found — run campaigns/run_c1.py first")


def q_series(sol):
    """Compactness maxima q_k = max_r(2m/r) over engine snapshots."""
    vs, qs = [], []
    for sn in getattr(sol, "snapshots", []):
        r = np.asarray(sn["r"], dtype=float)
        q = np.asarray(sn["two_m_over_r"], dtype=float)
        keep = np.isfinite(q) & np.isfinite(r) & (r > 0)
        if keep.any():
            vs.append(float(sn["v"]))
            qs.append(float(np.max(q[keep])))
    return np.array(vs), np.array(qs)


def local_maxima(q, min_prominence=2e-3):
    """Indices of local maxima of a 1-d series with simple prominence test."""
    idx = []
    for i in range(1, len(q) - 1):
        if q[i] >= q[i - 1] and q[i] > q[i + 1]:
            left = min(q[max(0, i - 40):i + 1])
            right = min(q[i:i + 41]) if i + 41 < len(q) else min(q[i:])
            if q[i] - max(left, right) >= min_prominence * max(1e-12, abs(q[i])):
                idx.append(i)
    return idx


def linfit(x, y):
    """Linear fit with r^2; returns (slope, intercept, r2, err) or Nones."""
    if len(x) < 3:
        return None, None, None, None
    (b, a), resid, *_ = np.polyfit(x, y, 1, cov=True)
    err = float(np.sqrt(resid[0][0])) if np.ndim(resid) == 2 else float("nan")
    yhat = a + b * x
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return float(b), float(a), r2, err


# ---------------------------------------------------------------------------
# Branch S — subcritical dispersal
# ---------------------------------------------------------------------------
def scan_subcritical(a_star, n, eps_targets):
    rows = []
    for eps in eps_targets:
        A = a_star - eps
        diag, sol = run_amplitude(A, n=n, monitor_every=1)
        vs, qs = q_series(sol)
        if len(qs) == 0:
            rows.append({"A": round(A, 8), "eps": float(eps), "flipped": False,
                         "q_max": None, "v_qmax": None, "n_peaks": None,
                         "q_final_over_qmax": None, "stop": diag.stopped_reason})
            continue
        i_pk_all = local_maxima(qs)
        i_max = int(np.argmax(qs))
        q_max = float(qs[i_max])
        row = {
            "A": round(A, 8), "eps": float(eps),
            "flipped": bool(diag.ah_found),          # formed AH -> not subcritical
            "q_max": q_max,
            "v_qmax": float(vs[i_max]),
            "n_peaks": int(len(i_pk_all)),
            "q_final_over_qmax": float(qs[-1] / q_max) if q_max > 0 else None,
            "stop": diag.stopped_reason,
        }
        rows.append(row)
        print(f"      eps = {eps:9.3e}  q_max = {row['q_max']:.4f}  "
              f"v_qmax = {row['v_qmax']:.3f}  peaks = {row['n_peaks']}  "
              f"[{'FLIPPED' if row['flipped'] else row['stop']}]", flush=True)
    return rows


def fit_slowdown(rows):
    """v_qmax vs ln(eps) over sane subcritical rows (slowdown slope b < 0)."""
    x = np.array([math.log(r["eps"]) for r in rows
                  if r["q_max"] is not None and not r["flipped"]
                  and r["q_max"] < Q_SANE_MAX])
    y = np.array([r["v_qmax"] for r in rows
                  if r["q_max"] is not None and not r["flipped"]
                  and r["q_max"] < Q_SANE_MAX])
    b, a, r2, err = linfit(x, y)
    return {"slope_ln_eps": b, "intercept": a, "r2": r2, "slope_err": err,
            "n_points": int(len(x)),
            "honest_note": ("fixed grid, 40 compactness samples per run; the "
                            "slowdown is the DSS logarithmic approach only in "
                            "the near-critical band")}


def fit_echo_rate(rows):
    """n_peaks vs ln(1/eps): echoes accumulated per e-fold (DSS: ~1/Delta)."""
    x = np.array([math.log(1.0 / r["eps"]) for r in rows
                  if r["n_peaks"] is not None and not r["flipped"]
                  and r["q_max"] is not None and r["q_max"] < Q_SANE_MAX])
    y = np.array([r["n_peaks"] for r in rows
                  if r["n_peaks"] is not None and not r["flipped"]
                  and r["q_max"] is not None and r["q_max"] < Q_SANE_MAX])
    b, a, r2, err = linfit(x, y)
    return {"echoes_per_efold": b, "intercept": a, "r2": r2, "err": err,
            "n_points": int(len(x)),
            "honest_note": ("40 compactness samples per run bound the countable "
                            "echoes; 1/Delta ~ 0.29 is the anchor for "
                            "comparison, never a fit target")}


# ---------------------------------------------------------------------------
# Branch X — supercritical bifurcation
# ---------------------------------------------------------------------------
def scan_bifurcation(a_star, n, eps_targets):
    rows = []
    for eps in eps_targets:
        A = a_star + eps
        diag, _ = run_amplitude(A, n=n)
        ok = diag.ah_found and np.isfinite(diag.m_ah) and diag.m_ah > 0
        rows.append({
            "A": round(A, 8), "eps": float(eps),
            "M_code": float(diag.m_ah) if ok else float("nan"),
            "stop": diag.stopped_reason,
            "sane": bool(ok and 0 < diag.m_ah < M_SANE_MAX),
        })
        print(f"      eps = {eps:9.3e}  M = {rows[-1]['M_code']:12.5e}  "
              f"[{rows[-1]['stop']}]", flush=True)
    return rows


def bifurcation_summary(rows):
    """M_sat (largest eps of THIS scan), f~ table, eps_half (log-interp)."""
    sane = [r for r in rows if r["sane"] and not r["stop"].startswith("junk")]
    if not sane:
        return {"M_sat_N800": None, "eps_half": None, "f_tilde_min": None,
                "honest_note": "no sane rows — bifurcation not measurable"}
    M_sat = max(r["M_code"] for r in sane)
    f_min = None
    for r in sane:
        r["f_tilde"] = r["M_code"] / M_sat
    f_min = min(r["f_tilde"] for r in sane if r["eps"] < 1e-2)
    # eps_half: log-eps interpolation across the f~ = 0.5 crossing;
    # scan ascending eps (f~ grows from the floor toward saturation) and
    # take the FIRST bracketing pair r1 (f~ < 0.5) -> r2 (f~ >= 0.5)
    srt = sorted(sane, key=lambda r: r["eps"])
    eps_half = None
    for r1, r2 in zip(srt[:-1], srt[1:]):
        if r1["f_tilde"] < 0.5 <= r2["f_tilde"]:
            x1, x2 = math.log(r1["eps"]), math.log(r2["eps"])
            y1, y2 = r1["f_tilde"], r2["f_tilde"]
            if y2 != y1:
                xh = x1 + (0.5 - y1) * (x2 - x1) / (y2 - y1)
                eps_half = float(math.exp(xh))
                break
    return {
        "M_sat_N800": M_sat,
        "M_sat_reference_N400": 0.0794,   # C1 committed cross-check, not an input
        "eps_half": eps_half,
        "f_tilde_min_below_1e2": f_min,
        "honest_note": ("the exponent fit is C3's committed measurement; C2 "
                        "commits the SHAPE (f~ table, eps_half) only"),
    }


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=800)
    ap.add_argument("--sub-points", type=int, default=13)
    ap.add_argument("--sup-points", type=int, default=13)
    args = ap.parse_args()

    t0 = time.time()
    print("=" * 72)
    print("COLLAPSE-HAWKING BRIDGE — CAMPAIGN C2 (two branches, clean slate)")
    print("=" * 72)
    a_star = load_a_star()
    print(f"A* (committed C1, N=800) = {a_star:.8f}")

    print(f"\n[1/4] Branch S: subcritical dispersal scan at N={args.N}...")
    # eps_max = 10^-1.2 ~ 0.063 < A* = 0.0805 keeps A = A* - eps positive
    # for every row (negative-amplitude pulses are a DIFFERENT family and
    # are excluded by construction, not by filtering)
    eps_sub = np.logspace(-1.2, -4.2, args.sub_points)
    sub_rows = scan_subcritical(a_star, args.N, eps_sub)

    print("\n[2/4] Branch S fits: critical slowdown + echo accumulation...")
    slowdown = fit_slowdown(sub_rows)
    echo_rate = fit_echo_rate(sub_rows)
    if slowdown["slope_ln_eps"] is not None:
        print(f"      slowdown: v_qmax = {slowdown['intercept']:.3f} "
              f"{slowdown['slope_ln_eps']:+.4f}*ln(eps)   "
              f"(r2 = {slowdown['r2']:.3f}, n = {slowdown['n_points']})")
    if echo_rate["echoes_per_efold"] is not None:
        print(f"      echo rate: {echo_rate['echoes_per_efold']:.4f} "
              f"peaks / e-fold  (r2 = {echo_rate['r2']:.3f})  "
              f"— anchor 1/Delta = {1.0/3.44:.4f}")
    flipped = [r for r in sub_rows if r["flipped"]]
    if flipped:
        print(f"      honest note: {len(flipped)} subcritical run(s) flipped "
              f"supercritical — kept verbatim")

    print(f"\n[3/4] Branch X: supercritical bifurcation scan at N={args.N}...")
    eps_sup = np.logspace(-0.5, -4.0, args.sup_points)
    sup_rows = scan_bifurcation(a_star, args.N, eps_sup)
    bif = bifurcation_summary(sup_rows)
    if bif["M_sat_N800"] is not None:
        print(f"      M_sat (this scan) = {bif['M_sat_N800']:.5f}   "
              f"(C1 N=400 reference 0.0794)")
        print(f"      eps_half = "
              f"{bif['eps_half'] if bif['eps_half'] is None else format(bif['eps_half'], '.3e')}")

    print("\n[4/4] Verdict...")
    V = {
        "campaign": "chb_c2",
        "engine": "engine/solver.py — double-null characteristic march (Goursat, RK2-Heun)",
        "project_version": PROJECT_VERSION,
        "units": "4 pi G = 1 (kappa = 2), geometric engine units",
        "family": {"u0": U0, "v_p": V_P, "sigma": SIGMA, "v0": V0,
                   "u_range": [U0, U1], "v_range": [V0, V1]},
        "grid": {"N": args.N},
        "a_star_N800": a_star,
        "subcritical": {
            "n_runs": len(sub_rows),
            "eps_span_decades": round(math.log10(max(eps_sub) / min(eps_sub)), 2),
            "flipped_runs": len(flipped),
            "rows": sub_rows,
            "slowdown_fit": slowdown,
            "echo_rate_fit": echo_rate,
        },
        "bifurcation": {
            "n_runs": len(sup_rows),
            "rows": sup_rows,
            "summary": bif,
        },
        "honest_notes": {
            "sampling": ("q(v) is sampled by 40 engine snapshots per run; "
                         "peak counts and v_qmax carry that sampling step"),
            "gamma": ("the mass-scaling exponent is deliberately NOT re-fit "
                      "here — C3 owns that committed measurement"),
            "flipped": ("subcritical runs that formed an apparent horizon are "
                        "kept verbatim with flipped=true (A*_800 is a fixed-"
                        "grid quantity; the closest eps can cross it)"),
            "junk": ("supercritical rows with overflowing masses are kept "
                     "with sane=false, never dropped"),
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "wall_total_s": None,
    }
    V["wall_total_s"] = time.time() - t0

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "c2_verdict.json"), "w") as f:
        json.dump(V, f, indent=1)
    with open(os.path.join(OUT, "subcritical_scan.csv"), "w", newline="") as f:
        cols = ["A", "eps", "flipped", "q_max", "v_qmax", "n_peaks",
                "q_final_over_qmax", "stop"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in sub_rows:
            w.writerow({c: r.get(c) for c in cols})
    with open(os.path.join(OUT, "bifurcation_ftilde.csv"), "w", newline="") as f:
        cols = ["A", "eps", "M_code", "f_tilde", "stop", "sane"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in sup_rows:
            w.writerow({c: r.get(c) for c in cols})

    print(f"      subcritical: {len(sub_rows)} runs "
          f"({len(flipped)} flipped), slowdown r2 = {slowdown['r2']}")
    print(f"      bifurcation: M_sat = "
          f"{bif['M_sat_N800'] if bif['M_sat_N800'] is None else round(bif['M_sat_N800'], 5)}, "
          f"eps_half = {bif['eps_half']}")
    print(f"\nDONE in {V['wall_total_s']:.1f} s -> campaigns/reference/c2_verdict.json")


if __name__ == "__main__":
    main()
