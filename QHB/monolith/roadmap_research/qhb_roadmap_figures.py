#!/usr/bin/env python3
"""QHB v2.1.0 — фигуры исполнения роадмапа R1–R4 (RU + EN), глава 14.
Стиль согласован с пакетом: светлый фон, без верхних/правых осей, пунктирная сетка."""
import json
import math
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.font_manager as fm

fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.25
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams['font.size'] = 11

OUT = "/home/z/my-project/qhb_work/rfigs"
os.makedirs(OUT, exist_ok=True)
R = json.load(open("/home/z/my-project/qhb_work/roadmap_results.json"))

C_MAIN = "#1a4a7a"; C_ACC = "#2d7ab3"; C_NEG = "#a05a3c"; C_MUT = "#5a7a96"
C_OK = "#3a7a4a"

T = {
 "ru": {
  "r1a": ("Лестница объёмов R1: зазор долины против 1/L (β* = 3.3583)",
          "1/L", "Δ_F(β*, L)",
          "данные лестницы (L = 4…10⁶)", "фит 1 − 0.35/L + 0.03/L²", "Δ_F,∞ = 0.181777 (не заявляется как континуум)"),
  "r1b": ("Ричардсон-анализ R1: эффективный коэффициент c_eff(L) = L·(1 − Δ/Δ_∞)",
          "L", "c_eff(L)",
          "лестница", "модель 0.35 − 0.03/L", None),
  "r2a": ("Расщепление пары ±iω при неравных циркуляциях Γ = (1, 1, γ): законы ветвей",
          "γ = Γ₃/Γ₁", "частота пары",
          "ν_tr = (2+γ)/2π (теория)", "ν_int = √(3(1+2γ))/2π (теория)",
          "спектр (97 точек)", "γ = 1: обе = 3/(2π) (T11)"),
  "r2b": ("Устойчивость якоря: максимум |Re| по спектру",
          "γ", "max |Re|",
          "одноимённые циркуляции (0.2 ≤ γ ≤ 5)", "встречная циркуляция Γ₃ = −γ",
          "γ* = 0.5 (критерий Синге)", "нуль устойчивости"),
  "r3": ("Температурный замок R3: граница η_crit(T) — выживание при термальной активации",
          "T_gap (эффективная температура сектора зазора)", "η_crit(T)",
          "N = 10⁶ попыток", "N = 10¹² попыток", "N = 10¹⁸ попыток",
          "η_B (Planck 2018)", "T_c(β*) = 0.0886 — мостовая температура",
          "зона выживания (η < η_crit(T))"),
  "r4a": ("Восстановление формы хвоста R4: ошибки (T₀, E₀) против разрешения f",
          "f (масштаб разрешения res → f·res)", "относительная ошибка",
          "|ΔT₀|/T₀", "|ΔE₀|/E₀", "порог 10%", "f_crit = 0.1929"),
  "r4b": ("R4: fitted (T₀, E₀) против f — вырождение при f = 1, сходимость при малых f",
          "f", "параметр фита",
          "T₀ fitted", "E₀ fitted (×10⁻³)", "истина T₀ = 0.0043", "истина E₀ = 1.8"),
 },
 "en": {
  "r1a": ("R1 volume ladder: valley gap vs 1/L (β* = 3.3583)",
          "1/L", "Δ_F(β*, L)",
          "ladder data (L = 4…10⁶)", "fit 1 − 0.35/L + 0.03/L²", "Δ_F,∞ = 0.181777 (no continuum claim)"),
  "r1b": ("R1 Richardson analysis: effective coefficient c_eff(L) = L·(1 − Δ/Δ_∞)",
          "L", "c_eff(L)",
          "ladder", "model 0.35 − 0.03/L", None),
  "r2a": ("Splitting of the ±iω pair for unequal circulations Γ = (1, 1, γ): branch laws",
          "γ = Γ₃/Γ₁", "pair frequency",
          "ν_tr = (2+γ)/2π (theory)", "ν_int = √(3(1+2γ))/2π (theory)",
          "spectrum (97 points)", "γ = 1: both = 3/(2π) (T11)"),
  "r2b": ("Anchor stability: spectral maximum of |Re|",
          "γ", "max |Re|",
          "same-sign circulations (0.2 ≤ γ ≤ 5)", "opposite circulation Γ₃ = −γ",
          "γ* = 0.5 (Synge criterion)", "stability zero"),
  "r3": ("R3 thermal lock: the η_crit(T) boundary — survival under thermal activation",
          "T_gap (effective temperature of the gap sector)", "η_crit(T)",
          "N = 10⁶ attempts", "N = 10¹² attempts", "N = 10¹⁸ attempts",
          "η_B (Planck 2018)", "T_c(β*) = 0.0886 — bridge temperature",
          "survival zone (η < η_crit(T))"),
  "r4a": ("R4 tail-shape recovery: (T₀, E₀) errors vs resolution f",
          "f (resolution scale res → f·res)", "relative error",
          "|ΔT₀|/T₀", "|ΔE₀|/E₀", "10% threshold", "f_crit = 0.1929"),
  "r4b": ("R4: fitted (T₀, E₀) vs f — degeneracy at f = 1, convergence at small f",
          "f", "fitted parameter",
          "T₀ fitted", "E₀ fitted (×10⁻³)", "truth T₀ = 0.0043", "truth E₀ = 1.8"),
 },
}

def save(fig, name):
    fig.savefig(f"{OUT}/{name}.png", dpi=200, facecolor="white")
    plt.close(fig)
    print("saved", name)

def fig_r1(lang):
    r1 = R["r1_continuum"]
    rows = [r for r in r1["ladder_rows"] if r["beta"] == "beta_star"]
    Ls = np.array([r["L"] for r in rows]); d = np.array([r["delta_F"] for r in rows])
    t = T[lang]
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.4), constrained_layout=True)
    ax = axes[0]
    x = 1.0 / Ls
    ax.plot(x, d, "o", ms=5, color=C_MAIN, label=t["r1a"][3])
    xf = np.linspace(0, x.max()*1.05, 200)
    dinf = r1["delta_inf_beta_star"]
    ax.plot(xf, dinf*(1 - 0.35*np.where(xf > 0, xf, 1e-9) + 0.03*np.where(xf > 0, xf, 1e-9)**2),
            "-", color=C_ACC, lw=1.6, label=t["r1a"][4])
    ax.axhline(dinf, color=C_NEG, ls=":", lw=1.6, label=t["r1a"][5])
    ax.set_xlabel(t["r1a"][1]); ax.set_ylabel(t["r1a"][2])
    ax.set_title(t["r1a"][0], fontsize=11)
    ax.legend(fontsize=8.5, loc="lower right", framealpha=0.9)
    ax.grid(True)
    ax = axes[1]
    ceff = Ls * (1 - d / dinf)
    ax.plot(Ls, ceff, "o", ms=5, color=C_MAIN, label=t["r1b"][3])
    Lf = np.logspace(np.log10(4), np.log10(1e6), 200)
    ax.plot(Lf, 0.35 - 0.03/Lf, "-", color=C_ACC, lw=1.6, label=t["r1b"][4])
    ax.set_xscale("log")
    ax.set_xlabel(t["r1b"][1]); ax.set_ylabel(t["r1b"][2])
    ax.set_title(t["r1b"][0], fontsize=11)
    ax.legend(fontsize=9, loc="lower right")
    ax.grid(True)
    save(fig, f"r1_continuum_{lang}")

def fig_r2(lang):
    r2 = R["r2_anisotropic"]
    t = T[lang]
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.4), constrained_layout=True)
    ax = axes[0]
    fr = r2["freq_rows"]
    g = np.array([f["gamma"] for f in fr if len(f["freqs"]) == 2])
    lo = np.array([min(f["freqs"]) for f in fr if len(f["freqs"]) == 2])
    hi = np.array([max(f["freqs"]) for f in fr if len(f["freqs"]) == 2])
    gg = np.linspace(0.2, 5.0, 300)
    ax.plot(gg, (2+gg)/(2*np.pi), "-", color=C_ACC, lw=2.0, label=t["r2a"][3])
    ax.plot(gg, np.sqrt(3*(1+2*gg))/(2*np.pi), "-", color=C_NEG, lw=2.0, label=t["r2a"][4])
    ax.plot(g, hi, "o", ms=3.5, color=C_MUT, label=t["r2a"][5])
    ax.plot(g, lo, "o", ms=3.5, color=C_MUT)
    ax.axvline(1.0, color="k", ls=":", lw=1.2)
    ax.plot([1.0], [3/(2*np.pi)], "*", ms=14, color=C_MAIN, label=t["r2a"][6])
    ax.set_xlabel(t["r2a"][1]); ax.set_ylabel(t["r2a"][2])
    ax.set_title(t["r2a"][0], fontsize=11)
    ax.legend(fontsize=8.5, loc="lower right", framealpha=0.9)
    ax.grid(True)
    ax = axes[1]
    sc = r2["scan_same_sign"]; mx = r2["mixed_sign_scan"]
    gs = np.array([s["gamma"] for s in sc]); re = np.array([max(s["max_Re"], 1e-18) for s in sc])
    gm = np.array([s["gamma"] for s in mx]); rem = np.array([max(s["max_Re"], 1e-18) for s in mx])
    ax.semilogy(gs, np.maximum(re, 1e-12), "o", ms=4, color=C_MAIN, label=t["r2b"][3])
    ax.semilogy(gm, np.maximum(rem, 1e-12), "s", ms=4, color=C_NEG, label=t["r2b"][4])
    ax.axvline(0.5, color=C_OK, ls="--", lw=1.6, label=t["r2b"][5])
    ax.axhline(1e-12, color="k", ls=":", lw=1.0, label=t["r2b"][6])
    ax.set_ylim(1e-13, 1e2)
    ax.set_xlabel(t["r2b"][1]); ax.set_ylabel(t["r2b"][2])
    ax.set_title(t["r2b"][0], fontsize=11)
    ax.legend(fontsize=8.5, loc="upper right", framealpha=0.9)
    ax.grid(True)
    save(fig, f"r2_splitting_{lang}")

def fig_r3(lang):
    r3 = R["r3_thermal"]
    t = T[lang]
    fig, ax = plt.subplots(figsize=(9.6, 5.2), constrained_layout=True)
    nu, B0 = r3["nu_attempt"], r3["B0"]
    Tg = np.logspace(np.log10(1e-4), np.log10(r3["Tc_bridge"]*1.2), 300)
    cols = [C_ACC, C_MAIN, C_MUT]
    for i, b in enumerate(r3["budgets"]):
        N = b["N_attempts"]
        L = math.log(N * nu / 1e-12)
        eta = np.maximum(0.0, (B0 - Tg * L) / 2)
        ax.plot(Tg, eta, "-", lw=1.9, color=cols[i], label=t["r3"][3+i])
        ax.axvline(b["T_death"], color=cols[i], ls=":", lw=1.0)
    etas = np.linspace(0, 0.11, 200)
    # зона выживания при N=1e12
    L12 = math.log(1e12 * nu / 1e-12)
    ax.fill_between(Tg, np.maximum(0, (B0 - Tg*L12)/2), 0.11,
                    color=C_MAIN, alpha=0.06)
    ax.axhline(6.1e-10, color=C_NEG, lw=1.6, ls="--")
    ax.plot([6.1e-10], [6.1e-10], "o", ms=6, color=C_NEG)
    ax.annotate(t["r3"][6], xy=(2e-4, 6.1e-10), fontsize=9, color=C_NEG,
                xytext=(1.3e-4, 6e-3),
                arrowprops=dict(arrowstyle="->", color=C_NEG, lw=1.0))
    ax.axvline(r3["Tc_bridge"], color="k", ls="--", lw=1.4)
    ax.annotate(t["r3"][7], xy=(r3["Tc_bridge"], 0.09),
                fontsize=9, rotation=90, va="top", ha="right")
    ax.text(3.0e-4, 0.012, t["r3"][8], fontsize=9.5, color=C_MAIN, rotation=6)
    ax.set_xscale("log")
    ax.set_xlim(1e-4, r3["Tc_bridge"]*1.2); ax.set_ylim(0, 0.11)
    ax.set_xlabel(t["r3"][1]); ax.set_ylabel(t["r3"][2])
    ax.set_title(t["r3"][0], fontsize=11)
    ax.legend(fontsize=9, loc="upper right", framealpha=0.9)
    ax.grid(True)
    save(fig, f"r3_thermal_{lang}")

def fig_r4(lang):
    r4 = R["r4_resolution"]
    t = T[lang]
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.4), constrained_layout=True)
    sc = r4["scan_f"]
    f = np.array([s["f"] for s in sc])
    eT = np.array([s["rel_err_T0"] for s in sc])
    eE = np.array([s["rel_err_E0"] for s in sc])
    ax = axes[0]
    ax.semilogy(f, np.maximum(eT, 1e-4), "o-", ms=5, color=C_MAIN, label=t["r4a"][3])
    ax.semilogy(f, np.maximum(eE, 1e-4), "s-", ms=5, color=C_ACC, label=t["r4a"][4])
    ax.axhline(0.10, color=C_NEG, ls="--", lw=1.5, label=t["r4a"][5])
    ax.axvline(r4["f_crit_shape"], color=C_OK, ls=":", lw=1.8, label=t["r4a"][6])
    ax.invert_xaxis()
    ax.set_xlabel(t["r4a"][1]); ax.set_ylabel(t["r4a"][2])
    ax.set_title(t["r4a"][0], fontsize=11)
    ax.legend(fontsize=8.5, framealpha=0.9)
    ax.grid(True)
    ax = axes[1]
    T0f = np.array([s["fit2"][2] for s in sc])
    E0f = np.array([s["fit2"][3] for s in sc])
    ax.plot(f, T0f*1e3, "o-", ms=5, color=C_MAIN, label=t["r4b"][3])
    ax.plot(f, E0f, "s-", ms=5, color=C_ACC, label=t["r4b"][4])
    ax.axhline(4.3, color=C_NEG, ls="--", lw=1.3, label=t["r4b"][5])
    ax.axhline(1.8, color=C_OK, ls="--", lw=1.3, label=t["r4b"][6])
    ax.invert_xaxis()
    ax.set_xlabel(t["r4b"][1]); ax.set_ylabel(t["r4b"][2])
    ax.set_title(t["r4b"][0], fontsize=11)
    ax.legend(fontsize=8.5, loc="center right", framealpha=0.9)
    ax.grid(True)
    save(fig, f"r4_resolution_{lang}")

if __name__ == "__main__":
    for lang in ("ru", "en"):
        fig_r1(lang); fig_r2(lang); fig_r3(lang); fig_r4(lang)
    print("done")
