#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
СИМВОЛЬНЫЙ ВЫВОД СИСТЕМЫ ЭЙНШТЕЙН–СКАЛЯРНОЕ ПОЛЕ В ДВУНУЛЕВЫХ КООРДИНАТАХ
SYMBOLIC DERIVATION OF THE DOUBLE-NULL EINSTEIN–SCALAR SYSTEM
================================================================================

Путь вывода (метод Гильберта, 1915):

  1. Действие Гильберта:
         S[g, Phi] = (1/2kappa) ∫ sqrt(-g) R d^4x  +  S_m[g, Phi],
         S_m = -1/2 ∫ sqrt(-g) g^{ab} Phi_a Phi_b d^4x   (безмассовое скалярное поле)

  2. Варьирование по g^{mu nu} даёт уравнения Эйнштейна
         G_{mu nu} = kappa T_{mu nu},
     где T_{mu nu} — ТЕНЗОР ЭНЕРГИИ-ИМПУЛЬСА ГИЛЬБЕРТА:
         T_{mu nu} = -(2/sqrt(-g)) delta S_m / delta g^{mu nu}
                   = Phi_mu Phi_nu - (1/2) g_{mu nu} (grad Phi)^2 .

  3. Варьирование по Phi даёт волновое уравнение  box Phi = 0;
     проверяется тождество Гильберта:  nabla_mu T^{mu}_nu == 0  <=>  box Phi = 0.

  4. Сферическая симметрия + двунулевые координаты
         ds^2 = -alpha(u,v)^2 du dv + r(u,v)^2 dOmega^2
     → замкнутая система 1+1 для (r, Phi, omega = ln alpha):
         (SC)  Phi_uv + (r_u Phi_v + r_v Phi_u)/r = 0
         (C1)  r_uu - omega_u r_u + (kappa/2) r Phi_u^2 = 0        [G_uu = kappa T_uu]
         (C2)  r_vv - omega_v r_v + (kappa/2) r Phi_v^2 = 0        [G_vv = kappa T_vv]
         (UV/TH): два уравнения на (r_uv, omega_uv) из G_uv и G_thth.

  5. МАШИННАЯ ПРОВЕРКА: точное решение Робертса–Оширо (исправленная форма из
     Burko, gr-qc/9608061) подставляется в выведенную систему — невязки должны
     обращаться в ноль с машинной точностью (mpmath, 50 знаков).

Запуск:   python3 sympy_derivation.py
Вывод:    results/derivation_results.json
================================================================================
"""
import json
import os
import time

import sympy as sp

BASE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

t_start = time.time()
log_lines = []


def log(msg):
    print(msg)
    log_lines.append(msg)


# ------------------------------------------------------------------------------
# 1. Метрика, символы Кристоффеля, тензор Риччи, тензор Эйнштейна
# ------------------------------------------------------------------------------
log("=" * 78)
log("ШАГ 1. Метрика ds^2 = -alpha(u,v)^2 du dv + r(u,v)^2 dOmega^2")
log("=" * 78)

u, v, th = sp.symbols("u v theta", real=True)
kappa = sp.Symbol("kappa", positive=True)

alpha = sp.Function("alpha")(u, v)
r = sp.Function("r")(u, v)
Phi = sp.Function("Phi")(u, v)

coords = (u, v, th, sp.Symbol("varphi", real=True))

# g_{mu nu}, порядок (u, v, theta, varphi)
g = sp.zeros(4, 4)
g[0, 0] = 0
g[0, 1] = g[1, 0] = -alpha**2 / 2
g[2, 2] = r**2
g[3, 3] = r**2 * sp.sin(th) ** 2

g_inv = g.inv()
sqrt_neg_g = sp.sqrt(-sp.det(g))

log(f"  sqrt(-g) = {sqrt_neg_g}")

# Символы Кристоффеля Gamma^sigma_{mu nu} (без упрощения, для скорости)
Gamma = {}
for sig in range(4):
    for mu in range(4):
        for nu in range(mu, 4):
            expr = sp.S.Zero
            for rho in range(4):
                expr += g_inv[sig, rho] * (
                    sp.diff(g[nu, rho], coords[mu])
                    + sp.diff(g[mu, rho], coords[nu])
                    - sp.diff(g[mu, nu], coords[rho])
                )
            expr = sp.simplify(expr / 2)
            Gamma[(sig, mu, nu)] = expr
            if nu != mu:
                Gamma[(sig, nu, mu)] = expr

log("  Кристоффели: вычислено %d символов" % len(Gamma))

# Тензор Риччи R_{mu nu} = d_rho Gamma^rho_{mu nu} - d_nu Gamma^rho_{mu rho}
#                       + Gamma^rho_{mu nu} Gamma^sigma_{rho sigma}
#                       - Gamma^sigma_{mu rho} Gamma^rho_{nu sigma}
Ric = {}
for mu in range(4):
    for nu in range(mu, 4):
        expr = sp.S.Zero
        for rho in range(4):
            expr += sp.diff(Gamma[(rho, mu, nu)], coords[rho])
            expr -= sp.diff(Gamma[(rho, mu, rho)], coords[nu])
            for sig in range(4):
                expr += Gamma[(rho, mu, nu)] * Gamma[(sig, rho, sig)]
                expr -= Gamma[(sig, mu, rho)] * Gamma[(rho, nu, sig)]
        Ric[(mu, nu)] = expr
        if nu != mu:
            Ric[(nu, mu)] = expr

# Скалярная кривизна R = g^{mu nu} R_{mu nu}
R_scalar = sp.S.Zero
for mu in range(4):
    for nu in range(4):
        R_scalar += g_inv[mu, nu] * Ric[(mu, nu)]
R_scalar = sp.simplify(R_scalar)

log("  R (скалярная кривизна) упрощена: %d символов в выражении" % len(str(R_scalar)))

# Тензор Эйнштейна
Einstein = {}
for mu in range(4):
    for nu in range(mu, 4):
        Einstein[(mu, nu)] = sp.simplify(Ric[(mu, nu)] - sp.Rational(1, 2) * g[mu, nu] * R_scalar)
        if nu != mu:
            Einstein[(nu, mu)] = Einstein[(mu, nu)]

log("  G_{mu nu} вычислен для всех компонент")

# --- Контрольные проверки общего вида -----------------------------------------
# R_phiphi = sin^2(theta) R_thth (сферическая симметрия)
check_sph = sp.simplify(Ric[(3, 3)] - sp.sin(th) ** 2 * Ric[(2, 2)])
log(f"  Проверка R_varphi varphi = sin^2(theta) R_thth: {'OK' if check_sph == 0 else 'FAIL: ' + str(check_sph)}")

# ------------------------------------------------------------------------------
# 2. ТЭИ Гильберта и волновое уравнение
# ------------------------------------------------------------------------------
log("")
log("=" * 78)
log("ШАГ 2. ТЭИ Гильберта T_{mu nu} = Phi_mu Phi_nu - 1/2 g_{mu nu} (grad Phi)^2")
log("=" * 78)

grad2 = sp.S.Zero  # (grad Phi)^2 = g^{ab} Phi_a Phi_b
for a in range(4):
    for b in range(4):
        pa = Phi.diff(coords[a])
        pb = Phi.diff(coords[b])
        if pa != 0 and pb != 0:
            grad2 += g_inv[a, b] * pa * pb
grad2 = sp.simplify(grad2)

T = {}
for mu in range(4):
    for nu in range(mu, 4):
        p_mu = Phi.diff(coords[mu])
        p_nu = Phi.diff(coords[nu])
        T[(mu, nu)] = sp.simplify(p_mu * p_nu - sp.Rational(1, 2) * g[mu, nu] * grad2)
        if nu != mu:
            T[(nu, mu)] = T[(mu, nu)]

log(f"  (grad Phi)^2 = {grad2}")
log(f"  T_uv = {T[(0, 1)]}   (для безмассового скаляра должно быть 0)")
log(f"  T_uu = {T[(0, 0)]}")
log(f"  T_vv = {T[(1, 1)]}")
log(f"  T_thth = {T[(2, 2)]}")

# Волновое уравнение box Phi = (1/sqrt(-g)) d_a (sqrt(-g) g^{ab} d_b Phi) = 0
boxPhi = sp.S.Zero
for a in range(4):
    for b in range(4):
        if g_inv[a, b] != 0:
            boxPhi += sp.diff(sqrt_neg_g * g_inv[a, b] * Phi.diff(coords[b]), coords[a])
boxPhi = sp.simplify(boxPhi / sqrt_neg_g)
log(f"  box Phi = {boxPhi}")

# Тождество Гильберта: nabla_mu T^{mu}_nu = 0 <=> box Phi = 0
# T^mu_nu = g^{mu a} T_{a nu};  nabla_mu T^mu_nu = d_mu T^mu_nu + Gamma^mu_{mu a} T^a_nu - Gamma^a_{mu nu} T^mu_a
hilbert_check = {}
for nu in range(4):
    # T^mu_nu = g^{mu a} T_{a nu}
    Tup_dn = {}
    for mu_ in range(4):
        acc = sp.S.Zero
        for a in range(4):
            if g_inv[mu_, a] != 0:
                acc += g_inv[mu_, a] * T[(a, nu)]
        Tup_dn[mu_] = sp.simplify(acc)
    # nabla_mu T^mu_nu = d_mu T^mu_nu + Gamma^mu_{mu a} T^a_nu - Gamma^a_{mu nu} T^mu_a
    expr = sp.S.Zero
    for mu_ in range(4):
        expr += sp.diff(Tup_dn[mu_], coords[mu_])
        for a in range(4):
            expr += Gamma[(mu_, mu_, a)] * Tup_dn[a]
            Tmu_a = sp.S.Zero
            for b_ in range(4):
                if g_inv[mu_, b_] != 0:
                    Tmu_a += g_inv[mu_, b_] * T[(b_, a)]
            expr -= Gamma[(a, mu_, nu)] * Tmu_a
    hilbert_check[nu] = sp.simplify(expr)

for nu, expr in hilbert_check.items():
    ratio = sp.simplify(expr / boxPhi) if boxPhi != 0 else sp.S.NaN
    log(f"  nabla_mu T^mu_{['u','v','th','ph'][nu]} / box Phi = {ratio}")

# ------------------------------------------------------------------------------
# 3. Проекция уравнений Эйнштейна: замкнутая 1+1 система (ПРЯМОЕ РЕШЕНИЕ)
# ------------------------------------------------------------------------------
log("")
log("=" * 78)
log("ШАГ 3. Проекции G_{mu nu} = kappa T_{mu nu} → замкнутая 1+1 система")
log("=" * 78)

omega = sp.Function("omega")(u, v)  # omega := ln(alpha)
alpha_to_omega = {alpha: sp.exp(omega)}

# Замена производных alpha -> omega: alpha = exp(omega),
# alpha_x = alpha*omega_x, alpha_xy = alpha*(omega_xy + omega_x*omega_y)
ALPHA_D = [
    (sp.Derivative(sp.exp(omega), u), sp.exp(omega) * omega.diff(u)),
    (sp.Derivative(sp.exp(omega), v), sp.exp(omega) * omega.diff(v)),
    (sp.Derivative(sp.exp(omega), u, v), sp.exp(omega) * (omega.diff(u, v) + omega.diff(u) * omega.diff(v))),
]


def ein_in_omega(component):
    """Компонента G_{mu nu} в переменных (r, Phi, omega)."""
    return sp.expand(component.subs(alpha_to_omega).subs(ALPHA_D))


def T_in_omega(component):
    """Компонента T_{mu nu} в переменных (r, Phi, omega)."""
    return sp.expand(component.subs(alpha_to_omega).subs(ALPHA_D[:2]))


r_uu_sym = sp.Derivative(r, u, 2)
r_vv_sym = sp.Derivative(r, v, 2)
r_uv_sym = sp.Derivative(r, u, v)
omega_uv_sym = sp.Derivative(omega, u, v)

# (C1): G_uu = kappa T_uu → решаем относительно r_uu
C1_eq = sp.expand(ein_in_omega(Einstein[(0, 0)]) - kappa * T_in_omega(T[(0, 0)]))
C1_solved = sp.solve(sp.Eq(C1_eq, 0), r_uu_sym)
C1_form = sp.simplify(C1_solved[0]) if C1_solved else None
log(f"  (C1)  r_uu = {C1_form}")

# (C2): G_vv = kappa T_vv → решаем относительно r_vv
C2_eq = sp.expand(ein_in_omega(Einstein[(1, 1)]) - kappa * T_in_omega(T[(1, 1)]))
C2_solved = sp.solve(sp.Eq(C2_eq, 0), r_vv_sym)
C2_form = sp.simplify(C2_solved[0]) if C2_solved else None
log(f"  (C2)  r_vv = {C2_form}")

# (SC): волновое уравнение box Phi = 0
SC_expr = sp.simplify(Phi.diff(u, v) + (r.diff(u) * Phi.diff(v) + r.diff(v) * Phi.diff(u)) / r)
box_check = sp.simplify(boxPhi + sp.Rational(4) / alpha**2 * SC_expr)  # boxPhi = -(4/alpha^2) SC ?
log(f"  (SC)  Phi_uv + (r_u Phi_v + r_v Phi_u)/r = 0 ; проверка box Phi = -(4/alpha^2)*SC: {box_check}")

# (UV): G_uv = kappa T_uv = 0 → решаем относительно r_uv
UV_eq = sp.expand(ein_in_omega(Einstein[(0, 1)]) - kappa * T_in_omega(T[(0, 1)]))
UV_solved = sp.solve(sp.Eq(UV_eq, 0), r_uv_sym)
UV_form = sp.simplify(UV_solved[0]) if UV_solved else None
log(f"  (UV)  r_uv = {UV_form}")

# (TH): G_thth = kappa T_thth → связь на omega_uv / r_uv (уравнение согласованности)
TH_eq = sp.expand(ein_in_omega(Einstein[(2, 2)]) - kappa * T_in_omega(T[(2, 2)]))
TH_form = None
for cand in (sp.simplify(TH_eq), TH_eq):
    sol = sp.solve(sp.Eq(cand, 0), omega_uv_sym)
    if sol:
        TH_form = sp.simplify(sol[0])
        break
if TH_form is None:
    for cand in (sp.simplify(TH_eq), TH_eq):
        sol = sp.solve(sp.Eq(cand, 0), r_uv_sym)
        if sol:
            TH_form = "r_uv = " + sp.sstr(sp.simplify(sol[0]))
            break
log(f"  (TH)  {TH_form if TH_form else 'не решено — см. структуру: ' + sp.sstr(sp.simplify(TH_eq))}")

# Замкнутое уравнение на r_uv: UV-форма уже не содержит omega_uv (чистая геометрия)
if UV_form is not None:
    if UV_form.has(omega_uv_sym) and TH_form is not None and not isinstance(TH_form, str):
        UV_closed = sp.simplify(UV_form.subs(omega_uv_sym, TH_form))
    else:
        UV_closed = UV_form
    log(f"  (UV∘TH)  r_uv = {UV_closed}")
else:
    UV_closed = None

# ------------------------------------------------------------------------------
# 4. Машинная проверка: точное решение Робертса–Оширо (Burko 1996, ур. (15)-(16))
# ------------------------------------------------------------------------------
log("")
log("=" * 78)
log("ШАГ 4. Проверка: решение Робертса–Оширо (исправл. форма, Burko gr-qc/9608061)")
log("=" * 78)
log("  r^2 = 1/4 [ (1-4s^2) v^2 - 2 u v + u^2 ],   Phi = 1/2 ln| 1 - 4s/(1+2s-u/v) |")
log("  (s = const — параметр решения; alpha = 1)")

# Численная проверка с mpmath 50 знаков в случайных точках
import mpmath as mp

mp.mp.dps = 50

K2 = mp.mpf(2)  # kappa = 8piG = 2  (система единиц 4piG = 1)


def roberts_fields(uu, vv, sigma):
    """Точное решение Робертса–Оширо: возвращает r, r_u, r_v, r_uu, r_vv, r_uv, Phi, Phi_u, Phi_v, Phi_uv."""
    u_m, v_m = mp.mpf(uu), mp.mpf(vv)
    s = mp.mpf(sigma)
    r2 = mp.mpf(1) / 4 * ((1 - 4 * s**2) * v_m**2 - 2 * u_m * v_m + u_m**2)
    rr = mp.sqrt(r2)
    r_u = (-2 * v_m + 2 * u_m) / 4 / (2 * rr)
    r_v = (2 * (1 - 4 * s**2) * v_m - 2 * u_m) / 4 / (2 * rr)
    # вторые производные из r^2: (r^2)_uu = 1/2, (r^2)_uv = -1/2, (r^2)_vv = (1-4s^2)/2
    # r_uu = (r^2)_uu/(2r) - (r_u)^2/r
    r_uu = (mp.mpf(1) / 2) / (2 * rr) - r_u**2 / rr
    r_vv = ((1 - 4 * s**2) / 2) / (2 * rr) - r_v**2 / rr
    r_uv = (-mp.mpf(1) / 2) / (2 * rr) - r_u * r_v / rr
    # Phi = 1/2 ln|1 - 4s/D|, D = 1+2s - u/v = (v(1+2s) - u)/v
    # dPhi/du = 1/2 [D_u/(D-4s) - D_u/D],  D_u = -1/v
    # dPhi/dv = 1/2 [D_v/(D-4s) - D_v/D],  D_v = 1 + u/v^2
    def Phi_f(x, y):
        Dxy = 1 + 2 * s - x / y
        return mp.mpf(1) / 2 * mp.log(abs(1 - 4 * s / Dxy))

    def Phi_u_f(x, y):
        Dxy = 1 + 2 * s - x / y
        return mp.mpf(1) / 2 * ((-1 / y) / (Dxy - 4 * s) - (-1 / y) / Dxy)

    def Phi_v_f(x, y):
        Dxy = 1 + 2 * s - x / y
        D_v = x / y**2
        return mp.mpf(1) / 2 * (D_v / (Dxy - 4 * s) - D_v / Dxy)

    # Phi_uv = d(Phi_v)/du  (не d/dv — это было бы Phi_vv!)
    Phi_uv_val = mp.diff(lambda xx: Phi_v_f(xx, v_m), u_m)
    Phi_uu_val = mp.diff(lambda xx: Phi_u_f(xx, v_m), u_m)
    Phi_vv_val = mp.diff(lambda yy: Phi_v_f(u_m, yy), v_m)
    return dict(r=rr, r_u=r_u, r_v=r_v, r_uu=r_uu, r_vv=r_vv, r_uv=r_uv,
                Phi=Phi_f(u_m, v_m), Phi_u=Phi_u_f(u_m, v_m), Phi_v=Phi_v_f(u_m, v_m),
                Phi_uu=Phi_uu_val, Phi_vv=Phi_vv_val, Phi_uv=Phi_uv_val,
                omega=mp.mpf(0), omega_u=mp.mpf(0), omega_v=mp.mpf(0), omega_uv=mp.mpf(0))


def residuals_1p1(f):
    """Невязки выведенной (SymPy) системы при omega = 0 (alpha = 1).
    Правые части берутся непосредственно из SymPy-форм C1_form / C2_form / UV_closed,
    так что тест автоматически согласован с выводом ШАГА 3.
    """
    res = {}
    # (SC) Phi_uv + (r_u Phi_v + r_v Phi_u)/r = 0
    res["SC"] = f["Phi_uv"] + (f["r_u"] * f["Phi_v"] + f["r_v"] * f["Phi_u"]) / f["r"]
    # (C1): r_uu - C1_form(r, Phi, omega=0) = 0
    res["C1"] = f["r_uu"] - eval_sym(C1_form, f)
    # (C2): r_vv - C2_form(...)
    res["C2"] = f["r_vv"] - eval_sym(C2_form, f)
    # (UV): r_uv - UV_closed(...)
    res["UV"] = f["r_uv"] - eval_sym(UV_closed, f) if UV_closed is not None else mp.mpf(0)
    # (TH): omega_uv - TH_form(...) — только если TH_form — выражение (не строка)
    if TH_form is not None and not isinstance(TH_form, str):
        res["TH"] = f["omega_uv"] - eval_sym(TH_form, f)
    return res


# Сопоставление sympy-атомов ключам численного словаря
_SYM_TO_KEY = {
    r: "r", r.diff(u): "r_u", r.diff(v): "r_v",
    r.diff(u, 2): "r_uu", r.diff(v, 2): "r_vv", r.diff(u, v): "r_uv",
    Phi: "Phi", Phi.diff(u): "Phi_u", Phi.diff(v): "Phi_v",
    Phi.diff(u, 2): "Phi_uu", Phi.diff(v, 2): "Phi_vv", Phi.diff(u, v): "Phi_uv",
    omega: "omega", omega.diff(u): "omega_u", omega.diff(v): "omega_v",
    omega.diff(u, v): "omega_uv",
    kappa: "kappa",
}


def eval_sym(expr, fval):
    """Численная оценка sympy-выражения по словарю значений полей (mpmath → 40 знаков).

    Отсутствующие ключи трактуются как нули (для теста Робертса omega ≡ 0),
    кроме kappa — берётся глобальная константа K2.
    """
    subs_map = {}
    for sym, key in _SYM_TO_KEY.items():
        if expr.has(sym):
            if key in fval:
                val = fval[key]
            elif key == "kappa":
                val = K2
            else:
                val = mp.mpf(0)
            subs_map[sym] = sp.Float(mp.nstr(val, 40), 40)
    return sp.N(expr.subs(subs_map), 40)


# Тестовые точки: избегаем u/v близких к сингулярностям решения (u = v(1+2s), u = v(1+2s-4s))
test_points = [(mp.mpf("0.13"), mp.mpf("1.7"), mp.mpf("0.2")),
               (mp.mpf("-0.8"), mp.mpf("2.3"), mp.mpf("-0.3")),
               (mp.mpf("0.5"), mp.mpf("3.1"), mp.mpf("0.15"))]

roberts_ok = True
max_res = mp.mpf(0)
for (uu, vv, ss) in test_points:
    f = roberts_fields(uu, vv, ss)
    res = residuals_1p1(f)
    for k, x in res.items():
        log(f"    [{k}] невязка = {mp.nstr(abs(x), 3)}")
    m = max(abs(x) for x in res.values())
    max_res = max(max_res, m)
    log(f"  точка (u,v,s) = ({uu}, {vv}, {ss}): max|невязка| = {mp.nstr(m, 3)}")
    if m > mp.mpf("1e-25"):
        roberts_ok = False

log(f"  ИТОГ: решение Робертса–Оширо удовлетворяет выведенной системе: "
    f"{'ДА (макс. невязка ' + mp.nstr(max_res, 3) + ')' if roberts_ok else 'НЕТ'}")

# Дополнительно: проверка уравнений Burko (alpha = 1): E1: r_uv + (r_u r_v + 1/4)/r = 0
burko_ok = True
for (uu, vv, ss) in test_points:
    f = roberts_fields(uu, vv, ss)
    res_burko = f["r_uv"] + (f["r_u"] * f["r_v"] + mp.mpf(1) / 4) / f["r"]
    if abs(res_burko) > mp.mpf("1e-40"):
        burko_ok = False
        log(f"  Burko E1 невязка в точке ({uu},{vv},{ss}): {mp.nstr(res_burko, 5)}")
log(f"  Проверка формы Burko E1 (r_uv + (r_u r_v + 1/4)/r = 0): {'OK' if burko_ok else 'НЕТ'}")

# ------------------------------------------------------------------------------
# 5. Сохранение результатов
# ------------------------------------------------------------------------------
results = {
    "title": "Symbolic derivation: Hilbert action -> double-null Einstein-scalar system",
    "metric": "ds^2 = -alpha(u,v)^2 du dv + r(u,v)^2 dOmega^2",
    "action": "S = (1/2kappa) int sqrt(-g) R + S_m,  S_m = -1/2 int sqrt(-g) (grad Phi)^2",
    "hilbert_tensor": "T_{mu nu} = Phi_mu Phi_nu - 1/2 g_{mu nu} (grad Phi)^2",
    "gradPhi2": sp.sstr(grad2),
    "T_uv": sp.sstr(T[(0, 1)]),
    "T_uu": sp.sstr(T[(0, 0)]),
    "T_vv": sp.sstr(T[(1, 1)]),
    "boxPhi": sp.sstr(boxPhi),
    "hilbert_identity": {str(nu): sp.sstr(expr) for nu, expr in hilbert_check.items()},
    "system_solved": {
        "C1_r_uu": sp.sstr(C1_form) if C1_form is not None else None,
        "C2_r_vv": sp.sstr(C2_form) if C2_form is not None else None,
        "UV_r_uv": sp.sstr(UV_form) if UV_form is not None else None,
        "TH_omega_uv": sp.sstr(TH_form) if TH_form is not None else None,
        "UV_closed_r_uv": sp.sstr(UV_closed) if UV_closed is not None else None,
    },
    "checks": {
        "R_phiphi_spherical": bool(check_sph == 0),
        "roberts_solution_ok": bool(roberts_ok),
        "roberts_max_residual": mp.nstr(max_res, 5),
        "burko_E1_ok": bool(burko_ok),
    },
    "units": "kappa = 8 pi G; numerical code uses kappa = 2 (4 pi G = 1, Burko normalization)",
    "runtime_seconds": round(time.time() - t_start, 1),
}

with open(os.path.join(RESULTS_DIR, "derivation_results.json"), "w", encoding="utf-8") as fh:
    json.dump(results, fh, ensure_ascii=False, indent=2)

with open(os.path.join(RESULTS_DIR, "derivation_log.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(log_lines))

log("")
log(f"Готово за {results['runtime_seconds']} c. Результаты: results/derivation_results.json")
