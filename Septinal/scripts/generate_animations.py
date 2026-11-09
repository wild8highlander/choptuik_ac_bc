#!/usr/bin/env python3
"""Septinal · generate_animations.py — the five GIF animations of the package.

All animations are deterministic (nothing random at render time; the
package seed 1993 is stamped in the manifest) and are regenerated via:

    python scripts/generate_animations.py [--lang en|ru] [--fps N]

Outputs (dark "cosmic" rendition, as the GitHub README theme):

    animations/en/anim_echoing.gif     DSS echo: profiles repeat after Delta
    animations/en/anim_scaling.gif     mass scaling: points + slope + wiggle
    animations/en/anim_collapse.gif    subcritical / critical / supercritical
    animations/en/anim_dial.gif        the septinial dial: gap, chirality, V4
    animations/en/anim_spectrum.gif    eigenvalues landing in certificate slots

and the Russian mirrors under ``animations/ru/``.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sepstyle import SEED, THEMES, labels

for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    try:
        fm.fontManager.addfont(f)
    except Exception:
        pass
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parents[1]
ANIM = ROOT / "animations"

LAMBDA0 = 2.6745
GAMMA = 1.0 / LAMBDA0
DELTA = 3.445452402
WIGGLE = LAMBDA0 * DELTA / 2.0
LN2 = math.log(2.0)
PI = math.pi


class Frame:
    """One animation = a list of draw functions over a themed fig/ax."""

    def __init__(self, theme: dict, lang: str, title: str):
        self.T, self.X = theme, labels(lang)
        self.title = title
        self.frames = []

    def draw(self, path: Path, fps: int = 14, dpi: int = 96) -> None:
        imgs = []
        for state in self.frames:
            fig, ax = plt.subplots(figsize=(7.2, 4.35), constrained_layout=True)
            fig.patch.set_facecolor(self.T["bg"])
            ax.set_facecolor(self.T["bg"])
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            for s in ("left", "bottom"):
                ax.spines[s].set_color(self.T["muted"])
            ax.tick_params(colors=self.T["muted"], labelsize=8)
            ax.grid(True, color=self.T["grid"], lw=0.6)
            ax.xaxis.label.set_color(self.T["text"])
            ax.yaxis.label.set_color(self.T["text"])
            ax.set_title(self.title, fontsize=12, weight="bold", color=self.T["text"])
            state(ax)
            fig.canvas.draw()
            buf = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
            imgs.append(Image.fromarray(buf.copy()))
            plt.close(fig)
        path.parent.mkdir(parents=True, exist_ok=True)
        imgs[0].save(path, save_all=True, append_images=imgs[1:],
                     duration=int(1000 / fps), loop=0, optimize=True)
        print(f"[anim] {path.relative_to(ROOT)}  ({len(imgs)} frames, "
              f"{path.stat().st_size // 1024} KB)")


# ----------------------------------------------------------------------
def anim_echoing(T, X, lang, n_frames=40):
    a = Frame(T, lang, X["echo_title"])
    rho = np.linspace(0.02, 1.0, 200)
    for f in range(n_frames):
        tau = 2 * DELTA * f / (n_frames - 1)
        def state(ax, tau=tau):
            s = (tau % DELTA) - DELTA / 2
            amp = 1 + 0.25 * math.sin(2 * PI * tau / DELTA)
            psi = amp * np.exp(-(rho * math.exp(s)) ** 2 / 2.0)
            ghost = amp * np.exp(-(rho * math.exp((tau - DELTA) % DELTA - DELTA / 2)) ** 2 / 2.0)
            ax.plot(rho, ghost, color=T["muted"], lw=1.0, ls="--", alpha=0.7)
            ax.plot(rho, psi, color=T["gold"], lw=2.4)
            ax.set_xlim(0, 1); ax.set_ylim(0, 1.4)
            ax.set_xlabel(X["radius"]); ax.set_ylabel(X["psi"])
            ax.text(0.02, 0.95, f"tau = {tau:6.3f}    Delta = {DELTA}", fontsize=8,
                    color=T["muted"], transform=ax.transAxes)
            ax.text(0.02, 0.88, X["echo_one_period"] + ":  " +
                    f"{tau / DELTA:4.2f} x Delta", fontsize=8, color=T["gold"],
                    transform=ax.transAxes)
            ins = ax.inset_axes([0.66, 0.10, 0.31, 0.30])
            tt = np.linspace(0, 2 * DELTA, 200)
            ins.plot(tt, 1 + 0.25 * np.sin(2 * PI * tt / DELTA), color=T["violet"], lw=1.0)
            ins.axvline(tau % (2 * DELTA), color=T["gold"], lw=1.4)
            ins.set_facecolor(T["band"]); ins.tick_params(colors=T["muted"], labelsize=6)
            ins.set_xticks([0, DELTA, 2 * DELTA]); ins.set_xticklabels(["0", "D", "2D"], fontsize=6)
        a.frames.append(state)
    return a


def anim_scaling(T, X, lang, n_frames=36):
    a = Frame(T, lang, X["scaling_title"])
    rng = np.random.default_rng(SEED)
    x = np.linspace(-9.0, -1.6, 26)
    y = GAMMA * x + 0.055 * np.sin(2 * PI * (-x) / WIGGLE) + rng.uniform(-0.012, 0.012, 26)
    for f in range(n_frames):
        k = 1 + int(24 * f / (n_frames - 1))
        def state(ax, k=k):
            ax.plot(x, GAMMA * x, color=T["gold"], lw=1.6,
                    label=X["scaling_fit"])
            ax.fill_between(x, GAMMA * x - 0.12, GAMMA * x + 0.12,
                            color=T["band"], zorder=1)
            ax.scatter(x[:k], y[:k], s=26, color=T["cyan"], ec=T["bg"], lw=0.5, zorder=4)
            wig = 0.055 * np.sin(2 * PI * (-x) / WIGGLE + 2 * PI * f / (n_frames - 1))
            ax.plot(x, GAMMA * x + wig, color=T["violet"], lw=1.0, ls=":",
                    label=X["scaling_wiggle"])
            ax.set_xlabel(X["scaling_xlabel"]); ax.set_ylabel(X["scaling_ylabel"])
            ax.legend(facecolor=T["bg"], edgecolor=T["grid"], labelcolor=T["text"],
                      fontsize=8, loc="lower right")
            ax.text(0.02, 0.96, "|gamma - 0.374| = 263/2674500   (PROVED)",
                    fontsize=8, color=T["green"], transform=ax.transAxes, va="top")
            ax.text(0.02, 0.89, f"points: {k}/26", fontsize=8, color=T["cyan"],
                    transform=ax.transAxes, va="top")
        a.frames.append(state)
    return a


def anim_collapse(T, X, lang, n_frames=42):
    a = Frame(T, lang, "Choptuik critical collapse")
    r = np.linspace(0.0, 1.0, 200)
    for f in range(n_frames):
        u = f / (n_frames - 1)
        def state(ax, u=u):
            sub = np.exp(-((r - 0.05) ** 2) / (2 * (0.12 + 1.8 * u) ** 2)) * (1 - 0.85 * u)
            crit_amp = math.exp(min(3.2, 5.5 * u)) * (1 + 0.3 * math.sin(2 * PI * 3.0 * u))
            crit = np.exp(-(r * math.exp(min(2.2, 2.6 * u))) ** 2 / 2.0) * min(1.0, crit_amp)
            crit = crit / max(crit.max(), 1e-9) * min(1.25, crit_amp)
            mass = 0.0 if u < 0.55 else ((u - 0.55) / 0.45) ** GAMMA
            sup = np.exp(-((r - 0.05) ** 2) / (2 * 0.12 ** 2)) * (1 + 2.2 * u)
            for val, c, lab in ((sub, T["cyan"], X["collapse_sub"]),
                                (crit, T["gold"], X["collapse_crit"]),
                                (sup, T["red"], X["collapse_super"])):
                ax.plot(r, val, color=c, lw=1.8, label=lab)
            ax.set_xlim(0, 1); ax.set_ylim(0, 3.0)
            ax.set_xlabel(X["radius"]); ax.set_ylabel(X["psi"])
            ax.legend(facecolor=T["bg"], edgecolor=T["grid"], labelcolor=T["text"],
                      fontsize=7.5, loc="upper right")
            ax.text(0.02, 0.35, f"{X['collapse_mass']}: {mass:.4f}", fontsize=10,
                    color=T["gold"], transform=ax.transAxes)
            ax.text(0.02, 0.26, f"t = {u:5.2f}", fontsize=8, color=T["muted"],
                    transform=ax.transAxes)
        a.frames.append(state)
    return a


def anim_dial(T, X, lang, n_frames=48):
    res = json.loads((ROOT / "data" / "dial22_results.json").read_text())
    kle = json.loads((ROOT / "data" / "klein_psl27_results.json").read_text())
    gap = set(res["gap"])
    left = set(res["chiral_split"]["left"])
    triples = kle["antipodal"]["triples"]
    tcol = {}
    palette = [T["red"], T["gold"], T["cyan"], T["green"], T["violet"],
               T["fit"], T["red"], T["cyan"]]
    for i, tr in enumerate(triples):
        for s in tr:
            tcol[s] = palette[i]
    a = Frame(T, lang, X["dial_title"])
    for f in range(n_frames):
        ph = 2 * PI * f / (n_frames - 1)
        def state(ax, ph=ph):
            circ = np.linspace(0, 2 * PI, 241)
            off = 0.35 * math.sin(ph)
            ax.plot(np.cos(circ) * (1 + 0.0 * off), np.sin(circ), color=T["muted"],
                    lw=1.0, zorder=2)
            hl = int((ph / (2 * PI)) * 24) % 24
            for s in range(24):
                th = s * 2 * PI / 24
                x0, y0 = math.cos(th), math.sin(th)
                if s in gap:
                    ax.scatter([x0], [y0], s=190, marker="x", color=T["red"], lw=3.5, zorder=6)
                else:
                    glow = 260 if s == hl else 110
                    ax.scatter([x0], [y0], s=glow, color=tcol[s],
                               ec=(T["core"] if s == hl else T["bg"]),
                               lw=(1.6 if s == hl else 0.8), zorder=5)
            for tr in triples:
                pts = [(math.cos(s * 2 * PI / 24), math.sin(s * 2 * PI / 24)) for s in tr]
                pts.append(pts[0])
                ax.plot([p[0] for p in pts], [p[1] for p in pts],
                        color=T["muted"], lw=0.5, alpha=0.3, zorder=1)
            ax.set_xlim(-1.42, 1.42); ax.set_ylim(-1.42, 1.42)
            ax.set_aspect("equal")
            ax.text(0.0, -1.28, f"rotation: slot {hl:2d}   |   free slots 22   |   gap {{0, 12}}",
                    ha="center", fontsize=8.5, color=T["text"])
            ax.text(0.0, -1.36, "k = 22 = b2(K3)   -   1 + 22 + 1 = 24   -   48 -> 4 -> 2",
                    ha="center", fontsize=8, color=T["green"])
            arc_x = [math.cos(s * 2 * PI / 24) * 1.22 for s in sorted(left)] + [None]
            ax.text(0.0, 1.24, X["dial_left"] + "  +  " + X["dial_right"], ha="center",
                    fontsize=8.5, color=T["violet"])
        a.frames.append(state)
    return a


def anim_spectrum(T, X, lang, n_frames=36):
    a = Frame(T, lang, X["spec_title"])
    pts = [(LAMBDA0, 0.0, T["gold"], 90)]
    for k in range(7):
        re = -(4.3 + 1.8 * k)
        im = (2 * k + 1) * PI / LN2
        pts.append((re, im, T["cyan"], 34))
        pts.append((re, -im, T["cyan"], 34))
    order = [0] + [i for i in range(1, 15)]
    for f in range(n_frames):
        k = 1 + int(14 * f / (n_frames - 1))
        def state(ax, k=k):
            ax.axvline(0, color=T["muted"], lw=0.8, ls="--")
            for i, (re, im, c, s) in enumerate(pts):
                if i < k:
                    ax.scatter([re], [im], s=s, color=c, ec=T["bg"], lw=0.5, zorder=4)
                elif i == k:
                    ax.scatter([re], [im], s=s * 2.2, color=c, ec=T["core"], lw=1.6,
                               zorder=6, alpha=0.95)
                else:
                    ax.scatter([re], [im], s=s * 0.5, color=T["muted"], alpha=0.25, zorder=3)
            ax.set_xlabel(X["spec_xlabel"]); ax.set_ylabel(X["spec_ylabel"])
            ax.text(0.02, 0.95, X["spec_unstable"], fontsize=8, color=T["gold"],
                    transform=ax.transAxes, va="top")
            ax.text(0.02, 0.88, X["spec_decaying"], fontsize=8, color=T["cyan"],
                    transform=ax.transAxes, va="top")
            ax.text(0.02, 0.81, f"slots: {k}/15", fontsize=8, color=T["muted"],
                    transform=ax.transAxes, va="top")
        a.frames.append(state)
    return a


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["en", "ru"], default=None)
    ap.add_argument("--fps", type=int, default=14)
    args = ap.parse_args()
    langs = [args.lang] if args.lang else ["en", "ru"]
    for lang in langs:
        T = THEMES["dark"]
        out = ANIM / lang
        anim_echoing(T, X := labels(lang), lang).draw(out / "anim_echoing.gif")
        anim_scaling(T, X, lang).draw(out / "anim_scaling.gif")
        anim_collapse(T, X, lang).draw(out / "anim_collapse.gif")
        anim_dial(T, X, lang).draw(out / "anim_dial.gif")
        anim_spectrum(T, X, lang).draw(out / "anim_spectrum.gif")
    (ANIM / "manifest.json").write_text(json.dumps(
        {"seed": SEED, "fps": args.fps, "languages": langs,
         "animations": ["anim_echoing", "anim_scaling", "anim_collapse",
                        "anim_dial", "anim_spectrum"]}, indent=2) + "\n")
    print(f"[anim] done  (seed {SEED})")


if __name__ == "__main__":
    main()
