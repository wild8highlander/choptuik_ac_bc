# -*- coding: utf-8 -*-
"""
figstyle.py — the visual identity of the Collapse-Hawking Bridge figures.

"Ink & Gold" tokens: one accent gold on near-monochrome ink backgrounds,
two themes (light for print, dark for screens), two languages (en/ru).
Every figure of the project is produced through this module, so the
whole figure set stays visually coherent.

Rules:
  * constrained_layout everywhere; no tight_layout / subplots_adjust;
  * no gridline louder than 0.35 alpha; no chartjunk;
  * the gold accent marks THE point of the figure (contact point,
    Page time, anchor line), never decoration.
"""
import matplotlib.font_manager as fm

for _p in ("/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
    try:
        fm.fontManager.addfont(_p)
    except Exception:
        pass

import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Noto Sans SC"]
plt.rcParams["axes.unicode_minus"] = False

TOKENS = {
    "light": {
        "bg": "#FAF7F0", "panel": "#FFFFFF", "ink": "#1A1A24",
        "gold": "#8C6D1F", "gold_soft": "#C9A84C", "muted": "#6B6455",
        "grid": "#D8D2C4", "ok": "#3A6B4F", "bad": "#8C3A2F",
    },
    "dark": {
        "bg": "#10101A", "panel": "#171724", "ink": "#E8E2D0",
        "gold": "#C9A84C", "gold_soft": "#E3C878", "muted": "#8A8574",
        "grid": "#2A2A3A", "ok": "#7FBF9A", "bad": "#D97B6C",
    },
}

LANG = {
    "en": {
        "hawking_title": "Hawking thermodynamics vs mass",
        "T_H": "Hawking temperature  $T_H$  [K]",
        "S_BH": "Bekenstein-Hawking entropy  $S_{BH}/k_B$",
        "M": "black-hole mass  M  [kg]",
        "cmb_contact": "CMB contact: $T_H = T_{CMB}$",
        "page_title": "Page curves of the born ensemble",
        "page_y": "radiation entropy  $S_{rad}/S_0$",
        "page_x": "time  $t/t_{evap}$",
        "page_time": "Page time  $(1-2^{-3/2})\\,t_{evap}$",
        "ladder_title": "Scale ladder (lengths)",
        "scaling_title": "Born spectrum and the critical anchor",
        "scaling_y": "black-hole mass  $M_{code}$",
        "scaling_x": "distance from threshold  $\\varepsilon = A - A^*$",
        "anchor": "anchor slope $\\gamma_{Ch} = 0.374$",
        "floor": "fixed-grid mass floor",
        "validation_title": "Engine validation (Roberts-Oshiro)",
        "val_y": "$\\max|r - r_{exact}|$",
        "val_x": "grid N",
        "map_title": "The Collapse-Hawking Bridge",
        "branch_sub_title": "Subcritical branch: approach to the threshold",
        "branch_sub_y": "peak compactness  $q_{max} = \\max(2m/r)$",
        "branch_sub_x": "distance from threshold  $\\varepsilon = A^* - A$",
        "branch_horizon": "horizon compactness  $q = 1$",
        "branch_bif_title": "Supercritical branch: born bifurcation",
        "branch_bif_y": "fraction of saturation  $\\tilde f(\\varepsilon)$",
        "branch_bif_x": "distance from threshold  $\\varepsilon = A - A^*$",
        "branch_eps_half": "$\\varepsilon_{1/2} = 4.86\\times10^{-3}$",
        "branch_sat": "saturation  $\\tilde f = 1$",
    },
    "ru": {
        "hawking_title": "Термодинамика Хокинга и масса",
        "T_H": "Температура Хокинга  $T_H$  [К]",
        "S_BH": "Энтропия Бекенштейна–Хокинга  $S_{BH}/k_B$",
        "M": "масса чёрной дыры  M  [кг]",
        "cmb_contact": "Контакт с CMB: $T_H = T_{CMB}$",
        "page_title": "Кривые Пейджа ансамбля рождения",
        "page_y": "энтропия излучения  $S_{rad}/S_0$",
        "page_x": "время  $t/t_{evap}$",
        "page_time": "Время Пейджа  $(1-2^{-3/2})\\,t_{evap}$",
        "ladder_title": "Лестница масштабов (длины)",
        "scaling_title": "Спектр рождения и критический якорь",
        "scaling_y": "масса чёрной дыры  $M_{code}$",
        "scaling_x": "расстояние от порога  $\\varepsilon = A - A^*$",
        "anchor": "якорь $\\gamma_{Ch} = 0.374$",
        "floor": "массовый пол сетки",
        "validation_title": "Валидация движка (Робертс–Оширо)",
        "val_y": "$\\max|r - r_{exact}|$",
        "val_x": "сетка N",
        "map_title": "Мост «Коллапс–Хокинг»",
        "branch_sub_title": "Докритическая ветвь: приближение к порогу",
        "branch_sub_y": "пиковая компактность  $q_{max} = \\max(2m/r)$",
        "branch_sub_x": "расстояние от порога  $\\varepsilon = A^* - A$",
        "branch_horizon": "компактность горизонта  $q = 1$",
        "branch_bif_title": "Сверхкритическая ветвь: бифуркация рождения",
        "branch_bif_y": "доля насыщения  $\\tilde f(\\varepsilon)$",
        "branch_bif_x": "расстояние от порога  $\\varepsilon = A - A^*$",
        "branch_eps_half": "$\\varepsilon_{1/2} = 4{,}86\\times10^{-3}$",
        "branch_sat": "насыщение  $\\tilde f = 1$",
    },
}


def style(theme="light"):
    """Apply theme rcParams; returns the token dict."""
    t = TOKENS[theme]
    plt.rcParams.update({
        "figure.facecolor": t["bg"],
        "axes.facecolor": t["panel"],
        "axes.edgecolor": t["grid"],
        "axes.labelcolor": t["ink"],
        "axes.titlecolor": t["ink"],
        "xtick.color": t["ink"], "ytick.color": t["ink"],
        "grid.color": t["grid"], "grid.alpha": 0.35,
        "text.color": t["ink"],
        "savefig.facecolor": t["bg"],
        "font.size": 11,
        "axes.titlesize": 13,
    })
    return t


def new_fig(w=8.0, h=5.2):
    """Constrained-layout figure (the ONLY layout engine used here)."""
    return plt.figure(figsize=(w, h), constrained_layout=True)


def finish(fig, path, dpi=300):
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
