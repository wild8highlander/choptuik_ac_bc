#!/usr/bin/env python3
"""
QHB Monolith — новые фигуры для главы 11 (RU + EN версии).
Стиль: согласован с пакетом (светлая тема, без верхних/правых осей, пунктирная сетка).
"""
import json
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

OUT = "/home/z/my-project/qhb_work/newfigs"
os.makedirs(OUT, exist_ok=True)
R = json.load(open("/home/z/my-project/qhb_work/extra_research_results.json"))

# Палитра (согласована с монографией: глубокий синий + акцент)
C_MAIN = "#1a4a7a"   # основной
C_ACC  = "#2d7ab3"   # акцент
C_NEG  = "#a05a3c"   # контрастный тёплый (негатив/порог)
C_MUT  = "#5a7a96"   # приглушённый

TEXTS = {
 "ru": {
  "valley": ("Закон долины зазора и фальсификаторы наивного окна",
             "β (безразмерная связность)", "Δ_F(β) = Δ_F,min + 0.35·(β − β*)²",
             "порог детектора", "наивный прогноз β_c", "второй экстраполятор"),
  "crossver": ("Кросс-версионная сверка v1.2.0 ↔ v1.3.0 (абсолютные отклонения)",
               "величина", "|отклонение|"),
  "digits": ("Цифровая устойчивость запаса замка margin = η_crit/η_B",
             "рабочая точность mpmath (dps)", "совпадающих ведущих цифр"),
  "etascan": ("Тонкий η-скан барьера замыкания: barrier(η) = B₀ − 2η",
              "η (амплитуда возмущения)", "барьер замыкания B(η)",
              "η_crit = 0.0908885", "η_B = 6.1×10⁻¹⁰ (Planck 2018)"),
  "drift": ("Дрейф зазора: Δ_cont − Δ_N = C·h² (независимый рефит лестницы)",
            "h² (шаг дискретизации, h = 8/(N+1))", "Δ_N (зазор, N = 32…512)",
            "OLS-интерцепт Δ_cont (не заявляется)", "пакетная оценка C (широкая пара)"),
  "binom": ("C5: закреплённый Монте-Карло 2433/10000 против аналитики p = 0.2433",
            "k (число бегств)", "плотность вероятности",
            "MC: 2433/10000", "аналитика: Binom(10⁴, 0.2433)", "95% интервал Уилсона"),
 },
 "en": {
  "valley": ("Gap valley law and naive-window falsifiers",
             "β (dimensionless coupling)", "Δ_F(β) = Δ_F,min + 0.35·(β − β*)²",
             "detector threshold", "naive forecast β_c", "second extrapolator"),
  "crossver": ("Cross-version audit v1.2.0 ↔ v1.3.0 (absolute deviations)",
               "quantity", "|deviation|"),
  "digits": ("Digit stability of the lock margin margin = η_crit/η_B",
             "mpmath working precision (dps)", "matching leading digits"),
  "etascan": ("Fine η-scan of the closure barrier: barrier(η) = B₀ − 2η",
              "η (perturbation amplitude)", "closure barrier B(η)",
              "η_crit = 0.0908885", "η_B = 6.1×10⁻¹⁰ (Planck 2018)"),
  "drift": ("Gap drift: Δ_cont − Δ_N = C·h² (independent ladder refit)",
            "h² (grid spacing, h = 8/(N+1))", "Δ_N (gap, N = 32…512)",
            "OLS intercept Δ_cont (not claimed)", "package C (wide pair)"),
  "binom": ("C5: pinned Monte Carlo 2433/10000 vs analytic p = 0.2433",
            "k (escape count)", "probability density",
            "MC: 2433/10000", "analytic: Binom(10⁴, 0.2433)", "95% Wilson interval"),
 },
}

def save(fig, name, lang):
    fig.savefig(f"{OUT}/{name}_{lang}.png", dpi=200, facecolor="white")
    plt.close(fig)
    print("saved", f"{OUT}/{name}_{lang}.png")

def build_all(lang):
    T = TEXTS[lang]
    beta_star, Dmin, K = 3.3583, 0.181777, 0.35

    # ---- F1: valley + falsifiers ----
    fig, ax = plt.subplots(figsize=(8.2, 4.8), constrained_layout=True)
    b = np.linspace(2.8, 4.55, 500)
    y = Dmin + K*(b - beta_star)**2
    ax.plot(b, y, color=C_MAIN, lw=2.2, label="Δ_F(β) = Δ_F,min + 0.35·(β − β*)²")
    thr = 0.03634845261904761
    ax.axhline(thr, color=C_NEG, lw=1.4, ls=":", label=f"{T['valley'][3]} = 0.0363485")
    bc = 2.9910
    ybc = Dmin + K*(bc-beta_star)**2
    ax.plot([bc], [ybc], "o", ms=8, mfc="white", mec=C_NEG, mew=1.8, zorder=5)
    ax.annotate(f"{T['valley'][4]} = 2.9910\nΔ_F = 0.228995 = 6.3×{T['valley'][3].split(' ')[0]}",
                xy=(bc, ybc), xytext=(2.86, 0.285), fontsize=9.5, color=C_NEG,
                arrowprops={"arrowstyle": "->", "color": C_NEG, "lw": 1.0})
    b2 = 2.9660810826496466
    yb2 = Dmin + K*(b2-beta_star)**2
    ax.plot([b2], [yb2], "s", ms=7, mfc="white", mec=C_ACC, mew=1.8, zorder=5)
    ax.annotate(f"{T['valley'][5]}\nΔ_F = 0.235619 = 6.48×порога" if lang=="ru" else f"{T['valley'][5]}\nΔ_F = 0.235619 = 6.48×threshold",
                xy=(b2, yb2), xytext=(3.0, 0.33), fontsize=9.5, color=C_ACC,
                arrowprops={"arrowstyle": "->", "color": C_ACC, "lw": 1.0})
    ax.plot([beta_star], [Dmin], "*", ms=14, color=C_MAIN, zorder=5)
    ax.annotate("β* = 3.3583, Δ_F,min = 0.181777", xy=(beta_star, Dmin),
                xytext=(3.55, 0.185), fontsize=9.5, color=C_MAIN)
    ax.set_xlabel(T["valley"][1]); ax.set_ylabel(T["valley"][2])
    ax.set_title(T["valley"][0], fontsize=12.5, fontweight="bold", loc="left")
    ax.legend(loc="upper right", frameon=False, fontsize=9.5)
    ax.grid(True, alpha=0.25)
    save(fig, "new_valley", lang)

    # ---- F2: cross-version deviations ----
    cv = R["cross_version"]
    names = {"ru": {"beta_star (дно долины C9)": "β* (дно долины)",
                    "Delta_F_min (минимум зазора)": "Δ_F,min",
                    "omega_exact (Лагранж)": "ω (Лагранж)",
                    "S_wkb_zero (ВКБ C7)": "S(0) (ВКБ)",
                    "T_wkb_zero": "T(0) (ВКБ)",
                    "V_star (статический барьер)": "V* (барьер)",
                    "r_max Арефа": "r_max (Ареф)",
                    "P_esc свободного трио": "P_esc (трио)",
                    "доля A %": "доля A %", "доля B %": "доля B %", "доля C %": "доля C %",
                    "eta_crit": "η_crit", "порог детектора": "порог детектора"},
             "en": {}}
    nm = names[lang]
    labels, devs = [], []
    for c in cv:
        lbl = nm.get(c["quantity"], c["quantity"]) if lang == "ru" else c["quantity"].split(" (")[0]
        labels.append(lbl)
        devs.append(max(float(c["abs_dev"]), 1e-18))
    order = np.argsort(devs)[::-1]
    labels = [labels[i] for i in order]; devs = [devs[i] for i in order]
    fig, ax = plt.subplots(figsize=(8.2, 4.6), constrained_layout=True)
    xpos = np.arange(len(labels))
    ax.bar(xpos, devs, color=[C_ACC if d < 1e-9 else C_NEG for d in devs], width=0.62)
    ax.set_yscale("log")
    ax.set_xticks(xpos)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8.5)
    ax.set_ylabel(T["crossver"][2])
    ax.set_title(T["crossver"][0], fontsize=12.5, fontweight="bold", loc="left")
    ax.grid(True, axis="y", alpha=0.25)
    ax.axhline(1e-11, color=C_MUT, lw=1.0, ls="--")
    ax.text(len(labels)-0.4, 2.2e-11, "fp64-шум ≈ 10⁻¹¹", fontsize=9, color=C_MUT, ha="right")
    save(fig, "new_crossver", lang)

    # ---- F3: digit stability ----
    match = [30, 51, 100]  # 30(dps30->50), 51(50->100), 100(100->150)
    fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    ax.plot([1, 2, 3], match, "o-", color=C_MAIN, lw=2.0, ms=7)
    for i, m in enumerate(match):
        ax.annotate(str(m), (i+1, m), textcoords="offset points", xytext=(8, 4), fontsize=10, color=C_MAIN)
    ax.plot([1, 3], [30, 100], "--", color=C_MUT, lw=1.0)
    ax.set_xticks([1, 2, 3]); ax.set_xticklabels(["30 → 50", "50 → 100", "100 → 150"])
    ax.set_xlabel(T["digits"][0]); ax.set_ylabel(T["digits"][1])
    ax.set_title(T["digits"][0], fontsize=12.5, fontweight="bold", loc="left")
    ax.grid(True, alpha=0.25)
    save(fig, "new_digits", lang)

    # ---- F4: eta fine scan ----
    fig, ax = plt.subplots(figsize=(8.2, 4.6), constrained_layout=True)
    eta = np.linspace(0, 0.18, 2001)
    bar = 0.181777 - 2.0*eta
    ax.plot(eta, bar, color=C_MAIN, lw=2.2)
    ax.axhline(0, color=C_NEG, lw=1.2, ls=":")
    ax.axvline(0.0908885, color=C_ACC, lw=1.4, ls="--")
    ax.annotate(T["etascan"][3], xy=(0.0908885, 0.0), xytext=(0.096, 0.028),
                fontsize=10, color=C_ACC, arrowprops={"arrowstyle": "->", "color": C_ACC})
    ax.annotate(T["etascan"][4], xy=(6.1e-10, 0.181777), xytext=(0.012, 0.16),
                fontsize=10, color=C_NEG, arrowprops={"arrowstyle": "->", "color": C_NEG})
    ax.fill_between(eta, bar, -0.02, where=(bar <= 0), color=C_NEG, alpha=0.12)
    ax.set_xlim(0, 0.18); ax.set_ylim(-0.02, 0.19)
    ax.set_xlabel(T["etascan"][1]); ax.set_ylabel(T["etascan"][2])
    ax.set_title(T["etascan"][0], fontsize=12.5, fontweight="bold", loc="left")
    ax.grid(True, alpha=0.25)
    save(fig, "new_etascan", lang)

    # ---- F5: drift ladder ----
    ladder = [(32, 0.521692147813), (64, 0.523004556028), (128, 0.523344719799),
              (256, 0.523431317627), (512, 0.523453164838)]
    hs = np.array([8.0/(n+1) for n, _ in ladder])
    ys = np.array([d for _, d in ladder])
    Cw = 0.03008931566777479; Dc = 0.5237317900626313
    fig, ax = plt.subplots(figsize=(8.2, 4.6), constrained_layout=True)
    xx = hs**2
    ax.plot(xx, ys, "o", ms=8, color=C_MAIN, zorder5=None, zorder=5) if False else ax.plot(xx, ys, "o", ms=8, color=C_MAIN, zorder=5)
    hl = np.linspace(0, xx.max()*1.08, 100)
    ax.plot(hl, Dc - Cw*hl, "-", color=C_ACC, lw=2.0, label=f"{T['drift'][4]}: C = 0.0300893")
    ax.axhline(Dc, color=C_MUT, lw=1.2, ls="--", label=f"{T['drift'][3]} ≈ 0.52373")
    for n, x, y in zip([l[0] for l in ladder], xx, ys):
        ax.annotate(f"N={n}", (x, y), textcoords="offset points", xytext=(6, -12), fontsize=8.5, color=C_MUT)
    ax.set_xlabel(T["drift"][1]); ax.set_ylabel(T["drift"][2])
    ax.set_title(T["drift"][0], fontsize=12.5, fontweight="bold", loc="left")
    ax.legend(loc="lower left", frameon=False, fontsize=9.5)
    ax.grid(True, alpha=0.25)
    save(fig, "new_drift", lang)

    # ---- F6: C5 binomial ----
    from scipy.stats import binom
    n_mc, p0 = 10000, 0.2433
    ks = np.arange(2160, 2720)
    pmf = binom.pmf(ks, n_mc, p0)
    fig, ax = plt.subplots(figsize=(8.2, 4.6), constrained_layout=True)
    ax.plot(ks, pmf, color=C_ACC, lw=1.8, label=T["binom"][4])
    ax.axvline(2433, color=C_MAIN, lw=1.6, ls="--", label=T["binom"][3])
    wil = R["new_sensitive_tests"]["c5_binomial_sensitivity"]["wilson95"]
    ax.axvspan(wil[0]*n_mc, wil[1]*n_mc, color=C_ACC, alpha=0.10, label=T["binom"][5])
    ax.set_xlabel(T["binom"][1]); ax.set_ylabel(T["binom"][2])
    ax.set_title(T["binom"][0], fontsize=12.5, fontweight="bold", loc="left")
    ax.legend(loc="upper right", frameon=False, fontsize=9.5)
    ax.grid(True, alpha=0.25)
    save(fig, "new_binom", lang)

build_all("ru")
build_all("en")
print("ALL NEW FIGURES DONE")
