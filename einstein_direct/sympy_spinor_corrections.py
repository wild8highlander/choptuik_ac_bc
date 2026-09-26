#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
ТРИ ПОПРАВКИ (b-C, a-C, a-B) В БАШНЯХ: КАНАЛЫ СВЯЗИ, ИСПРАВЛЕННЫЕ ТОЧКИ,
ЗАМЫКАНИЕ НА PI/30 (сеанс 15)
================================================================================

Вопрос автора: может, где-то в уравнениях Эйнштейна есть "ошибка"/пропуск, и
замыкание на пи/30 не получается потому, что мы сознательно НЕ встраивали в
вычисления три вычисленных поправки репозитория (a-C торможение, b-C Бэрри,
a-B) как естественные функции и формулы. Проверяем машинно.

ПОПРАВКИ (репозиторий: docs/monograph + audit_transfer, машинно верифицированы):
  фазы генераторов Γ(2,3,7):  δ_A = π/2,  δ_B = π/3,  δ_C = π/7
  Бэрри:   beta(d)  = d^2/2            -> bC = beta(δ_C) = π^2/98
  тормож.: alpha(d) = d^5/22 (k=b2(K3)) -> aC = alpha(δ_C) ≈ 1/1200
                                        -> aB = alpha(δ_B) = π^5/5346

ДВЕРИ ВСТРАИВАНИЯ (E-уровень, каналы квадратичных градиентов скаляра):
  C1: (kappa/2) r s^2   (s = Phi_u, исходящий канал)   -> kappa_C1
  C2: (kappa/2) r t^2   (t = Phi_v, коллапсный канал)   -> kappa_C2
  TH: (kappa/2) s t     (кросс-канал массы/кривизны)    -> kappa_TH
  SC/UV/Mdef — БЕЗ kappa (чистая геометрия) — проверяется машиной [S1].

УРОВНИ:
  [S0] Поправки как точные функции + кросс-чек по JSON монографии.
  [S1] Аудит дверей: символьные kappa по каналам; карта каналов по уровням;
       СТРУКТУРНАЯ СВЯЗКА кольца (kappa_C1 = kappa_C2 — условие существования
       CSS-точки, факторизация C1-невязки); ветви tau и резольвента.
  [S2] Исправленные башни по схемам встраивания: цепочка, ветви, tau*_corr,
       кольцо, часы, книги ln(tau*) против якорей kappa_obs.
  [S3] Тесты замыкания на pi/30: книги (скан комбинаций — честно помечен как
       скан), nsimplify tau*_corr, отношения к лестнице k*pi/30.
  [S4] Спектр карандаша в исправленной точке (QEP + sigma_min-фильтр фантомов);
       Im lambda фантомов против спинорной лестницы k*pi/30 (k=1..15).

Запуск: python3 sympy_spinor_corrections.py   (~2-5 мин)
Результат: results/spinor_corrections.json
================================================================================
"""
from __future__ import annotations

import json
import os
import sys
import time
import types

import numpy as np
import sympy as sp

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
RESULTS = os.path.join(BASE, "results")
OUT_PATH = os.path.join(RESULTS, "spinor_corrections.json")

log = print
T_START = time.time()


def sstr(e_):
    return sp.sstr(sp.factor(sp.cancel(sp.together(e_))))


# ------------------------------------------------------------------------------
# [S0] Три поправки как точные функции + кросс-чек по репозиторию
# ------------------------------------------------------------------------------
def s0_corrections():
    log("[S0] Поправки как точные функции; кросс-чек по JSON монографии...")
    PI = sp.pi
    dA, dB, dC = PI / 2, PI / 3, PI / 7

    def beta(d):        # Бэрри (1-й порядок голономии, 2-й член разложения)
        return d**2 / 2

    def alpha(d, k=22):  # торможение (k = b2(K3) = 22)
        return d**5 / k

    bC, aC = beta(dC), alpha(dC)
    bB, aB = beta(dB), alpha(dB)
    bA, aA = beta(dA), alpha(dA)
    vals = {
        "delta_A": dA, "delta_B": dB, "delta_C": dC,
        "bC_berry_pi7": bC, "aC_braking_pi7": aC,
        "bB_berry_pi3": bB, "aB_braking_pi3": aB,
        "bA_berry_pi2": bA, "aA_braking_pi2": aA,
    }
    out = {"functions": {"beta": "d^2/2", "alpha": "d^5/22, k=b2(K3)=22"},
           "values": {k_: float(sp.N(v_, 20)) for k_, v_ in vals.items()},
           "values_exact": {k_: sstr(v_) for k_, v_ in vals.items()}}
    # кросс-чек: Delta_bC - lambda_D2 == bC; delta_eff == aC
    mono = os.path.join(BASE, "..", "docs", "monograph",
                        "verification_results_enhanced.json")
    if os.path.exists(mono):
        with open(mono, encoding="utf-8") as fh:
            m = json.load(fh)
        lamD2 = sp.Rational(3338, 1000)
        chk1 = sp.simplify((sp.Float(m["Delta_bC"], 20) - sp.Float(m["lambda_1_D2"], 20)) - sp.N(bC, 20))
        chk2 = abs(float(m["delta_eff"]) - float(sp.N(aC, 20)))
        chk3 = abs(float(m["gamma"]) - float(sp.N(dC**4 / 22, 20)))
        out["repo_crosscheck"] = {
            "Delta_bC_minus_lambdaD2_equals_bC": bool(abs(float(chk1)) < 1e-9),
            "delta_eff_equals_aC_absdiff": chk2,
            "gamma_equals_dC4_over_22_absdiff": chk3,
            "status": "OK" if (abs(float(chk1)) < 1e-9 and chk2 < 1e-9 and chk3 < 1e-9) else "MISMATCH",
        }
        log(f"    кросс-чек монографии: {out['repo_crosscheck']['status']} "
            f"(bC = π²/98 = {float(sp.N(bC, 12)):.9f}, aC = {float(sp.N(aC, 12)):.9f}, "
            f"aB = {float(sp.N(aB, 12)):.9f})")
    return out, dict(bC=bC, aC=aC, bB=bB, aB=aB, bA=bA, aA=aA)


# ------------------------------------------------------------------------------
# [S1] Двери: символьные kappa по каналам + цепочка + связка кольца + ветви
# ------------------------------------------------------------------------------
C2_OLD = "sp.Rational(1, 2) * KAPPA_S * r_e * t_e**2"
TH_OLD = "sp.Rational(1, 2) * KAPPA_S * s_e * t_e"
C1_OLD = "sp.Rational(1, 2) * KAPPA_S * r_e * s_e**2"
KDEF_OLD = "KAPPA_S = sp.Integer(2)"


def load_patched(kc1, kc2, kth):
    """Пересборка sympy_center_o6 с поканальными kappa + импорт p4."""
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


def s1_doors_symbolic():
    log("[S1] Двери: символьная система с kappa_C1, kappa_C2, kappa_TH...")
    t0 = time.time()
    K1, K2, KT = sp.symbols("K1 K2 KT", real=True)
    mod, p4 = load_patched(K1, K2, KT)
    zc = p4.build_z_coefficients()
    ok = {k: v for k, v in zc.items() if v.get("status") == "ok"}
    # карта каналов
    chan = {}
    for k, v in ok.items():
        n = v["num"]
        ch = ([["C1"] if n.has(K1) else [], ["C2"] if n.has(K2) else [],
               ["TH"] if n.has(KT) else []])
        tags = []
        if n.has(K1):
            tags.append("C1")
        if n.has(K2):
            tags.append("C2")
        if n.has(KT):
            tags.append("TH")
        chan[k] = "+".join(tags) if tags else "-"
    leaks = [k for k in ok
             if k.split("_")[0] in ("SC", "UV", "Mdef")
             and (ok[k]["num"].has(K1) or ok[k]["num"].has(K2) or ok[k]["num"].has(KT))]
    log(f"    z-система ({time.time()-t0:.0f} c): {len(ok)} коэффициентов; "
        f"kappa-утечки в SC/UV/Mdef: {leaks or 'НЕТ'}")

    eqs = p4.equations_from(zc, p4.ZERO_ALL_FLOWS)
    log(f"    уравнений (все потоки = 0): {len(eqs)}: {sorted(eqs)}")

    T0h, P2h, D0h, R1h = p4.T0h, p4.P2h, p4.D0h, p4.R1h
    W2h, R3h, P4h, R5h, M5h = p4.W2h, p4.R3h, p4.P4h, p4.R5h, p4.M5h

    # --- цепочка (тот же порядок, что frozen_chain; без assert'ов) ---
    subs = []

    def solv(key, tgt):
        e = sp.simplify(sp.expand(eqs[key].subs(subs)))
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
    log("    цепочка (символьно в K2, KT):")
    for k_, v_ in chain.items():
        log(f"      {k_} = {sstr(v_)}")
    # контроль: при K2=KT=2 цепочка должна совпасть с сохранённой (p4 JSON)
    sub_base = {K1: 2, K2: 2, KT: 2}
    stored = {"R3h": "2*R1h*T0h**2/9", "W2h": "4*T0h**2/3",
              "P2h": "T0h/3"}
    loc = {n: sp.Symbol(n) for n in ("T0h", "R1h")}
    match = []
    for k_, s_ in stored.items():
        d_ = sp.simplify(sp.expand(
            chain[k_].subs(sub_base) - sp.sympify(s_, locals=loc)))
        match.append(bool(d_ == 0))
    log(f"    совпадение с сохранённой цепочкой при kappa=2: {sum(match)}/3")

    # --- СТРУКТУРНАЯ СВЯЗКА: невязки C1_xi* в точке цепочки ---------------
    res_at_point = {}
    for key in sorted(eqs):
        e = sp.simplify(sp.expand(eqs[key].subs(subs)))
        res_at_point[key] = sp.factor(sp.cancel(e))
    c1_facts = {}
    for key in ("C1_xi1", "C1_xi2", "C1_xi3"):
        f_ = res_at_point[key]
        cofactor = None
        if f_.has(K1) and sp.simplify(f_.subs(K1, K2)) == 0 and f_.has(K2):
            cof_ = sp.simplify(sp.cancel(f_ / (K1 - K2)))
            cofactor = sstr(cof_) if cof_ != 0 else None
        c1_facts[key] = {
            "expr": sstr(f_),
            "vanishes_at_K1_eq_K2":
                bool(sp.simplify(f_.subs(K1, K2)) == 0),
            "cofactor_over_K1_minus_K2": cofactor,
        }
        log(f"    {key}: vanishes at K1=K2: {c1_facts[key]['vanishes_at_K1_eq_K2']}")
    # условие существования CSS-точки: все 12 уравнений в точке = 0
    nonzero_keys = [k_ for k_, v_ in res_at_point.items()
                    if sp.simplify(v_.subs({K1: K2})) != 0]
    log(f"    уравнения, НЕ обращающиеся в 0 при K1=K2 (произвольно K2,KT): "
        f"{nonzero_keys or 'НЕТ — точка существует структурно'}")

    # --- ветви tau и резольвента ------------------------------------------
    sub_g = list(subs) + [(R1h, 1)]
    branches = {}
    for key in ("UV_xi3", "Mdef_xi5"):
        g = sp.simplify(sp.expand(eqs[key].subs(sub_g)))
        gp = sp.Poly(sp.together(g).as_numer_denom()[0], T0h)
        branches[key] = gp.as_expr()
        log(f"    {key}(T0h; K2, KT) = {sstr(gp.as_expr())}")
    # проверка при kappa=2
    b_uv2 = sp.expand(branches["UV_xi3"].subs(sub_base))
    b_md2 = sp.expand(branches["Mdef_xi5"].subs(sub_base))
    base_ok = bool(sp.simplify(b_uv2 / (-16 * T0h**2 * (4 * T0h**2 - 27)) - 1) == 0
                   if b_uv2 != 0 else False)
    # резольвента: условие на (K2, KT) существования общего корня
    t_res = time.time()
    resol = sp.resultant(sp.together(branches["UV_xi3"]).as_numer_denom()[0],
                         sp.together(branches["Mdef_xi5"]).as_numer_denom()[0],
                         T0h)
    resol = sp.factor(sp.cancel(resol))
    log(f"    резольвента (общий корень) = {sstr(resol)} "
        f"[{time.time()-t_res:.0f} c]")
    # НОД двух ветвей в Q(K2, KT)
    g_uv = sp.Poly(sp.together(branches["UV_xi3"]).as_numer_denom()[0], T0h)
    g_md = sp.Poly(sp.together(branches["Mdef_xi5"]).as_numer_denom()[0], T0h)
    try:
        gcdp = sp.gcd(g_uv, g_md)
        gcd_expr = gcdp.as_expr()
    except Exception as ex:  # noqa: BLE001
        gcd_expr, gcdp = None, None
        log(f"    gcd не удался: {ex}")
    log(f"    НОД ветвей в T0h: {sstr(gcd_expr) if gcd_expr is not None else '—'}")

    out = {
        "channel_map": chan,
        "kappa_leaks_in_geometry": leaks,
        "n_equations": len(eqs),
        "chain_symbolic": {k_: sstr(v_) for k_, v_ in chain.items()},
        "chain_matches_stored_at_kappa2": sum(match),
        "c1_ring_consistency": c1_facts,
        "nonzero_equations_at_K1_eq_K2": nonzero_keys,
        "branch_UV_xi3": sstr(branches["UV_xi3"]),
        "branch_Mdef_xi5": sstr(branches["Mdef_xi5"]),
        "branch_check_at_kappa2_is_neg16T2_4T2_27": base_ok,
        "resultant_UV3_Mdef5": sstr(resol),
        "gcd_UV3_Mdef5": sstr(gcd_expr) if gcd_expr is not None else None,
        "runtime_s": time.time() - t0,
    }
    payload = {"eqs": eqs, "subs": subs, "chain": chain, "res": res_at_point,
               "branches": branches, "resol": resol, "K": (K1, K2, KT),
               "p4": p4, "gcd": gcd_expr, "zc": zc}
    return out, payload


# ------------------------------------------------------------------------------
# [S2] Исправленные башни: семейство tau*(kappa) = 27/(2*kappa) + схемы
# ------------------------------------------------------------------------------
def s2_schemes(payload, corr):
    log("[S2] Исправленные башни по схемам встраивания...")
    K1, K2, KT = payload["K"]
    T0h, R1h = payload["p4"].T0h, payload["p4"].R1h
    eqs, subs, chain = payload["eqs"], payload["subs"], payload["chain"]
    bC, aC, bB, aB = corr["bC"], corr["aC"], corr["bB"], corr["aB"]

    # --- (a) СТРУКТУРА СЕМЕЙСТВА: корни ветвей как формулы ----------------
    # UV_xi3   = -2 T0h^2 (8 K2^2 T0h^2 - 93 K2 - 15 KT)  ->  T0h^2 = (93 K2 + 15 KT)/(8 K2^2)
    # Mdef_xi5 = -2 T0h^2 (4 K2^2 T0h^2 - 39 K2 - 15 KT)  ->  T0h^2 = (39 K2 + 15 KT)/(4 K2^2)
    t0sq_uv = (93 * K2 + 15 * KT) / (8 * K2**2)
    t0sq_md = (39 * K2 + 15 * KT) / (4 * K2**2)
    # машинная проверка формул подстановкой в ветви
    bs_uv = payload["branches"]["UV_xi3"]
    bs_md = payload["branches"]["Mdef_xi5"]
    # подстановка корня: T0h^4 = t0sq^2
    chk_uv = sp.simplify(bs_uv.subs(T0h**4, t0sq_uv**2).subs(T0h**2, t0sq_uv))
    chk_md = sp.simplify(bs_md.subs(T0h**4, t0sq_md**2).subs(T0h**2, t0sq_md))
    # условие совпадения корней
    cond = sp.factor(sp.cancel(sp.simplify(t0sq_uv - t0sq_md)))
    log(f"    формулы корней: T0h^2(UV) = {sstr(t0sq_uv)}; "
        f"T0h^2(Mdef) = {sstr(t0sq_md)}")
    log(f"    проверка подстановкой в ветви: UV -> {chk_uv}, Mdef -> {chk_md}")
    log(f"    условие общего корня: T0h^2(UV) - T0h^2(Mdef) = {cond}")
    # равномерная связь: K2 = KT = kappa -> tau*(kappa) = 27/(2 kappa)
    fam = sp.simplify(t0sq_uv.subs(KT, K2))
    fam_check = bool(fam == 27 / (2 * K2))
    log(f"    равномерная связь K2=KT=kappa: T0h^2 = {sstr(fam)} "
        f"== 27/(2*kappa): {fam_check}")

    # --- (b) схемы: равномерная голономная перенормировка kappa ------------
    # (структурно допустимы только РАВНОМЕРНЫЕ схемы — связка [S1])
    schemes = {
        "S0_baseline": sp.Integer(2),
        "H_mono_(1+bC-aC)_screening_off": 2 * (1 + bC - aC),
        "H_screen_(1-bC+aC)": 2 * (1 - bC + aC),
        "H_brakes_(1-aC-aB)": 2 * (1 - aC - aB),
        "H_brakeC_only_(1-aC)": 2 * (1 - aC),
        "H_berry_only_(1+bC)": 2 * (1 + bC),
        "H_brakeB_only_(1-aB)": 2 * (1 - aB),
        "H_berry_half_down_(1-bC/2)": 2 * (1 - bC / 2),
        "H_berry_half_brakes_(1-bC/2-aC-aB)": 2 * (1 - bC / 2 - aC - aB),
        "H_berry_half_brakeC_(1-bC/2-aC)": 2 * (1 - bC / 2 - aC),
    }

    # якоря кампании (без подгонки)
    DELTA_SP = 7 * sp.pi / 30
    GAMMA_LIT = sp.Rational(374, 1000)
    B_CH = 1 - sp.cos(2 * sp.pi / 7)
    kap_glit = sp.N(DELTA_SP / GAMMA_LIT, 25)     # 1.9599954...
    kap_bch = sp.N(DELTA_SP / B_CH, 25)           # 1.9469281...
    kap_req_glit = sp.N(27 / (2 * sp.exp(kap_glit)), 25)  # kappa, дающий ln tau* = kappa_obs
    kap_req_bch = sp.N(27 / (2 * sp.exp(kap_bch)), 25)
    log(f"    требуемая связь для замыкания книги: kappa_req(glit) = "
        f"{float(kap_req_glit):.6f}, kappa_req(b_Ch) = {float(kap_req_bch):.6f}")

    prec = 30
    out = {"family": {
        "T0h2_UV_formula": sstr(t0sq_uv),
        "T0h2_Mdef_formula": sstr(t0sq_md),
        "common_root_condition": sstr(cond),
        "uniform_family_tau_star": sstr(fam),
        "uniform_family_is_27_over_2kappa": fam_check,
        "residual_checks_UV_Mdef": [sstr(chk_uv), sstr(chk_md)],
        "kappa_required_for_book_closure": {
            "gamma_lit": float(kap_req_glit), "b_Ch": float(kap_req_bch)},
    }}
    for name, kv in schemes.items():
        t0 = time.time()
        kvn = sp.N(kv, prec)
        rec = {"kappa_uniform": float(sp.N(kv, 12)),
               "kappa_exact": sstr(kv)}
        tausq = sp.N(fam.subs(K2, kvn), prec)
        t0v = sp.sqrt(tausq)
        rec["tau_star_corrected"] = float(tausq)
        rec["ln_tau_star"] = float(sp.N(sp.log(tausq), 20))
        # численная верификация ветвей и всех 12 невязок в полной точке
        subv = {K1: kvn, K2: kvn, KT: kvn}
        point = {T0h: t0v, R1h: sp.Integer(1)}
        point.update({amp: sp.N(chain[k_].subs(subv).subs(T0h, t0v).subs(R1h, 1), prec)
                      for k_, amp in (("D0h", payload["p4"].D0h),
                                      ("R3h", payload["p4"].R3h),
                                      ("W2h", payload["p4"].W2h),
                                      ("P2h", payload["p4"].P2h),
                                      ("R5h", payload["p4"].R5h),
                                      ("M5h", payload["p4"].M5h),
                                      ("P4h", payload["p4"].P4h))})
        max_res = 0.0
        for e_ in eqs.values():
            rv = sp.N(e_.subs(subv).subs(point), 20)
            max_res = max(max_res, abs(complex(rv)))
        rec["max_residual_at_point"] = max_res
        rec["point_exists"] = bool(max_res < 1e-12)
        rec["ring_W2_over_T0h2"] = float(sp.N(point[payload["p4"].W2h] / tausq, 12))
        rec["clock_P2_over_T0h"] = float(sp.N(point[payload["p4"].P2h] / t0v, 12))
        rec["M5h"] = float(sp.N(point[payload["p4"].M5h], 12))
        kt_book = sp.log(tausq)
        rec["kappa_book_ln_tau"] = float(sp.N(kt_book, 15))
        rec["dev_vs_kappa_obs_gamma_lit_pct"] = float(sp.N(100 * (kt_book - kap_glit) / kap_glit, 8))
        rec["dev_vs_kappa_obs_b_Ch_pct"] = float(sp.N(100 * (kt_book - kap_bch) / kap_bch, 8))
        rec["delta_ln_vs_baseline_pct"] = float(sp.N(100 * (kt_book - sp.log(sp.Rational(27, 4))) / sp.log(sp.Rational(27, 4)), 8))
        rec["kappa_dev_vs_required_glit_pct"] = float(sp.N(100 * (kvn - kap_req_glit) / kap_req_glit, 8))
        log(f"    {name}: kappa={rec['kappa_uniform']:.6f}, tau*={rec['tau_star_corrected']:.6f}, "
            f"book={rec['kappa_book_ln_tau']:.6f} ({rec['dev_vs_kappa_obs_gamma_lit_pct']:+.2f}%), "
            f"res={max_res:.1e} [{time.time()-t0:.1f} c]")
        out[name] = rec

    # --- (c) демонстрация нарушения: НЕравномерная схема -------------------
    viol = {"scheme": "aB in C1 only: (k1,k2,kT) = (2(1-aB), 2, 2)",
            "kappa": {"C1": float(sp.N(2 * (1 - aB), 12)), "C2": 2.0, "TH": 2.0}}
    kv1, kv2 = sp.N(2 * (1 - aB), prec), sp.N(2, prec)
    # корень UV-ветви при (K2, KT) = (2, 2): tau = 27/4; C1-невязка в этой точке
    t0v = sp.sqrt(sp.N(sp.Rational(27, 4), prec))
    subv = {K1: kv1, K2: kv2, KT: kv2}
    point = {T0h: t0v, R1h: sp.Integer(1)}
    point.update({amp: sp.N(chain[k_].subs({K2: kv2, KT: kv2}).subs(T0h, t0v).subs(R1h, 1), prec)
                  for k_, amp in (("D0h", payload["p4"].D0h),
                                  ("R3h", payload["p4"].R3h),
                                  ("W2h", payload["p4"].W2h),
                                  ("P2h", payload["p4"].P2h),
                                  ("R5h", payload["p4"].R5h),
                                  ("M5h", payload["p4"].M5h),
                                  ("P4h", payload["p4"].P4h))})
    c1res = sp.N(eqs["C1_xi1"].subs(subv).subs(point), 20)
    viol["C1_xi1_residual_at_uncorrected_point"] = float(abs(complex(c1res)))
    # расщепление ветвей
    viol["tau_UV"] = float(sp.N(t0sq_uv.subs(subv), 15))
    viol["tau_Mdef"] = float(sp.N(t0sq_md.subs(subv), 15))
    viol["branch_split"] = float(abs(sp.N(t0sq_uv.subs(subv), 20)
                                     - sp.N(t0sq_md.subs(subv), 20)))
    viol["verdict"] = ("асимметричное встраивание (a-B только в C1): C1-невязка "
                       "ненулевая, ветви расходятся — точка умирает; "
                       "поправка обязана быть равномерной по трём каналам")
    out["violation_demo"] = viol
    log(f"    {viol['scheme']}: C1-невязка = {viol['C1_xi1_residual_at_uncorrected_point']:.4f}, "
        f"расщепление ветвей = {viol['branch_split']:.6f}")
    return out


# ------------------------------------------------------------------------------
# [S3] Тесты замыкания на pi/30
# ------------------------------------------------------------------------------
def s3_closure(schemes_out, corr):
    log("[S3] Тесты замыкания на pi/30...")
    bC, aC, bB, aB = corr["bC"], corr["aC"], corr["bB"], corr["aB"]
    DELTA_SP = 7 * sp.pi / 30
    GAMMA_LIT = sp.Rational(374, 1000)
    B_CH = 1 - sp.cos(2 * sp.pi / 7)
    kap_glit = sp.N(DELTA_SP / GAMMA_LIT, 25)
    kap_bch = sp.N(DELTA_SP / B_CH, 25)
    out = {"anchors": {"Delta_sp": "7*pi/30", "kappa_obs_gamma_lit": float(kap_glit),
                       "kappa_obs_b_Ch": float(kap_bch)}}

    # (a) СКАН СЕМЕЙСТВА: x = комбо поправок -> kappa = 2(1+x) ->
    #     tau* = 27/(2 kappa) -> книга ln tau* против якорей.
    #     Помечено как скан (multiple testing); принципиальные схемы
    #     H_mono/H_screen/H_brakes входят в S2 отдельно.
    scan = []
    base_book = sp.log(sp.Rational(27, 4))
    for s1 in (-1, 0, 1):
        for s2 in (-1, 0, 1):
            for s3 in (-1, 0, 1):
                for s4_ in (-1, 0, 1):
                    x = s1 * bC + s2 * aC + s3 * bB + s4_ * aB
                    if x == 0 and (s1 or s2 or s3 or s4_):
                        continue
                    kap = 2 * (1 + x)
                    if kap <= 0:
                        continue
                    book = sp.log(27 / (2 * kap))
                    d1 = float(sp.N(100 * (book - kap_glit) / kap_glit, 8))
                    d2 = float(sp.N(100 * (book - kap_bch) / kap_bch, 8))
                    scan.append({
                        "combo": (f"{s1:+d}*bC {s2:+d}*aC {s3:+d}*bB {s4_:+d}*aB"),
                        "x": float(sp.N(x, 12)),
                        "kappa_corr": float(sp.N(kap, 12)),
                        "tau_star": float(sp.N(27 / (2 * kap), 12)),
                        "book": float(sp.N(book, 15)),
                        "dev_gamma_lit_pct": d1, "dev_b_Ch_pct": d2})
    scan.sort(key=lambda r_: min(abs(r_["dev_gamma_lit_pct"]), abs(r_["dev_b_Ch_pct"])))
    out["family_scan_book_vs_anchors"] = {
        "note": ("СКАЧ знаковых комбинаций поправок в равномерной связи "
                 "kappa = 2(1+x) (multiple testing!): не доказательство, "
                 "а таблица расстояний; база без поправок: dev %.2f%% / %.2f%%; "
                 "принципиальные схемы (H_mono: +bC-aC, H_screen: -bC+aC, "
                 "H_brakes: -aC-aB) см. S2"
                 % (float(sp.N(100 * (base_book - kap_glit) / kap_glit, 8)),
                    float(sp.N(100 * (base_book - kap_bch) / kap_bch, 8)))),
        "top6": scan[:6]}

    # (b) nsimplify tau*_corr по принципиальным схемам
    ns = {}
    for name, rec in schemes_out.items():
        if name in ("family", "violation_demo") or "tau_star_corrected" not in rec:
            continue
        tv = rec["tau_star_corrected"]
        tvf = sp.Float(tv, 25)
        cands = {}
        for atoms_ in ([sp.pi, sp.sqrt(3)],
                       [sp.pi, sp.sqrt(3), sp.sqrt(7)],
                       [sp.pi, sp.sqrt(2), sp.sqrt(3)]):
            try:
                r_ = sp.nsimplify(tvf, atoms_, full=False, tolerance=sp.Float("1e-9", 25))
                if r_ != 0:
                    cands[sstr(sorted(atoms_, key=str))] = sstr(r_)
            except Exception:  # noqa: BLE001
                pass
        ns[name] = {"tau": tv, "nsimplify": cands,
                    "tau_over_27_4": float(sp.N(tvf / sp.Rational(27, 4), 15)),
                    "tau_minus_27_4": float(sp.N(tvf - sp.Rational(27, 4), 15)),
                    "ln_tau_dev_glit_pct": rec.get("dev_vs_kappa_obs_gamma_lit_pct")}
    out["nsimplify_tau_corrected"] = ns

    # (c) лестница k*pi/30: эхо и квант — якоря замыкания
    ladder = {}
    for k in range(1, 16):
        ladder[f"{k}*pi/30"] = float(sp.N(k * sp.pi / 30, 12))
    out["ladder_k_pi_over_30"] = ladder
    # (d) монодромия за эхо в исправленных точках (где есть lambda+ из S4 —
    #     см. verdict; здесь только структура mu = exp(lambda_plus * Delta))
    out["monodromy_note"] = ("монодромия за эхо mu = e^{lambda+ * Delta}; "
                             "Delta = 7*pi/30 (спинорная лестница) vs "
                             "Delta_lit = 0.737637 (GHS 1993), разрыв 0.63%")
    return out


# ------------------------------------------------------------------------------
# [S4] Карандаш в исправленной точке (QEP + sigma_min-фильтр фантомов)
# ------------------------------------------------------------------------------
def s4_pencil(payload, scheme_name, kappa_vals, tau_star):
    """Спектр карандаша M(lam) = Ja + lam*JvP в исправленной точке.

    Честный протокол сеанса 14, численная версия: G(lam) = M^T M -> QEP;
    корни QEP фильтруются sigma_min(M(lam0)) на C (фантомы отсеиваются).
    """
    log(f"[S4] Карандаш в исправленной точке ({scheme_name})...")
    t0 = time.time()
    K1, K2, KT = payload["K"]
    p4 = payload["p4"]
    k1v, k2v, ktv = kappa_vals
    # система с живыми первыми потоками (ZERO_ADIABATIC) + пролонгации
    eqs_live = [sp.expand(e_) for e_ in p4.equations_from(
        payload["zc"], p4.ZERO_ADIABATIC).values() if e_ != 0]
    flow_of = {p4.D0h: p4.dD0, p4.R3h: p4.dR3, p4.W2h: p4.dW2,
               p4.P2h: p4.Qh, p4.R5h: p4.dR5, p4.P4h: p4.dP4}
    prolong = []
    for amp, form in payload["subs"]:
        if amp not in flow_of:
            continue
        e_ = (sp.diff(form, p4.T0h) * p4.dT0
              + sp.diff(form, p4.R1h) * p4.dR1 - flow_of[amp])
        prolong.append(sp.expand(e_))
    F = eqs_live + prolong
    amps = [p4.T0h, p4.P2h, p4.D0h, p4.R1h, p4.W2h, p4.R3h, p4.P4h, p4.R5h, p4.M5h]
    flows = [p4.dT0, p4.dD0, p4.Qh, p4.dR1, p4.dW2, p4.dR3, p4.dP4, p4.dR5]
    log(f"    система: {len(eqs_live)} башенных + {len(prolong)} пролонг. = {len(F)} ур.")

    # исправленная точка
    subv = {K1: sp.N(k1v, 25), K2: sp.N(k2v, 25), KT: sp.N(ktv, 25)}
    chain = payload["chain"]
    tv = tau_star
    if tv is None:
        return {"status": "no_common_root"}
    t0v = sp.sqrt(sp.Float(tv, 25))
    point = {p4.T0h: t0v, p4.R1h: sp.Float(1, 25), p4.D0h: sp.Float(0, 25)}
    for k_ in ("R3h", "W2h", "P2h", "R5h", "M5h", "P4h"):
        point[{"R3h": p4.R3h, "W2h": p4.W2h, "P2h": p4.P2h,
               "R5h": p4.R5h, "M5h": p4.M5h, "P4h": p4.P4h}[k_]] = \
            sp.N(chain[k_].subs(subv).subs(p4.T0h, t0v).subs(p4.R1h, 1), 25)
    for f_ in flows:
        point[f_] = sp.Float(0, 25)
    # невязки в точке (все 12+6)
    resmax = 0.0
    for e_ in F:
        rv = sp.N(e_.subs(subv).subs(point), 20)
        resmax = max(resmax, abs(complex(rv)))
    log(f"    max |невязка| в точке: {resmax:.2e}")

    flow_amp_idx = {0: 0, 1: 2, 2: 1, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}
    Pproj = sp.zeros(len(flows), len(amps))
    for i_, j_ in flow_amp_idx.items():
        Pproj[i_, j_] = 1
    Ja = sp.Matrix(len(F), len(amps),
                   lambda i_, j_: sp.diff(F[i_], amps[j_]).subs(subv).subs(point))
    Jv = sp.Matrix(len(F), len(flows),
                   lambda i_, j_: sp.diff(F[i_], flows[j_]).subs(subv).subs(point))
    Ja_n = np.array(Ja.evalf(15).tolist(), dtype=complex)
    B_n = np.array((Jv * Pproj).evalf(15).tolist(), dtype=complex)
    # QEP: G(lam) = (Ja + lam B)^T (Ja + lam B) -> E0 + lam E1 + lam^2 E2
    # (протокол сеанса 14: G = M^T M; над C корни QEP шире рангового падения)
    E0 = Ja_n.conj().T @ Ja_n
    E1 = Ja_n.conj().T @ B_n + B_n.conj().T @ Ja_n
    E2 = B_n.conj().T @ B_n
    # компанион-линеаризация БЕЗ обращения E2 (E2 вырождена: B 18x9 ранга <= 8):
    # A0 z = lam A1 z, z = [x; lam x], A0 = [[E0, E1], [0, I]], A1 = [[0, -E2], [I, 0]]
    from scipy.linalg import eig as scipy_eig
    A0 = np.zeros((18, 18), dtype=complex)
    A1 = np.zeros((18, 18), dtype=complex)
    A0[:9, :9] = E0
    A0[:9, 9:] = E1
    A0[9:, 9:] = np.eye(9)
    A1[:9, 9:] = -E2
    A1[9:, :9] = np.eye(9)
    try:
        lams = scipy_eig(A0, A1, right=False)
    except Exception as ex:  # noqa: BLE001
        log(f"    QEP не удался: {ex}")
        lams = np.array([np.nan])
    lams = np.array([l_ for l_ in lams if np.isfinite(l_)])
    # sigma_min-фильтр (отсев фантомов det(M^T M))
    genuine, phantoms = [], []
    for lam0 in lams:
        if not np.isfinite(lam0):
            continue
        Mlam = Ja_n + lam0 * B_n
        sv = np.linalg.svd(Mlam, compute_uv=False)
        rel = float(sv[-1] / sv[0])
        rec = {"lambda": [float(np.real(lam0)), float(np.imag(lam0))],
               "rel_sigma_min": rel}
        if rel < 1e-8:
            genuine.append(rec)
        else:
            phantoms.append(rec)
    # лестница k*pi/30 против Im lambda фантомов
    ladder = [float(sp.N(k * sp.pi / 30, 15)) for k in range(1, 16)]
    hits = []
    for ph in phantoms:
        im = abs(ph["lambda"][1])
        if im < 1e-9:
            continue
        best = min(ladder, key=lambda L_: abs(L_ - im))
        rel = abs(best - im) / best
        hits.append({"lambda": ph["lambda"], "nearest_ladder": best,
                     "k_over_30": int(round(best / (sp.pi.evalf(15) / 30))),
                     "rel_diff_pct": 100 * rel,
                     "match_1pct": bool(rel < 0.01)})
    hits.sort(key=lambda h_: h_["rel_diff_pct"])
    out = {
        "scheme": scheme_name,
        "tau_star": tv,
        "max_residual_at_point": float(resmax),
        "n_QEP_roots": int(len(lams)),
        "genuine_modes": genuine,
        "n_phantoms": len(phantoms),
        "phantoms": phantoms,
        "phantom_Im_vs_ladder_top": hits[:8],
        "note": ("QEP-корни с rel sigma_min >= 1e-8 — фантомы (протокол "
                 "сеанса 14); сопоставление Im lambda с k*pi/30 — тест "
                 "связки фантомов со спинорной лестницей"),
        "runtime_s": time.time() - t0,
    }
    log(f"    подлинных мод: {len(genuine)}, фантомов: {len(phantoms)}; "
        f"лучший хит лестницы: {hits[0] if hits else '—'}")
    return out


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
def main() -> None:
    results = {"title": "Three spinor corrections (bC, aC, aB) in the towers",
               "question": ("does embedding the repo corrections as natural "
                            "coupling renormalizations correct the towers and "
                            "close on pi/30?")}
    s0, corr = s0_corrections()
    results["S0_corrections"] = s0

    s1, payload = s1_doors_symbolic()
    results["S1_doors"] = s1

    results["S2_schemes"] = s2_schemes(payload, corr)

    results["S3_closure"] = s3_closure(results["S2_schemes"], corr)

    # [S4] карандаш: базовая точка (контроль протокола) + принципиальные схемы
    K1, K2, KT = payload["K"]
    base = results["S2_schemes"]["S0_baseline"]
    results["S4_pencil_baseline"] = s4_pencil(
        payload, "S0_baseline", (2, 2, 2), base.get("tau_star_corrected"))
    for cand in ("H_mono_(1+bC-aC)_screening_off", "H_screen_(1-bC+aC)"):
        rec = results["S2_schemes"].get(cand, {})
        if rec.get("point_exists") and rec.get("tau_star_corrected"):
            kv = rec["kappa_uniform"]
            results[f"S4_pencil_{cand}"] = s4_pencil(
                payload, cand, (kv, kv, kv), rec["tau_star_corrected"])

    results["verdict"] = verdict(results)
    results["runtime_s"] = round(time.time() - T_START, 1)

    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2, default=str)
    log(f"\nГотово за {results['runtime_s']} c. Результат: {OUT_PATH}")
    log(f"ВЕРДИКТ: {results['verdict']}")


def verdict(results):
    """Сборка честного вердикта из машинных фактов."""
    s1 = results["S1_doors"]
    s2 = results["S2_schemes"]
    lines = []
    leak = s1["kappa_leaks_in_geometry"]
    lines.append(
        ("геометрия SC/UV/Mdef без kappa: утечек НЕТ — 'ошибки' в уравнениях нет"
         if not leak else f"kappa-утечки: {leak}"))
    cons = s1["c1_ring_consistency"]
    ok_cons = all(v["vanishes_at_K1_eq_K2"] for k, v in cons.items()
                  if k in ("C1_xi1", "C1_xi2", "C1_xi3"))
    lines.append(
        "структурная связка кольца: C1-невязки обнуляются ТОЛЬКО при "
        "kappa_C1 = kappa_C2 — голономная поправка обязана быть ДИАГОНАЛЬНОЙ "
        "(одной для обоих нулевых каналов); асимметричное встраивание убивает "
        "CSS-точку" if ok_cons else
        "связка C1=C2 НЕ подтвердилась — смотри c1_ring_consistency")
    alive = {k: v for k, v in s2.items() if v.get("point_exists")}
    dead = {k: v for k, v in s2.items() if not v.get("point_exists")}
    lines.append(f"схем с живой точкой: {len(alive)}/{len(s2)}; "
                 f"мертвые: {sorted(dead) or '—'}")
    best = None
    for k, v in alive.items():
        d = v.get("dev_vs_kappa_obs_gamma_lit_pct")
        if d is not None and (best is None or abs(d) < abs(best[1])):
            best = (k, d, v.get("tau_star_corrected"))
    if best:
        lines.append(f"лучшая книга: {best[0]}: ln(tau*) = ln({best[2]:.6f}), "
                     f"dev vs kappa_obs(gamma_lit) = {best[1]:+.2f}% "
                     f"(базовая ln(27/4): {s2['S0_baseline']['dev_vs_kappa_obs_gamma_lit_pct']:+.2f}%)")
    s4s = {k: v for k, v in results.items() if k.startswith("S4_pencil")}
    for k, v in s4s.items():
        hits = v.get("phantom_Im_vs_ladder_top") or []
        if hits:
            h0 = hits[0]
            lines.append(f"{k}: лучший хит фантомов к лестнице k*pi/30: "
                         f"Im lambda = {h0['lambda'][1]:.5f} ~ {h0['k_over_30']}*pi/30 "
                         f"({h0['rel_diff_pct']:.2f}%)")
        else:
            lines.append(f"{k}: хитов фантомов к лестнице нет")
    return lines


if __name__ == "__main__":
    main()

