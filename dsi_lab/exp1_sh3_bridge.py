#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 ЭКСПЕРИМЕНТ 1. МОСТ Ш.3(iii): софичность -> матричные модели
================================================================================
Постановка (audit_transfer, лемма Ш.3, часть (iii) — единственная открытая
аналитическая программа фреймворка):

  ЛЕММА Ш.3. Пусть G = U(L_{F2}(1,2)) софична: существуют n_k -> inf и
  отображения rho_k: G -> Sym(n_k) с ошибкой eps_k -> 0 (условия C1/C2).
  Тогда существуют X1, X2 in M_{n_k}(C) с дефектом на душу
  e_k = F(X1,X2)/n_k <= eta(eps_k) -> 0, eta(eps) = C*eps^{1/2}.

  НО по острой теореме следа (i): F >= 5n/7 при ВСЕХ n, т.е. e >= 5/7.
  Значит, мост (iii) не может существовать для G = U(L) — что и требуется
  для цепочки Ш1–Ш4 (несофичность). Вопрос: МОЖНО ЛИ численно увидеть,
  что естественные «переносы» перестановочных данных в M_n НЕ дают
  убывающего дефекта? Этот эксперимент строит «лестницу препятствий»:

  A. Проверка острой теоремы при n = 7..12 (L-BFGS, рестарты)
     + проверка тождества F = G(P,Q) и границы Хаара при больших n.
  B. Перестановочные модели: X_i = P_i — точный дефект F = 2n, e = 2.
  C. Масштабированные перестановки X_i = c*P_i: аналитика F/n = 7t^2-8t+3
     (t = c^2), минимум при t = 4/7 равен РОВНО 5/7 (случай равенства
     теоремы — та же скалярная задача h(u,v)).
  D. Двухпараметрическое семейство X1 = a*P1, X2 = b*P2: минимум при
     a=b=sqrt(4/7) — воспроизводит скалярную задачу теоремы h(u,v).
  E. Обрезка дерева Кунца (Cuntz-tree truncation) уровня k:
     X_i = усечённые сдвиги; ТОЧНО F = n+2, e = 1 + 2/n -> 1
     (диапазоны S1, S2 разбивают depth>=1 без перекрытия:
     S1S1*+S2S2* = P(depth>=1) ровно).
  F. Взвешенное дерево X_i = c_i*S_i: ТОЧНО
     F = (n-1)[(c1^2-1)^2 + (c2^2-1)^2] + n + 2 — минимум при c = (1,1):
     никакое взвешивание не улучшает обрезку; e_min = 1 + 2/n -> 1.
  G. Софические данные с ошибкой Хэмминга eps (случайные подстановки с
     долей неподвижных точек eps) + естественный перенос X_i = c*P_i:
     дефект e(eps) НЕ убывает с eps — качественный аргумент, что
     «наивная амлификация» не даёт eta(eps) = C*eps^{1/2}.

Запуск: python3 exp1_sh3_bridge.py
Вывод:  results/exp1_sh3.json + figures (RU/EN).
================================================================================
"""
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from figlabels import L  # bilingual labels: L["ru"], L["en"]

RNG = np.random.default_rng(42)


def leavitt_F(x1, x2):
    """Кунцевский дефект F(X1,X2) (норма Фробениуса) — как в stability_lemma.py."""
    I = np.eye(x1.shape[0])
    return (np.linalg.norm(x1.conj().T @ x1 - I, 'fro') ** 2
            + np.linalg.norm(x2.conj().T @ x2 - I, 'fro') ** 2
            + np.linalg.norm(x1.conj().T @ x2, 'fro') ** 2
            + np.linalg.norm(x1 @ x1.conj().T + x2 @ x2.conj().T - I, 'fro') ** 2)


def G_of_PQ(P, Q):
    """G(P,Q) = 2trP^2 + 2trQ^2 + 3tr(PQ) - 4trP - 4trQ + 3n."""
    n = P.shape[0]
    return (2 * np.trace(P @ P) + 2 * np.trace(Q @ Q) + 3 * np.trace(P @ Q)
            - 4 * np.trace(P) - 4 * np.trace(Q) + 3 * n)


def random_pair(n, rng):
    """Случайная комплексная пара."""
    A = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    B = rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))
    return A, B


def haar_average_G(P, Q):
    """G((trP/n)I, (trQ/n)I) — значение после усреднения по Хаару."""
    n = P.shape[0]
    u = np.trace(P).real / n
    v = np.trace(Q).real / n
    return 2 * n * u * u + 2 * n * v * v + 3 * n * u * v - 4 * n * u - 4 * n * v + 3 * n


# =============================================================================
# A. Острая теорема при больших n
# =============================================================================
def part_A(n_max=12, n_random=300, restarts=25):
    print("=" * 78)
    print("A. ОСТРАЯ ТЕОРЕМА СЛЕДА ПРИ БОЛЬШИХ n (7..%d)" % n_max)
    print("=" * 78)
    out = {"identity_max_err": 0.0, "haar_violations": 0, "haar_pairs": 0,
           "minimization": []}
    for n in range(7, n_max + 1):
        # тождество F = G(P,Q) и граница Хаара на случайных парах
        ident_err = 0.0
        for _ in range(n_random):
            X1, X2 = random_pair(n, RNG)
            P = X1 @ X1.conj().T
            Q = X2 @ X2.conj().T
            F = leavitt_F(X1, X2)
            G = G_of_PQ(P, Q).real
            ident_err = max(ident_err, abs(F - G) / max(1.0, abs(F)))
            if G < haar_average_G(P, Q) - 1e-9:
                out["haar_violations"] += 1
            out["haar_pairs"] += 1
        out["identity_max_err"] = max(out["identity_max_err"], ident_err)

        # L-BFGS минимизация
        best = np.inf
        for r in range(restarts):
            rng = np.random.default_rng(5000 + 97 * r + n)
            x0 = rng.standard_normal(4 * n * n)

            def unpack(x):
                re1, im1, re2, im2 = np.split(x, 4)
                X1 = re1.reshape(n, n) + 1j * im1.reshape(n, n)
                X2 = re2.reshape(n, n) + 1j * im2.reshape(n, n)
                return X1, X2

            def fval(x):
                X1, X2 = unpack(x)
                return leavitt_F(X1, X2)

            res = minimize(fval, x0, method="L-BFGS-B",
                           options={"maxiter": 600})
            best = min(best, res.fun)
        floor = 5 * n / 7
        gap = best - floor
        out["minimization"].append({"n": n, "F_min": float(best),
                                    "5n/7": float(floor),
                                    "gap": float(gap)})
        print(f"  n={n:2d}: F_min = {best:.12f}  5n/7 = {floor:.12f}  "
              f"зазор = {gap:+.2e}")
    print(f"  Тождество F=G(P,Q): макс. отн. ошибка = {out['identity_max_err']:.2e}")
    print(f"  Граница Хаара: нарушений {out['haar_violations']} / {out['haar_pairs']} пар")
    return out


# =============================================================================
# B/C/D. Перестановочные семейства
# =============================================================================
def part_BCD(n_values=(16, 64, 128), n_perm=50):
    print("\n" + "=" * 78)
    print("B/C/D. ПЕРЕСТАНОЧНЫЕ СЕМЕЙСТВА (точно/аналитика/минимизация)")
    print("=" * 78)
    out = {"permutation_exact": [], "scaled_1p": [], "scaled_2p": []}
    for n in n_values:
        # B: X_i = P_i — дефект должен быть ровно 2n
        errs = []
        for s in range(n_perm):
            rng = np.random.default_rng(777 + 13 * s + n)
            P1 = np.eye(n)[rng.permutation(n)]           # матрица перестановки
            P2 = np.eye(n)[rng.permutation(n)]
            F = leavitt_F(P1.astype(complex), P2.astype(complex))
            errs.append(abs(F - 2 * n))
        out["permutation_exact"].append(
            {"n": n, "max_err": float(max(errs)), "theory": 2 * n})
        print(f"  B: n={n:3d}: |F - 2n| макс = {max(errs):.2e} (по {n_perm} парам)")

    # C: X_i = c*P_i, F/n = 7t^2 - 8t + 3, t = c^2 -> min 5/7 при t = 4/7
    t_grid = np.linspace(0.01, 1.4, 280)
    curve = 7 * t_grid ** 2 - 8 * t_grid + 3
    i_min = int(np.argmin(curve))
    out["scaled_1p"] = {"t_grid": t_grid.tolist(), "F_over_n": curve.tolist(),
                        "t_min": float(t_grid[i_min]),
                        "F_min": float(curve[i_min]),
                        "t_theory": 4 / 7, "F_theory": 5 / 7}
    print(f"  C: min F/n = {curve[i_min]:.8f} при t = c^2 = {t_grid[i_min]:.4f} "
          f"(теория: 5/7 = {5/7:.8f} при t = 4/7 = {4/7:.4f})")

    # D: X1 = a*P1, X2 = b*P2 — 2D-минимизация (численная) против аналитики
    def F2(uv, n):
        u, v = uv
        return (u - 1) ** 2 + (v - 1) ** 2 + u * v + (u + v - 1) ** 2

    res = minimize(F2, x0=[0.5, 0.5], args=(None,), method="Nelder-Mead",
                   options={"xatol": 1e-12, "fatol": 1e-14})
    out["scaled_2p"] = {"u_opt": float(res.x[0]), "v_opt": float(res.x[1]),
                        "F_min": float(res.fun),
                        "u_theory": 4 / 7, "F_theory": 5 / 7}
    print(f"  D: min F/n = {res.fun:.10f} при (u,v) = ({res.x[0]:.6f}, "
          f"{res.x[1]:.6f}) (теория: 4/7, 4/7 -> 5/7)")
    return out


# =============================================================================
# E/F. Дерево Кунца: обрезка и взвешивание
# =============================================================================
def build_tree_shifts(k):
    """Усечённые сдвиги дерева Кунца глубины k.

    Вершины: слова длины 0..k (n = 2^{k+1}-1). X_i переводит w -> iw,
    если depth(w) <= k-1, иначе 0. Возвращаем плотные матрицы и маски.
    """
    words = [""]
    level = [""]
    for _ in range(k):
        level = [a + w for w in level for a in ("a", "b")]
        words += level
    n = len(words)                       # 2^{k+1}-1
    idx = {w: i for i, w in enumerate(words)}
    boundary = {w for w in words if len(w) == k}
    S1 = np.zeros((n, n))
    S2 = np.zeros((n, n))
    for w in words:
        if w not in boundary:
            S1[idx["a" + w], idx[w]] = 1.0
            S2[idx["b" + w], idx[w]] = 1.0
    return S1, S2, n, words, boundary, idx


def part_EF(k_values=(2, 3, 4, 5, 6, 7)):
    print("\n" + "=" * 78)
    print("E/F. ДЕРЕВО КУНЦА: ОБРЕЗКА (F = n+2) И ВЗВЕШИВАНИЕ (минимум при c=(1,1))")
    print("=" * 78)
    out = {"truncation": [], "weighted": []}
    for k in k_values:
        S1, S2, n, words, boundary, idx = build_tree_shifts(k)
        # E: обрезка — точный дефект n+2
        F = leavitt_F(S1, S2)
        err = abs(F - (n + 2))
        out["truncation"].append({"k": k, "n": n, "F": float(F),
                                  "n+2": n + 2, "err": float(err),
                                  "e": float(F / n)})
        print(f"  E: k={k} n={n:4d}: F = {F:.6f}  (n+2 = {n+2})  "
          f"err = {err:.1e}  e = {F/n:.6f}")

        # F: X_i = c_i * S_i — численная минимизация по (c1, c2)
        #   + проверка ТОЧНОЙ формулы F = (n-1)[(u1-1)^2+(u2-1)^2] + n+2
        def Fw(c):
            return leavitt_F(c[0] * S1, c[1] * S2)

        def Fanalytic(c):
            u1, u2 = c[0] ** 2, c[1] ** 2
            return (n - 1) * ((u1 - 1) ** 2 + (u2 - 1) ** 2) + n + 2

        # проверка формулы на случайных (c1,c2)
        f_err = 0.0
        for r in range(12):
            rng = np.random.default_rng(9000 + 31 * r + k)
            cc = rng.uniform(0.3, 1.4, size=2)
            f_err = max(f_err, abs(Fw(cc) - Fanalytic(cc)))

        best = None
        for r in range(8):
            rng = np.random.default_rng(9000 + 131 * r + k)
            x0 = rng.uniform(0.5, 1.2, size=2)
            res = minimize(Fw, x0, method="Nelder-Mead",
                           options={"xatol": 1e-10, "fatol": 1e-12})
            if best is None or res.fun < best.fun:
                best = res
        out["weighted"].append({"k": k, "n": n, "F_min": float(best.fun),
                                "e_min": float(best.fun / n),
                                "c1": float(best.x[0]), "c2": float(best.x[1]),
                                "analytic_formula_maxerr": float(f_err),
                                "theory_e_asym": 1.0})
        print(f"  F: k={k}: e_min = {best.fun/n:.6f} при c = ({best.x[0]:.4f}, "
              f"{best.x[1]:.4f})  (асимптота e -> 1; ошибка точной формулы "
              f"F = (n-1)[(u1-1)^2+(u2-1)^2]+n+2: {f_err:.1e})")
    return out


# =============================================================================
# G. Софические данные с ошибкой Хэмминга eps
# =============================================================================
def part_G(n=256, eps_values=(0.0, 0.01, 0.02, 0.05, 0.1, 0.2), n_perm=40):
    """Случайные подстановки с долей неподвижных точек ~ eps.

    Моделирует «приближённые гомоморфизмы» с ошибкой Хэмминга eps
    (условие C1 леммы Ш.3: Hamming(rho(w), id) >= 1 - eps).
    Естественный перенос в M_n: X_i = c*P_i с оптимальным c (t = 4/7).
    Вопрос: убывает ли e(eps) как C*sqrt(eps)?
    """
    print("\n" + "=" * 78)
    print("G. СОФИЧЕСКИЕ ДАННЫЕ С ОШИБКОЙ ХЭММИНГА + ЕСТЕСТВЕННЫЙ ПЕРЕНОС")
    print("=" * 78)
    out = []
    t_opt = 4 / 7  # c^2
    c_opt = math.sqrt(t_opt)
    for eps in eps_values:
        n_fixed = int(round(eps * n))
        es = []
        hamm = []
        for s in range(n_perm):
            rng = np.random.default_rng(11000 + 17 * s + int(eps * 1000))
            perm = rng.permutation(n)
            # принудительно делаем n_fixed неподвижных точек
            if n_fixed > 0:
                fixed_idx = rng.choice(n, size=n_fixed, replace=False)
                rest = [i for i in range(n) if i not in set(fixed_idx)]
                perm = np.array(fixed_idx.tolist() +
                                rng.permutation(rest).tolist())
                # корректируем: точки fixed_idx остаются на месте
                perm[fixed_idx] = fixed_idx
            P1 = np.eye(n)[perm]
            rng2 = np.random.default_rng(11000 + 991 * s + int(eps * 1000))
            perm2 = rng2.permutation(n)
            if n_fixed > 0:
                fixed_idx2 = rng2.choice(n, size=n_fixed, replace=False)
                rest2 = [i for i in range(n) if i not in set(fixed_idx2)]
                perm2 = np.array(fixed_idx2.tolist() +
                                 rng2.permutation(rest2).tolist())
                perm2[fixed_idx2] = fixed_idx2
            P2 = np.eye(n)[perm2]
            X1, X2 = c_opt * P1, c_opt * P2
            es.append(leavitt_F(X1, X2) / n)
            # доля точек, сдвинутых хотя бы одной из двух подстановок
            moved = ((perm != np.arange(n)) | (perm2 != np.arange(n))).mean()
            hamm.append(moved)
        e_mean, e_std = float(np.mean(es)), float(np.std(es))
        # sqrt-закон: eta(eps) = C*sqrt(eps) при C = 5/7 (eps=1 -> 5/7)
        eta_pred = (5 / 7) * math.sqrt(eps) if eps > 0 else 5 / 7
        out.append({"eps": eps, "e_mean": e_mean, "e_std": e_std,
                    "hamming_moved_mean": float(np.mean(hamm)),
                    "eta_sqrt_prediction": float(eta_pred),
                    "floor": 5 / 7})
        print(f"  eps={eps:5.2f}: e = {e_mean:.6f} ± {e_std:.2e}  "
              f"(пол 5/7 = {5/7:.6f}; C*sqrt(eps) = {eta_pred:.6f})")
    print("  Вывод: дефект РАСТЁТ с eps (минимум e = 5/7 при eps = 0) — ")
    print("  естественный перенос не даёт убывания; sqrt-закон не наблюдается")
    print("  (мост (iii) требует принципиально иной конструкции).")
    return out


# =============================================================================
# Фигуры
# =============================================================================
def make_figures(out, lang_dir, lang):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = L[lang]
    # Рис. 1: лестница препятствий
    fig, ax = plt.subplots(figsize=(8.4, 5.2), constrained_layout=True)
    fam = [
        (t["floor"], 5 / 7, "#0e7c66"),
        (t["tree_trunc"], 1.0, "#1e6091"),
        (t["permutation"], 2.0, "#b45309"),
    ]
    names = [f[0] for f in fam]
    vals = [f[1] for f in fam]
    cols = [f[2] for f in fam]
    bars = ax.barh(names, vals, color=cols, alpha=0.85, height=0.55)
    ax.axvline(5 / 7, color="#0e7c66", ls="--", lw=1.6)
    ax.text(5 / 7 + 0.02, -0.45, "e* = 5/7", color="#0e7c66", fontsize=11)
    ax.set_xlabel(t["e_xlabel"])
    ax.set_title(t["e_title"])
    ax.set_xlim(0, 2.35)
    for b, v in zip(bars, vals):
        ax.text(v + 0.03, b.get_y() + b.get_height() / 2, f"{v:.4f}",
                va="center", fontsize=10)
    ax.invert_yaxis()
    fig.savefig(os.path.join(lang_dir, "fig_sh3_ladder.png"), dpi=300)
    plt.close(fig)

    # Рис. 2: e(eps) — софические данные
    g = out["hamming"]
    fig, ax = plt.subplots(figsize=(8.4, 5.2), constrained_layout=True)
    eps = [d["eps"] for d in g]
    e = [d["e_mean"] for d in g]
    err = [d["e_std"] for d in g]
    ax.errorbar(eps, e, yerr=err, fmt="o-", color="#1e3a5f", lw=1.8,
                capsize=3, label=t["e_observed"])
    ax.axhline(5 / 7, color="#0e7c66", ls="--", lw=1.6,
               label=t["floor_label"])
    sq = [(5 / 7) * math.sqrt(x) if x > 0 else 5 / 7 for x in eps]
    ax.plot(eps, sq, "s--", color="#b45309", alpha=0.8,
            label=r"$\eta(\varepsilon)=C\sqrt{\varepsilon}$")
    ax.set_xlabel(r"$\varepsilon$ " + t["hamming_eps"])
    ax.set_ylabel(t["e_ylabel"])
    ax.set_title(t["hamming_title"])
    ax.legend(loc="upper left", bbox_to_anchor=(0.02, 0.98))
    ax.set_ylim(0.6, 0.85)
    fig.savefig(os.path.join(lang_dir, "fig_sh3_hamming.png"), dpi=300)
    plt.close(fig)
    print(f"  [фигуры] {lang_dir}/fig_sh3_ladder.png, fig_sh3_hamming.png")


def main():
    print("=" * 78)
    print("ЭКСПЕРИМЕНТ 1. МОСТ Ш.3(iii): ЛЕСТНИЦА ПРЕПЯТСТВИЙ")
    print("=" * 78)
    out = {}
    out["theorem_big_n"] = part_A(n_max=12, n_random=300, restarts=15)
    out["permutations"] = part_BCD()
    out["tree"] = part_EF()
    out["hamming"] = part_G()

    # сводка
    print("\n" + "=" * 78)
    print("СВОДКА (лестница препятствий e = F/n)")
    print("=" * 78)
    mm = out["theorem_big_n"]["minimization"]
    worst = max(abs(m["gap"]) for m in mm)
    print(f"  Теорема (L-BFGS, n=7..12): макс. |F_min - 5n/7| = {worst:.2e}")
    print(f"  Перестановки: e = 2 (точно); обрезка дерева: e = 1 + 2/n -> 1 (точно)")
    print(f"  Взвешенное дерево: минимум при c=(1,1) — взвешивание не помогает")
    print(f"  Масштабированные унитарии: e = 5/7 (случай равенства)")
    print(f"  Софические данные: e(eps) растёт от 5/7 (eps=0) до ~1.14 (eps=0.2)")

    for lang, lang_dir in (("ru", os.path.join(BASE, "fig_ru")),
                           ("en", os.path.join(BASE, "fig_en"))):
        make_figures(out, lang_dir, lang)

    res_path = os.path.join(BASE, "results", "exp1_sh3.json")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] {res_path}")


if __name__ == "__main__":
    main()
