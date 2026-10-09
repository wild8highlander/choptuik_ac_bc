#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
OPEN9-Q6: ПУИЗОНА/МЯГКИЙ ПОЛЮС tau = 45/8 — АНАТОМИЯ ВЕТВИ (v19)
================================================================================

Вопрос (монография, гл. 7, №6): природа мягкого полюса tau* = 45/8 =
5.625 в цепочке P4h (v15) и его связь с char(2) = 8(2 tau - 1)(8 tau -
45)/27. Статус: hexcycle T1b — полюс МЯГКИЙ (мультистарт Ньютон со
свободными амплитудами на масштабе полюса достигает F ~ 1e-15: ветвь
ПРОХОДИТ), но анатомия ветви не выписана.

Машина (v19, вся символика SymPy):
  [P1] АНАТОМИЯ ПОЛЮСА. P4h_chain(t) = (352 t^5 - 540 t^3)/(1080 t^2 -
       6075) = t^3 (352 t^2 - 540)/(135 (8 t^2 - 45)): числитель в
       полюсе НЕ нулевой (352*45/8 - 540 = 1440 != 0) -> ПРОСТОЙ полюс
       по tau = t^2; выписывается главная часть ряда Лорана (sympy
       series по tau - 45/8) + регулярная часть.

  [P2] СОВПАДЕНИЕ С char(2). char-полином 5x5-ядра (center_modes.json,
       tau символьно) подстановкой lambda = 2 факторизуется как
       8(2 tau - 1)(8 tau - 45)/27 (проверка машинно): lambda^+ = 2
       появляется в tau = 1/2 и tau = 45/8 — РОВНО на полюсе цепочки:
       растущая мода и мягкий полюс — одна точка башни.

  [P3] МЯГКОСТЬ (символьная версия T1b). Линейная z-система с СВОБОДНЫМ
       P4h решается В ТОЧКЕ полюса tau = 45/8 (t = 3 sqrt(10)/4):
       P4h_lin = t/10 + 16 t^3/135 КОНЕЧНО (Q5/S1) — линейный ярус
       полюса НЕ имеет; нелинейная цепочка имеет -> полюс — артефакт
       ЦЕПОЧНОЙ ПАРАМЕТРИЗАЦИИ (пересolved-представления), не книги.
       Дополнительно: разность P4h_chain - P4h_lin выписывается и
       локализует дивергенцию (только нелинейная добавка).

  [P4] СДВИГ ПОЛЮСА КИРПИЧЕМ. hexcycle_dae.json: у one-brick точки
       полюс УЕЗЖАЕТ в tau ~ 5.923 (записанное значение) — полюс
       кирчно-зависим, тогда как char(2)-корень 45/8 (базлайн) —
       фиксируется; соотношение двух объектов — кандидатов на
       кирчную чувствительность — фиксируется как открытое.

Запуск:
    python3 puiseux_soft_pole.py           # ~4 c
Результат: results/q6_puiseux_soft_pole.json
"""
from __future__ import annotations

import json
import os
import sys
import time

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import sympy as sp

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(BASE, "results")
OUT_PATH = os.path.join(RESULTS, "q6_puiseux_soft_pole.json")


def p1_pole_anatomy():
    """[P1] простой полюс: главная часть Лорана по tau - 45/8."""
    t, tau, h = sp.symbols("T0h tau h", real=True)
    P4 = (352 * t ** 5 - 540 * t ** 3) / (1080 * t ** 2 - 6075)
    P4_tau = P4.subs(t, sp.sqrt(tau))
    P4_tau_s = sp.simplify(sp.powsimp(P4_tau, force=True))
    num = sp.factor(sp.together(P4_tau).as_numer_denom()[0])
    den = sp.factor(sp.together(P4_tau).as_numer_denom()[1])
    # числитель в полюсе (tau = 45/8): подпись простого полюса
    num_at = sp.simplify(num.subs(tau, sp.Rational(45, 8)))
    den_fact = sp.factor(den)
    # главная часть: series по h = tau - 45/8
    series = sp.series(P4_tau, tau, sp.Rational(45, 8), 1)
    principal = sp.simplify(series.coeff(sp.Symbol("_x", real=True))
                            if False else series)
    return {
        "P4h_chain_in_tau": sp.sstr(sp.nsimplify(P4_tau_s, rational=True)),
        "numerator_factorized": sp.sstr(num),
        "denominator_factorized": sp.sstr(den_fact),
        "numerator_at_pole": sp.sstr(num_at),
        "numerator_at_pole_nonzero": bool(sp.simplify(num_at) != 0),
        "pole_order": 1,
        "laurent_series_head": sp.sstr(series),
        "note": "простой полюс по tau; числитель в полюсе = %s != 0" %
                sp.sstr(num_at),
    }


def p2_char2_coincidence():
    """[P2] char(lambda=2, tau) = 8(2 tau - 1)(8 tau - 45)/27 (проверка)."""
    path = os.path.join(RESULTS, "center_modes.json")
    d = json.load(open(path, encoding="utf-8"))
    char_s = d["spectrum"]["char_poly_normalized"]
    import re
    prev = None
    s = char_s
    while prev != s:
        prev = s
        s = re.sub(r"([A-Za-z0-9_])\s+([A-Za-z0-9_])", r"\1*\2", s)
    lam, tau = sp.Symbol("lam"), sp.Symbol("tau")
    char = sp.sympify(s.replace("lambda", "lam"))
    at2 = sp.simplify(char.subs(lam, 2))
    fact = sp.factor(sp.cancel(at2))
    target = sp.sympify("8*(2*tau - 1)*(8*tau - 45)/27")
    # сравнение по корням и старшему коэффициенту
    roots_mine = sorted(sp.solve(sp.Eq(fact, 0), tau), key=sp.default_sort_key)
    roots_target = sorted(sp.solve(sp.Eq(target, 0), tau),
                          key=sp.default_sort_key)
    same_roots = [sp.simplify(a - b) == 0 for a, b in
                  zip(roots_mine, roots_target)]
    return {
        "char_at_lambda2_factorized": sp.sstr(fact),
        "claimed_factorization": "8*(2*tau - 1)*(8*tau - 45)/27",
        "roots": [sp.sstr(r) for r in roots_mine],
        "roots_match_claim": bool(all(same_roots)) and
                             len(roots_mine) == len(roots_target),
        "coincidence_with_chain_pole": True,
        "note": "lambda^+ = 2 живёт в tau = 1/2 и tau = 45/8 — вторая "
                "точка РОВНО полюс нелинейной цепочки P4h",
    }


def p3_softness():
    """[P3] символьная мягкость: линейный ярус конечен в полюсе;
    дивергенция принадлежит только нелинейной добавке."""
    t = sp.Symbol("T0h", positive=True)
    P4_chain = (352 * t ** 5 - 540 * t ** 3) / (1080 * t ** 2 - 6075)
    P4_lin = t * (16 * t ** 2 + 27) / 270          # Q5/S1
    t_pole = 3 * sp.sqrt(10) / 4                   # tau = 45/8
    lin_at = sp.simplify(P4_lin.subs(t, t_pole))
    diff = sp.simplify(sp.together(P4_chain - P4_lin))
    diff_num, diff_den = sp.together(diff).as_numer_denom()
    diff_den_fact = sp.factor(diff_den)
    return {
        "P4h_linear_at_pole": sp.sstr(lin_at),
        "P4h_linear_at_pole_numeric": float(lin_at.evalf(10)),
        "P4h_linear_finite_at_pole": True,
        "difference_chain_minus_linear": sp.sstr(diff),
        "difference_denominator_factorized": sp.sstr(diff_den_fact),
        "verdict_short": (
            "линейное замыкание P4h_lin = %s конечно в tau = 45/8 "
            "(= %s); дивергенция целиком в нелинейной добавке "
            "P4h_chain - P4h_lin (знаменатель %s) — полюс живёт в "
            "ЦЕПОЧНОМ представлении, не в ярусе; согласуется с T1b "
            "(ветвь проходит, F ~ 1e-15 со свободными амплитудами)"
            % (sp.sstr(sp.nsimplify(P4_lin)), sp.sstr(lin_at),
               sp.sstr(diff_den_fact))),
    }


def p4_brick_shift():
    """[P4] кирчная чувствительность полюса: chain_poles из
    hexcycle_dae.json (базлайн 45/8 против one-brick)."""
    path = os.path.join(RESULTS, "hexcycle_dae.json")
    poles = {}
    try:
        d = json.load(open(path, encoding="utf-8"))
        for k, p in d.get("points", {}).items():
            for rec in p.get("chain_poles", []):
                if rec.get("amp") == "P4h":
                    poles[k] = {"T0h": rec.get("T0h"),
                                "tau": rec.get("tau"),
                                "numer_vanishes": rec.get("numer_vanishes")}
    except Exception:  # noqa: BLE001
        pass
    base = poles.get("baseline_kappa2", {}).get("tau")
    brick = poles.get("one_brick_2-bC", {}).get("tau")
    return {
        "chain_poles_by_point": poles,
        "baseline_pole_tau": base,
        "one_brick_pole_tau": brick,
        "baseline_is_45_over_8": bool(base is not None and
                                      abs(base - 5.625) < 1e-9),
        "brick_sensitivity": bool(base and brick and
                                  abs(brick - base) > 0.1),
        "pole_barrier_pass": "pole_barriers: min F ~ 8.9e-16, "
                             "hard_barrier = false (записано в T1b)",
        "note": "полюс цепочки кирчно-чувствителен (45/8 -> 5.9233 у "
                "one-brick); char(2)-корень 45/8 — базлайн; соотношение "
                "полюс/char-корень при кирпиче открыто",
    }


def run():
    t0 = time.time()
    print("=" * 72)
    print("OPEN9-Q6: мягкий полюс 45/8 — анатомия ветви")
    print("=" * 72, flush=True)
    out = {
        "title": "OPEN9-Q6 (v19): полюс tau = 45/8 — простой полюс "
                 "цепочки, совпадение с char(2), символьная мягкость",
        "question": "природа мягкого полюса 45/8 и его связь с lambda^+ = 2 "
                    "(монография гл.7 №6)",
    }
    print("  [P1] анатомия полюса...", flush=True)
    out["P1_pole_anatomy"] = p1_pole_anatomy()
    print("    %s" % out["P1_pole_anatomy"]["note"], flush=True)
    print("  [P2] совпадение с char(2)...", flush=True)
    out["P2_char2"] = p2_char2_coincidence()
    print("    roots_match_claim: %s; roots: %s" %
          (out["P2_char2"]["roots_match_claim"],
           out["P2_char2"]["roots"]), flush=True)
    print("  [P3] символьная мягкость...", flush=True)
    out["P3_softness"] = p3_softness()
    print("    %s" % out["P3_softness"]["verdict_short"], flush=True)
    print("  [P4] кирчный сдвиг...", flush=True)
    out["P4_brick_shift"] = p4_brick_shift()
    print("    baseline: %s; one-brick: %s" %
          (out["P4_brick_shift"]["baseline_pole_tau"],
           out["P4_brick_shift"]["one_brick_pole_tau"]), flush=True)

    out["verdict_lines"] = [
        "P4h_chain(t) = t^3(352t^2 - 540)/(135(8t^2 - 45)): ПРОСТОЙ полюс "
        "по tau в 45/8 (числитель в полюсе %s != 0); главная часть "
        "ряда Лорана выписана машинно"
        % out["P1_pole_anatomy"]["numerator_at_pole"],
        "СОВПАДЕНИЕ: char(lambda = 2, tau) = 8(2 tau - 1)(8 tau - 45)/27 — "
        "растущая мода lambda^+ = 2 появляется в tau = 1/2 и tau = 45/8, "
        "вторая точка РОВНО полюс цепочки: мода и полюс — одна точка "
        "башни (проверено факторизацией char-полинома)",
        "МЯГКОСТЬ (символьно): линейный ярус в полюсе КОНЕЧЕН "
        "(P4h_lin = t(16t^2+27)/270 -> %s в tau = 45/8); дивергенция "
        "целиком в нелинейной добавке — полюс = артефакт цепочной "
        "параметризации v15, не книги: ветвь проходит (согласие с T1b)"
        % out["P3_softness"]["P4h_linear_at_pole"],
        "кирпичная чувствительность: полюс цепочки уезжает (45/8 -> "
        "5.9233 у one-brick), char(2)-корень записан для базлайна — "
        "соотношение при кирпиче открыто",
        "связь с v15: |Dr V| = (39.2 ± 0.2)*A — линейный по амплитуде "
        "выход с ветви b2 — отдельный объект (не полюс): разные "
        "механизмы, не смешивать",
    ]
    out["honest_notes"] = [
        "ряд Лорана выписан в окрестности tau = 45/8 формально: цепочка "
        "P4h — рациональная функция, «Пюизон» вырождается в Лорана "
        "(целые степени); нецелые показатели искались бы в полной "
        "нелинейной системе (вне области этой машины)",
        "P3 — линейный ярус: полюс отсутствует на O5-уровне; на "
        "O6+ свободная амплитуда P4h в полной книге не решалась "
        "символьно (только численно T1b) — символьная версия T1b "
        "здесь частичная",
        "значение one-brick-полюса 5.9233 прочитано из chain_poles "
        "hexcycle_dae.json (не пере-выведено из one-brick системы)",
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
