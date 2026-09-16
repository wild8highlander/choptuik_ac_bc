#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 ЭКСПЕРИМЕНТ 3. БАШНЯ ПОВЕРХНОСТЕЙ ГУРВИЦА: АУДИТ + РАСШИРЕНИЕ
================================================================================
Постановка. Монография (Часть 7 verify_enhanced) фиксирует «башню Гурвица»:
  Klein g=3 (n=7, b2=22), Macbeath g=7 (n=9, b2=46), Hurwitz_3 g=14 (n=11, b2=94)
и вычисляет delta_eff = (pi/n)^5 / b2, gamma = (pi/n)^4 / b2.

Здесь мы:
  A. Аудит группы Гурвица: 84(g-1) = |Aut| и n | |Aut| (элемент порядка n).
     НАХОДКА D1: для Hurwitz_3 (g=14) в репо n=11, но |Aut| = 84*13 = 1092
     НЕ делится на 11 — элемента порядка 11 быть не может. Реальный род-14
     гурвицев поверхность — PSL(2,13) с (2,3,13). Исправляем башню.
  B. Корректная башня (известные младшие поверхности Гурвица):
       g=3  PSL(2,7)   (2,3,7)  |G|=168
       g=7  PSL(2,8)   (2,3,9)  |G|=504   (Macbeath/Fricke-Macbeath)
       g=14 PSL(2,13)  (2,3,13) |G|=1092
       g=17 триплет Гурвица (2,3,8) |G|=1344 (первый триплет, 3 поверхности)
     Проверки: 84(g-1)=|G|, n | |G|, гиперболичность 1/2+1/3+1/n < 1.
  C. Расчёты фреймворка по башне: delta = pi/n; delta_eff, gamma — при
     ГИПОТЕТИЧЕСКОМ b2(k) из паттерна репо (22, 46, 94 -> 2*b+2);
     честно помечено: b2 для не-Клейновых поверхностей НЕ выведен,
     это структурная гипотеза фреймворка.
  D. Универсальная кривая Delta_Ch(delta) = lambda_D2 + delta^2/2 - delta^5/22
     при lambda_D2 = 3.338: значение в точках delta = pi/n башни + минимум
     кривой (сравнение с delta = pi/7).
  E. Экстраполяция: асимптотика delta_eff(g) по корректной башне.

Запуск: python3 exp3_hurwitz.py
Вывод:  results/exp3_hurwitz.json + figures (RU/EN).
================================================================================
"""
import json
import math
import os
import sys

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from figlabels import L

PI = math.pi


def b_Ch(n):
    return 1.0 - math.cos(2 * PI / n)


# =============================================================================
def part_A():
    """Аудит башни репо."""
    print("=" * 78)
    print("A. АУДИТ БАШНИ РЕПО (Klein/Macbeath/Hurwitz_3)")
    print("=" * 78)
    repo_tower = [
        {"name": "Klein", "g": 3, "n": 7, "b2": 22},
        {"name": "Macbeath", "g": 7, "n": 9, "b2": 46},
        {"name": "Hurwitz_3", "g": 14, "n": 11, "b2": 94},
    ]
    out = []
    for s in repo_tower:
        aut = 84 * (s["g"] - 1)
        n_divides = aut % s["n"] == 0
        ok = n_divides
        out.append({**s, "aut": aut, "n_divides_aut": n_divides, "consistent": ok})
        print(f"  {s['name']:<10s} g={s['g']:3d} n={s['n']:3d} |Aut|=84(g-1)={aut:5d}  "
              f"n|Aut: {'OK' if n_divides else 'FAIL'}  "
              f"{'согласовано' if ok else '<<< НАХОДКА D1: НЕСОГЛАСОВАНО'}")
    print("\n  D1: группы порядка 1092 = 2^2*3*7*13 не содержат элементов")
    print("  порядка 11 (11 не делит 1092). Реальный род-14 гурвицев")
    print("  поверхность: PSL(2,13) с сигнатурой (2,3,13).")
    return out


def part_B():
    """Корректная башня."""
    print("\n" + "=" * 78)
    print("B. КОРРЕКТНАЯ БАШНЯ (младшие поверхности Гурвица)")
    print("=" * 78)
    tower = [
        {"name": "Klein (g=3)", "g": 3, "n": 7, "aut": 168,
         "group": "PSL(2,7)", "n_tower": 0},
        {"name": "Macbeath (g=7)", "g": 7, "n": 9, "aut": 504,
         "group": "PSL(2,8)", "n_tower": 1},
        {"name": "PSL(2,13) (g=14)", "g": 14, "n": 13, "aut": 1092,
         "group": "PSL(2,13)", "n_tower": 2},
        {"name": "Триплет (g=17)", "g": 17, "n": 8, "aut": 1344,
         "group": "первый триплет Гурвица", "n_tower": 3},
    ]
    out = []
    for s in tower:
        hyperbolic = 0.5 + 1 / 3 + 1 / s["n"] < 1
        checks = {
            "84(g-1)=|Aut|": 84 * (s["g"] - 1) == s["aut"],
            "n | |Aut|": s["aut"] % s["n"] == 0,
            "(2,3,n) гиперболична": hyperbolic,
        }
        s2 = {**s, "checks": checks,
              "all_ok": all(checks.values())}
        out.append(s2)
        print(f"  {s['name']:<20s} {s['group']:<24s} (2,3,{s['n']}) "
              f"|G|={s['aut']:5d}: " +
              ", ".join(f"{k}={'OK' if v else 'FAIL'}" for k, v in checks.items()))
    return out


def part_C(tower):
    """Расчёты фреймворка: delta_eff, gamma; паттерн b2 — гипотеза."""
    print("\n" + "=" * 78)
    print("C. РАСЧЁТЫ ФРЕЙМВОРКА (b2(k) = 2*b2(k-1)+2 — ГИПОТЕЗА паттерна репо)")
    print("=" * 78)
    b2_hyp = [22]
    for _ in range(3):
        b2_hyp.append(2 * b2_hyp[-1] + 2)
    out = []
    print(f"  {'поверхность':<22s} {'n':>3s} {'b2(гип.)':>9s} "
          f"{'delta=pi/n':>12s} {'gamma=d^4/b2':>14s} {'d_eff=d^5/b2':>14s}")
    for s, b2 in zip(tower, b2_hyp):
        delta = PI / s["n"]
        gamma = delta ** 4 / b2
        d_eff = delta ** 5 / b2
        out.append({**s, "b2_hyp": b2, "delta": delta, "gamma": gamma,
                    "delta_eff": d_eff})
        print(f"  {s['name']:<22s} {s['n']:3d} {b2:9d} {delta:12.6f} "
              f"{gamma:14.4e} {d_eff:14.4e}")
    # паттерн b2: 22, 46, 94 = 3*2^(k+3) - 2 (проверка)
    alt = [3 * 2 ** (k + 3) - 2 for k in range(4)]
    print(f"  паттерн 2b+2: {b2_hyp}; эквивалентно 3*2^(k+3)-2: {alt} — "
          f"{'совпадают' if alt == b2_hyp else 'РАСХОЖДЕНИЕ'}")
    print("  ЧЕСТНОСТЬ: b2 для g>3 не выведен из топологии — это гипотеза")
    print("  фреймворка; для Клейна b2=22 = b2(K3) топологичен.")
    return {"rows": out, "b2_hyp": b2_hyp}


def part_D():
    """Универсальная кривая Delta_Ch(delta).

    Кривая монотонно растёт на [0, 1.64] (d/dd: delta*(1 - 5delta^3/22) > 0),
    поэтому «минимум вблизи pi/7» в монографии — это минимум ОТКЛОНЕНИЯ
    |Delta_Ch(delta) - 3.443| (точка пересечения кривой с наблюдаемым
    значением). Считаем именно его.
    """
    print("\n" + "=" * 78)
    print("D. УНИВЕРСАЛЬНАЯ КРИВАЯ Delta_Ch(delta) = 3.338 + delta^2/2 - delta^5/22")
    print("=" * 78)
    lam = 3.338
    DELTA_OBS = 3.443

    def Delta_Ch(delta):
        return lam + delta ** 2 / 2 - delta ** 5 / 22

    # минимум |Delta_Ch(delta) - 3.443| (монотонность проверяем явно)
    grid = np.linspace(0.0, 1.4, 140001)
    vals = Delta_Ch(grid)
    deriv = grid * (1 - 5 * grid ** 3 / 22)
    monotone = bool(np.all(deriv[grid < 1.6] > 0))
    dev_abs = np.abs(vals - DELTA_OBS)
    i_min = int(np.argmin(dev_abs))
    delta_star = float(grid[i_min])
    out = {
        "lambda_D2": lam,
        "delta_obs": DELTA_OBS,
        "monotone_on_0_16": monotone,
        "delta_star_deviation_min": delta_star,
        "Delta_at_star": float(vals[i_min]),
        "Delta_at_pi_over_7": float(Delta_Ch(PI / 7)),
        "dev_at_pi_over_7_pct": float(abs(Delta_Ch(PI / 7) - DELTA_OBS) / DELTA_OBS * 100),
        "points": [],
    }
    print(f"  кривая монотонна на [0, 1.6]: {monotone} -> минимум отклонения =")
    print(f"  точка пересечения с 3.443: delta* = {delta_star:.5f} "
          f"(pi/7 = {PI/7:.5f}, расхождение {abs(delta_star - PI/7):.4f})")
    print(f"  Delta_Ch(pi/7) = {Delta_Ch(PI/7):.6f} "
          f"(отклонение от 3.443: {out['dev_at_pi_over_7_pct']:.3f}%)")
    for n in (7, 8, 9, 13, 11):
        d = Delta_Ch(PI / n)
        out["points"].append({"n": n, "delta": PI / n, "Delta_Ch": d,
                              "dev_pct": float(abs(d - DELTA_OBS) / DELTA_OBS * 100)})
        print(f"  n={n:3d}: delta = pi/{n:<2d} = {PI/n:.5f} -> Delta_Ch = {d:.6f} "
              f"(откл. {out['points'][-1]['dev_pct']:.2f}%)")
    return out


def part_E(rows):
    """Точные пошаговые факторы давления + формальная экстраполяция паттерна."""
    print("\n" + "=" * 78)
    print("E. ФАКТОРЫ ДАВЛЕНИЯ + ФОРМАЛЬНАЯ ЭКСТРАПОЛЯЦИЯ ПАТТЕРНА")
    print("=" * 78)
    out = {"step_factors": [], "formal_continuation": []}
    for i in range(len(rows) - 1):
        a, b = rows[i], rows[i + 1]
        f = a["delta_eff"] / b["delta_eff"]
        out["step_factors"].append({"from": a["name"], "to": b["name"],
                                    "factor": float(f)})
        print(f"  {a['name']:<20s} -> {b['name']:<20s}: "
              f"давление delta_eff x{f:.2f}")
    # формальная экстраполяция: продолжаем паттерн b2(k) = 3*2^(k+3)-2,
    # n растёт на 2 (формально, без привязки к реальным группам)
    b2 = 190
    for k in (4, 5, 6):
        n = 8 + 2 * (k - 3)
        b2 = 3 * 2 ** (k + 3) - 2
        d_eff = (PI / n) ** 5 / b2
        out["formal_continuation"].append({"k": k, "n": n, "b2": b2,
                                           "delta_eff": d_eff})
        print(f"  [формально] k={k}: n={n}, b2={b2} -> "
              f"delta_eff = {d_eff:.3e}")
    print("  ЧЕСТНОСТЬ: формальная экстраполяция НЕ привязана к реальным")
    print("  поверхностям Гурвица — это продолжение паттерна фреймворка.")
    return out


def make_figures(out, lang_dir, lang):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = L[lang]
    rows = out["framework"]["rows"]
    g = [r["g"] for r in rows]
    de = [r["delta_eff"] for r in rows]
    gam = [r["gamma"] for r in rows]
    names = [f"{r['name']}\n(2,3,{r['n']})" for r in rows]

    fig, ax = plt.subplots(figsize=(8.6, 5.4), constrained_layout=True)
    ax.semilogy(g, de, "o-", color="#1e3a5f", lw=1.8, ms=9,
                label=r"$\delta_{\mathrm{eff}}=\delta^5/b_2$")
    ax.semilogy(g, gam, "s--", color="#b45309", lw=1.6, ms=8,
                label=r"$\gamma=\delta^4/b_2$")
    for x, y, nm in zip(g, de, names):
        ax.annotate(nm, (x, y), textcoords="offset points", xytext=(8, 8),
                    fontsize=9)
    ax.set_xlabel(t["tower_xlabel"])
    ax.set_ylabel(t["tower_ylabel"])
    ax.set_title(t["tower_title"])
    ax.grid(alpha=0.3, which="both")
    ax.legend(loc="upper right")
    fig.savefig(os.path.join(lang_dir, "fig_hurwitz_tower.png"), dpi=300)
    plt.close(fig)

    # универсальная кривая
    d = out["curve"]
    lam = d["lambda_D2"]
    grid = np.linspace(0.0, 1.2, 1200)
    vals = lam + grid ** 2 / 2 - grid ** 5 / 22
    fig, ax = plt.subplots(figsize=(8.6, 5.4), constrained_layout=True)
    ax.plot(grid, vals, color="#1e3a5f", lw=2)
    ax.axhline(3.443, color="#0e7c66", ls="--", lw=1.4,
               label=r"наблюдаемое $\Delta=3.443$")
    ax.axvline(PI / 7, color="#b45309", ls=":", lw=1.4,
               label=r"$\delta_C=\pi/7$")
    for p in d["points"]:
        ax.plot([p["delta"]], [p["Delta_Ch"]], "o", ms=7, color="#8338ec")
        ax.annotate(f"n={p['n']}", (p["delta"], p["Delta_Ch"]),
                    textcoords="offset points", xytext=(6, -14), fontsize=9)
    ax.set_xlabel(r"$\delta$")
    ax.set_ylabel(r"$\Delta_{\mathrm{Ch}}(\delta)$")
    ax.set_ylim(3.3, 3.9)
    ax.legend(loc="upper left")
    ax.set_title(t["tower_title"] + " — " + r"$\Delta_{\mathrm{Ch}}(\delta)$")
    fig.savefig(os.path.join(lang_dir, "fig_hurwitz_curve.png"), dpi=300)
    plt.close(fig)
    print(f"  [фигуры] {lang_dir}/fig_hurwitz_tower.png, "
          f"fig_hurwitz_curve.png")


def main():
    print("=" * 78)
    print("ЭКСПЕРИМЕНТ 3. БАШНЯ ГУРВИЦА: АУДИТ + РАСШИРЕНИЕ")
    print("=" * 78)
    out = {}
    out["repo_audit"] = part_A()
    out["tower"] = part_B()
    out["framework"] = part_C(out["tower"])
    out["curve"] = part_D()
    out["extrapolation"] = part_E(out["framework"]["rows"])

    print("\n" + "=" * 78)
    print("СВОДКА")
    print("=" * 78)
    d1 = [r for r in out["repo_audit"] if not r["consistent"]]
    print(f"  Находка D1: башня репо несогласована в 1 точке "
          f"({d1[0]['name']}, n={d1[0]['n']} при |Aut|={d1[0]['aut']})")
    print(f"  Корректная башня: 4 поверхности, все проверки OK")
    de0 = out["framework"]["rows"][0]["delta_eff"]
    de3 = out["framework"]["rows"][3]["delta_eff"]
    print(f"  delta_eff: Клейн {de0:.3e} -> триплет {de3:.3e} "
          f"(давление x{de0/de3:.1f})")
    print(f"  точка пересечения кривой с 3.443: delta* = "
          f"{out['curve']['delta_star_deviation_min']:.5f} "
          f"(pi/7 = {PI/7:.5f})")
    sf = out["extrapolation"]["step_factors"]
    print(f"  давление delta_eff по башне: "
          f"x{sf[0]['factor']:.1f}, x{sf[1]['factor']:.1f}, x{sf[2]['factor']:.1f}")

    for lang, lang_dir in (("ru", os.path.join(BASE, "fig_ru")),
                           ("en", os.path.join(BASE, "fig_en"))):
        make_figures(out, lang_dir, lang)

    res_path = os.path.join(BASE, "results", "exp3_hurwitz.json")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] {res_path}")


if __name__ == "__main__":
    main()
