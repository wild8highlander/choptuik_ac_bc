#!/usr/bin/env python3
"""
Campaign C3 — the Delta*gamma invariant check.

Target: the project hypothesis  Delta * gamma ~= 1.27, where
  Delta  — the echoing period of near-critical collapse (DSS scale),
  gamma  — the black-hole mass-scaling exponent  M ~ eps^gamma.

Three products are computed and reported with EXPLICIT semantics
(v2.2.0 reclassification, external audit point 10):

  P_anchor  = Delta_lit * gamma_Ch  = 3.44 * 0.374 = 1.28656
              ANCHOR ARITHMETIC: both factors are literature/engine
              anchors, so comparing P_anchor with the target 1.27 is a
              consistency statement about the project's own constants,
              NOT a measurement and NOT a physics test.  Verdict token:
              ANCHOR_ARITHMETIC (+ boolean P_anchor_within_target).
  P_engine  = Delta_eff * gamma_eff (both measured by THIS engine in
              this run; floor-biased at fixed grid — honest caveat)
  P_mixed   = Delta_eff * gamma_Ch  (measured period, anchor exponent)

  P_engine / P_mixed are the only physical tests.  When a factor is not
  measurable at the committed resolution (gamma floor-dominated, fewer
  than three resolved echo peaks), the product is reported INCONCLUSIVE
  — never silent, never replaced by the anchor arithmetic.

Acceptance: |P - 1.27| < DGAMMA_TOL (0.05).  The target and the tolerance
are FROZEN by PREREGISTRATION.md since v2.2.0; they were chosen post hoc
in v1.x and any future change is a CHANGELOG event with a retro-label.

Measurements
------------
gamma_eff : supercritical amplitude scan at N (default 800) around the
            committed A*_N800; weighted log-log fit over completed,
            sane, above-floor rows; the fit is stated WITH its floor
            caveat (fixed-grid floor dominates the smallest eps).
Delta_eff : echo detector.  A near-critical supercritical run
            (A = A* + eps_echo, monitor_every=1) is marched; the
            compactness proxy  q(v) = max_r(2m/r)  is recorded per
            v-row; local maxima of q(v) give spacings dv; the effective
            echo period is their mean.  Repeated for several eps_echo.

Run:   python3 campaigns/run_c3.py            (quick, ~1-2 min)
       python3 campaigns/run_c3.py --N 1200   (deeper scan)
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, os.path.join(ROOT, "chbridge"))
from constants import DGAMMA_LIT, DGAMMA_TARGET, DGAMMA_TOL, b_Ch, echo_delta, gamma_Ch
from solver import DoubleNullSolver, GaussianPulseData, SolverConfig

OUT = os.path.join(ROOT, "campaigns", "reference")

with open(os.path.join(ROOT, "VERSION")) as _f:
    PROJECT_VERSION = _f.read().strip()

U0, V0 = -1.0, 0.0
V_P, SIGMA = 0.5, 0.1
U1, V1 = 1.05, 1.0


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


# ---------------------------------------------------------------------------
# gamma_eff
# ---------------------------------------------------------------------------
def measure_gamma(a_star, n, n_points=16):
    """Supercritical scan + honest log-log fit; returns (gamma, err, rows).

    Fit dataset: ALL sane rows (any non-junk stop reason) with
    eps < 3e-2 — saturation is a property of the stop criterion, not of
    the formed mass; junk rows (overflowing masses) are excluded by the
    sane flag.  The result carries the fixed-grid floor caveat."""
    eps_targets = np.logspace(-1.0, -4.2, n_points)
    rows = []
    for eps in eps_targets:
        diag, _ = run_amplitude(a_star + eps, n=n)
        ok = diag.ah_found and np.isfinite(diag.m_ah) and diag.m_ah > 0
        rows.append({
            "A": round(a_star + eps, 8), "eps": float(eps),
            "M_code": float(diag.m_ah) if ok else float("nan"),
            "stop": diag.stopped_reason,
            "sane": bool(ok and 0 < diag.m_ah < 0.1),
        })
        print(f"      eps = {eps:9.3e}  M = {rows[-1]['M_code']:12.5e}  "
              f"[{rows[-1]['stop']}]", flush=True)
    fit_rows = [r for r in rows if r["sane"] and not r["stop"].startswith("junk")
                and r["eps"] < 3e-2]
    gamma = err = r2 = None
    if len(fit_rows) >= 5:
        x = np.log10([r["eps"] for r in fit_rows])
        y = np.log10([r["M_code"] for r in fit_rows])
        (g, C), resid, *_ = np.polyfit(x, y, 1, cov=True)
        err = float(np.sqrt(resid[0][0])) if np.ndim(resid) == 2 else float("nan")
        yhat = C + g * x
        ss_res = float(np.sum((y - yhat) ** 2))
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        gamma = float(g)
    return gamma, err, r2, rows


# ---------------------------------------------------------------------------
# Delta_eff — echo detector
# ---------------------------------------------------------------------------
def local_maxima(q, min_prominence=2e-3):
    """Indices of local maxima of a 1-d series with simple prominence test."""
    idx = []
    for i in range(1, len(q) - 1):
        if q[i] >= q[i - 1] and q[i] > q[i + 1]:
            # prominence: highest neighbour valley on both sides
            left = min(q[max(0, i - 40):i + 1])
            right = min(q[i:i + 41]) if i + 41 < len(q) else min(q[i:])
            if q[i] - max(left, right) >= min_prominence * max(1e-12, abs(q[i])):
                idx.append(i)
    return idx


def measure_delta(a_star, n, eps_echo_list):
    """Echo detector in LOG time, as DSS requires.

    For a near-critical supercritical run the DSS ansatz predicts that
    the echo peaks of any central quantity occur at
        v* - v_k = C * exp(-k * Delta),
    so the spacings of  x_k = ln(v* - v_k)  between successive peaks
    directly estimate Delta.  The accumulation time v* is taken as the
    apparent-horizon formation time v_ah of the same run (v_ah -> v* as
    eps -> 0).  Only peaks with v_k < v_ah and v_ah - v_k > 1e-4 are
    used; the raw-v spacings are kept for reference but NOT used in the
    estimate (raw-v spacings shrink geometrically and are not Delta).
    """
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
        # in log-time the peaks march DOWNWARD; Delta = -mean(dx)
        delta = float(-np.mean(dx)) if len(dx) else None
        dstd = float(np.std(dx)) if len(dx) else None
        raw = np.diff(vs[peaks]) if len(peaks) >= 3 else np.array([])
        res = {
            "eps_echo": eps, "n_snapshots": len(vs),
            "v_star_proxy": round(v_star, 6),
            "ah_found": bool(diag.ah_found),
            "n_peaks": len(peaks),
            "peak_v": [round(float(vs[i]), 5) for i in peaks],
            "ln_time_x": [round(x, 4) for x in xs],
            "delta_eff": delta,
            "delta_eff_std": dstd,
            "raw_v_spacings": [round(float(s), 5) for s in raw],
        }
        results.append(res)
        print(f"      eps={eps:.1e}: v*={v_star:.4f}, {res['n_peaks']} peaks, "
              f"Delta_eff = {delta if delta is None else round(delta, 3)} "
              f"+- {dstd if dstd is None else round(dstd, 3)}",
              flush=True)
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=800)
    ap.add_argument("--scan-points", type=int, default=12)
    ap.add_argument("--eps-echo", type=float, nargs="*",
                    default=[1e-3, 3e-4, 1e-4])
    args = ap.parse_args()

    t0 = time.time()
    print("=" * 72)
    print("COLLAPSE-HAWKING BRIDGE — CAMPAIGN C3 (Delta*gamma invariant)")
    print("=" * 72)
    a_star = load_a_star()
    print(f"A* (committed C1, N=800) = {a_star:.8f}")

    print(f"\n[1/3] gamma_eff: supercritical scan at N={args.N}...")
    gamma_eff, gamma_err, r2, scan_rows = measure_gamma(
        a_star, args.N, args.scan_points)
    if gamma_eff is not None:
        print(f"      fit: gamma_eff = {gamma_eff:.3f} +- {gamma_err:.3f} "
              f"(r2 = {r2:.3f})  — floor-biased, anchor gamma_Ch = {gamma_Ch}")

    print(f"\n[2/3] Delta_eff: echo detector at N={args.N}...")
    delta_rows = measure_delta(a_star, args.N, args.eps_echo)
    deltas = [r["delta_eff"] for r in delta_rows if r["delta_eff"]]
    delta_eff = float(np.mean(deltas)) if deltas else None
    delta_std = float(np.std(deltas)) if len(deltas) > 1 else (
        delta_rows[0]["delta_eff_std"] if delta_rows else None)

    print("\n[3/3] Verdict...")
    P_anchor = DGAMMA_LIT                      # 3.44 * 0.374 = 1.28656
    P_engine = (delta_eff * gamma_eff
                if (delta_eff and gamma_eff is not None) else None)
    P_mixed = (delta_eff * gamma_Ch if delta_eff else None)

    def measured_verdict(p):
        """Verdict for a MEASURED product (both factors engine data)."""
        if p is None:
            return "INCONCLUSIVE"   # unmeasurable factor — stated, never silent
        return ("PASS" if abs(p - DGAMMA_TARGET) < DGAMMA_TOL
                else "OUT-OF-TOLERANCE")

    # v2.2.0: the anchor product is arithmetic over the project's own two
    # anchors.  It is classified, never counted as a physics PASS.
    P_anchor_within_target = bool(abs(P_anchor - DGAMMA_TARGET) < DGAMMA_TOL)

    V = {
        "campaign": "chb_c3",
        "engine": "engine/solver.py — double-null characteristic march (Goursat, RK2-Heun)",
        "project_version": PROJECT_VERSION,
        "units": "4 pi G = 1 (kappa = 2), geometric engine units",
        "grid": {"N": args.N},
        "a_star_N800": a_star,
        "gamma": {
            "gamma_eff": gamma_eff, "gamma_err": gamma_err, "r2": r2,
            "gamma_Ch_anchor": gamma_Ch,
            "honest_note": ("fixed-grid mass floor dominates the smallest eps; " +
                            "gamma_eff is a floor-biased honest measurement, " +
                            "NOT a precision determination"),
        },
        "delta": {
            "delta_eff": delta_eff, "delta_eff_std": delta_std,
            "delta_lit": echo_delta, "delta_lit_err": 0.02,
            "per_eps_rows": delta_rows,
            "honest_note": ("fixed-grid verdict is NOT-DSS (no exact discrete " +
                            "self-similarity); delta_eff is an EFFECTIVE period"),
        },
        "products": {
            "P_anchor": P_anchor,
            "P_anchor_class": ("anchor arithmetic — both factors are " +
                               "literature/engine anchors; consistency with " +
                               "the target, NOT a measurement"),
            "P_anchor_verdict": "ANCHOR_ARITHMETIC",
            "P_anchor_within_target": P_anchor_within_target,
            "P_anchor_deviation": abs(P_anchor - DGAMMA_TARGET),
            "P_engine": P_engine,
            "P_engine_verdict": measured_verdict(P_engine),
            "P_mixed": P_mixed,
            "P_mixed_verdict": measured_verdict(P_mixed),
            "verdict_semantics": (
                "ANCHOR_ARITHMETIC = consistency of the project's own anchors " +
                "with the frozen target (not evidence); PASS/OUT-OF-TOLERANCE " +
                "= measured product inside/outside the frozen tolerance; " +
                "INCONCLUSIVE = a factor is unmeasurable at this resolution " +
                "(never silent).  Falsification criteria: PREREGISTRATION.md."),
        },
        "scan_rows": scan_rows,
        "target": {"value": DGAMMA_TARGET, "tolerance": DGAMMA_TOL,
                   "frozen_by": "PREREGISTRATION.md (v2.2.0)"},
        "b_Ch_crosscheck": b_Ch,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "wall_total_s": None,
    }
    print(f"      P_anchor = {P_anchor:.5f}  -> "
          f"{V['products']['P_anchor_verdict']} "
          f"(within target: {P_anchor_within_target})")
    print(f"      P_mixed  = "
          f"{P_mixed if P_mixed is None else round(P_mixed, 5)}  -> "
          f"{V['products']['P_mixed_verdict']}")
    print(f"      P_engine = "
          f"{P_engine if P_engine is None else round(P_engine, 5)}  -> "
          f"{V['products']['P_engine_verdict']}")
    print(f"      target = {DGAMMA_TARGET} +- {DGAMMA_TOL}")

    V["wall_total_s"] = time.time() - t0
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "c3_verdict.json"), "w") as f:
        json.dump(V, f, indent=1)
    print(f"\nDONE in {V['wall_total_s']:.1f} s -> campaigns/reference/c3_verdict.json")


if __name__ == "__main__":
    main()
