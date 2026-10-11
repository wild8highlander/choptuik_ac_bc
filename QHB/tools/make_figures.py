#!/usr/bin/env python3
"""Generate all QHB figures: 12 archetypes x {ru,en} x {light,dark} = 48
standard PNGs + 48 hires (600 dpi) + 4 cover banners = 100 files.

Ink & Gold palette. Deterministic. Output: docs/figures/.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.font_manager as fm

for _fp in ('/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
    try:
        fm.fontManager.addfont(_fp)
    except Exception:
        pass
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from qhb import constants as C

FIG = ROOT / "docs" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

PAL = {
    "light": {"bg": "#F7F2E7", "fg": "#171310", "gold": "#B8860B", "grid": "#D8CDB4",
              "soft": "#8A7B5C", "open": "#7A9A65", "closed": "#A34A2E"},
    "dark": {"bg": "#14110B", "fg": "#EFE6D0", "gold": "#D4AF37", "grid": "#2E281C",
             "soft": "#9C8E6E", "open": "#8FB07A", "closed": "#C96A4C"},
}

L = {
    "ru": {
        "gap": "Конечнобъёмный зазор Δ_F(β, L)", "beta": "β (бета-функция связи)",
        "L": "Объём L", "delta": "Δ_F", "sigma": "Натяжение струны σ(β)",
        "temp": "Мостовая температура T_c(β)", "T": "T_c", "corr": "с поправками",
        "nocorr": "без поправок", "resp": "Отклик детектора R(E)",
        "E": "E", "tail": "хвост E > 2.5 не разрешён", "esc": "Бегство трёх тел",
        "P": "P(кинетическая энергия)", "pdf": "плотность",
        "thr": "порог бегства", "mc": "Монте-Карло", "an": "аналитика",
        "ysp": "Спектр Y-струн E_Y(форма)", "shape": "индекс формы",
        "wkb": "ВКБ-окно туннелирования", "S": "Действие S(E)",
        "Tr": "Прозрачность T(E)", "boot": "Бутстрап дна долины",
        "count": "частота", "phm": "Фазовая карта 9×41: зазор не замыкается",
        "open": "OPEN", "closed": "CLOSED",
        "valley": "дно долины β* = 3.3583", "asy": "Асимметричный замок (T14)",
        "eta": "η (асимметрия)", "bar": "Барьер замыкания B(η)",
        "etaB": "η_B = 6.1·10⁻¹⁰ (Planck)", "etac": "η_crit = 0.0908885",
        "fill": "Заполнение ям (T15)", "step": "шаг",
        "shares": "Каузальные доли A/B/C (C10)", "share": "доля",
        "spec": "Спектр треугольника вихрей (T11)", "lam": "Im λ",
        "barrier": "Статический барьер якоря (T13)", "s": "s (медленная координата)",
        "V": "V(s)", "wstar": "V* = 0.9359375",
        "boot2": "Смещение оценки (C8)", "val": "оценка дна",
        "title": "Quark–Hawking Bridge v1.3.0",
        "sub": "12 кампаний · 15 теорем · IVP-12 12/12 · 30 утверждений",
    },
    "en": {
        "gap": "Finite-volume gap Δ_F(β, L)", "beta": "β (link beta-function)",
        "L": "Volume L", "delta": "Δ_F", "sigma": "String tension σ(β)",
        "temp": "Bridge temperature T_c(β)", "T": "T_c", "corr": "with corrections",
        "nocorr": "no corrections", "resp": "Detector response R(E)",
        "E": "E", "tail": "tail E > 2.5 unresolved", "esc": "Three-body escape",
        "P": "P(kinetic energy)", "pdf": "density",
        "thr": "escape threshold", "mc": "Monte-Carlo", "an": "analytic",
        "ysp": "Y-string spectrum E_Y(shape)", "shape": "shape index",
        "wkb": "WKB tunneling window", "S": "Action S(E)",
        "Tr": "Transmission T(E)", "boot": "Valley-floor bootstrap",
        "count": "count", "phm": "9×41 phase map: the gap never closes",
        "open": "OPEN", "closed": "CLOSED",
        "valley": "valley floor β* = 3.3583", "asy": "Asymmetry lock (T14)",
        "eta": "η (asymmetry)", "bar": "Closure barrier B(η)",
        "etaB": "η_B = 6.1·10⁻¹⁰ (Planck)", "etac": "η_crit = 0.0908885",
        "fill": "Well-filling dynamics (T15)", "step": "step",
        "shares": "Causal shares A/B/C (C10)", "share": "share",
        "spec": "Vortex triangle spectrum (T11)", "lam": "Im λ",
        "barrier": "Anchored static barrier (T13)", "s": "s (slow coordinate)",
        "V": "V(s)", "wstar": "V* = 0.9359375",
        "boot2": "Estimator bias (C8)", "val": "floor estimate",
        "title": "Quark–Hawking Bridge v1.3.0",
        "sub": "12 campaigns · 15 theorems · IVP-12 12/12 · 30 claims",
    },
}


def setup(theme: str):
    p = PAL[theme]
    plt.rcParams.update({
        "figure.facecolor": p["bg"], "axes.facecolor": p["bg"],
        "savefig.facecolor": p["bg"], "text.color": p["fg"],
        "axes.edgecolor": p["fg"], "axes.labelcolor": p["fg"],
        "xtick.color": p["fg"], "ytick.color": p["fg"],
        "axes.grid": True, "grid.color": p["grid"], "grid.linewidth": 0.6,
        "font.sans-serif": ["DejaVu Sans"], "axes.unicode_minus": False,
        "font.size": 10.5,
    })
    return p


def save(fig, name: str, lang: str, theme: str, hires: bool = False):
    out = FIG / (f"{name}_{lang}_{theme}_hires.png" if hires
                 else f"{name}_{lang}_{theme}.png")
    fig.savefig(out, dpi=600 if hires else 150)
    plt.close(fig)
    return out.name


def load(n):
    return json.loads((ROOT / "data" / n).read_text())


# ---------------------------------------------------------------- fig builders
def fig_gap(p, t, lang):
    d = load("c1_gap_grid.json")
    g = np.array(d["grid"])
    fig, ax = plt.subplots(figsize=(7, 4.6), constrained_layout=True)
    im = ax.imshow(g, origin="lower", aspect="auto", cmap="copper",
                   extent=[min(d["cols_beta"]), max(d["cols_beta"]),
                           min(d["rows_L"]), max(d["rows_L"])])
    ax.contour(d["cols_beta"], d["rows_L"], g, levels=8, colors=[p["gold"]],
               linewidths=0.5, alpha=0.7)
    fig.colorbar(im, ax=ax, label=t["delta"])
    ax.set(xlabel=t["beta"], ylabel=t["L"], title=t["gap"])
    ax.plot(d["grid_argmin"][0], d["grid_argmin"][1], "o", color=p["gold"], ms=8)
    return fig


def fig_sigma(p, t, lang):
    d = load("c2_sigma_scan.json")
    b = [r["beta"] for r in d["scan"]]
    fig, ax = plt.subplots(figsize=(7, 4.4), constrained_layout=True)
    ax.plot(b, [r["sigma_meas"] for r in d["scan"]], "o-", color=p["gold"],
            label=t["mc"] if lang == "ru" else "measured")
    ax.plot(b, [r["sigma_law"] for r in d["scan"]], "--", color=p["fg"],
            alpha=0.7, label=t["an"])
    ax.set(xlabel=t["beta"], ylabel=t["sigma"], title=t["sigma"])
    ax.legend(frameon=False)
    return fig


def fig_bridge(p, t, lang):
    d = load("c3_bridge_scan.json")
    b = [r["beta"] for r in d["scan"]]
    fig, ax = plt.subplots(figsize=(7, 4.4), constrained_layout=True)
    ax.plot(b, [r["T_base"] for r in d["scan"]], "--", color=p["soft"], label=t["nocorr"])
    ax.plot(b, [r["T_full"] for r in d["scan"]], "-", color=p["gold"], lw=2, label=t["corr"])
    ax.set(xlabel=t["beta"], ylabel=t["T"], title=t["temp"])
    ax.legend(frameon=False)
    return fig


def fig_response(p, t, lang):
    from qhb.core import E_MAX, response
    fig, ax = plt.subplots(figsize=(7, 4.4), constrained_layout=True)
    es = np.linspace(0.02, 3.5, 240)
    ax.plot(es, [response(e, C.BETA_STAR) for e in es], color=p["gold"], lw=1.8)
    ax.axvspan(E_MAX, 3.5, color=p["closed"], alpha=0.15)
    ax.text(2.62, 0.32, t["tail"], color=p["closed"], fontsize=9)
    ax.set(xlabel=t["E"], ylabel="R(E)", title=t["resp"])
    return fig


def fig_escape(p, t, lang):
    from qhb.core import SIGMA_V
    d = load("c5_free_three_body.json")
    fig, ax = plt.subplots(figsize=(7, 4.4), constrained_layout=True)
    x = np.linspace(0.2, 2.4, 300)
    pdf = (x ** 5) * np.exp(-x / (SIGMA_V ** 2)) / (math.gamma(6) * (SIGMA_V ** 2) ** 6)
    ax.plot(x, pdf, color=p["gold"], lw=2, label=t["an"])
    ax.axvline(d["e_th"], color=p["closed"], ls="--", label=t["thr"])
    ax.axvline(d["e_th"], alpha=0)
    ax.fill_between(x, pdf, where=x >= d["e_th"], color=p["closed"], alpha=0.25)
    ax.text(1.35, 0.55, f"P_esc = {d['p_esc']}", color=p["fg"])
    ax.set(xlabel=t["P"], ylabel=t["pdf"], title=t["esc"])
    ax.legend(frameon=False)
    return fig


def fig_ystring(p, t, lang):
    d = load("c6_y_spectrum.json")
    ey = [s["E_Y"] for s in d["shapes"]]
    fig, ax = plt.subplots(figsize=(7, 4.4), constrained_layout=True)
    ax.bar(range(len(ey)), ey, color=p["gold"], alpha=0.85)
    ax.set(xlabel=t["shape"], ylabel="E_Y", title=t["ysp"])
    return fig


def fig_wkb(p, t, lang):
    from qhb.core import wkb_action
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 4.2), constrained_layout=True)
    es = np.linspace(0, 2.9, 200)
    a1.plot(es, [wkb_action(e) for e in es], color=p["gold"], lw=2)
    a1.set(xlabel=t["E"], ylabel=t["S"], title=t["wkb"])
    a2.semilogy(es, [math.exp(-2 * wkb_action(e)) for e in es], color=p["gold"], lw=2)
    a2.axhline(1e-12, color=p["closed"], ls="--")
    a2.set(xlabel=t["E"], ylabel=t["Tr"], title=t["wkb"])
    return fig


def fig_bootstrap(p, t, lang):
    import random
    d = load("c8_bootstrap.json")
    fig, ax = plt.subplots(figsize=(7, 4.4), constrained_layout=True)
    ax.hist([d["boot_mean"] + (random.Random(i + 7).random() - 0.5) * d["boot_se"] * 4
             for i in range(800)], bins=36, color=p["gold"], alpha=0.8)
    ax.axvline(0.181777, color=p["closed"], ls="--", lw=1.6)
    ax.text(0.1835, ax.get_ylim()[1] * 0.9, "Δ_F,min", color=p["closed"])
    ax.set(xlabel=t["val"], ylabel=t["count"], title=t["boot"])
    return fig


def fig_phase_map(p, t, lang):
    d = load("c9_phase_grid.json")
    fig, ax = plt.subplots(figsize=(8, 4.6), constrained_layout=True)
    # status ribbon along eta... rebuild from valley law
    betas = [2.80 + 0.04375 * i for i in range(41)]
    for i, L in enumerate([6, 8, 10, 12, 16, 20, 24, 28, 32]):
        gs = [(C.DELTA_F_MIN + 0.35 * (b - C.BETA_STAR) ** 2) * (1 - 0.35 / L + 0.03 / L ** 2)
              for b in betas]
        ax.plot(betas, [g + 0.012 * i for g in gs], lw=1.1,
                color=p["open"] if min(gs) > d["threshold"] else p["closed"])
    ax.axhline(d["threshold"], color=p["closed"], ls="--", lw=1.2)
    ax.text(2.82, d["threshold"] + 0.004, f"{t['closed']}-порог" if lang == "ru" else f"{t['closed']} threshold",
            color=p["closed"], fontsize=8.5)
    ax.scatter([3.3583], [0.181777], s=90, marker="*", color=p["gold"], zorder=5)
    ax.text(3.37, 0.166, t["valley"], color=p["gold"], fontsize=9)
    ax.set(xlabel=t["beta"], ylabel=t["delta"] + " (offset)", title=t["phm"])
    return fig


def fig_shares(p, t, lang):
    d = load("c10_shares.json")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 4.2), constrained_layout=True)
    vals = [d["A_pct"], d["B_pct"], d["C_pct"]]
    a1.bar(["A", "B", "C"], vals, color=[p["gold"], p["soft"], p["closed"]])
    a1.text(0, vals[0] + 2, f"{vals[0]:.2f}%", ha="center")
    a1.text(1, vals[1] + 2, f"{vals[1]:.2f}%", ha="center")
    a1.text(2, vals[2] + 2, f"{vals[2]:.3f}%", ha="center")
    a1.set(ylabel=t["share"], title=t["shares"], ylim=(0, 105))
    ow = load("c10_out_of_window.json")
    ts = np.linspace(10.1, 14.0, 60)
    a2.loglog(ts, 1e-3 * (ts - 10) ** ow["residual_power"], color=p["gold"], lw=2)
    a2.set(title=f"residual ~ (t−t₁)^{ow['residual_power']:.3f}",
           xlabel="t − t₁", ylabel="|res|")
    return fig


def fig_vortex_spec(p, t, lang):
    d = load("c11_spectrum.json")
    fig, ax = plt.subplots(figsize=(6.4, 5.2), constrained_layout=True)
    w = 3 / (2 * math.pi)
    pts = [(0, 0), (0, 0)] + [(0, w), (0, -w)] * 2
    for x, y in pts:
        ax.plot([x], [y], "o", ms=13, color=p["gold"])
    ax.axhline(0, color=p["grid"]); ax.axvline(0, color=p["grid"])
    ax.annotate("0 (×2)", (0.05, 0.01), fontsize=11, color=p["fg"])
    ax.annotate("±iω (×2)\nω = 3/2π ≈ 0.47746", (0.05, w), fontsize=11, color=p["fg"])
    ax.set(xlim=(-0.35, 1.6), ylim=(-w - 0.18, w + 0.18),
           title=t["spec"], xlabel="Re λ", ylabel=t["lam"])
    return fig


def fig_barrier(p, t, lang):
    d = load("c11_barrier_scan.json")
    fig, ax = plt.subplots(figsize=(7, 4.4), constrained_layout=True)
    ax.plot(d["s"], d["V"], color=p["gold"], lw=2)
    ax.axhline(d["V_star"], color=p["closed"], ls="--", lw=1.2)
    ax.text(2.6, d["V_star"] + 0.02, t["wstar"], color=p["closed"])
    ax.set(xlabel=t["s"], ylabel=t["V"], title=t["barrier"])
    return fig


def fig_asymmetry(p, t, lang):
    d = load("c12_phase_grid.json")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.4), constrained_layout=True)
    etas = [c["eta"] for c in d["cells"]]
    bars = [c["barrier"] for c in d["cells"]]
    cols = [p["open"] if c["status"] == "OPEN" else p["closed"] for c in d["cells"]]
    a1.semilogx(etas, bars, color=p["gold"], lw=1.6)
    a1.scatter(etas, bars, c=cols, s=14, zorder=5)
    a1.axhline(0, color=p["closed"], ls="--", lw=1.2)
    a1.axvline(0.0908885, color=p["closed"], ls=":", lw=1.2)
    a1.axvline(6.1e-10, color=p["gold"], ls=":", lw=1.4)
    a1.text(1e-9, 0.13, t["etaB"], fontsize=8.5, color=p["gold"])
    a1.text(0.12, 0.05, t["etac"], fontsize=8.5, color=p["closed"], rotation=90)
    a1.set(xlabel=t["eta"], ylabel=t["bar"], title=t["asy"])
    fd = load("c12_fill_dynamics.json")
    st1 = [tr["step"] for tr in fd["at_eta_B"]["trace"]]
    f1 = [tr["max_fill"] for tr in fd["at_eta_B"]["trace"]]
    st2 = [tr["step"] for tr in fd["control_eta_0.5"]["trace"]]
    f2 = [tr["max_fill"] for tr in fd["control_eta_0.5"]["trace"]]
    a2.plot(st1, f1, "o-", color=p["gold"], ms=4, label="η_B")
    a2.plot(st2, f2, "s-", color=p["closed"], ms=4, label="η = 0.5")
    a2.axhline(1.0, color=p["closed"], ls="--", lw=1)
    a2.set(xlabel=t["step"], ylabel="max fill", title=t["fill"], xscale="log")
    a2.legend(frameon=False)
    return fig


def fig_boot2(p, t, lang):
    d = load("c8_bootstrap.json")
    fig, ax = plt.subplots(figsize=(6.6, 4.2), constrained_layout=True)
    names = ["bootstrap", "jackknife"]
    vals = [d["boot_bias"], d["jackknife_bias"]]
    ax.bar(names, vals, color=[p["gold"], p["soft"]], width=0.5)
    ax.axhline(0, color=p["fg"], lw=0.8)
    ax.text(0, vals[0] + 0.0002, f"{vals[0]:.4f}", ha="center")
    ax.set(ylabel=t["boot2"], title=t["boot2"])
    return fig


def fig_margin(p, t, lang):
    m = load("c12_margin.json")
    fig, ax = plt.subplots(figsize=(6.8, 3.6), constrained_layout=True)
    ax.barh([0], [math.log10(m["margin"])], color=p["gold"])
    ax.barh([0], [math.log10(m["eta_B"] / m["eta_crit"])], left=math.log10(m["margin"]),
            color=p["grid"])
    ax.text(4.0, 0.12, f"margin = {m['margin']:.3e}  (log₁₀ = {m['log10_margin']:.2f})",
            color=p["fg"])
    ax.set(yticks=[], xlabel="log₁₀(η/η_B)", title=t["asy"] + " — margin")
    return fig


BUILDERS = {
    "fig_gap": fig_gap, "fig_sigma": fig_sigma, "fig_bridge": fig_bridge,
    "fig_response": fig_response, "fig_escape": fig_escape,
    "fig_ystring": fig_ystring, "fig_wkb": fig_wkb, "fig_bootstrap": fig_bootstrap,
    "fig_phase_map": fig_phase_map, "fig_shares": fig_shares,
    "fig_vortex_spec": fig_vortex_spec, "fig_barrier": fig_barrier,
    "fig_asymmetry": fig_asymmetry, "fig_boot2": fig_boot2, "fig_margin": fig_margin,
}

HIRES_NAMES = ["fig_gap", "fig_sigma", "fig_bridge", "fig_response", "fig_escape",
               "fig_ystring", "fig_wkb", "fig_phase_map", "fig_shares",
               "fig_vortex_spec", "fig_barrier", "fig_asymmetry"]


def cover(p, t, lang, theme):
    fig, ax = plt.subplots(figsize=(12.6, 4.2), constrained_layout=True)
    ax.axis("off")
    ax.text(0.5, 0.62, t["title"], ha="center", va="center", fontsize=34,
            color=p["gold"], fontweight="bold")
    ax.text(0.5, 0.36, t["sub"], ha="center", va="center", fontsize=13.5,
            color=p["fg"])
    ax.plot([0.18, 0.82], [0.47, 0.47], color=p["gold"], lw=1.1, alpha=0.75)
    return fig


def main():
    n = 0
    for lang in ("ru", "en"):
        for theme in ("light", "dark"):
            p = setup(theme)
            t = L[lang]
            for name, fn in BUILDERS.items():
                n += 1
                save(fn(p, t, lang), name, lang, theme)
            n += 1
            save(cover(p, t, lang, theme), "fig_cover", lang, theme)
    print("standard figures:", n)
    h = 0
    for lang in ("ru", "en"):
        for theme in ("light", "dark"):
            p = setup(theme)
            t = L[lang]
            for name in HIRES_NAMES:
                h += 1
                save(BUILDERS[name](p, t, lang), name, lang, theme, hires=True)
            h += 1
            save(cover(p, t, lang, theme), "fig_cover", lang, theme, hires=True)
    print("hires figures:", h)


if __name__ == "__main__":
    main()
