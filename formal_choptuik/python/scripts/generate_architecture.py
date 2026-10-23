"""Render the Lean<->Python bridge architecture diagram (Playwright + CSS).

Phased-vertical layout (charts skill Layout C): four layer cards stacked
top to bottom, arrows only between adjacent layers, low-saturation fills,
2px saturated borders.  Variants: en-dark (repo), en-light / ru-light
(monographs).

    python scripts/generate_architecture.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BUILD = Path("/home/z/my-project/scripts/build")

TEXT = {
    "en": {
        "title": "formal_choptuik — system architecture",
        "subtitle": "Lean owns the proof · Python owns the numbers · ZeroMQ owns the border",
        "l1": "LAYER 1 · PROOF SUBSTRATE",
        "l1s": "Lean 4 + mathlib — machine-checked theory",
        "l1c": ["Choptuik.Geometry", "Choptuik.Analysis", "Choptuik.Existence",
                "Choptuik.Stability", "Choptuik.Scaling"],
        "l2": "LAYER 2 · BRIDGE",
        "l2s": "JSON over ZeroMQ · REQ/REP · tcp://127.0.0.1:5557",
        "l2c": ["ping", "spectrum", "scaling_fit", "echo_period", "evolve", "interval_bound"],
        "l3": "LAYER 3 · NUMERICAL SERVICE",
        "l3s": "python/choptuik_service — deterministic, seed 1993",
        "l3c": ["evolver.py — mode model", "spectrum.py — linearized operator",
                "interval_checks.py — strict bounds", "server.py — REP loop",
                "pytest — 14 protocol tests"],
        "l4": "LAYER 4 · VERIFIED ARTIFACTS",
        "l4s": "everything regenerates from one command",
        "l4c": ["data/*.csv", "figures/*.png", "assets/gifs/*.gif", "monographs/*"],
        "a1": "numerical certificates as proof seeds",
        "a2": "JSON request / response",
        "a3": "datasets · plots · animations",
        "loop": "numerical seed → implicit-function theorem → formal existence proof",
    },
    "ru": {
        "title": "formal_choptuik — архитектура системы",
        "subtitle": "Lean отвечает за доказательство · Python — за вычисления · ZeroMQ — за границу",
        "l1": "СЛОЙ 1 · СИСТЕМА ДОКАЗАТЕЛЬСТВ",
        "l1s": "Lean 4 + mathlib — машинно-проверяемая теория",
        "l1c": ["Choptuik.Geometry", "Choptuik.Analysis", "Choptuik.Existence",
                "Choptuik.Stability", "Choptuik.Scaling"],
        "l2": "СЛОЙ 2 · МОСТ",
        "l2s": "JSON поверх ZeroMQ · REQ/REP · tcp://127.0.0.1:5557",
        "l2c": ["ping", "spectrum", "scaling_fit", "echo_period", "evolve", "interval_bound"],
        "l3": "СЛОЙ 3 · ЧИСЛЕННЫЙ СЕРВИС",
        "l3s": "python/choptuik_service — детерминированный, seed 1993",
        "l3c": ["evolver.py — модовая модель", "spectrum.py — линеаризованный оператор",
                "interval_checks.py — строгие оценки", "server.py — цикл REP",
                "pytest — 14 протокольных тестов"],
        "l4": "СЛОЙ 4 · ПРОВЕРЕННЫЕ АРТЕФАКТЫ",
        "l4s": "всё воспроизводится одной командой",
        "l4c": ["data/*.csv", "figures/*.png", "assets/gifs/*.gif", "monographs/*"],
        "a1": "численные сертификаты как затравки доказательства",
        "a2": "JSON-запрос / ответ",
        "a3": "данные · графики · анимации",
        "loop": "численная затравка → теорема о неявной функции → формальное доказательство существования",
    },
}

THEMES = {
    "dark": {
        "bg": "#0F172A", "card": "#141F44", "text": "#F1F5F9", "muted": "#94A3B8",
        "gold": "#E8B44A", "violet": "#9B8CDE", "cyan": "#4CC9F0",
        "fill_gold": "#1C1812", "fill_violet": "#1A2444", "fill_cyan": "#122036",
        "arrow": "#7E86A8",
    },
    "light": {
        "bg": "#FAF8F4", "card": "#FFFFFF", "text": "#2B2A28", "muted": "#6B6455",
        "gold": "#B08A3E", "violet": "#7A6BC0", "cyan": "#3E93B5",
        "fill_gold": "#F5EFDF", "fill_violet": "#EFECF8", "fill_cyan": "#E8F1F5",
        "arrow": "#8A8272",
    },
}


def build_html(lang: str, theme: str) -> str:
    t, T = TEXT[lang], THEMES[theme]
    chips1 = "".join(f'<span class="chip" style="border-color:{T["violet"]};color:{T["text"]};background:{T["fill_violet"]}">{c}</span>' for c in t["l1c"])
    chips2 = "".join(f'<span class="chip mono" style="border-color:{T["cyan"]};color:{T["text"]};background:{T["fill_cyan"]}">{c}</span>' for c in t["l2c"])
    chips3 = "".join(f'<span class="chip" style="border-color:{T["gold"]};color:{T["text"]};background:{T["fill_gold"]}">{c}</span>' for c in t["l3c"])
    chips4 = "".join(f'<span class="chip mono" style="border-color:{T["muted"]};color:{T["text"]};background:transparent">{c}</span>' for c in t["l4c"])
    return f"""<!DOCTYPE html>
<html lang="{lang}"><head><meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ width:1180px; background:{T["bg"]}; font-family:'DejaVu Sans','Segoe UI',sans-serif;
         padding:36px 44px 30px; }}
  .hd {{ text-align:center; margin-bottom:26px; }}
  .hd h1 {{ font-size:25px; color:{T["text"]}; font-weight:700; letter-spacing:.4px; }}
  .hd p  {{ font-size:13.5px; color:{T["muted"]}; margin-top:7px; font-style:italic; }}
  .layer {{ border-radius:14px; padding:16px 22px 18px; border:2px solid; background:{T["card"]}; }}
  .layer h2 {{ font-size:14.5px; letter-spacing:1.6px; font-weight:800; }}
  .layer .sub {{ font-size:12.5px; color:{T["muted"]}; margin:4px 0 12px; }}
  .chips {{ display:flex; flex-wrap:wrap; gap:8px; }}
  .chip {{ font-size:12.5px; padding:6px 13px; border-radius:9px; border:1.6px solid; }}
  .mono {{ font-family:'DejaVu Sans Mono','Courier New',monospace; font-size:12px; }}
  .arrowrow {{ display:flex; align-items:center; justify-content:center; gap:14px; padding:7px 0; }}
  .arrowrow svg {{ display:block; }}
  .arrowrow .lbl {{ font-size:12px; color:{T["muted"]}; }}
  .loop {{ margin-top:14px; text-align:center; font-size:12.5px; color:{T["violet"]};
          border:1.6px dashed {T["violet"]}; border-radius:10px; padding:9px 14px;
          background:transparent; }}
</style></head><body>
  <div class="hd"><h1>{t["title"]}</h1><p>{t["subtitle"]}</p></div>

  <div class="layer" style="border-color:{T["violet"]}">
    <h2 style="color:{T["violet"]}">{t["l1"]}</h2>
    <div class="sub">{t["l1s"]}</div>
    <div class="chips">{chips1}</div>
  </div>

  <div class="arrowrow">
    <svg width="26" height="30"><line x1="13" y1="0" x2="13" y2="20" stroke="{T["arrow"]}" stroke-width="2"/><polygon points="7,19 19,19 13,29" fill="{T["arrow"]}"/></svg>
    <span class="lbl">{t["a2"]}</span>
  </div>

  <div class="layer" style="border-color:{T["cyan"]}">
    <h2 style="color:{T["cyan"]}">{t["l2"]}</h2>
    <div class="sub">{t["l2s"]}</div>
    <div class="chips">{chips2}</div>
  </div>

  <div class="arrowrow">
    <svg width="26" height="30"><line x1="13" y1="0" x2="13" y2="20" stroke="{T["arrow"]}" stroke-width="2"/><polygon points="7,19 19,19 13,29" fill="{T["arrow"]}"/></svg>
    <span class="lbl">{t["a3"]}</span>
  </div>

  <div class="layer" style="border-color:{T["gold"]}">
    <h2 style="color:{T["gold"]}">{t["l3"]}</h2>
    <div class="sub">{t["l3s"]}</div>
    <div class="chips">{chips3}</div>
  </div>

  <div class="arrowrow">
    <svg width="26" height="30"><line x1="13" y1="0" x2="13" y2="20" stroke="{T["arrow"]}" stroke-width="2"/><polygon points="7,19 19,19 13,29" fill="{T["arrow"]}"/></svg>
    <span class="lbl">{t["a1"]}</span>
  </div>

  <div class="layer" style="border-color:{T["muted"]}">
    <h2 style="color:{T["muted"]}">{t["l4"]}</h2>
    <div class="sub">{t["l4s"]}</div>
    <div class="chips">{chips4}</div>
  </div>

  <div class="loop">↺&nbsp; {t["loop"]}</div>
</body></html>"""


def render(lang: str, theme: str, out: Path) -> None:
    html_path = BUILD / f"arch_{lang}_{theme}.html"
    html_path.write_text(build_html(lang, theme), encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1180, "height": 900},
                                device_scale_factor=2)
        page.goto(html_path.as_uri())
        page.wait_for_timeout(250)
        box = page.evaluate("""() => {
            const loop = document.querySelector('.loop').getBoundingClientRect();
            const b = document.body;
            return {w: Math.max(b.scrollWidth, document.documentElement.scrollWidth),
                    h: Math.ceil(loop.bottom + 30)};
        }""")
        page.set_viewport_size({"width": box["w"], "height": box["h"]})
        page.wait_for_timeout(120)
        page.screenshot(path=str(out), full_page=True)
        browser.close()
    print(f"  {out.name}  ({box['w']}x{box['h']} css px @2x)")


if __name__ == "__main__":
    BUILD.mkdir(parents=True, exist_ok=True)
    render("en", "dark", ROOT_FIGURES := Path("/home/z/my-project/download/formal_choptuik/figures/fig_architecture.png"))
    render("en", "light", BUILD / "fig_architecture_en.png")
    render("ru", "light", BUILD / "fig_architecture_ru.png")
    print("architecture diagrams done")
