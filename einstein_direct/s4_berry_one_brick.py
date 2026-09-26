#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S4-прогон фантомного теста для ОДНО-кирпичной схемы (барионная асимметрия башни).

Гипотеза автора: 'всё ровно поднимается, отклонение в одном кирпичике, чтобы
не происходило полной аннигиляции'. Машина уже показала:
  - статическая асимметрия в одной 'двери' запрещена (точка умирает, C1 = 0.386);
  - равномерное (симметричное) встраивание оставляет монодромию = 1 ТОЧНО
    (полная аннигиляция фазы, возврат в пирамиду) — стерильно.
Единственная выжившая поправка в лучшей книге — ОДИН кирпич: bC = pi^2/98
(бэрри, фаза delta_C = pi/7). В S4 фантомный тест для этой схемы НЕ прогонялся.
Здесь добиваем: карандаш в исправленной точке kappa = 2 - pi^2/98,
tau* = 27/(2*kappa) = 7.10792, сопоставление Im lambda фантомов с k*pi/30.
"""
import json
import sys
import os

sys.path.insert(0, "/home/z/my-project/choptuik_ac_bc/einstein_direct")
os.chdir("/home/z/my-project/choptuik_ac_bc/einstein_direct")

import sympy_spinor_corrections as ssc  # noqa: E402

def main() -> None:
    s0, corr = ssc.s0_corrections()
    s1, payload = ssc.s1_doors_symbolic()
    schemes = ssc.s2_schemes(payload, corr)
    rec = schemes["H_berry_half_down_(1-bC/2)"]
    kv = rec["kappa_uniform"]
    tv = rec["tau_star_corrected"]
    print(f"kappa (one brick, 2 - bC) = {kv!r}")
    print(f"tau* = 27/(2 kappa)      = {tv!r}")
    out = ssc.s4_pencil(payload, "H_berry_half_down_(1-bC/2)_ONE_BRICK",
                        (kv, kv, kv), tv)
    path = "/home/z/my-project/choptuik_ac_bc/einstein_direct/results/spinor_corrections_one_brick.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2, default=str)
    print("saved ->", path)

    print("\n=== Im lambda фантомов vs лестница k*pi/30 ===")
    for row in out["phantom_Im_vs_ladder_top"]:
        print(f"  k/30={row['k_over_30']:>2}  Im|lam|={abs(row['lambda'][1]):.6f}  "
              f"лестница={row['nearest_ladder']:.6f}  rel={row['rel_diff_pct']:+.3f}%")
    print("\n genuine (вещественно-нейтральные) моды:",
          [f"{m['lambda'][0]:.2e}{m['lambda'][1]:+.4f}i" for m in out["genuine_modes"]])

if __name__ == "__main__":
    main()
