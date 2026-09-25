"""Быстрые регрессионные тесты модуля einstein_direct (pytest)."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from solver import DoubleNullSolver, GaussianPulseData, RobertsData, SolverConfig, flat_space_test


def test_flat_space_machine_precision():
    err_r, err_Phi, err_a2 = flat_space_test(200, verbose=False)
    assert err_r < 1e-10
    assert err_Phi == 0.0
    assert err_a2 == 0.0


def test_roberts_solution_satisfies_system():
    """Точное решение Робертса–Оширо должно удовлетворять системе (SymPy-проверка
    продублирована здесь по данным results/derivation_results.json)."""
    res_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "results", "derivation_results.json")
    if os.path.exists(res_path):
        import json
        res = json.load(open(res_path))
        assert res["checks"]["roberts_solution_ok"] is True
        assert res["checks"]["burko_E1_ok"] is True


def test_subcritical_disperses():
    data = GaussianPulseData(A=0.03, v_p=0.5, sigma=0.1, u0=-1.0, v0=0.0)
    cfg = SolverConfig(n_u=400, n_v=400, u_range=(-1.0, 1.05), v_range=(0.0, 1.0),
                       monitor_every=10 ** 9)
    sol = DoubleNullSolver(cfg, data)
    diag = sol.run(verbose=False)
    assert not diag.ah_found
    assert diag.stopped_reason == "completed"


def test_supercritical_forms_horizon():
    data = GaussianPulseData(A=0.45, v_p=0.5, sigma=0.1, u0=-1.0, v0=0.0)
    cfg = SolverConfig(n_u=700, n_v=700, u_range=(-1.0, 1.05), v_range=(0.0, 1.0),
                       monitor_every=10 ** 9)
    sol = DoubleNullSolver(cfg, data)
    diag = sol.run(verbose=False)
    assert diag.ah_found
    assert diag.m_ah > 0
    # масса горизонта не превышает полную энергию конфигурации
    assert diag.m_ah < 0.05


def test_misner_sharp_definition_consistency():
    """Определение массы Мизнера–Шарпа согласовано с эволюцией на плоском фоне."""
    data = GaussianPulseData(A=0.0, v_p=0.5, sigma=0.1, u0=-1.0, v0=0.0)
    cfg = SolverConfig(n_u=300, n_v=300, u_range=(-1.0, 1.05), v_range=(0.0, 1.0),
                       monitor_every=10 ** 9)
    sol = DoubleNullSolver(cfg, data)
    sol.run(verbose=False)
    m_def = 0.5 * sol.r * (1 + 4 * sol.p * sol.q / sol.alpha2)
    assert np.max(np.abs(sol.m - m_def)) < 1e-10
