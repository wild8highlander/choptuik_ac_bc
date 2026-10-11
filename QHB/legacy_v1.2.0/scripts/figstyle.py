"""
figstyle.py — the visual identity of the Quark-Hawking Bridge figures.

"Ink & Gold" tokens inherited verbatim from the Collapse-Hawking Bridge:
one accent gold on near-monochrome ink backgrounds, two themes (light
for print, dark for screens), two languages (en/ru).  Every figure of
the project is produced through this module, so the whole figure set
stays visually coherent.

Rules:
  * constrained_layout everywhere; no tight_layout / subplots_adjust;
  * no gridline louder than 0.35 alpha; no chartjunk;
  * the gold accent marks THE point of the figure (contact point,
    trap boundary, anchor line), never decoration.
"""
import matplotlib.font_manager as fm

for _p in ("/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
    try:
        fm.fontManager.addfont(_p)
    except Exception:
        pass

import matplotlib.pyplot as plt

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
        "gap_title": "The gap law of the three corrections",
        "gap_y": "Floquet gap  $\\Delta_F$  [code]",
        "gap_x": "trio drive amplitude  $\\beta$",
        "gap_quad": "committed quadratic law  $\\Delta_0 + B_2\\beta^2$",
        "gap_window": "committed window",
        "gap_wing": "pre-asymptotic wing (carried, not fitted)",
        "gap_delta0": "static gap  $\\Delta_0$",
        "trap_title": "The three-body trap (escape probability)",
        "trap_y": "escape probability  $P_{esc}$",
        "trap_x": "wall amplitude  $V_0$",
        "trap_free": "free trio (honest negative)",
        "trap_one_e": "$P_{esc} = 1/e$ boundary",
        "wu_title": "The Wu door (residual imbalance)",
        "wu_y": "residual  $r(\\alpha, x)$",
        "wu_x": "freeze-out ratio  $x = \\Gamma/H$",
        "wu_anchor": "Wu anchor $\\alpha = 0.9$ (approx.)",
        "contacts_title": "Two contact points of the bridge",
        "contacts_y": "Hawking temperature  $T_H$  [K]",
        "contacts_x": "black-hole mass  M  [kg]",
        "qcd_contact": "QCD contact: $T_H = T_{QCD}$",
        "cmb_contact": "CMB contact: $T_H = T_{CMB}$",
        "floor_title": "The spectral floor law",
        "floor_y": "gap error  |measured $-$ reference|",
        "floor_x": "simulation window  $T_{sim}$",
        "floor_env": "resolution envelope  $2/N$",
        "floor_unres": "unresolved (beats < 3)",
        "drift_title": "The gap-drift law (heir of T10)",
        "drift_y": "$\\Delta_N$  [code]",
        "drift_x": "grid step  $h$",
        "drift_fit": "$\\Delta_{cont} - C h^2$ (fit; $\\Delta_{cont}$ NOT claimed)",
        "sectors_title": "Per-sector gap response",
        "sectors_y": "shift  $\\Delta_F - \\Delta_0$",
        "sectors_A": "sector A ($\\pi/2$)",
        "sectors_B": "sector B ($\\pi/3$)",
        "sectors_C": "sector C ($\\pi/7$)",
        "map_title": "The physical mapping: three branches (C6)",
        "map_y": "frequency  [Hz]",
        "map_fcontact": "contact  $f = k_B T / h$",
        "map_fgap": "mapped gap  $\\Delta_0 f$",
        "map_L": "$\\Lambda_{QCD}$ (renorm. scale)",
        "map_Q": "$T_{QCD}$ (temperature)",
        "map_E": "$v_{EW}$ (VEV, marked)",
        "anh_title": "The anharmonic trio (C7): the flux tube seals",
        "anh_y": "escape probability  $P_{esc}$",
        "anh_x": "confining core  $\\sigma$",
        "anh_b_title": "The wall boundary $V_0^*$ shrinks (C7)",
        "anh_b_y": "sealing boundary  $V_0^*$ ($P_{esc} = 0.05$)",
        "pair_title": "The pairwise Wu door (C8): it stays, the shape moves",
        "pair_y": "residual  $r$",
        "pair_x": "rate  $\\lambda$ (x := $\\lambda$ for the linear curve)",
        "pair_lin": "linear model (T7)",
        "pair_pair": "pairwise kinetics (C8)",
        "pair_full": "full imbalance",
        "phase_title": "The gap phase map (C9): the valley, no closure",
        "phase_y": "Floquet gap  $\\Delta_F$  [code]",
        "phase_x": "trio drive amplitude  $\\beta$",
        "phase_floor": "detector floor  $2/N$",
        "phase_valley": "measured valley  $\\beta^*(q_{pk})$",
        "phase_betac": "naive-window closure forecast (falsified)",
        "abl_title": "The causal map of the drive (C10): factorial ablation",
        "abl_x": "$|B_2|$ per configuration [code]",
        "abl_y": "sector configuration",
        "abl_none": "exact zero",
        "vor_title": "The invariant wall and the static barrier (C11)",
        "vor_left_y": "y  [code]",
        "vor_left_x": "x  [code]",
        "vor_aref": "Aref manifold (bound, no wall)",
        "vor_right_x": "wall amplitude  $V_0$",
        "vor_right_y": "radius: bound / measured  $r$",
        "vor_bound": "exact bound (T13)",
        "vor_vstar": "$V^* = 0.9359$: escape impossible",
        "vor_resc": "escape radius  $R_{ESC}$",
        "vor_meas": "measured max radius (0/300 escapes)",
    },
    "ru": {
        "gap_title": "Закон зазора трёх поправок",
        "gap_y": "Флоке-зазор  $\\Delta_F$  [код]",
        "gap_x": "амплитуда трио-драйва  $\\beta$",
        "gap_quad": "зафиксированный квадратичный закон  $\\Delta_0 + B_2\\beta^2$",
        "gap_window": "зафиксированное окно",
        "gap_wing": "пре-асимптотическое крыло (пронесено, не фит)",
        "gap_delta0": "статический зазор  $\\Delta_0$",
        "trap_title": "Трёхтельная ловушка (вероятность побега)",
        "trap_y": "вероятность побега  $P_{esc}$",
        "trap_x": "амплитуда стенки  $V_0$",
        "trap_free": "свободное трио (честный негатив)",
        "trap_one_e": "граница $P_{esc} = 1/e$",
        "wu_title": "Дверь Ву (остаточный дисбаланс)",
        "wu_y": "остаток  $r(\\alpha, x)$",
        "wu_x": "отношение заморозки  $x = \\Gamma/H$",
        "wu_anchor": "якорь Ву $\\alpha = 0{,}9$ (прибл.)",
        "contacts_title": "Две точки контакта моста",
        "contacts_y": "Температура Хокинга  $T_H$  [К]",
        "contacts_x": "масса чёрной дыры  M  [кг]",
        "qcd_contact": "контакт с QCD: $T_H = T_{QCD}$",
        "cmb_contact": "контакт с CMB: $T_H = T_{CMB}$",
        "floor_title": "Закон спектрального пола",
        "floor_y": "ошибка зазора  |измерен $-$ референс|",
        "floor_x": "окно моделирования  $T_{sim}$",
        "floor_env": "конверт разрешения  $2/N$",
        "floor_unres": "неразрешено (биений < 3)",
        "drift_title": "Закон дрейфа зазора (наследник T10)",
        "drift_y": "$\\Delta_N$  [код]",
        "drift_x": "шаг сетки  $h$",
        "drift_fit": "$\\Delta_{cont} - C h^2$ (фит; $\\Delta_{cont}$ НЕ утверждается)",
        "sectors_title": "Отклик зазора по секторам",
        "sectors_y": "сдвиг  $\\Delta_F - \\Delta_0$",
        "sectors_A": "сектор A ($\\pi/2$)",
        "sectors_B": "сектор B ($\\pi/3$)",
        "sectors_C": "сектор C ($\\pi/7$)",
        "map_title": "Физическое отображение: три ветви (C6)",
        "map_y": "частота  [Гц]",
        "map_fcontact": "контакт  $f = k_B T / h$",
        "map_fgap": "отображённый зазор  $\\Delta_0 f$",
        "map_L": "$\\Lambda_{QCD}$ (масштаб перенормировки)",
        "map_Q": "$T_{QCD}$ (температура)",
        "map_E": "$v_{EW}$ (VEV, с пометкой)",
        "anh_title": "Ангармоническое трио (C7): трубка запечатывает",
        "anh_y": "вероятность побега  $P_{esc}$",
        "anh_x": "конфайн-ядро  $\\sigma$",
        "anh_b_title": "Граница стенки $V_0^*$ сжимается (C7)",
        "anh_b_y": "граница запечатывания  $V_0^*$ ($P_{esc} = 0{,}05$)",
        "pair_title": "Парная дверь Ву (C8): дверь остаётся, форма уходит",
        "pair_y": "остаток  $r$",
        "pair_x": "скорость  $\\lambda$ (x := $\\lambda$ для линейной кривой)",
        "pair_lin": "линейная модель (T7)",
        "pair_pair": "парная кинетика (C8)",
        "pair_full": "полный дисбаланс",
        "phase_title": "Фазовая карта зазора (C9): долина без закрытия",
        "phase_y": "Флоке-зазор  $\\Delta_F$  [код]",
        "phase_x": "амплитуда трио-драйва  $\\beta$",
        "phase_floor": "порог детектора  $2/N$",
        "phase_valley": "измеренная долина  $\\beta^*(q_{pk})$",
        "phase_betac": "наивный прогноз закрытия (опровергнут)",
        "abl_title": "Каузальная карта драйва (C10): факторная абляция",
        "abl_x": "$|B_2|$ конфигурации [код]",
        "abl_y": "конфигурация секторов",
        "abl_none": "точный нуль",
        "vor_title": "Инвариантная стена и статический барьер (C11)",
        "vor_left_y": "y  [код]",
        "vor_left_x": "x  [код]",
        "vor_aref": "многообразие Арефа (связано, без стенки)",
        "vor_right_x": "амплитуда стенки  $V_0$",
        "vor_right_y": "радиус: граница/измерен  $r$",
        "vor_bound": "точная граница (T13)",
        "vor_vstar": "$V^* = 0{,}9359$: побег невозможен",
        "vor_resc": "радиус побега  $R_{ESC}$",
        "vor_meas": "измеренный макс. радиус (0/300 побегов)",
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
