"""
campaign C11 — the vortex anchor and the static barrier (v1.2.0).

The trap physics of the package rests on T4 (the Newtonian equilateral
solution is UNSTABLE — Gascheau) and T6 (the oscillating wall seals).
This campaign adds the classical contrast layer and the first EXACT
confinement statement of the package.  Four blocks:

  B1 — T11 (exact): the stability contrast.  The SAME equilateral
     triangle that is linearly unstable under 1/r attraction (T4) is a
     rigidly rotating relative equilibrium of the classical three-vortex
     problem (Kirchhoff 1876) with omega = Gamma_tot/(2 pi a^2), and its
     corotating-frame linearization is NEUTRAL: the exact analytic
     Jacobian has spectrum {0, 0, +-i omega, +-i omega} — every
     eigenvalue on the imaginary axis or at the origin.  Machine gates:
     max |Re| on the +-i omega pairs < 1e-12; the characteristic
     polynomial identity lambda^2 (lambda^2 + omega^2)^2 to 1e-12; the
     zero pair at solver-noise magnitude (< 1e-6).  Reading for H4:
     "three-ness" does not create the escape channel — the INTERACTION
     decides; the trap is a property of the physics, not of the triangle.

  B2 — T11 (measured): the rigid rotation.  Three full rotations of the
     triangle: rigidity (pairwise distances constant), invariants
     I, H, P, Q conserved, measured omega = exact to RK4 error.

  B3 — T12 (measured): the invariant wall.  The mixed-sign (1,1,-1)
     right-isosceles launch sits EXACTLY on the classical Aref (1979)
     collapse manifold I = H = P = Q = 0 (machine zeros at launch) and
     evolves NON-rigidly while all four invariants stay pinned and the
     orbit stays BOUNDED WITHOUT ANY WALL on the committed horizon
     (t = 12): max radius ~ 2.8 << R_ESC = 12.  Confinement by invariants
     — the topological complement of the geometric wall.  Honest scope:
     the manifold is measure-zero; the collapse separatrix itself is
     classical (Aref 1979) and is NOT integrated.

  B4 — T13 (exact + measured): the static barrier.  With the wall frozen
     (Omega = 0) the engine's total energy IS conserved, and the wall
     potential grows without bound: any solution of the committed
     softened engine obeys the exact radius bound

       r_i(t) <= R_b + w * sqrt( (E0 + 3/sqrt(soft2)) / (2 V0) ),

     hence escape (crossing R_ESC = 12) is IMPOSSIBLE whenever
     V0 > V* = (E0_max + 3/sqrt(soft2)) w^2 / (2 (R_ESC - R_b)^2) = 0.9359
     on the committed band.  The committed C2 cells with V0 >= 1.6 at
     Omega = 0 are therefore exactly sealed — a theorem about the engine
     equations, not a Monte-Carlo frequency.  Measured complements: the
     bound holds with margin on every trial; P_esc = 0/300 at the three
     Omega = 0 cells; energy conserved to solver error; and the HONEST
     complement — at Omega > 0 the wall pumps energy (median |dE| > 0):
     the oscillating seal of C2/C7 is finite-time, the static seal is
     exact.  The stratification:

       V0 >= V* (Omega = 0):  escape impossible (exact, proven)
       V0 <  V* (Omega = 0):  escape allowed by the bound, NOT OBSERVED
                              (0/300 on the committed horizon)
       Omega > 0:             the wall does work; measured finite-time
                              sealing (C2/C7)

The verdict is written to campaigns/reference/c11_verdict.json.
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from engine.solver import (
    N_TRIALS,
    R_ESC,
    SOFT2,
    WALL_R,
    WALL_W,
    make_ensemble,
    total_energy,
    trio_run,
)
from qhb.constants import __version__
from qhb.vortex import (
    aref_launch,
    equilateral_positions,
    invariants_of,
    kirchhoff_run,
    linearize_triangle_exact,
    rotation_angle,
    triangle_shape_error,
)

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "reference")

GAMMA = 1.0
A_SIDE = 1.0
N_ROTS = 3.0
DT_VORTEX = 1e-3
RECORD = 10
T_AREF = 12.0

BAND_EDGES = (-0.6, -0.05)          # the committed C2 ensemble band
STATIC_CELLS = ((0.4, 0.0), (0.8, 0.0), (1.6, 0.0))
OSC_CELL = (0.8, 2.0)               # the wall-work complement


def charpoly_dev(ev, omega):
    """dev of the measured characteristic polynomial against
    lambda^2 (lambda^2 + omega^2)^2."""
    coeffs = np.real(np.poly(ev))
    w2 = omega * omega
    expected = np.array([1.0, 0.0, 2 * w2, 0.0, w2 ** 2, 0.0, 0.0])
    return float(np.abs(coeffs - expected).max())


def main():
    t0 = time.time()
    out = {}

    # ================== B1 — T11 exact: the linearization ==================
    ev, omega_ex, _J = linearize_triangle_exact((GAMMA,) * 3, A_SIDE)
    imag_pairs = [e for e in ev if abs(e.imag) > 1e-6]
    zero_pair = [e for e in ev if abs(e.imag) <= 1e-6]
    re_imag = max(abs(e.real) for e in imag_pairs)
    zero_mag = max(abs(e) for e in zero_pair)
    cp_dev = charpoly_dev(ev, omega_ex)
    b1 = {"omega_exact": omega_ex,
          "spectrum_sorted": [{"re": float(e.real), "im": float(e.imag)}
                              for e in sorted(ev, key=lambda z: (abs(z.imag),
                                                                 abs(z.real)))],
          "max_re_on_imag_pairs": re_imag,
          "zero_pair_max_magnitude": zero_mag,
          "charpoly_identity_dev": cp_dev,
          "jacobian_entries_exact": True}
    b1_ok = bool(re_imag < 1e-12 and cp_dev < 1e-12 and zero_mag < 1e-6)
    print(f"B1/T11 exact: omega = {omega_ex:.12f}; max|Re| (imag pairs) = "
          f"{re_imag:.2e}; zero pair |lambda| = {zero_mag:.2e}; "
          f"char-poly dev = {cp_dev:.2e} -> {'PASS' if b1_ok else 'FAIL'}",
          flush=True)
    out["B1_T11_exact"] = {**b1, "ok": b1_ok}

    # ================== B2 — T11 measured: rigid rotation ==================
    T_period = 2.0 * math.pi / omega_ex
    steps = int(round(N_ROTS * T_period / DT_VORTEX))
    res = kirchhoff_run(equilateral_positions(1.0, A_SIDE),
                        np.array([GAMMA] * 3), dt=DT_VORTEX, steps=steps,
                        record_every=RECORD)
    traj = res["traj"]
    g3 = np.array([GAMMA] * 3)
    inv0 = invariants_of(traj[0], g3)
    inv_drift = {k: 0.0 for k in inv0}
    shape_err = 0.0
    for k in range(traj.shape[0]):
        invk = invariants_of(traj[k], g3)
        for key in inv_drift:
            inv_drift[key] = max(inv_drift[key], abs(invk[key] - inv0[key]))
        shape_err = max(shape_err, triangle_shape_error(traj[k], A_SIDE))
    theta = rotation_angle(traj, GAMMA, A_SIDE)
    t_span = traj.shape[0] and (traj.shape[0] - 1) * RECORD * DT_VORTEX
    omega_meas = theta / t_span
    omega_dev = abs(omega_meas - omega_ex)
    b2 = {"T_period": T_period, "steps": steps, "t_span": t_span,
          "omega_measured": omega_meas, "omega_dev": omega_dev,
          "shape_err_max": shape_err, "invariants_drift": inv_drift}
    b2_ok = bool(omega_dev < 1e-6 and shape_err < 1e-10
                 and max(inv_drift.values()) < 1e-10)
    print(f"B2/T11 rotation: omega_dev = {omega_dev:.2e}; rigidity = "
          f"{shape_err:.2e}; inv drift = {max(inv_drift.values()):.2e} -> "
          f"{'PASS' if b2_ok else 'FAIL'}", flush=True)
    out["B2_T11_rotation"] = {**b2, "ok": b2_ok}

    # ================== B3 — T12: the Aref manifold =========================
    pos_a, gam_a = aref_launch()
    inv_launch = invariants_of(pos_a, gam_a)
    launch_ok = max(abs(v) for v in inv_launch.values()) < 1e-15
    steps_a = int(round(T_AREF / DT_VORTEX))
    res_a = kirchhoff_run(pos_a, gam_a, dt=DT_VORTEX, steps=steps_a,
                          record_every=RECORD)
    traj_a = res_a["traj"]
    drift_a = 0.0
    r_max_a = 0.0
    sep_min = float("inf")
    sep_max = 0.0
    for k in range(traj_a.shape[0]):
        invk = invariants_of(traj_a[k], gam_a)
        drift_a = max(drift_a, max(abs(invk[key] - inv_launch[key])
                                   for key in inv_launch))
        r_max_a = max(r_max_a,
                      float(np.sqrt((traj_a[k] ** 2).sum(axis=1)).max()))
        for i, j in ((0, 1), (0, 2), (1, 2)):
            d = float(np.hypot(*(traj_a[k][i] - traj_a[k][j])))
            sep_min = min(sep_min, d)
            sep_max = max(sep_max, d)
    b3 = {"launch_invariants": inv_launch, "launch_ok": bool(launch_ok),
          "t_horizon": T_AREF, "invariants_drift_max": drift_a,
          "r_max": r_max_a, "R_ESC": R_ESC,
          "separations_min_max": (sep_min, sep_max),
          "rigid": False,
          "traj_decimated": [[round(float(x), 8) for x in row]
                             for row in traj_a[::25].reshape(
                                 traj_a[::25].shape[0], -1)]}
    b3_ok = bool(launch_ok and drift_a < 1e-10 and r_max_a < R_ESC)
    print(f"B3/T12 Aref: launch zeros = {launch_ok}; drift = {drift_a:.2e}; "
          f"r_max = {r_max_a:.6f} << R_ESC = {R_ESC}; seps in "
          f"[{sep_min:.4f}, {sep_max:.4f}] -> {'PASS' if b3_ok else 'FAIL'}",
          flush=True)
    out["B3_T12_manifold"] = {**b3, "ok": b3_ok}

    # ================== B4 — T13: the static barrier ========================
    pos0, vel0, _rejected = make_ensemble()
    E0 = total_energy(pos0, vel0, 0.0, 0.0, 0.0)
    E0_max = float(E0.max())
    pair_floor = 3.0 / math.sqrt(SOFT2)          # softened pair floor (exact)
    V_star = (max(BAND_EDGES) + pair_floor) * WALL_W ** 2 \
        / (2.0 * (R_ESC - WALL_R) ** 2)
    print(f"B4/T13: band [{BAND_EDGES[0]}, {BAND_EDGES[1]}], E0_max = "
          f"{E0_max:.6f}; pair floor = -{pair_floor:.1f}; V* = {V_star:.6f}",
          flush=True)

    cells = []
    E0_abs_max = float(np.abs(E0).max())
    for V0c, Om in STATIC_CELLS:
        run = trio_run(pos0, vel0, V0=V0c, Omega=Om)
        n_esc = int(run["escaped"].sum())
        r_final = run["r_max"]
        bounds = WALL_R + WALL_W * np.sqrt(
            np.maximum(E0 + pair_floor, 0.0) / (2.0 * V0c))
        violation = float(np.max(r_final - bounds))
        margin = float(np.min(bounds - r_final))
        impossible = bounds.max() < R_ESC
        abs_drift = run["E_drift_rel"] * E0_abs_max
        r_meas = float(np.max(r_final))
        cells.append({"V0": V0c, "Omega": Om, "P_esc": n_esc / N_TRIALS,
                      "n_escaped": n_esc,
                      "r_max_final": r_meas,
                      "bound_violation_max": violation,
                      "bound_margin_min": margin,
                      "escape_exactly_impossible": bool(impossible),
                      "E_drift_rel": run["E_drift_rel"],
                      "E_drift_abs_max": abs_drift})
        print(f"  cell V0={V0c} Omega={Om}: P_esc = {n_esc}/{N_TRIALS}; "
              f"r_max(final) = {r_meas:.3f}; "
              f"bound violation = {violation:.2e}; margin = {margin:.3f}; "
              f"exactly impossible = {impossible}; E drift (abs) = "
              f"{abs_drift:.2e}", flush=True)

    # the honest complement: the oscillating wall does work
    run_o = trio_run(pos0, vel0, V0=OSC_CELL[0], Omega=OSC_CELL[1])
    alive = ~run_o["escaped"]
    E_end_o = total_energy(run_o["pos"][alive], run_o["vel"][alive],
                           OSC_CELL[0], OSC_CELL[1], 12.0)
    dE = np.abs(E_end_o - E0[alive])
    wall_work = {"cell": list(OSC_CELL),
                 "median_abs_dE": float(np.median(dE)),
                 "max_abs_dE": float(dE.max()),
                 "note": "the oscillating wall pumps energy — the C2/C7 " +
                         "sealing is finite-time; the static seal is exact"}
    print(f"  oscillating complement {OSC_CELL}: median |dE| = "
          f"{wall_work['median_abs_dE']:.4f} (wall work > 0)", flush=True)

    static_ok = bool(all(c["P_esc"] == 0.0 for c in cells)
                     and all(c["bound_violation_max"] < 1e-3 for c in cells)
                     and all(c["E_drift_abs_max"] < 1e-4 for c in cells)
                     and cells[-1]["escape_exactly_impossible"])
    print(f"B4/T13: {'PASS' if static_ok else 'FAIL'}", flush=True)
    out["B4_T13_barrier"] = {
        "V_star": V_star, "V_star_formula":
            "(E0_max + 3/sqrt(soft2)) w^2 / (2 (R_ESC - R_b)^2)",
        "pair_floor": -pair_floor, "cells": cells,
        "oscillating_complement": wall_work, "ok": static_ok}

    # ================== verdict =============================================
    gates = {"T11_spectrum": b1_ok, "T11_rotation": b2_ok,
             "T12_manifold": b3_ok, "T13_static": static_ok}
    verdict = {
        "campaign": "qhb_c11",
        "engine": "own RK4 Kirchhoff integrator (qhb.vortex) + the " +
                  "committed trio engine at Omega = 0 (engine.solver); " +
                  "exact analytic corotating Jacobian",
        "project_version": __version__,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "blocks": out,
        "gates": gates,
        "verdicts": {
            "T11_stability_contrast": "PASS" if (b1_ok and b2_ok)
                                      else "FAIL",
            "T12_invariant_wall": "PASS" if b3_ok else "FAIL",
            "T13_static_barrier": "PASS" if static_ok else "FAIL",
            "T13_oscillating": "REPORTED (finite-time; the wall does " +
                               "work — measured, honest complement)",
        },
        "honest_notes": [
            "the vortex layer is implemented from the classical Kirchhoff " +
            "(1876) equations with the package's own code paths; the " +
            "invariants and the Aref (1979) manifold are classical " +
            "results re-derived and re-measured here, never imported",
            "T11 is a statement about the committed toy models: the " +
            "Newtonian trio is unstable (T4), the vortex trio is " +
            "neutrally stable (T11) — the contrast is exact, its QCD " +
            "reading remains the marked hypothesis H4",
            "T12 boundness is measured on the committed horizon t = 12 " +
            "on a measure-zero invariant manifold; the collapse " +
            "separatrix is classical (Aref 1979) and is NOT integrated",
            "T13 is exact FOR THE COMMITTED SOFTENED ENGINE (the bound " +
            "uses the softened pair floor -3/sqrt(soft2)); at Omega > 0 " +
            "the wall does work, energy is not conserved, and the " +
            "sealing stays the measured finite-time statement of C2/C7",
        ],
        "wall_s": time.time() - t0,
    }
    os.makedirs(REF, exist_ok=True)
    with open(os.path.join(REF, "c11_verdict.json"), "w",
              encoding="utf-8") as fh:
        json.dump(verdict, fh, indent=1)
    print(f"verdict written: campaigns/reference/c11_verdict.json "
          f"[{verdict['wall_s']:.1f}s]", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
