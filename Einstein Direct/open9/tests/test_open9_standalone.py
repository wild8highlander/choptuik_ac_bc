#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Автономный смоук-набор папки open9/ (без путей репо).

Запуск из open9/:  python3 -m pytest tests/test_open9_standalone.py -q
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MACH = os.path.join(HERE, "machines")
sys.path.insert(0, MACH)


def _res(name):
    with open(os.path.join(MACH, "results", name), encoding="utf-8") as fh:
        return json.load(fh)


# ---------- импортируемость всех 11 машин ----------
def test_all_machines_import():
    for mod in ("brick_selection", "finite_amplitude_mono",
                "echo_fit_global", "mirror_ring_v2", "sympy_center_o7",
                "puiseux_soft_pole", "m1_tracker", "lyapunov_center",
                "krawczyk_census", "amplitude_ladder", "depth_z30",
                "deep_echo_v21"):
        __import__(mod)


# ---------- ключевые машинные факты v19 ----------
def test_q1_barrier():
    d = _res("q1_brick_selection.json")
    # идеал ликвидации тривиален: базис Грёбнера = ['1'] => дельта свободна
    assert d["L1_closure"]["groebner_basis"] == ["1"]
    assert any("трансцендент" in v or "transcend" in v.lower()
               for v in [str(d["L3_transcendence"])])


def test_q2_structural():
    d = _res("q2_finite_amplitude_mono.json")
    assert d["F1_robustness"]["structural_ratio"] > 10
    assert d["F2_linear_inconsistency"]["inconsistency_factor_vs_growth_bound"] > 1e10
    assert abs(d["F3_jordan2_scaling"]["numpy_fit_exponent_p"] - 0.5) < 1e-6


def test_q4_blocked():
    d = _res("q4_mirror_ring_v2.json")
    # trim-медианы НЕ стягиваются к 4/3: мусор фоновый, канал заблокирован
    med = [p["W2_trim_med_over_t02_median"] for p in d["M1_robust_pairs"]]
    assert all(abs(m - 4.0 / 3.0) > 0.1 for m in med)
    assert d["n_pairs_nonextrap"] >= 10000


def test_q9_census():
    d = _res("q9_krawczyk_census.json")
    assert d["K3_census_2d_chain"]["out_area_fraction"] > 0.99


# ---------- v20 ----------
def test_v20a_honest():
    d = _res("v20a_amplitude_ladder.json")
    assert len(d["rungs"]) == 4
    ok = [r for r in d["rungs"] if "delta_eff" in r]
    if len(ok) < 3:
        assert d.get("fit_p_delta") is None
        assert "НЕ измерен" in " ".join(d["verdict_lines"])


def test_v20b_certified():
    import numpy as np
    d = _res("v20b_depth_z30.json")
    d1 = d["D1_linear_sector"]
    assert d1["phase_drift_max_rad"] < 1e-12
    assert abs(d1["B"][0][1] + 350.0 / 61.0) < 1e-9
    sc = {s["z_target"]: s for s in d["D3_percentile_ladder"]["scenarios"]}
    assert sc[30.0]["success"] is True
    assert sc[9.35]["ols_naive_err_pct"] > 20.0


# ---------- автономность: машина v20b реально бежит из папки ----------
def test_depth_z30_runs_standalone(tmp_path):
    import importlib
    import depth_z30 as dz
    out = dz.d1_linear_sector_certified()
    assert out["nilpotency_max_abs_B2"] < 1e-12


# ---------- v21: глубинная кампания эха (протокол раздела 5) ----------
def test_v21_deep_echo_facts():
    d = _res("v21_deep_echo.json")
    assert "раздел 5" in d["protocol_reference"]
    assert d["config"]["eps"] == 1e-3 and d["config"]["n_grid"] == 800
    p = d["window_policy_probe"]
    assert p["status"] == "executed"
    rows = {r["w_factor"]: r for r in p["rows"]}
    # стена чувствительна к оконной политике (рычаг [P3])
    assert rows[3.0]["z_reached"] > 7.0 > 1.8
    assert rows[3.0]["n_invasions"] == 0
    sp = d["second_pass"]
    assert sp["status"] == "executed" and len(sp["rungs"]) == 3
    assert sp["fit_p_delta"] is None          # p честно не измерим
    assert any("калиброван" in n.lower() for n in d["honest_notes"])


# ---------- v22: v-бюджет и якорение окна ----------
def test_v22_v_budget_facts():
    d = _res("v22_v_budget.json")
    cert = d["cert"]
    # контроль: вилка нейтральна, цепочка v21 w=3 воспроизведена точно
    assert cert["reproduced_v21_w3"] is True and cert["z_dev_vs_v21"] < 1e-9
    # [F1] кап не связан; [F3] _try_extend мёртв (запас 0.0 точно)
    assert cert["F1_cap_free"]["cap_active_count"] == 0
    assert cert["F3_dead_extension"]["slack_all_zero"] is True
    # [C2]/[C2b]: вперёд инертен, глобальный назад разрушителен, поздний зажат
    assert d["probe"]["ahead_inert"] is True
    assert all(r["z_reached"] < 2.5 for r in d["probe"]["rows"])
    assert d["probe2"]["back_unlocks_late"] is False
    # [C2c]/[C3]: корневой якорь двигает стену; 4-й пик достигнут;
    # Delta_eff = 0.61 +- 0.45 не равна DSS 3.44 (честно)
    assert d["probe3"]["back_unlocks_root"] is True
    assert d["depth_record_z"] > 8.0
    deb = d["deep"]["delta_eff_best"]
    assert deb is not None and deb["n_peaks_seg"] >= 4
    assert abs(deb["delta_eff"] - 3.44) > 6 * deb["delta_err"]
    assert d["second_pass"]["fit_p_delta"] is None
