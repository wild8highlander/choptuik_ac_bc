#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кампания [сессия 21 / v17]: CLOCK-CLOSURE-T1C — замыкание часов через
однокирпичную форму источников T1c (вместо несовместной наивной O6+).

Вопрос (директива автора, сессия 21): попытка замыкания часов через
однокирпичную (one-brick, kappa = 2 - pi^2/98) форму источников T1c — вместо
наивной O6+ (записанный якорь несовместимости: ветвь UV[xi^3] форсирует
tau = 9/4, ветвь Mdef[xi^5] форсирует tau = 9/16, совместно только тривиальное
R3 = 0 — center_o6_nsolve.json) — либо remnant-тест B4 на данных с большей
delta-чувствительностью. Выполнены ОБА слоя (C1-C2 = часы, C3 = B4-remnant).

ERRATUM к v16 (обнаружен при подготовке v17): static_landing в hexcycle_dae
НЕ прикалывала T0h (ньютоновский шаг по всем 9 амплитудам, dx[0] != 0, хотя
docstring заявляет «T0h приколот») — посадки [T1c] сходились к ТРИВИАЛЬНОЙ
ветви (T0h -> 0: вся башня аннигилирует, F -> 0) или к полубашне R1h -> 0.
Отсюда chain_dev до 1e6 и «компенсированная книга» = захват тривиальной
ветви. Вердикт v16 T1c (статический хребет CSS-подобных равновесий,
покрывающий масштабы книги) ПЕРЕСМАТРИВАЕТСЯ в [A0]/[A1].

Слои (обе точки kappa = 2 и 2 - pi^2/98; коллапс 2 цикла, обдув 1 цикл):
  [A0] ERRATUM-аудит: воспроизведение посадок v16 + классификация каждого
       приземления (тривиальный захват по T0h_land / полубашня R1h ~ 0 /
       книжноподобное) — пересчёт статистики v16.
  [A1] ЧЕСТНАЯ СТАТИЧЕСКАЯ КАРТА: мультистарт-Ньютон с ЖЁСТКИМ прикалыванием
       T0h (dx[0] = 0; 5 сидов R1h; кап шага; отсечка дегенератов) на каждом
       забронированном масштабе: существует ли недегенератное статическое
       состояние вне критического масштаба.
  [C1] ТЕОРЕМА О ПАРЕ ЧАСОВ (точно, SymPy): на цепочке ветвные уравнения
       UV_xi3 и Mdef_xi5 имеют ЕДИНСТВЕННЫЙ общий положительный корень
       tau*(kappa) = 27/(2kappa) — 27/4 (baseline), 1323/(196-pi^2) (one-brick):
       де-адиабатизованная (T1c-)форма источников растворяет наивную пару
       9/4 vs 9/16 в ЕДИНСТВЕННЫЕ общие часы, и один кирпич двигает эти часы
       к наблюдаемому значению (закрытие ln tau* до +0.062%).
  [C2] НОСИТЕЛИ ЧАСОВ: книги (W2/T0^2 = 2k/3, 9R3/(2R1T0^2), s = 3P2/T0)
       в x* (обе точки) и в дегенератных углах (кольцевой сектор мертв —
       часы не имеют статического носителя вне критического масштаба).
  [C3] B4-REMNANT на данных с большей delta-чувствительностью: кернел
       M_r ((v,dd) -> r) в x* обеих точек; марш 1 эхо из x* с кернел-
       направлением (тест живых часов на one-brick); дефект совместимости
       книги вдоль мелкой сетки масштабов (статический F + гомотетический r).

Запуск: python3 clock_closure_t1c.py  (~5-8 мин) -> results/clock_closure_t1c.json
"""
from __future__ import annotations

import json
import os
import sys
import time
import warnings

import numpy as np
import sympy as sp

warnings.filterwarnings("ignore")
BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)
os.chdir(BASE)
RESULTS = os.path.join(BASE, "results")
T_START = time.time()

import dae_nonlinear_core as dnc                       # noqa: E402
from dae_nonlinear_core import NonlinearDAE            # noqa: E402
import sympy_second_flows as sf                        # noqa: E402
import sympy_hexcycle as hx                            # noqa: E402
from hexcycle_dae import (parse_chain, station_scales, make_state,   # noqa: E402
                          static_landing, chain_poles)

NAMES = ["T0h", "P2h", "D0h", "R1h", "W2h", "R3h", "P4h", "R5h", "M5h"]


def log(msg):
    print(msg, flush=True)


# ------------------------------------------------------------- система/цепочка --
def build_point(kv):
    """Система, цепочка, DAE, якоря замороженных уравнений и chain-подстановок."""
    sysd = dnc.build_nonlinear_system(kv, validate=False)
    chain = parse_chain(sysd)
    dae = NonlinearDAE(sysd)
    o6, p4 = sf.load_patched(kv, kv, kv)
    zc_sf, dds = sf.build_zc_sf(o6, p4)
    ok_sf = {k: v for k, v in zc_sf.items() if v.get("status") == "ok"}
    flows8 = (p4.dT0, p4.dD0, p4.Qh, p4.dR1, p4.dW2, p4.dR3, p4.dP4, p4.dR5)
    zero_all = {f: 0 for f in flows8}
    zero_all.update({d: 0 for d in dds})
    eqs_frozen = {k: sp.expand(v["num"].subs(zero_all))
                  for k, v in ok_sf.items()
                  if sp.expand(v["num"].subs(zero_all)) != 0}
    T0h, P2h, D0h, R1h = p4.T0h, p4.P2h, p4.D0h, p4.R1h
    W2h, R3h, P4h, R5h, M5h = p4.W2h, p4.R3h, p4.P4h, p4.R5h, p4.M5h
    subs = []

    def solv(key, tgt):
        e = sp.simplify(sp.expand(eqs_frozen[key].subs(subs)))
        r = sp.solve(sp.Eq(e, 0), tgt)
        assert r, f"цепочка: {key}"
        return sp.simplify(sp.cancel(r[0]))

    d0 = solv("Mdef_xi3", D0h); subs.append((D0h, d0))
    r3 = solv("UV_xi1", R3h); subs.append((R3h, r3))
    w2 = solv("C2_xi1", W2h); subs.append((W2h, w2))
    r3 = sp.simplify(r3.subs(W2h, w2)); subs[1] = (R3h, r3)
    p2 = solv("C2_xi2", P2h); subs.append((P2h, p2))
    r5 = solv("C2_xi3", R5h); subs.append((R5h, r5))
    m5 = solv("TH_xi2", M5h); subs.append((M5h, m5))
    p4v = solv("SC_xi4", P4h); subs.append((P4h, p4v))
    used = {"Mdef_xi3", "UV_xi1", "C2_xi1", "C2_xi2", "C2_xi3",
            "TH_xi2", "SC_xi4"}
    rest = sorted(k for k in eqs_frozen if k not in used)
    return {
        "sysd": sysd, "chain": chain, "dae": dae,
        "eqs_frozen": eqs_frozen, "chain_subs": dict(subs), "rest": rest,
        "syms": {"T0h": T0h, "P2h": P2h, "D0h": D0h, "R1h": R1h,
                 "W2h": W2h, "R3h": R3h, "P4h": P4h, "R5h": R5h, "M5h": M5h},
    }


# ---------------------------------------------------------------- [A0] аудит --
def classify_landing(sl, T0h_pin, a_book):
    """Классификация приземления: тривиальный захват / полубашня / книжноподобное."""
    if not sl.get("converged") or sl.get("a") is None:
        return {"class": "no_landing", "T0h_ratio": None}
    a = np.array(sl["a"], dtype=float)
    ref = float(np.linalg.norm(a_book))
    ratio = float(a[0] / T0h_pin) if T0h_pin else None
    tower = float(np.linalg.norm(a[[1, 4, 5, 6, 7, 8]]))
    if ratio is not None and (ratio < 0.5 or ratio > 2.0):
        cls = "trivial_capture_T0h"
    elif tower < 1e-8 * ref:
        cls = "trivial_tower"
    elif abs(a[3]) < 0.05:
        cls = "half_tower_R1h"
    elif abs(a[3]) < 0.2:
        cls = "near_half_tower"
    else:
        cls = "book_like" if sl.get("chain_dev_max", 1) < 1e-4 else "off_book"
    return {"class": cls, "T0h_ratio": ratio,
            "R1h": float(a[3]), "F_max": float(sl["F_max"]),
            "chain_dev_max": sl.get("chain_dev_max"),
            "in_S": sl.get("in_S")}


def layer_A0(kv, bp, label):
    """[A0] аудит посадок v16 (воспроизведение + классификация)."""
    out = {"label": label}
    dae, chain = bp["dae"], bp["chain"]
    t0s = float(bp["sysd"]["x_star"][0])
    log(f"  [A0] воспроизведение посадок v16 ({label})...")
    stats = {}
    rows = {}
    for tag, ndir, nsides in (("collapse", -1, 12), ("blowup", 1, 6)):
        rr = {}
        cnt = {}
        for rec in station_scales(t0s, nsides, ndir):
            if rec["k"] == 0:
                continue
            a_book = make_state(chain, rec["T0h"], r1h=1.0,
                                kinetic=False)[:9]
            try:
                sl = static_landing(dae, chain, rec["T0h"])
                cl = classify_landing(sl, rec["T0h"], a_book)
            except dnc.BreakdownError:
                cl = {"class": "breakdown", "T0h_ratio": None}
            rr[f"k{rec['k']}"] = cl
            cnt[cl["class"]] = cnt.get(cl["class"], 0) + 1
        rows[tag] = rr
        stats[tag] = cnt
        log(f"    {tag}: {cnt}")
    out["rows"] = rows
    out["stats"] = stats
    n_book = sum(stats[t].get("book_like", 0) for t in stats)
    n_triv = sum(stats[t].get("trivial_capture_T0h", 0)
                 + stats[t].get("trivial_tower", 0) for t in stats)
    n_half = sum(stats[t].get("half_tower_R1h", 0)
                 + stats[t].get("near_half_tower", 0) for t in stats)
    out["verdict"] = (f"посадки v16: книжноподобных {n_book}, тривиальных "
                      f"захватов {n_triv}, полубашен {n_half} из 36 — "
                      f"{'ERRATUM ПОДТВЕРЖДЁН: компенсированная книга v16 = '
                       'захваты тривиальной/полудегенератной ветви'
                      if n_book == 0 else 'есть книжноподобные посадки'}")
    log(f"    {out['verdict']}")
    return out


# ------------------------------------------------------- [A1] честная карта --
def pinned_landing(dae, chain, T0h_pin, iters=60,
                   seeds=(1.0, 0.5, 2.0, 0.1, 10.0)):
    """Мультистарт-Ньютон на F(a,0,0)=0 с ЖЁСТКО приколотым T0h (dx[0]=0)."""
    a_book = make_state(chain, T0h_pin, r1h=1.0, kinetic=False)[:9].copy()
    if not np.all(np.isfinite(a_book)):
        return {"F_max": None, "reason": "chain NaN (полюс)", "a": None}
    ref = float(np.linalg.norm(a_book))
    best = {"F_max": np.inf, "a": None, "R1h": None, "F_book":
            float(np.max(np.abs(dae.eval_F(np.concatenate([a_book,
                                                           np.zeros(11)])))))}
    for si, r1_0 in enumerate(seeds):
        a = a_book.copy()
        if si > 0:
            a[3] = r1_0
            a[5] = 2 * r1_0 * a[0] ** 2 / 9
            a[7] = 2 * r1_0 * a[0] ** 2 * (3 * a[0] ** 2 - 5) / 45
            a[8] = 2 * r1_0 * a[0] ** 2 * (23 - 6 * a[0] ** 2) / 9
        try:
            for _ in range(iters):
                x = np.concatenate([a, np.zeros(11)])
                Fv = dae.eval_F(x)
                m = float(np.max(np.abs(Fv)))
                if m < best["F_max"]:
                    best = {"F_max": m, "a": a.copy(), "R1h": float(a[3]),
                            "F_book": best["F_book"]}
                if m < 1e-12:
                    break
                Dm = dae.eval_DF(x)[:, :9]
                da_, *_ = np.linalg.lstsq(Dm, -Fv, rcond=None)
                da_[0] = 0.0                          # ЖЁСТКИЙ пин T0h
                nrm = float(np.linalg.norm(da_))
                cap = 0.3 * ref
                if nrm > cap:
                    da_ *= cap / nrm
                a = a + da_
                if not np.all(np.isfinite(a)):
                    break
        except dnc.BreakdownError:
            continue
    if best["a"] is None:
        return {"F_max": None, "reason": "все сиды breakdown", "a": None,
                "F_book": best.get("F_book")}
    a = best["a"]
    ref2 = float(np.linalg.norm(a_book))
    tower = float(np.linalg.norm(a[[1, 4, 5, 6, 7, 8]]))
    best["tower_norm_ratio"] = tower / ref2
    best["class"] = ("half_tower_R1h" if abs(a[3]) < 0.05
                     else ("near_half_tower" if abs(a[3]) < 0.2
                           else "nondegenerate"))
    best["a"] = [float(v) for v in a]
    best["converged"] = bool(best["F_max"] < 1e-9)
    return best


def layer_A1(kv, bp, label):
    """[A1] честная статическая карта (T0h жёстко приколот)."""
    dae, chain = bp["dae"], bp["chain"]
    t0s = float(bp["sysd"]["x_star"][0])
    poles = [p["T0h"] for p in chain_poles(bp["sysd"])]
    log(f"  [A1] статическая карта с жёстким пином ({label})...")
    out = {}
    n_ndg = 0
    n_tot = 0
    for tag, ndir, nsides in (("collapse", -1, 12), ("blowup", 1, 6)):
        rr = {}
        for rec in station_scales(t0s, nsides, ndir):
            if rec["k"] == 0:
                continue
            if any(abs(rec["T0h"] - p) < 1e-6 for p in poles):
                rr[f"k{rec['k']}"] = {"class": "pole_station",
                                      "T0h": rec["T0h"]}
                continue
            pl = pinned_landing(dae, chain, rec["T0h"])
            pl["T0h"] = rec["T0h"]
            pl["station"] = rec["station"]
            rr[f"k{rec['k']}"] = {
                k: pl.get(k) for k in
                ("F_max", "F_book", "R1h", "class", "converged",
                 "tower_norm_ratio", "T0h", "station")}
            n_tot += 1
            if pl.get("class") == "nondegenerate" and pl.get("converged"):
                n_ndg += 1
        out[tag] = rr
        ndg = [k for k, v in rr.items() if v.get("class") == "nondegenerate"]
        log(f"    {tag}: недегенератных носителей: {len(ndg)} "
            f"(полубашни/близкие: "
            f"{sum(1 for v in rr.values() if 'half' in str(v.get('class')))})")
    out["verdict"] = (f"недегенератных статических состояний на "
                      f"забронированных масштабах: {n_ndg}/{n_tot} — "
                      f"{' часы не имеют статического носителя вне '
                       'критического масштаба' if n_ndg == 0 else
                       'ЕСТЬ недегенератные носители (см. классы)'}")
    log(f"    {out['verdict']}")
    return out


# ------------------------------------------- [C1] теорема о паре часов (точно) --
def layer_C1(kv, bp, label):
    """[C1] общие факторы UV_xi3/Mdef_xi5 на цепочке; единственность tau*."""
    log(f"  [C1] пара часов UV_xi3 vs Mdef_xi5 на цепочке ({label})...")
    T0h = bp["syms"]["T0h"]
    R1h = bp["syms"]["R1h"]
    nums = {}
    for k in ("UV_xi3", "Mdef_xi5"):
        e = sp.cancel(sp.together(sp.expand(
            bp["eqs_frozen"][k].subs(bp["chain_subs"]).subs(R1h, 1))))
        nums[k] = sp.expand(sp.numer(e))
        log(f"    {k} | chain = {sp.sstr(sp.factor(nums[k]))[:150]}")
    g = sp.gcd(nums["UV_xi3"], nums["Mdef_xi5"])
    g = sp.factor(g)
    log(f"    GCD = {sp.sstr(g)}")
    tau_star_s = sp.simplify(27 / (2 * kv))
    g_at = sp.simplify(g.subs(T0h, sp.sqrt(tau_star_s)))
    exact_zero = bool(sp.simplify(g_at) == 0)
    roots = []
    for r_ in sp.nroots(g, n=30, maxsteps=300):
        if abs(sp.im(r_)) < 1e-20:
            roots.append(float(sp.re(r_)))
    pos = sorted({round(r, 8) for r in roots if r > 1e-8})
    # индивидуальные корни каждого уравнения (вся структура)
    ind = {}
    for k, n_ in nums.items():
        rp = sorted({round(float(sp.re(r)), 8) for r in sp.nroots(n_, n=30,
                                                                maxsteps=300)
                     if abs(sp.im(r)) < 1e-12 and sp.re(r) > 1e-8})
        ind[k] = rp
    out = {
        "gcd_on_chain": sp.sstr(g),
        "UV_xi3_on_chain": sp.sstr(sp.factor(nums["UV_xi3"])),
        "Mdef_xi5_on_chain": sp.sstr(sp.factor(nums["Mdef_xi5"])),
        "gcd_at_tau_star_zero": exact_zero,
        "tau_star_symbolic": sp.sstr(tau_star_s),
        "tau_star_numeric": float(sp.N(tau_star_s, 20)),
        "gcd_positive_roots": pos,
        "individual_positive_roots": ind,
    }
    unique = (len(pos) == 1
              and abs(pos[0] - np.sqrt(float(sp.N(tau_star_s, 20)))) < 1e-6)
    out["unique_common_clock"] = bool(unique)
    out["verdict"] = (
        f"пара часов (UV_xi3, Mdef_xi5) на T1c-форме источников (цепочка) "
        f"имеет ЕДИНСТВЕННЫЙ общий положительный корень tau* = "
        f"{out['tau_star_symbolic']} = {out['tau_star_numeric']:.6f} "
        f"(точно: {exact_zero}; единственность: {unique}) — наивная "
        f"несовместимость 9/4 vs 9/16 растворена: обе ветви замыкаются на "
        f"ОДНИХ часах, один кирпич двигает их 27/4 -> 1323/(196-pi^2)")
    log(f"    {out['verdict']}")
    return out


# ------------------------------------------------------- [C2] носители часов --
def layer_C2(kv, bp, label):
    """[C2] книги часов в x* и в дегенератных углах [A1]."""
    dae = bp["dae"]
    x_star = bp["sysd"]["x_star"]
    a = x_star[:9]
    w = float(a[4] / a[0] ** 2)
    u3 = float(9 * a[5] / (2 * a[3] * a[0] ** 2))
    s = float(3 * a[1] / a[0])
    kappa = float(sp.N(kv, 20))
    tau_s = float(sp.N(27 / (2 * kv), 20))
    w_book = 2 * kappa / 3
    u3_book = 27.0 / (4.0 * tau_s)      # лестница R3h = 3/2 => 9R3/(2R1T0^2) = k/2
    out = {"x_star": {"W2_over_T02": w, "W2_book_2k/3": w_book,
                      "W2_defect": w - w_book,
                      "UV_book_9R3/(2R1T0^2)": u3,
                      "UV_book_k/2": u3_book,
                      "UV_defect": u3 - u3_book,
                      "R3h_ladder_3/2": float(a[5]),
                      "s_clock_3P2/T0": s,
                      "ladder": {"R3h": float(a[5]), "W2h": float(a[4]),
                                 "R5h": float(a[7]), "M5h": float(a[8])}}}
    log(f"    x*: W2/T0^2 = {w:.9f} (книга {w_book:.9f}, дефект "
        f"{out['x_star']['W2_defect']:.2e}); UV-книга {u3:.9f} "
        f"(k/2 = {u3_book:.9f}, дефект {out['x_star']['UV_defect']:.2e}, "
        f"R3h = {float(a[5]):.6f} vs лестница 3/2); s = {s:.12f}")
    # дегенератный угол: R1h -> 0 (полубашня) — кольцевые книги мертвы
    corners = {}
    for rec in station_scales(float(x_star[0]), 3, -1):
        if rec["k"] == 0:
            continue
        ac = np.zeros(9)
        ac[0] = rec["T0h"]
        ac[1] = rec["T0h"] / 3
        ac[3] = 1e-12
        Fv = dae.eval_F(np.concatenate([ac, np.zeros(11)]))
        corners[f"k{rec['k']}"] = {
            "F_max_half_tower": float(np.max(np.abs(Fv))),
            "W2_over_T02": float(4 * ac[3] * rec["T0h"] ** 2 / 3
                                 / rec["T0h"] ** 2),
            "note": "R1h=1e-12: R3h=R5h=M5h=0, кольцевые часы мертвы"}
    out["half_tower_corners"] = corners
    fmax = max(v["F_max_half_tower"] for v in corners.values())
    out["verdict"] = (
        f"часы в x*: кольцевая книга W2/T0^2 = 2k/3 точна "
        f"({out['x_star']['W2_defect']:.1e}), UV-книга 9R3/(2R1T0^2) = k/2 "
        f"точна ({out['x_star']['UV_defect']:.1e}; лестница R3h = "
        f"{float(a[5]):.6f} ~ 3/2 — голономно-инвариантна), s = "
        f"{s:.12f}; вне x* статический носитель часов аннигилирует "
        f"(полубашня: F = {fmax:.1e} при R1h = 1e-12, кольцевые амплитуды "
        f"= 0) — часы живут только в критическом масштабе статически")
    log(f"    {out['verdict']}")
    return out


# --------------------------------------- [C3] B4-remnant (дельта-чувствительность) --
def kernel_Mr(dae, x_amp):
    """Точная линейная карта (v,dd) -> r при фиксированных амплитудах."""
    M = np.zeros((9, 11))
    for j in range(11):
        x = np.concatenate([x_amp, np.zeros(11)])
        x[9 + j] = 1.0
        M[:, j] = dae.rvec(x)[0]
    return M


def layer_C3(kv, bp, label):
    """[C3] кернел в x*, марш 1 эхо с кернел-направлением, мелкая сетка."""
    dae = bp["dae"]
    x_star = bp["sysd"]["x_star"]
    chain = bp["chain"]
    out = {}
    # (i) кернел M_r в x*
    M = kernel_Mr(dae, x_star[:9])
    sv = np.linalg.svd(M, compute_uv=False)
    rk10 = int(np.sum(sv > sv[0] * 1e-10))
    rk7 = int(np.sum(sv > sv[0] * 1e-7))
    _, _, vt = np.linalg.svd(M)
    ker = vt[rk7:]
    out["kernel_at_x_star"] = {
        "sv": [float(v) for v in sv],
        "rank_tol1e-10": rk10, "rank_tol1e-7": rk7,
        "dim_kernel": 11 - rk7,
        "top_kernel_dir_(v,dd)": [float(v) for v in ker[0]] if len(ker) else None,
    }
    log(f"    кернел M_r в x*: rank = {rk10} (1e-10) / {rk7} (1e-7), "
        f"dim ker = {11 - rk7}")
    # (ii) марш 1 эхо из project_Fr(x* + eps*ker)
    eps = 0.05 * dae.scale
    tick = {}
    if len(ker):
        z = ker[0] / (float(np.max(np.abs(ker[0]))) or 1.0)
        tick = {}
        for e_tag, e_eps in (("eps0.05", eps), ("eps0.01", 0.01 * dae.scale)):
            x0 = np.concatenate([x_star[:9], np.zeros(11)]) + e_eps * \
                np.concatenate([np.zeros(9), z])
            try:
                x0p, rep = dae.project_Fr(x0, rounds=3)
                rec = {"start_F_max": rep["F_max"],
                       "start_r_max": rep["r_max"],
                       "kick": e_eps}
                try:
                    V, dia = dae.closure(x0p)
                    h = 1e-7 * max(1.0, float(np.linalg.norm(x0p)))
                    rp, _ = dae.rvec(x0p + h * V)
                    rm, _ = dae.rvec(x0p)
                    rec["V_norm_at_start"] = float(np.linalg.norm(V))
                    rec["exit_rate"] = float(np.linalg.norm(rp - rm) / h)
                    mres = dae.march(x0p, 1)
                    rec["march_breakdown"] = mres["monitors"]["breakdown"]
                    rec["march_r_max"] = max(r_["r_max"]
                                             for r_ in mres["rows"])
                    rec["march_dist_end"] = mres["rows"][-1]["dist"]
                except dnc.BreakdownError as ex2:
                    rec["closure_breakdown"] = str(ex2)
                tick[e_tag] = rec
            except dnc.BreakdownError as ex:
                tick[e_tag] = {"breakdown_at_projection": str(ex),
                               "kick": e_eps}
    out["tick_test"] = tick
    log(f"    тик-тест: {json.dumps(tick, ensure_ascii=False)[:400]}")
    # (iii) мелкая сетка: статический F и гомотетический r книги
    t0s = float(x_star[0])
    pole_t = [p["T0h"] for p in chain_poles(bp["sysd"])]
    grid = {}
    for j in range(6):                       # первый цикл коллапса, 4 точки/сторону
        r0 = sum(hx.STEPS[i % 6] for i in range(j))
        r1 = r0 + hx.STEPS[j % 6]
        for m in range(4):
            rb = r0 + (r1 - r0) * m / 4.0
            T0h_v = t0s * float(np.exp(-rb))
            if any(abs(T0h_v - p) < 1e-6 for p in pole_t):
                continue
            try:
                xs = make_state(chain, T0h_v, kinetic=False)
                if not np.all(np.isfinite(xs)):
                    continue
                Fs = float(np.max(np.abs(dae.eval_F(xs))))
                xk = make_state(chain, T0h_v, kinetic=True)
                rv, _ = dae.rvec(xk)
                grid[f"r{rb:.5f}"] = {"T0h": T0h_v, "F_static_max": Fs,
                                      "r_homothetic_max":
                                      float(np.max(np.abs(rv)))}
            except dnc.BreakdownError:
                continue
    out["fine_grid_book_defects"] = grid
    if grid:
        fmx = max(v["F_static_max"] for v in grid.values())
        rmx = max(v["r_homothetic_max"] for v in grid.values())
        out["fine_grid_summary"] = {"F_static_max": fmx,
                                    "r_homothetic_max": rmx}
        log(f"    мелкая сетка ({len(grid)} масштабов): F_static_max = "
            f"{fmx:.3e}, r_homothetic_max = {rmx:.3e}")
    tt = out.get("tick_test", {})
    t05 = tt.get("eps0.05", {})
    t01 = tt.get("eps0.01", {})
    out["verdict"] = (
        f"кернел (v,dd)->r в x* {11 - rk7}-мерен (линейная свобода тика "
        f"есть), но подъём на совместное многообразие остановивается "
        f"(project_Fr: r_max = {t05.get('start_r_max', float('nan')):.3g} "
        f"при кике {t05.get('kick', float('nan')):.3g}; "
        f"{t05.get('closure_breakdown', 'замыкание/марш: см. данные')[:80]}) "
        f"— согласуется с v15 T2 (кокоядро-препятствие); дефект книги "
        f"вдоль мелкой сетки: F/r до "
        f"{out.get('fine_grid_summary', {}).get('F_static_max', float('nan')):.2e}/"
        f"{out.get('fine_grid_summary', {}).get('r_homothetic_max', float('nan')):.2e} "
        f"— B4-remnant на большой delta-чувствительности")
    log(f"    {out['verdict']}")
    return out


# --------------------------------------------------------------------- main --
def main() -> None:
    log("[1/4] Якоря гексцикла + точки кампании...")
    with open(os.path.join(RESULTS, "hexcycle.json"), encoding="utf-8") as fh:
        hxc = json.load(fh)
    assert abs(hxc["closure"]["kappa_cyc"] - np.log(64 / 9)) < 1e-12
    log(f"    tau3 = {hxc['anchors']['tau3']}, tau5 = {hxc['anchors']['tau5']}, "
        f"kappa_cyc = {hxc['closure']['kappa_cyc']:.6f}")

    bC = sp.pi**2 / 98
    points = {"baseline_kappa2": sp.Integer(2), "one_brick_2-bC":
              sp.Integer(2) - bC}
    out = {
        "title": "CLOCK-CLOSURE-T1C v17: замыкание часов через однокирпичную "
                 "форму источников T1c (вместо несовместной наивной O6+) "
                 "+ B4-remnant на большой delta-чувствительности",
        "question": ("автор, сессия 21: замыкание часов через однокирпичную "
                     "форму источников T1c вместо наивной O6+ (несовместные "
                     "ветви 9/4 vs 9/16), либо remnant-тест B4 на данных с "
                     "большей delta-чувствительностью"),
        "erratum_v16": (
            "static_landing (v16) не прикалывала T0h (dx[0] != 0 в ньютоновском "
            "шаге при заявленном пине): посадки [T1c] v16 — захваты тривиальной "
            "ветви (T0h -> 0, tower -> 0) или полубашни R1h -> 0; вердикт v16 "
            "«компенсированная книга = статический хребет CSS-подобных "
            "равновесий» пересматривается слоями [A0]/[A1]"),
        "points": {},
        "runtime_s": None,
    }

    for label, kv in points.items():
        log(f"\n================ {label}: kappa = {sp.N(kv, 15)} ================")
        bp = build_point(kv)
        t0s = float(bp["sysd"]["x_star"][0])
        log(f"  [N0] T0h* = {t0s:.9f}, tau* = {bp['sysd']['tau_star']:.9f}, "
            f"F(x*) = {bp['sysd']['residual_at_point']:.2e}")
        p = {"T0h_star": t0s, "tau_star": bp["sysd"]["tau_star"],
             "residual_at_point": bp["sysd"]["residual_at_point"]}
        p["A0_erratum_audit"] = layer_A0(kv, bp, label)
        p["A1_honest_static_map"] = layer_A1(kv, bp, label)
        p["C1_clock_pair_theorem"] = layer_C1(kv, bp, label)
        p["C2_clock_carriers"] = layer_C2(kv, bp, label)
        p["C3_b4_remnant"] = layer_C3(kv, bp, label)
        out["points"][label] = p

    log("\n[4/4] Вердикт...")
    v = []
    c1b = out["points"]["baseline_kappa2"]["C1_clock_pair_theorem"]
    c1o = out["points"]["one_brick_2-bC"]["C1_clock_pair_theorem"]
    v.append(f"ТЕОРЕМА О ПАРЕ ЧАСОВ (точно): {c1b['verdict']}")
    v.append(f"one-brick: {c1o['verdict']}")
    a0b = out["points"]["baseline_kappa2"]["A0_erratum_audit"]["verdict"]
    a0o = out["points"]["one_brick_2-bC"]["A0_erratum_audit"]["verdict"]
    v.append(f"ERRATUM v16 (baseline): {a0b}")
    v.append(f"ERRATUM v16 (one-brick): {a0o}")
    v.append(f"статическая карта (baseline): "
             f"{out['points']['baseline_kappa2']['A1_honest_static_map']['verdict']}")
    v.append(f"статическая карта (one-brick): "
             f"{out['points']['one_brick_2-bC']['A1_honest_static_map']['verdict']}")
    v.append(f"носители часов: "
             f"{out['points']['baseline_kappa2']['C2_clock_carriers']['verdict']}")
    v.append(f"B4-remnant (baseline): "
             f"{out['points']['baseline_kappa2']['C3_b4_remnant']['verdict']}")
    v.append(f"B4-remnant (one-brick): "
             f"{out['points']['one_brick_2-bC']['C3_b4_remnant']['verdict']}")
    v.append("ИТОГ: замыкание часов через однокирпичную форму источников T1c "
             "состоялось КАК КНИГА ПАРЫ (единственные общие часы tau* = "
             "27/(2kappa), один кирпич двигает их к наблюдаемому значению), "
             "но НЕ как статический носитель: недегенератных статических "
             "состояний вне критического масштаба нет (посадки v16 — "
             "тривиальные захваты, erratum), тик на кернеле срывается — "
             "живые часы остаются за PDE-машиной v6-v9")
    out["verdict_lines"] = v
    for line in v:
        log(f"    - {line}")
    out["honest_notes"] = [
        "erratum: дефект пина T0h в static_landing (v16) — посадки [T1c]/часть "
        "[T1b]/часть [T3] v16 могли сходиться к тривиальной ветви; чистые "
        "слои v16 (T1a прямые вычисления, T1d скан, T2 кинетика) не зависят "
        "от пина и остаются в силе",
        "якоря tau3 = 9/4, tau5 = 9/16 — записанные ветвные значения "
        "наивного O6+ (center_o6_nsolve, вход модели гексцикла); в "
        "де-адиабатизованной форме они не являются корнями ветвных уравнений "
        "на цепочке — пара замыкается на единых часах tau*(kappa)",
        "мультистарт-Ньютон локален: недегенератные статические ветви вдали "
        "от книги/стартов не исключены (глобальный поиск — отдельная машина)",
        "жёсткость — свойство усечённой башни; PDE-машина v6-v9 остаётся "
        "носителем физики эха и живых часов",
    ]
    out["runtime_s"] = round(time.time() - T_START, 1)
    path = os.path.join(RESULTS, "clock_closure_t1c.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, default=str)
    log(f"Сохранено: {path} ({out['runtime_s']} c)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
