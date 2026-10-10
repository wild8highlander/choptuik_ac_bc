# -*- coding: utf-8 -*-
"""
hires_figures.py — the 600-dpi edition: 17 architectures x RU/EN x
light/dark.  The 7 committed 300-dpi architectures plus 10 extended
views.  Reads data/qhb and the committed verdicts only.
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

from figstyle import TOKENS, LANG, style, new_fig, finish
import make_figures as _mf
from make_figures import BUILDERS, load, DATA
from figstyle import finish as _finish_orig

FIGS = os.path.join(ROOT, "figures_hires")


def _finish600(fig, path, dpi=600):
    _finish_orig(fig, path, dpi=600)


_mf.finish = _finish600          # the hires edition renders at 600 dpi

BASE_NAMES = {
    "fig_map": "hq_01_map",
    "fig_gap": "hq_02_gap_law",
    "fig_trap": "hq_03_trap",
    "fig_wu": "hq_04_wu_door",
    "fig_contacts": "hq_05_contacts",
    "fig_floor": "hq_06_floor",
    "fig_drift": "hq_07_drift",
    "fig_phase": "hq_21_phase_valley",
    "fig_ablation": "hq_22_causal_map",
    "fig_vortex": "hq_23_vortex_barrier",
}


# --- extended architectures --------------------------------------------------
def hq_per_sector(lang, tok, L, path):
    d = load("gap_per_sector.json")
    scan = load("gap_scan_window.json")
    d0 = scan["gap"][0]
    fig = new_fig()
    ax = fig.gca()
    betas = np.linspace(0.01, 0.2, 60)
    labels = [("B2_A_pi2", L["sectors_A"], tok["ink"]),
              ("B2_B_pi3", L["sectors_B"], tok["gold"]),
              ("B2_C_pi7", L["sectors_C"], tok["muted"])]
    for key, lab, col in labels:
        B2 = d[key]
        ax.semilogy(betas, [abs(B2) * b ** 2 for b in betas], lw=2.0,
                    color=col, label=lab)
    ax.set_xlabel(L["gap_x"])
    ax.set_ylabel(L["sectors_y"] + " (abs)")
    ax.set_title(L["sectors_title"])
    ax.legend(framealpha=0.0)
    finish(fig, path)


def hq_trap_heatmap(lang, tok, L, path):
    with open(os.path.join(DATA, "trap_grid.csv"), encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")[1:]
    rows = [ln.split(",") for ln in lines]
    V = sorted({float(r[0]) for r in rows})
    O = sorted({float(r[1]) for r in rows})
    M = np.zeros((len(O), len(V)))
    for r in rows:
        M[O.index(float(r[1])), V.index(float(r[0]))] = float(r[2])
    fig = new_fig()
    ax = fig.gca()
    im = ax.imshow(M, aspect="auto", cmap="inferno", vmin=0, vmax=0.25,
                   extent=[math.log10(min(V) + 1e-6), math.log10(max(V)),
                           -0.5, len(O) - 0.5], origin="lower")
    ax.set_yticks(range(len(O)))
    ax.set_yticklabels([f"{o:g}" for o in O])
    ax.set_xlabel(L["trap_x"] + " (log10)")
    ax.set_ylabel(L["trap_y"].split()[0] + " $\\Omega$")
    ax.set_title(L["trap_title"])
    fig.colorbar(im, ax=ax)
    finish(fig, path)


def hq_lyapunov(lang, tok, L, path):
    d = load("trap_lyapunov.json")
    fig = new_fig()
    ax = fig.gca()
    names = ["free", "trap_V08_Om2"]
    cols = [tok["muted"], tok["gold"]]
    labels = ["V$_0$ = 0", "V$_0$ = 8, $\\Omega$ = 2"]
    for name, col, lab in zip(names, cols, labels):
        ax.bar([lab], [d[name]["median"]], color=col, width=0.5)
    ax.set_ylim(0, 0.4)
    ax.set_ylabel("$\\lambda_{max}$ (Benettin)")
    ax.set_title(L["trap_title"] + " — bound chaos")
    ax.text(0.5, 0.06, "the wall does not change the chaos — it changes "
            "the EXIT", transform=ax.transAxes, ha="center", fontsize=9,
            color=tok["muted"])
    finish(fig, path)


def hq_wu_slices(lang, tok, L, path):
    with open(os.path.join(DATA, "wu_residual_grid.csv"), encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")[1:]
    fig = new_fig()
    ax = fig.gca()
    alphas = sorted({float(ln.split(",")[0]) for ln in lines})
    shades = [tok["muted"], tok["muted"], tok["ink"], tok["ink"], tok["gold"],
              tok["gold_soft"]]
    for a, col in zip(alphas, shades):
        pts = sorted(((float(ln.split(",")[1]), float(ln.split(",")[2]))
                      for ln in lines if float(ln.split(",")[0]) == a))
        x = [p[0] for p in pts]
        r = [p[1] for p in pts]
        ax.plot(x, r, "o-" if a == 0.9 else "o--", ms=5,
                lw=2.2 if a == 0.9 else 1.2, color=col,
                label=f"$\\alpha = {a:g}$")
    ax.set_xscale("log")
    ax.set_xlabel(L["wu_x"])
    ax.set_ylabel(L["wu_y"] + " (grid)")
    ax.set_title(L["wu_title"])
    ax.legend(framealpha=0.0, fontsize=8)
    finish(fig, path)


def hq_contacts_zoom(lang, tok, L, path):
    from qhb.bridge import T_H, equal_qcd_mass, T_QCD_K
    from qhb.constants import LAMBDA_QCD_MeV, MeV_J, k_B, h
    fig = new_fig()
    ax = fig.gca()
    M = np.logspace(9.5, 12.5, 300)
    ax.plot(M, [T_H(m) for m in M], lw=2.0, color=tok["ink"])
    Mc = equal_qcd_mass()
    ax.axhline(T_QCD_K, color=tok["gold"], ls=":", lw=1.2)
    ax.axvline(Mc, color=tok["gold"], ls=":", lw=1.2)
    ax.plot([Mc], [T_QCD_K], "o", ms=10, color=tok["gold"], zorder=5)
    lam_Hz = LAMBDA_QCD_MeV * MeV_J / h
    ax.axhline(lam_Hz * 6.62607015e-34 / 1.380649e-23, color=tok["muted"],
               ls="--", lw=1.0)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(L["contacts_x"])
    ax.set_ylabel(L["contacts_y"])
    ax.set_title(L["contacts_title"] + " — QCD zoom")
    ax.text(0.05, 0.08,
            f"$M_{{QCD}}$ = {Mc:.4e} kg = 0.68 x 10$^{{11}}$ kg\n"
            "literature PBH@QCD ~ 1e11 kg (comparison)",
            transform=ax.transAxes, fontsize=9, color=tok["muted"])
    finish(fig, path)


def hq_density_ladder(lang, tok, L, path):
    with open(os.path.join(DATA, "scale_ladder_density.csv"),
              encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")[1:]
    fig = new_fig()
    ax = fig.gca()
    members = ("near_floor", "mid", "saturated")
    cols = (tok["muted"], tok["gold"], tok["ink"])
    scales = []
    for ln in lines:
        p = ln.split(",")
        if p[0] not in scales:
            scales.append(p[0])
    import numpy as np
    x = np.arange(len(scales))
    w = 0.26
    for j, (m, col) in enumerate(zip(members, cols)):
        vals = [float(ln.split(",")[4]) for ln in lines
                if ln.split(",")[1] == m]
        ax.bar(x + (j - 1) * w, vals, width=w, color=col, label=m)
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels([s.replace(" input", "") for s in scales],
                       fontsize=8)
    ax.set_ylabel("$\\bar\\rho / \\rho_P$ (mean horizon density)")
    ax.set_title("The binding furnace (H1): density of the born ensemble")
    ax.legend(framealpha=0.0, fontsize=8)
    finish(fig, path)


def hq_drift_residuals(lang, tok, L, path):
    with open(os.path.join(DATA, "drift_ladder.csv"), encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")[1:]
    h = np.array([float(ln.split(",")[1]) for ln in lines])
    dN = np.array([float(ln.split(",")[2]) for ln in lines])
    d = load("drift_law.json")
    dcont = d["fit"]["Delta_cont_fit"]
    C = d["fit"]["C_measured"]
    fig = new_fig()
    ax = fig.gca()
    ax.loglog(h, np.abs(dcont - dN), "o", ms=6, color=tok["gold"],
              label="observed drift")
    ax.loglog(h, [abs(C) * hh ** 2 for hh in h], "-", lw=1.6, color=tok["ink"],
              label=f"$|C| h^2$, C = {C:.4e}")
    ex = d["exact_channel"]["C_exact_s_kappa_over_8"]
    ax.loglog(h, [abs(ex) * hh ** 2 for hh in h], "--", lw=1.4,
              color=tok["muted"],
              label=f"exact channel $|s\\kappa/8| h^2$, share {-1*ex/C:+.3f}")
    ax.set_xlabel(L["drift_x"])
    ax.set_ylabel("$|\\Delta_{cont} - \\Delta_N|$")
    ax.set_title(L["drift_title"] + " — channels")
    ax.legend(framealpha=0.0, fontsize=8)
    finish(fig, path)


def hq_lemma_a(lang, tok, L, path):
    from qhb.gap import parabolic_profile, KAPPA, Q_PK
    fig = new_fig()
    ax = fig.gca()
    x, q, hstep, Lb = parabolic_profile(16, KAPPA, Q_PK)
    xc = np.linspace(-Lb / 2, Lb / 2, 400)
    qc = 0.5 * KAPPA * xc ** 2 - Q_PK
    ax.plot(xc, qc, "-", lw=1.4, color=tok["muted"], alpha=0.8)
    ax.plot(x, q, "o", ms=7, color=tok["gold"])
    depth = -q.min()
    ax.axhline(-Q_PK, color=tok["muted"], ls=":", lw=1)
    ax.axhline(-depth, color=tok["gold"], ls=":", lw=1)
    ax.annotate("", xy=(0, -Q_PK), xytext=(0, -depth),
                arrowprops=dict(arrowstyle="<->", color=tok["bad"], lw=1.4))
    ax.text(0.1, -(Q_PK + depth) / 2,
            f"$\\kappa h^2/8$ = {Q_PK - depth:.3e}", fontsize=9,
            color=tok["bad"])
    ax.set_xlabel("x")
    ax.set_ylabel("q(x)")
    ax.set_title("Lemma A: the sampled parabola loses exactly "
                 "$\\kappa h^2/8$")
    finish(fig, path)


def hq_kepler(lang, tok, L, path):
    from engine.solver import kepler_period_check, DT
    fig = new_fig()
    ax = fig.gca()
    dts = [2e-2, 1e-2, 5e-3, 2e-3, 1e-3]
    errs = []
    for dt in dts:
        _, _, e = kepler_period_check(dt=dt)
        errs.append(max(e, 1e-16))
    ax.loglog(dts, errs, "o-", ms=6, color=tok["gold"])
    ref = errs[1] * (np.array(dts) / dts[1]) ** 4
    ax.loglog(dts, ref, "--", lw=1.2, color=tok["muted"],
              label="4th order (RK4)")
    ax.set_xlabel("dt")
    ax.set_ylabel("|T_meas - T_kepler| / T")
    ax.set_title("Engine validation: the Kepler anchor")
    ax.legend(framealpha=0.0)
    finish(fig, path)


def hq_master_heat(lang, tok, L, path):
    with open(os.path.join(DATA, "bridge_master.csv"), encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")
    header = lines[0].split(",")
    fig = new_fig(9.6, 6.4)
    ax = fig.gca()
    rows_txt = []
    for ln in lines[1:]:
        p = ln.split(",")
        rows_txt.append(f'{p[0][:12]:12s} {p[2][:10]:10s} '
                        f'M={float(p[4]):.3e}  T={float(p[7]):.3e}  '
                        f'rho/rhoP={float(p[16]):.3e}')
    ax.axis("off")
    ax.text(0.01, 0.98, "bridge_master.csv — 15 x 23 (compact view)",
            transform=ax.transAxes, va="top", fontsize=12,
            color=tok["ink"], fontweight="bold")
    for i, r in enumerate(rows_txt):
        ax.text(0.01, 0.93 - i * 0.062, r, transform=ax.transAxes,
                fontsize=8.2, family="monospace",
                color=tok["ink"] if i % 2 == 0 else tok["muted"])
    finish(fig, path)


# --- v1.1.0: the C6-C8 architectures -----------------------------------------
def hq_mapping_branches(lang, tok, L, path):
    with open(os.path.join(DATA, "mapping_branches.csv"),
              encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")[1:]
    rows = [ln.split(",") for ln in lines]
    names = [r[0] for r in rows]
    fc = [float(r[2]) for r in rows]
    fg = [float(r[4]) for r in rows]
    eg = [float(r[5]) for r in rows]
    tags = [L["map_L"], L["map_Q"], L["map_E"]]
    fig = new_fig(8.6, 5.2)
    ax = fig.gca()
    x = np.arange(len(names))
    w = 0.36
    ax.bar(x - w / 2, fc, width=w, color=tok["muted"], label=L["map_fcontact"])
    ax.bar(x + w / 2, fg, width=w, color=tok["gold"], label=L["map_fgap"])
    ax.set_yscale("log")
    ax.set_ylim(1e21, 1e33)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{n}\n{t}" for n, t in zip(names, tags)],
                       fontsize=8.5)
    ax.set_ylabel(L["map_y"])
    ax.set_title(L["map_title"])
    for xi, e in zip(x, eg):
        ax.text(xi + w / 2, 3e25,
                f"$E_{{gap}}$ = {e:.1f} MeV" if e < 1e4
                else f"$E_{{gap}}$ = {e:.2e} MeV",
                ha="center", fontsize=8, color=tok["gold"], rotation=90)
    ax.legend(framealpha=0.0, fontsize=9)
    finish(fig, path)


def hq_anharmonic(lang, tok, L, path):
    with open(os.path.join(DATA, "anharmonic_free.csv"),
              encoding="utf-8") as fh:
        flines = fh.read().strip().split("\n")[1:]
    sig = [float(ln.split(",")[0]) for ln in flines]
    pes = [float(ln.split(",")[1]) for ln in flines]
    import json as _json
    with open(os.path.join(DATA, "anharmonic_boundary.json"),
              encoding="utf-8") as fh:
        B = _json.load(fh)
    fig = new_fig(9.8, 4.6)
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.semilogx([s + 1e-4 for s in sig], pes, "o-", ms=6, lw=2.0,
                 color=tok["gold"])
    ax1.axhline(0.05, color=tok["bad"], ls=":", lw=1.2)
    ax1.text(0.0021, 0.062, "$P_{esc} = 0.05$", fontsize=8, color=tok["bad"])
    ax1.set_xlabel(L["anh_x"])
    ax1.set_ylabel(L["anh_y"])
    ax1.set_title(L["anh_title"], fontsize=11)
    ax2 = fig.add_subplot(1, 2, 2)
    grid = B["L2"]["V0_star_per_Omega_per_sigma"]
    sigmas = [0.0, 0.01, 0.02]
    for Om, col in (("0.0", tok["ink"]), ("2.0", tok["gold"])):
        v = [grid[Om][str(s)] for s in sigmas]
        ax2.plot(sigmas, v, "o-", ms=6, lw=2.0, color=col,
                 label=f"$\\Omega = {float(Om):g}$")
    ax2.set_xlabel(L["anh_x"])
    ax2.set_ylabel(L["anh_b_y"])
    ax2.set_title(L["anh_b_title"], fontsize=11)
    ax2.legend(framealpha=0.0, fontsize=9)
    finish(fig, path)


def hq_pairwise_door(lang, tok, L, path):
    with open(os.path.join(DATA, "pairwise_residual.csv"),
              encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")[1:]
    fig = new_fig(8.0, 5.2)
    ax = fig.gca()
    for al, col in ((0.9, tok["gold"]), (0.5, tok["ink"])):
        pts = sorted((float(ln.split(",")[1]), float(ln.split(",")[2]),
                      float(ln.split(",")[3])) for ln in lines
                     if abs(float(ln.split(",")[0]) - al) < 1e-12)
        lam = [p[0] for p in pts]
        rp = [p[1] for p in pts]
        rl = [p[2] for p in pts]
        ax.plot(lam, rp, "o-", ms=6, lw=2.2, color=col,
                label=f"{L['pair_pair']}, $\\alpha = {al:g}$")
        ax.plot(lam, rl, "s--", ms=4, lw=1.2, color=tok["muted"],
                label=f"{L['pair_lin']}, $\\alpha = {al:g}$")
        ax.axhline(al, color=col, ls=":", lw=0.9, alpha=0.5)
    ax.axhline(1.0, color=tok["bad"], ls=":", lw=1.0)
    ax.text(0.011, 1.008, L["pair_full"], fontsize=8, color=tok["bad"])
    ax.set_xscale("log")
    ax.set_ylim(-0.03, 1.08)
    ax.set_xlabel(L["pair_x"])
    ax.set_ylabel(L["pair_y"])
    ax.set_title(L["pair_title"], fontsize=11)
    ax.legend(framealpha=0.0, fontsize=8)
    finish(fig, path)


def hq_phase_heatmap(lang, tok, L, path):
    """The (beta, q_pk) phase map as a heatmap + the valley locus."""
    with open(os.path.join(DATA, "phase_map.csv"), encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")[1:]
    qpk = sorted({float(ln.split(",")[0]) for ln in lines})
    beta = sorted({float(ln.split(",")[1]) for ln in lines})
    Z = np.full((len(qpk), len(beta)), np.nan)
    for ln in lines:
        q, b, g = ln.split(",")[:3]
        Z[qpk.index(float(q)), beta.index(float(b))] = float(g)
    with open(os.path.join(DATA, "phase_valley.csv"),
              encoding="utf-8") as fh:
        vlines = fh.read().strip().split("\n")[1:]
    vq = [float(ln.split(",")[0]) for ln in vlines]
    vb = [float(ln.split(",")[1]) for ln in vlines]
    fig = new_fig(9.0, 5.4)
    ax = fig.gca()
    pc = ax.pcolormesh(beta, qpk, Z, cmap="cividis", shading="auto")
    ax.plot(vb, vq, "o", ms=6, mfc="none", mew=1.8, color="#FAF7F0",
            label=L["phase_valley"])
    ax.axvline(2.9910, color="#FAF7F0", ls=":", lw=1.2)
    ax.set_colorbar = None
    cb = fig.colorbar(pc, ax=ax, pad=0.015)
    cb.set_label(L["phase_y"])
    ax.set_xlabel(L["phase_x"])
    ax.set_ylabel("$q_{pk}$")
    ax.set_title(L["phase_title"], fontsize=11)
    ax.legend(framealpha=0.0, fontsize=8.5)
    finish(fig, path)


def hq_ablation_zoom(lang, tok, L, path):
    """The ablation B2 ladder with the additive predictions overlaid."""
    import json as _json
    with open(os.path.join(DATA, "ablation.csv"), encoding="utf-8") as fh:
        lines = fh.read().strip().split("\n")[1:]
    meas = {ln.split(",")[0]: abs(float(ln.split(",")[1])) for ln in lines}
    with open(os.path.join(DATA, "ablation_additivity.json"),
              encoding="utf-8") as fh:
        add = _json.load(fh)
    single = {"A": meas["A"], "B": meas["B"], "C": meas["C"]}
    order = ["A", "B", "C", "AB", "AC", "BC", "ABC"]
    fig = new_fig(9.0, 5.2)
    ax = fig.gca()
    y = np.arange(len(order))
    vals = [meas[c] for c in order]
    ax.barh(y, vals, height=0.6, color=tok["gold"], edgecolor="none",
            label="measured $|B_2|$")
    for i, c in enumerate(order):
        if len(c) > 1:
            pred = sum(single[s] for s in c)
            ax.plot([pred], [i], "s", ms=9, mfc="none", mew=1.8,
                    color=tok["ink"])
    ax.set_yticks(y)
    ax.set_yticklabels(["+".join(c) for c in order])
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(1e-5, 0.2)
    ax.set_xlabel(L["abl_x"])
    ax.set_ylabel(L["abl_y"])
    ax.set_title(L["abl_title"] + "  (max cross 1.3e-4)", fontsize=11)
    ax.legend(framealpha=0.0, fontsize=9)
    finish(fig, path)


def hq_vortex_barrier(lang, tok, L, path):
    _mf.fig_vortex(lang, tok, L, path)


EXTENDED = {
    "hq_08_per_sector": hq_per_sector,
    "hq_09_trap_heatmap": hq_trap_heatmap,
    "hq_10_lyapunov": hq_lyapunov,
    "hq_11_wu_slices": hq_wu_slices,
    "hq_12_contacts_zoom": hq_contacts_zoom,
    "hq_13_density_ladder": hq_density_ladder,
    "hq_14_drift_channels": hq_drift_residuals,
    "hq_15_lemma_a": hq_lemma_a,
    "hq_16_kepler": hq_kepler,
    "hq_17_master_compact": hq_master_heat,
    "hq_18_mapping_branches": hq_mapping_branches,
    "hq_19_anharmonic": hq_anharmonic,
    "hq_20_pairwise_door": hq_pairwise_door,
    "hq_24_phase_heatmap": hq_phase_heatmap,
    "hq_25_ablation_zoom": hq_ablation_zoom,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None
    n = 0
    for lang in ("en", "ru"):
        for theme in ("light", "dark"):
            tok = style(theme)
            L = LANG[lang]
            out_dir = os.path.join(FIGS, lang, theme)
            os.makedirs(out_dir, exist_ok=True)
            for name, fn in BUILDERS.items():
                hq = BASE_NAMES[name]
                if only and hq not in only:
                    continue
                fn(lang, tok, L, os.path.join(out_dir, f"{hq}.png"))
                n += 1
            for name, fn in EXTENDED.items():
                if only and name not in only:
                    continue
                fn(lang, tok, L, os.path.join(out_dir, f"{name}.png"))
                n += 1
    print(f"{n} hires figures @600dpi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
