#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Пробник канала j=19-20: построчная трассировка смерти стадии.

Запуск: python3 probe_v6_channel.py [eps] [max_zooms]
Печатает построчно: mx, Q, max|t|, max|s|, tay-строки, фолбэки, гейты,
C_j/M1 кольца, максимум правки перемарша. Сохраняет JSON в results/.
"""
import json
import os
import sys

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zoom_solver import ZoomRunner, RESULTS, V_P, SIGMA  # noqa: E402
from grid_machine_annulus import A_STAR  # noqa: E402

eps = float(sys.argv[1]) if len(sys.argv) > 1 else 1e-3
max_zooms = int(sys.argv[2]) if len(sys.argv) > 2 else 8
gate = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
cross = int(sys.argv[4]) if len(sys.argv) > 4 else 1

rows = []


def dbg(runner, st, v_now, mx, Q):
    sol = runner.sol
    tay = getattr(sol, "_tay", None) or {}
    ann = getattr(sol, "_ann_hist", [])
    ann_last = ann[-1] if ann else {}
    r = st["r"]
    zone = sol.reg_zone_du * sol.du
    out_m = np.abs(r) > 3.0 * zone
    t_out = float(np.max(np.abs(st["t"][out_m]))) if out_m.any() else 0.0
    s_out = float(np.max(np.abs(st["s"][out_m]))) if out_m.any() else 0.0
    p_out = float(np.max(np.abs(st["p"][out_m]))) if out_m.any() else 0.0
    q_out = float(np.max(np.abs(st["q"][out_m]))) if out_m.any() else 0.0
    rows.append({
        "zoom": runner.diag.zooms, "j": runner.j, "v": float(v_now),
        "mx": float(mx), "Q": float(Q),
        "t_out": t_out, "s_out": s_out, "p_out": p_out, "q_out": q_out,
        "tay_rows": int(tay.get("rows", 0)),
        "fallbacks": int(tay.get("fallbacks", 0)),
        "t0": float(tay.get("t0", np.nan)),
        "d0": float(tay.get("d0", np.nan)),
        "P2": float(tay.get("P2", np.nan)),
        "W2": float(tay.get("W2", np.nan)),
        "d0_capped": int(tay.get("d0_capped", 0)),
        "W2_gated": int(tay.get("W2_gated", 0)),
        "M3_gated": int(tay.get("M3_gated", 0)),
        "C_j": float(ann_last.get("C_j", np.nan)),
        "M1": float(ann_last.get("M1", np.nan)),
        "gated": ann_last.get("gated", ""),
        "du": float(sol.du),
    })
    # фокусный дамп профиля: стадия смерти, строки вокруг j_focus
    if runner.diag.zooms >= 2 and 9 <= runner.j <= 13:
        i0 = int(np.argmin(np.abs(r)))
        ks = np.arange(0, 24)
        ip = i0 - ks
        x = (float(v_now) - sol.u) / 2.0
        x_star = float(tay.get("xstar_prev", x[i0]) or x[i0])
        prof = {
            "zoom": runner.diag.zooms, "j": runner.j, "v": float(v_now),
            "xi": [float(x[i] - x_star) for i in ip],
            "t": [float(st["t"][i]) for i in ip],
            "s": [float(st["s"][i]) for i in ip],
            "pq": [float(st["p"][i] + st["q"][i]) for i in ip],
            "m": [float(st["m"][i]) for i in ip],
            "d": [float(st["d"][i]) for i in ip],
            "a2": [float(st["alpha2"][i]) for i in ip],
        }
        profs.append(prof)


profs = []


r = ZoomRunner(A=A_STAR + eps, n=800, max_zooms=max_zooms, verbose=False,
               annulus=True, ann_factor=10.0, march_center=True, r_ah_du=8.0,
               ann_relax_gate=gate, ann_cross=bool(cross))
r.dbg = dbg
d = r.run()

print("=" * 100)
print(f"eps={eps} gate={gate} cross={cross}  stop={d.stopped}  zooms={d.zooms}  z={r._z_acc:.3f}  "
      f"M_frozen={d.m_ah:.6f}  M_max={d.m_ah_max:.6f}")
if d.stop_detail:
    print("stop_detail:", json.dumps(
        {k: (float(v) if isinstance(v, (int, float)) else v)
         for k, v in d.stop_detail.items()}, indent=1))
print("=" * 100)
# последние 30 строк трассировки
print(f"{'zm':>2} {'j':>4} {'mx':>8} {'Q':>9} {'max|t|out':>10} {'max|s|out':>10} "
      f"{'max|p|out':>10} {'tay':>4} {'fb':>3} {'t0':>10} {'d0':>10} "
      f"{'P2':>10} {'gated':>12}")
for x in rows[-32:]:
    print(f"{x['zoom']:>2} {x['j']:>4} {x['mx']:>8.3f} {x['Q']:>9.3f} "
          f"{x['t_out']:>10.3g} {x['s_out']:>10.3g} {x['p_out']:>10.3g} "
          f"{x['tay_rows']:>4} {x['fallbacks']:>3} {x['t0']:>10.3g} "
          f"{x['d0']:>10.3g} {x['P2']:>10.3g} {x['gated']:>12}")

# tay-гистограмма последних стадий: невязки/гейты O-фита (почему P2=0)
print("-" * 100)
print("tay hist tail (v, t0, P2, res_r, res_E, res_O, E0_free, C_par, pq_even_max):")
for rec in r.tay_hist_all[-24:]:
    print(f"  st{rec.get('stage')} v={rec.get('v'):.5f} t0={rec.get('t0'):.4g} "
          f"P2={rec.get('P2'):.4g} res_r={rec.get('res_r'):.3g} "
          f"res_E={rec.get('res_E'):.3g} res_O={rec.get('res_O'):.3g} "
          f"E0={rec.get('E0_free'):.4g} Cpar={rec.get('C_par'):.3g} "
          f"pqev={rec.get('pq_even_max'):.3g}")
print("ann hist tail (C_j, M1, corr_ts_max, gated):")
for rec in list(getattr(r.sol, "_ann_hist", []))[-12:]:
    print(f"  v={rec.get('v'):.5f} C_j={rec.get('C_j'):.3g} "
          f"M1={rec.get('M1'):.3g} corr_ts={rec.get('corr_ts_max'):.3g} "
          f"gated={rec.get('gated')}")

out = {"eps": eps, "gate": gate, "cross": cross, "stop": d.stopped, "zooms": d.zooms, "z": float(r._z_acc),
       "profiles": profs,
       "m_ah": float(d.m_ah), "m_ah_max": float(d.m_ah_max),
       "stop_detail": {k: (float(v) if isinstance(v, (int, float)) else v)
                       for k, v in (d.stop_detail or {}).items()},
       "rows": rows,
       "tay_hist_tail": r.tay_hist_all[-40:],
       "ann_hist_tail": list(getattr(r.sol, "_ann_hist", [])[-40:])}
path = os.path.join(RESULTS, f"probe_channel_eps{eps:.0e}.json")
with open(path, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
print("saved:", path)
