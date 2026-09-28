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


# ==================== сессия 20: HEXCYCLE-DAE (цикл фигур) ====================

def _load_hexcycle_dae():
    import json as _json
    res_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "results")
    with open(os.path.join(res_dir, "hexcycle_dae.json"),
              encoding="utf-8") as fh:
        return _json.load(fh)


def test_hexcycle_dae_compensated_book_in_S():
    """Сессия 20 T1c: компенсированная книга цикла фигур — статические
    решения на ВСЕХ масштабах книги (коллапс 12/12, обдув 6/6), лежат в
    S = {F=0, r=0} — глобальные статические компоненты S (ответ на оговорку
    v15); дегенератный угол R1h->0 отбракован; дефект возврата линейки
    delta_R1h < 0.1 за цикл; полюс P4h — мягкая дегенерация."""
    res = _load_hexcycle_dae()
    for key in ("baseline_kappa2", "one_brick_2-bC"):
        pt = res["points"][key]
        walk = pt["T1c_ruler_walk"]
        for tag, n_exp in (("collapse", 12), ("blowup", 6)):
            rows = walk[tag]
            ok = [v for v in rows.values()
                  if v.get("converged") and not v.get("degenerate")]
            assert len(ok) == n_exp, (key, tag, len(ok))
            nS = sum(1 for v in ok if v.get("in_S"))
            assert nS >= n_exp - 1, (key, tag, nS)
        assert pt["delta_R1h_one_cycle"] < 0.1
        for b in pt["pole_barriers"]:
            assert not b["hard_barrier"]


def test_hexcycle_dae_pure_book_static_defect():
    """Сессия 20 T1a: чистая книга (R1h == 1) статически НЕ точна вне
    критического масштаба (F до 2.7e2 коллапс / 2.7e5 обдув), но станция 0
    (пирамида) = x* точно — якорь вложения."""
    res = _load_hexcycle_dae()
    for key in ("baseline_kappa2", "one_brick_2-bC"):
        pt = res["points"][key]
        assert pt["T1_static_collapse"]["F_max"] > 1.0
        assert pt["T1_static_blowup"]["F_max"] > 1e3
        assert pt["T1_static_collapse"]["F_max_station0"] < 1e-10
        assert pt["station0_is_x_star"] < 1e-13


def test_hexcycle_dae_kinetic_annihilation():
    """Сессия 20 T2/T3: пролонгация гомотетической кинематики точна
    (<= 1e-11, по построению), но замыкание несовместимо с ходьбой
    (r_max > 1); все L1-посадки с |V| > 1e-3 имеют exit_rate > 1 — поток
    покидает S (вердикт v15 продолжается глобально)."""
    res = _load_hexcycle_dae()
    for key in ("baseline_kappa2", "one_brick_2-bC"):
        pt = res["points"][key]
        for tag in ("collapse", "blowup"):
            kin = pt["T2_kinetic"][tag]
            assert kin["prolong_max"] < 1e-11
            assert kin["r_max"] > 1.0
        for tag in ("collapse", "blowup"):
            for v in pt["T3_landings"][tag]["L1_free"].values():
                if v.get("converged") and (v.get("V_norm") or 0) > 1e-3:
                    assert v["exit_rate"] > 1.0, (key, tag, v)


# ============= сессия 21: CLOCK-CLOSURE-T1C (часы + B4-remnant) ==============

def _load_clock_closure():
    import json as _json
    res_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "results")
    with open(os.path.join(res_dir, "clock_closure_t1c.json"),
              encoding="utf-8") as fh:
        return _json.load(fh)


def test_clock_pair_unique_closure_scale():
    """Сессия 21 C1: пара часов (UV_xi3, Mdef_xi5) на цепочке имеет
    ЕДИНСТВЕННЫЙ общий положительный корень tau*(kappa) = 27/(2kappa):
    27/4 (baseline), 1323/(196-pi^2) (one-brick); GCD в tau* обращается
    в нуль ТОЧНО (SymPy) — наивная несовместимость 9/4 vs 9/16 растворена
    де-адиабатизованной (T1c-)формой источников."""
    res = _load_clock_closure()
    for key, tau_ref in (("baseline_kappa2", 6.75),
                         ("one_brick_2-bC", 7.10792020692263)):
        c1 = res["points"][key]["C1_clock_pair_theorem"]
        assert c1["gcd_at_tau_star_zero"] is True, key
        assert c1["unique_common_clock"] is True, key
        assert abs(c1["tau_star_numeric"] - tau_ref) < 1e-9, key
        assert len(c1["gcd_positive_roots"]) == 1, key


def test_t1c_erratum_and_honest_static_map():
    """Сессия 21 A0/A1 (ERRATUM к v16): посадки [T1c] v16 — захваты
    тривиальной ветви (T0h не был приколот в static_landing), книжноподобных
    посадок 0; с ЖЁСТКИМ пином T0h недегенератных статических состояний на
    забронированных масштабах нет (0/18 в обеих точках) — часы не имеют
    статического носителя вне критического масштаба."""
    res = _load_clock_closure()
    for key in ("baseline_kappa2", "one_brick_2-bC"):
        pt = res["points"][key]
        stats = pt["A0_erratum_audit"]["stats"]
        n_book = sum(s.get("book_like", 0) for s in stats.values())
        assert n_book == 0, key
        a1 = pt["A1_honest_static_map"]
        assert "0/18" in a1["verdict"], key


def test_clock_books_exact_and_tick_obstruction():
    """Сессия 21 C2/C3: книги в x* точны (W2/T0^2 = 2k/3, UV 9R3/(2R1T0^2)
    = k/2, лестница R3h = 3/2 голономно-инвариантна, s = 3P2/T0 = 1);
    кернел (v,dd)->r 5-мерен (линейная свобода тика), но подъём на
    совместное многообразие остановывается (r ~ O(kick)); one-brick
    препятствие МЕНЬШЕ baseline — дельта-чувствительность remnant'а."""
    res = _load_clock_closure()
    obs = {}
    for key in ("baseline_kappa2", "one_brick_2-bC"):
        pt = res["points"][key]
        c2 = pt["C2_clock_carriers"]["x_star"]
        assert abs(c2["W2_defect"]) < 1e-12, key
        assert abs(c2["UV_defect"]) < 1e-9, key
        assert abs(c2["R3h_ladder_3/2"] - 1.5) < 1e-9, key
        assert abs(c2["s_clock_3P2/T0"] - 1.0) < 1e-12, key
        c3 = pt["C3_b4_remnant"]
        assert c3["kernel_at_x_star"]["dim_kernel"] >= 4, key
        t01 = c3["tick_test"]["eps0.01"]
        assert t01["start_r_max"] > 1e-3, key      # остановка реальна
        obs[key] = t01["start_r_max"]
    assert obs["one_brick_2-bC"] < obs["baseline_kappa2"]


# ------------------------------------------------------------ сессия 22 --
def _load_brick_scan():
    import json as _json
    res_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "results")
    with open(os.path.join(res_dir, "brick_scan_tick.json"),
              encoding="utf-8") as fh:
        return _json.load(fh)


def _load_global_static():
    import json as _json
    res_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "results")
    with open(os.path.join(res_dir, "global_static_search.json"),
              encoding="utf-8") as fh:
        return _json.load(fh)


def test_brick_ladder_clock_pair_theorem():
    """Сессия 22 [B1]/[B2]: лестница кирпичей delta_k = pi/k, kappa = 2 -
    delta^2/2: на КАЖДОМ кирпиче пара часов (UV_xi3, Mdef_xi5) на цепочке
    имеет ЕДИНСТВЕННЫЙ общий положительный корень tau*(delta) = 27/(2 -
    delta^2) с ТОЧНЫМ нулём GCD в нём; плоская линия R1h при критическом
    масштабе существует на каждом кирпиче (v15 T1 не зависит от кирпича)."""
    res = _load_brick_scan()
    n = 0
    for lbl, pt in res["points"].items():
        if "build_failed" in pt or "B2_clock_pair" not in pt:
            continue
        n += 1
        b2 = pt["B2_clock_pair"]
        assert b2["unique_common_clock"] is True, lbl
        assert b2["gcd_zero_at_tau_star"] is True, lbl
        assert abs(b2["tau_star_numeric"]
                   - 27.0 / (2.0 * pt["kappa_numeric"])) < 1e-9, lbl
        assert pt["B1_point"]["flat_line_ok"] is True, lbl
        assert abs(pt["B1_point"]["tau_star"]
                   - 27.0 / (2.0 * pt["kappa_numeric"])) < 1e-9, lbl
    assert n >= 10


def test_brick_ladder_tick_obstruction():
    """Сессия 22 [B3]: препятствие тика (исторически-свободная мера ||r|| в
    замороженном базисе x*) немонотонно по delta и не степенное; выживший
    кирпич delta_C = pi/7 НЕ является минимумом лестницы (тик не селектирует
    кирпич); относительный якорь v17 (one-brick < baseline) держится."""
    res = _load_brick_scan()
    rows = res["tick_vs_delta"]
    ks = [r for r in rows if r["k"] is not None]
    assert len(ks) >= 10
    vals = [r["r_norm_kick0.05"] for r in ks]
    diffs = [b - a for a, b in zip(vals, vals[1:])]
    assert any(d > 0 for d in diffs) and any(d < 0 for d in diffs)
    pl = res["powerlaw_kick0.05"]
    assert pl["max_abs_residual_ln"] > 0.5          # не степенная
    lm = res["ladder_minimum_kick0.05"]
    assert lm["is_survivor"] is False
    row = {r["label"]: r for r in rows}
    assert (row["brick_pi_over_7"]["r_norm_kick0.05"]
            < row["baseline_delta0"]["r_norm_kick0.05"])
    assert (row["brick_pi_over_7"]["r_norm_kick0.01"]
            < row["baseline_delta0"]["r_norm_kick0.01"])


def test_brick_ladder_phantom_gap():
    """Сессия 22 [B4]: скан фантомного зазора к pi/30 по лестнице кирпичей —
    внутри 1% ничего (лучший hit ~ +1.14% при delta = pi/3) — скан замыкания
    pi/30 НЕ находит (multiple-testing оговорка)."""
    res = _load_brick_scan()
    rels = []
    for pt in res["points"].values():
        b4 = pt.get("B4_phantoms") or {}
        bh = b4.get("best_hit") or {}
        if bh:
            rels.append(abs(bh["rel_diff_pct"]))
    assert len(rels) >= 10
    assert min(rels) > 1.0


def test_global_static_census_exhaustive():
    """Сессия 22 [G1a]-[G3]: теорема факторизации — UV_xi3 = 2*R1h*Mdef_xi5
    ТОЧНО, часовые факторы пропорциональны константе, уникальный
    положительный корень; S ∩ цепочка = {R1h=0} ∪ {T0h=0} ∪ {T0h=T0h*}
    точно; численная перепись и свободный Ньютон новых ветвей не находят;
    статический кернел dF/da в x* 1-мерен (только касательная плоской
    линии), попытки ветвления в провалах ранга ничего не дают."""
    res = _load_global_static()
    for key in ("baseline_kappa2", "one_brick_2-bC"):
        pt = res["points"][key]
        g1a = pt["G1a_factorization_theorem"]
        assert g1a["ratio_is_2R1h"] is True, key
        assert g1a["clock_zero_sets_identical"] is True, key
        assert g1a["unique_positive_clock_root"] is True, key
        assert g1a["clock_zero_at_book_tau_star"] is True, key
        assert g1a["other_rest_eqs_vanish_identically"] is True, key
        g1 = pt["G1_chain_2d_scan"]
        assert g1["n_new_confirmed"] == 0, key
        assert "NEW_candidate" not in g1["class_counts"], key
        g2 = pt["G2_free_newton"]
        assert g2["new_candidates"] == [], key
        assert g2["landing_classes"].get(
            "flat_line_or_xstar_S1S2", 0) > 0, key
        g3 = pt["G3_shooting_continuation"]
        assert g3["kernel_dFda_at_x_star"][
            "kernel_dim_tol1e-7"] == 1, key
        assert len(g3["branch_attempts"]["landings"]) == 0, key
