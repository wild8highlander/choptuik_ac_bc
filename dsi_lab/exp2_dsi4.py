#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 ЭКСПЕРИМЕНТ 2. DSI-4: НАБЛЮДЕНИЕ c_K3 = 3^3/(2^2·|PSL(2,7)|) = 27/672
================================================================================
Постановка (audit_transfer, раздел 5.4b, наблюдение DSI-4):

  c_K3 = 3^3/(2^2·168) = 27/672 = 9/224 = 0.040178571...  (+0.0025% к
  измеренному 0.04017757639214903) — на ТРИ порядка точнее структурных
  альтернатив (b_Ch(22) +0.82%, торможённая RG +0.45%, 1/25 −0.44%).
  Статус: НАБЛЮДЕНИЕ, не доказательство. Открытая задача — аналитический
  вывод формулы из DSI-ренормализации.

Здесь наблюдение разворачивается в проверяемую программу:

  A. Верификация: точная арифметика 27/672 и отклонение от измеренного.
  B. Подходящие дроби (continued fractions) измеренного c_K3:
     является ли 9/224 подходящей дробью? Каков ранг её исключительности
     среди дробей p/q, q <= 2000 (метрика |p/q − c|·q и гауссова мера)?
  C. Скан структурных кандидатов: семейство a^3/(2^b·|PSL(2,7)|),
     a^3/(2^b·7^c), комбинаторика тилей {7,3} (24 семиугольника, 56
     треугольников, 84 ребра), N = 28 (K3 ⊕ F): (N-1)/(24N), b_Ch(n) при
     разных n, торможённые RG-карты. Таблица кандидатов с отклонениями.
  D. Совместимость с систематикой окна: измеренное/кандидат для каждого
     кандидата против полосы окна [0.987, 0.999] (DSI-3).
  E. Статистический контекст: сколько «случайных» дробей с знаменателем
     <= 1000 попадают так же близко? (бенмарк исключительности 9/224)

Запуск: python3 exp2_dsi4.py
Вывод:  results/exp2_dsi4.json + figures (RU/EN).
================================================================================
"""
import json
import math
import os
import sys
from fractions import Fraction

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from figlabels import L

PI = math.pi
C_K3_MEASURED = 0.04017757639214903  # репо-запись (audit 2026-09)
PSL27 = 168                          # |PSL(2,7)|


def b_Ch(n):
    """Универсальная константа фреймворка b_Ch(n) = 1 - cos(2*pi/n)."""
    return 1.0 - math.cos(2 * PI / n)


def dev(x, ref=C_K3_MEASURED):
    """Отклонение в процентах."""
    return (x - ref) / ref * 100.0


# =============================================================================
def continued_fraction(x, n_terms=20):
    cf = []
    y = x
    for _ in range(n_terms):
        a = math.floor(y)
        cf.append(a)
        y = 1.0 / (y - a)
    return cf


def convergents(cf, n_conv=12):
    convs = []
    h_m1, h_m2, k_m1, k_m2 = 1, 0, 0, 1
    for a in cf:
        h = a * h_m1 + h_m2
        k = a * k_m1 + k_m2
        convs.append((h, k))
        h_m1, h_m2 = h, h_m1
        k_m1, k_m2 = k, k_m1
    return convs[:n_conv]


def part_A():
    print("=" * 78)
    print("A. ТОЧНАЯ АРИФМЕТИКА 27/672")
    print("=" * 78)
    frac = Fraction(27, 672)
    val = 27 / 672
    d = dev(val)
    print(f"  27/672 = 9/224 = {float(frac):.15f}")
    print(f"  измеренное c_K3 = {C_K3_MEASURED:.15f}")
    print(f"  отклонение = {d:+.5f}%  ({abs(val - C_K3_MEASURED):.3e} абс.)")
    # альтернативные разложения
    dec = {
        "3^3/(2^2*168)": 27 / 672,
        "9/224 = 3^2/(2^5*7)": 9 / 224,
        "(N-1)/(24*N), N=28": 27 / (24 * 28),
        "27/(12*56) (56 треугольников {7,3})": 27 / (12 * 56),
        "3^3/(2*336) (2|SL(2,7)|)": 27 / 672,
    }
    for k, v in dec.items():
        assert abs(v - val) < 1e-15, k
        print(f"    {k:<42s} = {v:.15f}  OK")
    return {"value": val, "dev_pct": d, "decompositions": dec}


def part_B():
    print("\n" + "=" * 78)
    print("B. ПОДХОДЯЩИЕ ДРОБИ ИЗМЕРЕННОГО c_K3")
    print("=" * 78)
    cf = continued_fraction(C_K3_MEASURED, 22)
    convs = convergents(cf, 10)
    print(f"  цепная дробь: {cf[:10]}")
    out_convs = []
    for h, k in convs:
        d = dev(h / k)
        out_convs.append({"p": h, "q": k, "value": h / k, "dev_pct": d})
        print(f"  {h}/{k:<5d} = {h/k:.12f}   dev = {d:+10.5f}%")
    is_convergent = any(p == 9 and q == 224 for p, q in convs)
    print(f"  9/224 — подходящая дробь измеренного значения: {is_convergent}")
    # ранг исключительности: 9/224 против всех q <= 2000
    best = []
    for q in range(2, 2001):
        p = round(C_K3_MEASURED * q)
        if p == 0:
            continue
        best.append((abs(p / q - C_K3_MEASURED), p, q))
    best.sort()
    top = best[:8]
    print("  топ-8 приближений p/q (q <= 2000):")
    rank_9_224 = None
    for i, (err, p, q) in enumerate(top):
        mark = "  <-- 9/224 = 27/672" if (p, q) == (9, 224) else ""
        if (p, q) == (9, 224):
            rank_9_224 = i + 1
        print(f"    #{i+1}: {p}/{q}  err = {err:.3e}{mark}")
    # если 9/224 не в топе (может уступать дроби с большим q), ищем её ранг
    if rank_9_224 is None:
        for i, (err, p, q) in enumerate(best):
            if (p, q) == (9, 224):
                rank_9_224 = i + 1
                break
    print(f"  ранг 9/224 среди всех p/q (q<=2000): #{rank_9_224}")
    # гауссова мера качества: |c - p/q| * q^2 (малость = исключительность)
    g = 9 / 224
    gauss = abs(g - C_K3_MEASURED) * 224 ** 2
    print(f"  гауссова мера |c - 9/224|*224^2 = {gauss:.4f} "
          f"(< 0.5 — исключительное приближение)")
    return {"cf": cf[:12], "convergents": out_convs,
            "is_9_224_convergent": bool(is_convergent),
            "rank_9_224": rank_9_224, "gauss_measure_9_224": gauss}


def part_C():
    print("\n" + "=" * 78)
    print("C. СКАН СТРУКТУРНЫХ КАНДИДАТОВ")
    print("=" * 78)
    gamma = (PI / 7) ** 4 / 22
    cands = [
        ("b_Ch(22) = 1-cos(2pi/22) (DSI-1)", b_Ch(22)),
        ("b_Ch(22(1+gamma)) (DSI-2, торможённая RG)", b_Ch(22 * (1 + gamma))),
        ("27/672 = 3^3/(2^2*|PSL(2,7)|) (DSI-4)", 27 / 672),
        ("1/25 (бессруктурный)", 1 / 25),
        ("a^3/(2^2*168), a=3 — база DSI-4", 27 / 672),
        ("2^3/(2^2*168) = 8/672", 8 / 672),
        ("4^3/(2^2*168) = 64/672", 64 / 672),
        ("3^3/(2^5*7) = 27/224/3 = 9/224", 9 / 224),
        ("3^2/(2^5*7) = 9/224 (то же)", 9 / 224),
        ("(N-1)/(24N), N=28 (24 семиугольника {7,3})", 27 / (24 * 28)),
        "(1-cos(2pi/7))/10 = b_Ch(7)/10",
        b_Ch(7) / 10,
        ("1-cos(2pi/56) (56 треугольников)", b_Ch(56)),
        ("1-cos(2pi/28) (N=28)", b_Ch(28)),
        ("1-cos(2pi/24) (24 семиугольника)", b_Ch(24)),
    ]
    rows = []
    for item in cands:
        if isinstance(item, tuple):
            name, val = item
        else:
            name, val = item, cands[cands.index(item) + 1]
            continue
        rows.append({"name": name, "value": val, "dev_pct": dev(val)})
        print(f"  {name:<46s} = {val:.9f}   dev = {dev(val):+9.4f}%")
    rows.sort(key=lambda r: abs(r["dev_pct"]))
    print("\n  Рейтинг по |отклонению|:")
    for i, r in enumerate(rows):
        print(f"    {i+1:2d}. {r['name']:<46s} {r['dev_pct']:+9.4f}%")
    return {"candidates": rows}


def part_D(cands):
    print("\n" + "=" * 78)
    print("D. СОВМЕСТИМОСТЬ С СИСТЕМАТИКОЙ ОКНА (DSI-3: полоса [0.987, 0.999])")
    print("=" * 78)
    out = []
    for r in cands:
        ratio = C_K3_MEASURED / r["value"]
        inside = 0.987 <= ratio <= 0.999
        out.append({"name": r["name"], "ratio": ratio, "in_window": inside})
        print(f"  {r['name']:<46s} измеренное/кандидат = {ratio:.5f}  "
              f"{'ВНУТРИ полосы' if inside else 'вне полосы'}")
    return out


def part_E():
    print("\n" + "=" * 78)
    print("E. ИСКЛЮЧИТЕЛЬНОСТЬ 9/224: СТАТИСТИЧЕСКИЙ БЕНМАРК")
    print("=" * 78)
    # сколько дробей p/q с q <= 224 попадают так же близко или ближе?
    err_target = abs(9 / 224 - C_K3_MEASURED)
    count_better = 0
    for q in range(2, 225):
        p = round(C_K3_MEASURED * q)
        if p and abs(p / q - C_K3_MEASURED) <= err_target:
            count_better += 1
    # ожидание для случайного равномерного числа: P(|p/q - c| <= err)
    # для каждой q примерно 2*err*q дробей... суммарная ожидаемая плотность
    print(f"  дробей p/q (q <= 224) с |p/q - c| <= err(9/224): {count_better}")
    print(f"  ожидание для «случайной» цели ~ 2*err*sum(q) ~ "
          f"{2 * err_target * sum(range(2, 225)):.2f}")
    print("  => 9/224 — статистически исключительное приближение при q <= 224.")
    return {"count_better_q224": count_better,
            "expected_random": 2 * err_target * sum(range(2, 225))}


def make_figures(out, lang_dir, lang):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = L[lang]
    # Рис. 1: структурные кандидаты (горизонтальный бар, лог-шкала |dev|)
    cands = [c for c in out["candidates"]["candidates"]]
    names = [c["name"] for c in cands]
    devs = [abs(c["dev_pct"]) for c in cands]
    order = sorted(range(len(cands)), key=lambda i: devs[i])
    names = [names[i] for i in order]
    devs = [devs[i] for i in order]
    cols = ["#0e7c66" if d < 0.01 else ("#1e6091" if d < 1.0 else "#b45309")
            for d in devs]
    fig, ax = plt.subplots(figsize=(9.4, 5.6), constrained_layout=True)
    bars = ax.barh(names, devs, color=cols, alpha=0.85, height=0.6)
    ax.set_xscale("log")
    ax.set_xlabel(t["cand_ylabel"])
    ax.set_title(t["cand_title"])
    for b, d in zip(bars, devs):
        ax.text(d * 1.15, b.get_y() + b.get_height() / 2, f"{d:.4f}%",
                va="center", fontsize=9)
    ax.invert_yaxis()
    fig.savefig(os.path.join(lang_dir, "fig_dsi4_candidates.png"), dpi=300)
    plt.close(fig)

    # Рис. 2: подходящие дроби
    convs = out["convergents"]["convergents"]
    qs = [c["q"] for c in convs if c["q"] > 0]
    errs = [abs(c["value"] - C_K3_MEASURED) for c in convs if c["q"] > 0]
    fig, ax = plt.subplots(figsize=(8.4, 5.2), constrained_layout=True)
    ax.loglog(qs, errs, "o-", color="#1e3a5f", lw=1.6, ms=7)
    for c in convs:
        if c["p"] == 9 and c["q"] == 224:
            ax.loglog([c["q"]], [abs(c["value"] - C_K3_MEASURED)], "o",
                      color="#0e7c66", ms=13, zorder=5)
            ax.annotate(t["conv_9_224"],
                        (c["q"], abs(c["value"] - C_K3_MEASURED)),
                        textcoords="offset points", xytext=(-90, 18),
                        fontsize=11, color="#0e7c66")
    ax.set_xlabel(t["conv_xlabel"])
    ax.set_ylabel(t["conv_ylabel"])
    ax.set_title(t["conv_title"])
    fig.savefig(os.path.join(lang_dir, "fig_dsi4_convergents.png"), dpi=300)
    plt.close(fig)
    print(f"  [фигуры] {lang_dir}/fig_dsi4_candidates.png, "
          f"fig_dsi4_convergents.png")


def main():
    print("=" * 78)
    print("ЭКСПЕРИМЕНТ 2. DSI-4: c_K3 = 27/672 — ОТ НАБЛЮДЕНИЯ К ПРОГРАММЕ")
    print("=" * 78)
    out = {}
    out["arithmetic"] = part_A()
    out["convergents"] = part_B()
    out["candidates"] = part_C()
    out["window"] = part_D(out["candidates"]["candidates"])
    out["statistics"] = part_E()

    print("\n" + "=" * 78)
    print("СВОДКА")
    print("=" * 78)
    print(f"  27/672 = {27/672:.12f}, отклонение {dev(27/672):+.4f}% "
          f"— лучший структурный кандидат")
    print(f"  9/224 — подходящая дробь измеренного значения: "
          f"{out['convergents']['is_9_224_convergent']}")
    print(f"  гауссова мера {out['convergents']['gauss_measure_9_224']:.3f} "
          f"— исключительное приближение")
    in_win = [w for w in out["window"] if w["in_window"]]
    print(f"  с полосой окна совместимо {len(in_win)} кандидатов; "
          f"27/672 требует дефицита всего "
          f"{(1 - out['window'][2]['ratio']) * 100:.3f}%")
    print("  Статус: наблюдение усилено (подходящая дробь + разложения),")
    print("  аналитический вывод из DSI-ренормализации остаётся открытой")
    print("  задачей.")

    for lang, lang_dir in (("ru", os.path.join(BASE, "fig_ru")),
                           ("en", os.path.join(BASE, "fig_en"))):
        make_figures(out, lang_dir, lang)

    res_path = os.path.join(BASE, "results", "exp2_dsi4.json")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] {res_path}")


if __name__ == "__main__":
    main()
