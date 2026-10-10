"""C11 - classical vortex-triangle anchor (Kirchhoff equations, from scratch).

No external vortex libraries are used.  The layer implements:
  * Kirchhoff point-vortex equations (equal circulations Gamma = 1)
  * RK4 integrator with fixed step
  * exact rigid-rotation solution and its numerical verification
  * Aref invariants I, H, P, L and the boundedness radius 2*sqrt(I)
  * the anchored slow-manifold barrier V*(s) = V* s^2 e^{2-2s} (T13)
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

from .constants import OMEGA, SEED_C11, V_STAR


# -----------------------------------------------------------------------------
# Kirchhoff dynamics
# -----------------------------------------------------------------------------
def velocity_field(pos: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Point-vortex velocity field, equal circulations Gamma = 1."""
    n = len(pos)
    vel = []
    for i in range(n):
        vx = vy = 0.0
        xi, yi = pos[i]
        for j in range(n):
            if i == j:
                continue
            xj, yj = pos[j]
            r2 = (xi - xj) ** 2 + (yi - yj) ** 2
            vx += -(yi - yj) / r2 / (2 * math.pi)
            vy += (xi - xj) / r2 / (2 * math.pi)
        vel.append((vx, vy))
    return vel


def hamiltonian(pos: List[Tuple[float, float]]) -> float:
    h = 0.0
    n = len(pos)
    for i in range(n):
        for j in range(i + 1, n):
            r = math.hypot(pos[i][0] - pos[j][0], pos[i][1] - pos[j][1])
            h += -math.log(r) / (2 * math.pi)
    return h


def rk4_step(pos, dt):
    def add(p, v, s):
        return [(p[i][0] + s * v[i][0], p[i][1] + s * v[i][1]) for i in range(len(p))]
    k1 = velocity_field(pos)
    k2 = velocity_field(add(pos, k1, dt / 2))
    k3 = velocity_field(add(pos, k2, dt / 2))
    k4 = velocity_field(add(pos, k3, dt))
    return [(pos[i][0] + dt / 6 * (k1[i][0] + 2 * k2[i][0] + 2 * k3[i][0] + k4[i][0]),
             pos[i][1] + dt / 6 * (k1[i][1] + 2 * k2[i][1] + 2 * k3[i][1] + k4[i][1]))
            for i in range(len(pos))]


def equilateral(a: float, shift: Tuple[float, float] = (0.0, 0.0)) -> List[Tuple[float, float]]:
    R = a / math.sqrt(3.0)
    return [(shift[0] + R, shift[1]),
            (shift[0] - R / 2, shift[1] + R * math.sqrt(3) / 2),
            (shift[0] - R / 2, shift[1] - R * math.sqrt(3) / 2)]


# -----------------------------------------------------------------------------
# invariants
# -----------------------------------------------------------------------------
def invariants(pos) -> Dict:
    """Aref invariants in the vorticity-centroid frame (P = 0 by construction)."""
    cx = sum(p[0] for p in pos) / len(pos)
    cy = sum(p[1] for p in pos) / len(pos)
    I = sum((p[0] - cx) ** 2 + (p[1] - cy) ** 2 for p in pos)
    H = hamiltonian([(p[0] - cx, p[1] - cy) for p in pos])
    L = 0.0
    # compute velocities once
    vel = velocity_field(pos)
    L = sum(p[0] * vel[i][1] - p[1] * vel[i][0] for i, p in enumerate(pos))
    P = math.hypot(sum(p[0] for p in pos), sum(p[1] for p in pos))
    return {"I": I, "H": H, "L": L, "P": P,
            "radius_bound": 2.0 * math.sqrt(I)}


def max_pairwise(pos) -> float:
    m = 0.0
    for i in range(len(pos)):
        for j in range(i + 1, len(pos)):
            m = max(m, math.hypot(pos[i][0] - pos[j][0], pos[i][1] - pos[j][1]))
    return m


# -----------------------------------------------------------------------------
# C11 campaign pieces
# -----------------------------------------------------------------------------
def rigid_rotation_check(dt: float = 1e-4, T: float = 2.0) -> Dict:
    """Integrate the exact rotating triangle; fit omega from the polar angle."""
    a = 1.0
    pos = equilateral(a)
    R = a / math.sqrt(3.0)
    n_steps = int(round(T / dt))
    ang0 = math.atan2(pos[0][1], pos[0][0])
    p = pos
    for _ in range(n_steps):
        p = rk4_step(p, dt)
    angT = math.atan2(p[0][1], p[0][0])
    # unwrap: total angle should be omega*T (mod 2pi); use continuity of radius
    omega_fit = (angT - ang0)
    while omega_fit < 0:
        omega_fit += 2 * math.pi
    omega_fit /= T
    # more robust: average over all three vortices
    devs = []
    for k in range(3):
        a0 = math.atan2(pos[k][1], pos[k][0])
        aT = math.atan2(p[k][1], p[k][0])
        d = (aT - a0) % (2 * math.pi)
        devs.append(d / T)
    omega_fit = sum(devs) / 3.0
    dev = abs(omega_fit - OMEGA)
    r_drift = abs(math.hypot(p[0][0], p[0][1]) - R)
    return {"omega_fit": omega_fit, "omega_exact": OMEGA, "dev": dev,
            "radius_drift": r_drift, "dt": dt, "T": T}


def aref_boundedness(a0: float, delta: float, T_sim: float, dt: float,
                     seed: int = SEED_C11, theta: float = 0.0) -> Dict:
    """Perturbed triangle with H < 0: motion bounded; measure r_max.

    Exact bound (T12): max pairwise distance <= 2 sqrt(I) for all time;
    the run must stay well below the virtual wall L_box = 12.
    Vortex 1 is displaced by `delta` in direction `theta` from its
    equilateral position (theta = 0 -> radially outward).
    """
    base = equilateral(a0)
    pos = [(base[0][0] + delta * math.cos(theta), base[0][1] + delta * math.sin(theta)),
           base[1], base[2]]
    inv0 = invariants(pos)
    if inv0["H"] >= 0:
        raise ValueError("perturbation must keep H < 0 for boundedness")
    n_steps = int(round(T_sim / dt))
    r_max = max_pairwise(pos)
    p = pos
    for _ in range(n_steps):
        p = rk4_step(p, dt)
        r_max = max(r_max, max_pairwise(p))
    inv1 = invariants(p)
    return {"a0": a0, "delta": delta, "T_sim": T_sim, "dt": dt, "seed": seed,
            "I0": inv0["I"], "H0": inv0["H"], "L0": inv0["L"], "P0": inv0["P"],
            "bound": inv0["radius_bound"], "r_max": r_max,
            "I_drift": abs(inv1["I"] - inv0["I"]),
            "wall": 12.0, "bounded": bool(r_max < 12.0)}


# --- T13: anchored slow-manifold barrier ---------------------------------------
def anchored_potential(s: float) -> float:
    """V(s) = V* s^2 e^{2-2s}: well at s=0, exact maximum V* at s=1."""
    return V_STAR * s * s * math.exp(2.0 - 2.0 * s)


def anchored_escape_scan(n_tr: int = 300, T_sim: float = 200.0, dt: float = 0.01,
                         seed: int = SEED_C11) -> Dict:
    """Sample n_tr trajectories below the barrier; count escapes (expect 0).

    Energy E = V(s0) + sdot0^2/2 with s0 in (0, 0.6), sdot0 in (0, 0.5).
    Escape = s(t) > 3 within T_sim.
    """
    import random
    rng = random.Random(seed)
    escapes = 0
    e_min, e_max = 1e9, -1e9
    for _ in range(n_tr):
        s0 = 0.05 + 0.55 * rng.random()
        sd0 = 0.5 * rng.random()
        E = anchored_potential(s0) + 0.5 * sd0 * sd0
        e_min = min(e_min, E)
        e_max = max(e_max, E)
        s, sd = s0, sd0
        esc = False
        n_steps = int(round(T_sim / dt))
        for _ in range(n_steps):
            # Hamilton s-dot = pd, sddot = -dV/ds, dV/ds = 2 V* e^{2-2s} s (1-s)
            k1s = sd
            k1d = -2 * V_STAR * math.exp(2 - 2 * s) * s * (1 - s)
            k2s = sd + dt / 2 * k1d
            k2d = -2 * V_STAR * math.exp(2 - 2 * (s + dt / 2 * k1s)) * (s + dt / 2 * k1s) * (1 - s - dt / 2 * k1s)
            k3s = sd + dt / 2 * k2d
            k3d = -2 * V_STAR * math.exp(2 - 2 * (s + dt / 2 * k2s)) * (s + dt / 2 * k2s) * (1 - s - dt / 2 * k2s)
            k4s = sd + dt * k3d
            k4d = -2 * V_STAR * math.exp(2 - 2 * (s + dt * k3s)) * (s + dt * k3s) * (1 - s - dt * k3s)
            s += dt / 6 * (k1s + 2 * k2s + 2 * k3s + k4s)
            sd += dt / 6 * (k1d + 2 * k2d + 2 * k3d + k4d)
            if s > 3.0:
                esc = True
                break
        if esc:
            escapes += 1
    return {"n_tr": n_tr, "escapes": escapes, "E_min": e_min, "E_max": e_max,
            "V_star": V_STAR, "all_below_barrier": bool(e_max < V_STAR)}
