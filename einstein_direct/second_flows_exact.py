#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ТОЧНЫЙ анализ QEP второго потока в baseline-точке (все значения в Q(sqrt3)).

Закрывает два оставшихся вопроса:
  [E1] точный char-полином det(M^T M), deg <= 36, рациональной интерполяцией
       по 41 целой точке (метод сеанса 14, теперь для квадратичного карандаша)
       -> НЕТ ли пропущенных компанионом корней (в т.ч. кратности в lambda=0);
  [E2] вердикт mpmath 40 знаков С ТОЧНЫМИ записями (не float!) для всех
       корней: подлинная мода = sigma_min < 1e-30 * sigma_max.

Одинаково для baseline (Q(sqrt3), точно) и one-brick (pi-записи, evalf(40)).
"""
import os
import sys
import time
import warnings

import numpy as np
import sympy as sp
import mpmath as mp

BASE = "/home/z/my-project/choptuik_ac_bc/einstein_direct"
sys.path.insert(0, BASE)
os.chdir(BASE)
warnings.filterwarnings("ignore")

mp.mp.dps = 40
LAM = sp.Symbol("lam")


def build_exact_system(kv):
    """Точная (символьная) пересборка F + точки при kappa=kv."""
    import sympy_second_flows as sf
    o6, p4 = sf.load_patched(kv, kv, kv)
    zc_sf, dds = sf.build_zc_sf(o6, p4)
    ok_sf = {k: v for k, v in zc_sf.items() if v.get("status") == "ok"}
    zero_all = {f_: 0 for f_ in (p4.dT0, p4.dD0, p4.Qh, p4.dR1, p4.dW2,
                                 p4.dR3, p4.dP4, p4.dR5)}
    zero_all.update({d_: 0 for d_ in dds})
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

    tv_exact = sp.simplify(27 / (2 * kv))
    t0v = sp.sqrt(tv_exact)
    point = {T0h: t0v, R1h: sp.Integer(1), D0h: sp.Integer(0)}
    for k_, sym_ in (("R3h", R3h), ("W2h", W2h), ("P2h", P2h),
                     ("R5h", R5h), ("M5h", M5h), ("P4h", P4h)):
        point[sym_] = sp.simplify(sp.expand(
            {"R3h": r3, "W2h": w2, "P2h": p2, "R5h": r5,
             "M5h": m5, "P4h": p4v}[k_]).subs(T0h, t0v).subs(R1h, 1))
    for f_ in (p4.dT0, p4.dD0, p4.Qh, p4.dR1, p4.dW2, p4.dR3, p4.dP4, p4.dR5):
        point[f_] = sp.Integer(0)
    for d_ in dds:
        point[d_] = sp.Integer(0)

    eqs_live = [sp.expand(v["num"]) for v in ok_sf.values()
                if sp.expand(v["num"]) != 0]
    flow_of = {D0h: p4.dD0, R3h: p4.dR3, W2h: p4.dW2,
               P2h: p4.Qh, R5h: p4.dR5, P4h: p4.dP4}
    prolong = []
    for amp, form in subs:
        if amp not in flow_of:
            continue
        prolong.append(sp.expand(sp.diff(form, T0h) * p4.dT0
                                 + sp.diff(form, R1h) * p4.dR1 - flow_of[amp]))
    F = eqs_live + prolong
    amps = [T0h, P2h, D0h, R1h, W2h, R3h, P4h, R5h, M5h]
    flows = [p4.dT0, p4.dD0, p4.Qh, p4.dR1, p4.dW2, p4.dR3, p4.dP4, p4.dR5]
    # точные якобианы
    Ja = sp.Matrix(len(F), len(amps),
                   lambda i_, j_: sp.simplify(
                       sp.expand(sp.diff(F[i_], amps[j_]).subs(point))))
    Jv = sp.Matrix(len(F), len(flows),
                   lambda i_, j_: sp.simplify(
                       sp.expand(sp.diff(F[i_], flows[j_]).subs(point))))
    J2 = sp.Matrix(len(F), len(dds),
                   lambda i_, j_: sp.simplify(
                       sp.expand(sp.diff(F[i_], dds[j_]).subs(point))))
    Pproj = sp.zeros(8, 9)
    for i_, j_ in {0: 0, 1: 2, 2: 1, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}.items():
        Pproj[i_, j_] = 1
    P2proj = sp.zeros(3, 9)
    for i_, j_ in {0: 4, 1: 5, 2: 6}.items():
        P2proj[i_, j_] = 1
    A_ex = Ja
    B_ex = Jv * Pproj
    C_ex = J2 * P2proj
    return A_ex, B_ex, C_ex, point, tv_exact


def to_mp40(expr_mat):
    return mp.matrix([[mp.mpf(str(sp.N(e_, 45))) if e_.is_real
                       else mp.mpc(str(sp.N(sp.re(e_), 45)),
                                  str(sp.N(sp.im(e_), 45)))
                       for e_ in row] for row in expr_mat.tolist()])


def sv_verdict_mp(A_rows, B_rows, C_rows, lam_mp):
    nrow, ncol = 18, 9
    M = mp.matrix(nrow, ncol)
    for i_ in range(nrow):
        for j_ in range(ncol):
            M[i_, j_] = (A_rows[i_][j_] + lam_mp * B_rows[i_][j_]
                         + lam_mp**2 * C_rows[i_][j_])
    P = mp.matrix(nrow, ncol)
    Q = mp.matrix(nrow, ncol)
    for i_ in range(nrow):
        for j_ in range(ncol):
            P[i_, j_] = mp.re(M[i_, j_])
            Q[i_, j_] = mp.im(M[i_, j_])
    R = mp.matrix(2 * nrow, 2 * ncol)
    for i_ in range(nrow):
        for j_ in range(ncol):
            R[i_, j_] = P[i_, j_]
            R[i_, ncol + j_] = -Q[i_, j_]
            R[nrow + i_, j_] = Q[i_, j_]
            R[nrow + i_, ncol + j_] = P[i_, j_]
    G = R.T * R
    ev = sorted([float(mp.re(e_)) for e_ in mp.eigsy(G, eigvals_only=True)])
    smin = mp.sqrt(max(ev[0], 0.0))
    smax = mp.sqrt(max(ev[-1], 0.0))
    rel = smin / smax if smax > 0 else mp.mpf("0")
    verdict = ("GENUINE" if rel < mp.mpf("1e-30")
               else "BORDERLINE" if rel < mp.mpf("1e-18") else "PHANTOM")
    return float(rel), verdict


def main() -> None:
    t_all = time.time()
    out = {"title": "exact char polynomial + 40-digit verdicts (second flows)"}

    # ---------------- baseline: точная интерполяция в Q(sqrt3) ----------------
    print("=== baseline: точные матрицы Q(sqrt3) ===", flush=True)
    t0 = time.time()
    A_ex, B_ex, C_ex, point, tv_ex = build_exact_system(sp.Integer(2))
    print(f"  построено за {time.time()-t0:.1f} c; tau* = {tv_ex} = 27/4", flush=True)
    resid_max = max(abs(sp.N(e_.subs(point), 30)) for e_ in
                    [sp.expand(0)] ) if False else None
    # остаток в точке: F = 0 проверен в campaign_point; здесь точные записи:
    print(f"  A_ex[0,0] = {A_ex[0, 0]};  rank-структура C:", flush=True)
    C_rank = sp.Matrix(C_ex).rank()
    print(f"  rank C (точный) = {C_rank}", flush=True)

    lam = LAM
    t0 = time.time()
    pts_ = []
    for j_ in range(0, 45):
        lj = sp.Integer(j_)
        Mj = A_ex + lj * B_ex + lj**2 * C_ex
        Gj = (Mj.T * Mj)
        pts_.append((lj, sp.simplify(Gj.det())))
    print(f"  45 точных детерминантов за {time.time()-t0:.1f} c", flush=True)
    t0 = time.time()
    char = sp.interpolate(pts_, lam)
    char = sp.expand(sp.simplify(sp.cancel(char)))
    deg = sp.Poly(char, lam).degree()
    print(f"  интерполяция deg {deg} за {time.time()-t0:.1f} c", flush=True)
    # кросс-чек вне сетки
    chk = sp.simplify(char.subs(lam, sp.Rational(1, 2)) -
                      (A_ex + sp.Rational(1, 2) * B_ex
                       + sp.Rational(1, 4) * C_ex).T.multiply(
                          A_ex + sp.Rational(1, 2) * B_ex
                          + sp.Rational(1, 4) * C_ex).det()) == 0
    print(f"  кросс-чек вне сетки (lam=1/2): {chk}", flush=True)
    fac = sp.factor(char)
    print(f"  факторизация: {str(fac)[:300]}{'...' if len(str(fac))>300 else ''}",
          flush=True)
    mult0 = sp.Poly(char, lam).nth(0) == 0
    k0 = 0
    poly_ = char
    while sp.simplify(poly_.subs(lam, 0)) == 0 and k0 < 40:
        poly_ = sp.quo(poly_, lam)
        k0 += 1
    print(f"  кратность корня lambda=0: {k0}", flush=True)
    t0 = time.time()
    roots = sp.nroots(char, n=30, maxsteps=200)
    print(f"  nroots: {len(roots)} за {time.time()-t0:.1f} c", flush=True)

    A_mp = to_mp40(A_ex)
    B_mp = to_mp40(B_ex)
    C_mp = to_mp40(C_ex)
    A_rows = A_mp.tolist()
    B_rows = B_mp.tolist()
    C_rows = C_mp.tolist()
    seen = []
    verdicts = []
    for r_ in roots:
        if abs(complex(r_)) > 1e8:
            continue
        if any(abs(complex(r_) - s_) < 1e-6 * max(1.0, abs(complex(r_)))
               for s_ in seen):
            continue
        seen.append(complex(r_))
        rel, verdict = sv_verdict_mp(A_rows, B_rows, C_rows,
                                     mp.mpc(str(float(sp.re(r_))),
                                            str(float(sp.im(r_)))))
        verdicts.append({"lambda": [float(sp.re(r_)), float(sp.im(r_))],
                         "rel_sigma_min_40d": rel, "verdict": verdict})
        print(f"    l = {float(sp.re(r_)):+.6e} {float(sp.im(r_)):+.6e}i "
              f"rel40 = {float(rel):.2e} -> {verdict}", flush=True)
    n_gen = sum(1 for v_ in verdicts if v_["verdict"] == "GENUINE")
    print(f"  ИТОГ baseline: {n_gen} подлинных из {len(verdicts)} "
          f"различных корней; кратность lambda=0: {k0}", flush=True)
    out["baseline"] = {
        "char_degree": int(deg), "char_factor_head": str(fac)[:500],
        "multiplicity_lambda0": k0, "crosscheck_lam_half": bool(chk),
        "rank_C_exact": int(C_rank), "verdicts": verdicts,
        "n_genuine": n_gen,
    }

    # ---------------- one-brick: 40-значные записи ----------------
    print("\n=== one-brick (2 - pi^2/98): записи evalf(40) ===", flush=True)
    bC = sp.pi**2 / 98
    A_ex2, B_ex2, C_ex2, point2, tv2 = build_exact_system(2 - bC)
    print(f"  tau* = {sp.N(tv2, 20)}", flush=True)
    C_rank2 = sp.Matrix(C_ex2).rank()
    print(f"  rank C (точный) = {C_rank2}", flush=True)
    A_mp2 = to_mp40(A_ex2)
    B_mp2 = to_mp40(B_ex2)
    C_mp2 = to_mp40(C_ex2)
    A2r, B2r, C2r = A_mp2.tolist(), B_mp2.tolist(), C_mp2.tolist()
    # кандидаты: из численной кампании (7 genuine + окрестность нуля фантомов)
    import json
    with open("results/second_flows_limit_cycle.json", encoding="utf-8") as fh:
        stored = json.load(fh)
    pt2 = next(p_ for p_ in stored["points"] if p_["label"] == "one_brick_2-bC")
    cands = [complex(*g_["lambda"]) for g_ in pt2["qep"]["genuine"]]
    cands += [0.0 + 0.0j]
    verdicts2 = []
    seen2 = []
    for c_ in cands:
        if any(abs(c_ - s_) < 1e-6 * max(1.0, abs(c_)) for s_ in seen2):
            continue
        seen2.append(c_)
        rel, verdict = sv_verdict_mp(A2r, B2r, C2r, mp.mpc(str(c_.real), str(c_.imag)))
        verdicts2.append({"lambda": [c_.real, c_.imag],
                          "rel_sigma_min_40d": float(rel), "verdict": verdict})
        print(f"    l = {c_.real:+.6e} {c_.imag:+.6e}i "
              f"rel40 = {float(rel):.2e} -> {verdict}", flush=True)
    n_gen2 = sum(1 for v_ in verdicts2 if v_["verdict"] == "GENUINE")
    print(f"  ИТОГ one-brick: {n_gen2} подлинных из {len(verdicts2)}", flush=True)
    out["one_brick"] = {"rank_C_exact": int(C_rank2),
                        "verdicts": verdicts2, "n_genuine": n_gen2,
                        "tau_star": str(sp.N(tv2, 20))}

    with open("results/second_flows_exact.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, default=str)
    print(f"\nГотово за {time.time()-t_all:.1f} c -> results/second_flows_exact.json",
          flush=True)


if __name__ == "__main__":
    main()
