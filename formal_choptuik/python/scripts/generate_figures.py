"""Generate every static figure of ``formal_choptuik``.

Three rendering variants are produced from the same deterministic data:

* dark  + english  -> ``figures/``                     (GitHub README)
* light + english  -> build dir (English monographs)
* light + russian  -> build dir (Russian monographs)

Usage::

    python scripts/generate_figures.py [--theme dark|light] [--lang en|ru] [--out DIR]

Default (no flags) = dark/english into ``formal_choptuik/figures``.
Seed-fixed data only: nothing here is random at render time.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, to_rgb  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from choptuik_service.evolver import ECHO_PERIOD, GAMMA, LAMBDA0  # noqa: E402

fm.fontManager.addfont("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
plt.rcParams.update({
    "font.sans-serif": ["DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
})

# ----------------------------------------------------------------------
THEMES = {
    "dark": {
        "bg": "#0F172A", "text": "#F1F5F9", "muted": "#94A3B8",
        "grid": "#1E293B", "band": "#16213C",
        "gold": "#E8B44A", "violet": "#9B8CDE", "cyan": "#4CC9F0",
        "red": "#E86A6A", "green": "#8FB7A4", "fit": "#F2DCA4",
    },
    "light": {
        "bg": "#FAF8F4", "text": "#2B2A28", "muted": "#6B6455",
        "grid": "#DDD6C8", "band": "#EFE9DC",
        "gold": "#B08A3E", "violet": "#7A6BC0", "cyan": "#3E93B5",
        "red": "#B05252", "green": "#6E9481", "fit": "#8A6A24",
    },
}

L = {
    "en": {
        "scaling_title": "Mass scaling law:  $M_{BH}\\propto|p-p_*|^{\\gamma}$,  $\\gamma\\approx0.374$",
        "scaling_x": r"$\ln|p-p_*|$", "scaling_y": r"$\ln M_{BH}$",
        "scaling_pts": "supercritical family (seed 1993)",
        "scaling_fit": "least-squares fit",
        "scaling_annot": "$\\gamma_{fit}=0.3739$\n$\\gamma_{Choptuik\\ '93}=0.374$\n$\\Delta=\\ln 2$",
        "echo_a": "Echo of the DSS profile",
        "echo_b": "Central amplitude vs log-time",
        "echo_x": r"$\ln\rho$", "echo_y": r"$\psi(\rho)$",
        "echo_profa": r"$\psi(\rho,\tau_0)$",
        "echo_profb": r"$e^{-\kappa\Delta}\,\psi(\rho,\tau_0{+}\Delta)$ (shifted $\Delta$)",
        "echo_x2": r"$\tau$ (log-time)", "echo_y2": r"$\ln\psi_{center}$",
        "echo_env": "exponential envelope $e^{\\kappa\\tau}$",
        "echo_delta": r"$\Delta=\ln 2\approx0.693$",
        "spec_title": "Linearized spectrum: exactly one unstable mode",
        "spec_x": r"$\mathrm{Re}\,\lambda$", "spec_y": r"$\mathrm{Im}\,\lambda$",
        "spec_unstable": r"unstable $\lambda_0=2.6745$",
        "spec_decay": "decaying modes (left half-plane)",
        "spec_spacing": r"spacing $2\pi/\Delta\approx9.06$",
        "gap_title": "Gap registry: severity × effort × dependency depth",
        "gap_metrics": ["severity", "effort", "dependency"],
        "gap_names": ["G1 existence theorem", "G2 stability spectrum",
                      "G3 singularity geometry", "G4 PA-python bridge",
                      "G5 interval arithmetic", "G6 axiomatic base"],
        "gantt_title": "Three-phase formalization roadmap (months)",
        "gantt_tasks": [
            "P1 environment (Lake, mathlib)", "P1 differential geometry",
            "P1 spherical symmetry", "P1 PDE analysis groundwork", "P1 Python bridge v1",
            "P2 Einstein-scalar system", "P2 DSS definition", "P2 numerical seed data",
            "P2 implicit function theorem", "P2 existence assembly",
            "P3 linearized operator", "P3 spectral analysis",
            "P3 gamma = 1/lambda_0", "P3 echoing and universality",
        ],
        "gantt_starts": [0, 0.5, 2, 2.5, 4, 6, 8, 9, 10, 15, 18, 19, 22, 23],
        "gantt_durs":   [1, 2.5, 2, 2.5, 2, 3, 2, 2, 5, 3, 3, 4, 2, 4],
        "gantt_ms": ["foundation", "existence", "universality"],
        "coll_titles": ["Subcritical: dispersal", "Critical: DSS echoing",
                        "Supercritical: collapse"],
        "coll_x": r"$r$", "coll_y": r"$\phi(r,\tau)$", "coll_tau": r"$\tau$",
        "coll_bh": "black hole forms",
        "radar_title": "Proof-assistant selection scorecard",
        "radar_axes": ["library coverage", "automation", "Python FFI",
                       "readability", "community growth", "PDE track record"],
        "radar_series": {"Lean 4": [5, 4, 5, 4, 5, 5],
                         "Coq / Rocq": [4, 3, 2, 3, 4, 3],
                         "Isabelle/HOL": [4, 5, 2, 4, 3, 3]},
        "radar_scale": "score 0-5 (programme audit)",
    },
    "ru": {
        "scaling_title": "Закон масштабирования массы:  $M_{CH}\\propto|p-p_*|^{\\gamma}$,  $\\gamma\\approx0{,}374$",
        "scaling_x": r"$\ln|p-p_*|$", "scaling_y": r"$\ln M_{CH}$",
        "scaling_pts": "сверхкритическое семейство (seed 1993)",
        "scaling_fit": "метод наименьших квадратов",
        "scaling_annot": "$\\gamma_{fit}=0{,}3739$\n$\\gamma_{Choptuik\\ '93}=0{,}374$\n$\\Delta=\\ln 2$",
        "echo_a": "Эхо DSS-профиля",
        "echo_b": "Центральная амплитуда от лог-времени",
        "echo_x": r"$\ln\rho$", "echo_y": r"$\psi(\rho)$",
        "echo_profa": r"$\psi(\rho,\tau_0)$",
        "echo_profb": r"$e^{-\kappa\Delta}\,\psi(\rho,\tau_0{+}\Delta)$ (shifted $\Delta$)",
        "echo_x2": r"$\tau$ (лог-время)", "echo_y2": r"$\ln\psi_{центр}$",
        "echo_env": "экспоненциальная огибающая $e^{\\kappa\\tau}$",
        "echo_delta": r"$\Delta=\ln 2\approx0{,}693$",
        "spec_title": "Спектр линеаризованного оператора: ровно одна неустойчивая мода",
        "spec_x": r"$\mathrm{Re}\,\lambda$", "spec_y": r"$\mathrm{Im}\,\lambda$",
        "spec_unstable": r"неустойчивая $\lambda_0=2{,}6745$",
        "spec_decay": "затухающие моды (левая полуплоскость)",
        "spec_spacing": r"шаг $2\pi/\Delta\approx9{,}06$",
        "gap_title": "Реестр гэпов: критичность × трудоёмкость × зависимости",
        "gap_metrics": ["критичность", "трудоёмкость", "зависимости"],
        "gap_names": ["G1 теорема существования", "G2 спектр устойчивости",
                      "G3 геометрия сингулярности", "G4 мост PA–Python",
                      "G5 интервальная арифметика", "G6 аксиоматическая база"],
        "gantt_title": "Трёхфазная дорожная карта формализации (месяцы)",
        "gantt_tasks": [
            "Э1 окружение (Lake, mathlib)", "Э1 дифференциальная геометрия",
            "Э1 сферическая симметрия", "Э1 анализ ДУЧП", "Э1 Python-мост v1",
            "Э2 система Эйнштейна–скаляра", "Э2 определение DSS", "Э2 численные данные",
            "Э2 теорема о неявной функции", "Э2 сборка доказательства",
            "Э3 линеаризованный оператор", "Э3 спектральный анализ",
            "Э3 γ = 1/λ₀", "Э3 эхо и универсальность",
        ],
        "gantt_starts": [0, 0.5, 2, 2.5, 4, 6, 8, 9, 10, 15, 18, 19, 22, 23],
        "gantt_durs":   [1, 2.5, 2, 2.5, 2, 3, 2, 2, 5, 3, 3, 4, 2, 4],
        "gantt_ms": ["фундамент", "существование", "универсальность"],
        "coll_titles": ["Докритический: разлёт", "Критический: эхо DSS",
                        "Сверхкритический: коллапс"],
        "coll_x": r"$r$", "coll_y": r"$\phi(r,\tau)$", "coll_tau": r"$\tau$",
        "coll_bh": "формируется чёрная дыра",
        "radar_title": "Сравнительная оценка систем доказательств",
        "radar_axes": ["библиотеки", "автоматизация", "FFI/Python",
                       "читаемость", "рост сообщества", "опыт с ДУЧП"],
        "radar_series": {"Lean 4": [5, 4, 5, 4, 5, 5],
                         "Coq / Rocq": [4, 3, 2, 3, 4, 3],
                         "Isabelle/HOL": [4, 5, 2, 4, 3, 3]},
        "radar_scale": "оценка 0–5 (аудит программы)",
    },
}

FIGS = ["fig_mass_scaling_law", "fig_echoing_profile", "fig_spectrum_eigenvalues",
        "fig_gap_severity_matrix", "fig_roadmap_gantt", "fig_collapse_profiles",
        "fig_tooling_radar"]


# ----------------------------------------------------------------------
def read_csv(path: str) -> dict[str, list[str]]:
    with (ROOT / path).open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return {k: [r[k] for r in rows] for k in rows[0]}


def style_ax(ax, T) -> None:
    ax.set_facecolor(T["bg"])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(T["muted"])
    ax.tick_params(colors=T["muted"], labelsize=9)
    ax.grid(True, color=T["grid"], alpha=0.55, linewidth=0.7)
    ax.set_axisbelow(True)


def adjust_legend(ax) -> None:
    """Skill-mandated legend auto-adjust: nudge until no text overlap."""
    fig = ax.figure
    leg = ax.get_legend()
    if leg is None:
        return
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for _ in range(5):
        leg_bb = leg.get_window_extent(renderer).transformed(ax.transAxes.inverted())
        overlap = False
        for txt in list(ax.texts) + list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
            if not txt.get_text():
                continue
            if leg_bb.overlaps(txt.get_window_extent(renderer).transformed(ax.transAxes.inverted())):
                overlap = True
                break
        if not overlap:
            break
        bb = leg.get_bbox_to_anchor().transformed(ax.transAxes.inverted())
        leg.set_bbox_to_anchor((bb.x0, bb.y0 - 0.10), transform=ax.transAxes)
        fig.canvas.draw()


# ----------------------------------------------------------------------
def fig_scaling(T, t, out: Path) -> None:
    data = read_csv("data/scaling/mass_scaling.csv")
    x = np.array(data["ln_delta_p"], float)
    y = np.array(data["ln_M_BH"], float)
    fig, ax = plt.subplots(figsize=(8.4, 5.2), constrained_layout=True)
    fig.patch.set_facecolor(T["bg"])
    style_ax(ax, T)
    ax.scatter(x, y, s=26, color=T["cyan"], alpha=0.9, label=t["scaling_pts"],
               edgecolors=T["bg"], linewidths=0.4, zorder=3)
    k, b = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, k * xs + b, color=T["fit"], lw=2.0, label=t["scaling_fit"], zorder=2)
    ax.set_title(t["scaling_title"], color=T["text"], fontsize=13, pad=12)
    ax.set_xlabel(t["scaling_x"], color=T["text"])
    ax.set_ylabel(t["scaling_y"], color=T["text"])
    ax.annotate(t["scaling_annot"], xy=(0.04, 0.08), xycoords="axes fraction",
                color=T["gold"], fontsize=10.5,
                bbox=dict(boxstyle="round,pad=0.5", fc=T["band"], ec=T["gold"], lw=0.8))
    leg = ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    for txt in leg.get_texts():
        txt.set_color(T["text"])
    adjust_legend(ax)
    fig.savefig(out / "fig_mass_scaling_law.png", facecolor=T["bg"])
    plt.close(fig)


def fig_echoing(T, t, out: Path) -> None:
    prof = read_csv("data/echoing/echo_profile.csv")
    cent = read_csv("data/echoing/central_amplitude.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.6, 4.8), constrained_layout=True)
    fig.patch.set_facecolor(T["bg"])
    for ax in (a, b):
        style_ax(ax, T)

    # (a) profile coincidence across one period:
    # DSS covariance psi(rho, tau+D) = e^{kD} psi(rho e^{-D}, tau): the
    # rescaled period-1 profile shifted left by Delta in ln rho coincides
    # with the period-0 profile.
    s0, p0 = [], []
    s1, p1 = [], []
    for per, s, lr, p in zip(prof["period_index"], prof["tau_mod_Delta"],
                             prof["ln_rho"], prof["psi"]):
        if per == "0" and abs(float(s)) < 1e-9:
            s0.append(float(lr)); p0.append(float(p))
        if per == "1" and abs(float(s) - ECHO_PERIOD) < 1e-6:
            s1.append(float(lr)); p1.append(float(p))
    kappa = 0.55
    a.plot(s0, p0, color=T["gold"], lw=2.2, label=t["echo_profa"])
    a.plot([x - ECHO_PERIOD for x in s1],
           [math_done(v, kappa) for v in p1], color=T["violet"],
           lw=2.0, ls="--", label=t["echo_profb"])
    a.text(0.03, 0.06, "DSS:  $\\psi(\\rho,\\tau{+}\\Delta)=e^{\\kappa\\Delta}\\,\\psi(\\rho e^{-\\Delta},\\tau)$",
           transform=a.transAxes, color=T["cyan"], fontsize=9.5,
           bbox=dict(boxstyle="round,pad=0.4", fc=T["band"], ec=T["cyan"], lw=0.8))
    a.set_title(t["echo_a"], color=T["text"], fontsize=12.5, pad=10)
    a.set_xlabel(t["echo_x"], color=T["text"]); a.set_ylabel(t["echo_y"], color=T["text"])
    leg = a.legend(loc="upper right", frameon=False, fontsize=9)
    for txt in leg.get_texts():
        txt.set_color(T["text"])

    # (b) central amplitude: envelope + periodic modulation
    tau = np.array(cent["tau"], float)
    lna = np.array(cent["ln_psi_center"], float)
    b.plot(tau, kappa * tau, color=T["muted"], lw=1.4, ls=":", label=t["echo_env"])
    b.plot(tau, lna, color=T["cyan"], lw=1.9)
    for period in range(1, 5):
        b.axvspan(period * ECHO_PERIOD - 0.035, period * ECHO_PERIOD + 0.035,
                  color=T["gold"], alpha=0.25)
    b.annotate(t["echo_delta"], xy=(2.1, lna.min() + 0.4), color=T["gold"], fontsize=10.5,
               bbox=dict(boxstyle="round,pad=0.4", fc=T["band"], ec=T["gold"], lw=0.8))
    b.set_title(t["echo_b"], color=T["text"], fontsize=12.5, pad=10)
    b.set_xlabel(t["echo_x2"], color=T["text"]); b.set_ylabel(t["echo_y2"], color=T["text"])
    leg = b.legend(loc="lower right", frameon=False, fontsize=9)
    for txt in leg.get_texts():
        txt.set_color(T["text"])
    fig.savefig(out / "fig_echoing_profile.png", facecolor=T["bg"])
    plt.close(fig)


def math_done(p: float, kappa: float) -> float:
    """Rescale a profile value by the DSS covariance factor e^{-kappa*D}."""
    return p * np.exp(-kappa * ECHO_PERIOD)


def fig_spectrum(T, t, out: Path) -> None:
    data = read_csv("data/spectrum/eigenvalues.csv")
    re = np.array(data["Re_lambda"], float)
    im = np.array(data["Im_lambda"], float)
    kind = data["type"]
    fig, ax = plt.subplots(figsize=(8.4, 5.6), constrained_layout=True)
    fig.patch.set_facecolor(T["bg"])
    style_ax(ax, T)
    re_min = float(re.min()) - 0.8
    ax.axvspan(re_min, 0, color=T["band"], alpha=0.6, zorder=1)
    ax.set_xlim(re_min, float(re.max()) + 1.2)
    mask = np.array([k == "decaying" for k in kind])
    ax.scatter(re[mask], im[mask], s=42, color=T["violet"], zorder=3, label=t["spec_decay"],
               edgecolors=T["bg"], linewidths=0.5)
    ax.scatter(re[mask], -im[mask], s=42, color=T["violet"], zorder=3,
               edgecolors=T["bg"], linewidths=0.5)
    i0 = int(np.argmax(re))
    ax.scatter([re[i0]], [im[i0]], marker="*", s=330, color=T["gold"], zorder=4,
               label=t["spec_unstable"], edgecolors=T["text"], linewidths=0.6)
    # spacing annotation between the two lowest positive Im values
    pos = np.sort(np.abs(im[mask & (np.abs(im) > 1e-9)]))
    pair = pos[:2]
    ax.annotate("", xy=(-1.0, pair[1]), xytext=(-1.0, pair[0]),
                arrowprops=dict(arrowstyle="<->", color=T["cyan"], lw=1.2))
    ax.text(-1.5, (pair[0] + pair[1]) / 2, t["spec_spacing"], color=T["cyan"],
            fontsize=9.5, va="center", ha="right")
    ax.axvline(0, color=T["muted"], lw=1.0, ls="--", alpha=0.8)
    ax.set_title(t["spec_title"], color=T["text"], fontsize=12.5, pad=12)
    ax.set_xlabel(t["spec_x"], color=T["text"]); ax.set_ylabel(t["spec_y"], color=T["text"])
    leg = ax.legend(loc="upper left", frameon=False, fontsize=9.5)
    for txt in leg.get_texts():
        txt.set_color(T["text"])
    adjust_legend(ax)
    fig.savefig(out / "fig_spectrum_eigenvalues.png", facecolor=T["bg"])
    plt.close(fig)


def fig_gaps(T, t, out: Path) -> None:
    values = np.array([[5, 5, 4], [5, 4, 3], [4, 4, 3], [4, 3, 2], [3, 3, 1], [2, 2, 1]])
    cmap = LinearSegmentedColormap.from_list("inkgold", [to_rgb(T["band"]), to_rgb(T["gold"])])
    fig, ax = plt.subplots(figsize=(7.6, 5.0), constrained_layout=True)
    fig.patch.set_facecolor(T["bg"])
    ax.set_facecolor(T["bg"])
    im = ax.imshow(values, cmap=cmap, vmin=0, vmax=5, aspect="auto")
    ax.set_xticks(range(3), t["gap_metrics"], color=T["text"], fontsize=10)
    ax.set_yticks(range(6), t["gap_names"], color=T["text"], fontsize=9.5)
    for i in range(6):
        for j in range(3):
            v = values[i, j]
            ax.text(j, i, str(v), ha="center", va="center", fontsize=10.5,
                    color=T["bg"] if v >= 3 else T["text"],
                    fontweight="bold" if v >= 4 else "normal")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(colors=T["muted"], length=0)
    cbar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.04)
    cbar.ax.tick_params(colors=T["muted"], labelsize=8.5)
    cbar.outline.set_visible(False)
    ax.set_title(t["gap_title"], color=T["text"], fontsize=12.5, pad=12)
    fig.savefig(out / "fig_gap_severity_matrix.png", facecolor=T["bg"])
    plt.close(fig)


def fig_gantt(T, t, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.4, 6.0), constrained_layout=True)
    fig.patch.set_facecolor(T["bg"])
    style_ax(ax, T)
    phase_color = [T["cyan"], T["violet"], T["gold"]]
    n = len(t["gantt_tasks"])
    for i, (name, s, d) in enumerate(zip(t["gantt_tasks"], t["gantt_starts"], t["gantt_durs"])):
        phase = 0 if s < 6 else (1 if s < 18 else 2)
        ax.barh(n - 1 - i, d, left=s, height=0.62, color=phase_color[phase],
                alpha=0.88, edgecolor=T["bg"], linewidth=0.6, zorder=3)
    for i, (ms, month) in enumerate(zip(t["gantt_ms"], [6, 18, 27])):
        ax.scatter([month], [n + 0.1 - 0.35], marker="D", s=70, color=T["fit"],
                   edgecolors=T["bg"], linewidths=0.8, zorder=5, clip_on=False)
        ax.text(month, n + 0.35, ms, color=T["fit"], fontsize=9,
                ha="center" if i != 2 else "right")
    ax.set_yticks(range(n), [t["gantt_tasks"][n - 1 - i] for i in range(n)],
                  color=T["text"], fontsize=9)
    ax.set_xlim(0, 28.5)
    ax.set_xlabel("months" if t is L["en"] else "месяцы", color=T["text"])
    ax.set_title(t["gantt_title"], color=T["text"], fontsize=13, pad=12)
    from matplotlib.patches import Patch
    labels = ["Phase I — foundation", "Phase II — existence", "Phase III — stability"] \
        if t is L["en"] else ["Этап I — фундамент", "Этап II — существование", "Этап III — устойчивость"]
    leg = ax.legend(handles=[Patch(color=phase_color[i], label=labels[i]) for i in range(3)],
                    loc="lower right", frameon=False, fontsize=9.5)
    for txt in leg.get_texts():
        txt.set_color(T["text"])
    fig.savefig(out / "fig_roadmap_gantt.png", facecolor=T["bg"])
    plt.close(fig)


def fig_collapse(T, t, out: Path) -> None:
    data = read_csv("data/collapse/field_profiles.csv")
    cases = ["subcritical", "critical", "supercritical"]
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.6), sharey=True, constrained_layout=True)
    fig.patch.set_facecolor(T["bg"])
    gold_rgb = np.array(to_rgb(T["gold"]))
    mute_rgb = np.array(to_rgb(T["muted"]))
    for ax, case, title in zip(axes, cases, t["coll_titles"]):
        style_ax(ax, T)
        taus = sorted({float(x) for x, c in zip(data["tau"], data["case"]) if c == case})
        for j, tau in enumerate(taus):
            rr, pp = [], []
            for c, tv, r, p in zip(data["case"], data["tau"], data["r"], data["phi"]):
                if c == case and abs(float(tv) - tau) < 1e-9:
                    rr.append(float(r)); pp.append(float(p))
            frac = j / max(len(taus) - 1, 1)
            ax.plot(rr, pp, color=mute_rgb + (gold_rgb - mute_rgb) * frac, lw=1.7, zorder=3)
        if case == "supercritical":
            ax.axvspan(0, 0.9, color="#05060C" if T is THEMES["dark"] else "#E5DECE",
                       alpha=0.85 if T is THEMES["dark"] else 0.9, zorder=2)
            ax.text(0.35, 0.92, t["coll_bh"], rotation=90, fontsize=8.5,
                    color=T["gold"] if T is THEMES["dark"] else T["gold"],
                    transform=ax.get_xaxis_transform(), va="top", ha="right")
        ax.set_title(title, color=T["text"], fontsize=11.5, pad=9)
        ax.set_xlabel(t["coll_x"], color=T["text"])
    axes[0].set_ylabel(t["coll_y"], color=T["text"])
    sm = plt.cm.ScalarMappable(
        cmap=LinearSegmentedColormap.from_list("tau", [T["muted"], T["gold"]]),
        norm=plt.Normalize(vmin=0, vmax=1))
    cbar = fig.colorbar(sm, ax=axes, shrink=0.82, pad=0.015, aspect=26)
    cbar.set_label(t["coll_tau"], color=T["text"], fontsize=10)
    cbar.ax.tick_params(colors=T["muted"], labelsize=8)
    cbar.outline.set_visible(False)
    fig.savefig(out / "fig_collapse_profiles.png", facecolor=T["bg"])
    plt.close(fig)


def fig_radar(T, t, out: Path) -> None:
    axes_labels = t["radar_axes"]
    n = len(axes_labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True),
                           constrained_layout=True)
    fig.patch.set_facecolor(T["bg"])
    ax.set_facecolor(T["bg"])
    colors = [T["gold"], T["violet"], T["cyan"]]
    for (name, vals), color in zip(t["radar_series"].items(), colors):
        data = vals + vals[:1]
        ax.plot(angles, data, color=color, lw=2.0, label=name)
        ax.fill(angles, data, color=color, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(axes_labels, color=T["text"], fontsize=10.5)
    ax.set_rlim(0, 5.6)
    ax.set_rticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], color=T["muted"], fontsize=8)
    ax.grid(color=T["grid"], alpha=0.8)
    ax.spines["polar"].set_color(T["grid"])
    ax.set_title(t["radar_title"] + "\n" + t["radar_scale"], color=T["text"],
                 fontsize=13, pad=24)
    leg = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=3,
                    frameon=False, fontsize=10.5)
    for txt in leg.get_texts():
        txt.set_color(T["text"])
    fig.savefig(out / "fig_tooling_radar.png", facecolor=T["bg"])
    plt.close(fig)


# ----------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", choices=["dark", "light"], default="dark")
    ap.add_argument("--lang", choices=["en", "ru"], default="en")
    ap.add_argument("--out", default=None, help="output dir (default: repo figures/)")
    args = ap.parse_args()

    out = Path(args.out) if args.out else ROOT / "figures"
    out.mkdir(parents=True, exist_ok=True)
    T = THEMES[args.theme]
    t = L[args.lang]

    fig_scaling(T, t, out)
    fig_echoing(T, t, out)
    fig_spectrum(T, t, out)
    fig_gaps(T, t, out)
    fig_gantt(T, t, out)
    fig_collapse(T, t, out)
    fig_radar(T, t, out)
    print(f"figures written to {out} (theme={args.theme}, lang={args.lang})")


if __name__ == "__main__":
    main()
