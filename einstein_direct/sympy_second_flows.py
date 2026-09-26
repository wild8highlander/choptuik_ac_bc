#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кампания O6+ [сессия 17]: ВТОРЫЕ ПОТОКИ КАК ПЕРЕМЕННЫЕ ПРЕДЕЛЬНОГО ЦИКЛА.

Вопрос (автор, после гипотезы барионной асимметрии): порождает ли динамика
фазовый остаток монодромии delta_mono != 0 — «B-нарушение» контура башни, —
и это ли тот же остаток, что зазор фантомов Im lambda ~ 2.9% к pi/30?

Физическая постановка. Адиабатические таблицы источников (сеанс 11, аудит)
закрывают вторые z-коэффициенты профилей: W2'' -> (5 dW2 + 6 W2h)/S^4 и т.д.
Слот второго потока при этом ОБНУЛЁН (dd* = 0 «по построению таблиц»), хотя
машина сама содержит прецедент: P2'' -> (ddQ + 5 Q + 6 P2h)/S^4. Структура
коэффициентов 5,6 = (l+2)(l+3) и 9,20 = (l+4)(l+5) показывает: адиабатическая
таблица = истинная полиномиальная форма (l^2 + 5l + 6)F с отброшенным l^2.
Де-адиабатизация: W2'' -> (ddW2 + 5 dW2 + 6 W2h)/S^4, ddW2 := d^2 W2h/dtau^2
(коэффициент 1, как в прецеденте ddQ); то же для R3 (5,6), P4 (9,20).
T0/D0/R1 не трогаем: их таблицы (O1/O2/O3) — точные нижние уровни, не
адиабатические замыкания. ddQ — реликт (P2'' заранее замещается O5, в
уравнения ddQ не входит — проверено разведкой).

Метод. Кинематическое замыкание в анзаце A(tau) = A* + a e^{l tau}:
  flows = l*a, second flows = l^2*a  ->
  истинный полиномиальный карандаш M(l) = Ja + l*Jv*P + l^2*J2*P2  (18x9).
Ранг-падения = подлинные моды; протокол сеанса 14: кандидаты из
det(M^T M) = 0 (степень 36), фильтр sigma_min(M(l0)) на C, rel < 1e-8.

Дельта-моно. Для подлинной пары l = sigma ± i*omega:
  delta_mono = sigma * Delta, Delta = 2 pi/omega — лог-рост моды за эхо
  (нормировочно-инвариантная «монодромия != 1»). Дополнительно, индикативно:
  фазовый сдвиг шестистанционного контура на цикле с гексцикл- staggering
  tau_j = j*Delta/6 (предположение равномерного шага — помечено).
"""
import json
import os
import sys
import time
import types

import numpy as np
import sympy as sp

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)

RESULTS = os.path.join(BASE, "results")
T_START = time.time()
_MATRICES = {}  # label -> (A_n, B_n, C_n) для верификации


def log(msg):
    print(msg, flush=True)


# ------------------------------------------------------------------ патч ----
C2_OLD = "sp.Rational(1, 2) * KAPPA_S * r_e * t_e**2"
TH_OLD = "sp.Rational(1, 2) * KAPPA_S * s_e * t_e"
C1_OLD = "sp.Rational(1, 2) * KAPPA_S * r_e * s_e**2"
KDEF_OLD = "KAPPA_S = sp.Integer(2)"


def load_patched(kc1, kc2, kth):
    with open(os.path.join(BASE, "sympy_center_o6.py"), encoding="utf-8") as fh:
        src = fh.read()
    for old in (C2_OLD, TH_OLD, C1_OLD, KDEF_OLD):
        assert src.count(old) == 1, f"patch anchor not unique: {old!r}"
    src = src.replace(KDEF_OLD,
                      "K2C1 = _KC1\nK2C2 = _KC2\nK2TH = _KTH\nKAPPA_S = K2TH")
    src = src.replace(C2_OLD, "sp.Rational(1, 2) * K2C2 * r_e * t_e**2")
    src = src.replace(TH_OLD, "sp.Rational(1, 2) * K2TH * s_e * t_e")
    src = src.replace(C1_OLD, "sp.Rational(1, 2) * K2C1 * r_e * s_e**2")
    mod = types.ModuleType("sympy_center_o6")
    mod.__file__ = os.path.join(BASE, "sympy_center_o6.py")
    mod.__dict__["_KC1"] = kc1
    mod.__dict__["_KC2"] = kc2
    mod.__dict__["_KTH"] = kth
    exec(compile(src, mod.__file__, "exec"), mod.__dict__)  # noqa: S102
    sys.modules.pop("sympy_p4_einstein_hilbert", None)
    sys.modules["sympy_center_o6"] = mod
    import sympy_p4_einstein_hilbert as p4  # noqa: E402
    return mod, p4


# ------------------------------------------------- z-система с живыми dd ----
def build_zc_sf(o6, p4):
    """zc с де-адиабатизованными таблицами источников (слоты dd*, коэфф. 1)."""
    ddW2 = sp.Symbol("ddW2h")
    ddR3 = sp.Symbol("ddR3h")
    ddP4 = sp.Symbol("ddP4h")
    y, S = o6.y, o6.S
    ext_tbl = {
        sp.diff(o6.W2, y, 2): (ddW2 + 5 * p4.dW2 + 6 * p4.W2h) / S**4,
        sp.diff(o6.R3, y, 2): (ddR3 + 5 * p4.dR3 + 6 * p4.R3h) / S**4,
        sp.diff(o6.P4, y, 2): (ddP4 + 9 * p4.dP4 + 20 * p4.P4h) / S**6,
        sp.diff(o6.R5, y): (p4.dR5 + 4 * p4.R5h) / S**5,
    }
    coeffs = {nm: o6.series_coeffs(res, p4.ORDERS[nm])
              for nm, res in o6.RESIDUALS.items()}
    lv, ok = o6.lower_levels(coeffs)
    for k_, v_ in ok.items():
        assert sp.sstr(v_) == "0", f"форма {k_} не верифицирована"
    subs_lower = {
        o6.P0.diff(y, 2): lv["O1"],
        o6.R1.diff(y): lv["O2"],
        o6.W0.diff(y, 2): lv["O3"],
        o6.P2.diff(y, 2): lv["O5"],
        o6.M3: lv["O4"],
    }
    zc = {}
    for nm, arr in coeffs.items():
        for k_, co in enumerate(arr):
            if co == 0:
                continue
            e = co.subs(subs_lower)
            e = e.subs(ext_tbl)
            e = o6.to_z(e)
            kk, ze = o6.purify(e)
            if kk is None:
                zc[f"{nm}_xi{k_}"] = {"status": "unpurified"}
                continue
            ze = sp.cancel(sp.together(sp.expand(ze)))
            num, den = sp.fraction(ze)
            num = sp.simplify(sp.expand(num))
            if num.has(sp.Derivative):
                zc[f"{nm}_xi{k_}"] = {"status": "derivative_survived"}
                continue
            if num == 0:
                continue
            zc[f"{nm}_xi{k_}"] = {
                "status": "ok", "purity": kk, "num": num,
                "den": sp.sstr(sp.simplify(den)) if den != 1 else "1",
            }
    return zc, (ddW2, ddR3, ddP4)


# ------------------------------------------------------------------ QEP -----
def qep_at_point(F, amps, flows, dds, subv, point, label):
    """Истинный QEP M(l) = Ja + l*Jv*P + l^2*J2*P2 в точке + фильтр."""
    from scipy.linalg import eig as scipy_eig
    Ja = sp.Matrix(len(F), len(amps),
                   lambda i_, j_: sp.diff(F[i_], amps[j_]).subs(subv).subs(point))
    Jv = sp.Matrix(len(F), len(flows),
                   lambda i_, j_: sp.diff(F[i_], flows[j_]).subs(subv).subs(point))
    J2 = sp.Matrix(len(F), len(dds),
                   lambda i_, j_: sp.diff(F[i_], dds[j_]).subs(subv).subs(point))
    flow_amp_idx = {0: 0, 1: 2, 2: 1, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}
    Pproj = sp.zeros(len(flows), len(amps))
    for i_, j_ in flow_amp_idx.items():
        Pproj[i_, j_] = 1
    dd_amp_idx = {0: 4, 1: 5, 2: 6}  # ddW2->W2h, ddR3->R3h, ddP4->P4h
    P2proj = sp.zeros(len(dds), len(amps))
    for i_, j_ in dd_amp_idx.items():
        P2proj[i_, j_] = 1
    A_n = np.array(Ja.evalf(20).tolist(), dtype=complex)
    B_n = np.array((Jv * Pproj).evalf(20).tolist(), dtype=complex)
    C_n = np.array((J2 * P2proj).evalf(20).tolist(), dtype=complex)

    def svrel(lam0):
        Mlam = A_n + lam0 * B_n + lam0**2 * C_n
        sv = np.linalg.svd(Mlam, compute_uv=False)
        return float(sv[-1] / sv[0]), Mlam

    #Candidates: det(M(l)^T M(l)) = 0, G(l) = sum E_k l^k, степень 4
    E0 = A_n.conj().T @ A_n
    E1 = A_n.conj().T @ B_n + B_n.conj().T @ A_n
    E2 = A_n.conj().T @ C_n + C_n.conj().T @ A_n + B_n.conj().T @ B_n
    E3 = B_n.conj().T @ C_n + C_n.conj().T @ B_n
    E4 = C_n.conj().T @ C_n
    n = 9
    A0 = np.zeros((4 * n, 4 * n), dtype=complex)
    A1 = np.zeros((4 * n, 4 * n), dtype=complex)
    A0[:n, :n] = E0
    A0[:n, n:2 * n] = E1
    A0[:n, 2 * n:3 * n] = E2
    A0[:n, 3 * n:] = E3
    A0[n:2 * n, n:2 * n] = np.eye(n)
    A0[2 * n:3 * n, 2 * n:3 * n] = np.eye(n)
    A0[3 * n:, 3 * n:] = np.eye(n)
    A1[:n, 3 * n:] = -E4
    A1[n:2 * n, :n] = np.eye(n)
    A1[2 * n:3 * n, n:2 * n] = np.eye(n)
    A1[3 * n:, 2 * n:3 * n] = np.eye(n)
    lams = scipy_eig(A0, A1, right=False)
    lams = np.array([l_ for l_ in lams if np.isfinite(l_) and abs(l_) < 1e8])

    genuine, phantoms = [], []
    for lam0 in lams:
        rel, Mlam = svrel(lam0)
        rec = {"lambda": [float(np.real(lam0)), float(np.imag(lam0))],
               "rel_sigma_min": rel}
        if rel < 1e-8:
            _, _, vh = np.linalg.svd(Mlam)
            v = np.conj(vh[-1])
            rec["mode_shape"] = [float(np.real(x_)) for x_ in v]
            rec["mode_shape_imag"] = [float(np.imag(x_)) for x_ in v]
            genuine.append(rec)
        else:
            phantoms.append(rec)
    out = {
        "label": label,
        "n_candidate_roots": int(len(lams)),
        "n_genuine": len(genuine),
        "genuine": genuine,
        "n_phantoms": len(phantoms),
        "phantoms": sorted(phantoms, key=lambda r_: -abs(complex(r_["lambda"][0], r_["lambda"][1])))[:14],
        "norms": {"sv_max_M0": float(np.linalg.svd(A_n, compute_uv=False)[0]),
                  "sv_min_M0": float(np.linalg.svd(A_n, compute_uv=False)[-1]),
                  "sv_max_C": float(np.linalg.svd(C_n, compute_uv=False)[0]),
                  "rank_C": int(np.linalg.matrix_rank(C_n, tol=1e-10))},
    }
    return out, (A_n, B_n, C_n)


# --------------------------------------------------------------- контур -----
def contour_phase(mode, amps_vals, delta):
    """Индикативно: фазовый сдвиг шестистанционного контура на цикле.
    Staggering tau_j = j*Delta/6 (гексцикл: 6 станций, равномерный шаг —
    ПРЕДПОЛОЖЕНИЕ, помечено). ln Pi = sum_j e^{l tau_j} (v_{j+1}/A_{j+1} - v_j/A_j).
    mode: (lam, v) с v в базисе amps; amps_vals: значения станций в точке."""
    lam = complex(mode[0])
    v = np.array(mode[1], dtype=complex)
    contour = [3, 0, 1, 5, 4, 7]  # R1h, T0h, P2h, R3h, W2h, R5h (индексы amps)
    rel = v / np.array(amps_vals, dtype=complex)
    m = max(abs(rel[c_]) for c_ in contour)
    rel = rel / m
    total = 0.0 + 0.0j
    for j_ in range(6):
        a_, b_ = contour[j_], contour[(j_ + 1) % 6]
        tau_j = j_ * delta / 6.0
        total += np.exp(lam * tau_j) * (rel[b_] - rel[a_])
    return total


# ------------------------------------------------------------------ main ----
def campaign_point(kv, label):
    """Полный прогон в точке kappa = kv (равномерная связь)."""
    out = {"kappa": float(sp.N(kv, 15)), "label": label}
    log(f"\n================ {label}: kappa = {out['kappa']:.9f} ================")
    o6, p4 = load_patched(kv, kv, kv)
    t0 = time.time()
    zc_adiab = p4.build_z_coefficients()
    zc_sf, dds = build_zc_sf(o6, p4)
    log(f"  z-системы: адиабатическая + де-адиабатизованная ({time.time()-t0:.1f} c)")

    # [S0] регрессия: dd = 0 -> точное совпадение с адиабатической
    ok_a = {k: v for k, v in zc_adiab.items() if v.get("status") == "ok"}
    ok_sf = {k: v for k, v in zc_sf.items() if v.get("status") == "ok"}
    zero_dd = {d_: 0 for d_ in dds}
    reg = {}
    for k_ in sorted(set(ok_a) | set(ok_sf)):
        na_ = sp.expand(ok_a[k_]["num"]) if k_ in ok_a else None
        ns_ = sp.expand(ok_sf[k_]["num"].subs(zero_dd)) if k_ in ok_sf else None
        if na_ is None or ns_ is None:
            reg[k_] = "SET_MISMATCH"
        else:
            reg[k_] = bool(sp.simplify(sp.expand(ns_ - na_)) == 0)
    reg_ok = all(v_ is True for v_ in reg.values())
    out["regression_dd0_equals_adiabatic"] = {"per_equation": reg, "all_ok": reg_ok}
    log(f"  [S0] регрессия dd=0 == адиабатика: {reg_ok} "
        f"({sum(1 for v_ in reg.values() if v_ is True)}/{len(reg)})")

    # замороженная цепочка (на де-адиабатизованной системе, все потоки/dd = 0)
    zero_all = {f_: 0 for f_ in (p4.dT0, p4.dD0, p4.Qh, p4.dR1, p4.dW2,
                                 p4.dR3, p4.dP4, p4.dR5)}
    zero_all.update(zero_dd)
    eqs_frozen = {k: sp.expand(v["num"].subs(zero_all))
                  for k, v in ok_sf.items() if sp.expand(v["num"].subs(zero_all)) != 0}
    # K-символов нет: patched o6 несёт K2C1/K2C2/K2TH = kv (числа).
    # Якорь семейства (сеанс 15, точно): tau* = 27/(2*kappa).
    tv = sp.N(27 / (2 * kv), 25)
    t0v = sp.sqrt(sp.Float(tv, 25))

    T0h, P2h, D0h, R1h = p4.T0h, p4.P2h, p4.D0h, p4.R1h
    W2h, R3h, P4h, R5h, M5h = p4.W2h, p4.R3h, p4.P4h, p4.R5h, p4.M5h
    subs = []

    def solv(key, tgt):
        e = sp.simplify(sp.expand(eqs_frozen[key].subs(subs)))
        r = sp.solve(sp.Eq(e, 0), tgt)
        assert r, f"цепочка: {key} не решилась относительно {tgt}"
        return sp.simplify(sp.cancel(r[0]))

    d0 = solv("Mdef_xi3", D0h); subs.append((D0h, d0))
    r3 = solv("UV_xi1", R3h); subs.append((R3h, r3))
    w2 = solv("C2_xi1", W2h); subs.append((W2h, w2))
    r3 = sp.simplify(r3.subs(W2h, w2)); subs[1] = (R3h, r3)
    p2 = solv("C2_xi2", P2h); subs.append((P2h, p2))
    r5 = solv("C2_xi3", R5h); subs.append((R5h, r5))
    m5 = solv("TH_xi2", M5h); subs.append((M5h, m5))
    p4v = solv("SC_xi4", P4h); subs.append((P4h, p4v))
    chain = {"D0h": d0, "R3h": r3, "W2h": w2, "P2h": p2,
             "R5h": r5, "M5h": m5, "P4h": p4v}
    out["chain_symbolic"] = {k_: sp.sstr(v_) for k_, v_ in chain.items()}

    # точка
    point = {T0h: t0v, R1h: sp.Float(1, 25), D0h: sp.Float(0, 25)}
    for k_ in ("R3h", "W2h", "P2h", "R5h", "M5h", "P4h"):
        sym = {"R3h": R3h, "W2h": W2h, "P2h": P2h, "R5h": R5h,
               "M5h": M5h, "P4h": P4h}[k_]
        point[sym] = sp.N(chain[k_].subs(T0h, t0v).subs(R1h, 1), 25)
    for f_ in (p4.dT0, p4.dD0, p4.Qh, p4.dR1, p4.dW2, p4.dR3, p4.dP4, p4.dR5):
        point[f_] = sp.Float(0, 25)
    for d_ in dds:
        point[d_] = sp.Float(0, 25)

    # живые уравнения + пролонгации = F (18)
    eqs_live = [sp.expand(v["num"]) for v in ok_sf.values() if sp.expand(v["num"]) != 0]
    flow_of = {D0h: p4.dD0, R3h: p4.dR3, W2h: p4.dW2,
               P2h: p4.Qh, R5h: p4.dR5, P4h: p4.dP4}
    prolong = []
    for amp, form in subs:
        if amp not in flow_of:
            continue
        e_ = (sp.diff(form, T0h) * p4.dT0 + sp.diff(form, R1h) * p4.dR1
              - flow_of[amp])
        prolong.append(sp.expand(e_))
    F = eqs_live + prolong
    log(f"  система: {len(eqs_live)} башенных + {len(prolong)} пролонг. = {len(F)} ур.")

    resmax = 0.0
    for e_ in F:
        rv = complex(sp.N(e_.subs(point), 20))
        resmax = max(resmax, abs(rv))
    out["max_residual_at_point"] = float(resmax)
    log(f"  max |невязка| в точке (flows=dd=0): {resmax:.2e}")

    # QEP
    amps = [T0h, P2h, D0h, R1h, W2h, R3h, P4h, R5h, M5h]
    flows = [p4.dT0, p4.dD0, p4.Qh, p4.dR1, p4.dW2, p4.dR3, p4.dP4, p4.dR5]
    qep, (A_n, B_n, C_n) = qep_at_point(F, amps, flows, list(dds), {}, point, label)
    _MATRICES[label] = (A_n, B_n, C_n)
    out["qep"] = qep
    log(f"  [S1] QEP: кандидатов {qep['n_candidate_roots']}, "
        f"подлинных {qep['n_genuine']}, фантомов {qep['n_phantoms']}; "
        f"rank C = {qep['norms']['rank_C']} (l^2-сектор "
        f"{'ПУСТ' if qep['norms']['rank_C'] == 0 else 'жив'})")
    for g_ in qep["genuine"]:
        log(f"    подлинная мода: l = {g_['lambda'][0]:+.6f} "
            f"{g_['lambda'][1]:+.6f}i, rel_sigma_min = {g_['rel_sigma_min']:.2e}")

    # [S2] анализ подлинных мод: delta_mono = sigma*Delta, частоты
    Delta_sp = 0.7330382858376652  # измеренное эхо (v8, модель B)
    omega_echo = 2 * np.pi / Delta_sp
    analysis = {"Delta_sp": Delta_sp, "omega_echo_2pi_over_Delta": omega_echo,
                "modes": []}
    amps_vals = [float(sp.N(point[a_], 15)) for a_ in amps]
    for g_ in qep["genuine"]:
        lam0 = complex(g_["lambda"][0], g_["lambda"][1])
        rec = {"lambda": g_["lambda"]}
        if abs(lam0.imag) > 1e-9:
            Delta = 2 * np.pi / abs(lam0.imag)
            rec["Delta_cycle"] = float(Delta)
            rec["delta_mono_sigma_times_Delta"] = float(lam0.real * Delta)
            rec["omega_over_omega_echo"] = float(abs(lam0.imag) / omega_echo)
            ladder = [(k_, float(sp.N(k_ * sp.pi / 30, 15))) for k_ in range(1, 31)]
            k_best, L_best = min(ladder, key=lambda t_: abs(t_[1] - abs(lam0.imag)))
            rec["nearest_k_pi_over_30"] = {"k": k_best, "value": L_best,
                                           "rel_diff_pct": float(100 * abs(L_best - abs(lam0.imag)) / L_best)}
            if "mode_shape" in g_:
                v = np.array(g_["mode_shape"]) + 1j * np.array(g_["mode_shape_imag"])
                ph = contour_phase((lam0, list(v)), amps_vals, Delta)
                rec["contour_phase_per_unit_perturbation"] = {
                    "re": float(np.real(ph)), "im": float(np.imag(ph)),
                    "assumption": "staggering tau_j = j*Delta/6 (гексцикл), индикативно",
                }
        analysis["modes"].append(rec)
        log(f"    [S2] мода l = {lam0.real:+.6f} {lam0.imag:+.6f}i: "
            f"Delta = {rec.get('Delta_cycle', float('nan')):.4f}, "
            f"delta_mono = sigma*Delta = {rec.get('delta_mono_sigma_times_Delta', float('nan')):+.4f}")
    out["analysis"] = analysis
    return out


def main() -> None:
    results = {
        "title": "Second flows as limit-cycle variables (O6+ campaign, session 17)",
        "question": ("does the de-adiabatized source dynamics produce a true "
                     "oscillatory mode and a monodromy residue delta_mono != 0 "
                     "(the tower's 'B-violation')? is it the same residue as "
                     "the phantom Im lambda gap ~2.9% to pi/30?"),
        "method": ("de-adiabatized tables W2''/R3''/P4'' with dd-slots "
                   "(coefficient 1, ddQ precedent); true quadratic pencil "
                   "M(lam) = Ja + lam Jv P + lam^2 J2 P2 (18x9); candidates "
                   "from det(M^T M) deg 36 companion; sigma_min filter "
                   "rel < 1e-8 (session-14 protocol); delta_mono = sigma*Delta"),
    }
    pts = []
    pts.append(campaign_point(sp.Integer(2), "baseline_kappa2"))
    bC = sp.pi**2 / 98
    pts.append(campaign_point(2 - bC, "one_brick_2-bC"))
    results["points"] = pts

    # сравнение с фантомами Im lambda (сессия 15/16)
    try:
        with open(os.path.join(RESULTS, "spinor_corrections_one_brick.json"),
                  encoding="utf-8") as fh:
            ph = json.load(fh)
        ims = [abs(p_["lambda"][1]) for p_ in ph["phantoms"]]
        results["phantom_Im_reference_one_brick"] = sorted(ims)
    except Exception as ex:  # noqa: BLE001
        results["phantom_Im_reference_one_brick"] = f"unavailable: {ex}"

    # честный вердикт
    lines = []
    for pt in pts:
        q = pt["qep"]
        gens = q["genuine"]
        osc = [g_ for g_ in gens if abs(g_["lambda"][1]) > 1e-9]
        real = [g_ for g_ in gens if abs(g_["lambda"][1]) <= 1e-9]
        lines.append(
            f"{pt['label']}: dd-сектор rank C = {q['norms']['rank_C']}; "
            f"подлинных мод {len(gens)} "
            f"(осцилляторных {len(osc)}, вещественных/нулевых {len(real)})")
        for m_ in pt["analysis"]["modes"]:
            if "delta_mono_sigma_times_Delta" in m_:
                lines.append(
                    f"  l = {m_['lambda'][0]:+.5f}{m_['lambda'][1]:+.5f}i: "
                    f"Delta = {m_['Delta_cycle']:.4f}, "
                    f"delta_mono = {m_['delta_mono_sigma_times_Delta']:+.4f}, "
                    f"ближайшая k*pi/30: k={m_['nearest_k_pi_over_30']['k']} "
                    f"({m_['nearest_k_pi_over_30']['rel_diff_pct']:+.2f}%)")
    results["verdict_lines"] = lines
    results["runtime_s"] = round(time.time() - T_START, 1)
    for l_ in lines:
        log("ВЕРДИКТ: " + l_)

    out_path = os.path.join(RESULTS, "second_flows_limit_cycle.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2, default=str)
    log(f"\nГотово за {results['runtime_s']} c. Результат: {out_path}")


if __name__ == "__main__":
    main()
