#!/usr/bin/env python3
"""
Campaign C3b — concentrated-resolution retry of gamma and Delta.

What "adaptive" means here (honest definition, no AMR claims): the
engine is NOT rewritten; instead RESOLUTION IS CONCENTRATED on the
critical window.  Deep grids (N = 1600, 3200) are spent only on
  (a) a narrow supercritical eps band around the committed A*_800
      (where the fixed-grid mass floor polluted the C3 fit), and
  (b) echo runs nearest threshold.
The probe result that motivates the campaign: the mass floor DROPS
with resolution (at eps = 1e-3: M = 0.0179 at N=800, 0.0075 at N=1600,
0.0048 at N=3200) — so the C3 "gamma unmeasurable" verdict is a
statement about the floor, and the floor is a controllable knob.

Three products:

  gamma ladder — log-log fit of M(eps) at N = 1600 and N = 3200 over
      the narrow band; committed per grid with its floor_M; the ladder
      of gamma_eff(N) and floor_M(N) IS the result (does the fitted
      exponent approach the anchor gamma_Ch = 0.374 as the floor
      sinks?).
  delta ladder — echo detector at N = 1600 / 3200 for eps_echo near
      threshold; committed per run with peak tables; delta_eff is
      estimated only if >= 3 peaks are resolved (same rule as C3).
  products — P_engine_N (delta_eff x gamma_eff per deepest grid) and
      the anchor product P_anchor = Delta_lit x gamma_Ch = 1.28656,
      compared against the C3 target 1.27 +- 0.05.

Run:   python3 campaigns/run_c3b.py           (~5 min; needs c1_verdict.json)
       python3 campaigns/run_c3b.py --skip-delta   (gamma ladder only)

v2.0.1 (remediation F-2 of the independent audit IVP-11): eps is now
measured from the PER-GRID critical amplitude A*_N of the SAME grid
(bisected fresh at the start of the campaign), NOT from A*_N800.  The
2.0.0 release reused A*_N800 as the base for the N=1600/3200 scans;
since A*_N1600 = 0.07774 differs from A*_N800 = 0.08053 by 2.8e-3, the
committed eps axis was mislabeled and the fitted gamma_eff ~ 0.11 was
an artifact of that mislabeling (audit finding F-2).
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
from constants import DGAMMA_LIT, DGAMMA_TARGET, DGAMMA_TOL, gamma_Ch
from solver import DoubleNullSolver, GaussianPulseData, SolverConfig

OUT = os.path.join(ROOT, "campaigns", "reference")

with open(os.path.join(ROOT, "VERSION")) as _f:
    PROJECT_VERSION = _f.read().strip()

U0, V0 = -1.0, 0.0
V_P, SIGMA = 0.5, 0.1
U1, V1 = 1.05, 1.0

M_SANE_MAX = 0.1


def run_amplitude(A, n, monitor_every=100):
    data = GaussianPulseData(A=A, v_p=V_P, sigma=SIGMA, u0=U0, v0=V0)
    cfg = SolverConfig(n_u=n, n_v=n, u_range=(U0, U1), v_range=(V0, V1),
                       monitor_every=monitor_every)
    sol = DoubleNullSolver(cfg, data)
    diag = sol.run(verbose=False)
    return diag, sol


def load_a_star():
    p = os.path.join(OUT, "c1_verdict.json")
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)["a_star_grid"]["N800"]["a_star"]
    raise SystemExit("c1_verdict.json not found — run campaigns/run_c1.py first")


def bisect_a_star(n, tol=2e-6, max_iter=30):
    """Per-grid critical amplitude A*_N (F-2 remediation).

    Bracket is seeded from the committed remediated ladder
    (a_star_ladder.json) when available and re-validated / widened at
    this resolution; bisection on the AH classification to tol.
    """
    ladder_p = os.path.join(OUT, "a_star_ladder.json")
    seed = None
    if os.path.exists(ladder_p):
        with open(ladder_p) as f:
            seed = json.load(f)["ladder"].get(f"N{n}", {}).get("a_star")
    if seed is None:
        seed = load_a_star()
    lo, hi = seed - 0.01, seed + 0.01
    for _ in range(8):
        if not (run_amplitude(lo, n)[0].ah_found and
                np.isfinite(run_amplitude(lo, n)[0].m_ah)):
            break
        lo -= 0.02
    for _ in range(8):
        d = run_amplitude(hi, n)[0]
        if d.ah_found and np.isfinite(d.m_ah):
            break
        hi += 0.02
    assert not run_amplitude(lo, n)[0].ah_found, f"lo supercritical at N={n}"
    assert run_amplitude(hi, n)[0].ah_found, f"hi subcritical at N={n}"
    hist = []
    for it in range(max_iter):
        mid = 0.5 * (lo + hi)
        if hi - lo < tol:
            break
        d, _ = run_amplitude(mid, n)
        sup = bool(d.ah_found and np.isfinite(d.m_ah))
        hist.append({"it": it, "A": mid, "sup": sup})
        if sup:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi), hist


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


# ---------------------------------------------------------------------------
# gamma ladder
# ---------------------------------------------------------------------------
def gamma_at_grid(a_star, n, eps_targets):
    """Supercritical scan + honest log-log fit at one grid depth."""
    rows = []
    for eps in eps_targets:
        diag, _ = run_amplitude(a_star + eps, n=n)
        ok = diag.ah_found and np.isfinite(diag.m_ah) and diag.m_ah > 0
        rows.append({
            "A": round(a_star + eps, 8), "eps": float(eps),
            "M_code": float(diag.m_ah) if ok else float("nan"),
            "stop": diag.stopped_reason,
            "sane": bool(ok and 0 < diag.m_ah < M_SANE_MAX),
        })
        print(f"      N={n:<5} eps = {eps:9.3e}  M = "
              f"{rows[-1]['M_code']:12.5e}  [{rows[-1]['stop']}]", flush=True)
    fit_rows = [r for r in rows if r["sane"] and not r["stop"].startswith("junk")]
    gamma = err = r2 = None
    if len(fit_rows) >= 4:
        x = np.log10([r["eps"] for r in fit_rows])
        y = np.log10([r["M_code"] for r in fit_rows])
        (g, C), resid, *_ = np.polyfit(x, y, 1, cov=True)
        err = float(np.sqrt(resid[0][0])) if np.ndim(resid) == 2 else float("nan")
        yhat = C + g * x
        ss_res = float(np.sum((y - yhat) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        gamma = float(g)
    floor = min((r["M_code"] for r in fit_rows), default=None)
    return {"gamma_eff": gamma, "gamma_err": err, "r2": r2,
            "n_fit_rows": len(fit_rows), "n_runs": len(rows),
            "floor_M": floor, "rows": rows,
            "gamma_Ch_anchor": gamma_Ch}


# ---------------------------------------------------------------------------
# delta ladder
# ---------------------------------------------------------------------------
def delta_at_grid(a_star, n, eps_echo_list):
    """Echo detector at one grid depth (same estimator as C3)."""
    results = []
    for eps in eps_echo_list:
        diag, sol = run_amplitude(a_star + eps, n=n, monitor_every=1)
        vs, qs = [], []
        for sn in getattr(sol, "snapshots", []):
            r = np.asarray(sn["r"], dtype=float)
            q = np.asarray(sn["two_m_over_r"], dtype=float)
            keep = np.isfinite(q) & np.isfinite(r) & (r > 0)
            if keep.any():
                vs.append(float(sn["v"]))
                qs.append(float(np.max(q[keep])))
        vs, qs = np.array(vs), np.array(qs)
        v_star = float(diag.v_ah) if diag.ah_found else float(vs[-1])
        peaks = [i for i in local_maxima(qs)
                 if vs[i] < v_star - 1e-4 and vs[i] > vs[0] + 1e-6]
        xs = [math.log(v_star - vs[i]) for i in peaks]
        dx = np.diff(xs) if len(xs) >= 3 else np.array([])
        delta = float(-np.mean(dx)) if len(dx) else None
        dstd = float(np.std(dx)) if len(dx) else None
        res = {
            "N": n, "eps_echo": eps, "n_snapshots": len(vs),
            "v_star_proxy": round(v_star, 6),
            "ah_found": bool(diag.ah_found),
            "n_peaks": len(peaks),
            "peak_v": [round(float(vs[i]), 5) for i in peaks],
            "ln_time_x": [round(x, 4) for x in xs],
            "delta_eff": delta,
            "delta_eff_std": dstd,
        }
        results.append(res)
        print(f"      N={n:<5} eps={eps:.1e}: v*={v_star:.4f}, "
              f"{res['n_peaks']} peaks, "
              f"Delta_eff = {delta if delta is None else round(delta, 3)} "
              f"+- {dstd if dstd is None else round(dstd, 3)}", flush=True)
    return results


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-delta", action="store_true",
                    help="run the gamma ladder only")
    ap.add_argument("--N-deep", type=int, default=3200,
                    help="deepest grid of the ladder (default 3200)")
    args = ap.parse_args()

    t0 = time.time()
    print("=" * 72)
    print("COLLAPSE-HAWKING BRIDGE — CAMPAIGN C3b (concentrated resolution)")
    print("=" * 72)
    a_star_800 = load_a_star()
    print(f"A* (committed C1, N=800) = {a_star_800:.8f}  [cross-reference only]")
    print("'adaptive' = resolution CONCENTRATED on the critical window;\n"
          "no AMR rewrite of the engine is implied or claimed.")
    print("F-2 remediation: each grid uses its OWN freshly bisected A*_N.")

    grids = (1600, args.N_deep)

    print("\n[0/3] per-grid critical amplitudes A*_N ...")
    a_star_per_grid = {}
    for n in grids:
        tA = time.time()
        a_n, hist = bisect_a_star(n)
        a_star_per_grid[f"N{n}"] = {
            "a_star": a_n, "iters": len(hist),
            "wall_s": round(time.time() - tA, 1),
            "drift_from_N800": a_n - a_star_800,
        }
        print(f"      N={n:<5} A*_N = {a_n:.8f}  "
              f"(drift vs N800: {a_n - a_star_800:+.2e}; "
              f"{time.time() - tA:.0f} s)", flush=True)

    print("\n[1/3] gamma ladder (narrow band, deep grids)...")
    gamma_ladder = {}
    eps_by_grid = {
        1600: np.logspace(-1.5, -3.8, 7),
        args.N_deep: np.logspace(-1.5, -3.5, 5),
    }
    for n in grids:
        print(f"  --- N = {n} ---")
        a_n = a_star_per_grid[f"N{n}"]["a_star"]
        entry = gamma_at_grid(a_n, n, eps_by_grid[n])
        entry["a_star_used"] = a_n
        gamma_ladder[f"N{n}"] = entry
        g = gamma_ladder[f"N{n}"]
        print(f"      fit: gamma_eff = "
              f"{g['gamma_eff'] if g['gamma_eff'] is None else round(g['gamma_eff'], 4)} "
              f"+- {g['gamma_err'] if g['gamma_err'] is None else round(g['gamma_err'], 4)} "
              f"(r2 = {g['r2'] if g['r2'] is None else round(g['r2'], 3)}), "
              f"floor_M = "
              f"{g['floor_M'] if g['floor_M'] is None else format(g['floor_M'], '.4e')}")

    delta_ladder = {}
    delta_eff = None
    if not args.skip_delta:
        print("\n[2/3] delta ladder (echo detector, deep grids)...")
        eps_by_grid_d = {
            1600: [1e-3, 3e-4],
            args.N_deep: [3e-4, 1e-4],
        }
        for n in grids:
            print(f"  --- N = {n} ---")
            delta_ladder[f"N{n}"] = delta_at_grid(
                a_star_per_grid[f"N{n}"]["a_star"], n, eps_by_grid_d[n])
        deltas = [r["delta_eff"] for rows in delta_ladder.values()
                  for r in rows if r["delta_eff"]]
        if deltas:
            delta_eff = float(np.mean(deltas))
            print(f"      Delta_eff (all resolved runs) = {delta_eff:.3f} "
                  f"({len(deltas)} runs)")
        else:
            print("      no run resolved >= 3 peaks — honest negative kept")
    else:
        print("\n[2/3] delta ladder SKIPPED (--skip-delta)")

    print("\n[3/3] Verdict...")
    g3200 = gamma_ladder[f"N{args.N_deep}"]
    P_engine = None
    if delta_eff and g3200["gamma_eff"] is not None:
        P_engine = delta_eff * g3200["gamma_eff"]

    def measured_verdict(p):
        """Verdict for a MEASURED product; unmeasurable -> INCONCLUSIVE."""
        if p is None:
            return "INCONCLUSIVE"   # stated, never silent (v2.2.0)
        return ("PASS" if abs(p - DGAMMA_TARGET) < DGAMMA_TOL
                else "OUT-OF-TOLERANCE")

    # v2.2.0: the anchor product is arithmetic over the project's own two
    # anchors — classified, never counted as a physics PASS.
    P_anchor_within_target = bool(abs(DGAMMA_LIT - DGAMMA_TARGET) < DGAMMA_TOL)

    V = {
        "campaign": "chb_c3b",
        "engine": "engine/solver.py — double-null characteristic march (Goursat, RK2-Heun)",
        "project_version": PROJECT_VERSION,
        "units": "4 pi G = 1 (kappa = 2), geometric engine units",
        "family": {"u0": U0, "v_p": V_P, "sigma": SIGMA, "v0": V0,
                   "u_range": [U0, U1], "v_range": [V0, V1]},
        "a_star_N800": a_star_800,
        "a_star_per_grid": a_star_per_grid,
        "method": {
            "definition_of_adaptive": (
                "resolution concentrated on the critical window: deep grids "
                "spend runs only on eps in [1e-1.5, 1e-3.8] around their OWN "
                "threshold and on echo runs nearest threshold; no AMR rewrite "
                "of the engine"),
            "thresholds": (
                "v2.0.1 F-2 remediation: eps is measured from the per-grid "
                "A*_N (freshly bisected at tol 2e-6), NOT from A*_N800; the "
                "2.0.0 release reused A*_N800 for the deep grids, mislabeling "
                "the eps axis by +2.8e-3 at N=1600 and biasing gamma_eff to "
                "~0.11 (audit finding F-2 / IVP-11)"),
            "motivation": ("fixed-grid mass floor drops with resolution — "
                           "the C3 'gamma unmeasurable' verdict is a floor "
                           "statement, and the floor is a knob"),
        },
        "gamma_ladder": gamma_ladder,
        "delta_ladder": delta_ladder,
        "delta_eff": delta_eff,
        "products": {
            "P_anchor": DGAMMA_LIT,
            "P_anchor_class": ("anchor arithmetic — both factors are "
                               "literature/engine anchors; consistency with "
                               "the target, NOT a measurement"),
            "P_anchor_verdict": "ANCHOR_ARITHMETIC",
            "P_anchor_within_target": P_anchor_within_target,
            "P_engine_deep": P_engine,
            "P_engine_deep_verdict": measured_verdict(P_engine),
            "target": {"value": DGAMMA_TARGET, "tolerance": DGAMMA_TOL,
                       "frozen_by": "PREREGISTRATION.md (v2.2.0)"},
        },
        "honest_notes": {
            "stop_criterion": ("deep-grid rows near threshold may stop with "
                               "'AH mass saturated'; M_ah is recorded and the "
                               "row stays in the fit set only if sane"),
            "delta": ("delta_eff is an EFFECTIVE period from 40 snapshots "
                      "per run; the DSS verdict of C3 is not overwritten by "
                      "this campaign, only supplemented"),
            "anchors": ("gamma_Ch and echo_delta remain comparison anchors, "
                        "never fit targets"),
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "wall_total_s": None,
    }
    V["wall_total_s"] = time.time() - t0

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "c3b_verdict.json"), "w") as f:
        json.dump(V, f, indent=1)
    with open(os.path.join(OUT, "c3b_gamma_ladder.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["N", "A", "eps", "M_code", "stop", "sane"])
        for n in grids:
            for r in gamma_ladder[f"N{n}"]["rows"]:
                w.writerow([n, r["A"], r["eps"], r["M_code"], r["stop"],
                            r["sane"]])

    print(f"      P_anchor     = {DGAMMA_LIT:.5f} -> "
          f"{V['products']['P_anchor_verdict']}")
    print(f"      P_engine_deep = "
          f"{P_engine if P_engine is None else round(P_engine, 5)} -> "
          f"{V['products']['P_engine_deep_verdict']}")
    print(f"\nDONE in {V['wall_total_s']:.1f} s -> campaigns/reference/c3b_verdict.json")


if __name__ == "__main__":
    main()
