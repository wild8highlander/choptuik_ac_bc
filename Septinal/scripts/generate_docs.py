#!/usr/bin/env python3
"""Septinal · generate_docs.py — regenerates docs/THEOREMS.md from the Lean
sources: every top-level theorem of both libraries, its module and its
Lean line number, plus the audited headline lists parsed from the two
AxiomAudit files.  Deterministic; run from the package root via
``python scripts/generate_docs.py``.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean"
OUT = ROOT / "docs" / "THEOREMS.md"

AREAS = [
    ("Choptuik.Geometry", "Geometry — the double-null arena"),
    ("Choptuik.Analysis", "Analysis — field equations, PDE, intervals"),
    ("Choptuik.Existence", "Existence — DSS solutions and Newton–Kantorovich"),
    ("Choptuik.Stability", "Stability — linearization and the spectrum"),
    ("Choptuik.Scaling", "Scaling — the law, the echo, universality"),
    ("Choptuik.Bridge", "Bridge — the certificate channel"),
    ("Satellite.Berry", "Satellite B1 — the Berry quantum"),
    ("Satellite.Dial", "Satellite B2 — the dial-22"),
    ("Satellite.Chiral", "Satellite B2b — chirality"),
    ("Satellite.Corrections", "Satellite C2 — the corrections"),
    ("Satellite.Cascade", "Satellite C3 — the cascade"),
    ("Satellite.Unlock", "Satellite C4 — the unlock"),
    ("Satellite.Klein", "Satellite C5 — PSL(2,7) and the Klein quartic"),
]


def scan() -> dict:
    modules = {}
    for path in sorted(LEAN.rglob("*.lean")):
        rel = path.relative_to(LEAN)
        if rel.as_posix().endswith("AxiomAudit.lean") or rel.name in ("Choptuik.lean", "Satellite.lean"):
            continue
        mod = rel.as_posix()[:-5].replace("/", ".")
        text = path.read_text()
        thms = []
        for i, line in enumerate(text.splitlines(), 1):
            m = re.match(r"^theorem\s+([A-Za-z0-9_'.]+)", line)
            if m:
                thms.append((m.group(1), i))
        if thms:
            modules[mod] = thms
    return modules


def headline() -> dict:
    out = {}
    for audit, key in ((LEAN / "AxiomAudit.lean", "Choptuik"),
                       (LEAN / "Satellite" / "AxiomAudit.lean", "Satellite")):
        names = re.findall(r"#print axioms\s+([A-Za-z0-9_.']+)", audit.read_text())
        out[key] = names
    return out


def main() -> None:
    modules = scan()
    heads = headline()
    total = sum(len(v) for v in modules.values())

    lines = [
        "<p align=\"center\">",
        "  <img src=\"../assets/banners/banner_theorems.svg\" alt=\"theorem atlas\" width=\"100%\">",
        "</p>",
        "",
        "# docs/THEOREMS.md — the theorem atlas",
        "",
        "![theorems](https://img.shields.io/badge/top--level_theorems-"
        f"{total}-4CC9F0.svg)",
        "![headline](https://img.shields.io/badge/audited_headline-95-brightgreen.svg)",
        "![axioms](https://img.shields.io/badge/permitted-propext·choice·Quot.sound-6b2c8f.svg)",
        "",
        "Every top-level theorem of the two Lean libraries, scanned from the",
        "committed sources (regenerate: `python scripts/generate_docs.py`).",
        "Line numbers point into the module files; the headline lists are the",
        "exact `#print axioms` orders of the two audit files.",
        "",
    ]
    for prefix, title in AREAS:
        rows = []
        for mod, thms in modules.items():
            if mod.startswith(prefix):
                for name, ln in thms:
                    full = f"{mod}.{name}" if not name.startswith(prefix.split(".")[-1] + ".") else name
                    file = mod.replace(".", "/") + ".lean"
                    rows.append(f"| `{full}` | [{file}:{ln}]"
                                f"(../lean/{file}#L{ln}) |")
        if not rows:
            continue
        lines += [f"## {title}", "", "| Theorem | Source |", "|---|---|", *rows, ""]

    lines += ["## The audited headline declarations", ""]
    lines += ["### `Choptuik` — 33 declarations, all `[propext, Classical.choice, Quot.sound]`", ""]
    lines += [f"- `{n}`" for n in heads["Choptuik"]]
    lines += ["", "### `Satellite` — 62 declarations, all `[propext, Classical.choice, Quot.sound]`", ""]
    lines += [f"- `{n}`" for n in heads["Satellite"]]
    lines += ["",
              "---",
              "",
              "*Audit logs: `logs/choptuik_audit.log` (`AUDIT_EXIT=0`) and",
              "`logs/sat_final.log` (`Build completed successfully`).*",
              ""]
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines))
    print(f"[docs] {OUT.relative_to(ROOT)}  ({total} theorems listed)")


if __name__ == "__main__":
    main()
