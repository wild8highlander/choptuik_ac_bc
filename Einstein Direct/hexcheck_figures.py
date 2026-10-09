#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Рисунки гексчек-кампании (RU/EN, 300 dpi): tau-книга + часы; W2-пол + live-башня."""
import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(BASE, "results")
FIG_RU = os.path.join(BASE, "figures", "fig_ru")
FIG_EN = os.path.join(BASE, "figures", "fig_en")
os.makedirs(FIG_RU, exist_ok=True)
os.makedirs(FIG_EN, exist_ok=True)

D = json.load(open(os.path.join(RES, "grid_machine_hexcheck.json"), encoding="utf-8"))
DELTA_SP = 7.0 * math.pi / 30.0
KAPPA_CYC = math.log(64.0 / 9.0)
DELTA_CYC = 6.0 * math.log(16.0 / 9.0)

C_LEG = "#2b6cb0"; C_B = "#c05621"; C_A = "#2f855a"; C_FLOOR = "#a0aec0"
C_LIVE = "#c53030"; C_STAB = "#2b6cb0"; C_TGT = "#276749"

L = {
 "ru": {
  "t1": "Гексчек: tau-книга (свежие фиты) и часы near-critical цепочек",
  "a": "ln tau_fresh vs z_fine (глубокое окно)",
  "b": "часы: z_fine vs z_cont_fresh",
  "tau_f": "модель B: Delta = %.2f (%+.1f%% к Delta_sp) — индикативно",
  "dsp": "Delta_sp = 7pi/30 = 0.733",
  "note_a": "книга шумна (amp ~ 3): E0_free отравлен рядом зоны\n(стена v5 на уровне P4) — статусы честные",
  "slope": "наклон %.2f — нормировки часов расходятся",
  "xt": "z_fine (лестница зумов + s'=-1)", "yt": "ln tau_fresh",
  "xt2": "z_cont_fresh = ln(3P2_raw/|E0_free|)", "yt2": "z_fine",
  "t2": "Гексчек: W2/t0^2 -> 4/3 (пол измерения) и live-башня",
  "c": "W2-каналы, глубокое окно (медианы, p10-p90)",
  "d": "t0: live-башня (разнос) vs legacy (стабильна)",
  "tgt": "цель 4/3",
  "ch_names": ["raw (d-c)-фит", "dc-пара", "d0-clock", "реле (гейт)"],
  "floor": "пол d-мусора ~1e13 t0^2:\nW2-канал заблокирован\n(нужна P4-динамика)",
  "live": "live (tay_ode_fix): разнос t0\n(самореферентность зоны)", "stab": "legacy: t0 стабилен",
  "vt": "eps=1e-2, live z=3.45 (отказ) / legacy z=9.10",
  "xt3": "строка стадии 1", "yt3": "t0 (центральная амплитуда)",
 },
 "en": {
  "t1": "Hexcheck: tau book (fresh fits) and clocks of near-critical chains",
  "a": "ln tau_fresh vs z_fine (deep window)",
  "b": "clocks: z_fine vs z_cont_fresh",
  "tau_f": "model B: Delta = %.2f (%+.1f%% vs Delta_sp) — indicative",
  "dsp": "Delta_sp = 7pi/30 = 0.733",
  "note_a": "book is noisy (amp ~ 3): E0_free poisoned by the zone series\n(v5 wall at the P4 level) — honest statuses",
  "slope": "slope %.2f — clock normalizations diverge",
  "xt": "z_fine (zoom ladder + s'=-1)", "yt": "ln tau_fresh",
  "xt2": "z_cont_fresh = ln(3P2_raw/|E0_free|)", "yt2": "z_fine",
  "t2": "Hexcheck: W2/t0^2 -> 4/3 (measurement floor) and the live tower",
  "c": "W2 channels, deep window (medians, p10-p90)",
  "d": "t0: live tower (blow-up) vs legacy (stable)",
  "tgt": "target 4/3",
  "ch_names": ["raw (d-c) fit", "dc-pair", "d0-clock", "relay (gated)"],
  "floor": "d-junk floor ~1e13 t0^2:\nW2 channel blocked\n(P4 dynamics needed)",
  "live": "live (tay_ode_fix): t0 blow-up\n(zone self-reference)", "stab": "legacy: t0 stable",
  "vt": "eps=1e-2, live z=3.45 (refused) / legacy z=9.10",
  "xt3": "stage-1 row", "yt3": "t0 (central amplitude)",
 },
}


def pick(runs, eps):
    return [r for r in runs if abs(r["eps"] - eps) < 1e-15][0]


def fig1(lang):
    T = L[lang]
    runs = D["runs"]
    r1 = pick(runs, 1e-2)
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.6), constrained_layout=True)
    # (a) ln tau_fresh vs z_fine
    for r_, cc, lab in ((pick(runs, 1e-2), C_LEG, "eps=1e-2"),
                        (pick(runs, 1e-3), C_A, "eps=1e-3")):
        rows = [x for x in r_.get("rows_sample", [])
                if np.isfinite(x.get("tau_fresh", float("nan")))]
        if not rows:
            continue
        zf = np.array([x["z_fine"] for x in rows])
        lt = np.log(np.array([x["tau_fresh"] for x in rows]))
        m = zf >= zf.max() - 2.5 * DELTA_SP
        ax[0].plot(zf[m], lt[m], ".", ms=4, color=cc, alpha=0.75, label=lab)
    fB = (D.get("tau_star_global") or {}).get("model_B_deep_zfine")
    if fB:
        zz = np.linspace(fB["z_window"][0], fB["z_window"][1], 300)
        g = np.exp(0.3 * (zz - fB["z_window"][1]))
        ph = 2 * np.pi * zz / fB["Delta_fit"]
        base = math.log(fB["tau_star"])
        curve = base + g * (fB["wiggle_amp"] * np.cos(ph))
        ax[0].plot(zz, curve, "-", color=C_B, lw=1.8,
                   label=T["tau_f"] % (fB["Delta_fit"],
                                       100 * (fB["Delta_fit"] - DELTA_SP)
                                       / DELTA_SP))
    ax[0].set_title(T["a"], fontsize=11)
    ax[0].set_xlabel(T["xt"]); ax[0].set_ylabel(T["yt"])
    ax[0].legend(fontsize=8, loc="upper left", framealpha=0.9)
    ax[0].text(0.02, 0.02, T["note_a"], transform=ax[0].transAxes,
               fontsize=7.5, va="bottom", color="#4a5568")
    # (b) clock mismatch
    zc, zf2 = [], []
    for r_ in runs:
        for x in r_.get("rows_sample", []):
            if np.isfinite(x.get("z_cont_fresh", float("nan"))):
                zc.append(x["z_cont_fresh"]); zf2.append(x["z_fine"])
    ax[1].plot(zc, zf2, ".", ms=3, color=C_LEG, alpha=0.6)
    cc = (pick(runs, 1e-2).get("clock_check") or {}).get(
        "z_fine_vs_z_cont_fresh", {})
    if cc:
        xs = np.array([min(zc), max(zc)])
        ax[1].plot(xs, cc["slope"] * xs + cc["intercept"], "-", color=C_B,
                   lw=1.6, label=T["slope"] % cc["slope"])
        ax[1].legend(fontsize=8)
    ax[1].set_title(T["b"], fontsize=11)
    ax[1].set_xlabel(T["xt2"]); ax[1].set_ylabel(T["yt2"])
    fig.suptitle(T["t1"], fontsize=12.5)
    out = os.path.join(FIG_RU if lang == "ru" else FIG_EN,
                       "fig_tau_hexcheck.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print("saved", out)


def fig2(lang):
    T = L[lang]
    fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.6), constrained_layout=True)
    # (a) W2 channels floor
    w2 = D["verdicts"]["W2_over_t02_4_3"]["channels_deep_window"]
    names = T["ch_names"]
    keys = ["ch_raw_fit", "ch_dc_pair", "ch_d0_clock", "ch_relay_gated"]
    meds, los, his = [], [], []
    for k in keys:
        s = w2[k]
        meds.append(abs(s["median"]) if s["median"] is not None else np.nan)
        los.append(abs(s["p10"]) if s["p10"] is not None else np.nan)
        his.append(abs(s["p90"]) if s["p90"] is not None else np.nan)
    xs = np.arange(4)
    ax[0].bar(xs, meds, color=[C_FLOOR] * 3 + ["#718096"], width=0.6)
    ax[0].errorbar(xs, meds, yerr=[np.abs(np.array(meds) - np.array(los)),
                                   np.abs(np.array(his) - np.array(meds))],
                   fmt="none", ecolor="#4a5568", capsize=3, lw=1)
    ax[0].axhline(4.0 / 3.0, color=C_TGT, lw=2)
    ax[0].text(3.35, 4.0 / 3.0 * 1.15, T["tgt"], color=C_TGT, fontsize=9,
               ha="right")
    ax[0].set_yscale("log")
    ax[0].set_xticks(xs); ax[0].set_xticklabels(names, fontsize=8.5)
    ax[0].set_title(T["c"], fontsize=11)
    ax[0].text(0.03, 0.95, T["floor"], transform=ax[0].transAxes, fontsize=8,
               va="top", color="#742a2a")
    ax[0].set_ylabel("|W2/t0^2| (log)")
    # (b) live tower vs legacy t0
    lv = D.get("live_tower") or {}
    leg = pick(D["runs"], 1e-2)
    for rec, cc, lab in ((lv, C_LIVE, T["live"]), (leg, C_STAB, T["stab"])):
        rows = sorted(rec.get("rows_sample", []), key=lambda x: (x["stage"], x["v"]))
        rows = [x for x in rows if x["stage"] <= 1]
        if rows:
            ax[1].plot(range(len(rows)), [abs(x["t0"]) for x in rows], ".-",
                       ms=3.5, lw=1, color=cc, label=lab)
    ax[1].set_yscale("log")
    ax[1].set_title(T["d"], fontsize=11)
    ax[1].set_xlabel(T["xt3"]); ax[1].set_ylabel(T["yt3"])
    ax[1].legend(fontsize=8)
    ax[1].text(0.02, 0.02, T["vt"], transform=ax[1].transAxes, fontsize=7.5,
               va="bottom", color="#4a5568")
    fig.suptitle(T["t2"], fontsize=12.5)
    out = os.path.join(FIG_RU if lang == "ru" else FIG_EN,
                       "fig_w2_hexcheck.png")
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print("saved", out)


for lang in ("ru", "en"):
    fig1(lang)
    fig2(lang)
print("OK")
