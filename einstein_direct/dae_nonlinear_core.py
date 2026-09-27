#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ядро нелинейного марша DAE [сессия 19].

Обобщение пролонгационного замыкания (сессия 18b) на КОНЕЧНУЮ амплитуду.
Нелинейная DAE:
  ограничения   F(x) = 0          — 18 ур. (12 башенных + 6 пролонгационных),
                    x = (a[9], v[8], dd[3]) = 20;
  кинематика    a' = потоки (8 слотов), M5h' свободна;
  пролонгация   dF/dtau = Ja(x) a' + Jv(x) v' + J2(x) dd' = 0  (ЦЕПНОЕ ПРАВИЛО,
                    без линеаризации)  =>
  замыкание     Uk(x) u = -Known(x) (v, dd),
                    Uk(x) = [Ja_{:,M5h} | Jv_{:,{dT0',dD0',Q',dR1',dR5'}} | J2],
                    Known(x) = [Ja_{:,flow} | Jv_{:,{dW2',dR3',dP4'}}],
                    u = (M5h', dT0', dD0', Q', dR1', dR5', dddW2, dddR3, dddP4).
  Та же структура, что в 18b, но с x-зависимыми матрицами — закон выведен тем
  же пролонгационным аргументом (сохранение ограничений), не подогнан.

Совместность замыкания: r(x) = компонента -Known(x)(v,dd), ортогональная
range(Uk(x)) — нелинейный аналог скрытых условий Op(v,dd)=0. Базис левого
ядра Uk выравнивается к опорному (Procrustes) — гладкость для FD-Якобиана.

Проекция: min-norm Ньютон на {F=0} и (чередованием) на {r=0}.
Марш: RK4 (dt=2e-3, как в v14) с замыканием на каждой стадии + проекции.
Стражи: rank Uk < 9, lstsq-невязка, нечисловые значения, покидание окрестности.
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import time
import warnings

import numpy as np
import sympy as sp

warnings.filterwarnings("ignore")
BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)
os.chdir(BASE)

# индексация (согласована с sympy_dd_closure / march_delta_mono)
AMPS = ["T0h", "P2h", "D0h", "R1h", "W2h", "R3h", "P4h", "R5h", "M5h"]
FLOWS = ["dT0", "dD0", "Qh", "dR1", "dW2", "dR3", "dP4", "dR5"]
DDS = ["ddW2", "ddR3", "ddP4"]
FLOW_AMP = [0, 2, 1, 3, 4, 5, 6, 7]   # поток j живёт на амплитуде FLOW_AMP[j]
DD_AMP = [4, 5, 6]                    # dd k живёт на амплитуде DD_AMP[k]
NEW_FLOWS = [0, 1, 2, 3, 7]           # dT0, dD0, Qh, dR1, dR5

DT = 2e-3                              # шаг марша (как в v14)
DELTA_SP = 0.7330382858376652          # эхо (v8, модель B)
STEPS_ECHO = int(round(DELTA_SP / DT))  # 367


class BreakdownError(RuntimeError):
    """Марш вышел за область допустимости (ранг/совместность/численность)."""


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------- построение --
def build_nonlinear_system(kv, validate=True):
    """Символьная система F (18) + ламбдифицированные F, DF + точка x*.

    Возвращает dict с функциями и метаданными. DF(x*) кросс-чекуется с
    точными Ja/Jv/J2 из second_flows_exact.build_exact_system.
    """
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

    tv = sp.simplify(27 / (2 * kv))
    t0v = sp.sqrt(tv)
    point = {T0h: t0v, R1h: sp.Integer(1), D0h: sp.Integer(0)}
    chain = {"R3h": (R3h, r3), "W2h": (W2h, w2), "P2h": (P2h, p2),
             "R5h": (R5h, r5), "M5h": (M5h, m5), "P4h": (P4h, p4v)}
    for k_, (sym_, form) in chain.items():
        point[sym_] = sp.simplify(sp.expand(form).subs(T0h, t0v).subs(R1h, 1))
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
    assert len(F) == 18, f"F: {len(F)} != 18"

    amps = [T0h, P2h, D0h, R1h, W2h, R3h, P4h, R5h, M5h]
    flows = [p4.dT0, p4.dD0, p4.Qh, p4.dR1, p4.dW2, p4.dR3, p4.dP4, p4.dR5]
    vars20 = amps + flows + list(dds)
    DF = sp.Matrix(len(F), 20, lambda i_, j_: sp.diff(F[i_], vars20[j_]))
    F_fun = sp.lambdify(vars20, F, "numpy")
    DF_fun = sp.lambdify(vars20, DF.tolist(), "numpy")
    x_star = np.array([float(sp.N(point[v], 25)) for v in vars20])

    out = {
        "kappa": float(sp.N(kv, 15)), "tau_star": float(sp.N(tv, 20)),
        "F_fun": F_fun, "DF_fun": DF_fun, "x_star": x_star,
        "vars": [sp.sstr(v_) for v_ in vars20],
        "chain_symbolic": {k_: sp.sstr(v_[1]) for k_, v_ in chain.items()},
        "n_eqs_live": len(eqs_live), "n_prolong": len(prolong),
    }

    # невязка в точке
    Fv = np.array(F_fun(*x_star), dtype=float).reshape(18)
    out["residual_at_point"] = float(np.max(np.abs(Fv)))

    if validate:
        import second_flows_exact as sfe
        A_ex, B_ex, C_ex, _, _ = sfe.build_exact_system(kv)
        Ja_ex = np.array(A_ex.evalf(20).tolist(), dtype=complex)
        JvP = np.array(B_ex.evalf(20).tolist(), dtype=complex)
        J2P2 = np.array(C_ex.evalf(20).tolist(), dtype=complex)
        Jv_ex = np.zeros((18, 8), dtype=complex)
        for j in range(8):
            Jv_ex[:, j] = JvP[:, FLOW_AMP[j]]
        J2_ex = np.zeros((18, 3), dtype=complex)
        for k in range(3):
            J2_ex[:, k] = J2P2[:, DD_AMP[k]]
        Dm = np.array(DF_fun(*x_star), dtype=complex).reshape(18, 20)

        def relerr(a, b):
            d = float(np.max(np.abs(a - b)))
            s = max(float(np.max(np.abs(a))), float(np.max(np.abs(b))), 1e-300)
            return d / s

        out["crosscheck_rel"] = {
            "Ja": relerr(Dm[:, :9], Ja_ex),
            "Jv": relerr(Dm[:, 9:17], Jv_ex),
            "J2": relerr(Dm[:, 17:20], J2_ex),
        }
        sv = np.linalg.svd(Dm, compute_uv=False)
        out["rank_DF_at_point"] = int(np.sum(sv > sv[0] * 1e-11))
        # опорный базис левого ядра Uk(x*) для выравнивания
        Uk0 = _uk_of(Dm)
        u_, s_, _ = np.linalg.svd(Uk0, full_matrices=True)
        out["W_ref"] = np.ascontiguousarray(u_[:, 9:].conj().T)   # 9x18
        out["rank_Uk_at_point"] = int(np.sum(s_ > s_[0] * 1e-11))
    return out


def _uk_known(Dm):
    """Срез матриц замыкания из полного якобиана DF (18x20)."""
    Ja = Dm[:, :9]
    Jv = Dm[:, 9:17]
    J2 = Dm[:, 17:20]
    Uk = np.hstack([Ja[:, [8]], Jv[:, NEW_FLOWS], J2])          # 18x9
    Known = np.hstack([Ja[:, FLOW_AMP], Jv[:, [4, 5, 6]]])      # 18x11
    return Uk, Known


def _uk_of(Dm):
    return _uk_known(Dm)[0]


def assemble_V(x, u):
    """Скорость x' = (потоки | M5h' | v' | dd') в состоянии (20)."""
    v = x[9:17]
    dd = x[17:20]
    V = np.zeros(20)
    for j in range(8):
        V[FLOW_AMP[j]] = v[j]
    V[8] = u[0]
    for j, fi in enumerate(NEW_FLOWS):
        V[9 + fi] = u[1 + j]
    for k in range(3):
        V[9 + [4, 5, 6][k]] = dd[k]
    for k in range(3):
        V[17 + k] = u[5 + k]
    return V


# -------------------------------------------------------------------- DAE ----
class NonlinearDAE:
    """Нелинейная DAE башни: замыкание, проекции, марш, мониторинг."""

    def __init__(self, sysd, r_align_tol=1e-6):
        self.F_fun = sysd["F_fun"]
        self.DF_fun = sysd["DF_fun"]
        self.x_star = sysd["x_star"]
        self.W_ref = sysd.get("W_ref")
        self.W_align = sysd.get("W_ref")   # продолжение базиса левого ядра
        self.scale = float(np.max(np.abs(self.x_star)))
        self.align_tol = r_align_tol
        self.stats = {"n_closure": 0, "n_rank_drop": 0, "max_solv_res": 0.0,
                      "min_rank": 9, "max_align_err": 0.0}

    # ---------------- базовые оценки ----------------
    def eval_F(self, x):
        Fv = np.array(self.F_fun(*x), dtype=float).reshape(18)
        if not np.all(np.isfinite(Fv)):
            raise BreakdownError("F нечисловое")
        return Fv

    def eval_DF(self, x):
        Dm = np.array(self.DF_fun(*x), dtype=float).reshape(18, 20)
        if not np.all(np.isfinite(Dm)):
            raise BreakdownError("DF нечисловое")
        return Dm

    def closure(self, x):
        """Замыкание: u из Uk(x) u = -Known(x)(v,dd); скорость + диагностика."""
        Dm = self.eval_DF(x)
        Uk, Known = _uk_known(Dm)
        z = np.concatenate([x[9:17], x[17:20]])
        rhs = -(Known @ z)
        u, _, rank, sv = np.linalg.lstsq(Uk, rhs, rcond=None)
        solv_res = float(np.linalg.norm(Uk @ u - rhs))
        self.stats["n_closure"] += 1
        self.stats["min_rank"] = min(self.stats["min_rank"], int(rank))
        self.stats["max_solv_res"] = max(self.stats["max_solv_res"], solv_res)
        if rank < 9:
            self.stats["n_rank_drop"] += 1
            raise BreakdownError(f"rank Uk = {rank} < 9 (замыкание не единственно)")
        if solv_res > 1e-6 * max(1.0, float(np.linalg.norm(rhs))):
            raise BreakdownError(f"несовместность замыкания: |r| = {solv_res:.2e}")
        return assemble_V(x, u), {"rank": int(rank), "solv_res": solv_res,
                                  "sv_min_Uk": float(sv[-1])}

    @staticmethod
    def _kernel_res(Uk, rhs, target):
        """lstsq-решение + res18 (ортогонален range(Uk)) + выровненный базис
        левого ядра (Procrustes к target, если задан). |r| базис-инвариантен;
        выравнивание нужно только для гладкости FD-Якобиана rvec."""
        u, _, rank, sv = np.linalg.lstsq(Uk, rhs, rcond=None)
        res18 = Uk @ u - rhs
        u_, s_, _ = np.linalg.svd(Uk, full_matrices=True)
        W = np.ascontiguousarray(u_[:, 9:].conj().T)     # 9x18, строки ортонорм.
        align_err = 0.0
        if target is not None:
            M = W @ target.T                             # 9x9
            Um, _, Vmt = np.linalg.svd(M)
            Q = Vmt.T @ Um.T                             # max tr(Q M)
            W = Q @ W
            align_err = float(np.linalg.norm(W - target))
        return res18, W, align_err, sv

    def rvec(self, x, target=None):
        """Вектор совместимости r (9): компонента rhs вне range(Uk(x)).

        target=None: продолжение (выравнивание к предыдущему базису —
        мониторинг угла); target=W0: замороженный локальный базис (для FD).
        Норма |r| базис-инвариантна.
        """
        Dm = self.eval_DF(x)
        Uk, Known = _uk_known(Dm)
        z = np.concatenate([x[9:17], x[17:20]])
        rhs = -(Known @ z)
        tgt = self.W_align if target is None else target
        res18, W, align_err, sv = self._kernel_res(Uk, rhs, tgt)
        if target is None:
            self.W_align = W
        self.stats["max_align_err"] = max(self.stats["max_align_err"],
                                          align_err)
        return W @ res18, {"align_err": align_err,
                           "sv_min_Uk": float(sv[-1])}

    # ---------------- проекции ----------------
    def project_F(self, x, iters=3, tol=1e-12):
        x = x.copy()
        rep = {"F_max": 0.0}
        for _ in range(iters):
            Fv = self.eval_F(x)
            rep["F_max"] = float(np.max(np.abs(Fv)))
            if rep["F_max"] < tol:
                break
            dx, *_ = np.linalg.lstsq(self.eval_DF(x), -Fv, rcond=None)
            x = x + dx
        rep["F_max"] = float(np.max(np.abs(self.eval_F(x))))
        return x, rep

    def _r_jacobian(self, x, eps=1e-7):
        """FD-Якобиан rvec в ЗАМОРОЖЕННОМ локальном базисе (target = базис в x)."""
        n = len(x)
        r0, _ = self.rvec(x)
        W0 = self.W_align.copy()
        Dr = np.zeros((9, n))
        for j in range(n):
            xp = x.copy()
            step = eps * max(1.0, abs(x[j]))
            xp[j] += step
            rp, _ = self.rvec(xp, target=W0)
            Dr[:, j] = (rp - r0) / step
        return Dr, r0

    def project_r(self, x, iters=3, tol=1e-12):
        x = x.copy()
        rep = {"r_max": 0.0}
        for _ in range(iters):
            rv, _ = self.rvec(x)
            rep["r_max"] = float(np.max(np.abs(rv)))
            if rep["r_max"] < tol:
                break
            Dr, _ = self._r_jacobian(x)
            dx, *_ = np.linalg.lstsq(Dr, -rv, rcond=None)
            nrm = float(np.linalg.norm(dx))
            if nrm > 0.5 * self.scale:            # страж шага
                dx *= 0.5 * self.scale / nrm
            x = x + dx
        rv, _ = self.rvec(x)
        rep["r_max"] = float(np.max(np.abs(rv)))
        return x, rep

    def project_Fr(self, x, rounds=4):
        """Чередующая проекция на {F=0} и {r=0} (min-norm Ньютон)."""
        x = x.copy()
        rep = {"F_max": None, "r_max": None}
        for _ in range(rounds):
            x, rf = self.project_F(x, iters=3)
            x, rr = self.project_r(x, iters=3)
        x, rf = self.project_F(x, iters=3)
        rv, _ = self.rvec(x)
        rep["F_max"], rep["r_max"] = rf["F_max"], float(np.max(np.abs(rv)))
        return x, rep

    # ---------------- марш ----------------
    def rk4_step(self, x, dt):
        k1, d1 = self.closure(x)
        k2, d2 = self.closure(x + 0.5 * dt * k1)
        k3, d3 = self.closure(x + 0.5 * dt * k2)
        k4, d4 = self.closure(x + dt * k3)
        xn = x + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
        diag = {"solv_res": max(d1["solv_res"], d2["solv_res"],
                                d3["solv_res"], d4["solv_res"]),
                "sv_min_Uk": min(d1["sv_min_Uk"], d4["sv_min_Uk"])}
        return xn, diag

    def march(self, x0, n_echoes, proj_every=25, project_fr_every_echo=True,
              record_all=False, blowup_factor=12.0):
        """Марш n_echoes эхов; запись на границах эхов + мониторинг."""
        dt = DT
        nst = STEPS_ECHO
        x = x0.copy()
        traj = [] if record_all else None
        states = []
        rows = []
        m = {"F_drift_max": 0.0, "proj_corr_max": 0.0, "solv_res_max": 0.0,
             "sv_min_Uk_min": np.inf, "blowup_at": None, "breakdown": None}
        try:
            for echo in range(n_echoes + 1):
                Fv = self.eval_F(x)
                rv, _ = self.rvec(x)
                states.append(x.copy())
                rows.append({
                    "echo": echo, "t": echo * nst * dt,
                    "dist": float(np.linalg.norm(x - self.x_star)),
                    "F_max": float(np.max(np.abs(Fv))),
                    "r_max": float(np.max(np.abs(rv))),
                    "norm_x": float(np.linalg.norm(x)),
                })
                if record_all:
                    traj.append(x.copy())
                if echo == n_echoes:
                    break
                for step in range(nst):
                    x_new, diag = self.rk4_step(x, dt)
                    m["solv_res_max"] = max(m["solv_res_max"],
                                            diag["solv_res"])
                    m["sv_min_Uk_min"] = min(m["sv_min_Uk_min"],
                                             diag["sv_min_Uk"])
                    if (step + 1) % proj_every == 0:
                        Fpre = float(np.max(np.abs(self.eval_F(x_new))))
                        m["F_drift_max"] = max(m["F_drift_max"], Fpre)
                        x_new, _ = self.project_F(x_new, iters=2)
                    x = x_new
                    if float(np.linalg.norm(x - self.x_star)) > \
                            blowup_factor * self.scale:
                        m["blowup_at"] = (echo * nst + step + 1) * dt
                        raise BreakdownError(
                            f"покидание окрестности: |x-x*| > "
                            f"{blowup_factor}*|x*| при t = {m['blowup_at']:.3f}")
                if project_fr_every_echo:
                    x, _ = self.project_Fr(x, rounds=2)
        except BreakdownError as ex:
            m["breakdown"] = str(ex)
        m["solv_res_max"] = float(m["solv_res_max"])
        m["sv_min_Uk_min"] = (float(m["sv_min_Uk_min"])
                              if np.isfinite(m["sv_min_Uk_min"]) else None)
        return {"rows": rows, "traj": traj, "states": states,
                "monitors": m, "x_end": x}

    # ---------------- начальные данные ----------------
    def initial_condition(self, direction, A, probe_echoes=1, beta_rounds=2):
        """Допустимые начальные данные конечной амплитуды.

        x_try = x* + A*|x*|_inf * w_hat; чередующая проекция {F=0}+{r=0};
        пробный марш: рост r -> градиентная коррекция вдоль прочих касательных
        ядра [DF; Dr] (нелинейный аналог условия уровня 3, сессия 18b).
        """
        w = np.asarray(direction, dtype=float)
        nw = float(np.max(np.abs(w)))
        if nw < 1e-300:
            raise ValueError("нулевое направление")
        w = w / nw

        def probe(beta_vec):
            xb, repb = self.project_Fr(
                self.x_star + A * self.scale * w + beta_vec, rounds=3)
            pb = self.march(xb, probe_echoes)
            return pb["rows"][-1]["r_max"], xb, repb

        beta = np.zeros(20)
        r_end, x0, rep = probe(beta)
        rep0 = dict(rep)
        r0 = rep0["r_max"]
        betas_applied = []
        if r_end > max(10.0 * max(r0, 1e-15), 1e-9):
            # касательные ядра [DF; Dr] (уровень 2, dim ~3), исключая w
            Dr, _ = self._r_jacobian(x0)
            Dm = self.eval_DF(x0)
            st = np.vstack([Dm, Dr])
            _, sv, vt = np.linalg.svd(st)
            rk = int(np.sum(sv > sv[0] * 1e-11))
            ker = vt[rk:]
            cand = [k / float(np.max(np.abs(k))) for k in ker
                    if abs(float(k @ w)) < 0.99]
            eps_b = 0.05 * A * self.scale
            for _ in range(beta_rounds):
                if not cand:
                    break
                # градиент J = r_end^2 по beta-коэффициентам вдоль cand
                grad = []
                for t in cand:
                    rp, _, _ = probe(beta + eps_b * t)
                    rm, _, _ = probe(beta - eps_b * t)
                    grad.append((rp ** 2 - rm ** 2) / (2 * eps_b))
                gvec = sum(g_ * t_ for g_, t_ in zip(grad, cand))
                gn = float(np.linalg.norm(gvec))
                if gn < 1e-300:
                    break
                # шаг против градиента: секущая вдоль -gvec
                d = -gvec / gn
                h_sec = 0.05 * A * self.scale
                rp, _, _ = probe(beta + h_sec * d)
                slope = (rp ** 2 - r_end ** 2) / h_sec
                step_len = (-r_end ** 2 / slope) if abs(slope) > 1e-300 else 0.0
                step_len = float(np.clip(step_len, -0.3 * A * self.scale,
                                         0.3 * A * self.scale))
                beta = beta + step_len * d
                betas_applied.append(float(np.linalg.norm(beta)))
                r_end, x0, rep = probe(beta)
                if r_end <= max(10.0 * max(rep["r_max"], 1e-15), 1e-9):
                    break
        return {
            "x0": x0, "direction": w, "A": A,
            "F_max": rep["F_max"], "r_max": rep["r_max"],
            "r0_probe": r0, "r_end_probe": r_end,
            "beta_norm": betas_applied[-1] if betas_applied else 0.0,
            "beta_history": betas_applied,
            "probe_breakdown": None,
        }

    # ---------------- совместный Ньютон [F; r] ----------------
    def joint_newton(self, x0, iters=80, tol=1e-13):
        """Миннормальный Гаусс-Ньютон на G = [F; r] (27 ур.)."""
        x = x0.copy()
        gmax = np.inf
        used = 0
        for used in range(1, iters + 1):
            G = np.concatenate([self.eval_F(x), self.rvec(x)[0]])
            gmax = float(np.max(np.abs(G)))
            if gmax < tol:
                break
            Jj = np.vstack([self.eval_DF(x), self._r_jacobian(x)[0]])
            dx, *_ = np.linalg.lstsq(Jj, -G, rcond=None)
            x = x + dx
        return x, gmax, used

    def coker_split(self):
        """Кокоядро DG(x*) и декомпозиция рангов (для теста ветвей)."""
        DG0 = np.vstack([self.eval_DF(self.x_star),
                         self._r_jacobian(self.x_star)[0]])
        u_, s_, _ = np.linalg.svd(DG0, full_matrices=True)
        rk = int(np.sum(s_ > s_[0] * 1e-11))
        Wc = np.ascontiguousarray(u_[:, rk:].conj().T)      # (27-rk) x 27
        return DG0, Wc, rk

    def branch_ratio(self, t, h, Wc):
        """|P_coker G(x*+h t)| / |G(x*+h t)| и раздельно по блокам F/r."""
        xt = self.x_star + h * np.asarray(t, dtype=float)
        Fv = self.eval_F(xt)
        rv, _ = self.rvec(xt)
        G = np.concatenate([Fv, rv])
        GF = np.concatenate([Fv, np.zeros_like(rv)])
        GR = np.concatenate([np.zeros_like(Fv), rv])
        n = max(float(np.linalg.norm(G)), 1e-300)
        return {"ratio": float(np.linalg.norm(Wc @ G) / n),
                "ratio_F": float(np.linalg.norm(Wc @ GF) /
                                 max(np.linalg.norm(Fv), 1e-300)),
                "ratio_r": float(np.linalg.norm(Wc @ GR) /
                                 max(np.linalg.norm(rv), 1e-300)),
                "G_abs": float(n)}

    # ---------------- пропагатор ----------------
    def propagator(self, x0, basis, h=None, n_echoes=1):
        """Конечнo-амплитудный пропагатор центральными разностями.

        basis: 20x2 (колонки — входные касательные направления).
        Возвращает 2x2 Pi в координатах basis (МНК-отображение измеренных
        входных хорд в измеренные выходные хорды).
        """
        scale = self.scale
        if h is None:
            A_eff = float(np.linalg.norm(x0 - self.x_star)) / scale
            h = max(1e-7, 1e-3 * A_eff * scale)
        base = self.march(x0, n_echoes)
        x_end = base["x_end"]
        if base["monitors"]["breakdown"]:
            raise BreakdownError("базовый марш пропагатора: "
                                 + base["monitors"]["breakdown"])
        In, Out = [], []
        for j in range(basis.shape[1]):
            xi = np.asarray(basis[:, j], dtype=float)
            xi = xi / float(np.max(np.abs(xi)))
            xp, repp = self.project_Fr(x0 + h * xi, rounds=3)
            xm, repm = self.project_Fr(x0 - h * xi, rounds=3)
            dp, dm = xp - x0, xm - x0
            op = self.march(xp, n_echoes)
            om = self.march(xm, n_echoes)
            if op["monitors"]["breakdown"] or om["monitors"]["breakdown"]:
                raise BreakdownError("марш возмущения пропагатора: "
                                     + str(op["monitors"]["breakdown"]
                                           or om["monitors"]["breakdown"]))
            opo, omo = op["x_end"] - x_end, om["x_end"] - x_end
            In.append(dp - dm)
            Out.append(opo - omo)
        In = np.array(In).T          # 20x2: измеренные входные хорды
        Out = np.array(Out).T        # 20x2: выходные хорды
        Pin = np.linalg.pinv(In)     # 2x20
        Pi = Pin @ Out               # 2x2: Out ~ In @ Pi^T => Pi = In^+ Out
        return {"Pi": Pi, "h": h,
                "input_chord_norms": [float(np.linalg.norm(In[:, j]))
                                      for j in range(2)],
                "eig": [complex(e) for e in np.linalg.eigvals(Pi)],
                "Pi_lin_ref": None}
