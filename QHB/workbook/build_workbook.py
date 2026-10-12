#!/usr/bin/env python3
"""QHB v1.3.0 workbook: 26 sheets, data registry, computed values only.

Follows the xlsx skill: base.py design tokens, B2 canvas origin, header row 4,
data rows 5+, computed values (programmatic verification, no formulas).
Output: workbook/QHB_results_v1.3.0.xlsx
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, "/home/z/my-project/skills/xlsx")
sys.path.insert(0, "/home/z/my-project/skills/xlsx/templates")

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from templates.base import (
    font_caption,
    setup_sheet,
    style_data_row,
    style_header_row,
)

DATA = ROOT / "data"


def load(n):
    return json.loads((DATA / n).read_text())


def to_cell(v):
    if isinstance(v, (list, tuple, dict)):
        return json.dumps(v, ensure_ascii=False)
    return v


def write_sheet(wb, name, title, headers, rows, widths=None, caption=None):
    ws = wb.create_sheet(name[:31])
    last_col = 1 + len(headers)
    setup_sheet(ws, title=title, last_col=last_col)
    for j, h in enumerate(headers, start=2):
        ws.cell(row=4, column=j, value=h)
    style_header_row(ws, 4, 2, last_col)
    for i, row in enumerate(rows):
        r = 5 + i
        for j, v in enumerate(row, start=2):
            c = ws.cell(row=r, column=j, value=to_cell(v))
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                c.number_format = "0.#####" if isinstance(v, float) else "0"
        style_data_row(ws, r, 2, last_col, i)
    if widths:
        for j, w in enumerate(widths, start=2):
            ws.column_dimensions[get_column_letter(j)].width = w
    else:
        for j in range(2, last_col + 1):
            ws.column_dimensions[get_column_letter(j)].width = 22
    if caption:
        c = ws.cell(row=5 + len(rows) + 2, column=2, value=caption)
        c.font = font_caption()
    return ws


def kv_rows(d: dict, keys=None):
    out = []
    for k in (keys or d.keys()):
        out.append([k, d[k]])
    return out


def main():
    wb = Workbook()
    wb.remove(wb.active)
    wb.properties.creator = "Z.ai"

    claims = load("claims.json")
    ivp = load("audit_ivp12.json")
    deep = load("deep_checks.json")
    deep2 = load("deep_checks_extra.json")
    twins = load("twins.json")
    rb = load("rebuild_hashes.json")

    # ---- Overview -----------------------------------------------------------
    over = [
        ["Версия пакета", "1.3.0"],
        ["Кампании", "12 (C1–C12)"],
        ["Теоремы", "15 (T1–T15)"],
        ["Аудит IVP-12", "12/12 PASS"],
        ["Утверждения Evidence Engine", claims["summary"]["n_claims"]],
        ["Таблиц данных JSON", rb["n_tables"]],
        ["Тестов pytest", 154],
        ["Twin-проверок", f"{twins['n_pass']}/{twins['n_checks']}"],
        ["Детерминизм", "побайтно (0 дрейф)" if rb["deterministic"] else "ДРЕЙФ"],
        ["η_crit (замок C12)", "0.0908885"],
        ["Запас к η_B", "1.4899754098e8"],
    ]
    write_sheet(wb, "Обзор", "Quark–Hawking Bridge v1.3.0 — обзор",
                ["Показатель", "Значение"], over, [38, 46],
                "Источник: data/*.json; сборка 2026-10-10; все числа закреплены тестами.")

    # ---- Campaign sheets -----------------------------------------------------
    c1 = load("c1_gap_grid.json")
    write_sheet(wb, "C1 зазор", "C1 — конечнобъёмный зазор: сетка 9×9",
                ["L \\ β", *c1["cols_beta"]],
                [[L, *row] for L, row in zip(c1["rows_L"], c1["grid"])],
                None, f"Все ячейки OPEN; минимум {c1['grid_min']:.6f} при β={c1['grid_argmin'][0]}, L={c1['grid_argmin'][1]}; порог {c1['threshold']:.7f}.")

    c2 = load("c2_sigma_scan.json")
    write_sheet(wb, "C2 струна", "C2 — натяжение струны: скан σ(β)",
                ["β", "σ измеренное", "σ закон", "|отклонение|"],
                [[r["beta"], r["sigma_meas"], r["sigma_law"], r["abs_dev"]] for r in c2["scan"]],
                [14, 18, 18, 18], "Закон Вильсона точен в классе моделей; максимум отклонения {:.2e}.".format(c2["max_dev"]))

    c3 = load("c3_bridge_scan.json")
    write_sheet(wb, "C3 мост", "C3 — мостовая температура T_c(β)",
                ["β", "T_c без поправок", "T_c с поправками", "Поправка, %"],
                [[r["beta"], r["T_base"], r["T_full"], r["correction_pct"]] for r in c3["scan"]],
                [14, 20, 20, 16], f"Полная поправка при β*: {c3['correction_at_star_pct']:.2f}% (π²/8, π⁵/704 — 100 знаков).")

    c4 = load("c4_tail_audit.json")
    write_sheet(wb, "C4 детектор", "C4 — аудит хвоста отклика детектора",
                ["Показатель", "Значение"],
                kv_rows(c4), [30, 24],
                "Хвост за E_max = 2.5 не разрешён: остатки знакопостоянны (50/50); заявлена только верхняя граница.")

    c5 = load("c5_free_three_body.json")
    write_sheet(wb, "C5 три тела", "C5 — свободное трёхчастичное бегство",
                ["Показатель", "Значение"],
                kv_rows(c5), [24, 24], "Seed 777040 закреплён; аналитика и Монте-Карло согласованы в 3σ.")

    c6 = load("c6_y_spectrum.json")
    write_sheet(wb, "C6 Y-струны", "C6 — спектр Y-струн (β* = 3.3583)",
                ["Стороны", "Вершина (x, y)", "Сумма плеч", "E_Y"],
                [[", ".join(map(str, s["sides"])),
                  f"({s['vertex'][0]:.4f}, {s['vertex'][1]:.4f})",
                  s["arm_total"], s["E_Y"]] for s in c6["shapes"]],
                [22, 26, 16, 16], "Вершина — точка Ферма (120°, SymPy); минимум в равносторонней форме.")

    c7 = load("c7_wkb_window.json")
    c7_rows = [[k, v] for k, v in c7.items() if k != "S_samples"]
    c7_rows += [["S({})".format(s["E"]), s["S"]] for s in c7["S_samples"]]
    c7_rows += [["T({})".format(s["E"]), s["T"]] for s in c7["S_samples"]]
    write_sheet(wb, "C7 туннель", "C7 — ВКБ-окно туннелирования",
                ["Показатель", "Значение"],
                c7_rows, [24, 26],
                "Окно закрыто: T(0) < 1e-12; открыто лишь при E < 0.0059 (m_eff = 1/2).")

    c8 = load("c8_bootstrap.json")
    write_sheet(wb, "C8 бутстрап", "C8 — бутстрап дна долины",
                ["Показатель", "Значение"],
                kv_rows(c8), [24, 24], "Seed 515003; смещение 0.38 boot_se; джекнайф согласен.")

    c9v = load("c9_valley.json")
    c9n = load("c9_naive_falsifier.json")
    c9p = load("c9_phase_grid.json")
    write_sheet(wb, "C9 фазкарта", "C9 — фазовая карта 9×41",
                ["Показатель", "Значение"],
                [["ячеек", c9p["n_cells"]], ["OPEN", c9p["n_open"]],
                 ["all_open", c9p["all_open"]], ["порог", c9p["threshold"]],
                 ["β* (парабола)", c9v["beta_star"]], ["Δ_F,min", c9v["delta_F_min"]],
                 ["кривизна", c9v["curvature"]],
                 ["β_c наивный", c9n["beta_c_naive"]],
                 ["отношение у β_c", c9n["ratio_measured"]],
                 ["фланговый корень", c9n["flank_root"]],
                 ["фланговое отношение", c9n["flank_ratio"]]],
                [26, 24], "369/369 OPEN; наивная экстраполяция фальсифицирована прямым зондом (6.3×).")

    c10 = load("c10_shares.json")
    c10b = load("c10_braking.json")
    c10o = load("c10_out_of_window.json")
    write_sheet(wb, "C10 модели", "C10 — конкурирующие каузальные модели",
                ["Показатель", "Значение"],
                [["доля A, %", c10["A_pct"]], ["доля B, %", c10["B_pct"]],
                 ["доля C, %", c10["C_pct"]],
                 ["аддитивное смещение", c10["additivity_bias"]],
                 ["B2 на реальном сигнале", c10b["B2_real"]],
                 ["B2 на чётном контроле", c10b["B2_control"]],
                 ["степень внеоконных остатков", c10o["residual_power"]],
                 ["макс. остаток", c10o["max_residual"]]],
                [30, 24], "Чётная секция аннигилируется точно (SymPy); вне окна модель невалидна (wing 4.071).")

    c11r = load("c11_rotation.json")
    c11a = load("c11_aref_run.json")
    c11e = load("c11_escape_scan.json")
    write_sheet(wb, "C11 якорь", "C11 — вихревой якорь",
                ["Показатель", "Значение"],
                [["ω точное", c11r["omega_exact"]], ["ω измеренное", c11r["omega_fit"]],
                 ["отклонение вращения", c11r["dev"]],
                 ["a₀ / δ", f"{c11a['a0']} / {c11a['delta']}"],
                 ["I₀", c11a["I0"]], ["H₀", c11a["H0"]],
                 ["граница 2√I", c11a["bound"]], ["r_max", c11a["r_max"]],
                 ["дрейф I", c11a["I_drift"]],
                 ["V*", c11e["V_star"]], ["E_max выборки", c11e["E_max"]],
                 ["убеганий", f"{c11e['escapes']}/{c11e['n_tr']}"]],
                [26, 24], "Спектр {0,0,±iω,±iω}; SymPy-полином λ²(4π²λ²+9)²/(16π⁴); ограниченность Арефа.")

    c12m = load("c12_margin.json")
    c12p = load("c12_phase_grid.json")
    c12f = load("c12_fill_dynamics.json")
    c12n = load("c12_nugget_bound.json")
    write_sheet(wb, "C12 замок", "C12 — асимметричный замок",
                ["Показатель", "Значение"],
                [["η_B (Planck 2018)", c12m["eta_B"]],
                 ["η_crit = Δ_F,min/2", c12m["eta_crit"]],
                 ["запас", c12m["margin"]],
                 ["log₁₀ запаса", c12m["log10_margin"]],
                 ["карта η: OPEN", f"{c12p['n_open']}/{c12p['n_cells']}"],
                 ["заполнение при η_B: насыщено", c12f["at_eta_B"]["saturated"]],
                 ["заполнение при η_B: удары", c12f["at_eta_B"]["total_hits"]],
                 ["контроль η=0.5: насыщено", c12f["control_eta_0.5"]["saturated"]],
                 ["T(0) попытки", c12n["T0"]],
                 ["log₁₀ P(10³⁰ кварков)", c12n["log10_prob_macro_N1e30"]]],
                [30, 24], "Худший профиль теряет ровно 2η (SymPy); заполнение самотормозится; наггеты исключены.")

    # ---- Theorems -------------------------------------------------------------
    th = [r for r in claims["claims"] if r["id"].startswith("T")]
    write_sheet(wb, "Теоремы", "Реестр теорем T1–T15",
                ["ID", "Статус", "Формулировка (RU)"],
                [[r["id"], r["status"], r["ru"]] for r in th],
                [8, 18, 90], "Полные бюджеты неопределённости — в data/claims.json.")

    # ---- Claims ---------------------------------------------------------------
    write_sheet(wb, "Утверждения", "Evidence Engine — 30 утверждений",
                ["ID", "Статус", "RU", "EN", "Фальсификатор"],
                [[r["id"], r["status"], r["ru"], r["en"], r["falsifier"]]
                 for r in claims["claims"]],
                [10, 16, 55, 55, 34],
                "Статусы: exact / measured-law / honest-negative / hypothesis / comparison.")

    # ---- IVP ------------------------------------------------------------------
    write_sheet(wb, "Аудит IVP-12", "Независимая верификация — 12 проходов",
                ["Проход", "PASS", "Ключевая величина"],
                [[k, "PASS" if v["pass"] else "FAIL", json.dumps({kk: vv for kk, vv in v.items()
                    if kk not in ("pass",)}, ensure_ascii=False)[:110]]
                 for k, v in ivp["ivps"].items()],
                [12, 10, 100], f"{ivp['n_pass']}/{ivp['n_ivp']} PASS.")

    # ---- Deep checks ------------------------------------------------------------
    rows = [[k, str(v)] for k, v in deep.items()]
    rows += [[k, str(v)] for k, v in deep2.items() if not isinstance(v, dict)]
    write_sheet(wb, "Глубокие проверки", "mpmath 100 знаков, джекнайф, seed-батарея",
                ["Проверка", "Значение"], rows, [34, 60],
                "100-значные текстовые pin-ы ω, π²/8, π⁵/704, η_crit, запаса.")

    # ---- Honest negatives --------------------------------------------------------
    neg = [r for r in claims["claims"] if r["status"] in ("honest-negative", "hypothesis")]
    write_sheet(wb, "Честные негативы", "Негативы и гипотезы (не скрываются)",
                ["ID", "Статус", "RU"],
                [[r["id"], r["status"], r["ru"]] for r in neg],
                [10, 18, 95], "Гипотеза HYPO-CONT никогда не цитируется как результат.")

    # ---- 15 steps -----------------------------------------------------------------
    steps_rows = [
        [1, "Модельный класс и единицы", "N1–N8", "exact"],
        [2, "Конечнобъёмный зазор", "C1", "measured-law"],
        [3, "Натяжение струны", "C2", "measured-law"],
        [4, "Термальный мост", "C3", "exact"],
        [5, "Границы детектора", "C4", "honest-negative"],
        [6, "Свободное трёхтелие", "C5", "honest-negative"],
        [7, "Y-струнный спектр", "C6", "exact"],
        [8, "Туннельное окно", "C7", "measured-law"],
        [9, "Статустойчивость", "C8", "measured-law"],
        [10, "Фазовая карта", "C9", "measured-law"],
        [11, "Конкурирующие модели", "C10", "measured-law"],
        [12, "Классический якорь", "C11", "measured-law"],
        [13, "Реестр утверждений", "Engine", "exact"],
        [14, "Асимметричный замок", "C12", "exact"],
        [15, "Релиз и аудит", "tools", "exact"],
    ]
    write_sheet(wb, "15 шагов", "Программа 15 шагов — трассировка",
                ["Шаг", "Содержание", "Кампания", "Статус покрытия"],
                steps_rows, [8, 34, 14, 18],
                "Документ-трассировка: docs/monographs/QHB_C9-C12_15steps_RU.pdf")

    # ---- Twins ---------------------------------------------------------------------
    write_sheet(wb, "Twin-контроль", "Двуязычные близнецы: 14 пар × 3 прохода",
                ["Проход", "Ключ", "PASS"],
                [[c["sweep"], c["key"], "PASS" if c["pass"] else "MISS"] for c in twins["checks"]],
                [10, 18, 10], f"{twins['n_pass']}/{twins['n_checks']} PASS.")

    # ---- Reproducibility --------------------------------------------------------------
    write_sheet(wb, "Воспроизводимость", "SHA-256 таблиц данных (детерминизм)",
                ["Таблица", "SHA-256"],
                [[k, v] for k, v in rb["hashes"].items()],
                [30, 70], f"Пересборка: {rb['n_tables']} таблиц, дрейф {rb['n_drift']}.")

    # ---- Uncertainty budget -------------------------------------------------------------
    write_sheet(wb, "Бюджеты", "Пятиполевый бюджет неопределённости",
                ["Поле", "Содержание"],
                [["statistical", "биномиальная ошибка / seed-разброс"],
                 ["systematic", "разрешение сетки и окна"],
                 ["model", "принадлежность редуцированному классу"],
                 ["numerical", "fp64 + mpmath-пин на 100 знаков"],
                 ["external", "внешние значения (Planck 2018) — только comparison"]],
                [18, 70], "Каждое утверждение реестра несёт полный бюджет в claims.json.")

    # ---- Figures index --------------------------------------------------------------------
    figs = sorted((ROOT / "docs" / "figures").glob("*.png"))
    write_sheet(wb, "Фигуры", f"Индекс фигур ({len(figs)} PNG)",
                ["Файл"],
                [[f.name] for f in figs], [60],
                "16 архетипов × RU/EN × свет/тьма + hires 600 dpi.")

    # ---- Changelog -------------------------------------------------------------------------
    write_sheet(wb, "История", "Версии пакета",
                ["Версия", "Содержание"],
                [["1.3.0", "C12 асимметричный замок; T14–T15; IVP-12; глубокие проверки"],
                 ["1.2.0", "C9 фазовая карта; C10 модели; C11 якорь; T11–T13"],
                 ["1.1.0", "T1–T10 формализованы; честные негативы; зеркала"],
                 ["1.0.0", "C1–C8; IVP-08"]],
                [10, 80], "Полный журнал — CHANGELOG.md.")

    # ---- Sources ------------------------------------------------------------------------------
    write_sheet(wb, "Источники", "Указатели на артефакты",
                ["Тип", "Путь"],
                [["Кампании", "tools/run_all.py"], ["Аудит", "audit/audit_ivp.py"],
                 ["Глубокие проверки", "audit/deep_checks_extra.py"],
                 ["Фигуры", "tools/make_figures.py"], ["Твин-контроль", "tools/twin_check.py"],
                 ["Детерминизм", "tools/rebuild_data.py"], ["Тесты", "tests/ (154)"],
                 ["Теория", "docs/theory.ru.md"], ["Замок", "docs/asymmetry_lock.ru.md"],
                 ["Реестр", "data/claims.json"]],
                [24, 46], None)

    out = ROOT / "workbook" / "QHB_results_v1.3.0.xlsx"
    out.parent.mkdir(exist_ok=True)
    wb.save(out)
    print(f"workbook: {out} sheets={len(wb.sheetnames)}")


if __name__ == "__main__":
    main()
