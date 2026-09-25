#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Оркестратор «Аудита и переноса»: запускает все три задачи последовательно,
затем генерирует фигуры. Пишет results/*.json и figures/*.png.

Запуск из корня репозитория:
    python3 audit_transfer/python/run_all.py
или из этой папки:
    python3 run_all.py

Требования: python >= 3.10, numpy, scipy, matplotlib.
Опционально: playwright (только для одной структурной диаграммы
fig_transfer_map.png) — без него прогон завершается успешно, диаграмма
пропускается с предупреждением.
Полное время прогона ~2–4 минуты (доминирует численная минимизация леммы Ш.3).
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "audit_transfer")
sys.path.insert(0, PKG)


def banner(s):
    print("\n" + "#" * 78)
    print("# " + s)
    print("#" * 78)


def main():
    t0 = time.time()
    banner("«АУДИТ И ПЕРЕНОС» — ПОЛНЫЙ ПРОГОН (3 задачи + фигуры)")

    banner("ЗАДАЧА 1: аудит монографии (поправки b-C/a-C, каталог E1–E7)")
    import monograph_audit
    monograph_audit.main()

    banner("ЗАДАЧА 2: DSI-замыкание c_K3 = 0.04018 (λ = 22 = b₂(K3))")
    import dsi_closure
    dsi_closure.main()

    banner("ЗАДАЧА 3: лемма Ш.3 (равномерная устойчивость кунцевского дефекта)")
    import stability_lemma
    stability_lemma.main()

    banner("ФИГУРЫ (figures/*.png)")
    try:
        import figures
        figures.fig_dsi_closure()
        figures.fig_stability_lemma()
        figures.fig_audit_errors()
        figures.fig_transfer_map()
    except Exception as exc:  # noqa: BLE001 — фигуры не должны ронять верификацию
        print(f"[ПРЕДУПРЕЖДЕНИЕ] часть фигур не собрана: {exc}")
        print("  Результаты задач 1–3 (results/*.json) не затронуты и валидны.")

    banner("ГОТОВО")
    print(f"  Полное время прогона: {time.time() - t0:.1f} с")
    print("  Результаты: audit_transfer/results/*.json")
    print("  Фигуры:     audit_transfer/figures/*.png")
    print("  PDF-приложение: audit_transfer/appendix/ (см. README)")


if __name__ == "__main__":
    main()
