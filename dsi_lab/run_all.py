#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Оркестратор DSI-лаборатории: запуск всех 7 экспериментов одной командой.

Запуск:
    python3 run_all.py                # все 7 экспериментов + fig_choptuik
    python3 run_all.py 1 6 7          # только эксперименты 1, 6, 7
    python3 run_all.py --list         # список экспериментов без запуска
    python3 run_all.py --no-figures   # пропустить fig_choptuik.py

Вывод:
    results/exp{1..7}_*.json  +  фигуры в fig_ru/ и fig_en/

Эксперименты (пакет самодостаточен, зависит только от numpy/scipy/matplotlib):
    1  Ш.3(iii) — мост следа: теорема F >= 5n/7, дерево Кунца F = n+2, софика
    2  DSI-4: c_K3 = 27/672 = 9/224 — подходящая дробь, лемма единственности
    3  Башня Гурвица: находка D1 (несогласованность строки g=14), PSL(2,13)
    4  QNM: каталог 10 событий, 0.84 сигмы на CE, лестница обертонов GW150914
    5  QCD-мост: находка E1 (центрирование <лямбда>), наклон -0.99, kT-sweep
    6  Атака на 224 = 4*56: перепись {7,3} из GL(3,2), провенанс, c(g)
    7  Порог e >= 1: теоремы A/B/C — лестница 5/7 -> 1 -> 2 стала теоремой
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).parent

EXPERIMENTS = {
    "1": ("exp1_sh3_bridge.py",     "Ш.3(iii): мост следа, дерево Кунца, софика"),
    "2": ("exp2_dsi4.py",           "DSI-4: c_K3 = 27/672 = 9/224, подходящая дробь"),
    "3": ("exp3_hurwitz.py",        "Башня Гурвица, находка D1, PSL(2,13)"),
    "4": ("exp4_qnm.py",            "QNM: каталог, обнаружимость 0.84с, обертоны"),
    "5": ("exp5_qcd.py",            "QCD-мост: находка E1, ~1/N, kT-sweep"),
    "6": ("exp6_census_224.py",     "224 = 4*56: перепись {7,3}, провенанс, c(g)"),
    "7": ("exp7_e1_threshold.py",   "Теоремы A/B/C: порог e >= 1"),
}
EXTRA = {
    "fig": ("fig_choptuik.py", "Сводная фигура задачи Чоптюка (иллюстрация)"),
}


def run_script(name: str) -> None:
    print("\n" + "#" * 78)
    print(f"# ЗАПУСК: {name}")
    print("#" * 78)
    t0 = time.time()
    r = subprocess.run([sys.executable, str(BASE / name)])
    dt = time.time() - t0
    if r.returncode != 0:
        print(f"[ОШИБКА] {name} завершился с кодом {r.returncode} ({dt:.1f} с)")
        sys.exit(r.returncode)
    print(f"[OK] {name} — {dt:.1f} с")


def main():
    ap = argparse.ArgumentParser(description="DSI lab: все эксперименты одним прогоном")
    ap.add_argument("ids", nargs="*", help="номера экспериментов (1..7), пусто = все")
    ap.add_argument("--list", action="store_true", help="показать список и выйти")
    ap.add_argument("--no-figures", action="store_true",
                    help="не запускать fig_choptuik.py")
    args = ap.parse_args()
    t0 = time.time()

    if args.list:
        print("Эксперименты:")
        for k in sorted(EXPERIMENTS):
            f, d = EXPERIMENTS[k]
            print(f"  {k}. {f:<24s} {d}")
        f, d = EXTRA["fig"]
        print(f"  fig. {f:<24s} {d}")
        return

    todo = sorted(args.ids) if args.ids else sorted(EXPERIMENTS)
    for k in todo:
        if k not in EXPERIMENTS:
            print(f"[ОШИБКА] неизвестный номер эксперимента: {k} "
                  f"(доступны 1..{len(EXPERIMENTS)})")
            sys.exit(2)
        run_script(EXPERIMENTS[k][0])

    if not args.no_figures and (not args.ids or "fig" in args.ids):
        run_script(EXTRA["fig"][0])

    print("\n" + "=" * 78)
    print(f"ГОТОВО: {len(todo)} эксперимент(ов) за {time.time() - t0:.1f} с")
    print(f"Результаты:  {BASE / 'results'}")
    print(f"Фигуры:       {BASE / 'fig_ru'} и {BASE / 'fig_en'}")
    print("JSON закоммичены в репозиторий — сравните после прогона:")
    print("  git diff --stat results/")


if __name__ == "__main__":
    main()
