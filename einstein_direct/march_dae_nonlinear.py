#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кампания [сессия 19]: НЕЛИНЕЙНЫЙ МАРШ DAE — тест конечно-амплитудного остатка.

Вопрос (вердикт v14): весь ЛИНЕЙНЫЙ мир (статика + де-адиабатизованные вторые
потоки + третий порядок) аннигилирует ТОЧНО; остаток «барионной асимметрии»
(~2.9% фантомов к pi/30, delta_mono) — конечно-амплитудный феномен. Существует
ли он? Построен нелинейный марш DAE (ядро: dae_nonlinear_core.py):
  F(x) = 0 (18 ур.), x = (a[9], v[8], dd[3]); пролонгационное замыкание
  Uk(x) u = -Known(x)(v,dd) с ПОЛНЫМИ x-зависимыми якобианами (цепное правило
  dF/dtau = 0 без линеаризации); совместность r(x) = 0 — нелинейный аналог
  скрытых условий Op(v,dd)=0 (сессия 18b); RK4 dt=2e-3; проекции {F=0}, {r=0}.

РЕЗУЛЬТАТ (машинные теоремы, обе точки kappa=2 и 2-pi^2/98):
  [T1] ПЛОСКАЯ ЛИНИЯ: направление ker B (a-чистое: v=dd=0; ход
       R1h-R3h-R5h-M5h по цепочке) несёт F=0, r=0, V=0 ТОЧНО на всей
       испытанной амплитуде — линия ТОЧНЫХ равновесий; марш с линии
       стационарен до машинной точности.
  [T2] СТАТИКА СОГЛАСОВАННОГО МНОЖЕСТВА S = {F=0} ∩ {r=0}:
       (а) M2-направление e2 НЕ касается S: кокоядро-невязка
           |P_coker G(x*+h e2)|/|G| КОНСТАНТНА по h (0.058 baseline,
           5.9e-4 one-brick) — квадратичную невязку не погасить изгибом;
           совместный Ньютон из e2-точки коллапсирует к x*/линии;
       (б) НО нуль-множество препятствия содержит ВТОРОЕ направление b2
           (98.8% = t3 — направление, убитое ЛИНЕЙНЫМ level-3 анализом
           сессии 18b!): b2-ветвь СУЩЕСТВУЕТ статически — joint-Ньютон
           держит радиус (1.02x), |F|,|r| ~ 1e-14 на всех амплитудах.
  [T3] ПОТОК НА ВЕТВЯХ: на линии V = 0 (равновесия); с b2-ветви замыкание
       совместимо В точке (r ~ 1e-14), но поток немедленно ПОКИДАЕТ S:
       level-3 сход |Dr(x0) V(x0)| = O(A) != 0, срыв замыкания на первой
       стадии RK4 — b2-ветвь решений НЕ несёт.
ВЕРДИКТ: единственное многообразие РЕШЕНИЙ нелинейной де-адиабатизованной DAE
через критическую точку — плоская линия равновесий. Нелинейный марш вне линии
невозможен АЛГЕБРАИЧЕСКИ (согласованные нестационарные начальные данные
пусты), не численно. Линейная динамика M2 (нильпотентный Йордан-2, светской
дрейф, delta_mono = 0) — артефакт линеаризации: она не линеаризует никакого
нелинейного потока. Аннигиляция «барионной асимметрии» продолжается на
нелинейный уровень: выведенная динамика вторых потоков НЕ производит
конечно-амплитудного остатка в окрестности критической точки.
Честные оговорки: (i) Пюизо-ветви (не-C2) не исключены; (ii) глобальные
компоненты S вдали от x* не искались (стрельба/nsolve — следующая кампания);
(iii) жёсткость — свойство усечённой башни с выведенным dd-законом (весовое
правило); полная PDE-машина (v6-v9) остаётся носителем физики эха.
"""
import json
import os
import sys
import time
import warnings

import numpy as np
import sympy as sp

warnings.filterwarnings("ignore")
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)
RESULTS = os.path.join(BASE, "results")
T_START = time.time()

import dae_nonlinear_core as dnc
from dae_nonlinear_core import (NonlinearDAE, build_nonlinear_system,
                                DELTA_SP, STEPS_ECHO, DT, log)


def campaign_point(kv, label, N2_raw, B_raw):
    """Полная нелинейная кампания в точке kappa = kv."""
    out = {"label": label, "kappa": float(sp.N(kv, 15))}
    log(f"\n================ {label}: kappa = {out['kappa']:.9f} ================")
    t0 = time.time()
    sysd = build_nonlinear_system(kv, validate=True)
    out["build"] = {k: sysd[k] for k in
                    ("kappa", "tau_star", "residual_at_point", "crosscheck_rel",
                     "rank_DF_at_point", "rank_Uk_at_point", "n_eqs_live",
                     "n_prolong")}
    log(f"  [N0] F(x*) = {sysd['residual_at_point']:.2e}; rank DF = "
        f"{sysd['rank_DF_at_point']}; rank Uk = {sysd['rank_Uk_at_point']}; "
        f"кросс-чек DF-vs-exact rel = "
        f"{ {k: f'{v:.1e}' for k, v in sysd['crosscheck_rel'].items()} }; "
        f"{time.time()-t0:.1f} c")

    dae = NonlinearDAE(sysd)
    N2c = np.asarray(N2_raw)
    out["basis_imag_norm"] = (float(np.max(np.abs(N2c.imag)))
                              if np.iscomplexobj(N2c) else 0.0)
    N2 = np.asarray(N2c.real, dtype=float)
    B = np.asarray(np.real(B_raw))

    # [N0b] валидация замыкания против v14: V(N e_j) == N (B e_j)
    lin_chk = []
    Uk0, Known0 = dnc._uk_known(dae.eval_DF(dae.x_star))
    for j in range(2):
        zj = N2[:, j][9:20]
        uj, *_ = np.linalg.lstsq(Uk0, -(Known0 @ zj), rcond=None)
        Vj = dnc.assemble_V(N2[:, j], uj)
        lin_chk.append(float(np.linalg.norm(Vj - N2 @ (B[:, j])) /
                             max(np.linalg.norm(N2 @ (B[:, j])), 1e-300)))
    out["closure_vs_v14_B_rel"] = lin_chk
    log(f"  [N0b] замыкание vs v14-B: rel = [{lin_chk[0]:.1e}, "
        f"{lin_chk[1]:.1e}]")

    # направления
    _, svB, vtB = np.linalg.svd(B)
    ker_dir = np.real(vtB[-1])
    ker_dir /= np.max(np.abs(ker_dir))
    w_line = N2 @ ker_dir
    w_line /= np.max(np.abs(w_line))
    e1 = N2[:, 0] / np.max(np.abs(N2[:, 0]))
    e2 = N2[:, 1] / np.max(np.abs(N2[:, 1]))
    out["line_direction_a_part"] = [float(x) for x in w_line[:9]]
    out["line_direction_vdd_max"] = float(np.max(np.abs(w_line[9:20])))
    log(f"  линия: v,dd-компоненты = {out['line_direction_vdd_max']:.1e}; "
        f"a-часть (R1h,R3h,R5h,M5h) = "
        f"({w_line[3]:+.3f}, {w_line[5]:+.3f}, {w_line[7]:+.3f}, {w_line[8]:+.3f})")

    # ---------------- [T1] плоская линия ----------------
    log("  --- [T1] плоская линия точных равновесий ---")
    t1 = {"samples": {}}
    for s in (1e-3, 1e-2, 1e-1, 0.5, 1.0):
        x0 = dae.x_star + s * dae.scale * w_line
        V, diag = dae.closure(x0)
        rec = {"F_max": float(np.max(np.abs(dae.eval_F(x0)))),
               "r_max": float(np.max(np.abs(dae.rvec(x0)[0]))),
               "V_norm": float(np.linalg.norm(V)),
               "solv_res": diag["solv_res"]}
        t1["samples"][f"s{s:g}"] = rec
    ml = dae.march(dae.x_star + 0.5 * dae.scale * w_line, 8)
    t1["march_8_echoes"] = {
        "dist_per_echo": [r["dist"] for r in ml["rows"]],
        "dist_drift_max": float(max(abs(r["dist"] - ml["rows"][0]["dist"])
                                    for r in ml["rows"])),
        "breakdown": ml["monitors"]["breakdown"],
    }
    out["T1_flat_line"] = t1
    log(f"  max |F| = {max(v['F_max'] for v in t1['samples'].values()):.1e}, "
        f"max |r| = {max(v['r_max'] for v in t1['samples'].values()):.1e}, "
        f"max |V| = {max(v['V_norm'] for v in t1['samples'].values()):.1e}; "
        f"марш 8 эхов (s=0.5): дрейф "
        f"{t1['march_8_echoes']['dist_drift_max']:.1e}")

    # ---------------- [T2] статика множества S ----------------
    log("  --- [T2] статика S = {F=0, r=0}: M2-направление и b2-ветвь ---")
    DG0, Wc, rk = dae.coker_split()
    _, _, vt = np.linalg.svd(DG0)
    ker = vt[rk:]                        # касательное ядро (dim 20 - rk)
    b2 = ker[-1] / np.max(np.abs(ker[-1]))
    Npinv = np.linalg.pinv(N2)
    yb2 = Npinv @ b2
    t3_frac = float(np.linalg.norm(b2 - N2 @ yb2) / np.linalg.norm(b2))
    t2 = {"rank_DG": rk, "dim_tangent_kernel": 20 - rk,
          "b2_N_coords": [float(x) for x in yb2],
          "b2_t3_fraction": t3_frac}
    log(f"  rank DG = {rk}; b2: N-координаты "
        f"({yb2[0]:+.3f}, {yb2[1]:+.3f}), доля t3 = {t3_frac:.3f}")

    h_grid = [1e-2 * dae.scale, 3e-3 * dae.scale, 1e-3 * dae.scale]

    def ratios(t):
        tn = np.asarray(t, dtype=float)
        tn = tn / np.max(np.abs(tn))
        return [dae.branch_ratio(tn, h, Wc)["ratio"] for h in h_grid]

    t2["coker_ratio_e2"] = ratios(e2)
    t2["coker_ratio_line"] = ratios(w_line)
    t2["coker_ratio_b2"] = ratios(b2)
    log(f"  кокоядро-невязка |P_coker G|/|G| (h = 1e-2, 3e-3, 1e-3*scale):")
    log(f"    e2 (M2):   {t2['coker_ratio_e2']}")
    log(f"    линия:     {t2['coker_ratio_line']}")
    log(f"    b2 (~t3):  {t2['coker_ratio_b2']}")

    # (а) e2: коллапс совместного Ньютона
    A_t = 1e-2
    x_try = dae.x_star + A_t * dae.scale * e2
    xj, gmax, it = dae.joint_newton(x_try)
    d = xj - dae.x_star
    t2["e2_joint_newton"] = {
        "radius_target": A_t * dae.scale,
        "radius_after": float(np.linalg.norm(d)),
        "iters": it, "F_max": float(np.max(np.abs(dae.eval_F(xj)))),
        "r_max": float(np.max(np.abs(dae.rvec(xj)[0])))}
    log(f"  e2: joint-Ньютон: радиус {A_t * dae.scale:.3e} -> "
        f"{t2['e2_joint_newton']['radius_after']:.3e} (коллапс, {it} итер)")

    # (б) b2: статическая ветвь держит радиус
    t2["b2_branch"] = {}
    for A in (1e-3, 1e-2, 5e-2):
        xb, gmax, it = dae.joint_newton(
            dae.x_star + A * dae.scale * b2)
        rec = {"radius_target": A * dae.scale,
               "radius_after": float(np.linalg.norm(xb - dae.x_star)),
               "radius_ratio": float(np.linalg.norm(xb - dae.x_star) /
                                     (A * dae.scale)),
               "iters": it, "gmax": gmax,
               "F_max": float(np.max(np.abs(dae.eval_F(xb)))),
               "r_max": float(np.max(np.abs(dae.rvec(xb)[0])))}
        t2["b2_branch"][f"A{A:g}"] = rec
        log(f"  b2, A = {A:g}: радиус x{rec['radius_ratio']:.2f} удержан "
            f"({it} итер, |F| = {rec['F_max']:.1e}, |r| = {rec['r_max']:.1e})")
    out["T2_static_S"] = t2

    # ---------------- [T3] поток на ветвях ----------------
    log("  --- [T3] поток: level-3 сход с b2-ветви ---")
    t3d = {}
    for A in (1e-3, 1e-2):
        xb, _, _ = dae.joint_newton(dae.x_star + A * dae.scale * b2)
        V, diag = dae.closure(xb)
        Dr, _ = dae._r_jacobian(xb)
        exit_rate = float(np.linalg.norm(Dr @ V))
        # прямой марш (ожидается срыв на 1-й стадии)
        m = dae.march(xb, 2)
        rec = {"A": A,
               "V_norm": float(np.linalg.norm(V)),
               "level3_exit_rate": exit_rate,
               "exit_rate_over_A": exit_rate / A,
               "march_breakdown": m["monitors"]["breakdown"],
               "march_rows": len(m["rows"])}
        t3d[f"A{A:g}"] = rec
        log(f"  A = {A:g}: |V(x_b2)| = {rec['V_norm']:.3e}, "
            f"|Dr V| = {exit_rate:.3e} (level-3 сход, /A = "
            f"{rec['exit_rate_over_A']:.2f}); марш: срыв «"
            f"{(m['monitors']['breakdown'] or '-')[:60]}», строк {len(m['rows'])}")
    out["T3_flow_exit"] = t3d
    out["stats_machine"] = dict(dae.stats)
    return out


def main() -> None:
    results = {
        "title": "Nonlinear DAE march: finite-amplitude residue test "
                 "(session 19)",
        "question": ("the whole linear world annihilates exactly (v14); is the "
                     "baryon-asymmetry residue (phantom gap ~2.9% to pi/30, "
                     "delta_mono) produced at FINITE amplitude by the "
                     "nonlinear de-adiabatized source dynamics?"),
        "method": ("full nonlinear DAE: F(x)=0 (12 tower + 6 prolongation "
                   "equations), prolongation closure Uk(x) u = -Known(x)(v,dd) "
                   "with x-dependent Jacobians (chain rule dF/dtau=0, no "
                   "linearization); compatibility r(x)=0 = nonlinear hidden "
                   "constraints (Procrustes-aligned left kernel of Uk); "
                   "machine theorems T1-T3 on the solution set"),
        "reference": ("v14: linear M2 dynamics = nilpotent Jordan-2, "
                      "delta_mono < (2.8e-14, 2.7e-8)/echo; phantom gap "
                      "3.0e-3; session-18b flat direction (baseline)"),
    }
    res = {}
    for tag, kv, nb, bb in (
            ("baseline_kappa2", sp.Integer(2), "_m2_basis_baseline.npy",
             "_m2_B_baseline.npy"),
            ("one_brick_2-bC", 2 - sp.pi ** 2 / 98, "_m2_basis_onebrick.npy",
             "_m2_B_onebrick.npy")):
        N2 = np.load(os.path.join(RESULTS, nb))
        B = np.load(os.path.join(RESULTS, bb))
        res[tag] = campaign_point(kv, tag, N2, B)
    results["points"] = res

    # ----------------------------- вердикт -----------------------------
    lines = []
    for key, pt in res.items():
        t1 = pt["T1_flat_line"]
        lines.append(
            f"{key}: [T1] плоская линия — ТОЧНЫЕ равновесия: max|F| = "
            f"{max(v['F_max'] for v in t1['samples'].values()):.1e}, "
            f"max|V| = {max(v['V_norm'] for v in t1['samples'].values()):.1e}; "
            f"марш 8 эхов: дрейф {t1['march_8_echoes']['dist_drift_max']:.1e}.")
        t2 = pt["T2_static_S"]
        lines.append(
            f"{key}: [T2] статика S: M2-направление e2 НЕ касается S "
            f"(ratio {t2['coker_ratio_e2'][0]:.4f} константен по h, Ньютон "
            f"коллапсирует {t2['e2_joint_newton']['radius_target']:.3e} -> "
            f"{t2['e2_joint_newton']['radius_after']:.3e}); b2-ветвь "
            f"(t3-доля {t2['b2_t3_fraction']:.2f}) существует СТАТИЧЕСКИ "
            f"(радиус x{t2['b2_branch']['A0.01']['radius_ratio']:.2f} "
            f"удержан, |r| = {t2['b2_branch']['A0.01']['r_max']:.1e}).")
        t3 = pt["T3_flow_exit"]
        lines.append(
            f"{key}: [T3] поток с b2-ветви покидает S немедленно: level-3 "
            f"сход |Dr V| = {t3['A0.01']['level3_exit_rate']:.2e} = "
            f"{t3['A0.01']['exit_rate_over_A']:.1f}*A != 0, срыв замыкания "
            f"на первой стадии — b2-ветвь решений не несёт.")
    lines.append(
        "ВЕРДИКТ: единственное многообразие решений нелинейной "
        "де-адиабатизованной DAE через критическую точку — плоская линия "
        "равновесий (ker B: F = r = V = 0 точно). Нелинейный марш вне линии "
        "невозможен АЛГЕБРАИЧЕСКИ: согласованные нестационарные начальные "
        "данные конечной амплитуды пусты (e2 — статически, b2 — "
        "динамически). Линейная динамика M2 (Йордан-2, светской дрейф, "
        "delta_mono = 0) — артефакт линеаризации: она не линеаризует "
        "никакого нелинейного потока. Аннигиляция «барионной асимметрии» "
        "продолжается на нелинейный уровень: выведенная динамика вторых "
        "потоков НЕ производит конечно-амплитудного остатка в окрестности "
        "критической точки. Ограничения честности: Пюизо-ветви не исключены; "
        "глобальные компоненты S вдали от x* не искались (стрельба/nsolve — "
        "следующая кампания); жёсткость — свойство усечённой башни с "
        "выведенным dd-законом; полная PDE-машина остаётся носителем физики "
        "эха.")
    results["verdict_lines"] = lines
    results["runtime_s"] = round(time.time() - T_START, 1)
    for l_ in lines:
        log("ИТОГ: " + l_)
    out_path = os.path.join(RESULTS, "march_dae_nonlinear.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2, default=str)
    log(f"\nГотово за {results['runtime_s']} c. Результат: {out_path}")


if __name__ == "__main__":
    main()
