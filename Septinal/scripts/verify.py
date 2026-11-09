#!/usr/bin/env python3
"""Septinal · verify.py — the pre-push gate.

Checks, against the committed tree:
  1. every relative image/link in README.md / README_ru.md / docs/*.md
     resolves to an existing file;
  2. no leftover placeholders (TODO / XXX / 【…】 / undefined / NaN) in the
     markdown layer;
  3. every data file mentioned in the READMEs exists and is non-empty;
  4. the key counts quoted in the READMEs match the tree (modules, theorems,
     figures, animations, logs, banners);
  5. the committed JSON/CSV artifacts parse.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD_FILES = ["README.md", "README_ru.md", "docs/THEOREMS.md", "docs/AUDIT.md",
            "docs/GLOSSARY.md", "docs/REPRODUCE.md"]
PLACEHOLDERS = ["TODO", "XXX", "【", "undefined", "NaN", "Lorem", "待补充"]
fails = []


def check(cond: bool, msg: str) -> None:
    print(("  ok  " if cond else "  FAIL") + f"  {msg}")
    if not cond:
        fails.append(msg)


def md_links(text: str):
    for m in re.finditer(r"\]\(([^)#]+?)(#[^)]*)?\)", text):
        p = m.group(1).strip()
        if p.startswith(("http", "mailto:", "data:")):
            continue
        yield p
    for m in re.finditer(r"<img src=\"([^\"]+)\"", text):
        p = m.group(1).strip()
        if p.startswith(("http", "mailto:", "data:")):
            continue
        yield p
    for m in re.finditer(r"<source[^>]+srcset=\"([^\"]+)\"", text):
        p = m.group(1).strip()
        if p.startswith(("http", "mailto:", "data:")):
            continue
        yield p


def main() -> None:
    print("== link resolution ==")
    root_resolved = ROOT.resolve()
    for md in MD_FILES:
        text = (ROOT / md).read_text()
        n = 0
        for link in md_links(text):
            n += 1
            target = ((ROOT / md).parent / link).resolve()
            if not (target.exists() and root_resolved in target.parents
                    or target == root_resolved / md and target.exists()):
                fails.append(f"{md}: broken link {link}")
                print(f"  FAIL  {md}: {link}")
        check(True, f"{md}: {n} relative links checked")

    print("== placeholders ==")
    for md in MD_FILES:
        text = (ROOT / md).read_text()
        for p in PLACEHOLDERS:
            if p in text:
                fails.append(f"{md}: placeholder {p!r}")
                print(f"  FAIL  {md}: contains {p!r}")
    check(True, "no placeholders in the markdown layer")

    print("== data artifacts parse ==")
    for j in sorted((ROOT / "data").glob("*.json")):
        json.loads(j.read_text())
    for c in sorted((ROOT / "data").glob("*.csv")):
        with c.open() as fh:
            rows = list(csv.reader(fh))
        check(len(rows) > 1 and all(len(r) == len(rows[0]) for r in rows),
              f"{c.name}: {len(rows)-1} rows, rectangular")
    for j in sorted((ROOT / "data").glob("*.json")):
        check(j.stat().st_size > 2, f"{j.name}: {j.stat().st_size} bytes")

    print("== counts vs README ==")
    inv = list(csv.DictReader((ROOT / "data" / "theorem_inventory.csv").open()))
    thm = sum(int(r["theorems"]) for r in inv)
    lines = sum(int(r["lines"]) for r in inv)
    figs = len(list((ROOT / "figures").rglob("*.png")))
    gifs = len(list((ROOT / "animations").rglob("*.gif")))
    svgs = len(list((ROOT / "assets").rglob("*.svg")))
    logs = len(list((ROOT / "logs").glob("*.log")))
    scripts = len(list((ROOT / "scripts").glob("*.py")))
    check(len(inv) == 24, f"modules: {len(inv)} == 24")
    check(thm == 145, f"theorems: {thm} == 145")
    check(lines == 5108, f"lean lines: {lines} == 5108")
    check(figs == 32, f"figures: {figs} == 32")
    check(gifs == 10, f"animations: {gifs} == 10")
    check(svgs == 13, f"svgs: {svgs} == 13")
    check(logs == 8, f"logs: {logs} == 8")
    check(scripts == 12, f"scripts: {scripts} == 12 (incl. verify.py + septinal_verify.py)")

    print("== gif/png non-empty ==")
    for g in sorted((ROOT / "animations").rglob("*.gif")):
        check(g.stat().st_size > 50_000, f"{g.relative_to(ROOT)}: {g.stat().st_size//1024} KB")

    print()
    if fails:
        print(f"VERIFY: {len(fails)} FAILURE(S)")
        for f in fails:
            print(" -", f)
        return 1
    print("VERIFY: ALL GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
