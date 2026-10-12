#!/usr/bin/env python3
"""QHB v2.2.0 — фигуры глав 15–17 (RU/EN): ветви+расщепление, космо-сценарий, лестницы."""
import json
import math

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.font_manager as fm

for fp in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
    try:
        fm.fontManager.addfont(fp)
    except Exception:
        pass
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["axes.edgecolor"] = "#666666"
plt.rcParams["axes.labelcolor"] = "#171715"
plt.rcParams["xtick.color"] = "#444444"
plt.rcParams["ytick.color"] = "#444444"

WORK = "/home/z/my-project/qhb_work"
OUT = f"{WORK}/vfigs"
import os

os.makedirs(OUT, exist_ok=True)

T19 = json.load(open(f"{WORK}/v220_t19.json"))
COS = json.load(open(f"{WORK}/v220_cosmo.json"))
LAD = json.load(open(f"{WORK}/v220_ladders.json"))

C1, C2, C3, CMUT = "#8c7225", "#3f93b0", "#9c3b2e", "#7a7871"

TXT = {
 "ru": dict(
   v1a_t="Законы ветвей: точные кривые и численный спектр",
   v1a_x=r"$\gamma$ (циркуляция $\Gamma_3$)", v1a_y=r"$\nu$ (рад/ед. времени)",
   leg_tr=r"$\nu_{tr}=(2+\gamma)/2\pi$ (точно)", leg_int=r"$\nu_{int}=\sqrt{3(1+2\gamma)}/2\pi$ (точно)",
   leg_meas="измеренные пары (решатель)", leg_star="вырождение $T11$: $\\gamma=1$",
   v1b_t="Тождество расщепления и порог Синге",
   v1b_y=r"$\nu^2$ (рад$^2$/ед.$^2$)",
   leg_split=r"$(\nu_{tr}^2-\nu_{int}^2)\cdot 4\pi^2 = (\gamma-1)^2$ — тождество",
   leg_synge_pos=r"$\nu_{int}^2 \cdot 4\pi^2/3 = 1+2\gamma$ (одноимённые)",
   leg_synge_neg=r"$= 1-2\gamma$ (встречные: неустойчивость при $\gamma>0.5$)",
   leg_meas2="измеренный квадрат расщепления",
   v2a_t="Гонка остывания: сектор против дедлайна",
   v2a_x=r"$t/t_c$", v2a_y=r"$T_{gap}/T_c$",
   leg_a12=r"$\alpha=1/2$ (радиационное остывание)", leg_a1=r"$\alpha=1$",
   leg_tdeath=r"$T_{death}(10^{12})=T_c/25.9$", leg_tc=r"$T_c$",
   ann_deadline=r"дедлайн $t_{death}/t_c = 25.9^{1/\alpha}$",
   v2b_t="Скала остановки и горячее доминирование бюджета",
   v2b_x=r"$T_{floor}/T_{death}$", v2b_y=r"$\tau_{max}$ (ед. времени)",
   leg_tau=r"$\tau_{max}=\varepsilon_H e^{B/T}/\nu$",
   leg_dens=r"плотность бюджета $\propto T^{-3}e^{-B/T}$ (норм.)",
   ann_star=r"пик $T^*=B/3$",
   v3_t="Пять лестниц сходимости в бесконечность",
   p_t=("L-A время", "L-B шаг RK4", "L-C объём (Ричардсон)", "L-D бюджет попыток",
        "L-E выборка (бином)", "измеренные порядки"),
   LA_x=r"$T_{int}$ (периодов вращения)", LA_y=r"$|\hat\nu-\nu_{exact}|$",
   LA_leg_i=r"ветвь $\nu_{int}$", LA_leg_tr=r"ветвь $\nu_{tr}$",
   LA_leg_res=r"разрешение $1/T$", LA_ann=r"ветви разрешимы при $T>1/\Delta\nu\approx 865$",
   LB_x=r"$h/P_{rot}$", LB_y=r"$|\hat\omega-\omega_{exact}|$",
   LB_leg1=r"$\gamma=1$", LB_leg2=r"$\gamma=0.8$", LB_leg_ref=r"наклон 4",
   LB_ann=r"Ричардсон: dev $\approx 2.5\times10^{-11}$",
   LC_x=r"ступени $(L_1,L_2,L_3)$", LC_y=r"$|\Delta_\infty^{extrap}-\Delta_{F,min}|$",
   LC_ann=r"континуум уже в первых трёх ступенях",
   LD_x=r"$\log_{10} N$", LD_y=r"$T_{death}(N)$",
   LD_leg=r"$B_0/\ln(N\nu/\varepsilon_H)$", LD_leg_ref=r"$\propto 1/\ln N$",
   LD_ann=r"$T_{death}(\infty)=0$",
   LE_x=r"$n$ (выборка)", LE_y=r"$|\hat p-p|$",
   LE_leg_ref=r"$\propto n^{-1/2}$", LE_leg_se=r"$1\sigma$ Пуассона",
   LE_ann=r"все $|z|\leq 1.2$",
   LS_y=r"порядок $p$", LS_ann=("L-A: ~1–2 (интерполяция пика)", "L-B: 4.096",
        "L-C: точный 2-член", r"L-D: $1/\ln N$", "L-E: 0.5"),
 ),
 "en": dict(
   v1a_t="Branch laws: exact curves vs numerical spectrum",
   v1a_x=r"$\gamma$ (circulation $\Gamma_3$)", v1a_y=r"$\nu$ (rad/time unit)",
   leg_tr=r"$\nu_{tr}=(2+\gamma)/2\pi$ (exact)", leg_int=r"$\nu_{int}=\sqrt{3(1+2\gamma)}/2\pi$ (exact)",
   leg_meas="measured pairs (solver)", leg_star="$T11$ degeneracy: $\\gamma=1$",
   v1b_t="Splitting identity and the Synge threshold",
   v1b_y=r"$\nu^2$ (rad$^2$/unit$^2$)",
   leg_split=r"$(\nu_{tr}^2-\nu_{int}^2)\cdot 4\pi^2 = (\gamma-1)^2$ — identity",
   leg_synge_pos=r"$\nu_{int}^2 \cdot 4\pi^2/3 = 1+2\gamma$ (same-sign)",
   leg_synge_neg=r"$= 1-2\gamma$ (opposite: unstable for $\gamma>0.5$)",
   leg_meas2="measured squared splitting",
   v2a_t="The cooling race: sector vs the deadline",
   v2a_x=r"$t/t_c$", v2a_y=r"$T_{gap}/T_c$",
   leg_a12=r"$\alpha=1/2$ (radiation-like cooling)", leg_a1=r"$\alpha=1$",
   leg_tdeath=r"$T_{death}(10^{12})=T_c/25.9$", leg_tc=r"$T_c$",
   ann_deadline=r"deadline $t_{death}/t_c = 25.9^{1/\alpha}$",
   v2b_t="Stall cliff and the hot dominance of the budget",
   v2b_x=r"$T_{floor}/T_{death}$", v2b_y=r"$\tau_{max}$ (time units)",
   leg_tau=r"$\tau_{max}=\varepsilon_H e^{B/T}/\nu$",
   leg_dens=r"budget density $\propto T^{-3}e^{-B/T}$ (norm.)",
   ann_star=r"peak $T^*=B/3$",
   v3_t="Five convergence ladders to infinity",
   p_t=("L-A time", "L-B RK4 step", "L-C volume (Richardson)", "L-D attempt budget",
        "L-E sample (binomial)", "measured orders"),
   LA_x=r"$T_{int}$ (rotation periods)", LA_y=r"$|\hat\nu-\nu_{exact}|$",
   LA_leg_i=r"branch $\nu_{int}$", LA_leg_tr=r"branch $\nu_{tr}$",
   LA_leg_res=r"resolution $1/T$", LA_ann=r"branches resolved for $T>1/\Delta\nu\approx 865$",
   LB_x=r"$h/P_{rot}$", LB_y=r"$|\hat\omega-\omega_{exact}|$",
   LB_leg1=r"$\gamma=1$", LB_leg2=r"$\gamma=0.8$", LB_leg_ref=r"slope 4",
   LB_ann=r"Richardson: dev $\approx 2.5\times10^{-11}$",
   LC_x=r"rungs $(L_1,L_2,L_3)$", LC_y=r"$|\Delta_\infty^{extrap}-\Delta_{F,min}|$",
   LC_ann=r"the continuum is already in the first three rungs",
   LD_x=r"$\log_{10} N$", LD_y=r"$T_{death}(N)$",
   LD_leg=r"$B_0/\ln(N\nu/\varepsilon_H)$", LD_leg_ref=r"$\propto 1/\ln N$",
   LD_ann=r"$T_{death}(\infty)=0$",
   LE_x=r"$n$ (sample)", LE_y=r"$|\hat p-p|$",
   LE_leg_ref=r"$\propto n^{-1/2}$", LE_leg_se=r"$1\sigma$ Poisson",
   LE_ann=r"all $|z|\leq 1.2$",
   LS_y=r"order $p$", LS_ann=("L-A: ~1–2 (peak interpolation)", "L-B: 4.096",
        "L-C: exact 2-term law", r"L-D: $1/\ln N$", "L-E: 0.5"),
 ),
}

# ============================ Фигура V1: ветви ==============================
def fig_v1(L):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 4.7), constrained_layout=True)
    g = np.linspace(0.15, 5.0, 400)
    nu_tr = (2 + g) / (2 * np.pi)
    nu_int = np.sqrt(3 * (1 + 2 * g)) / (2 * np.pi)
    ax1.plot(g, nu_tr, color=C1, lw=2.2, label=TXT[L]["leg_tr"])
    ax1.plot(g, nu_int, color=C2, lw=2.2, label=TXT[L]["leg_int"])
    rows = T19["rk4_crosscheck_numeric_solver"]["rows"]
    mg, m1, m0 = [], [], []
    for r in rows:
        pr = r["measured_pairs"]
        if len(pr) == 2:
            mg.append(r["gamma"]); m1.append(pr[1]); m0.append(pr[0])
        elif len(pr) == 1:                     # вырождение в канон T11
            mg.append(r["gamma"]); m1.append(pr[0]); m0.append(pr[0])
    ax1.plot(mg, m1, "o", ms=6.5, mfc="white", mec=C3, mew=1.6, label=TXT[L]["leg_meas"])
    ax1.plot(mg, m0, "o", ms=6.5, mfc="white", mec=C3, mew=1.6)
    ax1.plot([1], [3 / (2 * np.pi)], "*", ms=17, color=C3, label=TXT[L]["leg_star"], zorder=5)
    ax1.set_xlabel(TXT[L]["v1a_x"]); ax1.set_ylabel(TXT[L]["v1a_y"])
    ax1.set_title(TXT[L]["v1a_t"], fontsize=11.5)
    ax1.legend(fontsize=8.6, frameon=False, loc="lower right")
    ax1.grid(alpha=0.25, lw=0.5)
    # панель b: тождество расщепления + Синге
    gg = np.linspace(0.15, 5.0, 400)
    split_exact = (gg - 1) ** 2
    nu2_same = 3 * (1 + 2 * gg)
    nu2_mix = 3 * (1 - 2 * gg)
    ax2.plot(gg, split_exact, color=C3, lw=2.2, label=TXT[L]["leg_split"])
    ax2.plot(gg, nu2_same, color=C2, lw=2.0, label=TXT[L]["leg_synge_pos"])
    ax2.plot(gg, nu2_mix, color=C1, lw=2.0, ls="--", label=TXT[L]["leg_synge_neg"])
    ax2.axvline(0.5, color=C1, lw=1.1, ls=":")
    ax2.axhline(0, color="#555555", lw=0.8)
    ax2.fill_between(gg, -6, 0, where=(gg > 0.5), color=C1, alpha=0.10)
    # измеренный квадрат расщепления
    if msplit := [(r["gamma"], (r["measured_pairs"][1] ** 2 - r["measured_pairs"][0] ** 2) * 4 * math.pi ** 2)
                  for r in rows if len(r["measured_pairs"]) == 2 and r["gamma"] > 0.2]:
        ax2.plot([m[0] for m in msplit], [m[1] for m in msplit], "s", ms=5.5,
                 mfc="white", mec=C3, mew=1.4, label=TXT[L]["leg_meas2"])
    ax2.set_ylim(-6, 34)
    ax2.set_xlabel(TXT[L]["v1a_x"]); ax2.set_ylabel(TXT[L]["v1b_y"])
    ax2.set_title(TXT[L]["v1b_t"], fontsize=11.5)
    ax2.legend(fontsize=8.2, frameon=False, loc="upper left")
    ax2.grid(alpha=0.25, lw=0.5)
    fig.savefig(f"{OUT}/v1_branches_{L}.png", dpi=145)
    plt.close(fig)

# ============================ Фигура V2: космо ==============================
def fig_v2(L):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 4.7), constrained_layout=True)
    TD = 1 / 25.939173
    t = np.logspace(-2, 3.4, 500)
    T_half = np.where(t ** -0.5 <= 2.4, t ** -0.5, np.nan)
    T_1 = np.where(t ** -1.0 <= 2.4, t ** -1.0, np.nan)
    ax1.plot(t, T_half, color=C1, lw=2.2, label=TXT[L]["leg_a12"])
    ax1.plot(t, T_1, color=C2, lw=2.0, ls="--", label=TXT[L]["leg_a1"])
    ax1.axhline(TD, color=C3, lw=1.6, ls="-.", label=TXT[L]["leg_tdeath"])
    ax1.axhline(1.0, color="#555555", lw=0.9, ls=":", label=TXT[L]["leg_tc"])
    ax1.axvline(TD ** 2, color=C3, lw=1.0, ls=":")
    ax1.axvline(TD, color=C2, lw=1.0, ls=":")
    ax1.annotate(TXT[L]["ann_deadline"] + "\n" + r"$\alpha$=1/2: 673",
                 xy=(TD ** 2, TD), xytext=(3, 0.028), fontsize=8.8, color=C3,
                 arrowprops=dict(arrowstyle="->", color=C3, lw=1.0))
    ax1.axvspan(1.0, TD ** 2, color=C1, alpha=0.07)
    ax1.set_xscale("log"); ax1.set_yscale("log")
    ax1.set_xlabel(TXT[L]["v2a_x"]); ax1.set_ylabel(TXT[L]["v2a_y"])
    ax1.set_title(TXT[L]["v2a_t"], fontsize=11.5)
    ax1.legend(fontsize=8.6, frameon=False, loc="upper right")
    ax1.set_ylim(0.018, 2.4)
    ax1.grid(alpha=0.25, lw=0.5, which="both")
    # панель b: скала + плотность
    rows = COS["P_C4_stall_cliff"]["rows"]
    x = np.array([r["T_floor_over_Tdeath"] for r in rows], dtype=float)
    y = []
    for r in rows:
        try:
            y.append(float(r["tau_max"]))
        except Exception:
            y.append(np.nan)
    ax2.plot(x, y, "o-", color=C3, lw=2.0, ms=6, label=TXT[L]["leg_tau"])
    ax2.set_xscale("log"); ax2.set_yscale("log")
    ax2.set_xlabel(TXT[L]["v2b_x"]); ax2.set_ylabel(TXT[L]["v2b_y"])
    ax2b = ax2.twinx()
    B0 = 0.181777
    tt = np.logspace(math.log10(0.003414), math.log10(0.09), 300)
    dens = tt ** -3 * np.exp(-B0 / tt)
    dens /= dens.max()
    ax2b.plot(tt / 0.003414, dens, color=C2, lw=1.8, ls="--", label=TXT[L]["leg_dens"])
    ax2b.set_yscale("log"); ax2b.set_ylim(1e-9, 3)
    ax2b.set_ylabel(TXT[L]["leg_dens"], color=C2, fontsize=9.5)
    ax2b.tick_params(axis="y", labelcolor=C2)
    ax2b.axvline((B0 / 3) / 0.003414, color=C2, lw=0.9, ls=":")
    ax2b.annotate(TXT[L]["ann_star"], xy=((B0 / 3) / 0.003414, 1.0),
                  xytext=(11, 0.55), fontsize=8.8, color=C2,
                  arrowprops=dict(arrowstyle="->", color=C2, lw=0.9))
    lines1, labs1 = ax2.get_legend_handles_labels()
    lines2, labs2 = ax2b.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labs1 + labs2, fontsize=8.4, frameon=False, loc="lower left")
    ax2.set_title(TXT[L]["v2b_t"], fontsize=11.5)
    ax2.grid(alpha=0.25, lw=0.5, which="both")
    fig.savefig(f"{OUT}/v2_cosmo_{L}.png", dpi=145)
    plt.close(fig)

# ============================ Фигура V3: лестницы ===========================
def fig_v3(L):
    fig, axs = plt.subplots(2, 3, figsize=(13.2, 7.0), constrained_layout=True)
    (aLA, aLB, aLC), (aLD, aLE, aLS) = axs
    # --- L-A
    rows = LAD["L_A_time_ladder"]["rows"]
    Tr = [r["T_rot"] for r in rows]
    ei = [max(r["err_int"], 1e-16) for r in rows]
    et = [max(r["err_tr"], 1e-16) if r["T_rot"] >= 1024 else np.nan for r in rows]
    res = [r["fourier_res"] for r in rows]
    aLA.loglog(Tr, ei, "o-", color=C1, lw=1.9, ms=5.5, label=TXT[L]["LA_leg_i"])
    aLA.loglog(Tr, et, "s-", color=C2, lw=1.9, ms=5.5, label=TXT[L]["LA_leg_tr"])
    aLA.loglog(Tr, res, ":", color=CMUT, lw=1.4, label=TXT[L]["LA_leg_res"])
    aLA.axvline(LAD["L_A_time_ladder"]["T_needed_to_resolve"], color=C3, lw=1.0, ls=":")
    aLA.set_xlabel(TXT[L]["LA_x"]); aLA.set_ylabel(TXT[L]["LA_y"])
    aLA.set_title(TXT[L]["p_t"][0], fontsize=11)
    aLA.legend(fontsize=8, frameon=False)
    aLA.annotate(TXT[L]["LA_ann"], xy=(865, 3e-4), fontsize=7.8, color=C3)
    aLA.grid(alpha=0.25, lw=0.5, which="both")
    # --- L-B
    for row, cc, mk, lb in ((LAD["L_B_step_ladder"]["rows"][0], C1, "o", TXT[L]["LB_leg1"]),
                            (LAD["L_B_step_ladder"]["rows"][1], C2, "s", TXT[L]["LB_leg2"])):
        hh = [r["dt_over_P"] for r in row["rows"]]
        ee = [max(r["err"], 1e-17) for r in row["rows"]]
        aLB.loglog(hh, ee, marker=mk, color=cc, lw=1.9, ms=5.5, label=lb)
    href = np.array([1 / 16, 1 / 512])
    aLB.loglog(href, href ** 4 * 2.5e4, ":", color=CMUT, lw=1.4, label=TXT[L]["LB_leg_ref"])
    for row, cc in ((LAD["L_B_step_ladder"]["rows"][0], C1), (LAD["L_B_step_ladder"]["rows"][1], C2)):
        aLB.loglog([row["rows"][-1]["dt_over_P"]], [max(row["richardson_dev"], 1e-17)],
                   "*", ms=14, color=cc, zorder=5)
    aLB.set_xlabel(TXT[L]["LB_x"]); aLB.set_ylabel(TXT[L]["LB_y"])
    aLB.set_title(TXT[L]["p_t"][1], fontsize=11)
    aLB.legend(fontsize=8, frameon=False, loc="lower right")
    aLB.annotate(TXT[L]["LB_ann"], xy=(1 / 128, 5e-12), fontsize=7.8, color=C3)
    aLB.grid(alpha=0.25, lw=0.5, which="both")
    # --- L-C
    rows = LAD["L_C_volume_ladder"]["rows"]
    xr = np.arange(len(rows))
    yy = [max(r["dev_from_true"], 5e-18) for r in rows]
    aLC.bar(xr, yy, color=C1, alpha=0.85, width=0.55)
    aLC.set_yscale("log")
    aLC.set_ylim(2e-18, 3e-15)
    aLC.set_xticks(xr)
    aLC.set_xticklabels([f"{r['rungs'][0]},{r['rungs'][1]},{r['rungs'][2]}" for r in rows],
                        fontsize=7.0, rotation=25)
    aLC.set_xlabel(TXT[L]["LC_x"]); aLC.set_ylabel(TXT[L]["LC_y"])
    aLC.set_title(TXT[L]["p_t"][2], fontsize=11)
    aLC.annotate(TXT[L]["LC_ann"], xy=(0.03, 0.86), xycoords="axes fraction", fontsize=8.4, color=C3)
    aLC.grid(alpha=0.25, lw=0.5, which="both", axis="y")
    # --- L-D
    rows = LAD["L_D_budget_ladder"]["rows"]
    lx = [r["log10_N"] for r in rows]
    ly = [float(r["T_death"]) for r in rows]
    aLD.semilogy(lx, ly, "o-", color=C2, lw=1.9, ms=5.5, label=TXT[L]["LD_leg"])
    lx2 = np.array(lx, dtype=float)
    aLD.semilogy(lx2, ly[0] * math.log(1e6 * 0.133159 / 1e-12) / np.log(10 ** lx2 * 0.133159 / 1e-12),
                 ":", color=CMUT, lw=1.4, label=TXT[L]["LD_leg_ref"])
    aLD.set_xlabel(TXT[L]["LD_x"]); aLD.set_ylabel(TXT[L]["LD_y"])
    aLD.set_title(TXT[L]["p_t"][3], fontsize=11)
    aLD.legend(fontsize=8, frameon=False)
    aLD.annotate(TXT[L]["LD_ann"], xy=(30, 0.0016), fontsize=8.4, color=C3)
    aLD.grid(alpha=0.25, lw=0.5, which="both")
    # --- L-E
    rows = LAD["L_E_sample_ladder"]["rows"]
    nn = [r["n"] for r in rows]
    ee = [max(r["err"], 1e-8) for r in rows]
    se = [r["binom_se"] for r in rows]
    aLE.loglog(nn, ee, "o-", color=C1, lw=1.9, ms=5.5, label=TXT[L]["LE_ann"] if False else None)
    aLE.loglog(nn, ee, "o-", color=C1, lw=1.9, ms=5.5)
    aLE.loglog(nn, se, "--", color=CMUT, lw=1.4, label=TXT[L]["LE_leg_se"])
    nref = np.array([1e3, 1e7])
    aLE.loglog(nref, 1.63e-2 * (nref / 1e3) ** -0.5, ":", color=C3, lw=1.4, label=TXT[L]["LE_leg_ref"])
    aLE.set_xlabel(TXT[L]["LE_x"]); aLE.set_ylabel(TXT[L]["LE_y"])
    aLE.set_title(TXT[L]["p_t"][4], fontsize=11)
    aLE.legend(fontsize=8, frameon=False, loc="lower left")
    aLE.annotate(TXT[L]["LE_ann"], xy=(2e5, 2.4e-2), fontsize=8.4, color=C3)
    aLE.grid(alpha=0.25, lw=0.5, which="both")
    # --- сводка порядков
    labels = ["L-A", "L-B", "L-C", "L-D", "L-E"]
    vals = [1.5, 4.096, 2.0, 0.35, 0.5]
    anns = TXT[L]["LS_ann"]
    bars = aLS.bar(labels, vals, color=[C1, C2, C3, CMUT, "#6d8a3f"], alpha=0.9, width=0.6)
    for b, a in zip(bars, anns):
        aLS.annotate(a, xy=(b.get_x() + b.get_width() / 2, b.get_height()),
                     xytext=(0, 4), textcoords="offset points",
                     ha="center", fontsize=7.6, rotation=0)
    aLS.set_ylim(0, 5.4)
    aLS.set_ylabel(TXT[L]["LS_y"])
    aLS.set_title(TXT[L]["p_t"][5], fontsize=11)
    aLS.grid(alpha=0.25, lw=0.5, axis="y")
    fig.suptitle(TXT[L]["v3_t"], fontsize=12.5, y=1.02)
    fig.savefig(f"{OUT}/v3_ladders_{L}.png", dpi=145, bbox_inches="tight")
    plt.close(fig)

for L in ("ru", "en"):
    fig_v1(L); fig_v2(L); fig_v3(L)
    print("figs done:", L)
print("saved to", OUT)
