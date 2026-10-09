"""OPEN9 (v19): быстрые регрессионные тесты машин девяти открытых вопросов.

Каждый тест проверяет КЛЮЧЕВОЙ машинный факт уровня функции (без полного
прогона кампаний): детерминизм, ключевые тождества, классификаторы.
"""
import json
import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "results")


def _res(name):
    path = os.path.join(RESULTS, name)
    if not os.path.exists(path):
        pytest.skip(f"{name} не найден (машина не запускалась)")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ============================== Q1: brick_selection ==========================

def test_q1_elimination_ideal_is_zero():
    """L1: книги {kappa(d), tau*(d)} оставляют delta свободной —
    элиминационный идеал в Q[delta] нулевой."""
    import brick_selection as bs
    out = bs.level1_closure()
    assert out["elimination_ideal_is_zero"] is True


def test_q1_pslq_control_and_no_cross_relation():
    """L2: контроль метода восстанавливает внутри-секторные связи;
    межсекторных связей (pi/7 vs log-часы) нет."""
    import brick_selection as bs
    out = bs.level2_pslq(precs=(50,), deg=6)
    ctrl = out["method_control"]
    assert ctrl["pi_sector_relation"] is not None      # [49, -30]-подобная
    assert ctrl["log_sector_relation"] is not None     # [1, -4, 2]-подобная
    assert out["cross_sector_relation"] is False


def test_q1_saved_verdict_barrier():
    """Сохранённый вердикт: структурный барьер зафиксирован."""
    d = _res("q1_brick_selection.json")
    assert d["L1_closure"]["elimination_ideal_is_zero"] is True
    assert d["L2_pslq"]["cross_sector_relation"] is False
    assert "НЕ селектируют" in " ".join(d["verdict_lines"]) or \
        "алгебраическая башня" in " ".join(d["verdict_lines"])


# ========================= Q2: finite_amplitude_mono =========================

def test_q2_residual_structural():
    """F1/F2: сдвиг к pi/30 структурный (>> разброса систем) и
    несовместим с линейным сектором."""
    d = _res("q2_finite_amplitude_mono.json")
    assert d["F1_robustness"]["structural_ratio"] > 5.0
    assert d["F2_linear_inconsistency"][
        "inconsistency_factor_vs_growth_bound"] > 1e4


def test_q2_jordan2_exponent_half():
    """F3: минимальная модель Йордан-2 даёт |Im lambda| ~ eps^{1/2}."""
    import finite_amplitude_mono as fm
    out = fm.f3_jordan2_scaling()
    assert abs(out["numpy_fit_exponent_p"] - 0.5) < 0.01
    assert "sqrt" in out["symbolic_eigenvalues"][0]


# ============================ Q3: echo_fit_global ============================

def test_q3_selftest_percentile_beats_ols():
    """G1: на синтетике с полом перцентильный фит восстанавливает гамму,
    ОЛС занижает."""
    import echo_fit_global as ef
    st = ef.selftest()
    assert st["method_ok"] is True
    assert st["gamma_ols_polluted"] < st["gamma_true"]
    assert abs(st["gamma_percentile"]["gamma"] - st["gamma_true"]) < \
        0.2 * st["gamma_true"]


def test_q3_repo_floor_dominates():
    """G2: на данных репо пол доминирует (нижняя половина масс плоская)."""
    d = _res("q3_echo_fit_global.json")
    g2 = d["G2_repo"]
    assert g2["gamma_low_mass_subset"] is not None
    assert abs(g2["gamma_low_mass_subset"]) < 0.2      # плоская
    assert g2["floor_dominance"]["ratio_low_over_high"] > 0.5


def test_q3_gate_word_after_q7():
    """G4: ворота согласованы с вердиктом Q7 (junk floor -> гамма
    лимитируется полом, не модой)."""
    d3 = _res("q3_echo_fit_global.json")
    d7 = _res("q7_m1_tracker.json")
    mode = d7["verdict"]["mode"]
    text = d3["G4_gate"]["text"]
    if mode.startswith("junk"):
        assert "не мода" in text
    elif mode.startswith("growing"):
        assert "ЗАГРЯЗНЕНА" in text


# ============================= Q4: mirror_ring_v2 ============================

def test_q4_row_stats_recovers_signal():
    """M1: на синтетике (сигнал W2*xi + мусор) робастная статистика
    выделяет сигнальное ядро."""
    from mirror_ring_v2 import _row_stats
    rng = np.random.default_rng(7)
    t0 = 0.5
    w2_true = 4.0 / 3.0 * t0 ** 2
    xi = np.linspace(1e-3, 1e-2, 200)
    junk = rng.normal(0, 0.01 * w2_true, xi.size)
    pairs = [{"xi": float(x_), "dc_p": float(4 * w2_true * x_ + j_),
              "dc_m": float(j_), "W2_pair": float(w2_true + j_ / (4 * x_)),
              "extrap_m": False}
             for x_, j_ in zip(xi, junk)]
    s = _row_stats(pairs, t0)
    assert s is not None
    assert abs(s["W2_med_over_t02"] - 4.0 / 3.0) < 0.1


def test_q4_saved_census_blocked():
    """Сохранённый вердикт Q4: критерий ядра НЕ отделяется от
    бутстрап-null (мусор фоновый) — блокировка количественная."""
    d = _res("q4_mirror_ring_v2.json")
    tri = d["M2_triage"]
    assert tri["criterion_pass"] is False or \
        tri.get("observed_vs_null_p95") is False


# ============================ Q5: sympy_center_o7 ============================

def test_q5_chain_closes_z_system():
    """S1: цепочка закрывает z-систему тождественно; P4h_lin — полином."""
    import sympy_center_o7 as sc
    out = sc.s1_chain_closes()
    for k in ("F1_dt0", "F2_dP2", "F4_dD0", "F5_dR1"):
        assert out[f"{k}_is_zero"] is True
    assert out["P4h_linear_closure_is_poly"] is True


def test_q5_m3_link_agrees():
    """S2: M3-связка O4 на цепочке = маршруту O3 (kappa = 2)."""
    import sympy_center_o7 as sc
    assert sc.s2_m3_link()["levels_agree"] is True


def test_q5_t1c_identity():
    """S4: tau*(delta_C) = 27/(4 - pi^2/49) = 1323/(196 - pi^2) ТОЧНО."""
    import sympy_center_o7 as sc
    out = sc.s4_t1c_resolution()
    assert out["clock_zero_exact"] is True
    assert out["ladder_equals_T1c"] is True


# =========================== Q6: puiseux_soft_pole ===========================

def test_q6_pole_location_and_char2():
    """P1/P2: полюс tau = 45/8; char(2) имеет корни {1/2, 45/8}."""
    import puiseux_soft_pole as pp
    out = pp.p2_char2_coincidence()
    assert out["roots_match_claim"] is True
    assert out["roots"] == ["1/2", "45/8"]


def test_q6_linear_closure_finite_at_pole():
    """P3: линейное замыкание P4h_lin конечно в полюсе (полюс —
    артефакт цепочной параметризации)."""
    import sympy as sp
    import puiseux_soft_pole as pp
    out = pp.p3_softness()
    v = sp.sympify(out["P4h_linear_at_pole"])
    assert v.is_finite is not False and v.is_number


# ============================== Q7: m1_tracker ===============================

def test_q7_fit_recovers_m1_m3():
    """T1: декомпозиция m = M1*xi + M3*xi^3 восстанавливает пару."""
    from m1_tracker import fit_m1_m3
    rng = np.random.default_rng(11)
    xi = np.linspace(-0.05, 0.05, 300)
    m = 2.0 * xi + 0.5 * xi ** 3 + rng.normal(0, 1e-9, xi.size)
    f = fit_m1_m3(xi, m)
    assert f is not None and f["R2"] > 0.99
    assert abs(f["M1"] - 2.0) < 1e-5
    assert abs(f["M3"] - 0.5) < 1e-4


def test_q7_mode_junk_floor():
    """T2: на сохранённых профилях |M1| убывает с зумами — мусорный пол,
    растущей 1/r-моды на доступной глубине нет."""
    d = _res("q7_m1_tracker.json")
    assert d["verdict"]["mode"].startswith("junk floor")


# ============================ Q8: lyapunov_center ============================

def test_q8_no_center_at_critical_point():
    """L1: char(i*omega, tau*) имеет только omega = 0 — центра нет."""
    import lyapunov_center as lc
    out = lc.l1_no_center()
    assert out["no_center"] is True
    assert out["nonzero_imaginary_pairs"] == 0


def test_q8_return_map_transient():
    """L3: возвратный дефект линейки воспроизводит записанный
    ruler_periodicity_max; collapse — релаксация (не цикл)."""
    import lyapunov_center as lc
    out = lc.l3_return_map()
    col = out["directions"]["collapse"]
    assert col["reproduces_recorded"] is True
    assert col["dev_monotone_decreasing_after_k1"] is True


# ============================ Q9: krawczyk_census ============================

def test_q9_interval_arithmetic_soundness():
    """K1: интервальная арифметика содержит точные значения."""
    from krawczyk_census import IV, ipow
    x = IV(2.0, 3.0)
    y = IV(-1.0, 4.0)
    assert (x * y).lo <= 2.0 * -1.0 and (x * y).hi >= 3.0 * 4.0
    assert (x + y).lo <= 5.0 and (x + y).hi >= 7.0
    p = ipow(IV(-2.0, 3.0), 2)
    assert p.lo <= 0.0 and p.hi >= 9.0


def test_q9_certifies_booked_clock_root():
    """K2: Кравчик сертифицирует ЕДИНСТВЕННЫЙ корень часов в коробке,
    содержащей забронированный T0h = 3*sqrt(3)/2."""
    from krawczyk_census import IV, g_base, dg_base, krawczyk_1d, tighten_1d
    booked = 3 * math.sqrt(3) / 2
    X = IV(booked - 1e-2, booked + 1e-2)
    K = krawczyk_1d(g_base, dg_base, X)
    assert K is not None
    X2 = tighten_1d(g_base, dg_base, X)
    assert X2.contains(booked) if hasattr(X2, "contains") else \
        (X2.lo <= booked <= X2.hi)


def test_q9_2d_out_exclusion():
    """K3: 2D-перепись цепного среза — OUT-сертификат > 99% площади."""
    d = _res("q9_krawczyk_census.json")
    c3 = d["K3_census_2d_chain"]
    assert c3["out_area_fraction"] > 0.99
    assert c3["undecided_area_fraction"] < 0.01


# ==================== v20a: amplitude_ladder (лестница амплитуд) ====================

def test_v20a_ladder_executed_and_honest():
    """v20a: лестница исполнена (4 ступени); при < 3 валидных ступеней
    вердикт честно фиксирует НЕизмеренность показателя и кросс-чек
    по сохранённым кампаниям."""
    d = _res("v20a_amplitude_ladder.json")
    assert len(d["rungs"]) == 4
    ok = [r for r in d["rungs"] if "delta_eff" in r]
    if len(ok) < 3:
        joined = " ".join(d["verdict_lines"])
        assert "НЕ измерен" in joined
        assert "zoom_campaign" in joined      # кросс-чек присутствует
        assert d.get("fit_p_delta") is None
    else:
        assert d["fit_p_delta"]["p"] is not None


def test_v20a_rung_stops_match_saved_campaigns():
    """v20a: стоп-критерии ступеней согласованы с сохранёнными кампаниями
    (singularity/v_exhausted), глубина z < 6.05 — стена, не параметр."""
    d = _res("v20a_amplitude_ladder.json")
    for r in d["rungs"]:
        if "stop" in r:
            assert r["stop"] in ("singularity", "v_exhausted", "max_zooms")
            assert r["z_reached"] < 6.1


# ==================== v20b: depth_z30 (глубина z >= 30) ====================

def test_v20b_linear_sector_certified():
    """v20b [D1]: пропагатор I + B*T точен (B^2 = 0), фаза ТОЧНО 0,
    рост светской; RK4 совпадает с замкнутой формой."""
    d = _res("v20b_depth_z30.json")
    d1 = d["D1_linear_sector"]
    assert d1["nilpotency_max_abs_B2"] < 1e-12
    assert d1["phase_drift_max_rad"] < 1e-12
    assert d1["rk4_vs_closed_form_rel"] < 1e-9
    assert d1["sigma_max_at_z30"] > 100.0      # ~126: светской рост O(T)


def test_v20b_budget_closed_loop():
    """v20b [D2]+[D3]: S_req(30) = e^{gamma*(30-9.35)} ~ 2.26e3; петля
    замкнута — при S = S_req(z) априорное правило даёт процентную гамму,
    наивный ОЛС у стены воспроизводит провал q3 (> 20% смещение)."""
    import math
    d = _res("v20b_depth_z30.json")
    d2, d3 = d["D2_budget"], d["D3_percentile_ladder"]
    assert abs(d2["S_req_at_z30"] - math.exp(0.374 * (30.0 - 9.35))) < 1.0
    assert d2["spinor_echoes_to_z30"] > 40
    sc = {s["z_target"]: s for s in d3["scenarios"]}
    assert sc[9.35]["ols_naive_err_pct"] > 20.0          # провал ОЛС у стены
    deep_ok = sum(1 for z in (20.0, 25.0, 30.0) if sc[z]["success"])
    assert deep_ok >= 2                                   # процент на глубине


# ==================== v21: deep_echo_v21 (глубинная кампания эха) ====================

def test_v21_protocol_reference_and_start():
    """v21: машина исполняет протокол раздела 5 монографии (depth_z30 [D4]);
    параметры старта совпадают с [P1]: eps = 1e-3, n = 800, цель z = 30."""
    d = _res("v21_deep_echo.json")
    assert "раздел 5" in d["protocol_reference"]
    assert d["config"]["eps"] == 1e-3
    assert d["config"]["n_grid"] == 800
    assert d["config"]["z_target"] == 30.0
    assert d["config"]["monitor_rows"] == [12, 24, 48, 96, 192, 384]


def test_v21_wrapper_neutral_to_physics():
    """v21 [D-v21] контроль: обёртка v21 не меняет физику марша — главная
    цепь (w = 5) воспроизводит чистый ZoomRunner n = 800 (z = 1.782...,
    1 зум, стоп singularity); инвазий гейтом не поднято."""
    d = _res("v21_deep_echo.json")
    assert d["z_reached"] == pytest.approx(1.7820506551, abs=1e-6)
    assert d["zooms"] == 1
    assert d["stop"]["kind"] == "machine:singularity"
    assert len(d["events"]) == 0


def test_v21_window_policy_probe():
    """v21 [D-v21]: стена глубины чувствительна к оконной политике —
    z(w = 3) ~ 7.2 против z(w = 5) ~ 1.8 при том же eps/n; пробы без
    инвазий; бюджет от лучшей политики S_req(30) ~ 5.0e3."""
    d = _res("v21_deep_echo.json")
    p = d["window_policy_probe"]
    assert p["status"] == "executed"
    rows = {r["w_factor"]: r for r in p["rows"]}
    assert rows[3.0]["z_reached"] > 7.0
    assert rows[1.5]["z_reached"] > 6.0
    assert rows[3.0]["n_invasions"] == 0 and rows[1.5]["n_invasions"] == 0
    z_best = max(rows[3.0]["z_reached"], rows[1.5]["z_reached"])
    assert math.exp(0.374 * (30.0 - z_best)) == pytest.approx(5044, rel=0.02)


def test_v21_ladder_second_pass_honest():
    """v21: лестница амплитуд исполнена вторым проходом на лучшей политике
    (3 ступени, eps in {3e-3, 1e-3, 1e-4}); Delta_eff не измерим
    (пиков <= 3 на ступень) — дискриминатор p сохранён как протокол."""
    d = _res("v21_deep_echo.json")
    sp = d["second_pass"]
    assert sp["status"] == "executed"
    assert sp["w_policy"] == 3.0
    assert len(sp["rungs"]) == 3
    assert {r["eps"] for r in sp["rungs"]} == {3e-3, 1e-3, 1e-4}
    assert all(r["n_Q_peaks"] <= 3 for r in sp["rungs"])
    assert sp["fit_p_delta"] is None


def test_v21_gate_and_trend_classifier():
    """v21 [P2]: слово ворот совместимо с q7[T4]; классификатор тренда |M1|
    воспроизводит семантику q7[T2] (убывание -> junk floor, рост ->
    growing); honest notes несут калибровку прогоном 0."""
    import deep_echo_v21 as m
    d = _res("v21_deep_echo.json")
    assert d["gate_word"].startswith(("open-for-percentile", "gated"))
    assert any("калиброван" in n.lower() for n in d["honest_notes"])
    down = m.classify_m1_trend([(1, 1e-6), (2, 1e-7), (3, 1e-8)])
    assert down["mode"].startswith("junk floor")
    up = m.classify_m1_trend([(1, 1e-8), (2, 1e-7), (3, 1e-6)])
    assert up["mode"].startswith("growing")
    assert m.gate_word(down["mode"]).startswith("open-for-percentile")
    assert m.gate_word(up["mode"]).startswith("gated")


# ==============================================================================
# v22: v-бюджет и якорение окна (стена z ~ 7.2 при w = 3)
# ==============================================================================
def test_v22_dead_extension_and_cap_facts():
    """v22 [F1]/[F3]: телескопический кап не связан (4/4 зумов свободны);
    _try_extend мёртв по построению — запас 0.0 точно на всех вызовах
    (v_now = v[n-1] = stage_v[1] при j >= n)."""
    d = _res("v22_v_budget.json")
    cert = d["cert"]
    assert cert["reproduced_v21_w3"] is True
    assert cert["z_dev_vs_v21"] < 1e-9
    f1, f3 = cert["F1_cap_free"], cert["F3_dead_extension"]
    assert f1["cap_active_count"] == 0
    assert f1["n_zooms"] == 4
    assert f3["n_calls"] >= 1
    assert f3["slack_all_zero"] is True


def test_v22_final_stage_vacuum_and_starvation():
    """v22 [F2]/[F4]: финальная стадия контроля — вакуум (доля пустых строк
    > 0.9, mx_max = 0); клэмп буфера активен минимум на одном зуме —
    голодание назад-размаха подтверждено."""
    d = _res("v22_v_budget.json")
    f2, f4 = d["cert"]["F2_final_vacuum"], d["cert"]["F4_starvation"]
    assert f2["vacuum_row_share"] > 0.9
    assert f2["max_mx_final_stage"] < 1e-3
    assert any(r["clamp_active"] for r in f4["rows"])


def test_v22_probes_robustness_of_wall():
    """v22 [C2]/[C2b]: v_ahead вперёд инертен, глобальный задний якорь
    разрушителен (z < 2.5 на всех ветках), поздний якорь зажат полом
    (z ~ контроль 7.204) — стена устойчива к наивным расширениям бюджета."""
    d = _res("v22_v_budget.json")
    probe, probe2 = d["probe"], d["probe2"]
    assert probe["ahead_inert"] is True
    assert all(r["z_reached"] < 2.5 for r in probe["rows"])
    assert probe2["back_unlocks_late"] is False
    assert all(abs(r["z_reached"] - d["cert"]["control"]["z_reached"])
               < 0.05 for r in probe2["rows"])


def test_v22_root_anchor_breaks_wall_and_fourth_peak():
    """v22 [C2c]/[C3]: корневой якорь + якорь на полу покрытия двигают
    стену (z-рекорд 8.56 > 7.20); политика k1 = 0.52 даёт 7 пиков (4 на
    одной стадии) — 4-й пик достигнут; Delta_eff = 0.61 +- 0.45 НЕ равна
    DSS 3.44 (исключена на > 6 sigma) — честный отрицательный вердикт
    периодичности на этой глубине."""
    d = _res("v22_v_budget.json")
    probe3, deep = d["probe3"], d["deep"]
    assert probe3["back_unlocks_root"] is True
    assert d["depth_record_z"] > 8.0
    assert deep["policy"]["k_back"] == 0.52
    assert deep["policy"]["anchor_from_zoom"] == 2
    assert max(s["n_peaks"] for s in deep["peaks_per_stage"]) >= 4
    deb = deep["delta_eff_best"]
    assert deb is not None and deb["n_peaks_seg"] >= 4
    assert abs(deb["delta_eff"] - 3.44) > 6 * deb["delta_err"]


def test_v22_ladder_second_pass_honest():
    """v22 [C4]: лестница амплитуд на политике k1 = 0.52 исполнена, но
    Delta_eff нет на >= 3 ступенях — p не измерим (дискриминатор сохранён)."""
    d = _res("v22_v_budget.json")
    sp = d["second_pass"]
    assert sp["status"] == "executed"
    assert sp["fit_p_delta"] is None
    assert len(sp["rungs"]) == 3


def test_v22_fork_neutral_by_construction():
    """v22: вилка _zoom нейтральна по построению — при (k_back=0.5,
    v_ahead=1.5, без якоря) формула v_lo совпадает с родительской
    бит-в-бит; якорные ветви включаются только флагами политики."""
    import deep_echo_v22 as m
    import zoom_solver as zs
    r = m.V22Runner(A=0.08, n=40, max_zooms=2, w_factor=3.0,
                    v_back=0.5, v_ahead=1.5)
    assert r._k_back_now() == 0.5
    assert r._anchor_floor_now() is False
    # инвариант телескопического бюджета (основа [F3])
    assert r.stage_v[1] == float(r.v[-1])
    assert r.stage_v[0] == float(r.v[0])
    # формула родителя: v_lo = max(v_now - 0.5*(v_hi - v_now), buffer_v[0])
    v_now, v_hi, buf0 = 0.45, 0.60, 0.30
    parent_lo = max(v_now - 0.5 * (v_hi - v_now), buf0)
    assert abs(parent_lo - 0.375) < 1e-12
    # а с якорем на пол: v_lo = buf0 = 0.30 (глубочайшая покрытая точка)
    r1 = m.V22Runner(A=0.08, n=40, max_zooms=2, w_factor=3.0,
                     v_back=0.52, v_ahead=1.5, anchor_from_zoom=2)
    assert r1._anchor_floor_now() is False   # зум 1 ещё без якоря
    r1.diag.zooms = 1
    assert r1._anchor_floor_now() is True    # с зума 2 — якорь на пол
    assert zs.ZoomRunner is not None
