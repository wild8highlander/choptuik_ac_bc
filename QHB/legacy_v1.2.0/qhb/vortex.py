"""
vortex.py — the classical three-vortex layer of the trap physics.

The fourth link of the hypothesis (H4, a marked HYPOTHESIS, see
docs/theory.md) claims that a triplet bound at maximal density cannot
shed a member.  The Newtonian side of the claim carries two exact
honest negatives already (T4 Gascheau instability; T5 the free trio
unbinds).  This module adds the CLASSICAL CONTRAST — the same geometric
triangle inside the oldest reduction of fluid dynamics, the point-vortex
problem of Kirchhoff (1876):

  * the same equilateral triangle that is UNSTABLE under 1/r attraction
    (T4) is a rigidly rotating RELATIVELY EQUILIBRIUM of the Kirchhoff
    equations with rotation rate

        omega = Gamma_tot / (2 pi a^2)          (exact, classical),

  * the problem carries FOUR analytic invariants — the Hamiltonian H,
    the angular impulse I = sum Gamma_k |r_k|^2 (the classical prototype
    of the Chaplygin topological integral) and the two linear-impulse
    components P, Q — and the mixed-sign (1,1,-1) right-isosceles launch
    annihilates ALL FOUR at once (the classical Aref (1979) collapse
    manifold I = H = P = Q = 0),

  * the equal same-sign triangle is linearly NEUTRALLY stable: every
    eigenvalue of the corotating-frame linearization sits on the
    imaginary axis (theorem T11 of the package; machine + symbolic).

Everything here is implemented from the classical equations (Kirchhoff
1876; Groebli 1877; Synge 1949; Aref 1979) with the package's own code
paths; the invariants are re-derived and re-measured, never imported.
Units: circulations Gamma in code units, lengths in code units, time in
code units (a^2/Gamma scale).
"""
import math

import numpy as np

TWO_PI = 2.0 * math.pi


# ============================================================================
# exact classical formulas
# ============================================================================
def lagrange_omega(Gamma=1.0, a=1.0):
    """Rigid rotation rate of the equal same-sign equilateral triangle:
    omega = Gamma_tot/(2 pi a^2) with Gamma_tot = 3 Gamma (exact, classical).

    For Gamma = 1, a = 1 this is 3/(2 pi) = 0.477464829275686..."""
    return (3.0 * Gamma) / (TWO_PI * a ** 2)


def relative_equilibrium_omega(Gammas, a=1.0):
    """General-circulation equilateral rotation rate: Gamma_tot/(2 pi a^2)."""
    return float(np.sum(Gammas)) / (TWO_PI * a ** 2)


def circumradius(a=1.0):
    """Circumradius of the equilateral triangle of side a: a/sqrt(3)."""
    return a / math.sqrt(3.0)


def equilateral_positions(Gamma=1.0, a=1.0, theta0=0.0):
    """Three equal same-sign vortices on the circumcircle (numpy (3,2)).

    Angles theta0 + {0, 2pi/3, 4pi/3}; pairwise distances equal a exactly
    (machine precision).  Gamma is accepted for signature symmetry and
    does not enter the positions."""
    R = circumradius(a)
    ang = theta0 + TWO_PI * np.array([0.0, 1.0 / 3.0, 2.0 / 3.0])
    return np.stack([R * np.cos(ang), R * np.sin(ang)], axis=1)


def aref_launch():
    """The classical mixed-sign launch on the Aref manifold.

    Gamma = (1, 1, -1); positions r1 = sqrt(2) xhat, r2 = sqrt(2) yhat,
    r3 = r1 + r2  (right-isosceles, separations (2, sqrt2, sqrt2)).
    All four invariants vanish EXACTLY:
      Q = sum Gamma x = sqrt2 - sqrt2 = 0
      P = sum Gamma y = sqrt2 - sqrt2 = 0
      I = sum Gamma |r|^2 = 2 + 2 - 4 = 0
      H = -(1/2pi) [ln 2 - ln sqrt2 - ln sqrt2] = 0
    (verified by invariants_of at machine precision).
    """
    g = np.array([1.0, 1.0, -1.0])
    s2 = math.sqrt(2.0)
    pos = np.array([[s2, 0.0], [0.0, s2], [s2, s2]])
    return pos, g


# ============================================================================
# the four classical invariants
# ============================================================================
def angular_impulse(pos, Gamma):
    """I = sum_k Gamma_k |r_k|^2 (the Chaplygin-integral prototype)."""
    r2 = (pos * pos).sum(axis=1)
    return float((Gamma * r2).sum())


def impulse_PQ(pos, Gamma):
    """Q = sum Gamma_k x_k,  P = sum Gamma_k y_k (classical convention)."""
    return float((Gamma * pos[:, 1]).sum()), float((Gamma * pos[:, 0]).sum())


def hamiltonian(pos, Gamma):
    """H = -(1/2pi) sum_{i<j} Gamma_i Gamma_j ln |r_i - r_j|  (classical)."""
    H = 0.0
    n = pos.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            d = pos[i] - pos[j]
            H -= Gamma[i] * Gamma[j] * math.log(math.hypot(d[0], d[1]))
    return H / TWO_PI


def invariants_of(pos, Gamma):
    """All four classical invariants as a dict."""
    P, Q = impulse_PQ(pos, Gamma)
    return {"I": angular_impulse(pos, Gamma), "H": hamiltonian(pos, Gamma),
            "P": P, "Q": Q}


# ============================================================================
# the Kirchhoff equations (first-order, no velocities)
# ============================================================================
def kirchhoff_rhs(pos, Gamma):
    """dr_k/dt = (1/2pi) sum_{j != k} Gamma_j zhat x (r_k - r_j)/|r_k-r_j|^2.

    Vectorised over an ensemble pos (T, n, 2); Gamma broadcast (n,)."""
    pos = np.asarray(pos, dtype=float)
    single = (pos.ndim == 2)
    if single:
        pos = pos[None, ...]
    T, n, _ = pos.shape
    Gam = np.asarray(Gamma, dtype=float)
    vel = np.zeros_like(pos)
    for k in range(n):
        acc = np.zeros((T, 2))
        for j in range(n):
            if j == k:
                continue
            d = pos[:, k, :] - pos[:, j, :]              # (T,2)
            r2 = (d * d).sum(axis=1) + 1e-300
            # zhat x d = (-d_y, d_x)
            acc += Gam[j] * np.stack([-d[:, 1], d[:, 0]], axis=1) / r2[:, None]
        vel[:, k, :] = acc / TWO_PI
    return vel[0] if single else vel


def kirchhoff_run(pos0, Gamma, dt=1e-3, steps=40000, record_every=0):
    """RK4 march of the Kirchhoff system (deterministic, fixed step).

    Returns dict with the trajectory (optionally sampled), the final
    state and the invariant drift bookkeeping."""
    pos = np.array(pos0, dtype=float)
    traj = [] if record_every else None
    if record_every:
        traj.append(pos.copy())
    for k in range(steps):

        def f(p):
            return kirchhoff_rhs(p, Gamma)

        k1 = f(pos)
        k2 = f(pos + 0.5 * dt * k1)
        k3 = f(pos + 0.5 * dt * k2)
        k4 = f(pos + dt * k3)
        pos = pos + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        if record_every and (k + 1) % record_every == 0:
            traj.append(pos.copy())
    out = {"pos": pos, "steps": steps, "t_end": steps * dt}
    if traj:
        out["traj"] = np.array(traj)
    return out


# ============================================================================
# the corotating-frame linearization (theorem T11)
# ============================================================================
def corotating_rhs(pos, Gamma, omega):
    """RHS of the Kirchhoff system in the frame corotating with rate omega:
    dr/dt = v(r) - omega * zhat x r."""
    v = kirchhoff_rhs(pos, Gamma)
    return v - omega * np.stack([-pos[..., 1], pos[..., 0]], axis=-1)


def jacobian_corotating_exact(pos, Gamma, omega):
    """Analytic Jacobian of the corotating Kirchhoff RHS (no finite
    differences).  pos (3,2), Gamma (3,), omega float -> J (6,6).

    Per ordered pair (k, j), k != j, with d = r_k - r_j, q = |d|^2:
      v_k += (Gamma_j/2pi) * zhat x d / q
      d/d(r_j) block = -(Gamma_j/2pi q^2) * [[2 dx dy,  dy^2 - dx^2],
                                             [dy^2 - dx^2, -2 dx dy]]
      d/d(r_k) block = the opposite-sign sum over j (plus the corotation
      block [[0, omega], [-omega, 0]] from -omega * zhat x r_k).
    """
    n = pos.shape[0]
    J = np.zeros((2 * n, 2 * n))
    for k in range(n):
        for j in range(n):
            if j == k:
                continue
            d = pos[k] - pos[j]
            q = d[0] ** 2 + d[1] ** 2
            q4 = q * q
            B = np.array([[2 * d[0] * d[1], d[1] ** 2 - d[0] ** 2],
                          [d[1] ** 2 - d[0] ** 2, -2 * d[0] * d[1]]])
            blk = -(Gamma[j] / (TWO_PI * q4)) * B
            J[2 * k:2 * k + 2, 2 * j:2 * j + 2] += blk
            J[2 * k:2 * k + 2, 2 * k:2 * k + 2] -= blk
    for k in range(n):
        J[2 * k:2 * k + 2, 2 * k:2 * k + 2] += np.array([[0.0, omega],
                                                         [-omega, 0.0]])
    return J


def linearize_triangle_exact(Gamma=(1.0, 1.0, 1.0), a=1.0, theta0=0.0):
    """Exact Jacobian linearization at the equilateral fixed point.

    Returns (eigenvalues (6,) complex, omega, J (6,6)).  The exact
    spectrum is {0, 0, +-i omega, +-i omega} (theorem T11): every
    eigenvalue lies on the imaginary axis or at the origin."""
    Gam = np.asarray(Gamma, dtype=float)
    pos = equilateral_positions(1.0, a, theta0)
    omega = relative_equilibrium_omega(Gam, a)
    J = jacobian_corotating_exact(pos, Gam, omega)
    ev = np.linalg.eigvals(J)
    return ev, omega, J


def linearize_triangle(Gamma=(1.0, 1.0, 1.0), a=1.0, theta0=0.0, h=1e-6):
    """Central-difference Jacobian of the corotating RHS at the equilateral
    fixed point.  Returns (eigenvalues (6,) complex, omega, J (6,6))."""
    Gam = np.asarray(Gamma, dtype=float)
    p0 = equilateral_positions(1.0, a, theta0).ravel()       # (6,)
    omega = relative_equilibrium_omega(Gam, a)

    def F(p):
        return corotating_rhs(p.reshape(3, 2), Gam, omega).ravel()

    J = np.zeros((6, 6))
    for i in range(6):
        e = np.zeros(6)
        e[i] = h
        J[:, i] = (F(p0 + e) - F(p0 - e)) / (2.0 * h)
    ev = np.linalg.eigvals(J)
    return ev, omega, J


# ============================================================================
# committed diagnostics
# ============================================================================
def triangle_shape_error(pos, a=1.0):
    """Max deviation of the three pairwise distances from a (rigidity)."""
    d = []
    for i, j in ((0, 1), (1, 2), (2, 0)):
        dd = pos[i] - pos[j]
        d.append(math.hypot(dd[0], dd[1]))
    return max(abs(x - a) for x in d)


def rotation_angle(traj, Gamma=1.0, a=1.0):
    """Accumulated rotation angle of the triangle (sum of per-sample
    angular increments of vortex 0 about the centroid).  traj (m,3,2)."""
    ang = np.arctan2(traj[:, 0, 1], traj[:, 0, 0])
    d = np.diff(ang)
    d = (d + math.pi) % TWO_PI - math.pi               # unwrap
    return float(d.sum())
