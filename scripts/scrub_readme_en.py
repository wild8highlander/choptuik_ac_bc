#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scrub version labels (vN) out of einstein_direct/README_EN.md.

Steps:
1. Retitle the module-status line.
2. Retitle every version-labelled section header.
3. Rebuild the table of contents (sections 1..29) with fresh GitHub anchors.
4. Apply ordered compound replacements, then a per-token fallback map.
5. Report any leftover tokens.
"""
import re
import sys

PATH = "README_EN.md"
s = open(PATH, encoding="utf-8").read()

# ---------------------------------------------------------------- 1. status
s = s.replace(
    "**Module status: v3 (zoom campaign v2). Hilbert-action derivation"
    " machine-verified; 2nd-order characteristic solver validated; fixed-grid"
    " critical point and mass-scaling floor analyzed; multi-zoom regridding"
    " machine rebuilt (v2) and pushed to z ≈ 5.2 with the remaining depth wall"
    " precisely diagnosed.**",
    "**Module status: verification laboratory. Hilbert-action derivation"
    " machine-verified; 2nd-order characteristic solver validated; fixed-grid"
    " critical point and mass-scaling floor analyzed; multi-zoom regridding"
    " machine rebuilt and pushed to z ≈ 5.2 with the remaining depth wall"
    " precisely diagnosed.**",
)

# ---------------------------------------------------------------- 2. headers
header_map = [
    ("## 7. Multi-zoom regridding machine v2",
     "## 7. Multi-zoom regridding machine (rebuilt prototype)"),
    ("### 7.1 What v2 fixed relative to v1",
     "### 7.1 What the rebuilt machine fixed relative to the prototype"),
    ("## 10. v3.2: the spinor (even/odd) center closure",
     "## 10. The spinor (even/odd) center closure"),
    ("## 15. v5: the central Taylor patch — machine-derived center hierarchy, ODE-internal boundary data, spinor ladder",
     "## 15. The central Taylor patch — machine-derived center hierarchy, ODE-internal boundary data, spinor ladder"),
    ("## 16. v6-fundamentals: convergence and repulsion from first principles (Thorne/MTW mass route, log-time tower, exact spectrum)",
     "## 16. Convergence and repulsion from first principles (Thorne/MTW mass route, log-time tower, exact spectrum)"),
    ("## 17. v6.1: closing the depth-wall channels — stable stages, the Thorne link seen in data, and the O6+ verdict",
     "## 17. Closing the depth-wall channels — stable stages, the Thorne link seen in data, and the O6+ verdict"),
    ("## 18. v8: the Poincare hexagonal transformation cycle (dynamics instead of the truncated tower)",
     "## 18. The Poincare hexagonal transformation cycle (dynamics instead of the truncated tower)"),
    ("## 19. v8-campaign: checking kappa = ln(64/9) and W2/t0^2 -> 4/3",
     "## 19. Hexcheck campaign: checking kappa = ln(64/9) and W2/t0^2 -> 4/3"),
    ("## 21. v9 mirror-ring pairs + exact char polynomial at tau* + monodromy books",
     "## 21. Mirror-ring pairs + exact char polynomial at tau* + monodromy books"),
    ("## 22. v11: the three repo corrections (b-C, a-C, a-B) embedded in the towers",
     "## 22. The three repo corrections (b-C, a-C, a-B) embedded in the towers"),
    ("## 23. v12: the baryon-asymmetry reading + the one-brick phantom test",
     "## 23. The baryon-asymmetry reading + the one-brick phantom test"),
    ("## 24. v13: second flows as limit-cycle variables — the linear verdict",
     "## 24. Second flows as limit-cycle variables — the linear verdict"),
    ("## 25. v14: third-order tables, the justified dd-closure, delta_mono measured by the march",
     "## 25. Third-order tables, the justified dd-closure, delta_mono measured by the march"),
    ("### 25.4 (c) delta_mono MEASURED by the march (v10-generation instrumentation)",
     "### 25.4 (c) delta_mono MEASURED by the march (precision-generation instrumentation)"),
    ("## 26. v15: the nonlinear DAE march — the solution set through the critical point is the flat line",
     "## 26. The nonlinear DAE march — the solution set through the critical point is the flat line"),
    ("## 27. v16: HEXCYCLE-DAE — the figure cycle as a global predictor (session 20)",
     "## 27. HEXCYCLE-DAE — the figure cycle as a global predictor (session 20)"),
    ("### ERRATUM to v16 (found while preparing v17)",
     "### ERRATUM (audit correction found while preparing the clock-closure campaign)"),
    ("## 28. v17: CLOCK-CLOSURE-T1C — closing the clocks through the one-brick T1c source form + the B4 remnant (session 21)",
     "## 28. CLOCK-CLOSURE-T1C — closing the clocks through the one-brick T1c source form + the B4 remnant (session 21)"),
    ("## 29. v18: BRICK-LADDER-TICK + GLOBAL-STATIC-SEARCH — intermediate bricks and the exhaustive static census (session 22)",
     "## 29. BRICK-LADDER-TICK + GLOBAL-STATIC-SEARCH — intermediate bricks and the exhaustive static census (session 22)"),
]
for old, new in header_map:
    if old not in s:
        print("[HEADER MISS]", old[:70])
    s = s.replace(old, new)

# ---------------------------------------------------------------- 3. TOC
def gh_anchor(header: str) -> str:
    t = header.lstrip("#").strip()
    t = re.sub(r"^(\d+\.)\s*", lambda m: m.group(1).replace(".", "") + " ", t)
    # GitHub: keep word chars (incl. unicode), hyphens, spaces, underscores
    t = t.lower()
    out = []
    for ch in t:
        if ch.isalnum() or ch in "_- " or ord(ch) > 127:
            out.append(ch)
        else:
            out.append("")
    t = "".join(out).replace(" ", "-")
    return t

lines = s.split("\n")
toc_entries = []
in_body = False
for ln in lines:
    if re.match(r"^## \d+\.", ln):
        m = re.match(r"^## (\d+)\.\s*(.*)$", ln)
        toc_entries.append((int(m.group(1)), m.group(2)))
toc_block = ["## Table of contents", ""]
for num, title in toc_entries:
    toc_block.append(f"{num}. [{title}](#{gh_anchor(f'## {num}. ' + title)})")
toc_block.append("")
new_toc = "\n".join(toc_block)
s = re.sub(r"## Table of contents\n\n(?:\d+\.\s*\[[^\n]*\n)+",
           new_toc + "\n", s, count=1)

# ---------------------------------------------------------------- 4. prose
compounds = [
    # code identifiers (already renamed in code)
    ("solver._tay_diag_v8", "solver._tay_diag_hex"),
    ("_tay_diag_v8", "_tay_diag_hex"),
    ("_mirror_probe_v9", "_mirror_ring_probe"),
    ("tay_diag_v9", "tay_diag_mirror"),
    ("tay_diag_v8", "tay_diag_hex"),
    # file names
    ("grid_machine_v6.json", "grid_machine_annulus.json"),
    ("grid_machine_v6.py", "grid_machine_annulus.py"),
    ("grid_machine_v8.json", "grid_machine_hexcheck.json"),
    ("grid_machine_v8.py", "grid_machine_hexcheck.py"),
    ("grid_machine_v9.json", "grid_machine_mirror.json"),
    ("grid_machine_v9.py", "grid_machine_mirror.py"),
    ("probe_v6_channel.py", "probe_channel_trace.py"),
    ("v8_figures.py", "hexcheck_figures.py"),
    ("zoom_campaign_v3.json", "zoom_campaign_regular.json"),
    ("zoom_campaign_v3.py", "zoom_campaign_regular.py"),
    ("zoom_campaign_v5.json", "zoom_campaign_taylor.json"),
    ("zoom_campaign_v5.py", "zoom_campaign_taylor.py"),
    ("fig_tau_v8.png", "fig_tau_hexcheck.png"),
    ("fig_w2_v8.png", "fig_w2_hexcheck.png"),
    # machine suite
    ("(v6–v9)", "(the PDE machine suite)"),
    ("(v6-v9)", "(the PDE machine suite)"),
    ("PDE machine v6–v9", "PDE machine suite"),
    ("PDE machine v6-v9", "PDE machine suite"),
    ("machine (v6–v9)", "machine suite"),
    ("v6–v9", "the PDE machine suite"),
    ("v6-v9", "the PDE machine suite"),
    # compounds
    ("v10-generation", "precision-generation"),
    ("v14-assigned", "third-order-campaign-assigned"),
    ("v17 uniqueness", "clock-closure uniqueness"),
    ("v11 convention", "correction-campaign convention"),
    ("v15 T3 verdict", "nonlinear-DAE-campaign T3 verdict"),
    ("v15 T2", "nonlinear-DAE-campaign T2"),
    ("v16 'static backbone'", "hexcycle-DAE 'static backbone'"),
    ("the v16 [T1c]", "the hexcycle-DAE [T1c]"),
    ("v15 flat line", "nonlinear-DAE-campaign flat line"),
    ("v15 proved", "the nonlinear-DAE campaign proved"),
    ("zoom campaign v2", "prototype zoom campaign"),
    ("v2 zoom campaign", "prototype zoom campaign"),
    ("machine rebuilt (v2)", "machine rebuilt"),
    ("regridding machine v2", "regridding machine"),
    ("the v2 `_center_heal`", "the rebuilt `_center_heal`"),
    ("v3.2 protocol campaign", "regular-closure protocol campaign"),
    ("v3.2 protocol", "regular-closure protocol"),
    ("v3.2 center closures", "regular-closure center closures"),
    ("the v3.2 code", "the regular-closure code"),
    ("(v3.2)", "(regular closure)"),
    ("v3.2", "regular-closure"),
    ("v5 death chain", "Taylor-patch death chain"),
    ("the v5 wall", "the Taylor-patch wall"),
    ("since v5", "since the Taylor-patch stage"),
    ("v5 wall", "Taylor-patch wall"),
    ("v5-минимум", "Taylor-patch minimum"),
    ("the v8 pairs", "the hexcheck pairs"),
    ("v8 pairs", "hexcheck pairs"),
    ("v8-campaign", "hexcheck campaign"),
    ("v8 campaign", "hexcheck campaign"),
    ("stable v6.1 chains", "stable annulus chains"),
    ("v6.1 chains", "annulus chains"),
    ("v6.1 machine", "annulus machine"),
    ("v6.1", "annulus"),
]
for a, b in compounds:
    s = s.replace(a, b)

fallback = {
    "v1": "the prototype",
    "v2": "the rebuilt machine",
    "v3": "the regular-closure stage",
    "v4": "the spinor campaign",
    "v5": "the Taylor-patch stage",
    "v6": "the annulus machine",
    "v7": "the next fix cycle",
    "v8": "the hexcheck campaign",
    "v9": "the mirror campaign",
    "v10": "the precision campaign",
    "v11": "the correction campaign",
    "v12": "the baryon-asymmetry campaign",
    "v13": "the second-flows campaign",
    "v14": "the third-order campaign",
    "v15": "the nonlinear-DAE campaign",
    "v16": "the hexcycle-DAE campaign",
    "v17": "the clock-closure campaign",
    "v18": "the brick-ladder campaign",
}
def _sub(m):
    tok = m.group(0)
    return fallback.get(tok, tok)
s = re.sub(r"\bv\d{1,2}(?:\.\d)?\b", _sub, s)

# tidy double articles produced by substitutions
s = s.replace("the the ", "the ").replace("The the ", "The ")

open(PATH, "w", encoding="utf-8").write(s)

# ---------------------------------------------------------------- 5. report
left = re.findall(r".{20}\bv\d{1,2}(?:\.\d)?\b.{20}", s)
print(f"leftover tokens: {len(left)}")
for l in left[:20]:
    print("  ", l)
print(f"TOC entries: {len(toc_entries)}")
