"""Generate the four animated GIFs of ``formal_choptuik/assets/gifs``.

All animations are rendered from the deterministic mode model (seed 1993)
in the cosmic-dark palette that matches the SVG banners:

* ``collapse_animation.gif``   — three families near the critical threshold
* ``echoing_animation.gif``    — DSS echoing with the echo-phase dial
* ``scaling_animation.gif``    — the mass scaling law assembled point by point
* ``attractor_animation.gif``  — schematic phase portrait of the codim-1 attractor

Usage::

    python scripts/generate_animations.py [--out DIR] [--fps 18]
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from choptuik_service.evolver import ECHO_PERIOD, GAMMA, LAMBDA0, ModeModel  # noqa: E402

fm.fontManager.addfont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
plt.rcParams.update({
    "font.sans-serif": ["DejaVu Sans"],
    "axes.unicode_minus": False,
})

T = {
    "bg": "#0F172A", "text": "#F1F5F9", "muted": "#94A3B8", "grid": "#1E293B",
    "band": "#16213C", "gold": "#E8B44A", "violet": "#9B8CDE",
    "cyan": "#4CC9F0", "red": "#E86A6A", "green": "#8FB7A4",
}
FOOTER = "formal_choptuik · seed 1993 · deterministic mode model"


def _style(ax) -> None:
    ax.set_facecolor(T["bg"])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(T["muted"])
    ax.tick_params(colors=T["muted"], labelsize=8)
    ax.grid(True, color=T["grid"], alpha=0.5, linewidth=0.6)
    ax.set_axisbelow(True)


def _decor(fig) -> None:
    fig.patch.set_facecolor(T["bg"])
    fig.text(0.99, 0.012, FOOTER, ha="right", fontsize=7, color=T["muted"], alpha=0.8)


# ----------------------------------------------------------------------
def animate_collapse(out: Path, fps: int) -> None:
    model = ModeModel()
    r = model.grid
    taus = np.linspace(-0.4, 3.0, 48)
    cases = {
        "Subcritical: dispersal": lambda tau: model.profile(tau) * math.exp(-0.8 * max(tau, 0)),
        "Critical: DSS echoing": model.profile,
        "Supercritical: collapse": lambda tau: model.profile(tau) * (1.0 + 0.35 * max(tau, 0)),
    }
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 4.0), sharey=True, constrained_layout=True)
    _decor(fig)
    lines, bh = [], []
    for ax, (name, _) in zip(axes, cases.items()):
        _style(ax)
        ax.set_title(name, color=T["text"], fontsize=11)
        ax.set_xlabel(r"$r$", color=T["text"])
        ax.set_xlim(0, 10)
        ax.set_ylim(-0.55, 1.9)
        (ln,) = ax.plot(r, np.zeros_like(r), color=T["gold"], lw=2.0)
        lines.append(ln)
        marker = ax.scatter([], [], s=0, color="#05060C", zorder=5)
        ring = ax.scatter([], [], s=0, facecolors="none", edgecolors=T["red"], linewidths=1.4, zorder=6)
        bh.append((marker, ring))
    axes[0].set_ylabel(r"$\phi(r,\tau)$", color=T["text"])
    title = fig.suptitle("", color=T["text"], fontsize=12)

    def update(i: int):
        tau = taus[i]
        for (marker, ring), (name, fn) in zip(bh, cases.items()):
            phi = fn(float(tau))
            lines[list(cases).index(name)].set_data(r, phi)
            if "Supercritical" in name and tau > 1.2:
                rad = 0.55 * min(max(tau - 1.2, 0), 1.6) + 0.35
                marker.set_sizes([int(rad * 260)])
                marker.set_offsets(np.zeros((1, 2)))
                ring.set_sizes([int(rad * 300)])
                ring.set_offsets(np.zeros((1, 2)))
            else:
                marker.set_sizes([0]); ring.set_sizes([0])
        title.set_text(
            f"Gravitational collapse of a massless scalar field — log-time  τ = {tau:5.2f}   "
            f"(γ = 1/λ₀ = {GAMMA:.3f})"
        )
        return [title, *lines]

    anim = FuncAnimation(fig, update, frames=len(taus), blit=False, interval=1000 // fps)
    anim.save(out / "collapse_animation.gif", writer=PillowWriter(fps=fps),
              savefig_kwargs={"facecolor": T["bg"]})
    plt.close(fig)


# ----------------------------------------------------------------------
def animate_echoing(out: Path, fps: int) -> None:
    model = ModeModel(n_grid=200)
    r = model.grid
    x = np.log(np.maximum(r, 1e-3) / r.max())  # ln rho on a fixed window
    periods = 4
    steps_per_period = 18
    taus = np.linspace(0, periods * ECHO_PERIOD, periods * steps_per_period)
    kappa = 0.55
    wavelet = lambda u: np.cosh(1.5 * u) ** -1 * np.cos(2.5 * u)

    fig, (a, b) = plt.subplots(1, 2, figsize=(10.6, 4.2),
                               gridspec_kw={"width_ratios": [2.2, 1]},
                               constrained_layout=True)
    _decor(fig)
    _style(a); _style(b)
    a.set_xlim(-4.4, 4.4); a.set_ylim(-0.45, 1.35)
    a.set_xlabel(r"$\ln\rho$", color=T["text"]); a.set_ylabel(r"$\psi$", color=T["text"])
    a.set_title("DSS echoing: profile drifts right by Δ each period", color=T["text"], fontsize=11)
    (solid,) = a.plot([], [], color=T["gold"], lw=2.2, label=r"$\psi(\rho,\tau)$")
    (ghost,) = a.plot([], [], color=T["violet"], lw=2.6, ls="--",
                      label=r"$e^{-\kappa\Delta}\,\psi(\rho\,e^{\Delta},\tau-\Delta)$")
    a.legend(loc="upper right", frameon=False, fontsize=8.5)
    for txt in a.get_legend().get_texts():
        txt.set_color(T["text"])

    b.set_xlim(-1.35, 1.35); b.set_ylim(-1.35, 1.35)
    b.set_aspect("equal"); b.axis("off")
    b.set_title("echo-phase dial (period Δ)", color=T["text"], fontsize=10.5)
    dial = b.plot(np.cos(np.linspace(0, 2 * np.pi, 100)) * 1.0,
                  np.sin(np.linspace(0, 2 * np.pi, 100)) * 1.0,
                  color=T["muted"], lw=1.2)[0]
    (needle,) = b.plot([], [], color=T["gold"], lw=2.6)
    phase_text = b.text(0, -1.22, "", ha="center", color=T["text"], fontsize=10)

    def update(i: int):
        tau = taus[i]
        s = tau % ECHO_PERIOD
        n = int(tau // ECHO_PERIOD)
        solid_x = x
        solid_y = math.exp(kappa * s) * wavelet(x - s)
        solid.set_data(solid_x, solid_y)
        # ghost: the same profile one period earlier, rescaled + reshifted
        sp = (tau - ECHO_PERIOD) % ECHO_PERIOD
        ghost_y = math.exp(kappa * sp) * wavelet(x - sp)
        ghost.set_data(solid_x, ghost_y)
        ang = 2 * np.pi * s / ECHO_PERIOD
        needle.set_data([0, 0.95 * np.cos(ang - np.pi / 2)],
                        [0, 0.95 * np.sin(ang - np.pi / 2)])
        phase_text.set_text(f"τ mod Δ = {s:.3f}   ·   echo #{n}")
        return [solid, ghost, needle, phase_text]

    anim = FuncAnimation(fig, update, frames=len(taus), blit=False, interval=1000 // fps)
    anim.save(out / "echoing_animation.gif", writer=PillowWriter(fps=fps),
              savefig_kwargs={"facecolor": T["bg"]})
    plt.close(fig)


# ----------------------------------------------------------------------
def animate_scaling(out: Path, fps: int) -> None:
    model = ModeModel()
    d = np.logspace(-7, -1.5, 24)
    m = np.array([model.black_hole_mass(x) for x in d])
    x, y = np.log(d), np.log(m)
    hold = 10
    frames = len(d) + hold

    fig, ax = plt.subplots(figsize=(8.6, 5.2), constrained_layout=True)
    _decor(fig); _style(ax)
    ax.set_xlim(x.min() - 0.4, x.max() + 0.4)
    ax.set_ylim(y.min() - 0.4, y.max() + 0.4)
    ax.set_xlabel(r"$\ln|p-p_*|$", color=T["text"])
    ax.set_ylabel(r"$\ln M_{BH}$", color=T["text"])
    ax.set_title("Assembling the mass scaling law, point by point",
                 color=T["text"], fontsize=12.5)
    scatter = ax.scatter([], [], s=30, color=T["cyan"], zorder=3,
                         edgecolors=T["bg"], linewidths=0.4)
    (fit_line,) = ax.plot([], [], color=T["gold"], lw=2.0, zorder=2)
    gamma_text = ax.text(0.04, 0.08, "", transform=ax.transAxes, color=T["gold"],
                         fontsize=11.5,
                         bbox=dict(boxstyle="round,pad=0.5", fc=T["band"], ec=T["gold"], lw=0.9))

    def update(i: int):
        n = min(i + 1, len(d))
        scatter.set_offsets(np.column_stack([x[:n], y[:n]]))
        if n >= 3:
            k, b = np.polyfit(x[:n], y[:n], 1)
            xs = np.linspace(x.min(), x[:n].max(), 40)
            fit_line.set_data(xs, k * xs + b)
            gamma_text.set_text(f"γ_fit = {k:.4f}\nγ_ref  = {GAMMA:.4f}")
        else:
            gamma_text.set_text(f"points: {n}/24")
        return [scatter, fit_line, gamma_text]

    anim = FuncAnimation(fig, update, frames=frames, blit=False, interval=1000 // fps)
    anim.save(out / "scaling_animation.gif", writer=PillowWriter(fps=fps),
              savefig_kwargs={"facecolor": T["bg"]})
    plt.close(fig)


# ----------------------------------------------------------------------
def animate_attractor(out: Path, fps: int) -> None:
    """Schematic phase portrait: codimension-one attractor on the threshold.

    Geometry: every trajectory sweeps left -> right; near the centre of the
    frame it is drawn toward the critical solution (the horizontal violet
    line, an attractor of codimension one), rides it for a while, then
    peels off upward (supercritical -> collapse) or downward (subcritical
    -> dispersal).  Only the exactly critical trajectory stays on the line.
    """
    frames = 64
    x = np.linspace(-3.8, 3.8, 160)

    def traj(p: float, peel: float) -> np.ndarray:
        y = 1.7 + p * np.exp(-1.4 * (x + 3.8)) \
            + peel * np.maximum(0.0, x - 0.7) ** 2.3
        return y

    ps = [(-0.9, -0.55), (-0.45, -0.25), (0.0, 0.0), (0.45, 0.25), (0.9, 0.55)]
    paths = [(x, traj(p, peel)) for p, peel in ps]

    fig, ax = plt.subplots(figsize=(8.8, 5.4), constrained_layout=True)
    _decor(fig); _style(ax)
    ax.set_xlim(-3.9, 3.9); ax.set_ylim(0.15, 3.35)
    ax.set_xlabel("evolution  (schematic)", color=T["text"])
    ax.set_ylabel("growing-mode amplitude", color=T["text"])
    ax.set_title("Phase portrait (schematic): a codimension-one attractor",
                 color=T["text"], fontsize=12.5)

    ax.plot(x, traj(0.0, 0.0), color=T["violet"], lw=2.4, zorder=4,
            label="critical solution — codimension-one attractor")
    for (px, py), (p, _) in zip(paths, ps):
        color = T["cyan"] if p < 0 else (T["gold"] if p == 0 else T["red"])
        ax.plot(px, py, color=color, lw=1.1, alpha=0.4, zorder=2)
    dots = [ax.plot([], [], "o", color=T["cyan"] if p < 0 else (T["gold"] if p == 0 else T["red"]),
                    ms=7, zorder=5)[0] for p, _ in ps]
    bh = ax.scatter([], [], s=0, color="#05060C", zorder=6)
    bh_ring = ax.scatter([], [], s=0, facecolors="none", edgecolors=T["red"],
                         linewidths=1.8, zorder=7)
    ax.text(-3.75, 0.32, "dispersal  (p < p*)", color=T["cyan"], fontsize=10)
    ax.text(1.05, 3.05, "collapse  (p > p*)", color=T["red"], fontsize=10)
    ax.text(-3.75, 2.98, "one unstable direction ⇒ γ = 1/λ₀", color=T["violet"], fontsize=10)
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    for txt in ax.get_legend().get_texts():
        txt.set_color(T["text"])
    ax.annotate("black hole", xy=(3.15, 3.02), color=T["red"], fontsize=9.5,
                ha="right")

    def update(i: int):
        idx = int(i / (frames - 1) * (len(x) - 1))
        for dot, (px, py) in zip(dots, paths):
            dot.set_data([px[idx]], [py[idx]])
        super_x, super_y = paths[-1]
        if super_x[idx] > 2.55:
            bh.set_sizes([300]); bh.set_offsets([[super_x[idx], super_y[idx]]])
            bh_ring.set_sizes([380]); bh_ring.set_offsets([[super_x[idx], super_y[idx]]])
        else:
            bh.set_sizes([0]); bh_ring.set_sizes([0])
        return [*dots, bh, bh_ring]

    anim = FuncAnimation(fig, update, frames=frames, blit=False, interval=1000 // fps)
    anim.save(out / "attractor_animation.gif", writer=PillowWriter(fps=fps),
              savefig_kwargs={"facecolor": T["bg"]})
    plt.close(fig)


# ----------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="output dir (default: repo assets/gifs)")
    ap.add_argument("--fps", type=int, default=18)
    args = ap.parse_args()
    out = Path(args.out) if args.out else ROOT / "assets" / "gifs"
    out.mkdir(parents=True, exist_ok=True)

    print("rendering collapse_animation.gif ...")
    animate_collapse(out, args.fps)
    print("rendering echoing_animation.gif ...")
    animate_echoing(out, args.fps)
    print("rendering scaling_animation.gif ...")
    animate_scaling(out, args.fps)
    print("rendering attractor_animation.gif ...")
    animate_attractor(out, args.fps)
    print(f"GIFs written to {out}")


if __name__ == "__main__":
    main()
