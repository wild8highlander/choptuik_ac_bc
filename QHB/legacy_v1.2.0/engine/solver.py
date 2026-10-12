"""
engine/solver.py — the numeric engine of the Quark-Hawking Bridge.

NumPy-only, vectorised over a seeded ensemble of trials.  Three blocks:

  1. trio      — three equal masses, softened Newtonian gravity, RK4
                 (fixed step), optional oscillating geometric wall
                 (the gap standing as a barrier); escape statistics and
                 Benettin largest-Lyapunov exponents.
  2. wu        — stochastic realisation of the linear two-rate pair model
                 (qhb.wu): Poisson births, thinned exponential survival;
                 measures the residual imbalance against the exact
                 closed form.
  3. kepler    — the engine validation anchor: a two-body ellipse with
                 e = 0.5; the measured period must match the Kepler
                 period to the committed RK4 order.

Units: code units G = m = 1.  Determinism: the ONLY randomness is
numpy default_rng(SEED) with SEED committed in qhb/constants.py.
"""
import math

import numpy as np
from qhb.constants import SEED
from qhb.trio import WALL_P, WALL_R, WALL_W

# --- committed engine parameters ---------------------------------------------
SOFT2 = 1e-2          # softening epsilon^2 (code units; honest toy-model choice,
#                      documented in engine/README.md: regularises encounters)
DT = 2e-3             # RK4 step
STEPS = 6000          # t_end = 12
R_ESC = 12.0          # escape radius
R0 = 0.9              # initial position radius bound (violent cluster)
V0_BOUND = 1.8        # initial speed bound (near-escape energies)
N_TRIALS = 300        # ensemble per cell (committed C2)


# ============================================================================
# forces
# ============================================================================
def trio_accel(pos, V0, Omega, t, soft2=SOFT2, R_b=WALL_R, w=WALL_W, p=WALL_P,
               sigma=0.0):
    """Accelerations for an ensemble pos (T,3,2) — softened Newton + wall.

    Wall (when V0 > 0): U(r,t) = V0 (1+cos(Omega t)) s^p, s = max(0,(r-R_b)/w);
    radial inward force F = -dU/dr r-hat, dU/dr = p V0(t) s^{p-1}/w.

    Confining linear core (C7, when sigma > 0): a Cornell-like flux-tube
    term per pair, U_conf(r) = sigma * r_soft,  r_soft = sqrt(r^2 + eps^2);
    the force on i is  F = sigma * d / r_soft  (d = pos_j - pos_i), i.e. a
    constant-magnitude attraction that grows the pair potential linearly
    with separation.  At sigma = 0 the code path is byte-identical to the
    committed v1.0.0 engine (the term simply does not exist there).
    """
    nb = pos.shape[1]
    acc = np.zeros_like(pos)
    for i in range(nb):
        for j in range(nb):
            if i == j:
                continue
            d = pos[:, j, :] - pos[:, i, :]
            r2 = (d * d).sum(axis=1) + soft2
            acc[:, i, :] += d / r2[:, None] ** 1.5
            if sigma > 0.0:
                acc[:, i, :] += sigma * d / np.sqrt(r2)[:, None]
    if V0 > 0.0:
        r = np.sqrt((pos * pos).sum(axis=2))                 # (T,nb)
        s = np.maximum(0.0, (r - R_b) / w)
        amp = V0 * (1.0 + math.cos(Omega * t))
        radial = np.where((r > 1e-300)[:, :, None],
                          pos / np.maximum(r, 1e-300)[:, :, None], 0.0)
        acc -= (p * amp * s ** (p - 1.0) / w)[:, :, None] * radial
    return acc


def total_energy(pos, vel, V0, Omega, t, soft2=SOFT2, R_b=WALL_R, w=WALL_W,
                 p=WALL_P, sigma=0.0):
    """Total energy including the wall potential (T,).

    With sigma > 0 the Cornell-like confining term sigma * r_soft is added
    per pair (the C7 anharmonic toy; see trio_accel).
    """
    kin = 0.5 * (vel * vel).sum(axis=(1, 2))
    pot = np.zeros(pos.shape[0])
    for i in range(3):
        for j in range(i + 1, 3):
            d = pos[:, j, :] - pos[:, i, :]
            r = np.sqrt((d * d).sum(axis=1) + soft2)
            pot -= 1.0 / r
            if sigma > 0.0:
                pot += sigma * r
    if V0 > 0.0:
        r = np.sqrt((pos * pos).sum(axis=2))
        s = np.maximum(0.0, (r - R_b) / w)
        pot += (V0 * (1.0 + math.cos(Omega * t)) * s ** p).sum(axis=1)
    return kin + pot


# ============================================================================
# RK4 ensemble march
# ============================================================================
def trio_run(pos0, vel0, V0=0.0, Omega=0.0, dt=DT, steps=STEPS,
             record_every=0, sigma=0.0):
    """RK4 march of the whole ensemble with EARLY-ESCAPE FREEZING.

    A trial whose any body passes r > R_ESC is frozen at the crossing
    step (flagged escaped) and removed from the force computation —
    the honest stop.  Returns dict with final state, escape mask,
    survivor energy drift, and (optionally) sampled trajectories.
    """
    pos = pos0.copy()
    vel = vel0.copy()
    alive = np.ones(pos.shape[0], dtype=bool)
    escaped_at = np.full(pos.shape[0], -1, dtype=int)
    E0 = total_energy(pos, vel, V0, Omega, 0.0, sigma=sigma)
    traj = [] if record_every else None

    for k in range(steps):
        t = k * dt
        if record_every and k % record_every == 0:
            traj.append(pos.copy())
        P, V = pos[alive], vel[alive]

        def f(state, tt):
            p_, v_ = state
            return v_, trio_accel(p_, V0, Omega, tt, sigma=sigma)

        k1v, k1a = f((P, V), t)
        k2v, k2a = f((P + 0.5 * dt * k1v, V + 0.5 * dt * k1a), t + 0.5 * dt)
        k3v, k3a = f((P + 0.5 * dt * k2v, V + 0.5 * dt * k2a), t + 0.5 * dt)
        k4v, k4a = f((P + dt * k3v, V + dt * k3a), t + dt)
        P = P + (dt / 6.0) * (k1v + 2 * k2v + 2 * k3v + k4v)
        V = V + (dt / 6.0) * (k1a + 2 * k2a + 2 * k3a + k4a)
        pos[alive], vel[alive] = P, V
        # freeze escapees at the crossing step
        r_now = np.sqrt((P * P).sum(axis=2))
        out_now = (r_now > R_ESC).any(axis=1)
        if out_now.any():
            idx_alive = np.where(alive)[0]
            froze = idx_alive[out_now]
            escaped_at[froze] = k
            alive[froze] = False
        if not alive.any():
            break
    E1 = total_energy(pos[alive], vel[alive], V0, Omega, steps * dt,
                      sigma=sigma) \
        if alive.any() else np.array([0.0])
    E0a = E0[alive] if alive.any() else np.array([1.0])
    r_final = np.sqrt((pos * pos).sum(axis=2))
    out = {"pos": pos, "vel": vel, "escaped": escaped_at >= 0,
           "escaped_at": escaped_at,
           "n_alive_end": int(alive.sum()),
           "r_max": r_final.max(axis=1),
           "E_drift_rel": float(np.max(np.abs((E1 - E0a) / np.abs(E0a))))
           if alive.any() else 0.0,
           "E0": E0}
    if traj:
        out["traj"] = np.array(traj)
    return out


def make_ensemble(n_trials=N_TRIALS, seed=SEED, R0=R0, vmax=V0_BOUND,
                  E_min=-0.6, E_max=-0.05):
    """Seeded weakly-bound ensemble: draws are accepted only with

        E_min <= E_total < 0 <= E_max          (and E < 0 strictly),

    i.e. the committed 'weakly bound band' — violent enough that the
    Newtonian trio can in principle sling a member out, bound enough
    that the question is meaningful.  Rejected draws are counted and
    reported (honest bookkeeping).
    """
    rng = np.random.default_rng(seed)
    pos = np.zeros((n_trials, 3, 2))
    vel = np.zeros((n_trials, 3, 2))
    kept = 0
    rejected = 0
    while kept < n_trials:
        ang = rng.uniform(0, 2 * math.pi, size=(3,))
        rad = R0 * np.sqrt(rng.uniform(0, 1, size=(3,)))
        p = np.stack([rad * np.cos(ang), rad * np.sin(ang)], axis=1)
        angv = rng.uniform(0, 2 * math.pi, size=(3,))
        vv = vmax * rng.uniform(0.05, 1.0, size=(3,))
        v = np.stack([vv * np.cos(angv), vv * np.sin(angv)], axis=1)
        # zero total momentum
        v = v - v.mean(axis=0)
        # zero total angular-position drift of the centre of mass
        p = p - p.mean(axis=0)
        E = total_energy(p[None, ...], v[None, ...], 0.0, 0.0, 0.0)[0]
        if E_min <= E < E_max:
            pos[kept], vel[kept] = p, v
            kept += 1
        else:
            rejected += 1
        if kept + rejected > 2000 * n_trials:
            raise RuntimeError("ensemble generation failed (band too narrow)")
    return pos, vel, rejected


# ============================================================================
# Benettin largest-Lyapunov exponent (vectorised tangent per trial)
# ============================================================================
def lyapunov(pos0, vel0, V0=0.0, Omega=0.0, dt=DT, steps=STEPS,
             renorm_every=50, sigma=0.0):
    """Largest Lyapunov exponent per trial (Benettin, one tangent vector)."""
    pos = pos0.copy()
    vel = vel0.copy()
    Tn = pos.shape[0]
    dpos = np.zeros_like(pos)
    dvel = np.zeros_like(vel)
    # one distinct random unit tangent per trial
    rng = np.random.default_rng(SEED + 1)
    dvel = rng.standard_normal(vel.shape)
    dvel /= np.sqrt((dvel * dvel).sum(axis=(1, 2), keepdims=True))
    acc_norm = np.zeros(Tn)

    def tangent_rhs(dp, dv, p, v, t):
        # analytic Jacobian of the softened pairwise force + wall gradient
        dacc = np.zeros_like(dp)
        for i in range(3):
            for j in range(3):
                if i == j:
                    continue
                d = p[:, j, :] - p[:, i, :]
                dd = dp[:, j, :] - dp[:, i, :]
                r2 = (d * d).sum(axis=1) + SOFT2
                r5 = r2 ** 2.5
                dacc[:, i, :] += dd / r2[:, None] ** 1.5 - 3 * d * \
                    ((d * dd).sum(axis=1) / r5)[:, None]
                if sigma > 0.0:
                    # Jacobian of sigma*d/r_soft: sigma*(I/r_soft - d dT/r^3)
                    rs = np.sqrt(r2)
                    dacc[:, i, :] += sigma * (dd / rs[:, None]
                                              - d * ((d * dd).sum(axis=1)
                                                     / rs ** 3)[:, None])
        if V0 > 0.0:
            r = np.sqrt((p * p).sum(axis=2))
            s = np.maximum(0.0, (r - WALL_R) / WALL_W)
            inside = s > 0
            amp = V0 * (1.0 + math.cos(Omega * t))
            radial = np.where((r[:, :, None] > 1e-300),
                              p / np.maximum(r, 1e-300)[:, :, None], 0.0)
            # d/dr of P_amp*s^(P-1)/w with s=(r-R_b)/w -> P(P-1)amp s^(P-2)/w^2
            k = WALL_P * (WALL_P - 1.0) * amp * s ** (WALL_P - 2.0) / WALL_W ** 2
            dr = (radial * dp).sum(axis=2)                      # (T,nb)
            dacc -= (k * inside * dr)[:, :, None] * radial
            dacc -= ((WALL_P * amp * s ** (WALL_P - 1.0) / WALL_W)
                     * inside)[:, :, None] \
                * (dp - (radial * dr[:, :, None]))
        return dv, dacc

    for k in range(steps):
        t = k * dt
        k1p, k1v = tangent_rhs(dpos, dvel, pos, vel, t)
        k2p, k2v = tangent_rhs(dpos + 0.5 * dt * k1p, dvel + 0.5 * dt * k1v,
                               pos, vel, t + 0.5 * dt)
        k3p, k3v = tangent_rhs(dpos + 0.5 * dt * k2p, dvel + 0.5 * dt * k2v,
                               pos, vel, t + 0.5 * dt)
        k4p, k4v = tangent_rhs(dpos + dt * k3p, dvel + dt * k3v,
                               pos, vel, t + dt)
        dpos = dpos + (dt / 6.0) * (k1p + 2 * k2p + 2 * k3p + k4p)
        dvel = dvel + (dt / 6.0) * (k1v + 2 * k2v + 2 * k3v + k4v)
        # advance the base trajectory with the same RK4 (duplicated logic)
        if (k + 1) % renorm_every == 0 or k == steps - 1:
            nrm = np.sqrt((dpos * dpos).sum(axis=(1, 2)) +
                          (dvel * dvel).sum(axis=(1, 2)))
            acc_norm += np.log(np.maximum(nrm, 1e-300))
            dpos = dpos / nrm[:, None, None]
            dvel = dvel / nrm[:, None, None]
        # base march (RK4, same step)
        a1 = trio_accel(pos, V0, Omega, t, sigma=sigma)
        v1 = vel
        a2 = trio_accel(pos + 0.5 * dt * v1, V0, Omega, t + 0.5 * dt,
                        sigma=sigma)
        v2 = vel + 0.5 * dt * a1
        a3 = trio_accel(pos + 0.5 * dt * v2, V0, Omega, t + 0.5 * dt,
                        sigma=sigma)
        v3 = vel + 0.5 * dt * a2
        a4 = trio_accel(pos + dt * v3, V0, Omega, t + dt, sigma=sigma)
        v4 = vel + dt * a3
        pos = pos + (dt / 6.0) * (v1 + 2 * v2 + 2 * v3 + v4)
        vel = vel + (dt / 6.0) * (a1 + 2 * a2 + 2 * a3 + a4)
    t_end = steps * dt
    return acc_norm / t_end


# ============================================================================
# Wu pair Monte-Carlo (stochastic realisation of the linear W-model)
# ============================================================================
def wu_mc(alpha, x, n_real=200_000, seed=SEED):
    """N_+/- ~ Poisson(Gamma_b (1 - e^{-x(1-/+alpha)})/(Gamma(1-/+alpha))).

    The committed survival realisation of qhb.wu; returns (r_mc, r_exact,
    abs deviation).  Gamma_b and Gamma drop out of r; x = Gamma/H survives.
    """
    rng = np.random.default_rng(seed)
    from qhb.wu import f_u
    tp = f_u(x, 1.0 - alpha)      # exact u->0 limit inside
    tm = f_u(x, 1.0 + alpha)
    Np = rng.poisson(tp, size=n_real).astype(float)
    Nm = rng.poisson(tm, size=n_real).astype(float)
    tot = Np + Nm
    good = tot > 0
    r_mc = float(((Np[good] - Nm[good]) / tot[good]).mean())
    from qhb.wu import residual
    r_ex = residual(alpha, x)
    return r_mc, r_ex, abs(r_mc - r_ex)


# ============================================================================
# Kepler validation anchor (the Roberts of this engine)
# ============================================================================
def kepler_period_check(e=0.5, dt=DT):
    """Two-body ellipse (m1=m2=1, a=1): measured vs Kepler period.

    Relative orbit with mu = G(m1+m2) = 2; bodies placed symmetric about
    the COM.  Start at perihelion; one period = first return of the
    relative y-coordinate through zero from below with x_rel > 0.
    Returns (T_kepler, T_measured, rel_error).
    """
    a, mu = 1.0, 2.0
    T_k = 2.0 * math.pi * a ** 1.5 / math.sqrt(mu)
    r_p = a * (1 - e)
    v_rel = math.sqrt(mu * (1 + e) / r_p)
    pos = np.array([[[r_p / 2, 0.0], [-r_p / 2, 0.0]]])          # (1,2,2)
    vel = np.array([[[0.0, v_rel / 2], [0.0, -v_rel / 2]]])      # (1,2,2)
    soft2 = 1e-10   # the validation anchor runs with negligible softening

    y_prev, t_prev = pos[0, 0, 1] - pos[0, 1, 1], 0.0
    n_steps = int(4 * T_k / dt)
    for k in range(n_steps):

        def deriv(p, v):
            return v, trio_accel(p, 0.0, 0.0, 0.0, soft2=soft2)

        k1v, k1a = deriv(pos, vel)
        k2v, k2a = deriv(pos + 0.5 * dt * k1v, vel + 0.5 * dt * k1a)
        k3v, k3a = deriv(pos + 0.5 * dt * k2v, vel + 0.5 * dt * k2a)
        k4v, k4a = deriv(pos + dt * k3v, vel + dt * k3a)
        pos = pos + (dt / 6.0) * (k1v + 2 * k2v + 2 * k3v + k4v)
        vel = vel + (dt / 6.0) * (k1a + 2 * k2a + 2 * k3a + k4a)
        y_new = pos[0, 0, 1] - pos[0, 1, 1]
        x_new = pos[0, 0, 0] - pos[0, 1, 0]
        t_new = (k + 1) * dt
        if k > 0 and y_prev < 0.0 <= y_new and x_new > 0.0:
            frac = -y_prev / (y_new - y_prev)
            T_meas = t_prev + frac * (t_new - t_prev)
            return T_k, T_meas, abs(T_meas - T_k) / T_k
        y_prev, t_prev = y_new, t_new
    return T_k, None, None
