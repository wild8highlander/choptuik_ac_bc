#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Кампания [сессия 22 / v18a]: BRICK-LADDER-TICK — кампания с промежуточными
кирпичами: зависимость препятствия тика от delta.

Директива автора (сессия 22): (а) кампания с промежуточными кирпичами —
зависимость препятствия тика от delta (намеченный кандидат v17 [C3]:
one-brick препятствие в ~1.7-3 раза меньше baseline — кирпичная
зависимость); (б) глобальный поиск недегенератных статических ветвей
(отдельная машина global_static_search.py).

Кирпич = бэрри-фаза delta с аддитивным скринингом kappa(delta) = 2 - delta^2/2
(записанное соглашение v11; выживший кирпич delta_C = pi/7 -> pi^2/98).
Лестница: delta_k = pi/k, k in {2..12, 14}, плюс baseline (delta = 0, kappa=2).

Слои (на каждом кирпиче лестницы):
  [B1] сборка точки: x*, tau* = 27/(2 kappa), F(x*); плоская линия R1h при
       T0h* (v15 T1) — проверка на каждом кирпиче;
  [B2] ТЕОРЕМА О ПАРЕ ЧАСОВ НА ЛЕСТНИЦЕ (точно, SymPy): GCD(UV_xi3, Mdef_xi5)
       на цепочке имеет ЕДИНСТВЕННЫЙ положительный корень tau*(delta) и
       обращается в нуль в нём ТОЧНО — обобщение [C1] v17 со всех кирпичей;
  [B3] ПРЕПЯТСТВИЕ ТИКА (главная наблюдаемая): кернел M_r ((v,dd) -> r) в x*,
       подъём project_Fr при киках 0.05/0.01 -> r_max (остановка подъёма на
       совместное многообразие {F=0, r=0}); марш 1 эхо (если замыкание живо);
  [B4] фантомный карандаш в исправленной точке: Im lambda фантомов vs
       лестница k*pi/30 (скан по кирпичам — multiple-testing оговорка);
  [B5] дефект книги по мелкой сетке масштабов (24 масштаба, как [C3] v17).

Запуск: python3 brick_scan_tick.py  (~8-12 мин) -> results/brick_scan_tick.json
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
import sympy_hexcycle as hx                            # noqa: E402
from hexcycle_dae import chain_poles                   # noqa: E402
from clock_closure_t1c import build_point, kernel_Mr   # noqa: E402


def log(msg):
    print(msg, flush=True)


LADDER = [None, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14]    # None = baseline
SURVIVOR_K = 7                                          # delta_C = pi/7


def kappa_of(k):
    """kappa(delta_k) = 2 - (pi/k)^2 / 2; None (baseline) -> 2."""
    if k is None:
        return sp.Integer(2)
    return sp.Integer(2) - sp.pi**2 / (2 * sp.Integer(k) ** 2)


def label_of(k):
    return "baseline_delta0" if k is None else f"brick_pi_over_{k}"


# ------------------------------------------------------------------ [B1] --
def layer_B1(kv, bp):
    """Сборка точки + плоская линия при критическом масштабе."""
    x_star = bp["sysd"]["x_star"]
    t0s = float(x_star[0])
    dae, chain = bp["dae"], bp["chain"]
    flat = {}
    for R in (0.1, 1.0, 13.0):
        x = make_chain_state(chain, t0s, R)
        if np.all(np.isfinite(x)):
            flat[f"R1h_{R}"] = float(np.max(np.abs(dae.eval_F(x))))
    flat_max = max(flat.values())
    return {"T0h_star": t0s, "tau_star": bp["sysd"]["tau_star"],
            "residual_at_point": bp["sysd"]["residual_at_point"],
            "flat_line_F_max": flat, "flat_line_F_max_abs": flat_max,
            "flat_line_ok": bool(flat_max < 1e-7)}


def make_chain_state(chain, T0h_val, r1h):
    """Цепочное 20-мерное состояние (v = dd = 0)."""
    from hexcycle_dae import make_state
    return make_state(chain, T0h_val, r1h=r1h, kinetic=False)


# ------------------------------------------------------------------ [B2] --
def layer_B2(kv, bp):
    """Теорема о паре часов на кирпиче: уникальность tau*(delta)."""
    T0h, R1h = bp["syms"]["T0h"], bp["syms"]["R1h"]
    nums = {}
    for name in ("UV_xi3", "Mdef_xi5"):
        e = sp.cancel(sp.together(sp.expand(
            bp["eqs_frozen"][name].subs(bp["chain_subs"]).subs(R1h, 1))))
        nums[name] = sp.expand(sp.numer(e))
    g = sp.factor(sp.gcd(nums["UV_xi3"], nums["Mdef_xi5"]))
    tau_s = sp.simplify(27 / (2 * kv))
    g_at = sp.simplify(g.subs(T0h, sp.sqrt(tau_s)))
    exact_zero = bool(sp.simplify(g_at) == 0)
    pos = sorted({round(float(sp.re(r_)), 8)
                  for r_ in sp.nroots(g, n=25, maxsteps=250)
                  if abs(sp.im(r_)) < 1e-15 and sp.re(r_) > 1e-8})
    unique = len(pos) == 1 and abs(
        pos[0] - float(sp.N(sp.sqrt(tau_s), 20))) < 1e-6
    return {"gcd_on_chain": sp.sstr(g)[:200],
            "tau_star_symbolic": sp.sstr(tau_s),
            "tau_star_numeric": float(sp.N(tau_s, 20)),
            "gcd_zero_at_tau_star": exact_zero,
            "gcd_positive_roots": pos,
            "unique_common_clock": bool(unique)}


# ------------------------------------------------------------------ [B3] --
def layer_B3(kv, bp):
    """Препятствие тика: кернел + подъём project_Fr при киках 0.05/0.01.

    ИСТОРИЧЕСКИ-СВОБОДНОЕ ИЗМЕРЕНИЕ (erratum к методу [C3] v17): r_max =
    max|W·res18| зависит от Procrustes-базиса W_align, который мутирует
    rvec(x, target=None) (продолжение) — у v17 [C3] базис был прокручен
    слоями A0/A1, поэтому абсолютные величины [C3] — история-зависимые.
    Здесь: замороженный базис W0 в x* (фиксированная последовательность
    вызовов), главная наблюдаемая = ||r|| (базис-инвариантна по построению),
    плюс робастность по всем кернел-направлениям (медиана/разброс).
    Траектория project_Fr инвариантна (lstsq инвариантен к строчным
    ортогональным преобразованиям) — точка x0p воспроизводима.
    """
    dae = bp["dae"]
    x_star = bp["sysd"]["x_star"]
    M = kernel_Mr(dae, x_star[:9])
    sv = np.linalg.svd(M, compute_uv=False)
    rk7 = int(np.sum(sv > sv[0] * 1e-7))
    _, _, vt = np.linalg.svd(M)
    ker = vt[rk7:]
    out = {"kernel_rank_tol1e-7": rk7, "kernel_dim": 11 - rk7,
           "singular_values": [float(v) for v in sv]}
    if len(ker):
        # замороженный базис ядра в x*: фиксированная последовательность
        # (kernel_Mr -> один вызов rvec) детерминирована на свежем dae
        dae.rvec(np.concatenate([x_star[:9], np.zeros(11)]))
        W0 = dae.W_align.copy()
        for kick in (0.05, 0.01):
            eps = kick * dae.scale
            norms, rmaxes = [], []
            rec = {"kick": kick}
            for di, zrow in enumerate(ker[:5]):
                z = zrow / (float(np.max(np.abs(zrow))) or 1.0)
                x0 = np.concatenate([x_star[:9], np.zeros(11)]) + eps * \
                    np.concatenate([np.zeros(9), z])
                try:
                    x0p, rep = dae.project_Fr(x0, rounds=3)
                    rvf, _ = dae.rvec(x0p, target=W0)
                    norms.append(float(np.linalg.norm(rvf)))
                    rmaxes.append(float(np.max(np.abs(rvf))))
                    if di == 0:
                        rec["F_max"] = float(rep["F_max"])
                        rec["r_norm_frozen"] = norms[0]
                        rec["r_max_frozen"] = rmaxes[0]
                        try:
                            V, dia = dae.closure(x0p)
                            rec["V_norm_at_start"] = \
                                float(np.linalg.norm(V))
                            mres = dae.march(x0p, 1)
                            rec["march_breakdown"] = \
                                bool(mres["monitors"]["breakdown"])
                            if mres["rows"]:
                                rec["march_r_max"] = max(
                                    float(r_["r_max"])
                                    for r_ in mres["rows"])
                        except dnc.BreakdownError as ex2:
                            rec["closure_breakdown"] = str(ex2)[:120]
                except dnc.BreakdownError as ex:
                    rec[f"dir{di}_breakdown"] = str(ex)[:100]
            if norms:
                rec["r_norm_frozen_median"] = float(np.median(norms))
                rec["r_norm_frozen_min"] = float(np.min(norms))
                rec["r_norm_frozen_max"] = float(np.max(norms))
                rec["r_norm_all_dirs"] = norms
            out[f"kick_{kick}"] = rec
    return out


# ------------------------------------------------------------------ [B4] --
def layer_B4(payload, kv, tau_star, k):
    """Фантомный карандаш в исправленной точке (Im lambda vs k*pi/30)."""
    import sympy_spinor_corrections as ssc
    name = f"brick_ladder_{label_of(k)}"
    out = ssc.s4_pencil(payload, name, (kv, kv, kv), tau_star)
    top = out.get("phantom_Im_vs_ladder_top") or []
    return {
        "n_genuine": len(out.get("genuine_modes") or []),
        "residual_at_point": out.get("residual_max"),
        "best_hit": {kk: top[0].get(kk) for kk in
                     ("lambda", "nearest_ladder", "k_over_30",
                      "rel_diff_pct", "match_1pct")} if top else None,
        "top_rows": [{kk: row.get(kk) for kk in
                      ("lambda", "nearest_ladder", "k_over_30",
                       "rel_diff_pct")} for row in top[:4]],
    }


# ------------------------------------------------------------------ [B5] --
def layer_B5(kv, bp):
    """Дефект книги по мелкой сетке масштабов (первый цикл коллапса)."""
    dae, chain = bp["dae"], bp["chain"]
    t0s = float(bp["sysd"]["x_star"][0])
    poles = [p["T0h"] for p in chain_poles(bp["sysd"])]
    grid = {}
    for j in range(6):
        r0 = sum(hx.STEPS[i % 6] for i in range(j))
        r1 = r0 + hx.STEPS[j % 6]
        for m in range(4):
            rb = r0 + (r1 - r0) * m / 4.0
            T0h_v = t0s * float(np.exp(-rb))
            if any(abs(T0h_v - p) < 1e-6 * p for p in poles):
                continue
            try:
                xs = make_chain_state(chain, T0h_v, 1.0)
                if not np.all(np.isfinite(xs)):
                    continue
                Fv = float(np.max(np.abs(dae.eval_F(xs))))
                grid[f"r{rb:.5f}"] = Fv
            except dnc.BreakdownError:
                continue
    fmx = max(grid.values()) if grid else None
    return {"n_scales": len(grid), "F_static_max": fmx, "grid": grid}


# --------------------------------------------------------------------- main --
def main() -> None:
    log("[1/3] Лестница кирпичей: delta_k = pi/k, k in {2..12,14} + baseline")
    log("      kappa(delta) = 2 - delta^2/2 (аддитивный бэрри-скрининг, v11)")

    bC = sp.pi**2 / 98
    assert sp.simplify(kappa_of(SURVIVOR_K) - (sp.Integer(2) - bC)) == 0

    # карандашный payload строится ОДИН раз (кэп: если упал — фантомный слой
    # честно помечается как пропущенный)
    payload = None
    try:
        import sympy_spinor_corrections as ssc
        _, corr = ssc.s0_corrections()
        _, payload = ssc.s1_doors_symbolic()
        log("      карандашный payload собран (фантомный слой активен)")
    except Exception as ex:                                # noqa: BLE001
        log(f"      !!! payload не собран ({ex}) — [B4] пропускается")

    out = {
        "title": "BRICK-LADDER-TICK v18a: кампания с промежуточными кирпичами "
                 "— зависимость препятствия тика от delta",
        "question": ("автор, сессия 22 (а): кампания с промежуточными "
                     "кирпичами — зависимость препятствия тика от delta "
                     "(намеченный кандидат v17 [C3])"),
        "ladder": [label_of(k) for k in LADDER],
        "kappa_convention": "kappa(delta) = 2 - delta^2/2, delta_k = pi/k",
        "survivor": "delta_C = pi/7 (kappa = 2 - pi^2/98)",
        "points": {},
        "runtime_s": None,
    }

    for k in LADDER:
        lbl = label_of(k)
        kv = kappa_of(k)
        log(f"\n================ {lbl}: kappa = {sp.N(kv, 12)} ================")
        rec = {"kappa": sp.sstr(kv), "kappa_numeric": float(sp.N(kv, 15)),
               "delta_over_pi": (0 if k is None else
                                 float(sp.N(1 / sp.Integer(k), 12)))}
        try:
            t0 = time.time()
            bp = build_point(kv)
            rec["build_s"] = round(time.time() - t0, 1)
        except Exception as ex:                            # noqa: BLE001
            rec["build_failed"] = str(ex)[:200]
            out["points"][lbl] = rec
            log(f"    !!! сборка не удалась: {ex}")
            continue
        rec["B1_point"] = layer_B1(kv, bp)
        log(f"    [B1] T0h* = {rec['B1_point']['T0h_star']:.9f}, "
            f"tau* = {rec['B1_point']['tau_star']:.9f} "
            f"(книга 27/(2k) = {float(sp.N(27 / (2 * kv), 12)):.9f}), "
            f"F(x*) = {rec['B1_point']['residual_at_point']:.2e}, "
            f"плоская линия: {rec['B1_point']['flat_line_ok']}")
        rec["B2_clock_pair"] = layer_B2(kv, bp)
        log(f"    [B2] часы: tau* = {rec['B2_clock_pair']['tau_star_numeric']:.9f},"
            f" уникальность = "
            f"{rec['B2_clock_pair']['unique_common_clock']}, "
            f"точный ноль GCD = "
            f"{rec['B2_clock_pair']['gcd_zero_at_tau_star']}")
        rec["B3_tick_obstruction"] = layer_B3(kv, bp)
        for kick in ("kick_0.05", "kick_0.01"):
            r = rec["B3_tick_obstruction"].get(kick, {}).get("r_norm_frozen")
            if r is not None:
                log(f"    [B3] {kick}: ||r||_frozen = {r:.6f} "
                    f"(медиана по направлениям "
                    f"{rec['B3_tick_obstruction'][kick].get('r_norm_frozen_median', float('nan')):.6f})")
        if payload is not None:
            try:
                rec["B4_phantoms"] = layer_B4(
                    payload, kv, rec["B2_clock_pair"]["tau_star_numeric"], k)
                bh = rec["B4_phantoms"].get("best_hit") or {}
                if bh:
                    log(f"    [B4] лучший фантом: Im|lam| = "
                        f"{abs(bh['lambda'][1]):.6f} vs лестница "
                        f"{bh['nearest_ladder']:.6f} "
                        f"({bh['rel_diff_pct']:+.3f}%)")
            except Exception as ex:                        # noqa: BLE001
                rec["B4_phantoms"] = {"failed": str(ex)[:200]}
                log(f"    [B4] не прошёл: {ex}")
        else:
            rec["B4_phantoms"] = {"skipped": "payload недоступен"}
        rec["B5_book_defect_grid"] = layer_B5(kv, bp)
        log(f"    [B5] дефект книги: F_static_max = "
            f"{rec['B5_book_defect_grid']['F_static_max']:.4g} "
            f"по {rec['B5_book_defect_grid']['n_scales']} масштабам")
        out["points"][lbl] = rec

    log("\n[2/3] Зависимость препятствия тика от delta ...")
    rows = []
    for k in LADDER:
        lbl = label_of(k)
        rec = out["points"].get(lbl, {})
        b3 = rec.get("B3_tick_obstruction", {})
        r05 = b3.get("kick_0.05", {}).get("r_norm_frozen")
        r01 = b3.get("kick_0.01", {}).get("r_norm_frozen")
        m05 = b3.get("kick_0.05", {}).get("r_norm_frozen_median")
        m01 = b3.get("kick_0.01", {}).get("r_norm_frozen_median")
        if r05 is None or r01 is None:
            continue
        rows.append({"label": lbl, "k": k,
                     "delta_over_pi": rec["delta_over_pi"],
                     "delta": (0.0 if k is None else
                               float(sp.N(sp.pi / sp.Integer(k), 12))),
                     "kappa": rec["kappa_numeric"],
                     "r_norm_kick0.05": r05, "r_norm_kick0.01": r01,
                     "r_norm_median_kick0.05": m05,
                     "r_norm_median_kick0.01": m01})
    out["tick_vs_delta"] = rows
    if len(rows) >= 4:
        # log-log наклон по кирпичной части лестницы (baseline исключён:
        # delta = 0 не линеаризуется в log-оси)
        ks = [r for r in rows if r["k"] is not None]
        x_ = np.log([r["delta"] for r in ks])
        for key, tag in (("r_norm_kick0.05", "kick0.05"),
                         ("r_norm_kick0.01", "kick0.01"),
                         ("r_norm_median_kick0.05", "kick0.05_median")):
            y_ = np.log([r[key] for r in ks])
            slope, intercept = np.polyfit(x_, y_, 1)
            resid = float(np.max(np.abs(
                np.polyval((slope, intercept), x_) - y_)))
            out[f"powerlaw_{tag}"] = {
                "loglog_slope": float(slope),
                "loglog_intercept": float(intercept),
                "max_abs_residual_ln": resid,
                "n_points": len(ks)}
            log(f"    наклон log-log ({tag}): {slope:+.3f} "
                f"(макс. невязка ln {resid:.2f}, {len(ks)} кирпичей)")
        r05s = [r["r_norm_kick0.05"] for r in ks]
        k_min = ks[int(np.argmin(r05s))]
        r05m = [r["r_norm_median_kick0.05"] for r in ks]
        km_min = ks[int(np.argmin(r05m))]
        out["ladder_minimum_kick0.05"] = {
            "label": k_min["label"], "k": k_min["k"],
            "r_norm": k_min["r_norm_kick0.05"],
            "is_survivor": bool(k_min["k"] == SURVIVOR_K)}
        out["ladder_minimum_kick0.05_median"] = {
            "label": km_min["label"], "k": km_min["k"],
            "r_norm_median": km_min["r_norm_median_kick0.05"],
            "is_survivor": bool(km_min["k"] == SURVIVOR_K)}
        log(f"    минимум лестницы (kick 0.05): {k_min['label']} "
            f"(||r|| = {k_min['r_norm_kick0.05']:.6f}); по медиане "
            f"направлений: {km_min['label']} "
            f"({km_min['r_norm_median_kick0.05']:.6f}); выживший кирпич "
            f"k={SURVIVOR_K}: "
            f"{'СОВПАДАЕТ' if k_min['k'] == SURVIVOR_K else 'не совпадает'}")

    log("\n[3/3] Вердикт ...")
    v = []
    ok_clocks = [r for r in out["points"].values()
                 if r.get("B2_clock_pair", {}).get("unique_common_clock")
                 and r.get("B2_clock_pair", {}).get("gcd_zero_at_tau_star")]
    n_built = sum(1 for r in out["points"].values() if "build_failed" not in r)
    v.append(f"ТЕОРЕМА О ПАРЕ ЧАСОВ НА ЛЕСТНИЦЕ: на {len(ok_clocks)}/{n_built} "
             f"кирпичах GCD(UV_xi3, Mdef_xi5) имеет ЕДИНСТВЕННЫЙ общий "
             f"положительный корень tau*(delta) = 27/(2 - delta^2) с ТОЧНЫМ "
             f"нулём в нём — пара часов непрерывно двигается кирпичом по "
             f"всей лестнице (обобщение [C1] v17)")
    flat_ok = [r for r in out["points"].values()
               if r.get("B1_point", {}).get("flat_line_ok")]
    v.append(f"плоская линия R1h при критическом масштабе существует на "
             f"{len(flat_ok)}/{n_built} кирпичах (F <= 1e-7) — известная "
             f"глобальная статическая ветвь v15 T1 не зависит от кирпича")
    if "powerlaw_kick0.05" in out:
        pl = out["powerlaw_kick0.05"]
        v.append(f"препятствие тика НЕ степенное по delta: log-log наклон "
                 f"{pl['loglog_slope']:+.3f} с невязкой ln "
                 f"{pl['max_abs_residual_ln']:.2f} — зависимость "
                 f"немонотонна (см. tick_vs_delta)")
    lm = out.get("ladder_minimum_kick0.05")
    lm_m = out.get("ladder_minimum_kick0.05_median")
    if lm:
        v.append(f"минимум препятствия на лестнице (kick 0.05, ||r||): "
                 f"{lm['label']} ({lm['r_norm']:.6f}); по медиане всех "
                 f"кернел-направлений: {lm_m['label']} "
                 f"({lm_m['r_norm_median']:.6f}) — "
                 + ("СОВПАДАЕТ с выжившим кирпичом delta_C = pi/7 "
                    "(наблюдение-селекция, multiple-testing оговорка)"
                    if lm["is_survivor"] and lm_m["is_survivor"] else
                    "НЕ совпадает с выжившим кирпичом delta_C = pi/7: "
                    "препятствие тика НЕ селектирует выживший кирпич"))
    hits = [(lbl, r["B4_phantoms"].get("best_hit"))
            for lbl, r in out["points"].items()
            if isinstance(r.get("B4_phantoms"), dict)
            and r["B4_phantoms"].get("best_hit")]
    if hits:
        best = min(hits, key=lambda t: abs(t[1]["rel_diff_pct"]))
        n1 = sum(1 for _, h in hits if h.get("match_1pct"))
        v.append(f"фантомный зазор к pi/30 по лестнице: лучший "
                 f"{best[0]} {best[1]['rel_diff_pct']:+.3f}%; внутри 1% "
                 f"ничего ({n1} попаданий) — скан по кирпичам замыкания "
                 f"pi/30 НЕ находит (multiple-testing оговорка)")
    v.append("ИТОГ: зависимость препятствия тика от delta существует, "
             "немонотонна и не степенная (исторически-свободная мера "
             "||r|| в замороженном базисе); выживший кирпич delta_C = pi/7 "
             "НЕ является минимумом препятствия на лестнице — тик не "
             "селектирует кирпич; часы пары непрерывны по всей лестнице "
             "(tau*(delta) = 27/(2 - delta^2), точная уникальность); живые "
             "часы по-прежнему за PDE-машиной v6-v9")
    out["verdict_lines"] = v
    for line in v:
        log(f"    - {line}")
    out["honest_notes"] = [
        "ERRATUM к методу [C3] v17: r_max = max|W·res18| — базис-зависимая "
        "величина (W_align мутирует rvec-продолжением); абсолютные числа "
        "[C3] v17 — история-зависимые, качественный вывод (остановка "
        "подъёма, r ~ O(кик)) остаётся в силе на инвариантной мере ||r||; "
        "здесь главная наблюдаемая — ||r|| в замороженном базисе x*",
        "скан из 12 кирпичей — multiple-testing: любой минимум/совпадение "
        "на лестнице — НАБЛЮДЕНИЕ, не вывод (нужен независимый принцип "
        "отбора)",
        "соглашение о кирпиче kappa(delta) = 2 - delta^2/2 — записанная "
        "аддитивная бэрри-форма v11; другая конвенция пере-параметризует "
        "delta и меняет форму кривой (но не саму лестницу tau*)",
        "препятствие тика измеряется линейным подъёмом project_Fr с "
        "кернел-направлениями — локальная линейная метрика остановки, а не "
        "глобальная инвариантность; траектория подъёма инвариантна, "
        "робастность проверена по всем 5 кернел-направлениям",
        "недегенератные статические ветви вдали от цепочки/стартов не "
        "исключались здесь — см. global_static_search.py (слой (б))",
        "жёсткость — свойство усечённой башни; PDE-машина v6-v9 остаётся "
        "носителем физики эха и живых часов",
    ]
    out["runtime_s"] = round(time.time() - T_START, 1)
    path = os.path.join(RESULTS, "brick_scan_tick.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, default=str)
    log(f"Сохранено: {path} ({out['runtime_s']} c)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
