#!/usr/bin/env python3
"""Septinal · sepstyle.py — the shared rendering style of every figure,
animation and banner of the package.

Two themes, inherited from the parent programme ``choptuik_ac_bc``:

* ``dark``  — "cosmic" (GitHub README rendition);
* ``light`` — "Ink & Gold" (monograph rendition).

Everything rendered here is deterministic: no RNG at draw time; the
package seed 1993 is stamped into every output manifest.
"""

from __future__ import annotations

from pathlib import Path

SEED = 1993

THEMES = {
    "dark": {
        "bg": "#0F172A", "text": "#F1F5F9", "muted": "#94A3B8",
        "grid": "#1E293B", "band": "#16213C",
        "gold": "#E8B44A", "violet": "#9B8CDE", "cyan": "#4CC9F0",
        "red": "#E86A6A", "green": "#8FB7A4", "fit": "#F2DCA4",
        "core": "#FFE9B0",
    },
    "light": {
        "bg": "#FAF8F4", "text": "#2B2A28", "muted": "#6B6455",
        "grid": "#DDD6C8", "band": "#EFE9DC",
        "gold": "#B08A3E", "violet": "#7A6BC0", "cyan": "#3E93B5",
        "red": "#B05252", "green": "#6E9481", "fit": "#8A6A24",
        "core": "#7A5B14",
    },
}

L = {
    "en": {
        "scaling_title": "Mass scaling law  (log-log)",
        "scaling_ylabel": "ln M_BH", "scaling_xlabel": "ln |p - p*|",
        "scaling_fit": "fit slope = 1/lambda0 = 0.373902",
        "scaling_pub": "Choptuik 1993: 0.374",
        "scaling_wiggle": "DSS wiggle  (period 4.6074)",
        "echo_title": "DSS echoing  (Delta = 3.445452402)",
        "echo_amp": "central amplitude  A(tau)",
        "echo_profiles": "rescaled profiles coincide",
        "echo_one_period": "one echoing period",
        "spec_title": "Certified spectrum of the mode model",
        "spec_ylabel": "Im lambda", "spec_xlabel": "Re lambda",
        "spec_unstable": "lambda0 = 2.6745  (unstable)",
        "spec_decaying": "decaying pairs  Re = -(4.3 + 1.8k)",
        "spec_spacing": "echo spacing  2*pi/ln2 = 9.0647",
        "record_title": "The exact records vs the published constants",
        "record_gamma": "|gamma - 0.374| = 263/2674500 = 9.83e-5",
        "record_delta": "|Delta - 3.4453| = 1.52e-4",
        "record_gamma3": "gamma3 = b_Ch - pi/1200",
        "record_bch": "b_Ch = 1 - cos(2*pi/7)",
        "berry_title": "The Berry quantum  (two-level normal form)",
        "berry_lambda": "lambda_-(delta) = (1 - sqrt(1+2 delta^2))/2",
        "berry_first": "first order  -delta^2/2",
        "berry_bound": "remainder bound  delta^4/4",
        "dial_title": "The septinial dial  (24 slots, gap 2)",
        "dial_free": "free slots  (22)",
        "dial_gap": "antipodal gap  {0, 12}",
        "dial_left": "left arc  11", "dial_right": "right arc  11",
        "dial_triples": "8 antipodal triples (Klein quartic)",
        "lattice_title": "Subgroup lattice of PSL(2,7)",
        "lattice_ylabel": "number of subgroups",
        "lattice_xlabel": "subgroup order",
        "lattice_total": "179 subgroups total  -  14 x S4",
        "thm_title": "Theorem inventory of the two Lean libraries",
        "thm_ylabel": "top-level theorems",
        "collapse_sub": "subcritical: dispersal",
        "collapse_crit": "critical: echoing",
        "collapse_super": "supercritical: black hole",
        "collapse_mass": "BH mass",
        "collapse_time": "retarded time",
        "psi": "scalar field",
        "radius": "areal radius",
    },
    "ru": {
        "scaling_title": "Закон массового скейлинга  (log-log)",
        "scaling_ylabel": "ln M_BH", "scaling_xlabel": "ln |p - p*|",
        "scaling_fit": "наклон = 1/lambda0 = 0.373902",
        "scaling_pub": "Чоптуик 1993: 0.374",
        "scaling_wiggle": "DSS-виггля  (период 4.6074)",
        "echo_title": "DSS-эхо  (Delta = 3.445452402)",
        "echo_amp": "центральная амплитуда  A(tau)",
        "echo_profiles": "профили совпадают после rescale",
        "echo_one_period": "один период эха",
        "spec_title": "Сертифицированный спектр модовой модели",
        "spec_ylabel": "Im lambda", "spec_xlabel": "Re lambda",
        "spec_unstable": "lambda0 = 2.6745  (неустойчивая)",
        "spec_decaying": "затухающие пары  Re = -(4.3 + 1.8k)",
        "spec_spacing": "шаг эха  2*pi/ln2 = 9.0647",
        "record_title": "Точные рекорды против опубликованных констант",
        "record_gamma": "|gamma - 0.374| = 263/2674500 = 9.83e-5",
        "record_delta": "|Delta - 3.4453| = 1.52e-4",
        "record_gamma3": "gamma3 = b_Ch - pi/1200",
        "record_bch": "b_Ch = 1 - cos(2*pi/7)",
        "berry_title": "Квант Берри  (двухуровневая нормальная форма)",
        "berry_lambda": "lambda_-(delta) = (1 - sqrt(1+2 delta^2))/2",
        "berry_first": "первый порядок  -delta^2/2",
        "berry_bound": "граница остатка  delta^4/4",
        "dial_title": "Септинальный диск  (24 слота, зазор 2)",
        "dial_free": "свободные слоты  (22)",
        "dial_gap": "антиподальный зазор  {0, 12}",
        "dial_left": "левая дуга  11", "dial_right": "правая дуга  11",
        "dial_triples": "8 антиподальных триплетов (квартика Клейна)",
        "lattice_title": "Решётка подгрупп PSL(2,7)",
        "lattice_ylabel": "число подгрупп",
        "lattice_xlabel": "порядок подгруппы",
        "lattice_total": "всего 179 подгрупп  -  14 x S4",
        "thm_title": "Инвентарь теорем двух Lean-библиотек",
        "thm_ylabel": "теоремы верхнего уровня",
        "collapse_sub": "докритический: рассеяние",
        "collapse_crit": "критический: эхо",
        "collapse_super": "сверхкритический: чёрная дыра",
        "collapse_mass": "масса ЧД",
        "collapse_time": "запаздывающее время",
        "psi": "скалярное поле",
        "radius": "арейный радиус",
    },
}


def theme_colors(name: str) -> dict:
    return THEMES[name]


def labels(lang: str) -> dict:
    return L[lang]


def apply_theme(ax, T) -> None:
    ax.set_facecolor(T["bg"])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(T["muted"])
    ax.tick_params(colors=T["muted"], labelsize=8)
    ax.grid(True, color=T["grid"], lw=0.6, alpha=0.9)
    ax.xaxis.label.set_color(T["text"])
    ax.yaxis.label.set_color(T["text"])
    ax.title.set_color(T["text"])


def style_mpl(plt, dpi: int = 300) -> None:
    plt.rcParams.update({
        "figure.dpi": dpi, "savefig.dpi": dpi,
        "axes.unicode_minus": False,
    })


def out_path(base: Path, kind: str, theme: str, lang: str, name: str) -> Path:
    """dark+en -> <base>; monograph renditions -> subfolders."""
    if theme == "dark" and lang == "en":
        return base / f"{name}.{kind}"
    sub = base / f"monograph_{lang}" if theme == "light" else base / f"dark_{lang}"
    sub.mkdir(parents=True, exist_ok=True)
    return sub / f"{name}.{kind}"
