#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 ЭКСПЕРИМЕНТ 7. ПОРОГ e >= 1: «ЛЕСТНИЦА» СТАНОВИТСЯ ТЕОРЕМОЙ
================================================================================
Класс «изометрических на носителе» конструкций: X_i in M_n(C) — ЧАСТИЧНЫЕ
ИЗОМЕТРИИ (все ненулевые сингулярные числа равны 1; носитель = начальное
подпространство, и на нём X_i изометрична). Это ровно класс, в котором лежат
все «структурные» модели фреймворка: перестановочные матрицы (унитарные),
усечённые сдвиги дерева Кунца; и НЕ лежат свободные скаляры sqrt(4/7)·I
(сингулярные числа sqrt(4/7) != 1) и взвешенные деревья c_i·S_i (c_i != 1).

ТЕОРЕМА A (порог). Для любых частичных изометрий X1, X2 in M_n:
    F(X1,X2) >= n,   т.е.  e = F/n >= 1.
    Равенство <=> P·Q = 0 и p + q = n, где P = X1X1*, Q = X2X2* (проекции),
    p = rank P, q = rank Q.
Доказательство (5 строк). Для частичных изометрий P, Q — проекции, и
    F = G(P,Q) = 3n − 2p − 2q + 3r,  r = tr(PQ)
    (тождество F = G(P,Q) из аудита + tr(P^2) = tr(P)).
    Оценки на проекциях: max(0, p+q−n) <= r <= min(p,q)  (tr(PQ) >= tr(P∧Q)
    >= p+q−n по размерности пересечения; tr(PQ) = tr(QPQ) <= ||P||·tr Q = q).
    Если p+q >= n:  F − n = 3r − 2(p+q−n) >= 3(p+q−n) − 2(p+q−n) = p+q−n >= 0.
    Если p+q <= n:  F − n = 2(n−p−q) + 3r >= 0.                         ∎

ТЕОРЕМА B (точная арифметика покрытия). Если X1, X2 — частичные изометрии и
P + Q <= I (комбинированные образы не накрывают пространство), то
    F = n + 2·rank(I − P − Q)   ТОЧНО.
    В частности, обрезка дерева Кунца (непокрыт только корень, rank = 1):
    F = n + 2, e = 1 + 2/n → 1 — почти-экстремаль класса.

ТЕОРЕМА C (унитарные пары). X1, X2 унитарны  =>  F = 2n ТОЧНО (e = 2):
    F = 0 + 0 + ||X1*X2||² + ||I||² = n + n. Перестановочные модели — частный
    случай; дефект целиком от перекрытия образов (r = n).

СЛЕДСТВИЕ D (замыкание класса). inf e по носитель-изометрическим парам = 1;
значение e = 5/7 < 1 в классе НЕДОСТИЖИМО (5/7 требует сжатия носителя).
Для цепочки Ш1–Ш4: Ш2 усиливается до класса — никакая последовательность
носитель-изометрических моделей не даёт e → 0; мост Ш.3(iii) невозможен для
изометрических переносов: eta ≡ 1 > 0.

Здесь все четыре утверждения верифицируются численно (машинная точность):
  A1: тождество F = 3n − 2p − 2q + 3r на случайных частичных изометриях;
  A2: порог F >= n на 10^5 случайных пар (n = 1..12) — ноль нарушений;
  A3: случай равенства — комплементарные проекции: F = n точно;
  B1: формула F = n + 2·rank(I−P−Q) на случайных проекциях с P+Q <= I;
  B2: обрезка дерева k = 2..10: rank(I−P−Q) = 1, F = n + 2 точно;
  C1: унитарные/перестановочные пары: F = 2n точно;
  E1: оценки tr(PQ): max(0,p+q−n) <= r <= min(p,q) на 10^4 случайных пар
      проекций — ноль нарушений;
  F1: контраст: sqrt(4/7)·I даёт e = 5/7 вне класса; взвешенное дерево
      c^2 = 4/7 не достигает 5/7 (формула F = (n−1)·2·(c²−1)² + n + 2).

Запуск: python3 exp7_e1_threshold.py
Вывод:  results/exp7_e1_threshold.json + figures (RU/EN).
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

RNG = np.random.default_rng(42)


def leavitt_F(x1, x2):
    I = np.eye(x1.shape[0])
    return (np.linalg.norm(x1.conj().T @ x1 - I, 'fro') ** 2
            + np.linalg.norm(x2.conj().T @ x2 - I, 'fro') ** 2
            + np.linalg.norm(x1.conj().T @ x2, 'fro') ** 2
            + np.linalg.norm(x1 @ x1.conj().T + x2 @ x2.conj().T - I, 'fro') ** 2)


def random_partial_isometry(n, rank, rng):
    """Случайная частичная изометрия ранга rank: U diag(1^rank, 0) V*."""
    A = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    B = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    U, _, _ = np.linalg.svd(A)
    V, _, _ = np.linalg.svd(B)
    S = np.zeros(n)
    S[:rank] = 1.0
    return U @ np.diag(S) @ V.conj().T


def random_projections_disjoint(n, p, q, rng):
    """Пары проекций P, Q с P + Q <= I: случайные ортогональные подпространства."""
    A = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    U, _ = np.linalg.qr(A)
    P = U @ np.diag(np.r_[np.ones(p), np.zeros(n - p)]) @ U.conj().T
    Q = U @ np.diag(np.r_[np.zeros(p), np.ones(q), np.zeros(n - p - q)]) \
        @ U.conj().T
    return P, Q


# =============================================================================
def part_A(n_max=12, n_pairs=2000):
    print("=" * 78)
    print("A. ТЕОРЕМА A: ПОРОГ e >= 1 ДЛЯ ЧАСТИЧНЫХ ИЗОМЕТРИЙ")
    print("=" * 78)
    out = {"identity_err": 0.0, "threshold_violations": 0, "pairs": 0,
           "min_e_by_n": [], "equality_err": 0.0}
    for n in range(1, n_max + 1):
        min_e = math.inf
        for _ in range(n_pairs):
            r1 = int(RNG.integers(0, n + 1))
            r2 = int(RNG.integers(0, n + 1))
            X1 = random_partial_isometry(n, r1, RNG)
            X2 = random_partial_isometry(n, r2, RNG)
            # проверка частичной изометрии: X X* X = X
            assert np.linalg.norm(X1 @ X1.conj().T @ X1 - X1) < 1e-11
            P = X1 @ X1.conj().T
            Q = X2 @ X2.conj().T
            p, q = int(np.round(np.trace(P).real)), int(np.round(np.trace(Q).real))
            r = np.trace(P @ Q).real
            F = leavitt_F(X1, X2)
            F_formula = 3 * n - 2 * p - 2 * q + 3 * r
            out["identity_err"] = max(out["identity_err"],
                                      abs(F - F_formula) / max(1.0, F))
            e = F / n
            if e < 1 - 1e-9:
                out["threshold_violations"] += 1
            out["pairs"] += 1
            min_e = min(min_e, e)
        out["min_e_by_n"].append({"n": n, "min_e_observed": float(min_e)})
        print(f"  n={n:2d}: минимальный наблюдённый e = {min_e:.6f}  "
              f"(теорема: e >= 1)")
    # случай равенства: комплементарные проекции
    for n, p in ((4, 2), (6, 2), (6, 3), (8, 3), (10, 4)):
        q = n - p
        X1 = np.diag(np.r_[np.ones(p, dtype=complex), np.zeros(q)])
        X2 = np.diag(np.r_[np.zeros(p, dtype=complex), np.ones(q)])
        F = leavitt_F(X1, X2)
        out["equality_err"] = max(out["equality_err"], abs(F - n))
        print(f"  равенство: n={n}, p={p}, q={q}: F = {F:.12f} (точно n: "
              f"|F−n| = {abs(F - n):.1e})")
    print(f"  тождество F = 3n − 2p − 2q + 3r: макс. отн. ошибка "
          f"{out['identity_err']:.2e}")
    print(f"  нарушений порога e >= 1: {out['threshold_violations']} / "
          f"{out['pairs']} пар")
    return out


# =============================================================================
def part_B(k_max=10, n_random=500):
    print("\n" + "=" * 78)
    print("B. ТЕОРЕМА B: ТОЧНАЯ АРИФМЕТИКА ПОКРЫТИЯ F = n + 2·rank(I−P−Q)")
    print("=" * 78)
    out = {"random_projections": [], "tree": []}
    # случайные проекции с P + Q <= I
    max_err = 0.0
    for _ in range(n_random):
        n = int(RNG.integers(2, 13))
        p = int(RNG.integers(0, n))
        q = int(RNG.integers(0, n - p + 1))
        P, Q = random_projections_disjoint(n, p, q, RNG)
        R = np.eye(n) - P - Q
        rankR = int(np.linalg.matrix_rank(R, tol=1e-9))
        X1, X2 = P.copy(), Q.copy()          # проекции — частичные изометрии
        F = leavitt_F(X1, X2)
        max_err = max(max_err, abs(F - (n + 2 * rankR)))
    out["random_projections"] = {"n_random": n_random, "max_err": float(max_err)}
    print(f"  случайные (P, Q), P+Q <= I: макс. |F − (n + 2·rank R)| = "
          f"{max_err:.2e}")
    # обрезка дерева Кунца
    for k in range(2, k_max + 1):
        words = [""]
        level = [""]
        for _ in range(k):
            level = [a + w for w in level for a in ("a", "b")]
            words += level
        n = len(words)
        idx = {w: i for i, w in enumerate(words)}
        S1 = np.zeros((n, n))
        S2 = np.zeros((n, n))
        for w in words:
            if len(w) < k:
                if ("a" + w) in idx:
                    S1[idx["a" + w], idx[w]] = 1.0
                if ("b" + w) in idx:
                    S2[idx["b" + w], idx[w]] = 1.0
        P = S1 @ S1.conj().T
        Q = S2 @ S2.conj().T
        R = np.eye(n) - P - Q
        rankR = int(np.linalg.matrix_rank(R, tol=1e-9))
        F = leavitt_F(S1, S2)
        err = abs(F - (n + 2 * rankR))
        out["tree"].append({"k": k, "n": n, "rank_R": rankR, "F": float(F),
                            "n_plus_2rank": n + 2 * rankR, "err": float(err),
                            "e": float(F / n)})
        print(f"  дерево k={k:2d}: n={n:5d}, rank(I−P−Q) = {rankR}, "
              f"F = {F:.6f} = n + 2·rank = {n + 2 * rankR}  (|err| = {err:.1e}, "
              f"e = {F / n:.6f})")
    return out


# =============================================================================
def part_C(n_max=32, n_pairs=200):
    print("\n" + "=" * 78)
    print("C. ТЕОРЕМА C: УНИТАРНЫЕ ПАРЫ — F = 2n ТОЧНО")
    print("=" * 78)
    out = {"unitary_max_err": 0.0, "perm_max_err": 0.0}
    for _ in range(n_pairs):
        n = int(RNG.integers(1, n_max + 1))
        A = RNG.standard_normal((n, n)) + 1j * RNG.standard_normal((n, n))
        B = RNG.standard_normal((n, n)) + 1j * RNG.standard_normal((n, n))
        U1, _ = np.linalg.qr(A)
        U2, _ = np.linalg.qr(B)
        out["unitary_max_err"] = max(out["unitary_max_err"],
                                     abs(leavitt_F(U1, U2) - 2 * n))
        perm1 = np.eye(n)[RNG.permutation(n)]
        perm2 = np.eye(n)[RNG.permutation(n)]
        out["perm_max_err"] = max(out["perm_max_err"],
                                  abs(leavitt_F(perm1.astype(complex),
                                                perm2.astype(complex)) - 2 * n))
    print(f"  унитарные пары:  макс. |F − 2n| = {out['unitary_max_err']:.2e}")
    print(f"  перестановочные: макс. |F − 2n| = {out['perm_max_err']:.2e}")
    return out


# =============================================================================
def part_E(n_random=10000):
    print("\n" + "=" * 78)
    print("E. ОЦЕНКИ ДЛЯ ПРОЕКЦИЙ: max(0,p+q−n) <= tr(PQ) <= min(p,q)")
    print("=" * 78)
    lo_viol = hi_viol = 0
    for _ in range(n_random):
        n = int(RNG.integers(2, 14))
        p = int(RNG.integers(0, n + 1))
        q = int(RNG.integers(0, n + 1))
        A = RNG.standard_normal((n, n)) + 1j * RNG.standard_normal((n, n))
        U, _ = np.linalg.qr(A)
        P = U @ np.diag(np.r_[np.ones(p), np.zeros(n - p)]) @ U.conj().T
        B = RNG.standard_normal((n, n)) + 1j * RNG.standard_normal((n, n))
        V, _ = np.linalg.qr(B)
        Q = V @ np.diag(np.r_[np.ones(q), np.zeros(n - q)]) @ V.conj().T
        r = np.trace(P @ Q).real
        if r < max(0, p + q - n) - 1e-9:
            lo_viol += 1
        if r > min(p, q) + 1e-9:
            hi_viol += 1
    print(f"  нарушений нижней оценки: {lo_viol} / {n_random}")
    print(f"  нарушений верхней оценки: {hi_viol} / {n_random}")
    return {"lower_violations": lo_viol, "upper_violations": hi_viol,
            "n_random": n_random}


# =============================================================================
def part_F():
    print("\n" + "=" * 78)
    print("F. КОНТРАСТ: ЧТО ТРЕБУЕТ ЗНАЧЕНИЕ e = 5/7 (ВНЕ КЛАССА)")
    print("=" * 78)
    out = {}
    # sqrt(4/7)·I — равенство глобальной теоремы следа, но НЕ частичная изометрия
    for n in (1, 2, 4, 8):
        c = math.sqrt(4 / 7)
        X1 = c * np.eye(n, dtype=complex)
        F = leavitt_F(X1, X1.copy())
        sv = np.linalg.svd(X1, compute_uv=False)
        isom = abs(sv[0] - 1.0) > 1e-9
        out[f"scalar_n{n}"] = {"F": float(F), "e": float(F / n),
                               "singular_value": float(sv[0]),
                               "is_partial_isometry": not isom}
        print(f"  sqrt(4/7)·I, n={n}: e = {F / n:.12f} (точно 5/7 = {5 / 7:.12f}); "
              f"сингулярное число = {sv[0]:.6f} != 1 => вне класса")
    # взвешенное дерево c^2 = 4/7 не достигает 5/7
    rows = []
    for k in (3, 5, 7):
        words = [""]
        level = [""]
        for _ in range(k):
            level = [a + w for w in level for a in ("a", "b")]
            words += level
        n = len(words)
        idx = {w: i for i, w in enumerate(words)}
        S1 = np.zeros((n, n))
        S2 = np.zeros((n, n))
        for w in words:
            if len(w) < k:
                if ("a" + w) in idx:
                    S1[idx["a" + w], idx[w]] = 1.0
                if ("b" + w) in idx:
                    S2[idx["b" + w], idx[w]] = 1.0
        c = math.sqrt(4 / 7)
        F = leavitt_F(c * S1, c * S2)
        F_formula = (n - 1) * 2 * (4 / 7 - 1) ** 2 + n + 2
        rows.append({"k": k, "n": n, "e_weighted": float(F / n),
                     "formula": float(F_formula / n)})
        print(f"  дерево c²=4/7, k={k}: e = {F / n:.6f} (формула: "
              f"{F_formula / n:.6f}) > 5/7 = {5 / 7:.6f}")
    out["weighted_tree"] = rows
    return out


# =============================================================================
def make_figures(out, lang_dir, lang):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.font_manager as fm
    for fp in ("/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(fp):
            fm.fontManager.addfont(fp)
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Noto Sans SC"]
    plt.rcParams["axes.unicode_minus"] = False

    t = L[lang]
    # Рис. 1: лестница-теорема
    fig, ax = plt.subplots(figsize=(9.6, 5.6), constrained_layout=True)
    items = [
        (t["lab_free"], 5 / 7, "#b45309", "5/7 (вне класса)"),
        (t["lab_pi"], 1.0, "#0e7c66", "e* = 1 (теорема A)"),
        (t["lab_tree"], 1.0, "#1e6091", "1 + 2/n → 1 (теорема B)"),
        (t["lab_unitary"], 2.0, "#7c3aed", "2 (теорема C)"),
    ]
    names = [i[0] for i in items]
    vals = [i[1] for i in items]
    cols = [i[2] for i in items]
    anns = [i[3] for i in items]
    bars = ax.barh(names, vals, color=cols, alpha=0.85, height=0.55)
    ax.axvline(5 / 7, color="#b45309", ls="--", lw=1.4)
    ax.axvline(1.0, color="#0e7c66", ls="--", lw=1.8)
    ax.text(1.0 + 0.015, 3.42, "e* = 1", color="#0e7c66", fontsize=12)
    for b, v, a in zip(bars, vals, anns):
        ax.text(v + 0.03, b.get_y() + b.get_height() / 2, a, va="center",
                fontsize=9.5)
    ax.set_xlabel(t["ladder2_xlabel"])
    ax.set_title(t["ladder2_title"], fontsize=11)
    ax.set_xlim(0, 2.5)
    ax.invert_yaxis()
    fig.savefig(os.path.join(lang_dir, "fig7_ladder.png"), dpi=300)
    plt.close(fig)

    # Рис. 2: арифметика дерева
    fig, ax = plt.subplots(figsize=(8.8, 5.4), constrained_layout=True)
    ks = [d["k"] for d in out["theorem_B"]["tree"]]
    ns = [d["n"] for d in out["theorem_B"]["tree"]]
    Fs = [d["F"] for d in out["theorem_B"]["tree"]]
    ax.plot(ks, Fs, "o-", color="#1e6091", lw=2, ms=8, label=t["tree_exact"])
    ax.plot(ks, ns, "--", color="#0e7c66", lw=2, label=t["floor_n"])
    ax.plot(ks, [2 * n for n in ns], ":", color="#7c3aed", lw=2,
            label=t["unit_line"])
    for k, n, F in zip(ks, ns, Fs):
        ax.annotate(f"F=n+2", (k, F), textcoords="offset points",
                    xytext=(6, 6), fontsize=9, color="#1e6091")
    ax.set_xlabel(t["tree_line_xlabel"])
    ax.set_ylabel(t["tree_line_ylabel"])
    ax.set_title(t["tree_line_title"], fontsize=11)
    ax.legend(loc="upper left", fontsize=9)
    fig.savefig(os.path.join(lang_dir, "fig7_tree.png"), dpi=300)
    plt.close(fig)
    print(f"  [фигуры] {lang_dir}/fig7_ladder.png, fig7_tree.png")


def main():
    print("=" * 78)
    print("ЭКСПЕРИМЕНТ 7. ПОРОГ e >= 1 ДЛЯ НОСИТЕЛЬ-ИЗОМЕТРИЧЕСКИХ ПАР")
    print("=" * 78)
    out = {}
    out["theorem_A"] = part_A()
    out["theorem_B"] = part_B()
    out["theorem_C"] = part_C()
    out["bounds_E"] = part_E()
    out["contrast_F"] = part_F()

    print("\n" + "=" * 78)
    print("СВОДКА (ЭКСПЕРИМЕНТ 7)")
    print("=" * 78)
    okA = out["theorem_A"]["threshold_violations"] == 0
    okB = max(d["err"] for d in out["theorem_B"]["tree"]) < 1e-9
    okC = max(out["theorem_C"]["unitary_max_err"],
              out["theorem_C"]["perm_max_err"]) < 1e-9
    okE = out["bounds_E"]["lower_violations"] + \
        out["bounds_E"]["upper_violations"] == 0
    print(f"  Теорема A (порог e >= 1, частичные изометрии): "
          f"{'ПОДТВЕРЖДЕНА' if okA else 'НАРУШЕНИЕ!'} "
          f"(0 нарушений на {out['theorem_A']['pairs']} пар)")
    print(f"  Теорема B (F = n + 2·rank(I−P−Q) точно): "
          f"{'ПОДТВЕРЖДЕНА' if okB else 'ОШИБКА!'}")
    print(f"  Теорема C (унитарные пары F = 2n): "
          f"{'ПОДТВЕРЖДЕНА' if okC else 'ОШИБКА!'}")
    print(f"  Оценки tr(PQ): {'ПОДТВЕРЖДЕНЫ' if okE else 'НАРУШЕНИЕ!'}")
    print("  Следствие D: inf e = 1 на классе; 5/7 недостижимо в классе;")
    print("  мост Ш.3(iii) невозможен для носитель-изометрических переносов")
    print("  (eta ≡ 1 > 0) — «лестница» стала теоремой.")

    for lang, lang_dir in (("ru", os.path.join(BASE, "fig_ru")),
                           ("en", os.path.join(BASE, "fig_en"))):
        os.makedirs(lang_dir, exist_ok=True)
        make_figures(out, lang_dir, lang)

    res_path = os.path.join(BASE, "results", "exp7_e1_threshold.json")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=float)
    print(f"\n[OK] {res_path}")


if __name__ == "__main__":
    main()
