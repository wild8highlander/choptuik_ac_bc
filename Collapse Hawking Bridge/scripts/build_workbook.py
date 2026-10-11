#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_workbook.py — the one-file Excel companion of the bridge.

Builds tables/bridge_workbook.xlsx from the 13 committed data tables in
data/bridge/ plus an Overview sheet (headline numbers + inventory).
Pure conversion: no new physics, no recomputation.

Run:  python3 scripts/build_workbook.py
"""
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# v2.0.1 (audit advisory IVP-03): styles are local to the tree; openpyxl
# is an optional dependency (pyproject: [project.optional-dependencies].
# workbook).
from workbook_style import (  # noqa: E402
    setup_sheet, style_header_row, style_data_row, style_total_row,
    font_title, font_body, align_number, align_text, FONT_NAME,
)

from openpyxl import Workbook  # noqa: E402
from openpyxl.utils import get_column_letter  # noqa: E402

DATA = os.path.join(ROOT, "data", "bridge")
OUT = os.path.join(ROOT, "tables", "bridge_workbook.xlsx")

SHEETS = [
    ("bridge_constants",       "Bridge constants (Part A/B/C)"),
    ("bridge_master",          "Master mapping (5 scales x 3 members)"),
    ("born_spectrum",          "Born spectrum (N400 + N800)"),
    ("collapse_verdict_summary", "Collapse verdict summary"),
    ("page_curve_grid",        "Page curve grid (CMB input)"),
    ("page_members",           "Page ensemble members"),
    ("page_haar_check",        "Haar audit (formula vs MC)"),
    ("scale_ladder_length",    "Scale ladder — lengths"),
    ("scale_ladder_accel",     "Scale ladder — accelerations"),
    ("scale_ladder_curvature", "Scale ladder — curvature"),
    ("campaign_c2_subcritical", "C2 subcritical branch"),
    ("campaign_c2_bifurcation", "C2 supercritical bifurcation"),
    ("campaign_c3b_ladder",    "C3b concentrated resolution ladder"),
]

HEADLINE = [
    ("A* critical amplitude (N=800)", "0.08053436", "c1_verdict.json"),
    ("Agreement with independent N=1600 reference", "1.06e-6", "c1_verdict.json"),
    ("Roberts-Oshiro convergence orders", "2.03 / 2.09", "c1_verdict.json"),
    ("Born ensemble members f~", "0.2877 / 0.2684 / 1.0", "collapse_verdict_summary.json"),
    ("CMB contact mass (T_H = T_CMB)", "4.5016e22 kg", "chbridge.hawking"),
    ("Page fraction t_Page/t_evap", "0.6464466 (exact 1 - 2^-3/2)", "chbridge.hawking"),
    ("Haar check max |S_formula - S_MC|", "0.0042 bits", "page_haar_check.csv"),
    ("Septinial constant b_Ch = 1 - cos(2pi/7)", "0.37651019814126640", "exact"),
    ("Framework gap |gamma_Ch - b_Ch|/b_Ch", "0.67%", "comparison"),
    ("Delta*gamma anchor product (arithmetic)", "1.28656 vs 1.27 (within frozen tolerance, 1.3%; ANCHOR_ARITHMETIC — not a measurement)", "C3"),
    ("Subcritical q_max", "0.0158 -> 0.5845 (monotone)", "C2"),
    ("Critical slowdown", "v = 0.510 - 0.0334 ln(eps), r2 = 0.71", "C2"),
    ("Echo accumulation rate", "0.1909 / e-fold (anchor 0.2907)", "C2"),
    ("Born bifurcation half-width eps_half", "4.86e-3", "C2"),
    ("Floor law floor_M(N)", "~12/N (0.0155 / 7.104e-3 / 3.842e-3)", "C1 + C3b"),
    ("gamma_eff at concentrated grids", "stabilises ~0.12 (honest negative)", "C3b"),
    ("Delta at any depth up to N=3200", "unmeasurable (< 3 peaks)", "C3/C3b"),
]


def _rows(name):
    path_csv = os.path.join(DATA, name + ".csv")
    if os.path.exists(path_csv):
        with open(path_csv) as f:
            return list(csv.reader(f))
    # JSON fallback: flatten one level into key / value / note rows
    with open(os.path.join(DATA, name + ".json")) as f:
        d = json.load(f)
    out = [["key", "value"]]
    for k, v in d.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                out.append([f"{k}.{k2}", _fmt(v2)])
        elif isinstance(v, list):
            out.append([k, _fmt(v)])
        else:
            out.append([k, _fmt(v)])
    return out


def _fmt(v):
    if isinstance(v, float):
        return f"{v:.10g}"
    if isinstance(v, (list, tuple)):
        return " / ".join(_fmt(x) for x in v)
    return str(v)


def _autowidth(ws, cap=42):
    for col in range(1, ws.max_column + 1):
        best = 8
        for row in range(1, ws.max_row + 1):
            v = ws.cell(row=row, column=col).value
            if v is not None:
                best = max(best, min(len(str(v)) + 2, cap))
        ws.column_dimensions[get_column_letter(col)].width = best


def _numify(v):
    if v is None or v == "":
        return v
    try:
        f = float(v)
        return int(f) if f.is_integer() and abs(f) < 1e15 else f
    except (ValueError, TypeError):
        return v


def add_table_sheet(wb, key, title):
    rows = _rows(key)
    ws = wb.create_sheet(key[:31])
    setup_sheet(ws, title=title, last_col=max(2, len(rows[0])))
    ws.append(rows[0])
    style_header_row(ws, 3, 1, len(rows[0]))
    for i, r in enumerate(rows[1:]):
        ws.append([_numify(x) for x in r])
        style_data_row(ws, 4 + i, 1, len(r), i)
    ws.freeze_panes = "A4"
    _autowidth(ws)
    return ws


def add_overview(wb):
    ws = wb.create_sheet("Overview", 0)
    setup_sheet(ws, title="Collapse-Hawking Bridge — data workbook", last_col=3)
    meta = [
        ("package", "Collapse-Hawking Bridge"),
        ("version", "2.0.0"),
        ("source of truth", "data/bridge/*.csv (byte-deterministic)"),
        ("verdicts", "campaigns/reference/*.json (C1, C2, C3, C3b)"),
        ("tests", "60 pytest + 7/7 mpmath checks"),
        ("sheets", "13 data tables + this overview"),
    ]
    r = 3
    for k, v in meta:
        ws.cell(row=r, column=1, value=k).font = font_body()
        ws.cell(row=r, column=2, value=v).font = font_body()
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="Headline numbers").font = font_title()
    r += 1
    hdr = ["quantity", "value", "source"]
    for j, h in enumerate(hdr, 1):
        ws.cell(row=r, column=j, value=h)
    style_header_row(ws, r, 1, 3)
    r += 1
    for i, (q, v, s) in enumerate(HEADLINE):
        ws.cell(row=r, column=1, value=q)
        ws.cell(row=r, column=2, value=v)
        ws.cell(row=r, column=3, value=s)
        style_data_row(ws, r, 1, 3, i)
        r += 1
    r += 1
    ws.cell(row=r, column=1, value="Sheet inventory").font = font_title()
    r += 1
    for j, h in enumerate(("sheet", "description"), 1):
        ws.cell(row=r, column=j, value=h)
    style_header_row(ws, r, 1, 2)
    r += 1
    for i, (key, desc) in enumerate(SHEETS):
        ws.cell(row=r, column=1, value=key)
        ws.cell(row=r, column=2, value=desc)
        style_data_row(ws, r, 1, 2, i)
        r += 1
    _autowidth(ws, cap=64)
    return ws


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    wb = Workbook()
    wb.remove(wb.active)
    add_overview(wb)
    for key, title in SHEETS:
        add_table_sheet(wb, key, title)
        print("sheet", key, "rows", _rows(key).__len__() - 1)
    wb.properties.creator = "Z.ai"
    wb.properties.title = "Collapse-Hawking Bridge — data workbook v2.0.0"
    wb.save(OUT)
    print("wrote", os.path.relpath(OUT, ROOT))


if __name__ == "__main__":
    main()
