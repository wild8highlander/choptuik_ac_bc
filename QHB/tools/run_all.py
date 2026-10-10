#!/usr/bin/env python3
"""Run all QHB campaigns C1-C12 and write data/*.json tables.

Deterministic: fixed seeds, no wall-clock, no randomness beyond pinned seeds.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from qhb import (asymmetry, claims, competing, constants as C, core,
                 phase_map, vortex)
from qhb.pins import (C5_N_TRIALS, C5_SEED, C11_AREF_A0, C11_AREF_DELTA,
                      C11_AREF_DT, C11_AREF_T, C11_AREF_THETA, C11_ROT_DT,
                      C11_ROT_T, C12_FILL_RATE, C12_FILL_SEED)

DATA = ROOT / "data"


def dump(name: str, obj) -> None:
    DATA.mkdir(exist_ok=True)
    (DATA / name).write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n",
                             encoding="utf-8")
    print(f"  wrote data/{name}")


def main() -> None:
    # ---- C1 ---------------------------------------------------------------
    print("C1 gap_finite_volume")
    betas9 = [round(2.80 + 0.21875 * i, 6) for i in range(9)]
    volumes = [6, 8, 10, 12, 16, 20, 24, 28, 32]
    t = core.c1_gap_table(betas9, volumes)
    dump("c1_gap_grid.json", t)

    # ---- C2 ---------------------------------------------------------------
    print("C2 string_tension")
    loops = [(1, 1), (1, 2), (2, 1), (2, 2), (3, 2), (4, 3)]
    scan = []
    for b in betas9:
        s = core.sigma_measure(b, loops)
        scan.append({"beta": b, "sigma_meas": s,
                     "sigma_law": C.sigma_of_beta(b),
                     "abs_dev": abs(s - C.sigma_of_beta(b))})
    dump("c2_sigma_scan.json", {"loops": loops, "scan": scan,
                                "max_dev": max(r["abs_dev"] for r in scan),
                                "sigma_star": C.SIGMA_STAR})

    # ---- C3 ---------------------------------------------------------------
    print("C3 bridge_thermal")
    spin = core.spin_constants_exact(100)
    bscan = []
    for b in betas9:
        base = core.bridge_temperature(b, corrections=False)
        full = core.bridge_temperature(b, corrections=True)
        bscan.append({"beta": b, "T_base": base, "T_full": full,
                      "correction_pct": 100 * (full / base - 1)})
    dump("c3_spin_constants.json", spin)
    dump("c3_bridge_scan.json", {"scan": bscan,
                                 "correction_at_star_pct":
                                     100 * (core.bridge_temperature(C.BETA_STAR) /
                                            core.bridge_temperature(C.BETA_STAR, False) - 1)})

    # ---- C4 ---------------------------------------------------------------
    print("C4 detector_response")
    dump("c4_tail_audit.json", core.c4_tail_audit(C.BETA_STAR))

    # ---- C5 ---------------------------------------------------------------
    print("C5 free_three_body")
    r5 = core.free_three_body(C5_N_TRIALS, C5_SEED)
    r5["e_th_pinned"] = r5["e_th"]
    dump("c5_free_three_body.json", r5)

    # ---- C6 ---------------------------------------------------------------
    print("C6 confined_spectrum")
    shapes = [(1, 1, 1), (1.2, 1, 1), (1.5, 1, 1), (1, 1.2, 1), (1, 1, 1.2),
              (1.5, 1.5, 1), (2, 1.5, 1.5), (2, 2, 1), (2, 2, 2)]
    spec = core.y_string_energy(shapes, C.BETA_STAR)
    dump("c6_y_spectrum.json", {"beta": C.BETA_STAR, "sigma": C.SIGMA_STAR,
                                "shapes": spec})

    # ---- C7 ---------------------------------------------------------------
    print("C7 tunneling_window")
    tw = core.tunneling_window()
    tw["S_samples"] = [{"E": e, "S": core.wkb_action(e),
                        "T": math.exp(-2 * core.wkb_action(e))}
                       for e in (0.0, 0.25, 0.5, 1.0, 2.0)]
    dump("c7_wkb_window.json", tw)

    # ---- C8 ---------------------------------------------------------------
    print("C8 bootstrap")
    dump("c8_bootstrap.json", core.c8_bootstrap(betas9))

    # ---- C9 ---------------------------------------------------------------
    print("C9 phase_map")
    betas41 = [round(2.80 + 0.04375 * i, 6) for i in range(41)]
    vols9 = [6, 8, 10, 12, 16, 20, 24, 28, 32]
    pg = phase_map.phase_grid(betas41, vols9)
    pg.pop("cells")  # 369 cells are bulky; keep the summary
    dump("c9_phase_grid.json", pg)
    dump("c9_valley.json", phase_map.valley_refine(betas41))
    dump("c9_naive_falsifier.json", phase_map.naive_falsifier())

    # ---- C10 --------------------------------------------------------------
    print("C10 competing_models")
    sh = competing.fit_shares()
    dump("c10_shares.json", sh)
    dump("c10_braking.json", {"B2_real": competing.braking_estimator_B2(),
                              "B2_control": competing.braking_estimator_control()})
    dump("c10_out_of_window.json", competing.out_of_window_residual())

    # ---- C11 --------------------------------------------------------------
    print("C11 vortex_anchor")
    rot = vortex.rigid_rotation_check(C11_ROT_DT, C11_ROT_T)
    dump("c11_rotation.json", rot)
    aref = vortex.aref_boundedness(C11_AREF_A0, C11_AREF_DELTA, C11_AREF_T,
                                   C11_AREF_DT, theta=C11_AREF_THETA)
    dump("c11_aref_run.json", aref)
    # barrier scan + escape scan
    ss = [round(0.05 * i, 4) for i in range(0, 61)]
    dump("c11_barrier_scan.json",
         {"s": ss, "V": [vortex.anchored_potential(s) for s in ss],
          "V_star": C.V_STAR})
    esc = vortex.anchored_escape_scan(300)
    dump("c11_escape_scan.json", esc)
    # spectrum: numeric eigenvalues of the exact corotating Jacobian
    import sympy as sp
    x1, y1, x2, y2, x3, y3 = sp.symbols('x1 y1 x2 y2 x3 y3', real=True)
    pts = [(x1, y1), (x2, y2), (x3, y3)]
    F = []
    for i in range(3):
        xi, yi = pts[i]
        vx = vy = sp.Integer(0)
        for j in range(3):
            if i == j:
                continue
            xj, yj = pts[j]
            r2 = (xi - xj) ** 2 + (yi - yj) ** 2
            vx += -(yi - yj) / r2 / (2 * sp.pi)
            vy += (xi - xj) / r2 / (2 * sp.pi)
        F += [vx, vy]
    vec = sp.Matrix([x1, y1, x2, y2, x3, y3])
    R3 = 1 / sp.sqrt(3)
    eq = [R3, 0, -R3 / 2, sp.sqrt(3) * R3 / 2, -R3 / 2, -sp.sqrt(3) * R3 / 2]
    J = sp.Matrix(F).jacobian(vec).subs(dict(zip(vec, eq)))
    K = sp.Matrix([[0, 1], [-1, 0]])
    K6 = sp.Matrix.vstack(sp.Matrix.hstack(K, sp.zeros(2), sp.zeros(2)),
                          sp.Matrix.hstack(sp.zeros(2), K, sp.zeros(2)),
                          sp.Matrix.hstack(sp.zeros(2), sp.zeros(2), K))
    A = J + (sp.Rational(3, 1) / (2 * sp.pi)) * K6
    lam = sp.symbols('lam')
    cp = sp.factor(sp.together(A.charpoly(lam).as_expr()))
    ev = sp.solve(cp, lam)
    dump("c11_spectrum.json",
         {"charpoly": sp.sstr(cp),
          "eigenvalues": [sp.sstr(sp.nsimplify(e)) for e in ev],
          "omega": sp.sstr(sp.Rational(3, 1) / (2 * sp.pi)),
          "unique_nonzero": "+-i*omega (double degeneracy)"})

    # ---- C12 --------------------------------------------------------------
    print("C12 asymmetry_lock")
    dump("c12_profiles.json", asymmetry.profiles())
    pg12 = asymmetry.phase_grid_eta(41)
    pg12["cells"] = [{"eta": c["eta"], "barrier": c["barrier"],
                      "status": c["status"]} for c in pg12["cells"]]
    dump("c12_phase_grid.json", pg12)
    dump("c12_margin.json", asymmetry.asymmetry_margin())
    fd_eta = asymmetry.fill_dynamics(eta=C.ETA_B, seed=C12_FILL_SEED,
                                     rate_scale=C12_FILL_RATE)
    fd_ctl = asymmetry.fill_dynamics(eta=0.5, n_steps=200_000, seed=C12_FILL_SEED,
                                     rate_scale=C12_FILL_RATE)
    dump("c12_fill_dynamics.json", {"at_eta_B": fd_eta, "control_eta_0.5": fd_ctl})
    dump("c12_nugget_bound.json", asymmetry.nugget_bound())
    dump("c12_summary.json", asymmetry.c12_summary())

    # ---- claims -----------------------------------------------------------
    print("Evidence Engine")
    reg = claims.claims_registry()
    dump("claims.json", {"claims": reg,
                         "summary": claims.claims_summary(reg)})

    print("done.")


if __name__ == "__main__":
    main()
