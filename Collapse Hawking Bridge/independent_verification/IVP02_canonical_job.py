#!/usr/bin/env python3
"""
IVP-02 canonical numeric job — printed with full precision so that
different clean-room interpreters can be compared byte-wise.

Runs three fixed engine jobs on the IVP suite's OWN initial-data classes:
  J1  Roberts-Oshiro regression, N=200 (own exact-solution formulas)
  J2  flat space (A = 0), N=200
  J3  Gaussian pulse A = 0.10, N=200  (supercritical; M_AH observable)

Output format: one "KEY  VALUE" line per quantity (17 significant digits).
"""
import os
import sys

import numpy as np

IVP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(IVP_DIR)
sys.path.insert(0, IVP_DIR)
sys.path.insert(0, os.path.join(ROOT, "engine"))

import solver as S
from ivp_common import GEO, make_independent_gaussian, make_independent_roberts

IndepRoberts = make_independent_roberts(S)
IndepG = make_independent_gaussian(S)


def out(key, value):
    print(f"{key}  {value:.17e}", flush=True)


def main():
    # J1: Roberts regression (verifier-own window and sigma)
    data = IndepRoberts(sigma=0.12)
    cfg = S.SolverConfig(n_u=200, n_v=200, u_range=(-0.25, 0.75),
                         v_range=(1.1, 1.9), monitor_every=25)
    sol = S.DoubleNullSolver(cfg, data)
    diag = sol.run(verbose=False)
    r_ex, Phi_ex, _, _, _, _ = data.fields(sol.u, np.full_like(sol.u, sol.v_final))
    out("J1_err_r", float(np.max(np.abs(sol.r - r_ex))))
    out("J1_err_Phi_rel", float(np.max(np.abs(sol.Phi - Phi_ex))
                                / max(float(np.max(np.abs(Phi_ex))), 1e-300)))
    out("J1_err_alpha2", float(np.max(np.abs(sol.alpha2 - 1.0))))

    # J2: flat space
    data = IndepG(A=0.0, v_p=GEO["v_p"], sigma=GEO["sigma"],
                  u0=GEO["u0"], v0=GEO["v0"])
    cfg = S.SolverConfig(n_u=200, n_v=200, u_range=(GEO["u0"], GEO["u1"]),
                         v_range=(GEO["v0"], GEO["v1"]), monitor_every=25)
    sol = S.DoubleNullSolver(cfg, data)
    diag = sol.run(verbose=False)
    out("J2_err_r_flat", float(np.max(np.abs(sol.r - (sol.v_final - sol.u) / 2.0))))
    out("J2_err_Phi", float(np.max(np.abs(sol.Phi))))
    out("J2_err_alpha2", float(np.max(np.abs(sol.alpha2 - 1.0))))

    # J3: Gaussian pulse supercritical observable
    data = IndepG(A=0.10, v_p=GEO["v_p"], sigma=GEO["sigma"],
                  u0=GEO["u0"], v0=GEO["v0"])
    cfg = S.SolverConfig(n_u=200, n_v=200, u_range=(GEO["u0"], GEO["u1"]),
                         v_range=(GEO["v0"], GEO["v1"]), monitor_every=25)
    sol = S.DoubleNullSolver(cfg, data)
    diag = sol.run(verbose=False)
    out("J3_ah_found", 1.0 if diag.ah_found else 0.0)
    out("J3_M_AH", float(diag.m_ah) if diag.ah_found else 0.0)
    out("J3_v_final", float(sol.v_final))


if __name__ == "__main__":
    main()
