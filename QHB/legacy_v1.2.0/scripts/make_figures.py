# -*- coding: utf-8 -*-
"""
make_figures.py — the 7 committed figures x RU/EN x light/dark (300 dpi).

Every figure reads ONLY the rebuilt data/qhb tables and the committed
verdicts; nothing is recomputed here.  Ink & Gold identity via figstyle.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from figstyle import TOKENS, LANG, style, new_fig, finish
from qhb.bridge import T_H, equal_cmb_mass, equal_qcd_mass, T_QCD_K
from qhb.constants import T_CMB
from qhb.wu import residual

DATA = os.path.join(ROOT, "data", "qhb")
REF = os.path.join(ROOT, "campaigns", "reference")
FIGS = os.path.join(ROOT, "figures")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


# ----------------------------------------------------------------------------
# 1. the map
# ----------------------------------------------------------------------------
def fig_map(lang, tok, L, path):
    fig = new_fig(10.5, 6.2)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    def box(x, y, w, h, text, fc, ec, tc, fs=10.5):
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.09",
                           facecolor=fc, edgecolor=ec, linewidth=1.6)
        ax.add_patch(b)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, color=tc, wrap=True)

    def arrow(x1, y1, x2, y2, color):
        a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                            mutation_scale=16, color=color, linewidth=1.8)
        ax.add_patch(a)

    g, gs, ink, mut = tok["gold"], tok["gold_soft"], tok["ink"], tok["muted"]
    panel = tok["panel"]

    box(0.25, 4.6, 2.9, 1.2,
        "три поправки\n$\\pi/2,\\ \\pi/3,\\ \\pi/7$" if lang == "ru" else
        "three corrections\n$\\pi/2,\\ \\pi/3,\\ \\pi/7$",
        panel, ink, ink)
    box(3.9, 4.6, 2.9, 1.2,
        "динамический зазор\n$\\Delta_F = \\Delta_0 + B_2\\beta^2$" if lang == "ru"
        else "the dynamic gap\n$\\Delta_F = \\Delta_0 + B_2\\beta^2$",
        panel, g, ink, 11)
    box(7.55, 4.6, 2.7, 1.2,
        "стенка геометрии\n(вибрация)" if lang == "ru" else
        "the geometric wall\n(the vibration)",
        panel, g, ink)
    box(0.25, 2.5, 2.9, 1.2,
        "печка: ЧД при\nпланковской плотности" if lang == "ru" else
        "the furnace: BH at\nPlanck density",
        panel, ink, ink)
    box(3.9, 2.5, 2.9, 1.2,
        "пары Хокинга $e^-e^+$\n+ дверь Ву" if lang == "ru" else
        "Hawking pairs $e^-e^+$\n+ the Wu door",
        panel, ink, ink)
    box(7.55, 2.5, 2.7, 1.2,
        "три кварка = три тела\n(хаос без выхода)" if lang == "ru" else
        "three quarks = three bodies\n(chaos without exit)",
        panel, g, ink)
    box(2.6, 0.3, 5.3, 1.0,
        "КОНФАЙНМЕНТ: зазор + жёсткость трио" if lang == "ru" else
        "CONFINEMENT: the gap + the trio rigidity",
        g, g, tok["bg"] if lang == "en" else "#FAF7F0", 13)

    arrow(3.15, 5.2, 3.9, 5.2, ink)
    arrow(6.8, 5.2, 7.55, 5.2, g)
    arrow(1.7, 4.6, 1.7, 3.7, ink)
    arrow(3.15, 3.1, 3.9, 3.1, ink)
    arrow(6.8, 3.1, 7.55, 3.1, ink)
    arrow(8.9, 4.6, 8.9, 3.7, g)
    arrow(8.9, 2.5, 6.5, 1.35, g)
    arrow(5.35, 4.6, 5.35, 3.7, ink)
    ax.text(5.25, 5.95, L["map_title"], ha="center", fontsize=15,
            color=ink, fontweight="bold")
    ax.text(0.3, 0.05, "гипотеза пакета — помечена; T2–T10 — машинные законы"
            if lang == "ru" else
            "the package hypothesis — marked; T2–T10 — machine laws",
            fontsize=8.5, color=mut)
    finish(fig, path)


# ----------------------------------------------------------------------------
# 2. the gap law
# ----------------------------------------------------------------------------
def fig_gap(lang, tok, L, path):
    d = load("gap_scan_window.json")
    fig = new_fig()
    ax = fig.gca()
    b = np.array(d["beta"])
    g = np.array(d["gap"])
    wing_b = np.array(d["wing_betas"])
    wing_s = np.array(d["wing_shifts"])
    d0 = g[0]
    B2 = d["B2"]
    ax.axhline(d0, color=tok["muted"], lw=1.2, ls=":")
    ax.text(0.005, d0 + 2e-4, L["gap_delta0"], color=tok["muted"], fontsize=9)
    bw = np.linspace(0, 0.2, 100)
    ax.plot(b, g, "o", ms=5, color=tok["gold"], zorder=5)
    ax.plot(bw, d0 + B2 * bw ** 2, "-", lw=1.8, color=tok["ink"],
            label=L["gap_quad"])
    ax.axvspan(0.2, wing_b.max() + 0.05, color=tok["grid"], alpha=0.25)
    ax.plot(wing_b, d0 + wing_s, "s", ms=4.5, color=tok["muted"],
            label=L["gap_wing"])
    ax.axvline(0.2, color=tok["muted"], lw=1, ls="--")
    ax.text(0.1, d0 - 8e-3, L["gap_window"], ha="center", color=tok["muted"],
            fontsize=9)
    ax.set_xlabel(L["gap_x"])
    ax.set_ylabel(L["gap_y"])
    ax.set_title(L["gap_title"])
    ax.legend(loc="lower left", framealpha=0.0)
    finish(fig, path)


# ----------------------------------------------------------------------------
# 3. the trap
# ----------------------------------------------------------------------------
def fig_trap(lang, tok, L, path):
    with open(os.path.join(DATA, "trap_grid.csv"), encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")[1:]
    rows = [dict(zip(("V0", "Om", "P", "err", "alive"), ln.split(",")))
            for ln in lines]
    fig = new_fig()
    ax = fig.gca()
    omegas = sorted({float(r["Om"]) for r in rows})
    shades = [tok["ink"], tok["muted"], tok["gold"], tok["gold_soft"]]
    for i, om in enumerate(omegas):
        rr = sorted((r for r in rows if float(r["Om"]) == om),
                    key=lambda r: float(r["V0"]))
        v = np.array([float(r["V0"]) for r in rr])
        p = np.array([float(r["P"]) for r in rr])
        lab = f"$\\Omega = {om:g}$"
        # V0 = 0 cells are drawn at a small leftward offset so they stay
        # visible on the log axis (open diamonds = the free trio)
        vx = np.where(v == 0.0, 0.055, v)
        ax.plot(vx[1:], p[1:], "o-", ms=4.5, lw=1.6, color=shades[i % 4],
                label=lab)
        ax.plot([vx[0]], [p[0]], "o", mfc="none", ms=8, mew=1.8,
                color=shades[i % 4])
    ax.axhline(1 / math.e, color=tok["bad"], lw=1.2, ls="--")
    ax.text(0.9, 0.035, L["trap_one_e"], color=tok["bad"],
            fontsize=9)
    p_free = [float(r["P"]) for r in rows if float(r["V0"]) == 0][0]
    ax.axhline(p_free, color=tok["muted"], lw=1, ls=":")
    ax.text(0.9, p_free + 0.012, f'{L["trap_free"]}: {p_free:.3f}',
            color=tok["muted"], fontsize=9)
    ax.set_xscale("log")
    ax.set_xlim(0.045, 20)
    ax.set_ylim(-0.03, 0.32)
    ax.set_xlabel(L["trap_x"])
    ax.set_ylabel(L["trap_y"])
    ax.set_title(L["trap_title"])
    ax.legend(loc="center right", framealpha=0.0)
    finish(fig, path)


# ----------------------------------------------------------------------------
# 4. the Wu door
# ----------------------------------------------------------------------------
def fig_wu(lang, tok, L, path):
    fig = new_fig()
    ax = fig.gca()
    x = np.logspace(-2.3, 2.3, 300)
    alphas = [0.25, 0.5, 0.75, 0.9, 1.0]
    shades = [tok["muted"], tok["muted"], tok["ink"], tok["gold"],
              tok["gold_soft"]]
    for a, c in zip(alphas, shades):
        lw = 2.4 if a == 0.9 else 1.4
        ax.plot(x, [residual(a, xx) for xx in x], lw=lw, color=c,
                label=(f"$\\alpha = {a:g}$" + ("  (" + L["wu_anchor"] + ")"
                        if a == 0.9 else "")))
    ax.set_xscale("log")
    ax.set_xlabel(L["wu_x"])
    ax.set_ylabel(L["wu_y"])
    ax.set_title(L["wu_title"])
    ax.legend(loc="lower right", framealpha=0.0)
    finish(fig, path)


# ----------------------------------------------------------------------------
# 5. the two contact points
# ----------------------------------------------------------------------------
def fig_contacts(lang, tok, L, path):
    M = np.logspace(9, 24, 400)
    TH = np.array([T_H(m) for m in M])
    fig = new_fig()
    ax = fig.gca()
    ax.plot(M, TH, lw=1.8, color=tok["ink"])
    ax.axhline(T_CMB, color=tok["muted"], lw=1, ls=":")
    ax.axhline(T_QCD_K, color=tok["gold"], lw=1.2, ls=":")
    for Mc, lab, col in ((equal_qcd_mass(), L["qcd_contact"], tok["gold"]),
                         (equal_cmb_mass(), L["cmb_contact"], tok["muted"])):
        ax.plot([Mc], [T_H(Mc)], "o", ms=9, color=col, zorder=5)
        ax.annotate(f"{lab}\n$M = {Mc:.3e}$ кг" if lang == "ru" else
                    f"{lab}\n$M = {Mc:.3e}$ kg",
                    (Mc, T_H(Mc)), textcoords="offset points", xytext=(12, -8),
                    fontsize=9, color=col)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(L["contacts_x"])
    ax.set_ylabel(L["contacts_y"])
    ax.set_title(L["contacts_title"])
    finish(fig, path)


# ----------------------------------------------------------------------------
# 6. the floor law
# ----------------------------------------------------------------------------
def fig_floor(lang, tok, L, path):
    with open(os.path.join(DATA, "floor_ladder.csv"), encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")[1:]
    rows = []
    for ln in lines:
        p = ln.split(",")
        rows.append({"T": float(p[0]), "N": int(p[1]), "beats": float(p[2]),
                     "res": float(p[3]), "gap": p[4], "err": p[5],
                     "res_flag": p[6] == "1"})
    ref = load("floor_law.json")
    fig = new_fig()
    ax = fig.gca()
    T = np.array([r["T"] for r in rows])
    N = np.array([r["N"] for r in rows])
    ok = np.array([r["res_flag"] for r in rows])
    errs = np.array([float(r["err"]) if r["err"] else np.nan for r in rows])
    ax.plot(T[ok], errs[ok], "o", ms=6, color=tok["gold"], label="error")
    ax.plot(T[~ok], errs[~ok], "x", ms=9, color=tok["bad"],
            label=L["floor_unres"])
    ax.plot(T, 2.0 / N, "-", lw=1.6, color=tok["ink"], label=L["floor_env"])
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(L["floor_x"])
    ax.set_ylabel(L["floor_y"])
    ax.set_title(L["floor_title"])
    ax.legend(loc="upper right", framealpha=0.0)
    finish(fig, path)


# ----------------------------------------------------------------------------
# 7. the drift law
# ----------------------------------------------------------------------------
def fig_drift(lang, tok, L, path):
    with open(os.path.join(DATA, "drift_ladder.csv"), encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")[1:]
    N = np.array([int(ln.split(",")[0]) for ln in lines])
    h = np.array([float(ln.split(",")[1]) for ln in lines])
    dN = np.array([float(ln.split(",")[2]) for ln in lines])
    d = load("drift_law.json")
    dcont = d["fit"]["Delta_cont_fit"]
    C = d["fit"]["C_measured"]
    fig = new_fig()
    ax = fig.gca()
    hh = np.linspace(0, h.max() * 1.05, 200)
    ax.plot(h, dN, "o", ms=6, color=tok["gold"], zorder=5)
    ax.plot(hh, dcont - C * hh ** 2, "-", lw=1.8, color=tok["ink"],
            label=L["drift_fit"])
    ax.axhline(dcont, color=tok["muted"], lw=1.2, ls=":")
    ax.text(h[0], dcont + 2e-5,
            f"$\\Delta_{{cont}}$(fit) $= {dcont:.6f}$ — "
            + ("НЕ утверждается" if lang == "ru" else "NOT claimed"),
            color=tok["muted"], fontsize=9)
    ax.set_xlabel(L["drift_x"])
    ax.set_ylabel(L["drift_y"])
    ax.set_ylim(dN.min() - 2e-4, dcont + 6e-4)
    ax.set_title(L["drift_title"])
    ax.legend(loc="lower right", framealpha=0.0)
    finish(fig, path)


# ----------------------------------------------------------------------------
# 8. the gap phase map (C9)
# ----------------------------------------------------------------------------
def fig_phase(lang, tok, L, path):
    with open(os.path.join(DATA, "phase_map.csv"), encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")[1:]
    rows = [ln.split(",") for ln in lines]
    with open(os.path.join(DATA, "phase_valley.csv"),
              encoding="utf-8") as fh:
        vlines = fh.read().strip().split("\n")[1:]
    valley = [ln.split(",") for ln in vlines]
    ce = load("phase_counterexample.json")
    floor = 2.0 / 64.0

    fig = new_fig()
    ax = fig.gca()
    show = (0.2, 0.4, 0.6, 0.8, 1.0)
    shades = [tok["gold_soft"], tok["gold"], tok["ink"], tok["muted"],
              tok["bad"]]
    for i, qp in enumerate(show):
        rr = sorted(((float(r[1]), float(r[2])) for r in rows
                     if abs(float(r[0]) - qp) < 1e-9))
        b = np.array([x[0] for x in rr])
        g = np.array([x[1] for x in rr])
        ax.plot(b, g, "-", lw=1.6, color=shades[i % 5],
                label=f"$q_{{pk}} = {qp:g}$")
    # the valley minima (gold dots)
    vb = [float(r[1]) for r in valley if float(r[0]) in show]
    vg = [float(r[2]) for r in valley if float(r[0]) in show]
    ax.plot(vb, vg, "o", ms=8, mfc="none", mew=2.0, color=tok["gold"],
            zorder=6, label=L["phase_valley"])
    # the detector floor and the naive-window forecast
    ax.axhline(floor, color=tok["bad"], lw=1.2, ls="--")
    ax.text(6.6, floor * 1.35, L["phase_floor"], color=tok["bad"],
            fontsize=9)
    ax.axvline(ce["beta_c_quadratic_forecast"], color=tok["muted"], lw=1.2,
               ls=":")
    ax.text(ce["beta_c_quadratic_forecast"] - 0.12, 2.35,
            L["phase_betac"], rotation=90, color=tok["muted"], fontsize=9,
            ha="right", va="top")
    ax.set_yscale("log")
    ax.set_ylim(floor * 0.5, 3.0)
    ax.set_xlim(-0.2, 10.2)
    ax.set_xlabel(L["phase_x"])
    ax.set_ylabel(L["phase_y"])
    ax.set_title(L["phase_title"])
    ax.legend(loc="lower left", framealpha=0.0, fontsize=8.5, ncol=2)
    finish(fig, path)


# ----------------------------------------------------------------------------
# 9. the causal map of the drive (C10)
# ----------------------------------------------------------------------------
def fig_ablation(lang, tok, L, path):
    with open(os.path.join(DATA, "ablation.csv"), encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")[1:]
    rows = [(ln.split(",")[0], abs(float(ln.split(",")[1])))
            for ln in lines]
    order = ["ABC", "AB", "AC", "A", "BC", "B", "C", "none"]
    rows.sort(key=lambda r: order.index(r[0]))
    labels = {"ABC": "A+B+C", "AB": "A+B", "AC": "A+C", "BC": "B+C",
              "A": "A", "B": "B", "C": "C", "none": "-"}
    shares = load("ablation_additivity.json")["shares"]
    fig = new_fig(8.0, 5.6)
    ax = fig.gca()
    y = np.arange(len(rows))
    vals = [max(r[1], 1e-7) for r in rows]
    colors = [tok["gold"] if r[0] == "ABC" else
              (tok["ink"] if r[0] in ("A", "AB", "AC") else
               (tok["muted"] if r[0] in ("B", "BC", "C") else tok["bad"]))
              for r in rows]
    ax.barh(y, vals, height=0.62, color=colors, edgecolor="none")
    ax.set_yticks(y)
    ax.set_yticklabels([labels[r[0]] for r in rows])
    ax.set_xscale("log")
    ax.set_xlim(1e-7, 1.0)
    ax.invert_yaxis()
    for i, r in enumerate(rows):
        if r[0] == "none":
            ax.text(1.6e-7, i, L["abl_none"], va="center", fontsize=9,
                    color=tok["bad"])
        else:
            key = {"ABC": "C", "AB": "B", "AC": "C", "BC": "C", "A": "A",
                   "B": "B", "C": "C"}[r[0]]
            share = shares.get(r[0], shares.get(key))
            if r[0] in shares:
                ax.text(r[1] * 1.5, i, f"{share * 100:.2f}%",
                        va="center", fontsize=9, color=tok["ink"])
    ax.set_xlabel(L["abl_x"])
    ax.set_ylabel(L["abl_y"])
    ax.set_title(L["abl_title"])
    finish(fig, path)


# ----------------------------------------------------------------------------
# 10. the invariant wall and the static barrier (C11)
# ----------------------------------------------------------------------------
def fig_vortex(lang, tok, L, path):
    v = load("vortex_anchor.json")
    traj = np.array(v["T12_manifold"]["traj_decimated"])   # (m, 6)
    # the exact T13 bound r(V0) = R_b + w sqrt((E0_max + 3/sqrt(eps^2))/(2V0))
    # constants from the committed engine (qhb.trio / engine.solver)
    E0_max = -0.052595
    pair_floor = 3.0 / math.sqrt(1e-2)
    Rb, w = 8.0, 1.0
    V = np.linspace(0.4, 12.8, 300)
    bound = Rb + w * np.sqrt((E0_max + pair_floor) / (2.0 * V))
    cells = [(0.4, 2.0), (0.8, 2.0), (1.6, 2.0)]           # placeholders
    import json as _json
    with open(os.path.join(ROOT, "campaigns", "reference",
                           "c11_verdict.json"), encoding="utf-8") as fh:
        cells = [(c["V0"], c["r_max_final"])
                 for c in _json.load(fh)["blocks"]["B4_T13_barrier"]
                 ["cells"]]

    fig = new_fig(10.5, 5.0)
    ax1, ax2 = fig.subplots(1, 2)
    # left: the Aref manifold evolution (bound without any wall)
    ax1.plot(traj[:, 0], traj[:, 1], "-", lw=1.1, color=tok["gold"])
    ax1.plot(traj[:, 2], traj[:, 3], "-", lw=1.1, color=tok["ink"])
    ax1.plot(traj[:, 4], traj[:, 5], "-", lw=1.1, color=tok["muted"])
    ax1.plot([traj[0, 0]], [traj[0, 1]], "o", ms=6, color=tok["gold"])
    ax1.plot([traj[0, 2]], [traj[0, 3]], "o", ms=6, color=tok["ink"])
    ax1.plot([traj[0, 4]], [traj[0, 5]], "o", ms=6, color=tok["muted"])
    ax1.set_xlabel(L["vor_left_x"])
    ax1.set_ylabel(L["vor_left_y"])
    ax1.set_title(L["vor_aref"], fontsize=11.5)
    ax1.set_aspect("equal")
    # right: the static barrier
    ax2.plot(V, bound, "-", lw=1.8, color=tok["ink"], label=L["vor_bound"])
    ax2.axhline(12.0, color=tok["bad"], lw=1.2, ls="--", label=L["vor_resc"])
    ax2.plot([c[0] for c in cells], [c[1] for c in cells], "o", ms=7,
             color=tok["gold"], zorder=6, label=L["vor_meas"])
    ax2.axvline(0.9359375, color=tok["gold_soft"], lw=1.6, ls=":",
                label=L["vor_vstar"])
    ax2.set_yscale("log")
    ax2.set_ylim(1.0, 30.0)
    ax2.set_xlabel(L["vor_right_x"])
    ax2.set_ylabel(L["vor_right_y"])
    ax2.set_title("T13", fontsize=11.5)
    ax2.legend(loc="upper right", framealpha=0.0, fontsize=8.5)
    fig.suptitle(L["vor_title"], fontsize=13, color=tok["ink"])
    finish(fig, path)


BUILDERS = {
    "fig_map": fig_map,
    "fig_gap": fig_gap,
    "fig_trap": fig_trap,
    "fig_wu": fig_wu,
    "fig_contacts": fig_contacts,
    "fig_floor": fig_floor,
    "fig_drift": fig_drift,
    "fig_phase": fig_phase,
    "fig_ablation": fig_ablation,
    "fig_vortex": fig_vortex,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="comma-separated figure ids")
    args = ap.parse_args()
    only = args.only.split(",") if args.only else None
    n = 0
    for lang in ("en", "ru"):
        for theme in ("light", "dark"):
            tok = style(theme)
            L = LANG[lang]
            out_dir = os.path.join(FIGS, lang, theme)
            os.makedirs(out_dir, exist_ok=True)
            for name, fn in BUILDERS.items():
                if only and name not in only:
                    continue
                fn(lang, tok, L, os.path.join(out_dir, f"{name}.png"))
                n += 1
                print(f"built {lang}/{theme}/{name}.png")
    print(f"{n} figures @300dpi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
