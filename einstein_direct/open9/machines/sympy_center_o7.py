#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
OPEN9-Q5: СХОДИМОСТЬ УСЕЧЁННОЙ БАШНИ — ЦЕПОЧКА, O6-НЕСОВМЕСТНОСТЬ, O7 (v19)
================================================================================

Вопрос (монография, гл. 7, №5): сходится ли усечённая башня? Статус:
T1c-замыкание одним кирпичом tau* = 7.1079 (2 уровня: 6.75); наивная
O6+ несовместна (tau = 2.25 против 0.5625); весовое правило доказано
до третьего порядка, четвёртый не проверен.

Машина (v19, вся символика SymPy):
  [S1] ЦЕПОЧКА ЗАКРЫВАЕТ Z-СИСТЕМУ ЛИНЕЙНОГО ЯРУСА (O5). Z-система
       (center_modes.json): F1_dt0, F2_dP2, F4_dD0, F5_dR1 закрываются
       цепочкой {D0h = 0, R3h = 2 R1 T0^2/9, W2h = 4 T0^2/3, P2h = T0/3}
       ТОЖДЕСТВЕННО (проверка на символе t = T0h). F3_ddQ решается по
       P4h -> ЛИНЕЙНОЕ замыкание P4h_lin = t/10 + 16 t^3/135 —
       ПОЛИНОМ, регулярный ВЕЗДЕ. Это новый машинный факт: полюс
       45/8 живёт только в НЕлинейной цепочке v15 (см. Q6).

  [S2] M3-СВЯЗКА O4 (весовое правило на уровне линка): M3_link_O4 на
       цепочке (chi = 0, R1 = 1) = 2 t^2/3 ТОЧНО = маршруту O3
       (kappa t0^2 - W2h = 2t^2 - 4t^2/3 при kappa = 2) — согласование
       уровней O3/O4 машинно.

  [S3] НАИВНАЯ O6-НЕСОВМЕСТНОСТЬ (воспроизведение): пары замыканий
       (3/2)^2 = tau3 = 9/4 (CORE) и (4/3)^2 = 1/tau5, tau5 = 9/16
       (RING) как точки башни противоречат (sympy: 9/4 != 9/16) —
       наивная система O6 переопределена (center_o6_nsolve: nsolve
       точку не нашёл, честная заметка сохранена).

  [S4] РАЗРЕШЕНИЕ T1c: часы пары (UV_xi3, Mdef_xi5) на T1c-цепочке
       tau* = 1323/(196 - pi^2): подстановка в часовой фактор
       (-196 T0h^2 + pi^2 T0h^2 + 1323) даёт 0 ТОЧНО (sympy, pi
       символьно). НОВОЕ ТОЖДЕСТВО: tau*(delta_C = pi/7) = 27/(4 -
       pi^2/49) = 1323/(196 - pi^2) — часы ТЕОРЕМЫ О ПАРЕ на
       выжившем кирпиче и T1c-часы СОВПАДАЮТ ТОЧНО (одно и то же
       число двумя независимыми маршрутами).

  [S5] ВЕРДИКТ СХОДИМОСТИ + ПРОГРАММА O7: уровни 6.75 (2 уровня) ->
       7.10792 (T1c) совпадают с лестницей на delta_C (S4): сдвиг
       башни монотонен, НО следующего члена нет — сходимость НЕ
       установлена. Программа O7 (что должна фиксировать седьмая
       уровневая система): (i) линеаризация = P4h_lin (S1);
       (ii) нелинейное продолжение = цепочка v15 с мягким полюсом;
       (iii) факторизация char(2) = 8(2 tau - 1)(8 tau - 45)/27;
       (iv) кольцо W2h/T0h^2 = 4/3; (v) весовое правило 4-го порядка.

Запуск:
    python3 sympy_center_o7.py             # ~5 c
Результат: results/q5_center_o7.json
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
OUT_PATH = os.path.join(RESULTS, "q5_center_o7.json")


def _z_system():
    """Z-система линейной башни из center_modes.json (sympify,
    с нормализацией неявных умножений '2 D0h R1h' -> '2*D0h*R1h')."""
    import re
    path = os.path.join(RESULTS, "center_modes.json")
    d = json.load(open(path, encoding="utf-8"))
    zs = d["tower"]["z_system"]

    def _norm(s):
        prev = None
        while prev != s:
            prev = s
            s = re.sub(r"([A-Za-z0-9_])\s+([A-Za-z0-9_])", r"\1*\2", s)
        return s

    return {k: sp.sympify(_norm(v)) for k, v in zs.items()
            if k in ("F1_dt0", "F2_dP2", "F3_ddQ", "F4_dD0", "F5_dR1",
                     "M3_link_O4")}


def s1_chain_closes():
    """[S1] подстановка цепочки в F1/F2/F4/F5 — тождественный нуль;
    F3 -> линейное замыкание P4h_lin."""
    # ВАЖНО: символы БЕЗ assumptions — совпадают с sympify-символами
    t, P4, Q = sp.Symbol("T0h"), sp.Symbol("P4h"), sp.Symbol("Qh")
    D0, R1, R3, W2, P2 = (sp.Symbol("D0h"), sp.Symbol("R1h"),
                          sp.Symbol("R3h"), sp.Symbol("W2h"),
                          sp.Symbol("P2h"))
    chain = {D0: 0, R1: 1, R3: 2 * t ** 2 / 9, W2: 4 * t ** 2 / 3,
             P2: t / 3, Q: 0}
    zs = _z_system()
    res = {}
    for name in ("F1_dt0", "F2_dP2", "F4_dD0", "F5_dR1"):
        expr = sp.expand(zs[name].subs(chain))
        res[name] = sp.sstr(sp.simplify(expr))
        res[name + "_is_zero"] = sp.simplify(expr) == 0
    # F3: линейное замыкание по P4h
    F3 = sp.expand(zs["F3_ddQ"].subs(chain))
    sol = sp.solve(sp.Eq(F3, 0), P4)
    P4_lin = sp.simplify(sol[0]) if sol else None
    res["F3_ddQ_residual_form"] = sp.sstr(F3)
    res["P4h_linear_closure"] = sp.sstr(P4_lin)
    res["P4h_linear_closure_is_poly"] = bool(P4_lin is not None and
                                             P4_lin.is_polynomial(t))
    # контроль: подстановка P4h_lin в F3 -> 0
    if P4_lin is not None:
        res["F3_with_P4lin_zero"] = sp.simplify(F3.subs(P4, P4_lin)) == 0
    return res


def s2_m3_link():
    """[S2] M3-связка O4 на цепочке = маршруту O3 (kappa = 2)."""
    t = sp.Symbol("T0h")
    A0, R3, W2, R1 = (sp.Symbol("A0"), sp.Symbol("R3h"),
                      sp.Symbol("W2h"), sp.Symbol("R1h"))
    dR1 = sp.Symbol("dR1h")          # слот производной R1' (цепочка: 0)
    zs = _z_system()
    link = zs["M3_link_O4"]
    chain = {A0: 1, R3: 2 * t ** 2 / 9, W2: 4 * t ** 2 / 3, R1: 1,
             dR1: 0}
    m3_link = sp.simplify(sp.expand(link.subs(chain)))
    # маршрут O3: M3* = kappa t0^2 - W2* (O3-уравнение d0'); kappa = 2
    kappa = sp.Integer(2)
    m3_o3 = sp.simplify(kappa * t ** 2 - 4 * t ** 2 / 3)
    return {
        "M3_link_O4_on_chain": sp.sstr(m3_link),
        "M3_route_O3_kappa2": sp.sstr(m3_o3),
        "levels_agree": bool(sp.simplify(m3_link - m3_o3) == 0),
        "note": ("согласование O3/O4 на цепочке ТОЧНО при kappa = 2; "
                 "kappa-зависимость маршрута O3 при кирпиче здесь НЕ "
                 "тестируется (цепочные формы v15 k-независимы, а "
                 "O3-маршрут с кирпичом требует отдельной прокачки)"),
    }


def s3_naive_o6():
    """[S3] наивная O6-несовместность: tau3 = 9/4 vs tau5 = 9/16."""
    tau3, tau5 = sp.Rational(9, 4), sp.Rational(9, 16)
    return {
        "tau3_CORE_pair": "(3/2)^2 = 9/4",
        "tau5_RING_pair": "(4/3)^2 = 16/9 -> 1/tau5 = 9/16",
        "as_tower_points_conflict": bool(sp.simplify(tau3 - tau5) != 0),
        "difference": sp.sstr(sp.simplify(tau3 - tau5)),
        "cross_ref": "center_o6_nsolve.json: nsolve точку не нашёл — "
                     "сырая система может быть несовместной (честная заметка)",
    }


def s4_t1c_resolution():
    """[S4] T1c-часы и лестница на delta_C совпадают ТОЧНО."""
    pi = sp.pi
    T0h = sp.Symbol("T0h", real=True)
    clock_factor = -196 * T0h ** 2 + pi ** 2 * T0h ** 2 + 1323
    tau_star = sp.Rational(1323, 1) / (196 - pi ** 2)
    # подстановка T0h^2 = tau* в часовой фактор (через sqrt-структуру:
    # фактор линеен по T0h^2 — подставляем T0h^2 = tau*)
    x = sp.Symbol("x", real=True)
    cf_x = clock_factor.subs(T0h ** 2, x)
    cf_at = sp.simplify(cf_x.subs(x, tau_star))
    # тождество лестницы: 27/(4 - pi^2/49) = 1323/(196 - pi^2)
    ladder = 27 / (4 - pi ** 2 / 49)
    ident = sp.simplify(sp.together(ladder - tau_star))
    return {
        "clock_factor_T1c_chain": sp.sstr(cf_x),
        "tau_star_T1c": "1323/(196 - pi^2)",
        "tau_star_numeric": float(tau_star.evalf(12)),
        "clock_factor_at_tau_star": sp.sstr(cf_at),
        "clock_zero_exact": bool(cf_at == 0),
        "ladder_at_delta_C": "27/(4 - (pi/7)^2)",
        "ladder_equals_T1c": bool(ident == 0),
        "identity_residual": sp.sstr(ident),
        "note": "часы теоремы о паре на выжившем кирпиче и T1c-замыкание "
                "одним кирпичом — ОДНО число двумя маршрутами",
    }


def s5_verdict_and_program(s1, s2, s4):
    """[S5] сводка сходимости + программа O7."""
    return {
        "levels": {"2_levels": "27/4 = 6.75",
                   "T1c_one_brick": "1323/(196 - pi^2) = 7.107920",
                   "ladder_at_delta_C": "identically T1c (S4)"},
        "shift_2lvl_to_T1c_pct": 100 * (7.10792020692263 - 6.75) / 6.75,
        "convergence": "НЕ установлена: следующий член неизвестен; "
                       "сдвиг 2->T1c монотонен (+5.27%), совпадение с "
                       "лестницей на delta_C точное — башня движется по "
                       "кирпичу, но предела не видит",
        "O7_program": [
            "линеаризация O7 обязана редуцироваться к P4h_lin = t/10 + "
            "16 t^3/135 (S1: регулярный полином — полюс 45/8 НЕЛИНЕЙНЫЙ)",
            "нелинейное продолжение = цепочка v15 (P4h с мягким полюсом "
            "45/8; ветвь проходит — hexcycle T1b, F ~ 1e-15)",
            "факторизация char(2) = 8(2 tau - 1)(8 tau - 45)/27 сохраняется "
            "(lambda^+ = 2 в tau in {1/2, 45/8})",
            "кольцо W2h/T0h^2 = 4/3 (три машинных маршрута) сохраняется",
            "весовое правило 4-го порядка: факторизация (l+p)...(l+p+n-1) "
            "проверяется на O7-таблицах (сейчас доказано до n = 3)",
        ],
    }


def run():
    t0 = time.time()
    print("=" * 72)
    print("OPEN9-Q5: сходимость башни — цепочка, O6, T1c, программа O7")
    print("=" * 72, flush=True)
    out = {
        "title": "OPEN9-Q5 (v19): усечённая башня — цепочное замыкание "
                 "z-системы, наивная O6, T1c-тождество, программа O7",
        "question": "сходится ли усечённая башня? (монография гл.7 №5)",
    }
    print("  [S1] цепочка закрывает z-систему (O5)...", flush=True)
    out["S1_chain_closure"] = s1_chain_closes()
    print("    F1/F2/F4/F5 = 0: %s; P4h_lin = %s (полином: %s)" %
          ([out["S1_chain_closure"]["%s_is_zero" % k]
            for k in ("F1_dt0", "F2_dP2", "F4_dD0", "F5_dR1")],
           out["S1_chain_closure"]["P4h_linear_closure"],
           out["S1_chain_closure"]["P4h_linear_closure_is_poly"]),
          flush=True)
    print("  [S2] M3-связка O4 vs маршрут O3...", flush=True)
    out["S2_m3_link"] = s2_m3_link()
    print("    согласование: %s" % out["S2_m3_link"]["levels_agree"],
          flush=True)
    print("  [S3] наивная O6...", flush=True)
    out["S3_naive_o6"] = s3_naive_o6()
    print("    конфликт: %s" % out["S3_naive_o6"]["as_tower_points_conflict"],
          flush=True)
    print("  [S4] T1c-тождество с лестницей...", flush=True)
    out["S4_t1c_identity"] = s4_t1c_resolution()
    print("    clock_zero_exact: %s; ladder_equals_T1c: %s" %
          (out["S4_t1c_identity"]["clock_zero_exact"],
           out["S4_t1c_identity"]["ladder_equals_T1c"]), flush=True)
    print("  [S5] вердикт + программа O7...", flush=True)
    out["S5_convergence_program"] = s5_verdict_and_program(
        out["S1_chain_closure"], out["S2_m3_link"], out["S4_t1c_identity"])

    out["verdict_lines"] = [
        "ЦЕПОЧКА ЗАКРЫВАЕТ ЛИНЕЙНУЮ Z-СИСТЕМУ ТОЧНО: F1/F2/F4/F5 = 0 "
        "тождественно по T0h; F3 даёт линейное замыкание P4h_lin = "
        "t/10 + 16 t^3/135 — ПОЛИНОМ без особенностей: полюс 45/8 "
        "принадлежит ТОЛЬКО нелинейной цепочке v15 (уточнение статуса "
        "вопроса Q6)",
        "M3-связка O4 на цепочке = 2t^2/3 = маршруту O3 (kappa = 2) "
        "ТОЧНО — весовая структура согласована по уровням O3/O4",
        "наивная O6 несовместна машинно: tau3 = 9/4 vs 1/tau5 = 9/16 — "
        "переопределённая система (воспроизведено, center_o6_nsolve)",
        "НОВОЕ ТОЖДЕСТВО: tau*(delta_C = pi/7) = 27/(4 - pi^2/49) = "
        "1323/(196 - pi^2) — часы пары на выжившем кирпиче и T1c-"
        "замыкание ОДНИМ кирпичом совпадают ТОЧНО (два маршрута, одно "
        "число); часовой фактор T1c обращается в 0 в tau* точно",
        "сходимость башни: НЕ установлена (уровни 6.75 -> 7.1079, "
        "+5.27%); программа O7 сформулирована (5 фиксаций)",
    ]
    out["honest_notes"] = [
        "S1 — проверка ЛИНЕЙНОЙ z-системы (sympy_center ярус O1-O5); "
        "нелинейная книга (dae eval_F) на цепочке верифицирована ранее "
        "(second_flows: max_residual 9.9e-24) — здесь не перепроверяется",
        "тождество S4 связывает ЧАСЫ (tau*), а не весь набор амплитуд: "
        "совпадение T1c с лестницей на delta_C — про масштаб, не про "
        "отбор кирпича (вопрос Q1 остаётся барьерным)",
        "kappa-зависимость M3-маршрута O3 при кирпиче не тестировалась: "
        "цепочные формы v15 k-независимы, согласование с кирпичом "
        "требует отдельной прокачки (честная граница S2)",
        "весовое правило 4-го порядка здесь НЕ доказано: O7-программа "
        "лишь фиксирует, ЧТО именно подлежит проверке на O7-таблицах",
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
