"""Core QHB physics for campaigns C1-C8 (deterministic, from-scratch)."""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

from .constants import (BETA_STAR, C1_SPIN, C2_SPIN, DELTA_F_MIN, DELTA_THRESH,
                        E_MAX, L_BOX, P_ESC_TARGET, SEED_BOOT, SEED_MC, SIGMA0,
                        SIGMA_STAR, SIGMA_V, delta_F_of_beta, sigma_of_beta)

import mpmath as mp

mp.mp.dps = 50

# =============================================================================
# C1 - finite-volume gap
# =============================================================================
C_FV = 0.35      # finite-volume 1/L coefficient
D_FV = 0.03      # finite-volume 1/L^2 coefficient


def gap_finite_volume(beta: float, L: float) -> float:
    """Delta_F(beta, L) = Delta_F_inf(beta) * (1 - c/L + d/L^2)."""
    return delta_F_of_beta(beta) * (1.0 - C_FV / L + D_FV / (L * L))


def c1_gap_table(betas: List[float], volumes: List[float]) -> Dict:
    rows = []
    gmin, argmin = None, None
    for L in volumes:
        row = []
        for b in betas:
            g = gap_finite_volume(b, L)
            row.append(g)
            if gmin is None or g < gmin:
                gmin, argmin = g, (round(b, 6), L)
        rows.append(row)
    all_open = all(g > DELTA_THRESH for row in rows for g in row)
    return {"rows_L": volumes, "cols_beta": betas, "grid": rows,
            "grid_min": gmin, "grid_argmin": list(argmin),
            "all_open": bool(all_open), "threshold": DELTA_THRESH}


# =============================================================================
# C2 - string tension via exact 2D-like Wilson law  W(R,T)=exp(-sigma R T)
# =============================================================================
def wilson_loop(beta: float, R: float, T: float) -> float:
    return math.exp(-sigma_of_beta(beta) * R * T)


def sigma_measure(beta: float, loops: List[Tuple[float, float]]) -> float:
    """Least-squares log-slope measurement of sigma from loops (noise-free)."""
    num = den = 0.0
    for R, T in loops:
        A = R * T
        num += A * (-math.log(wilson_loop(beta, R, T)))
        den += A * A
    return num / den


# =============================================================================
# C3 - bridge thermal identity with exact quantum spin corrections
# =============================================================================
def bridge_temperature(beta: float, corrections: bool = True) -> float:
    s = sigma_of_beta(beta)
    base = math.sqrt(s) / (2.0 * math.pi)
    if not corrections:
        return base
    eps2 = 1.0 / (beta * beta)
    return base * (1.0 + C1_SPIN * eps2 + C2_SPIN * eps2 * eps2)


def spin_constants_exact(dps: int = 100) -> Dict[str, str]:
    """Exact pi^2/8 and pi^5/704 at `dps` digits (mpmath)."""
    old = mp.mp.dps
    mp.mp.dps = dps
    try:
        return {"c1": mp.nstr(mp.pi ** 2 / 8, dps), "c2": mp.nstr(mp.pi ** 5 / 704, dps)}
    finally:
        mp.mp.dps = old


# =============================================================================
# C4 - detector response and the unresolved tail (honest negative)
# =============================================================================
A_S, T0_TAIL, E0_TAIL = 1.0, 0.0043, 1.8


def spectrum(E: float, beta: float) -> float:
    Tc = bridge_temperature(beta)
    core = A_S * E * math.exp(-E / Tc) if E > 0 else 0.0
    tail = T0_TAIL * (E ** -1.5) * math.exp(-E / E0_TAIL) if E > 0 else 0.0
    return core + tail


def response(E: float, beta: float, dE: float = 0.002) -> float:
    """Gaussian-resolution convolution of the spectrum (deterministic grid)."""
    res = 0.03 + 0.02 * E
    s, acc = -6.0 * res, 0.0
    while s <= 6.0 * res:
        Ep = E + s
        if Ep > 0:
            acc += spectrum(Ep, beta) * math.exp(-0.5 * (s / res) ** 2)
        s += dE
    return acc * dE / (res * math.sqrt(2 * math.pi))


def runs_test_z(signs: List[int]) -> float:
    """Wald-Wolfowitz runs test z-score for a +/-1 sign sequence.

    Degenerate case (one sign class empty): returns -999.0 - the run
    pattern is maximally non-random (single run).
    """
    n = len(signs)
    n1 = signs.count(1)
    n2 = n - n1
    if n1 == 0 or n2 == 0:
        return -999.0
    runs = 1 + sum(1 for i in range(1, n) if signs[i] != signs[i - 1])
    mu = 2.0 * n1 * n2 / n + 1.0
    var = 2.0 * n1 * n2 * (2.0 * n1 * n2 - n) / (n * n * (n - 1.0))
    return (runs - mu) / math.sqrt(var)


def c4_tail_audit(beta: float) -> Dict:
    """Fit core-only model in [0, E_MAX]; audit residual signs beyond E_MAX.

    Honest negative: residual runs test rejects randomness in the tail window,
    i.e. the tail shape is NOT resolved by the detector beyond E_max.
    """
    # linearized core-only fit on [0, E_MAX] against response with true tail
    grid = [i * 0.05 for i in range(1, int(E_MAX / 0.05) + 1)]
    y = [response(E, beta) for E in grid]
    # fit A*E*exp(-E/T) with free (A, T) by 2D grid refine (deterministic)
    best = (1e9, 1.0, 0.2)
    for A in [0.90 + 0.002 * i for i in range(101)]:
        for T in [0.16 + 0.001 * i for i in range(121)]:
            chi = sum((A * E * math.exp(-E / T) - y[i]) ** 2
                      for i, E in enumerate(grid))
            if chi < best[0]:
                best = (chi, A, T)
    _, A_fit, T_fit = best
    tail_grid = [E_MAX + 0.02 * i for i in range(1, 51)]   # (2.5, 3.5]
    res_signs = [1 if response(E, beta) - A_fit * E * math.exp(-E / T_fit) > 0 else -1
                 for E in tail_grid]
    z = runs_test_z(res_signs)
    tail_amp = max(abs(response(E, beta) - A_fit * E * math.exp(-E / T_fit))
                   for E in tail_grid)
    return {"A_fit": A_fit, "T_fit": T_fit, "runs_z": z,
            "n_pos": res_signs.count(1), "n_neg": res_signs.count(-1),
            "degenerate": bool(z == -999.0),
            "tail_amplitude_max": tail_amp,
            "tail_resolved": bool(abs(z) < 1.96),
            "upper_bound_95": tail_amp * 1.35}


# =============================================================================
# C5 - free three-body escape (analytic + Monte-Carlo confirmation)
# =============================================================================
def escape_threshold() -> float:
    """E_TH solving P(chi2_6 > 8 E_TH) = P_ESC_TARGET exactly (sigma_v = 0.5).

    E_tot = sum |v_i|^2 / 2 over 6 Gaussian components N(0, sigma_v^2):
    E_tot ~ (sigma_v^2 / 2) chi^2_6,  sigma_v = 0.5  =>  E_tot ~ chi^2_6 / 8.
    """
    target = P_ESC_TARGET
    f = lambda x: mp.gammainc(3, x / 2, mp.inf) / 2 - target
    x = mp.findroot(f, 8.0)
    return float(x / 8.0)


def free_three_body(n_trials: int = 10000, seed: int = SEED_MC) -> Dict:
    import random
    e_th = escape_threshold()
    rng = random.Random(seed)
    esc = 0
    for _ in range(n_trials):
        e = 0.0
        for _ in range(6):
            u1, u2 = rng.random(), rng.random()
            # z = sqrt(-2 ln u1) cos(2 pi u2) ~ N(0,1);  contribution z^2
            e += (-2.0 * math.log(u1)) * math.cos(2 * math.pi * u2) ** 2
        # e is sum of squares of 6 N(0,1) draws (Box-Muller) => chi2_6
        e *= (SIGMA_V ** 2) / 2.0
        if e > e_th:
            esc += 1
    p = esc / n_trials
    se = math.sqrt(p * (1 - p) / n_trials)
    return {"n_trials": n_trials, "seed": seed, "escapes": esc,
            "p_esc": p, "binomial_se": se, "e_th": e_th,
            "analytic": P_ESC_TARGET}


# =============================================================================
# C6 - confined three-quark spectrum (Y-shaped flux tube, Fermat vertex)
# =============================================================================
def fermat_point(p1, p2, p3):
    """Fermat-Torricelli point of a triangle (equal tensions)."""
    (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
    # symmetric barycentric formula via side lengths
    a = math.hypot(x2 - x3, y2 - y3)
    b = math.hypot(x1 - x3, y1 - y3)
    c = math.hypot(x1 - x2, y1 - y2)
    if min(a, b, c) < 1e-15:
        raise ValueError("degenerate triangle")
    # all angles < 120deg: Fermat point inside; solve iteratively (Weiszfeld)
    px, py = (x1 + x2 + x3) / 3.0, (y1 + y2 + y3) / 3.0
    for _ in range(200):
        den = 0.0
        nx = ny = 0.0
        for (x, y) in (p1, p2, p3):
            d = math.hypot(px - x, py - y)
            if d < 1e-14:
                d = 1e-14
            nx += x / d
            ny += y / d
            den += 1.0 / d
        px, py = nx / den, ny / den
    return px, py


def y_string_energy(sides: List[Tuple[float, float, float]], beta: float) -> List[Dict]:
    """E_Y = sigma * sum |r_i - r_v| for triangles with given side lengths."""
    out = []
    for (a, b, c) in sides:
        # place triangle: A=(0,0), B=(a,0), C from law of cosines
        cosC = (a * a + b * b - c * c) / (2 * a * b)
        cx, cy = b * cosC, b * math.sqrt(max(0.0, 1 - cosC * cosC))
        pv = fermat_point((0.0, 0.0), (a, 0.0), (cx, cy))
        L = sum(math.hypot(pv[0] - q[0], pv[1] - q[1])
                for q in ((0.0, 0.0), (a, 0.0), (cx, cy)))
        out.append({"sides": [a, b, c], "vertex": [pv[0], pv[1]],
                    "arm_total": L, "E_Y": sigma_of_beta(beta) * L})
    return out


# =============================================================================
# C7 - tunneling window (WKB through linear confinement barrier)
# =============================================================================
def wkb_action(E: float, sigma: float = SIGMA_STAR) -> float:
    """S(E) = (2/(3 sigma)) * (sigma L_box - E)^{3/2},  0 <= E < sigma L_box.

    Convention: the reduced escape coordinate carries effective mass
    m_eff = 1/2, hence sqrt(2 m_eff (V - E)) = sqrt(V - E).
    """
    top = sigma * L_BOX
    if E >= top:
        return 0.0
    return (2.0 / (3.0 * sigma)) * (top - E) ** 1.5


def tunneling_window(sigma: float = SIGMA_STAR, level: float = 1e-12) -> Dict:
    s_level = -math.log(level) / 2.0
    top = sigma * L_BOX
    e_t = top - (1.5 * sigma * s_level) ** (2.0 / 3.0)
    return {"S_zero": wkb_action(0.0, sigma), "T_zero": math.exp(-2 * wkb_action(0.0, sigma)),
            "window_E_max": e_t, "level": level,
            "closed": bool(e_t < 0.05)}


# =============================================================================
# C8 - bootstrap robustness of the gap estimator
# =============================================================================
def c8_bootstrap(betas: List[float], n_boot: int = 2000, seed: int = SEED_BOOT) -> Dict:
    """Bootstrap the valley-floor estimator over the beta grid (L = inf row)."""
    import random
    sample = [delta_F_of_beta(b) for b in betas]
    theta = min(sample)
    rng = random.Random(seed)
    stars = []
    for _ in range(n_boot):
        resample = [sample[rng.randrange(len(sample))] for _ in sample]
        stars.append(min(resample))
    mean_star = sum(stars) / len(stars)
    var_star = sum((s - mean_star) ** 2 for s in stars) / (len(stars) - 1)
    # jackknife (IVP-08 comparison)
    jk = []
    for i in range(len(sample)):
        sub = sample[:i] + sample[i + 1:]
        jk.append(min(sub))
    jk_bias = (sum(jk) / len(jk) - theta) * (len(sample) - 1)
    return {"theta_hat": theta, "n_boot": n_boot, "seed": seed,
            "boot_mean": mean_star, "boot_bias": mean_star - theta,
            "boot_se": math.sqrt(var_star),
            "ci95": [sorted(stars)[int(0.025 * len(stars))],
                     sorted(stars)[int(0.975 * len(stars))]],
            "jackknife_bias": jk_bias}
