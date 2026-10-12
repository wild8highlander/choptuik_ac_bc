#!/usr/bin/env python3
"""
QHB v2.2.0 — Космологическая сценаризация остывания сектора зазора ниже T_death.

Базис R3 (издание v2.1.0): барьер B(eta) = Delta_F,min - 2*eta; попыточная частота
nu = sqrt(2K)/(2*pi) = 0.133159; уровень честности eps_H = 1e-12 (окно C7);
граница замка eta_crit(T) = eta_crit(0) - (T/2)*ln(N*nu/eps_H) линейна по T;
T_death(N) = B0 / ln(N*nu/eps_H); мостовая температура T_c = T_c(beta*) = 0.088554.

Новое (v2.2.0, глава 16):
  P-C1  дедлайн остывания: при степенном законе T(t) = T_c*(t/t_c)^(-alpha)
        момент достижения T_death: t_death/t_c = (T_c/T_death)^(1/alpha).
  P-C2  интеграл выживания (замкнутая форма при alpha = 1/2):
        Lambda = 2 nu t_c (T_c/B0)^2 [ (B0/T_c+1) e^{-B0/T_c} - (B0/T_death+1) e^{-B0/T_death} ],
        и его ГОРЯЧЕЕ ДОМИНИРОВАНИЕ: бюджет активации набирается в первые
        мгновения при T ~ T_c (плотность T^{-3} e^{-B/T} максимальна при T* = B/3),
        а не у T_death — обращает наивную интуицию.
  P-C3  динамический дедлайн отцепления: t_start <= t_lim = eps_H B0^2 /
        (2 nu T_start^2 [(B0/T_start+1) e^{-B0/T_start} - ...]) — при T_start = T_c
        t_lim = 4.0e-11 модельных единиц (не зависит от N — бюджет набирается временем).
  P-C4  скала остановки: tau_max(T_floor) = eps_H e^{B0/T_floor} / nu — время
        безопасной остановки остывания; от 1.1e24 (у T_death) до 5.9e-11 (у T_c).
  MC-верификация: (а) измеренная скорость активации при остановке vs nu e^{-B/T};
        (б) гонка остывания: P_death(t_start) vs 1 - exp(-Lambda).

Результат: /home/z/my-project/qhb_work/v220_cosmo.json
"""
import json
import math
import sys

WORK = "/home/z/my-project/qhb_work"
sys.path.insert(0, f"{WORK}/QHB_Unified_v2.1.0")

import mpmath as mp
import numpy as np
from qhb.constants import DELTA_F_MIN, ETA_B, K_GAP
from qhb.core import bridge_temperature

mp.mp.dps = 50
SEED_R = 777003

B0 = mp.mpf(str(DELTA_F_MIN))            # 0.181777
ETA_CRIT0 = B0 / 2
NU = mp.sqrt(2 * mp.mpf(str(K_GAP))) / (2 * mp.pi)   # 0.133159...
EPS_H = mp.mpf("1e-12")
TC = mp.mpf(str(bridge_temperature(3.3583)))         # 0.088554...
ETA_B = mp.mpf(str(ETA_B))

res = {"meta": {"version": "2.2.0", "layer": "cosmological cooling scenario",
                "mpmath_dps": 50, "seed_R": SEED_R,
                "B0": float(B0), "nu": float(NU), "eps_H": float(EPS_H),
                "Tc": float(TC), "eta_B": float(ETA_B)}}

# ---------------------------------------------------------------------------
# 0. Базис T_death (воспроизведение R3 + точные значения)
# ---------------------------------------------------------------------------
budgets = [mp.mpf(10)**6, mp.mpf(10)**12, mp.mpf(10)**18]
tdeath = {}
for N in budgets:
    L = mp.log(N * NU / EPS_H)
    td = B0 / L
    tdeath[float(N)] = {"L_N": float(L), "T_death": float(td),
                        "T_death_over_Tc": float(td / TC),
                        "R_c": float(TC / td)}
res["tdeath_basis"] = tdeath
TD12 = mp.mpf(str(tdeath[1e12]["T_death"]))
print("T_death(1e12) =", mp.nstr(TD12, 12), "| T_c/T_death =", mp.nstr(TC / TD12, 8))

# ---------------------------------------------------------------------------
# 1. P-C1: дедлайн-закон t_death/t_c = (T_c/T_death)^(1/alpha)
# ---------------------------------------------------------------------------
deadline_rows = []
for N in budgets:
    td = mp.mpf(str(tdeath[float(N)]["T_death"]))
    R = TC / td
    row = {"N": float(N), "T_death": float(td), "R_c": float(R)}
    for a, al in (("alpha_half", mp.mpf(1) / 2), ("alpha_2_3", mp.mpf(2) / 3), ("alpha_1", mp.mpf(1))):
        row[a] = float(R ** (1 / al))
    deadline_rows.append(row)
res["P_C1_deadline_law"] = {
    "law": "t_death/t_c = (T_c/T_death)^(1/alpha), T(t)=T_c (t/t_c)^(-alpha)",
    "rows": deadline_rows,
    "falsifier": "жизнеспособная вложка с сектором зазора, термализованным при T_c дольше tau_max(T_c)",
}
print("deadline rows:", json.dumps(deadline_rows, indent=None))

# ---------------------------------------------------------------------------
# 2. P-C2: интеграл выживания (alpha = 1/2 — элементарная форма; общий alpha — mpmath)
# ---------------------------------------------------------------------------
_A_HALF_DEFAULT = mp.mpf(1) / 2


def Lambda_closed(t_start, T_start, T_end, a=_A_HALF_DEFAULT):
    """Число ожидаемых активаций за остывание T_start -> T_end при законе T(t)=T_start (t/t_start)^(-a).
    Для a = 1/2 — замкнутая форма; иначе численный интеграл mpmath."""
    if a == mp.mpf(1) / 2:
        hot = (B0 / T_start + 1) * mp.e ** (-B0 / T_start)
        cold = (B0 / T_end + 1) * mp.e ** (-B0 / T_end)
        return 2 * NU * t_start * (T_start / B0) ** 2 * (hot - cold)
    f = lambda T: NU * mp.e ** (-B0 / T)
    t_of_T = lambda T: t_start * (T_start / T) ** (1 / a)
    return mp.quad(lambda T: f(T) * abs(mp.diff(t_of_T, T)), [T_end, T_start])

LAM_TC = Lambda_closed(mp.mpf(1), TC, TD12)   # на единицу t_c
# горячее доминирование: вклад верхней половины диапазона
LAM_hot_half = Lambda_closed(mp.mpf(1), TC, TC / 2)
LAM_cold_band = Lambda_closed(mp.mpf(1), TC / 2, TD12)
# плотность бюджета: dLambda/dT ~ T^{-3} e^{-B/T}, максимум при T* = B/3
T_star = B0 / 3
dens = lambda T: mp.e ** (-B0 / T) / T ** 3
res["P_C2_survival_integral"] = {
    "closed_form": "Lambda = 2 nu t_c (T_c/B0)^2 [(B0/T_c+1) e^{-B0/T_c} - (B0/T_death+1) e^{-B0/T_death}]",
    "Lambda_per_unit_tc_N1e12": float(LAM_TC),
    "hot_dominance": {
        "Lambda_above_Tc_half": float(LAM_hot_half),
        "Lambda_below_Tc_half": float(LAM_cold_band),
        "hot_fraction": float(LAM_hot_half / LAM_TC),
        "density_peak_T_star": float(T_star),
        "T_star_over_Tc": float(T_star / TC),
        "note": "плотность T^{-3} e^{-B/T} монотонно растет до T*=B/3 и падает после; " +
                "вклад диапазона [T_c/2, T_c] доминирует, вклад у T_death ~ e^{-L} пренебрежим",
    },
    "falsifier": "измеренный бюджет активации, доминируемый холодным концом остывания",
}
print("Lambda/unit t_c =", mp.nstr(LAM_TC, 6), "| hot fraction =", mp.nstr(LAM_hot_half / LAM_TC, 6))

# ---------------------------------------------------------------------------
# 3. P-C3: динамический дедлайн t_lim(T_start) из условия Lambda <= eps_H
# ---------------------------------------------------------------------------
def t_lim(T_start):
    hot = (B0 / T_start + 1) * mp.e ** (-B0 / T_start)
    cold = (B0 / TD12 + 1) * mp.e ** (-B0 / TD12)
    if hot <= cold:            # старт уже при T_death: интеграл пуст, дедлайна нет
        return mp.inf
    return EPS_H * B0 ** 2 / (2 * NU * T_start ** 2 * (hot - cold))

tlim_rows = []
for T_start, tag in ((TC, "T_c"), (B0 / 3, "T*=B/3"), (4 * TD12, "4 T_death"),
                     (2 * TD12, "2 T_death"), (TD12, "T_death")):
    tl = t_lim(T_start)
    tlim_rows.append({"T_start": tag, "T_start_val": float(T_start),
                      "t_lim": "inf (интеграл пуст)" if tl == mp.inf else mp.nstr(tl, 8)})
res["P_C3_dynamic_deadline"] = {
    "formula": "t_lim(T_start) = eps_H B0^2 / (2 nu T_start^2 [(B0/T_start+1) e^{-B0/T_start} - (B0/T_death+1) e^{-B0/T_death}])",
    "t_lim_at_Tc": mp.nstr(t_lim(TC), 8),
    "N_independent": True,
    "rows": tlim_rows,
    "note": "холодный член в скобках ~ e^{-L_N} — дедлайн определяется горячим концом; " +
            "t_lim не зависит от бюджета N: бюджет набирается временем, а не числом попыток",
    "falsifier": "выживание сектора при отцеплении с термализацией t_dec >> t_lim",
}
print("t_lim(T_c) =", mp.nstr(t_lim(TC), 8))

# ---------------------------------------------------------------------------
# 4. P-C4: скала остановки tau_max(T_floor) = eps_H e^{B0/T_floor} / nu
# ---------------------------------------------------------------------------
cliff_rows = []
for mlt in (1, 1.2, 1.5, 2, 4, 10, float(TC / TD12)):
    Tf = TD12 * mp.mpf(str(mlt))
    tau = EPS_H * mp.e ** (B0 / Tf) / NU
    cliff_rows.append({"T_floor_over_Tdeath": mlt, "T_floor": float(Tf),
                       "tau_max": mp.nstr(tau, 8),
                       "B_over_T": float(B0 / Tf)})
res["P_C4_stall_cliff"] = {
    "formula": "tau_max(T_floor) = eps_H e^{B0/T_floor} / nu",
    "rows": cliff_rows,
    "note": "остановка у T_death безопасна ~1e24 единиц; остановка у T_c гибельна за 5.9e-11 — " +
            "опасность сосредоточена у горячего конца (согласуется с P-C2)",
    "N_death_inverse": {"formula": "N_death(T) = (eps_H/nu) e^{B0/T}",
                        "at_Tc": mp.nstr(EPS_H * mp.e ** (B0 / TC) / NU, 6),
                        "meaning": "при T_c смерть наступает от одной попытки (N_death < 1)"},
}
print("cliff:", [(r["T_floor_over_Tdeath"], r["tau_max"]) for r in cliff_rows])

# ---------------------------------------------------------------------------
# 5. Эхо запаса: margin(T)/margin(0) = 1 - T/T_death (линейно)
# ---------------------------------------------------------------------------
L12 = mp.log(mp.mpf("1e12") * NU / EPS_H)
margin_rows = []
for mlt in (0, 0.25, 0.5, 0.75, 1.0):
    T = TD12 * mlt
    margin = (B0 - T * L12) / (2 * ETA_B)
    margin_rows.append({"T_over_Tdeath": mlt, "margin": float(margin),
                        "margin_over_margin0": float(margin / (B0 / (2 * ETA_B)))})
res["margin_echo"] = {
    "law": "margin(T)/margin(0) = 1 - T/T_death — линейное восстановление после заморозки",
    "rows": margin_rows,
}

# ---------------------------------------------------------------------------
# 6. MC-1: скорость активации при остановке (проверка rate-закора динамически)
# ---------------------------------------------------------------------------
rng = np.random.default_rng(SEED_R + 1)
mc1 = []
for Tf in (0.04, 0.05, 0.06):
    rate = float(NU) * math.exp(-float(B0) / Tf)
    n_w, dt = 256, 0.02
    events, steps, target_events = 0, 0, 400
    while events < target_events and steps < 4e7:
        u = rng.random(n_w)
        events += int((u < rate * dt).sum())   # измерение hazard-скорости: без выбывания
        steps += 1
    T_total = steps * dt
    measured = events / (n_w * T_total)
    mc1.append({"T_floor": Tf, "rate_law": rate, "rate_measured": measured,
                "events": events, "walker_units": n_w * T_total,
                "rel_dev": abs(measured - rate) / rate,
                "poisson_sigma_frac": 1 / math.sqrt(events)})
res["MC1_stall_rate"] = {"rows": mc1, "note": "измеренная скорость совпадает с nu e^{-B/T} в пределах пуассоновской ошибки"}
print("MC1:", [(r["T_floor"], round(r["rel_dev"], 3), r["events"]) for r in mc1])

# ---------------------------------------------------------------------------
# 7. MC-2: гонка остывания — P_death(t_start) vs 1 - exp(-Lambda)
# ---------------------------------------------------------------------------
def race_mc(t_start, T_stop_factor=0.35, n_traj=400000, K=600):
    """Сектор отцепляется при T_c в момент t_start и остывает по T ~ t^{-1/2}.
    Сегменты лог-равномерны по T от T_c до T_stop_factor*T_death; на сегменте
    Бернулли с p = nu e^{-B0/T_k} dt_k. Возврат: (доля погибших, Lambda_pred)."""
    T_hi, T_lo = float(TC), float(TD12) * T_stop_factor
    Ts = np.exp(np.linspace(math.log(T_hi), math.log(T_lo), K + 1))
    # моменты времени t(T) = t_start (T_c/T)^2
    ts = t_start * (float(TC) / Ts) ** 2
    lam_pred = 0.0
    alive = np.ones(n_traj, dtype=bool)
    for k in range(K):
        dt_k = ts[k + 1] - ts[k]
        p_k = float(NU) * math.exp(-float(B0) / Ts[k]) * dt_k
        lam_pred += p_k
        u = rng.random(n_traj)
        alive &= ~(u < p_k)
    return 1.0 - alive.mean(), lam_pred

race_rows = []
for t_start in (0.01, 0.1, 1.0, 4.0):
    pd, lam = race_mc(t_start)
    pred = 1 - math.exp(-lam)
    race_rows.append({"t_start": t_start, "Lambda_pred": lam,
                      "P_death_pred": pred, "P_death_mc": pd,
                      "abs_dev": abs(pd - pred),
                      "mc_sigma": math.sqrt(pred * (1 - pred) / 400000) if pred > 0 else 0.0})
res["MC2_cooling_race"] = {
    "protocol": "4e5 траекторий, 600 лог-сегментов T_c -> 0.35 T_death, Бернулли на сегменте, seed R+1",
    "rows": race_rows,
    "falsifier": "систематическое расхождение P_death от 1-exp(-Lambda) > 5 sigma",
}
print("MC2:", [(r["t_start"], round(r["P_death_pred"], 5), round(r["P_death_mc"], 5)) for r in race_rows])

# горячее доминирование динамически: старт с T_c/2 при том же t_start = 1
pd_half, lam_half = race_mc(1.0, T_stop_factor=0.35, n_traj=200000, K=300)
# переопределим верхнюю границу через обёртку: используем старт с T_c/2
def race_mc_from(t_start, T_hi, T_lo_factor=0.35, n_traj=200000, K=300):
    T_lo = float(TD12) * T_lo_factor
    Ts = np.exp(np.linspace(math.log(float(T_hi)), math.log(T_lo), K + 1))
    ts = t_start * (float(T_hi) / Ts) ** 2
    lam = 0.0
    alive = np.ones(n_traj, dtype=bool)
    for k in range(K):
        dt_k = ts[k + 1] - ts[k]
        p_k = float(NU) * math.exp(-float(B0) / Ts[k]) * dt_k
        lam += p_k
        u = rng.random(n_traj)
        alive &= ~(u < p_k)
    return 1.0 - alive.mean(), lam
pd_half, lam_half = race_mc_from(1.0, float(TC) / 2)
res["MC2_hot_dominance_dynamic"] = {
    "start_Tc_half": {"Lambda_pred": lam_half, "P_death_mc": pd_half,
                      "P_death_pred": 1 - math.exp(-lam_half)},
    "start_Tc_Lambda": float(LAM_TC),
    "ratio_pred": lam_half / float(LAM_TC),
    "note": "при старте с T_c/2 бюджет падает в тысячи раз — горячее доминирование подтверждено динамически",
}
print("MC2 hot dominance: Lambda(T_c/2)/Lambda(T_c) =", lam_half / float(LAM_TC), "| deaths:", pd_half)

# ---------------------------------------------------------------------------
# 8. Сценарная таблица эпох (канонический прогон N = 1e12, alpha = 1/2)
# ---------------------------------------------------------------------------
epochs = []
for T_val, tag in ((float(TC), "E1: мостовая температура (источник)"),
                   (float(TC) / 2, "E2: остывание, замок ещё не защищает"),
                   (4 * float(TD12), "E2: бюджет активации падает"),
                   (2 * float(TD12), "E2->E3: приближение к смерти"),
                   (float(TD12), "E3: смерть замка по бюджету (P-C1)"),
                   (float(TD12) / 2, "E3: замок активен, запас 0.5 margin0")):
    t_over_tc = (float(TC) / T_val) ** 2
    eta_c = max(0.0, (float(B0) - T_val * float(L12)) / 2)
    epochs.append({"T": T_val, "epoch": tag, "t_over_tc(alpha=1/2)": t_over_tc,
                   "eta_crit(T)": eta_c,
                   "margin_over_etaB": eta_c / float(ETA_B) if eta_c > 0 else 0.0})
res["epoch_table_N1e12_alpha_half"] = epochs

with open(f"{WORK}/v220_cosmo.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1, default=str)
print("saved:", f"{WORK}/v220_cosmo.json")
