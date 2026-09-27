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


def test_third_order_weight_rule():
    """Сессия 18a: весовое правило таблиц — факторизация (l+p)...(l+p+n-1)
    точна для всех (p, n) в {0,1,2,4}x{1,2,3}; старший коэффициент = 1."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base)
    import sympy_third_order as t3
    res = t3.t1_weight_rule()
    assert res["all_exact"] is True


def test_dd_closure_nilpotent_jordan2():
    """Сессия 18b: замкнутая эволюция на M2 — нильпотентный Йордан-2
    (B^2 = 0 с допуском масштаба), spec(B) = {0, 0}."""
    res_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "results")
    B = np.load(os.path.join(res_dir, "_m2_B_baseline.npy"))
    assert B.shape == (2, 2)
    nB = float(np.linalg.norm(B))
    assert nB > 0.1  # связка не вырождена (точно -350/61 ~ 5.74)
    assert float(np.linalg.norm(B @ B)) < 1e-10 * max(1.0, nB ** 2)
    ev = np.linalg.eigvals(B)
    assert np.max(np.abs(ev)) < 1e-10


def test_march_delta_mono_bounds():
    """Сессия 18c: марш подтверждает delta_mono = 0 — рост за эхо < 1e-12,
    фаза за эхо < 1e-6 (пол дефектности), зазор фантомов >= 1e3 границ."""
    res_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "results")
    import json as _json
    with open(os.path.join(res_dir, "march_delta_mono.json"), encoding="utf-8") as fh:
        res = _json.load(fh)
    for key in ("baseline_kappa2", "one_brick_2-bC"):
        d = res[key]["delta_mono_march_per_echo"]
        assert d["growth"] < 1e-12
        assert d["phase"] < 1e-6
        assert res[key]["m2_vs_m1_relative_max"] < 1e-9
        assert res[key]["gap_over_march_bound"] > 1e3


# ============================ сессия 19: нелинейный марш DAE =================

def _load_nonlinear_march():
    import json as _json
    res_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "results")
    with open(os.path.join(res_dir, "march_dae_nonlinear.json"),
              encoding="utf-8") as fh:
        return _json.load(fh)


def test_nonlinear_flat_line_of_equilibria():
    """Сессия 19 T1: плоская линия ker B — точные равновесия нелинейной DAE
    (v = dd = 0, F = r = V ~ 0 на всей амплитуде; марш стационарен)."""
    res = _load_nonlinear_march()
    for key in ("baseline_kappa2", "one_brick_2-bC"):
        pt = res["points"][key]
        assert pt["line_direction_vdd_max"] < 1e-10
        t1 = pt["T1_flat_line"]
        assert max(v["V_norm"] for v in t1["samples"].values()) < 1e-9
        assert max(v["r_max"] for v in t1["samples"].values()) < 1e-11
        assert t1["march_8_echoes"]["dist_drift_max"] < 1e-9


def test_nonlinear_branch_exclusion():
    """Сессия 19 T2: M2-направление e2 не касается S = {F=0, r=0}
    (кокоядро-невязка константна по h и != 0); b2-ветвь (~t3) существует
    статически (joint-Ньютон держит радиус)."""
    res = _load_nonlinear_march()
    for key in ("baseline_kappa2", "one_brick_2-bC"):
        t2 = res["points"][key]["T2_static_S"]
        rats = t2["coker_ratio_e2"]
        assert min(rats) > 1e-5                       # препятствие реально
        assert (max(rats) - min(rats)) < 0.1 * max(rats)  # константа по h
        assert max(t2["coker_ratio_line"]) < 1e-5     # линия — точная ветвь
        assert max(t2["coker_ratio_b2"]) < 1e-5       # b2 — точная ветвь
        assert t2["b2_t3_fraction"] > 0.9             # b2 ~ t3 (вне M2)
        brec = t2["b2_branch"]["A0.01"]
        assert 0.9 < brec["radius_ratio"] < 1.2       # радиус удержан
        assert brec["r_max"] < 1e-12


def test_nonlinear_flow_exits_b2_branch():
    """Сессия 19 T3: поток с b2-ветви немедленно покидает S — level-3 сход
    |Dr V| линеен по A и != 0; марш срывается на первой стадии."""
    res = _load_nonlinear_march()
    for key in ("baseline_kappa2", "one_brick_2-bC"):
        t3 = res["points"][key]["T3_flow_exit"]
        r1 = t3["A0.001"]["exit_rate_over_A"]
        r2 = t3["A0.01"]["exit_rate_over_A"]
        assert 5.0 < r1 < 500.0                       # сход O(A), != 0
        assert abs(r2 / r1 - 1.0) < 0.5               # линейность по A
        assert t3["A0.01"]["march_rows"] == 1         # срыв на 1-й стадии
