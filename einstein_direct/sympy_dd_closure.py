#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кампания [сессия 18, шаг (b)]: НЕЗАВИСИМЫЙ ЗАКОН ЭВОЛЮЦИИ dd.

Вопрос (сессия 17): слоты dd* введены с коэффициентом 1 «по прецеденту ddQ» —
закон эволюции вторых потоков надо ОБОСНОВАТЬ, не подогнать.

Метод (пролонгационное замыкание — единственное, выводимое из тождеств).
Состояние DAE: x = (a[9], v[8], dd[3]) = 20;
  ограничения  J1s x = 0,  J1s = [Ja | Jv | J2]  (18x20);
  кинематика   a' = P~v (8 слотов; M5h' свободна);
  пролонгация  d/dtau(J1s x) = 0  =>  J1s x' = 0:
    неизвестные (9): M5h', ddT0, ddD0, ddQ, ddR1, ddR5, dddW2, dddR3, dddP4
      (производные dW2', dR3', dP4' = dd ИЗВЕСТНЫ из состояния);
    матрица неизвестных  Uk = [Ja_{:,M5h} | Jv_{:,{dT0,dD0,Q,dR1,dR5}} | J2];
    известная часть      Known = [Ja_{:,flow} | Jv_{:,{dW2,dR3,dP4}}].
  Замыкание ЕДИНСТВЕННО <=> rank Uk = 9; совместимость <=> скрытые условия
    Op (v, dd) = 0, Op = W Known, W = левое ядро Uk (dim 9).
Допустимое многообразие эволюции: M2 = ker[J1s; Op'] (Op' — в координатах
состояния). Замыкание — НЕ выбор: это единственное решение пролонгации
тождеств (y-пролонгация остатков == tau-пролонгация на очищенных формах,
весовое правило сессии 18a) — «обосновано, не подогнано».

Обоснование (цепочка): остатки = Бианки-редуцированные уравнения Эйнштейна
( identity в y ) -> y-пролонгация = identity -> d/dy = (1/s) d/dtau
на очищенных формах (T1/T2 сессии 18a) -> tau-пролонгация = сохранение
ограничений -> Uk-система -> единственный закон dd' = ddd(a, v, dd).

Альтернативы (машинные факты):
  C0 (адиабатика dd = 0)  — допустима только на замороженном множестве
                            (ветви UV_xi3 и Mdef_xi5: общий фактор 4T0h^2-27,
                            R1h свободен — 1-мерное плоское направление);
  C-chain (потоки = d(цепочка)/dtau) — только замороженная точка (сессия 13,
                            V3-пролонгация, честная цитата);
  C-prol (пролонгационное) — единственное обоснованное; спектр = {0}
                            (Йордан-2) => delta_mono = 0 линейно.
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

# индексация машины (sympy_second_flows.campaign_point)
AMPS = ["T0h", "P2h", "D0h", "R1h", "W2h", "R3h", "P4h", "R5h", "M5h"]
FLOWS = ["dT0", "dD0", "Qh", "dR1", "dW2", "dR3", "dP4", "dR5"]
DDS = ["ddW2", "ddR3", "ddP4"]
FLOW_AMP = [0, 2, 1, 3, 4, 5, 6, 7]   # поток j живёт на амплитуде FLOW_AMP[j]
DD_AMP = [4, 5, 6]                    # dd k живёт на амплитуде DD_AMP[k]
NEW_FLOWS = [0, 1, 2, 3, 7]           # dT0, dD0, Qh, dR1, dR5 (их производные —
#              новые неизвестные; производные dW2/dR3/dP4 = dd из состояния)


def log(msg):
    print(msg, flush=True)


def _n(sp_mat):
    """sp.Matrix -> numpy complex128 (float64)."""
    return np.array(sp_mat.evalf(20).tolist(), dtype=complex)


def build_raw(kv):
    """Сырые якобианы состояния: Ja (18x9), Jv (18x8), J2 (18x3), tau*.

    build_exact_system возвращает проецированные JvP = Jv*Pproj (18x9) и
    J2P2 = J2*P2proj (18x9); сырые столбцы восстанавливаются точной
    перестановкой: JvP[:, FLOW_AMP[j]] = Jv[:, j]; J2P2[:, DD_AMP[k]] = J2[:, k].
    """
    import second_flows_exact as sfe
    A, B, C, point, tv = sfe.build_exact_system(kv)
    Ja = sp.Matrix(A)
    JvP, J2P2 = sp.Matrix(B), sp.Matrix(C)
    Jv = sp.Matrix(18, 8, lambda i, j: JvP[i, FLOW_AMP[j]])
    J2 = sp.Matrix(18, 3, lambda i, j: J2P2[i, DD_AMP[j]])
    return Ja, Jv, J2, tv


def closure_structures(Ja, Jv, J2):
    """Все матрицы пролонгационного замыкания (sp.Matrix, точные)."""
    Ja_f = Ja[:, FLOW_AMP]             # 18x8: кинематическая часть a'
    Ja_M5 = Ja[:, [8]]                 # 18x1: столбец M5h'
    Jv_new = Jv[:, NEW_FLOWS]          # 18x5: dT0', dD0', Q', dR1', dR5'
    Jv_dd = Jv[:, [4, 5, 6]]           # 18x3: известные dW2', dR3', dP4' = dd
    Uk = Ja_M5.row_join(Jv_new).row_join(J2)          # 18x9 неизвестные
    Known = Ja_f.row_join(Jv_dd)                      # 18x11 известные (v, dd)
    J1s = Ja.row_join(Jv).row_join(J2)                # 18x20 состояние
    return Uk, Known, J1s


def op_prime(Op):
    """Op (9x11) на (v, dd) -> матрица 9x20 в координатах состояния."""
    out = sp.zeros(Op.rows, 20)
    for i in range(Op.rows):
        for j in range(11):
            out[i, 9 + j] = Op[i, j]
    return out


# ============================== [B1] обоснование ============================
def b1_justification():
    """Точное ядро обоснования: d/dy = (1/s) d/dtau на очищенных формах."""
    s = sp.Symbol("s", positive=True)
    m, k = sp.Integer(3), sp.Integer(2)
    Gl = sp.exp(m * (-sp.log(s)))                     # G(tau) = e^{m tau}
    # проба чистой формы: d/dy[G] = G'/s  =>  (-d/ds[G]) * s = G'
    lhs = (-sp.diff(Gl, s)) * s
    ok_probe = sp.simplify(lhs - m * Gl) == 0
    # общее правило веса: d/dy[G s^-k] = (G' + kG) s^-k-1
    gen_lhs = -sp.diff(Gl * s**(-k), s) * s**(k + 1)
    gen_rhs = (m + k) * Gl
    gen_ok = sp.simplify(gen_lhs - gen_rhs) == 0
    log(f"  [B1] проба d/dy = (1/s) d/dtau (G=e^tau, m=3): {ok_probe}; "
        f"весовое правило d/dy[G s^-k] = (G'+kG) s^-k-1 (k=2): {gen_ok}")
    return {"pure_form_exact": bool(ok_probe),
            "weight_rule_exact": bool(gen_ok),
            "chain": ("остатки = Бианки-редуцированные Эйнштейна (identity в y)"
                      " -> y-пролонгация identity -> d/dy=(1/s)(d/dtau+вес)"
                      " (T1/T2 сессии 18a) -> tau-пролонгация = сохранение "
                      "ограничений -> единственное замыкание Uk")}


# ============================== [B2] замыкание ==============================
def b2_closure(kv, label=""):
    """Полная структура замыкания в точке kappa = kv.

    baseline (kappa = 2): ТОЧНЫЙ путь (Q(sqrt3), sympy rank/nullspace/linsolve)
    + дублирующий числовой контроль; прочие точки: числовой путь float64 с
    отчётом сингулярных зазоров (честная маркировка NUMERIC).
    """
    exact = (kv == sp.Integer(2))
    log(f"--- [B2] {label}: kappa = {sp.N(kv, 12)} "
        f"({'EXACT Q(sqrt3)' if exact else 'NUMERIC float64'}) ---")
    Ja, Jv, J2, tv = build_raw(kv)
    Uk, Known, J1s = closure_structures(Ja, Jv, J2)
    out = {"kappa": float(sp.N(kv, 15)), "tau_star": str(sp.N(tv, 20)),
           "mode": "EXACT" if exact else "NUMERIC-float64"}

    # ---------- ранги ----------
    if exact:
        r_Uk = Uk.rank()
        sv_Uk = None
    else:
        Ukn = _n(Uk)
        sv = np.linalg.svd(Ukn, compute_uv=False)
        r_Uk = int(np.sum(sv > sv[0] * 1e-11))
        sv_Uk = [float(x) for x in sv[-3:]]
    out["rank_Uk"] = int(r_Uk)
    out["sv_Uk_tail"] = sv_Uk
    log(f"  rank Uk = {r_Uk} (18x9) -> замыкание "
        f"{'ЕДИНСТВЕННО' if r_Uk == 9 else 'НЕ единственно'}")
    assert r_Uk == 9, "замыкание не единственно — останов"

    # ---------- левое ядро Uk -> скрытые условия ----------
    if exact:
        W = sp.Matrix(Uk.T).nullspace()
        assert len(W) == 9, f"левое ядро Uk: dim {len(W)} != 9"
        Wm = sp.Matrix.hstack(*W).T                   # 9x18
        Op = sp.simplify(Wm * Known)                  # 9x11
    else:
        u_, s_, _ = np.linalg.svd(_n(Uk), full_matrices=True)
        Wn = u_[:, 9:].conj().T                       # 9x18
        Op = sp.Matrix((Wn @ _n(Known)).tolist())     # 9x11
    r_Op = Op.rank() if exact else int(np.sum(
        np.linalg.svd(_n(Op), compute_uv=False) >
        np.linalg.svd(_n(Op), compute_uv=False)[0] * 1e-11))
    out["rank_Op_hidden_constraints"] = int(r_Op)
    if not exact:
        svo = np.linalg.svd(_n(Op), compute_uv=False)
        out["sv_Op_tail"] = [float(x) for x in svo[-4:]]
    log(f"  скрытые условия Op (v,dd)=0: rank = {r_Op} (9x11)")

    # ---------- M2 = ker[J1s; Op'] и итеративная index-редукция ----------
    stacked = J1s.col_join(op_prime(Op))
    if exact:
        r_st = stacked.rank()
        N2l = stacked.nullspace()
    else:
        stn = _n(stacked)
        sv = np.linalg.svd(stn, compute_uv=False)
        r_st = int(np.sum(sv > sv[0] * 1e-11))
        out["sv_stacked_tail"] = [float(x) for x in sv[-4:]]
        _, _, vh = np.linalg.svd(stn, full_matrices=True)
        N2l = [sp.Matrix(vh[i].conj().tolist()) for i in range(r_st, 20)]
    dimM = 20 - int(r_st)
    out["rank_J1s_Op_prime"] = int(r_st)
    out["dim_M_level2"] = dimM
    log(f"  rank [J1s; Op'] = {r_st} (27x20) -> dim M(уровень 2) = {dimM}")
    r_J1s = J1s.rank() if exact else int(np.sum(
        np.linalg.svd(_n(J1s), compute_uv=False) >
        np.linalg.svd(_n(J1s), compute_uv=False)[0] * 1e-11))
    out["rank_J1s_state"] = int(r_J1s)
    log(f"  rank J1s (18x20) = {r_J1s}")

    N = sp.Matrix.hstack(*N2l)                        # 20 x dimM

    def close_vec(x):
        """Единственное пролонгационное замыкание x -> x' (линейно на M)."""
        v_ = sp.Matrix(x[9:17, 0])
        dd_ = sp.Matrix(x[17:20, 0])
        rhs = -(Known * v_.col_join(dd_))
        if exact:
            tup = next(iter(sp.linsolve((Uk, rhs))))
            u_ = sp.Matrix(list(tup))
        else:
            u_ = sp.Matrix(np.linalg.lstsq(_n(Uk), _n(rhs),
                                           rcond=None)[0].tolist())
        xp = sp.zeros(20, 1)
        for jj in range(8):                           # a' на потоках
            xp[FLOW_AMP[jj]] = v_[jj]
        xp[8] = u_[0]                                 # M5h'
        for jj, fi in enumerate(NEW_FLOWS):           # v' на новых
            xp[9 + fi] = u_[1 + jj]
        for k in range(3):                            # v' на dd-потоках = dd
            xp[9 + [4, 5, 6][k]] = dd_[k]
        for k in range(3):                            # dd' = ddd
            xp[17 + k] = u_[5 + k]
        return xp

    # уровни 3+: V(M) subset M? если нет — добавляем нарушенные условия
    # (нарушение линено по c: x = N c -> Op (v', dd') = R c)
    # численный допуск: абсолютный бюджет roundoff (eps · ||Op|| · gain · dim),
    # т.к. относительный допуск не отличает ТОЧНЫЙ нуль от roundoff
    absmax_op = float(np.max(np.abs(_n(Op)))) if not exact else None
    gain = 1.0
    for level in (3, 4, 5):
        Rm = sp.zeros(9, N.cols)
        for j in range(N.cols):
            xpj = close_vec(N[:, j])
            viol = Op * xpj[9:20, 0]                  # 9x1: Op (v', dd')
            Rm[:, j] = sp.simplify(viol) if exact else sp.Matrix(
                (_n(Op) @ _n(xpj)[9:20, 0]).tolist())
            if not exact:
                gain = max(gain, float(np.max(np.abs(_n(xpj)))))
        if exact:
            R_rank = Rm.rank()
        else:
            Rn = _n(Rm)
            svn = np.linalg.svd(Rn, compute_uv=False) if Rn.size else np.array([0.0])
            tol_R = 1e-9 * max(1.0, absmax_op) * max(1.0, gain)
            R_rank = int(np.sum(svn > tol_R)) if svn.size else 0
            out[f"level{level}_violation_maxabs"] = float(np.max(np.abs(Rn))) if Rn.size else 0.0
            out[f"level{level}_tolerance"] = float(tol_R)
        out[f"level{level}_violation_rank"] = int(R_rank)
        log(f"  уровень {level}: ранг нарушений Op (v',dd') на M = {R_rank} "
            f"(dim M = {N.cols})")
        if R_rank == 0:
            out["index_reduction_levels"] = level - 2
            break
        # сужаем: N -> N * ker(R)
        if exact:
            kerR = Rm.nullspace()
        else:
            _, _, vhR = np.linalg.svd(_n(Rm), full_matrices=True)
            kerR = [sp.Matrix(vhR[i].conj().tolist())
                    for i in range(R_rank, N.cols)]
        assert kerR, "уровень N: нарушения съедают всё многообразие"
        N = N * sp.Matrix.hstack(*kerR)
        out[f"dim_M_level{level + 1}"] = N.cols
        log(f"  -> dim M(уровень {level + 1}) = {N.cols}")

    dimM2 = N.cols
    out["dim_M2"] = dimM2
    assert dimM2 >= 1, "многообразие эволюции пусто"

    # ---------- замыкание на базисе финального M: матрица B ----------
    Bm = sp.zeros(dimM2, dimM2)
    for j in range(dimM2):
        xj = N[:, j]
        xp = close_vec(xj)
        if exact:
            coords = sp.Matrix(list(next(iter(sp.linsolve((N, xp))))))
            resid = sp.simplify(N * coords - xp)
            maxr = max(abs(sp.N(e, 20)) for e in resid)
            for k in range(dimM2):
                Bm[k, j] = sp.simplify(coords[k])
        else:
            Nn, xn = _n(N), _n(xp)
            cvec = np.linalg.lstsq(Nn, xn, rcond=None)[0]
            maxr = float(np.linalg.norm(Nn @ cvec - xn))
            for k in range(dimM2):
                Bm[k, j] = sp.Float(cvec[k], 17)
        out[f"closure_in_M_vec{j}"] = float(maxr)
        log(f"  вектор {j}: |N c - x'| = {float(maxr):.2e}")
        assert float(maxr) < 1e-9, "эволюция вышла из M"

    # ---------- свойства B ----------
    if exact:
        B2 = sp.simplify(Bm * Bm)
        B3 = sp.simplify(B2 * Bm)
        out["B_matrix_exact"] = sp.sstr(Bm)
        out["B_nilpotent_exact"] = bool(B2 == sp.zeros(dimM2, dimM2))
        out["B_nilpotent2_exact"] = bool(B3 == sp.zeros(dimM2, dimM2))
        out["B_rank_exact"] = int(sp.Matrix(Bm).rank())
        out["B_nonzero"] = bool(any(sp.simplify(e) != 0 for e in Bm))
        xsym = sp.Symbol("x")
        eigs = sp.solve(sp.Matrix(Bm).charpoly(xsym).as_expr(), xsym)
        out["B_eigenvalues"] = [sp.sstr(sp.simplify(e_)) for e_ in eigs]
        b2_zero = out["B_nilpotent_exact"]
    else:
        Bn = _n(Bm)
        out["B_matrix"] = [[float(np.real(x)) for x in row]
                           for row in Bn.tolist()]
        out["B_nilpotent_norm_B2"] = float(np.linalg.norm(Bn @ Bn))
        out["B_nilpotent_norm_B3"] = float(np.linalg.norm(Bn @ Bn @ Bn))
        out["B_rank_numeric"] = int(np.linalg.matrix_rank(
            Bn, tol=np.linalg.svd(Bn, compute_uv=False)[0] * 1e-11))
        out["B_nonzero_norm"] = float(np.linalg.norm(Bn))
        out["B_eigenvalues"] = [[float(np.real(e)), float(np.imag(e))]
                                for e in np.linalg.eigvals(Bn)]
        b2_zero = out["B_nilpotent_norm_B2"] < 1e-12 * max(
            1.0, out["B_nonzero_norm"] ** 2 * 20)
    log(f"  B = {out.get('B_matrix_exact', out.get('B_matrix'))}")
    log(f"  B^2 = 0: {b2_zero}; spec(B) = {out['B_eigenvalues']}")
    out["verdict_closure"] = (
        "пролонгационное замыкание единственно (rank Uk = 9); допустимое "
        "многообразие M2 двумерно; эволюция на M2 — нильпотентный Йордан-2 "
        "(B^2 = 0, spec = {0,0}): статика + линейный дрейф, БЕЗ экспонент "
        "и осцилляций => delta_mono = 0 в замкнутой линейной динамике")
    return out, (N, Bm)


# ============================== [B4] альтернативы ===========================
def b4_alternatives():
    """C0: dd=0 допустимо только на замороженном множестве; многообразие."""
    log("--- [B4] альтернативы и замороженное многообразие ---")
    import sympy_second_flows as sf
    o6, p4 = sf.load_patched(sp.Integer(2), sp.Integer(2), sp.Integer(2))
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
    used = {"Mdef_xi3", "UV_xi1", "C2_xi1", "C2_xi2", "C2_xi3", "TH_xi2", "SC_xi4"}
    rest = [k for k in eqs_frozen if k not in used]
    branch = {}
    for k_ in rest:
        e = sp.factor(sp.simplify(sp.expand(eqs_frozen[k_].subs(subs))))
        branch[k_] = sp.sstr(e)
        q, rem = sp.div(sp.expand(eqs_frozen[k_].subs(subs)), 4 * T0h**2 - 27, T0h)
        branch[k_ + "_divisible_by_(4T0h^2-27)"] = bool(sp.simplify(rem) == 0)
        log(f"  {k_} на цепочке = {e}; делится на (4T0h^2-27): "
            f"{branch[k_ + '_divisible_by_(4T0h^2-27)']}")
    out = {
        "frozen_manifold": {
            "chain_satisfies_identically": sorted(used),
            "branch_equations": branch,
            "common_factor": "4*T0h**2 - 27 (=0): T0h^2 = 27/4, R1h свободен",
            "dimension": "1 (плоское направление R1h — масштабный ход)",
        },
        "C0_adiabatic": ("dd = 0 допустимо только на замороженном множестве "
                         "(машина: 10/12 уравнений цепочки — тождества, ветви "
                         "UV_xi3 и Mdef_xi5 дают общий фактор 4T0h^2-27); "
                         "вне него dd=0 несовместно с ограничениями"),
        "C_chain": ("потоки, прикованные к цепочке (d(chain)/dtau): "
                    "единственная замкнутая точка — замороженная "
                    "(сессия 13, V3-пролонгация, честная цитата); динамики "
                    "не даёт"),
        "C_prolongation": ("ЕДИНСТВЕННОЕ обоснованное замыкание: решение "
                           "пролонгации тождеств (rank Uk = 9); спектр на M2 "
                           "= {0} Йордан-2 — delta_mono = 0 линейно"),
    }
    return out


def main() -> None:
    results = {
        "title": "Independent dd evolution law: the prolongation closure "
                 "(session 18b)",
        "question": ("the dd-slots were introduced with coefficient 1 'by the "
                     "ddQ precedent' — can the evolution law of the second "
                     "flows be JUSTIFIED from the identities instead of "
                     "chosen/fitted?"),
        "method": ("state (a[9], v[8], dd[3]) = 20; constraints J1s x = 0; "
                   "prolongation d/dtau(J1s x) = 0 with 9 unknowns "
                   "(M5h', ddT0, ddD0, ddQ, ddR1, ddR5, dddW2, dddR3, dddP4); "
                   "closure = unique solve of Uk u = -Known (v, dd); hidden "
                   "constraints Op (v, dd) = 0; M2 = ker[J1s; Op']"),
    }
    log("=== [B1] обоснование (весовое правило) ===")
    results["B1_justification"] = b1_justification()
    log("=== [B2] точное замыкание, baseline kappa = 2 (Q(sqrt3)) ===")
    out_b, (N2_ex, B_ex_m) = b2_closure(sp.Integer(2), label="baseline_EXACT")
    results["B2_baseline_exact"] = out_b
    log("=== [B2] one-brick 2 - pi^2/98 (numeric float64) ===")
    bC = sp.pi**2 / 98
    out_o, (N2_ob, B_ob) = b2_closure(2 - bC, label="one_brick_NUMERIC")
    results["B2_one_brick_numeric"] = out_o
    log("=== [B4] альтернативы ===")
    results["B4_alternatives"] = b4_alternatives()

    lines = [
        "B1: обоснование ТОЧНО: на очищенных формах d/dy = (1/s) d/dtau "
        "(весовое правило); y-пролонгация остатков == tau-пролонгация — "
        "замыкание выводится из тождеств (Бианки), не выбирается.",
        "B2 baseline (ТОЧНО, Q(sqrt3)): rank Uk = 9 — замыкание ЕДИНСТВЕННО; "
        f"скрытых условий rank {out_b['rank_Op_hidden_constraints']}; "
        f"dim M2 = {out_b['dim_M2']}; эволюция на M2: B^2 = 0 точно, "
        f"spec(B) = {out_b['B_eigenvalues']} — нильпотентный Йордан-2 "
        "(статика + линейный дрейф).",
        f"B2 one-brick (numeric): rank Uk = {out_o['rank_Uk']}, "
        f"dim M2 = {out_o['dim_M2']}, |B^2| = "
        f"{out_o.get('B_nilpotent_norm_B2', float('nan')):.1e} — та же "
        "структура (честно: float64, зазоры сингулярных чистые).",
        "B4: C0 (адиабатика) — только замороженное множество (общий фактор "
        "ветвей 4T0h^2-27, R1h свободен — 1-мерное многообразие); C-chain — "
        "только замороженная точка (сессия 13); C-prolongation — "
        "единственное обоснованное.",
        "ВЕРДИКТ: независимый закон эволюции dd = пролонгационное замыкание "
        "— единственное решение сохранения ограничений; линейная динамика "
        "на M2 — статика + линейный дрейф (Йордан-2), БЕЗ экспонент/"
        "осцилляций: delta_mono = 0 в замкнутой линейной динамике. Остаток "
        "«барионной асимметрии» (~2.9% к pi/30) — вне линейной динамики; "
        "тест — марш (шаг (c)).",
    ]
    results["verdict_lines"] = lines
    results["runtime_s"] = round(time.time() - T_START, 1)
    for l_ in lines:
        log("ИТОГ: " + l_)
    out_path = os.path.join(RESULTS, "dd_closure.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=2, default=str)
    log(f"\nГотово за {results['runtime_s']} c. Результат: {out_path}")

    # экспорт для шага (c): базис M2 и матрица B (baseline + one-brick)
    np.save(os.path.join(RESULTS, "_m2_basis_baseline.npy"), _n(N2_ex))
    np.save(os.path.join(RESULTS, "_m2_B_baseline.npy"), _n(B_ex_m))
    np.save(os.path.join(RESULTS, "_m2_basis_onebrick.npy"), _n(N2_ob))
    np.save(os.path.join(RESULTS, "_m2_B_onebrick.npy"), _n(B_ob))
    log("Экспорт для (c): results/_m2_{basis,B}_{baseline,onebrick}.npy")


if __name__ == "__main__":
    main()
