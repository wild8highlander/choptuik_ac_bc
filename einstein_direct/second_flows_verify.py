#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Верификация мод QEP второго потока: Ньютон-полировка + mpmath-вердикт.

Вопрос: какие из кандидатов — ПОДЛИННЫЕ ранг-падения M(lam) (18x9), какие —
артефакты компанион-линеаризации / лямбда^2-доминирования?

[V1] символическое ядро Ja (якорь l=0, протокол сеанса 14);
[V2] Ньютон по lam на sigma_min(M(lam));
[V3] mpmath 40 знаков: подлинная мода = sigma_min < 1e-25 * sigma_max
     (пол записей на 40 знаках ~1e-38 * sigma_max).
"""
import os
import sys
import warnings

import numpy as np
import sympy as sp
import mpmath as mp

BASE = "/home/z/my-project/choptuik_ac_bc/einstein_direct"
sys.path.insert(0, BASE)
os.chdir(BASE)
warnings.filterwarnings("ignore")

import sympy_second_flows as sf  # noqa: E402

mp.mp.dps = 40


def to_mp(mat):
    return mp.matrix([[mp.mpc(str(float(np.real(x_))), str(float(np.imag(x_))))
                       for x_ in row] for row in mat.tolist()])


def sv_min_max_mp(M_mp):
    """sigma_min/sigma_max комплексной 18x9 через реафикацию R=[[P,-Q],[Q,P]]:
    сингулярные числа R = сингулярные числа M (каждый дважды), R^T R — вещественная
    симметричная 18x18 -> mp.eigsy."""
    nrow, ncol = M_mp.rows, M_mp.cols
    P = mp.matrix(nrow, ncol)
    Q = mp.matrix(nrow, ncol)
    for i_ in range(nrow):
        for j_ in range(ncol):
            P[i_, j_] = mp.re(M_mp[i_, j_])
            Q[i_, j_] = mp.im(M_mp[i_, j_])
    R = mp.matrix(2 * nrow, 2 * ncol)
    for i_ in range(nrow):
        for j_ in range(ncol):
            R[i_, j_] = P[i_, j_]
            R[i_, ncol + j_] = -Q[i_, j_]
            R[nrow + i_, j_] = Q[i_, j_]
            R[nrow + i_, ncol + j_] = P[i_, j_]
    G = R.T * R
    ev = sorted([float(mp.re(e_)) for e_ in mp.eigsy(G, eigvals_only=True)])
    return mp.sqrt(max(ev[0], 0.0)), mp.sqrt(max(ev[-1], 0.0))


def polish_and_verdict(A_n, B_n, C_n, lam0, n_iter=80):
    lam = complex(lam0)

    def svmin_sc(l_):
        M = A_n + l_ * B_n + l_**2 * C_n
        sv = np.linalg.svd(M, compute_uv=False)
        return float(sv[-1])

    f0 = svmin_sc(lam)
    lam_start = lam
    for _ in range(n_iter):
        M = A_n + lam * B_n + lam**2 * C_n
        U, sv, Vh = np.linalg.svd(M)
        if sv[-1] <= 0:
            break
        u = U[:, -1]
        v = np.conj(Vh[-1])
        Mp = B_n + 2 * lam * C_n
        w = np.conj(u) @ (Mp @ v)
        grad = np.array([float(np.real(w)), float(-np.imag(w))])
        gn = np.linalg.norm(grad)
        if gn < 1e-300:
            break
        t = 1e-7 * max(f0, 1e-30) / gn
        improved = False
        for _ in range(40):
            lam_new = lam - t * (grad[0] + 1j * grad[1])
            f_new = svmin_sc(lam_new)
            if f_new < f0:
                lam, f0 = lam_new, f_new
                improved = True
                break
            t /= 3
        if not improved or f0 == 0.0:
            break
    A_mp, B_mp, C_mp = to_mp(A_n), to_mp(B_n), to_mp(C_n)
    lam_mp = mp.mpc(str(lam.real), str(lam.imag))
    smin, smax = sv_min_max_mp(A_mp + lam_mp * B_mp + lam_mp**2 * C_mp)
    rel = smin / smax
    verdict = ("GENUINE" if rel < mp.mpf("1e-25")
               else "BORDERLINE" if rel < mp.mpf("1e-15") else "PHANTOM")
    return {"lam_before": [float(np.real(lam0)), float(np.imag(lam0))],
            "lam_polished": [float(lam.real), float(lam.imag)],
            "rel_before": None, "rel_after_mp": float(rel),
            "sigma_min_abs_mp": float(smin), "sigma_max_mp": float(smax),
            "verdict": verdict}


def main() -> None:
    print("=== пересборка точек (кэш матриц) ===", flush=True)
    sf.campaign_point(sp.Integer(2), "baseline_kappa2")
    bC = sp.pi**2 / 98
    sf.campaign_point(2 - bC, "one_brick_2-bC")

    out = {"title": "verification of second-flow QEP modes (Newton + mpmath 40d)",
           "points": []}
    for label in ("baseline_kappa2", "one_brick_2-bC"):
        A_n, B_n, C_n = sf._MATRICES[label]
        rec = {"label": label, "V1_kernel_Ja": {}, "verified": []}
        # [V1] ядро Ja (l=0)
        sv = np.linalg.svd(A_n, compute_uv=False)
        rel0 = float(sv[-1] / sv[0])
        rec["V1_kernel_Ja"] = {"rel_sigma_min_at_0": rel0,
                               "kernel_dim_approx": int(np.sum(sv < sv[0] * 1e-9))}
        # кандидаты: все genuine + фантомы с |lam| < 0.05 (окрестность нуля)
        qep = None
        # достаём кандидатов из сохранённого JSON
        import json
        with open("results/second_flows_limit_cycle.json", encoding="utf-8") as fh:
            stored = json.load(fh)
        pt = next(p_ for p_ in stored["points"] if p_["label"] == label)
        cands = [complex(*g_["lambda"]) for g_ in pt["qep"]["genuine"]]
        cands += [complex(*p_["lambda"]) for p_ in pt["qep"]["phantoms"]
                  if abs(complex(*p_["lambda"])) < 0.05]
        # дополнение: l=0 явно + подлинные моды ЛИНЕЙНОГО карандаша (сеанс 15/16)
        cands.append(0.0 + 0.0j)
        ref = "spinor_corrections.json" if label == "baseline_kappa2" \
            else "spinor_corrections_one_brick.json"
        try:
            with open(os.path.join("results", ref), encoding="utf-8") as fh:
                sp15 = json.load(fh)
            key = "S4_pencil_baseline" if label == "baseline_kappa2" else None
            if key and key in sp15:
                cands += [complex(*g_["lambda"]) for g_ in sp15[key]["genuine_modes"]]
            if label != "baseline_kappa2":
                cands += [complex(*g_["lambda"]) for g_ in sp15["genuine_modes"]]
        except Exception as ex_:  # noqa: BLE001
            print(f"  линейно-карандашные кандидаты недоступны: {ex_}")
        seen = []
        for c_ in cands:
            if any(abs(c_ - s_) < 1e-6 * max(1, abs(c_)) for s_ in seen):
                continue
            seen.append(c_)
            v = polish_and_verdict(A_n, B_n, C_n, c_)
            rec["verified"].append(v)
            print(f"  [{label}] l = {v['lam_before'][0]:+.6g}{v['lam_before'][1]:+.6g}i "
                  f"-> polished {v['lam_polished'][0]:+.6g}{v['lam_polished'][1]:+.6g}i "
                  f"rel_after = {v['rel_after_mp']:.2e} -> {v['verdict']}", flush=True)
        n_gen = sum(1 for v_ in rec["verified"] if v_["verdict"] == "GENUINE")
        rec["n_genuine_verified"] = n_gen
        out["points"].append(rec)
        print(f"  [{label}] VERIFIED genuine: {n_gen} / {len(rec['verified'])} "
              f"(ядро Ja при l=0: rel = {rel0:.2e})", flush=True)

    import json
    with open("results/second_flows_verified.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, default=str)
    print("saved -> results/second_flows_verified.json", flush=True)


if __name__ == "__main__":
    main()
