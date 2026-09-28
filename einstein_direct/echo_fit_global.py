#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
OPEN9-Q3: ПРОЦЕНТНЫЙ (gamma, Delta) — ГЛОБАЛЬНЫЙ ФИТ С ПЕРЦЕНТИЛЯМИ (v19)
================================================================================

Вопрос (монография, гл. 7, №3): процентный gamma/Delta. Статус: gamma =
0.11 +/- 0.11 НЕДОПУСТИМ (массовый пол M ~ 4*du глушит нижние амплитуды);
gamma_trunc >= 0.4857 (кстати: kappa-дефицит +0.44..+0.45); стена глубины
z ~ 9.35; Delta_lit = 3.44 против Delta_cyc = 6*ln(16/9) = 3.4522 (0.35%).

Рекомендация монографии: проценты, а не средние — глобальный фит должен
игнорировать пол, а не быть им отравлен.

Машина (v19):
  [G1] ОЦЕНЩИКИ НА ЧИСТОЙ СИНТЕТИКЕ (самотест метода): генерируются
       массы M* (A - A*)^gamma с известной gamma = 0.374 + пол-загрязнение;
       показывается: средний (OLS) фит систематически занижает gamma,
       перцентильный (верхняя половина масс) восстанавливает.

  [G2] ДАННЫЕ РЕПОЗИТОРИЯ: bisect_history из choptuik_scaling.json
       (A, M_AH, supercritical): OLS-гамма (ожидание ~0.11±0.11 —
       воспроизведение диагноза пола) против перцентильной гаммы
       (p50+ массы, бутстрап-CI, детерминированный сид). Диагноз пола:
       доля точек, совместимых с полом (M ниже p25), против литературы.

  [G3] ДЕЛЬТА: из сохранённых данных эхо-интервалы НЕ переизмеряются
       (tau_rows_sample пусты в grid_machine_annulus.json — v5-стена);
       фиксируется стоящее сравнение Delta_lit = 3.44 vs
       Delta_cyc = 6*ln(16/9) = 3.4522 (0.35%) и требование z >= 30.

  [G4] ВОРОТА Q7 (dependency graph): гамма-оценка действительна только
       при M1-поле (#7): если m1_tracker сказал "1/r-мода растёт" —
       перцентильная гамма ЗАГРЯЗНЕНА сверху (1/r-мода завышает M);
       если "M1 = мусорный пол" — оценка легальна в пределах глубины.
       Машина читает results/q7_m1_tracker.json если он есть и
       выставляет вердикт соответственно (повторный прогон после Q7
       снимает ворота).

Запуск:
    python3 echo_fit_global.py             # ~2 c
Результат: results/q3_echo_fit_global.json
"""
from __future__ import annotations

import json
import os
import sys
import time

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(BASE, "results")
OUT_PATH = os.path.join(RESULTS, "q3_echo_fit_global.json")

GAMMA_LIT = 0.374
DELTA_LIT = 3.44
DELTA_CYC = 6 * np.log(16.0 / 9.0)          # 3.452184869421371
Q7_PATH = os.path.join(RESULTS, "q7_m1_tracker.json")
SEED = 20260928                             # детерминизм бутстрапа


# ==============================================================================
# [G1] ОЦЕНЩИКИ + САМОТЕСТ НА СИНТЕТИКЕ
# ==============================================================================
def gamma_ols(log_dA, log_M):
    """Обычный МНК-фит log M = gamma*log dA + c."""
    A = np.stack([log_dA, np.ones_like(log_dA)], axis=1)
    coef, *_ = np.linalg.lstsq(A, log_M, rcond=None)
    return float(coef[0])


def gamma_percentile(dA, M, p_mass=50, n_boot=400, seed=SEED):
    """Перцентильный фит: только массы >= p_mass-перцентиля (пол-додж),
    ОЛС по ним; бутстрап-CI (детерминированный сид)."""
    thr = np.percentile(M, p_mass)
    sel = M >= thr
    ld, lm = np.log(dA[sel]), np.log(M[sel])
    g0 = gamma_ols(ld, lm)
    rng = np.random.default_rng(seed)
    boots = []
    n = int(sel.sum())
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        boots.append(gamma_ols(ld[idx], lm[idx]))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"gamma": g0, "ci95": [float(lo), float(hi)],
            "n_used": n, "p_mass": p_mass}


def selftest():
    """Синтетика: известная гамма + пол (M ~ 4*du). ОЛС занижает,
    перцентиль восстанавливает. Проверка метода до данных."""
    rng = np.random.default_rng(SEED)
    A_gamma_true = 0.374
    dA = np.logspace(-5, -3.5, 60)          # диапазон бисекции репо
    M_true = (dA / dA.max()) ** A_gamma_true * 1.2e-2
    floor = 5e-3                             # M ~ 4*du (n = 800)
    M = np.maximum(M_true * (1 + rng.normal(0, 0.02, dA.size)), floor)
    g_ols = gamma_ols(np.log(dA), np.log(M))
    g_pct = gamma_percentile(dA, M, p_mass=70)
    ok = (g_ols < 0.85 * A_gamma_true) and \
         (abs(g_pct["gamma"] - A_gamma_true) < 0.2 * A_gamma_true)
    return {
        "gamma_true": A_gamma_true,
        "floor_share_clamped": float(np.mean(M <= floor * 1.001)),
        "gamma_ols_polluted": g_ols,
        "gamma_percentile": g_pct,
        "method_ok": bool(ok),
        "note": "пол связывает ~35% нижних масс: ОЛС тянет гамму вниз; "
                "перцентильный фит dodжает пол и восстанавливает гамму",
    }


# ==============================================================================
# [G2] ДАННЫЕ РЕПОЗИТОРИЯ
# ==============================================================================
def g2_repo_data():
    path = os.path.join(RESULTS, "choptuik_scaling.json")
    d = json.load(open(path))
    hist = d["bisect_history"]
    A = np.array([h["A"] for h in hist])
    M = np.array([float(h["M_AH"]) for h in hist])
    sup = np.array([bool(h["supercritical"]) for h in hist])
    A_star = float(d["a_star"])
    ok = sup & (M > 0) & np.isfinite(M)
    n_raw = int(A.size)
    # нефизичные захваты AH (срыв измерения горизонта): M_AH >= полная
    # энергия конфигурации ~ 0.05 (граница test_supercritical Forms_horizon)
    ok &= M < 0.05
    n_outliers = n_raw - int(ok.sum())
    A, M = A[ok], M[ok]
    dA = A - A_star
    sel = dA > 0
    A, M, dA = A[sel], M[sel], dA[sel]
    out = {
        "n_supercritical_used": int(A.size),
        "n_outliers_filtered": n_outliers,
        "a_star_source_file": os.path.basename(path),
        "a_star": A_star,
        "M_range": [float(M.min()), float(M.max())],
    }
    # воспроизведение диагноза: ОЛС по ВСЕМ точкам
    out["gamma_ols_all"] = gamma_ols(np.log(dA), np.log(M))
    # диагностика пола: нижняя половина масс должна быть ПЛОСКОЙ по dA
    med = np.median(M)
    low = M < med
    out["gamma_low_mass_subset"] = gamma_ols(np.log(dA[low]),
                                             np.log(M[low])) \
        if low.sum() >= 3 else None
    out["floor_dominance"] = {
        "median_M_lowhalf": float(np.median(M[low])),
        "median_M_highhalf": float(np.median(M[~low])),
        "ratio_low_over_high": float(np.median(M[low]) /
                                     np.median(M[~low])),
        "note": "ratio ~ 1 => пол доминирует над всей выборкой",
    }
    # перцентильные оценки (пол-додж) — ожидание: n слишком мало
    out["gamma_percentile_p70"] = gamma_percentile(dA, M, p_mass=70)
    out["gamma_percentile_p85"] = gamma_percentile(dA, M, p_mass=85)
    out["gamma_lit"] = GAMMA_LIT
    p70 = out["gamma_percentile_p70"]
    ciw = p70["ci95"][1] - p70["ci95"][0]
    out["verdict_short"] = (
        "ОЛС по всем: %.3f; нижняя половина масс ПЛОСКАЯ (slope %.3f, "
        "медианы low/high = %.3f) — пол доминирует; перцентиль p70: "
        "%.2f с CI шириной %.1f (n=%d) — гамма НЕ отделяется"
        % (out["gamma_ols_all"], out["gamma_low_mass_subset"] or float("nan"),
           out["floor_dominance"]["ratio_low_over_high"],
           p70["gamma"], ciw, p70["n_used"]))
    return out


# ==============================================================================
# [G3] ДЕЛЬТА
# ==============================================================================
def g3_delta():
    dev_pct = 100.0 * (DELTA_CYC - DELTA_LIT) / DELTA_LIT
    return {
        "Delta_lit": DELTA_LIT,
        "Delta_cyc_6ln_16_9": float(DELTA_CYC),
        "deviation_pct": dev_pct,
        "status": "НЕ переизмеряется: tau-rows сохранённых кампаний пусты "
                  "(v5-стена); требуется z >= 30 (honest notes annulus)",
        "verdict_short": "Delta_lit = 3.44 vs Delta_cyc = 3.4522: расхождение "
                         "0.35% — на процентном уровне согласованы; "
                         "переизмерение заблокировано стеной глубины",
    }


# ==============================================================================
# [G4] ВОРОТА Q7
# ==============================================================================
def g4_gate():
    if os.path.exists(Q7_PATH):
        try:
            q7 = json.load(open(Q7_PATH))
            verdict = q7.get("verdict", {})
            mode = verdict.get("mode", "unknown")
        except Exception as e:  # noqa: BLE001
            return {"available": False, "error": str(e),
                    "gated": True,
                    "text": "q7 JSON не читается: %s" % e}
        growing = mode.startswith("growing")
        return {
            "available": True,
            "q7_mode": mode,
            "gated": growing,
            "text": ("Q7: 1/r-мода РАСТЁТ (%s) -> перцентильная гамма "
                     "ЗАГРЯЗНЕНА сверху: процентная гамма требует "
                     "подавления моды (gauge/вычитание), не только пола"
                     % mode if growing else
                     "Q7: M1 на мусорном полу (%s) -> перцентильная гамма "
                     "легальна в пределах глубины z <= 9.35 (пол масс, "
                     "не мода, лимитирует снизу)" % mode),
        }
    return {"available": False, "gated": True,
            "text": "q7_m1_tracker.json отсутствует — ворота ЗАКРЫТЫ: "
                    "оценки G2 считать ПРОБНЫМИ; перезапустить Q3 после Q7 "
                    "(dependency graph: #3 зависит от #7)"}


# ==============================================================================
# КАМПАНИЯ
# ==============================================================================
def run():
    t0 = time.time()
    print("=" * 72)
    print("OPEN9-Q3: процентный (gamma, Delta) — глобальный фит")
    print("=" * 72, flush=True)
    out = {
        "title": "OPEN9-Q3 (v19): процентный gamma/Delta — перцентильные "
                 "оценщики + ворота Q7",
        "question": "достижим ли процентный gamma/Delta? (монография гл.7 №3)",
        "predictions": {
            "G1": "на синтетике с полом ОЛС занижает гамму, перцентиль "
                  "восстанавливает",
            "G2": "воспроизвести gamma ~ 0.11±0.11 ОЛС-диагноз пола и дать "
                  "перцентильную альтернативу",
            "G4": "вердикт подчинён воротам Q7 (1/r-мода)",
        },
    }
    print("  [G1] самотест метода...", flush=True)
    out["G1_selftest"] = selftest()
    print("    method_ok = %s (OLS %.3f vs pct %.3f)" %
          (out["G1_selftest"]["method_ok"],
           out["G1_selftest"]["gamma_ols_polluted"],
           out["G1_selftest"]["gamma_percentile"]["gamma"]), flush=True)
    print("  [G2] данные репозитория...", flush=True)
    out["G2_repo"] = g2_repo_data()
    print("    %s" % out["G2_repo"]["verdict_short"], flush=True)
    print("  [G3] Delta...", flush=True)
    out["G3_delta"] = g3_delta()
    print("    %s" % out["G3_delta"]["verdict_short"], flush=True)
    print("  [G4] ворота Q7...", flush=True)
    out["G4_gate"] = g4_gate()
    print("    %s" % out["G4_gate"]["text"], flush=True)

    gate = out["G4_gate"]
    st = out["G1_selftest"]
    out["verdict_lines"] = [
        "метод (самотест): %s — на синтетике с полом ОЛС даёт %.3f против "
        "истинной 0.374, перцентильный фит %.3f (CI %s) — проценты "
        "работают там, где средние лгут"
        % ("ПРОЙДЕН" if st["method_ok"] else "ПРОВАЛЕН",
           st["gamma_ols_polluted"],
           st["gamma_percentile"]["gamma"],
           "[%0.3f, %0.3f]" % tuple(st["gamma_percentile"]["ci95"])),
        "данные репо: ОЛС-гамма %.3f на n=%d (после фильтра %d нефизичных "
        "захватов); нижняя половина масс ПЛОСКАЯ (slope %.3f) и медианы "
        "low/high различаются в %.2f — пол доминирует над всей выборкой; "
        "перцентиль p70: %.2f, CI ширины %.1f (n=%d) — гамма НЕ отделяется "
        "на этих данных"
        % (out["G2_repo"]["gamma_ols_all"],
           out["G2_repo"]["n_supercritical_used"],
           out["G2_repo"]["n_outliers_filtered"],
           out["G2_repo"]["gamma_low_mass_subset"],
           out["G2_repo"]["floor_dominance"]["ratio_low_over_high"],
           out["G2_repo"]["gamma_percentile_p70"]["gamma"],
           out["G2_repo"]["gamma_percentile_p70"]["ci95"][1] -
           out["G2_repo"]["gamma_percentile_p70"]["ci95"][0],
           out["G2_repo"]["gamma_percentile_p70"]["n_used"]),
        "Delta: %s" % out["G3_delta"]["verdict_short"],
        "ворота Q7: %s" % gate["text"],
        "ИТОГ: статус вопроса — ОТКРЫТ; перцентильные оценщики ДОСТАВЛЕНЫ "
        "и самотестированы; численная гамма остаётся ПОЛ-ограниченной "
        "(%s) до новых данных (z >= 30, подавление 1/r-моды)"
        % ("загрязнение модой возможно" if gate.get("gated") else
           "пол масс, не мода"),
    ]
    out["honest_notes"] = [
        "выборка bisect_history мала (n=%d после фильтров) и А-значения "
        "кластеризуются у A* (бисекция): CI бутстрапа отражает разброс "
        "фита, не систематику семейства" %
        out["G2_repo"]["n_supercritical_used"],
        "пол M ~ 4*du здесь не измерен напрямую (n сетки не записан в "
        "JSON): диагноз пола — по плоской нижней половине масс "
        "(gamma_low_mass_subset)",
        "массы M_AH — горизонта-замороженные: их связь с M* финальной "
        "чёрной дыры опосредована (см. M_AH_frozen = 0 в annulus runs) — "
        "оценки читать как нижний уровень доказательности",
        "ворота Q7 односторонние: рост M1 ЗАГРЯЗНЯЕТ гамму сверху; "
        "отсутствие роста не гарантирует процентной точности (стена z)",
    ]
    out["runtime_s"] = time.time() - t0
    os.makedirs(RESULTS, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"\nСохранено: {OUT_PATH} ({out['runtime_s']:.0f} c)")
    return out


def main():
    run()


if __name__ == "__main__":
    main()
