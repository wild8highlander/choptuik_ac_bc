# -*- coding: utf-8 -*-
"""Engine smoke test: Roberts-Oshiro regression at N=200 (~1 s)."""
import math

import numpy as np

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))

from solver import DoubleNullSolver, RobertsData, SolverConfig  # noqa: E402


def test_roberts_regression_n200():
    """Second-order engine reproduces the exact Roberts-Oshiro solution."""
    data = RobertsData(sigma=0.1)
    cfg = SolverConfig(n_u=200, n_v=200, u_range=(-0.3, 0.7), v_range=(1.0, 2.0),
                       monitor_every=25)
    sol = DoubleNullSolver(cfg, data)
    diag = sol.run(verbose=False)
    v_f = sol.v_final
    r_ex, Phi_ex, _, _, _, _ = data.fields(sol.u, np.full_like(sol.u, v_f))
    err_r = float(np.max(np.abs(sol.r - r_ex)))
    assert err_r < 1e-4, err_r
    assert abs(sol.alpha2 - 1.0).max() < 1e-3
    assert diag.c1_max < 0.01          # Hamiltonian constraint
    assert diag.c2_max < 1e-4          # momentum constraint
    assert diag.mdef_max < 1e-3        # mass definition identity


def test_engine_units_and_config():
    """The engine declares kappa = 2 (4 pi G = 1)."""
    import solver as S
    assert S.KAPPA == 2.0
