#!/usr/bin/env python3
"""Septinal · generate_banners.py — the SVG banners and logos of the package.

Hand-built vector art in the parent programme's identity: concentric gold
rings converging on a luminous core (the critical collapse motif), the
24-slot septinial dial, and the {7,3} Klein map ghost lines.  Dark and
light renditions for GitHub's prefers-color-scheme picture element.

Outputs: assets/banners/banner_header.svg, banner_header_ru.svg,
banner_theorems.svg, banner_theorems_ru.svg, banner_bridge.svg,
banner_bridge_ru.svg, banner_satellite.svg, banner_satellite_ru.svg,
banner_data.svg, banner_data_ru.svg and assets/logo/logo_dark.svg,
logo_light.svg — English and Russian renditions of every banner.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets"

GOLD = "#E8B44A"
GOLD_CORE = "#FFE9B0"
VIOLET = "#9B8CDE"
CYAN = "#4CC9F0"
RED = "#E86A6A"
GREEN = "#8FB7A4"


def rings(cx, cy, radii, stroke, opacities, sw=1.6):
    out = []
    for r, o in zip(radii, opacities):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
                   f'stroke="{stroke}" stroke-width="{sw}" opacity="{o}"/>')
    return "\n  ".join(out)


def dial_slots(cx, cy, R, n=24, skip=(0, 12), r=3.2, palette=None):
    """the 24 slots, with the antipodal gap crossed out"""
    import math
    out = []
    cols = palette or [GOLD, VIOLET, CYAN, GREEN, RED]
    for s in range(n):
        th = 2 * math.pi * s / n - math.pi / 2
        x, y = cx + R * math.cos(th), cy + R * math.sin(th)
        if s in skip:
            out.append(f'<line x1="{x-4.5:.1f}" y1="{y-4.5:.1f}" x2="{x+4.5:.1f}" '
                       f'y2="{y+4.5:.1f}" stroke="{RED}" stroke-width="2.4" opacity="0.95"/>')
            out.append(f'<line x1="{x-4.5:.1f}" y1="{y+4.5:.1f}" x2="{x+4.5:.1f}" '
                       f'y2="{y-4.5:.1f}" stroke="{RED}" stroke-width="2.4" opacity="0.95"/>')
        else:
            c = cols[s % len(cols)]
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c}" opacity="0.9"/>')
    return "\n  ".join(out)


def header(dark=True, ru=False) -> str:
    bg1, bg2 = ("#05060C", "#0F172A") if dark else ("#F4F0E6", "#FAF8F4")
    txt = "#F1F5F9" if dark else "#2B2A28"
    sub = "#94A3B8" if dark else "#6B6455"
    core = GOLD_CORE if dark else "#8A6A24"
    tagline = ("формальный Чоптуик  ·  септинальный тормозной спутник" if ru else
               "formal Choptuik  ·  the Septinial braking satellite")
    meta = ("Lean 4 + Mathlib  —  ноль sorry  —  ноль аксиом  —  seed 1993" if ru else
            "Lean 4 + Mathlib  —  sorry-free  —  axiom-clean  —  seed 1993")
    wing = ("машинно-верифицированное крыло choptuik_ac_bc" if ru else
            "a machine-verified wing of choptuik_ac_bc")
    W, H = 1600, 320
    cx, cy = 1450, 160
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/>
    </linearGradient>
    <radialGradient id="core" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{core}"/>
      <stop offset="0.35" stop-color="{GOLD}" stop-opacity="0.85"/>
      <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  {rings(cx, cy, [26, 58, 92, 128, 166, 206, 248], GOLD, [0.95, 0.7, 0.5, 0.36, 0.25, 0.16, 0.09])}
  <circle cx="{cx}" cy="{cy}" r="64" fill="url(#core)"/>
  {dial_slots(cx, cy, 166)}
  <text x="64" y="128" font-family="Georgia, 'Times New Roman', serif" font-size="58"
        fill="{txt}" letter-spacing="10">SEPTINAL</text>
  <text x="66" y="176" font-family="Verdana, DejaVu Sans, sans-serif" font-size="21"
        fill="{GOLD}">{tagline}</text>
  <text x="66" y="216" font-family="Verdana, DejaVu Sans, sans-serif" font-size="16"
        fill="{sub}">{meta}</text>
  <text x="66" y="262" font-family="Verdana, DejaVu Sans, sans-serif" font-size="13"
        fill="{sub}" opacity="0.8">{wing}</text>
</svg>'''


def section(title, subtitle, accent, dark=True) -> str:
    bg1, bg2 = ("#05060C", "#101a30") if dark else ("#F4F0E6", "#EFE9DC")
    txt = "#F1F5F9" if dark else "#2B2A28"
    sub = "#94A3B8" if dark else "#6B6455"
    W, H = 1600, 140
    cx, cy = 1530, 70
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{bg1}"/><stop offset="1" stop-color="{bg2}"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect x="0" y="0" width="10" height="{H}" fill="{accent}"/>
  {rings(cx, cy, [22, 44, 68, 94], accent, [0.8, 0.5, 0.3, 0.15])}
  <text x="48" y="62" font-family="Georgia, 'Times New Roman', serif" font-size="34"
        fill="{txt}">{title}</text>
  <text x="50" y="98" font-family="Verdana, DejaVu Sans, sans-serif" font-size="15"
        fill="{sub}">{subtitle}</text>
</svg>'''


def logo(dark=True) -> str:
    bg = "none"
    txt = "#F1F5F9" if dark else "#2B2A28"
    core = GOLD_CORE if dark else "#8A6A24"
    W, H = 640, 240
    cx, cy = 120, 120
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{bg}"/>
  {rings(cx, cy, [30, 62, 94, 104], GOLD, [0.95, 0.65, 0.4, 0.2])}
  <circle cx="{cx}" cy="{cy}" r="42" fill="url(#g)"/>
  <defs>
    <radialGradient id="g" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{core}"/>
      <stop offset="0.4" stop-color="{GOLD}" stop-opacity="0.8"/>
      <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  {dial_slots(cx, cy, 94)}
  <text x="248" y="118" font-family="Georgia, 'Times New Roman', serif" font-size="52"
        fill="{txt}" letter-spacing="8">SEPTINAL</text>
  <text x="250" y="156" font-family="Verdana, DejaVu Sans, sans-serif" font-size="17"
        fill="{GOLD}">24 - 2 = 22   ·   Lean 4   ·   seed 1993</text>
</svg>'''


def main() -> None:
    (OUT / "banners").mkdir(parents=True, exist_ok=True)
    (OUT / "logo").mkdir(parents=True, exist_ok=True)
    files = {
        "banners/banner_header.svg": header(True),
        "banners/banner_header_light.svg": header(False),
        "banners/banner_header_ru.svg": header(True, ru=True),
        "banners/banner_theorems.svg": section("Theorem atlas",
                                               "every headline theorem, its module and its axiom line",
                                               GOLD),
        "banners/banner_theorems_ru.svg": section("Атлас теорем",
                                                  "каждая заголовочная теорема, её модуль и её аксиомная строка",
                                                  GOLD),
        "banners/banner_bridge.svg": section("The certificate bridge",
                                             "Python produces rational certificates - Lean checks and discharges them",
                                             CYAN),
        "banners/banner_bridge_ru.svg": section("Сертификатный мост",
                                                "Python выдаёт рациональные сертификаты - Lean проверяет и разряжает их",
                                                CYAN),
        "banners/banner_satellite.svg": section("The Septinial braking satellite",
                                                "24 slots - gap 2 - k = 22 = b2(K3) - PSL(2,7) - the Klein quartic",
                                               VIOLET),
        "banners/banner_satellite_ru.svg": section("Септинальный тормозной спутник",
                                                   "24 слота - зазор 2 - k = 22 = b2(K3) - PSL(2,7) - квартика Клейна",
                                                   VIOLET),
        "banners/banner_data.svg": section("Data &amp; calculations",
                                           "deterministic, seed 1993 - every number regenerable, every claim pinned",
                                           GREEN),
        "banners/banner_data_ru.svg": section("Данные и вычисления",
                                              "детерминизм, seed 1993 - каждое число регенерируемо, каждое утверждение пришпилено",
                                              GREEN),
        "logo/logo_dark.svg": logo(True),
        "logo/logo_light.svg": logo(False),
    }
    for rel, svg in files.items():
        (OUT / rel).write_text(svg)
        print(f"[svg] assets/{rel}")


if __name__ == "__main__":
    main()
