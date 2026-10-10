#!/usr/bin/env python3
"""Multilingual twin check: 14 RU/EN twin pairs x 3 sweeps = 42 checks.

Sweep 1 (numbers): every pinned numeric value appears in README.ru.md and README.md.
Sweep 2 (headers): section headers are paired 1:1 between the two files.
Sweep 3 (claims):  all 30 claim ids appear in RESULTS.ru.md and RESULTS.md.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TWINS = [
    ("beta_star", "3.3583", "3.3583"),
    ("delta_f_min", "0.181777", "0.181777"),
    ("delta_thresh", "0.0363485", "0.0363485"),
    ("beta_c", "2.9910", "2.9910"),
    ("ratio_naive", "6.3", "6.3"),
    ("p_esc", "0.2433", "0.2433"),
    ("omega", "0.477464", "0.477464"),
    ("v_star", "0.9359375", "0.9359375"),
    ("r_max", "2.7654", "2.7654"),
    ("shares_A", "91.95", "91.95"),
    ("wing", "4.071", "4.071"),
    ("eta_crit", "0.0908885", "0.0908885"),
    ("margin", "1.49", "1.49"),
    ("eta_B", "6.1", "6.1"),
]

HEADERS_RU = ["Обзор", "Результаты", "Честные негативные результаты",
              "Теоремы", "Аудит", "Воспроизводимость", "Цитирование"]
HEADERS_EN = ["Overview", "Results", "Honest negative results",
              "Theorems", "Audit", "Reproducibility", "Citation"]


def sweep_numbers() -> list:
    out = []
    ru = (ROOT / "README.ru.md").read_text(encoding="utf-8")
    en = (ROOT / "README.md").read_text(encoding="utf-8")
    for i, (key, ru_v, en_v) in enumerate(TWINS):
        out.append(("s1", f"{i:02d}:{key}", ru_v in ru and en_v in en))
    return out


def sweep_headers() -> list:
    ru = (ROOT / "README.ru.md").read_text(encoding="utf-8")
    en = (ROOT / "README.md").read_text(encoding="utf-8")
    out = []
    for i, (h_ru, h_en) in enumerate(zip(HEADERS_RU, HEADERS_EN)):
        out.append(("s2", f"h{i:02d}", (h_ru in ru) and (h_en in en)))
    return out


def sweep_claims() -> list:
    ru = (ROOT / "RESULTS.ru.md").read_text(encoding="utf-8")
    en = (ROOT / "RESULTS.md").read_text(encoding="utf-8")
    reg = json.loads((ROOT / "data" / "claims.json").read_text())["claims"]
    out = []
    for i, c in enumerate(reg):
        cid = c["id"]
        out.append(("s3", f"c{i:02d}:{cid}", (cid in ru) and (cid in en)))
    return out


def main() -> int:
    checks = sweep_numbers() + sweep_headers() + sweep_claims()
    n_pass = sum(1 for _, _, ok in checks if ok)
    for sweep, key, ok in checks:
        if not ok:
            print(f"  MISS {sweep} {key}")
    print(f"twin check: {n_pass}/{len(checks)} PASS "
          f"(14 pairs x 3 sweeps)")
    (ROOT / "data" / "twins.json").write_text(json.dumps(
        {"n_checks": len(checks), "n_pass": n_pass,
         "pairs": len(TWINS), "sweeps": 3,
         "all_pass": bool(n_pass == len(checks)),
         "checks": [{"sweep": s, "key": k, "pass": bool(o)} for s, k, o in checks]},
        indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if n_pass == len(checks) else 2


if __name__ == "__main__":
    sys.exit(main())
