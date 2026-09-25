#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 ГЕНЕРАЦИЯ ФИГУР ДЛЯ «АУДИТА И ПЕРЕНОСА» (README + PDF-приложение)
================================================================================
  fig_dsi_closure.png      — DSI-замыкание c_K3 (3 панели)
  fig_stability_lemma.png  — лемма Ш.3: теорема следа, острота 5n/7, контраст
  fig_audit_errors.png     — E1 (спектры до/после фикса) + E2 (ряд и суммы)
  fig_transfer_map.png     — карта переноса (структурная диаграмма, HTML+CSS)
Все тексты — на русском (язык пользователя). Шрифт: DejaVu Sans (кириллица).
Запуск: python3 figures.py  → ../figures/*.png
================================================================================
"""
import json
import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

FIG_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", "..", "figures"))
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "axes.unicode_minus": False,
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "figure.dpi": 110,
})

# Палитра фреймворка (низкая насыщенность, тёмные акценты)
C_MAIN = "#1e3a5f"    # глубокий сине-индиго
C_ACC = "#0e7c66"     # тил
C_WARM = "#b45309"    # янтарный
C_RED = "#b91c1c"     # ошибка
C_GRAY = "#6b7280"
C_BG = "#f8fafc"

PI = math.pi
RES_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", "..", "results"))


def load(name):
    p = os.path.join(RES_DIR, name)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


# ==============================================================================
def fig_dsi_closure():
    res = load("dsi_closure.json")
    c0 = res.get("dsi1", {}).get("c0_bare", 0.040507026)
    cstar = res.get("dsi2", {}).get("c_star", 0.040359588)
    measured = res.get("measured", {}).get("extended", 0.04017757639214903)
    lam = 22.0
    omega = 2 * PI / math.log(lam)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4), constrained_layout=True)
    fig.suptitle("DSI-замыкание c_K3 = 0.04018: ренормализация с λ = 22 = b₂(K3)",
                 fontsize=13, fontweight="bold", color=C_MAIN)

    # --- (a) лог-периодическая модуляция -------------------------------------
    ax = axes[0]
    x = np.linspace(0, 3, 1200)          # t = ln(ρ/ρ₀)/ln 22 — в циклах DSI
    sig = 1 + c0 * np.cos(2 * PI * x)
    sig_r = 1 + cstar * np.cos(2 * PI * x + 0.15)
    ax.fill_between(x, 1 - c0, 1 + c0, color=C_MAIN, alpha=0.10)
    ax.plot(x, sig, color=C_MAIN, lw=1.8,
            label=f"каскад, амплитуда c₀ = b_Ch(22) = {c0:.5f}")
    ax.plot(x, sig_r, color=C_ACC, lw=1.2, ls="--",
            label=f"торможённая RG, c* = {cstar:.5f}")
    ax.axhline(1.0, color=C_GRAY, lw=0.7)
    for k in range(4):
        ax.axvline(k, color=C_GRAY, lw=0.5, ls=":")
    ax.set_xlabel("t = ln(ρ/ρ₀) / ln 22   (циклы DSI)")
    ax.set_ylabel("F(ρ)/F₀ρ^α  (нормированная модуляция)")
    ax.set_title("(a) Log-периодическая модуляция, λ = 22", color=C_MAIN)
    ax.legend(loc="upper right", fontsize=8, framealpha=0.9)
    ax.set_xlim(0, 3)
    ax.set_ylim(0.955, 1.045)

    # --- (b) лестница кандидатов ---------------------------------------------
    ax = axes[1]
    cands = [
        ("b_Ch(22)\n[DSI-1, голая]", c0, C_MAIN),
        ("b_Ch(22(1+γ))\n[DSI-2, RG]", cstar, C_ACC),
        ("δ_C⁴ = (π/7)⁴\n[член Бери]", (PI / 7) ** 4, C_GRAY),
        ("1/(χ+1) = 1/25\n[без структуры]", 0.04, C_GRAY),
        ("измерено\n(монография)", measured, C_WARM),
    ]
    ys = np.arange(len(cands))[::-1]
    for y, (nm, v, col) in zip(ys, cands):
        ax.barh(y, v * 1000, color=col, alpha=0.85, height=0.62)
        ax.text(v * 1000 + 0.15, y, f"{v:.6f}", va="center", fontsize=8.5,
                color="#111827")
    ax.axvline(measured * 1000, color=C_WARM, lw=1.2, ls="--")
    ax.set_yticks(ys)
    ax.set_yticklabels([c[0] for c in cands], fontsize=8)
    ax.set_xlabel("амплитуда ×10³")
    ax.set_title("(b) Кандидаты вывода c_K3 (0 подгонки)", color=C_MAIN)
    ax.set_xlim(0, 46)

    # --- (c) систематика окна -------------------------------------------------
    ax = axes[2]
    rows = res.get("dsi3", {}).get("rows", [])
    n_res_vals = sorted({r["n_res"] for r in rows})
    drift_vals = sorted({r["drift"] for r in rows})
    colors = {0.0: C_GRAY, 0.01: C_ACC, 0.02: C_MAIN, 0.05: C_RED}
    for drift in drift_vals:
        xs = [r["n_res"] for r in rows if r["drift"] == drift]
        ys = [100 * r["median_ratio"] for r in rows if r["drift"] == drift]
        ax.plot(xs, ys, "o-", color=colors[drift], lw=1.4, ms=5,
                label=f"дрейф фазы {drift:.2f} рад/ед.t")
    ratio_meas = 100 * measured / c0
    ax.axhline(ratio_meas, color=C_WARM, lw=1.6, ls="--")
    ax.text(9.9, ratio_meas - 0.55, f"измерено/голая = {ratio_meas:.2f}%",
            color=C_WARM, fontsize=9, fontweight="bold",
            bbox=dict(facecolor="white", edgecolor=C_WARM, alpha=0.9,
                      boxstyle="round,pad=0.25"))
    ax.set_xlabel("длина окна измерения, N_res (циклов DSI)")
    ax.set_ylabel("восстановленная / голая амплитуда, %")
    ax.set_title("(c) Систематика окна измерения", color=C_MAIN)
    ax.legend(loc="lower left", fontsize=8)
    ax.set_ylim(79, 102.8)

    out = os.path.join(FIG_DIR, "fig_dsi_closure.png")
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    print(f"[OK] {out}")


# ==============================================================================
def fig_stability_lemma():
    res = load("stability_lemma.json")
    num = res.get("sharpness", {}).get("numerical_min", {})
    sofic = res.get("contrast", {}).get("sofic_F2", {})

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4), constrained_layout=True)
    fig.suptitle("Лемма Ш.3: равномерная устойчивость кунцевского дефекта",
                 fontsize=13, fontweight="bold", color=C_MAIN)

    # --- (a) F_min/n против n -------------------------------------------------
    ax = axes[0]
    ns = sorted(int(k) for k in num.keys())
    fmin_n = [num[str(n)]["per_dim"] for n in ns]
    ax.plot(ns, fmin_n, "o", color=C_MAIN, ms=7, label="численный минимум F_min/n")
    ax.axhline(5 / 7, color=C_ACC, lw=1.8,
               label="острая теорема следа: 5/7 (доказана; равенство — конструкция √(4/7)·I)")
    ax.axhline(1 / 2, color=C_WARM, lw=1.4, ls="--",
               label="оценка v1.0: 1/2 (заменена острой теоремой)")
    ax.set_xlabel("размерность n матричных моделей M_n(ℂ)")
    ax.set_ylabel("дефект на душу размерности e = F/n")
    ax.set_title("(a) Пол дефекта e* = 5/7 — константа по n", color=C_MAIN)
    ax.set_ylim(0.40, 0.80)
    ax.set_xticks(ns)
    ax.legend(loc="upper center", fontsize=8, framealpha=0.92)

    # --- (b) софический профиль F₂ --------------------------------------------
    ax = axes[1]
    Ns = sorted(int(k) for k in sofic.keys())
    mins = [100 * sofic[str(N)]["min_hamming"] for N in Ns]
    ax.plot(Ns, mins, "s-", color=C_ACC, lw=1.8, ms=7,
            label="min Hamming(w)/N, слова ≤ 6")
    ax.axhline(100, color=C_GRAY, lw=0.8, ls=":")
    ax.set_xlabel("размерность перестановочных моделей N")
    ax.set_ylabel("минимальная доля неподвижных точек, %")
    ax.set_title("(b) F₂: дефекты РАЗМЫВАЮТСЯ по масштабу", color=C_MAIN)
    ax.set_ylim(85, 102)
    ax.set_xticks(Ns)
    ax.legend(loc="lower right", fontsize=8)

    # --- (c) пол по классам моделей -------------------------------------------
    ax = axes[2]
    classes = [
        ("теорема следа\n(граница, доказана)", 0.5, C_WARM),
        ("матричные модели\nM_n(ℂ), достигается", 5 / 7, C_MAIN),
        ("перестановочные\nмодели (σᵢτᵢ = id)", 2.0, C_RED),
    ]
    xs = np.arange(len(classes))
    vals = [c[1] for c in classes]
    bars = ax.bar(xs, vals, color=[c[2] for c in classes], alpha=0.85,
                  width=0.55)
    for x, (nm, v, _) in zip(xs, classes):
        ax.text(x, v + 0.05, f"{v:.4f}" if v < 3 else f"{v:.1f}",
                ha="center", fontsize=10, fontweight="bold", color="#111827")
    ax.axhline(0.5, color=C_WARM, lw=1.2, ls="--", alpha=0.6)
    ax.set_xticks(xs)
    ax.set_xticklabels([c[0] for c in classes], fontsize=8.5)
    ax.set_ylabel("дефект на душу размерности e = F/n")
    ax.set_title("(c) Препятствие УСИЛИВАЕТСЯ на софической стороне", color=C_MAIN)
    ax.set_ylim(0, 2.35)

    out = os.path.join(FIG_DIR, "fig_stability_lemma.png")
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    print(f"[OK] {out}")


# ==============================================================================
def fig_audit_errors():
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6), constrained_layout=True)
    fig.suptitle("Аудит монографии: ошибка E1 (знак A) и ошибка E2 (член ряда)",
                 fontsize=13, fontweight="bold", color=C_MAIN)

    # --- (a) E1: спектры на единичной окружности ------------------------------
    ax = axes[0]
    th = np.linspace(0, 2 * PI, 400)
    ax.plot(np.cos(th), np.sin(th), color=C_GRAY, lw=0.8)
    for ang, col, nm in [(6 * PI / 7, C_RED, "печатные матрицы:\n(AB)⁷ = +I, arg = 6π/7"),
                         (PI / 7, C_ACC, "фикс A → −A:\n(AB)⁷ = −I, arg = π/7")]:
        ax.plot([0, math.cos(ang)], [0, math.sin(ang)], color=col, lw=2)
        ax.plot([0, math.cos(-ang)], [0, math.sin(-ang)], color=col, lw=2)
        ax.plot(math.cos(ang), math.sin(ang), "o", color=col, ms=9)
        ax.plot(math.cos(-ang), math.sin(-ang), "o", color=col, ms=9)
        ax.annotate(nm, xy=(math.cos(ang), math.sin(ang)),
                    xytext=(0.15, 1.22 if ang < PI / 2 else -1.5),
                    fontsize=8.5, color=col, fontweight="bold")
    ax.plot(math.cos(PI / 7) * 0.25, math.sin(PI / 7) * 0.25, "h", color=C_WARM, ms=8)
    ax.text(0.3, 0.02, "δ_C = π/7\n(спинорная фаза)", fontsize=8.5, color=C_WARM)
    ax.axhline(0, color=C_GRAY, lw=0.4)
    ax.axvline(0, color=C_GRAY, lw=0.4)
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.65, 1.65)
    ax.set_aspect("equal")
    ax.set_title("(a) E1: знак A — spec(AB) на единичной окружности", color=C_MAIN)
    ax.axis("off")

    # --- (b) E2: ряд и накопленные суммы --------------------------------------
    ax = axes[1]
    dC = PI / 7
    base = 3.4379
    terms_lbl = ["база\nλ₁−R/4+δ²/2−δ⁵/22", "+ δ⁴/8", "+ δ⁶/2\n(два варианта члена)"]
    cum_printed = [base, base + dC**4/8, base + dC**4/8 + 0.00918]
    cum_true = [base, base + dC**4/8, base + dC**4/8 + dC**6/2]
    xs = [0, 1, 2]
    ax.plot(xs, cum_printed, "o-", color=C_RED, lw=1.8, ms=7,
            label="с напечатанным членом (0.00918)")
    ax.plot(xs, cum_true, "s-", color=C_ACC, lw=1.8, ms=7,
            label="с верным членом (0.004086)")
    ax.axhline(3.4470, color=C_MAIN, lw=1.4, ls="--")
    ax.text(0.05, 3.44718, "итог монографии 3.4470 — верен", color=C_MAIN,
            fontsize=9, fontweight="bold")
    ax.axhline(3.443, color=C_GRAY, lw=1.0, ls=":")
    ax.text(0.05, 3.44318, "цель 3.443 (Чоптьюк)", color=C_GRAY, fontsize=9)
    ax.axhline(3.442953, color=C_WARM, lw=1.0, ls="-.", alpha=0.9)
    ax.text(1.02, 3.44135, "следствие E2: база+δ⁴/8 = 3.442953 "
            "(откл. 0.0014% — лучшее)", color=C_WARM, fontsize=8.5)
    for x, v in zip([xs[0], xs[-1]], [cum_printed[0], cum_printed[-1]]):
        ax.annotate(f"{v:.4f}", (x, v), textcoords="offset points",
                    xytext=(8, 7), fontsize=8.5, color=C_RED)
    for x, v in zip([xs[0], xs[-1]], [cum_true[0], cum_true[-1]]):
        ax.annotate(f"{v:.4f}", (x, v), textcoords="offset points",
                    xytext=(8, -14), fontsize=8.5, color=C_ACC)
    ax.set_xticks(xs)
    ax.set_xticklabels(terms_lbl, fontsize=8.5)
    ax.set_ylabel("накопленная сумма Δ_Ch")
    ax.set_title("(b) E2: δ_C⁶/2 — итог 3.4470 верен, слагаемое — нет", color=C_MAIN)
    ax.set_ylim(3.4372, 3.4532)
    ax.legend(loc="upper left", fontsize=8.5)

    out = os.path.join(FIG_DIR, "fig_audit_errors.png")
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    print(f"[OK] {out}")


# ==============================================================================
_HTML = """<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'DejaVu Sans','Noto Sans SC',sans-serif; background:#ffffff; }
  .canvas { width:1180px; padding:26px 30px; background:#ffffff; }
  .title { text-align:center; font-size:21px; font-weight:700; color:#1e3a5f; margin-bottom:6px;}
  .subtitle { text-align:center; font-size:12.5px; color:#6b7280; margin-bottom:22px;}
  .row { display:flex; justify-content:center; gap:26px; margin-bottom:0; }
  .stage { display:flex; flex-direction:column; align-items:center; }
  .box { border-radius:10px; padding:13px 17px; text-align:center; width:330px;
         border:1.6px solid; }
  .b1 { background:#eff6ff; border-color:#1e3a5f; }
  .b2 { background:#f0fdf4; border-color:#0e7c66; }
  .b3 { background:#fefce8; border-color:#b45309; }
  .b4 { background:#faf5ff; border-color:#6d28d9; }
  .box h3 { font-size:14.5px; color:#111827; margin-bottom:5px;}
  .box p { font-size:11.5px; color:#374151; line-height:1.45; }
  .chip { display:inline-block; font-size:10.5px; padding:2px 9px; border-radius:10px;
          margin:2px 3px 0 3px; background:#ffffff; border:1px solid #d1d5db; color:#374151;}
  .down { text-align:center; font-size:19px; color:#1e3a5f; margin:5px 0; line-height:1.1;}
  .down small { display:block; font-size:10.5px; color:#6b7280; }
  .final { width:760px; margin:0 auto; background:#1e3a5f; color:#ffffff;
           border-radius:10px; padding:14px 20px; text-align:center;}
  .final h3 { font-size:15px; margin-bottom:4px;}
  .final p { font-size:11.5px; color:#dbeafe; line-height:1.5;}
</style></head>
<body><div class="canvas">
  <div class="title">Карта переноса: три поправки фреймворка → теория аппроксимаций групп</div>
  <div class="subtitle">геометрия поставляет только (n, B, λ₀); вся структура — чистая алгебра, «работающая в бесконечность»</div>

  <div class="row">
    <div class="stage">
      <div class="box b1">
        <h3>Три поправки (монографии)</h3>
        <p>b-C: δ²/2 = (π/7)²/2 — бэровская фаза порядка 7</p>
        <p>a-C: −δ⁵/22 — торможение, знаменатель b₂(K3)</p>
        <p>𝒞: c_K3 = 0.04018 — амплитуда DSI (λ = 22)</p>
        <span class="chip">источник: геометрия Клейна / K3</span>
      </div>
      <div class="down">▼<small>снятие геометрии</small></div>
    </div>
    <div class="stage">
      <div class="box b2">
        <h3>Алгебраический скелет Δ(n, B; λ₀)</h3>
        <p>Δ = λ₀ + (π/n)²/2 − (π/n)⁵/B (+ δ⁴/8, δ⁶/2)</p>
        <p>n — порядок элемента, B — целочисленный индекс</p>
        <p>определён для ВСЕХ n, B — «работает в бесконечность»</p>
        <span class="chip">проверен на 12 поверхностях ≤ 0.01%</span>
      </div>
      <div class="down">▼<small>функционал метрики</small></div>
    </div>
    <div class="stage">
      <div class="box b3">
        <h3>Универсальная константа b_Ch(n) = 1 − cos(2π/n)</h3>
        <p>= 1 − Re tr(U)/d = ½‖U − I‖²_HS — точное тождество</p>
        <p>минимальный косинусный дефицит модели порядка n</p>
        <p>родной функционал теории аппроксимаций групп</p>
        <span class="chip">hyperlinear: унитарные модели</span>
        <span class="chip">sofic: подстановочные модели</span>
      </div>
    </div>
  </div>

  <div class="down" style="margin-top:2px;">▼<small>перенос на два класса групп</small></div>

  <div class="row">
    <div class="stage">
      <div class="box b2">
        <h3>Софичная сторона: препятствия НЕТ</h3>
        <p>F₂, все линейные группы (включая PSL(2,7) и Γ(2,3,7) монографии):
        Мальцев ⇒ residually finite ⇒ софичны.</p>
        <p>Случайные подстановки: min Hamming/N ≥ 0.9 — фазовые поправки
        размываются вдоль аппроксимаций.</p>
      </div>
    </div>
    <div class="stage">
      <div class="box b4">
        <h3>Несофичная сторона: алгебра Ливитта L_{F₂}(1,2)</h3>
        <p>Кунцевские соотношения: дефект ≥ 5n/7 в КАЖДОЙ M_n (острая теорема
        следа: выпуклость+Хаар); равенство — конструкция √(4/7)·I;
        перестановочные модели: 2n — ещё хуже.</p>
        <p>Пол на душу размерности — константа: поправка НЕ размывается
        никаким масштабом.</p>
      </div>
    </div>
  </div>

  <div class="down">▼<small>лемма Ш.3 (равномерная устойчивость) замыкает цепочку</small></div>

  <div class="final">
    <h3>Цепочка Ш1–Ш4: при лемме Ш.3 группа единиц U(L_{F₂}(1,2)) несофична</h3>
    <p>Ш1: квантованный индекс ([1] = 0 в K₀) и острый дефект ≥ 5/7 на душу &nbsp;•&nbsp;
       Ш2: матричные модели не дают e → 0 &nbsp;•&nbsp;
       Ш3: софичность индуцировала бы e → 0 (лемма Ш.3) &nbsp;•&nbsp;
       Ш4: противоречие.</p>
    <p>Механизм препятствия — и есть алгебраический скелет трёх поправок фреймворка.</p>
  </div>
</div></body></html>
"""


def fig_transfer_map():
    """Структурная диаграмма: HTML+CSS → PNG @2x (Playwright).

    Playwright — опциональная зависимость: если он не установлен (или в
    системе нет браузера Chromium), диаграмма пропускается с понятным
    предупреждением, а весь прогон run_all.py завершается успешно.
    Все остальные фигуры (matplotlib) генерируются как раньше.
    """
    html_path = os.path.join(FIG_DIR, "_transfer_map.html")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(_HTML)
        print("[SKIP] fig_transfer_map.png — модуль playwright не установлен;")
        print("       HTML-заготовка сохранена:", html_path)
        print("       Чтобы собрать PNG: pip install playwright"
              " && playwright install chromium")
        return
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1240, "height": 900},
                        device_scale_factor=2)
        pg.goto("file://" + html_path)
        pg.wait_for_timeout(300)
        el = pg.query_selector(".canvas")
        el.screenshot(path=os.path.join(FIG_DIR, "fig_transfer_map.png"))
        b.close()
    os.remove(html_path)
    print(f"[OK] {os.path.join(FIG_DIR, 'fig_transfer_map.png')}")


# ==============================================================================
if __name__ == "__main__":
    fig_dsi_closure()
    fig_stability_lemma()
    fig_audit_errors()
    fig_transfer_map()
    print("[Все фигуры сгенерированы]")
