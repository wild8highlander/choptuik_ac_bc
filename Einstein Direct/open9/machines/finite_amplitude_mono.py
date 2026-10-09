#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
OPEN9-Q2: ФАНТОМНЫЙ ОСТАТОК pi/30 — КОНЕЧНОАМПЛИТУДНЫЙ МЕХАНИЗМ (v19)
================================================================================

Вопрос (монография, гл. 7, №2): Im lambda фантома = 0.107731 против
pi/30 = 0.104720 — остаток +2.88%. Линейный мир аннигилирует остаток
ТОЧНО (march_delta_mono.json: delta_mono = 0, рост за эхо < 2.8e-14,
фаза 2.7e-8 = пол дефектности ~ sqrt(eps)). Зазор 3.0e-3 = 1e4..1e5
границ марша -> остаток НЕ может жить в линейном секторе; гипотеза:
конечноамплитудный эффект, носитель — нильпотентный Йордан-2 блок
(dd_closure: B^2 = 0 ТОЧНО, spec(B) = {0, 0} дефектный).

Машина (v19):
  [F1] РОБАСТНОСТЬ ОСТАТКА. Две НЕЗАВИСИМЫЕ линейные системы дают
       фантомы с Im lambda ~ 0.1077 (кирпичный B4, rel_sigma 1e-6) и
       ~ 0.1080 (карандаш spectrum_tau_star, rel_sigma 2.1e-6):
       разброс систем 0.22% против сдвига к pi/30 +2.88%..+3.10% —
       сдвиг структурный, не системный мусор.

  [F2] НЕСОВМЕСТНОСТЬ С ЛИНЕЙНЫМ СЕКТОРОМ (машинно). Остаток
       |Im lambda - pi/30| / pi/30-нормировка против границы марша:
       фактор >= 1e4 — линейная монодромия за эхо e^{lambda Delta} с
       Im lambda = pi/30 + r потребовала бы delta_mono = sigma*r,
       запрещённую маршем (рост < 3.8e-14 за эхо).

  [F3] НОРМАЛЬНАЯ ФОРМА ЙОРДАН-2: ЗАКОН МАСШТАБИРОВАНИЯ. Для
       дефектного нильпотентного блока J2 (N^2 = 0) возмущение
       конечной амплитуды eps*N расщепляет спектр как
       lambda(eps) = +/- sqrt(eps * n12 * n21) — частота ~ eps^{1/2}
       (sympy-вывод + numpy-фит показателя на минимальной модели).
       Для ПОЛУПРОСТОЙ пары (центр) сдвиг частоты ~ eps или eps^2
       (первый коэффициент Ляпунова). Это ФАЛЬСИФИЦИРУЕМЫЙ
       дискриминатор: показатель p = 1/2 (Йордан-2 монодромия)
       против p = 1..2 (ляпуновский центр).

  [F4] ПРОТОКОЛ ИЗМЕРЕНИЯ. Лестница амплитуд A in {A*, A*/2, A*/4}
       (через eps марша), извлечение ближайшей комплексной пары на
       каждой амплитуде, фит p в Im lambda - pi/30 ~ A^p. С
       СОХРАНЁННЫМИ данными (одна амплитуда) показатель НЕ
       измеряется — честный статус: механизм идентифицирован,
       экспонента не измерена.

Запуск:
    python3 finite_amplitude_mono.py       # ~5 c
Результат: results/q2_finite_amplitude_mono.json
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
import sympy as sp

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(BASE, "results")
OUT_PATH = os.path.join(RESULTS, "q2_finite_amplitude_mono.json")

PI_30 = float(sp.pi / 30)                 # 0.10471975511965977
IM_BRICK = 0.10773111490778432            # brick_scan_tick B4 best hit (pi/7)
IM_PENCIL = 0.10796860584436327           # spectrum_tau_star pencil phantom
MARCH_GROWTH_BOUND = 2.7866597918091817e-14   # march_delta_mono (baseline)
MARCH_PHASE_FLOOR = 2.716815383774294e-08     # ~ sqrt(eps) дефектный пол
PHANTOM_GAP_SCALE = 0.0030368                 # march_delta_mono


# ==============================================================================
# [F1] РОБАСТНОСТЬ ОСТАТКА ПО ДВУМ СИСТЕМАМ
# ==============================================================================
def f1_robustness():
    r_brick = (IM_BRICK - PI_30) / PI_30
    r_pencil = (IM_PENCIL - PI_30) / PI_30
    spread = abs(IM_PENCIL - IM_BRICK) / PI_30
    return {
        "im_lambda_brick_B4": IM_BRICK,
        "im_lambda_pencil": IM_PENCIL,
        "pi_over_30": PI_30,
        "residual_brick_pct": 100.0 * r_brick,
        "residual_pencil_pct": 100.0 * r_pencil,
        "system_spread_pct": 100.0 * spread,
        "structural_ratio": (100.0 * r_brick) / (100.0 * spread),
        "verdict_short": (
            "сдвиг +%.2f%%..+%.2f%% при разбросе систем %.2f%% — "
            "сдвиг в ~%.0f раз больше разброса: структурный, не системный"
            % (100 * r_brick, 100 * r_pencil, 100 * spread,
               100 * r_brick / (100 * spread))),
    }


# ==============================================================================
# [F2] НЕСОВМЕСТНОСТЬ С ЛИНЕЙНЫМ СЕКТОРОМ
# ==============================================================================
def f2_linear_inconsistency():
    resid = abs(IM_BRICK - PI_30)
    factor_growth = resid / MARCH_GROWTH_BOUND
    factor_floor = resid / MARCH_PHASE_FLOOR
    return {
        "residual_abs": resid,
        "march_growth_bound_per_echo": MARCH_GROWTH_BOUND,
        "march_phase_floor_per_echo": MARCH_PHASE_FLOOR,
        "inconsistency_factor_vs_growth_bound": factor_growth,
        "inconsistency_factor_vs_phase_floor": factor_floor,
        "verdict_short": (
            "остаток %.3e = %.3g границы роста марша (и %.3g пола "
            "дефектности sqrt(eps)) — линейный сектор НЕ может нести "
            "остаток: требуется конечноамплитудный механизм"
            % (resid, factor_growth, factor_floor)),
    }


# ==============================================================================
# [F3] НОРМАЛЬНАЯ ФОРМА ЙОРДАН-2 — ЗАКОН МАСШТАБИРОВАНИЯ
# ==============================================================================
def f3_jordan2_scaling():
    """Минимальная модель: ФИКСИРОВАННЫЙ нильпотент B = [[0,1],[0,0]]
    (масштаб книги: ||B|| ~ 5.74, B^2 = 0) + возмущение eps*N.
    Характер. полином: lambda^2 - eps(a+b)lambda + eps^2*ab - eps*d*(1+eps*c)
    = 0; при a = b = c = 0: lambda = ±sqrt(eps*d) — ЧАСТОТА ~ eps^{1/2}.
    numpy-фит показателя p в |Im lambda| ~ eps^p (d < 0 — мнимые ветви).
    Контраст: полупростая пара (центр) — сдвиг частоты ~ A^2
    (первый коэффициент Ляпунова)."""
    a, b, c, d, eps, lam = sp.symbols("a b c d eps lam", real=True)
    B = sp.Matrix([[0, 1], [0, 0]])                # B^2 = 0, дефектный
    N = sp.Matrix([[a, c], [d, b]])                # общий порядок eps
    M = B + eps * N
    cp = sp.expand((M - lam * sp.eye(2)).det())
    cp_reduced = sp.simplify(cp.subs({a: 0, b: 0, c: 0}))
    ev = [sp.simplify(e) for e in sp.solve(cp_reduced, lam)]
    # numpy: численный показатель p в |Im lambda| ~ eps^p (n21 < 0)
    epss = np.logspace(-8, -2, 25)
    ims = []
    for e_ in epss:
        Mnum = np.array([[0.0, 1.0], [-e_, 0.0]])  # B + eps*N, d = -1
        evn = np.linalg.eigvals(Mnum)
        ims.append(max(abs(evn.imag)))
    ims = np.asarray(ims)
    p, c = np.polyfit(np.log(epss), np.log(ims), 1)
    # контраст: полупростая (нормальная) пара — сдвиг частоты линейный по
    # квадратичной амплитуде: omega_eff = omega0 + c1*A^2 (ляпуновский)
    return {
        "model": "lambda(eps) для B + eps*N, B = [[0,1],[0,0]] (B^2 = 0), "
                 "N — общий порядок eps",
        "char_poly_reduced": sp.sstr(cp_reduced),
        "symbolic_eigenvalues": [sp.sstr(e) for e in ev],
        "predicted_exponent_jordan2": 0.5,
        "predicted_exponent_jordan2_exact": "1/2",
        "numpy_fit_exponent_p": float(p),
        "numpy_fit_residual_max": float(np.max(np.abs(
            np.log(ims) - (p * np.log(epss) + c)))),
        "semisimple_center_exponent": "p = 2 в амплитуде A "
                                      "(omega_eff = omega0 + c1 A^2)",
        "discriminator": (
            "p = 1/2 в eps (Йордан-2) vs p = 2 в A: измерение по лестнице "
            "амплитуд различает носителя остатка"),
    }


# ==============================================================================
# [F4] ПРОТОКОЛ
# ==============================================================================
def f4_protocol():
    return {
        "amplitude_ladder": ["A*", "A*/2", "A*/4 (eps-марш)"],
        "extract": "ближайшая к Im = pi/30 комплексная пара (sigma_min-фильтр "
                   "сессии 14: rel_sigma_min < 1e-8 — отсечение фантомов "
                   "карандаша)",
        "fit": "log|Im lambda - pi/30| vs log A -> p; p = 1/2 => Йордан-2 "
               "монодромия; p = 2 => ляпуновский центр; p нецелое/1/2-неверно "
               "=> новый носитель",
        "status_with_saved_data": "НЕ ИЗМЕРЕНО: в сохранённых данных фантом "
                                  "извлечён на ОДНОЙ амплитуде (A*) — "
                                  "показатель требует новой лестницы (v19+)",
    }


# ==============================================================================
# КАМПАНИЯ
# ==============================================================================
def run():
    t0 = time.time()
    print("=" * 72)
    print("OPEN9-Q2: фантомный остаток pi/30 — конечноамплитудный механизм")
    print("=" * 72, flush=True)
    out = {
        "title": "OPEN9-Q2 (v19): остаток pi/30 — робастность, "
                 "несовместность с линейным сектором, закон Йордан-2",
        "question": "почему Im lambda фантома = 0.107731, а не pi/30 = "
                    "0.104720 (+2.88%)? (монография гл.7 №2)",
        "inputs": {
            "march_delta_mono.json": "delta_mono = 0 (рост 2.8e-14, фаза "
                                     "2.7e-8 = пол дефектности); "
                                     "phantom_gap_scale = 0.0030368",
            "brick_scan_tick.json B4": "best hit [-0.10644, -0.10773] "
                                       "(rel_sigma 1e-6 уровень)",
            "spectrum_tau_star.json": "pencil phantom +-0.10797 "
                                      "(rel_sigma_min 2.1e-6)",
            "dd_closure / _m2_B_baseline.npy": "B^2 = 0 ТОЧНО, spec = {0,0} "
                                               "дефектный (норма ~5.74)",
        },
    }
    print("  [F1] робастность...", flush=True)
    out["F1_robustness"] = f1_robustness()
    print("    %s" % out["F1_robustness"]["verdict_short"], flush=True)
    print("  [F2] несовместность с линейным сектором...", flush=True)
    out["F2_linear_inconsistency"] = f2_linear_inconsistency()
    print("    %s" % out["F2_linear_inconsistency"]["verdict_short"],
          flush=True)
    print("  [F3] нормальная форма Йордан-2...", flush=True)
    out["F3_jordan2_scaling"] = f3_jordan2_scaling()
    print("    numpy p = %.4f (предсказание 1/2)" %
          out["F3_jordan2_scaling"]["numpy_fit_exponent_p"], flush=True)
    print("  [F4] протокол...", flush=True)
    out["F4_protocol"] = f4_protocol()

    out["verdict_lines"] = [
        "остаток +2.88% (кирпичный B4) / +3.10% (карандаш tau*) при "
        "разбросе систем 0.22% — сдвиг структурный (~13x разброса)",
        "несовместность машинно: остаток 3.0e-3 = 1.1e11 границы роста "
        "марша (1e4..1e5 даже против пола дефектности sqrt(eps)) — "
        "линейная монодромия НЕ может нести остаток; linear-world "
        "аннигиляция (delta_mono = 0) подтверждена с обеих сторон",
        "носитель-кандидат: дефектный Йордан-2 (B^2 = 0 точно) — "
        "минимальная модель даёт lambda(eps) = ±sqrt(eps*n12*n21): "
        "частота ~ eps^{1/2} (numpy-фит p = %.4f на модели)" %
        out["F3_jordan2_scaling"]["numpy_fit_exponent_p"],
        "ФАЛЬСИФИЦИРУЕМЫЙ дискриминатор: Йордан-2 => p = 1/2 в eps; "
        "ляпуновский центр (полупростая пара) => p = 2 в A; текущие "
        "данные (одна амплитуда) показатель НЕ различают",
        "согласование с Q1: pi/30 — pi-квант (трансцендентный вход); "
        "остаток как конечноамплитудная добавка к трансцендентной "
        "константе не противоречит барьеру Q1",
    ]
    out["honest_notes"] = [
        "показатель p НЕ ИЗМЕРЕН: требуется лестница амплитуд с "
        "извлечением пары на каждой (протокол F4, кампания v19+); "
        "вывод F3 — модельный, не PDE-уровень",
        "минимальная модель 2x2 иллюстративна: в полной системе "
        "возмущение конечной амплитуды — не диагональное; закон "
        "sqrt(eps) — робастный вывод дефектности, коэффициент — нет",
        "фантомный статус: оба Im lambda получены sigma_min-фильтром "
        "(гарантии нет) — релевантность пары 0.108/pi/30 сама зависит "
        "от того, что пара не фантом карандаша; марш это не проверяет",
        "связь с v15: |Dr(x0)V(x0)| = (39.2±0.2)*A — конечноамплитудный "
        "выход с ветви b2 линейный по A (не sqrt): носители могут "
        "различаться (выход vs фаза)",
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
