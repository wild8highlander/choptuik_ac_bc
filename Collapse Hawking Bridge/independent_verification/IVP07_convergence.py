#!/usr/bin/env python3
"""
IVP-07 — independent method-of-convergence test of the engine.

The verifier evolves the INDEPENDENT Roberts-Oshiro data (own formulas,
verifier-chosen window u in (-0.25, 0.75), v in (1.1, 1.9), sigma = 0.12
— deliberately NOT the engine test window) and measures, at the final
row v_final:

    E_N^r   = max_u |r_num(u, v_final) - r_exact(u, v_final)|
    E_N^Phi = max_u |Phi_num - Phi_exact| / max |Phi_exact|

then determines the observed order ITSELF:

    p_N = log2(E_N / E_2N)

Pre-registered criteria (RK2-Heun engine):
    C1: p_N in [1.8, 2.3] for every consecutive doubling;
    C2: E_200^r < 1e-4;
    C3: error decreases monotonically along the ladder.

The committed engine validation numbers are loaded ONLY in the final
comparison phase; because the verifier window/sigma differ, agreement
with them is expected in ORDER and MAGNITUDE, not in digits.
"""
import math
import os
import sys

import numpy as np

IVP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(IVP_DIR)
sys.path.insert(0, IVP_DIR)
from ivp_common import (
    load_engine,
    log,
    make_independent_roberts,
    read_committed_verdict,
    save_result,
    worst_status,
)

SIGMA = 0.12          # verifier-chosen (different from engine's 0.1 test)
U_BOX = (-0.25, 0.75) # verifier-chosen window
V_BOX = (1.1, 1.9)
LADDER = [100, 200, 400, 800, 1600]


def main():
    log("=" * 72)
    log("IVP-07 — method-of-convergence test (blind order determination)")
    log("=" * 72)

    S = load_engine()
    IndepRoberts = make_independent_roberts(S)
    data = IndepRoberts(sigma=SIGMA)

    rows = []
    log(f"\n[A] blind ladder, sigma = {SIGMA}, box u{U_BOX} x v{V_BOX}")
    for n in LADDER:
        cfg = S.SolverConfig(n_u=n, n_v=n, u_range=U_BOX, v_range=V_BOX,
                             monitor_every=max(1, n // 8))
        sol = S.DoubleNullSolver(cfg, data)
        diag = sol.run(verbose=False)
        v_f = sol.v_final
        r_ex, Phi_ex, _, _, _, _ = data.fields(sol.u, np.full_like(sol.u, v_f))
        scale = max(float(np.max(np.abs(Phi_ex))), 1e-300)
        row = {
            "n": n, "v_final": float(v_f),
            "err_r": float(np.max(np.abs(sol.r - r_ex))),
            "err_Phi_rel": float(np.max(np.abs(sol.Phi - Phi_ex)) / scale),
            "err_alpha2": float(np.max(np.abs(sol.alpha2 - 1.0))),
            "c1_max": float(diag.c1_max), "c2_max": float(diag.c2_max),
            "mdef_max": float(diag.mdef_max),
        }
        rows.append(row)
        log(f"    N={n:<5} err_r = {row['err_r']:.3e}  "
            f"err_Phi_rel = {row['err_Phi_rel']:.3e}  "
            f"err_alpha2 = {row['err_alpha2']:.3e}")

    log("\n[B] verifier-determined convergence order")
    for a, b in zip(rows[:-1], rows[1:]):
        p = math.log2(a["err_r"] / b["err_r"]) if b["err_r"] > 0 else float("inf")
        b["p_r"] = p
        log(f"    N {a['n']:>4} -> {b['n']:<4} p_r = {p:.3f}")

    orders = [r["p_r"] for r in rows[1:]]
    checks = {
        "C1_order_in_[1.8,2.3]": all(1.8 <= p <= 2.3 for p in orders),
        "C2_err200_below_1e-4": rows[1]["err_r"] < 1e-4,
        "C3_monotone_decrease": all(a["err_r"] > b["err_r"]
                                    for a, b in zip(rows[:-1], rows[1:])),
    }
    for k, v in checks.items():
        log(f"    [{'OK ' if v else 'FAIL'}] {k}")

    # ------------------------------------------------------------------
    # [COMPARISON PHASE] committed engine validation (different window!)
    # ------------------------------------------------------------------
    log("\n[C] comparison phase — committed validation block (c1_verdict)")
    committed = read_committed_verdict("c1_verdict.json").get("validation", [])
    comp_rows = []
    for c in committed:
        mine = next((r for r in rows if r["n"] == c["n"]), None)
        if mine:
            comp_rows.append({
                "n": c["n"],
                "committed_err_r": c["err_r"], "ivp_err_r": mine["err_r"],
                "committed_p": c.get("convergence_order_r"),
                "note": "windows differ (verifier sigma/window are own choice); " +
                        "comparison is order-and-magnitude only",
            })
            log(f"    N={c['n']}: committed err_r = {c['err_r']:.3e}, "
                f"IVP err_r = {mine['err_r']:.3e} "
                f"(same order of magnitude: "
                f"{10 ** abs(np.log10(mine['err_r'] / c['err_r'])) < 100})")

    status = worst_status(["PASS" if v else "FAIL" for v in checks.values()])
    log(f"\nIVP-07 overall: {status}   orders = "
        f"{[round(p, 3) for p in orders]}")
    save_result("IVP07", {
        "status": status,
        "pre_registered": {
            "window": {"sigma": SIGMA, "u_box": U_BOX, "v_box": V_BOX},
            "criteria": {
                "C1": "verifier-determined order p_N in [1.8, 2.3] per doubling",
                "C2": "err_r(N=200) < 1e-4",
                "C3": "monotone decrease along the ladder",
            },
        },
        "ladder": rows,
        "orders": orders,
        "comparison_vs_committed": comp_rows,
        "checks": checks,
    })
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
