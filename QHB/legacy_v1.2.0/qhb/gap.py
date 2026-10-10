# -*- coding: utf-8 -*-
"""
gap.py — the confinement gap of the three spinor corrections.

The physical picture (a marked HYPOTHESIS of the package, see
docs/theory.md): the three dynamic corrections of the septinial family
(Berry quanta b_k = {pi^2/8, pi^2/18, pi^2/98} and braking quanta
a_k = {pi^5/704, pi^5/5346, pi^5/369754} of the pi/2, pi/3, pi/7
sectors) act as a three-tone drive on a discretized parabolic geometry.
The static sampled geometry already carries a splitting Delta_0 (the
chord-flattening world of CHB theorem T10); the drive opens and shifts
a FLOQUET gap Delta_F.

Committed model (G-model, fully specified in docs/methods.md):

  geometry   H_static = hopping J=1 on a Dirichlet chain of N sites with
             on-site potential q_n = (kappa/2)(x_n - x0)^2 - q_pk;
  two-band   the two lowest levels |0>, |1> with static gap Delta_0;
  drive      H(t) = (Delta_0/2) sigma_z + v(t) sigma_x + w(t) sigma_z,
             v(t) = sum_k b_k cos(omega_k t + phi_k)   (Berry, transverse)
             w(t) = sum_k a_k cos(omega_k t + psi_k)   (braking, longitudinal)
             omega = (2, 3, 7) * Omega_0, Omega_0 = 1 (single Floquet
             period T0 = 2*pi), septinial phases phi = psi = (pi/2, pi/3, pi/7);
  Floquet    U(T0) built from M piecewise-constant exact 2x2 exponentials;
  gap        quasi-energy spacing of the two eigenphases, folded to
             (0, Omega_0/2].

Exact facts proven here (theorem T2):
  * b -> -b:  H(-b) = sigma_z H(b) sigma_z  => U(-b) = sigma_z U(b) sigma_z
    => identical eigenphases => the gap is EVEN in every Berry amplitude;
  * a -> -a:  H(-a) = sigma_x H(a) sigma_x  => the gap is EVEN in every
    braking amplitude.
  Hence the leading gap response is O(b^2, a^2) — no linear opening.
"""
import math
import numpy as np

from .constants import (BERRY_TRIO, BRAKING_TRIO, delta_A, delta_B, delta_C)

# --- committed drive configuration (G-model) --------------------------------
OMEGA0 = 2.0                                # base Floquet frequency
T_PERIOD = 2.0 * math.pi / OMEGA0           # drive period
OMEGA_TONES = (2.0, 3.0, 7.0)               # tone frequencies in Omega0 units
PHI_SEPTINIAL = (delta_A, delta_B, delta_C) # (pi/2, pi/3, pi/7) — exact
M_STEPS = 1920                              # piecewise-constant steps per period

# committed geometry of the static chain (code units)
#   CONTINUUM-CONSISTENT convention: the hopping scales as J = 1/h^2 so the
#   chain converges to the fixed continuum Schrodinger operator as N grows
#   (with J fixed the effective mass would diverge and the gap would be a
#   band-edge artifact ~ h).  A SHALLOW well (exactly two bound levels, E1
#   near threshold) makes the gap sensitive to the peak depth — the
#   response s = dDelta/dq_pk is a committed C5 input; Omega0/2 = 1 >> Delta_0.
KAPPA = 0.05                                # parabola curvature
Q_PK = 0.4                                  # parabola peak (well depth)
N_CHAIN = 64                                # committed chain for C1


# ============================================================================
# Lemma A (inherited from CHB T10) — exact chord flattening of a parabola
# ============================================================================
def lemma_a_worst(kappa, hstep):
    """Worst-alignment peak loss of a sampled parabola: kappa*h^2/8 (exact)."""
    return kappa * hstep ** 2 / 8.0


def lemma_a_mean(kappa, hstep):
    """Mean-alignment peak loss of a sampled parabola: kappa*h^2/24 (exact)."""
    return kappa * hstep ** 2 / 24.0


# ============================================================================
# static chain — the sampled parabolic geometry
# ============================================================================
def parabolic_profile(N, kappa=KAPPA, q_pk=Q_PK):
    """On-site potential q_n = (kappa/2) x_n^2 - q_pk on a Dirichlet chain.

    The chain half-length L/2 is fixed by the honest truncation condition
    q(L/2) = 0, i.e. L = sqrt(8*q_pk/kappa); the sampled peak is flattened
    by Lemma A exactly as in CHB T10.
    """
    L = math.sqrt(8.0 * q_pk / kappa)
    hstep = L / (N + 1)
    x = (np.arange(1, N + 1, dtype=float) - (N + 1) / 2.0) * hstep
    q = 0.5 * kappa * x ** 2 - q_pk
    return x, q, hstep, L


def static_gap(N, kappa=KAPPA, q_pk=Q_PK):
    """Two lowest eigenvalues of the sampled parabolic chain.

    Returns (E0, E1, Delta_0).  Dirichlet boundaries; hopping J = 1/h^2
    (the continuum-consistent convention); on-site potential q_n.
    Uses a symmetric tridiagonal solver.
    """
    x, q, hstep, L = parabolic_profile(N, kappa, q_pk)
    J = 1.0 / hstep ** 2
    off = -J * np.ones(N - 1)
    diag = q + 2.0 * J          # kinetic = J(2I - adjacency) >= 0
    try:
        from scipy.linalg import eigh_tridiagonal
        w = eigh_tridiagonal(diag, off, eigvals_only=True,
                             select="i", select_range=(0, 1))
        E0, E1 = float(w[0]), float(w[1])
    except Exception:
        H = np.diag(diag) + np.diag(off, 1) + np.diag(off, -1)
        w = np.linalg.eigvalsh(H)
        E0, E1 = float(w[0]), float(w[1])
    return E0, E1, E1 - E0


def gap_response(N, kappa=KAPPA, q_pk=Q_PK, dq=None):
    """s = d(Delta_0)/d(q_pk) by a central difference (committed diagnostic).
    NOTE: q_pk enters only through the potential depth; the truncation
    length L = sqrt(8 q_pk/kappa) moves with it, which is part of the
    committed definition (the well always ends where the potential does)."""
    if dq is None:
        dq = 1e-4 * q_pk
    _, _, d_up = static_gap(N, kappa, q_pk + dq)
    _, _, d_dn = static_gap(N, kappa, q_pk - dq)
    return (d_up - d_dn) / (2.0 * dq)


# ============================================================================
# two-band Floquet operator (exact 2x2 exponentials, piecewise constant)
# ============================================================================
def _expm_h2(c0, cz, cx, dt):
    """exp(-i (c0 I + cz sz + cx sx) dt) — closed form for Hermitian 2x2.

    exp(-i V dt) = cos(w dt) I - i (sin(w dt)/w)(cz sz + cx sx),  w = |(cz,cx)|.
    """
    w = math.hypot(cz, cx)
    cph = math.cos(w * dt)
    if w > 1e-300:
        s = math.sin(w * dt) / w          # sin(w dt)/w, -> dt as w -> 0
    else:
        s = dt
    a11 = cph - 1j * s * cz
    a22 = cph + 1j * s * cz
    a12 = -1j * s * cx
    ph = math.cos(c0 * dt) - 1j * math.sin(c0 * dt)
    return ph * np.array([[a11, a12], [a12, a22]], dtype=complex)


def floquet_gap(Delta0, beta=0.0, b=None, a=None, M=M_STEPS):
    """Quasi-energy gap of the driven two-band system.

    beta  — rigid-trio scaling: b_k = beta*BERRY_TRIO[k], a_k = beta*BRAKING_TRIO[k];
    b, a  — explicit amplitude triples (override beta when given).

    Returns (Delta_F, diag) with diag carrying the folded quasi-energies.
    """
    if b is None:
        b = tuple(beta * v for v in BERRY_TRIO)
    if a is None:
        a = tuple(beta * v for v in BRAKING_TRIO)
    dt = T_PERIOD / M
    U = np.eye(2, dtype=complex)
    for m in range(M):
        t = (m + 0.5) * dt
        v = sum(b[k] * math.cos(OMEGA_TONES[k] * OMEGA0 * t + PHI_SEPTINIAL[k])
                for k in range(3))
        w = sum(a[k] * math.cos(OMEGA_TONES[k] * OMEGA0 * t + PHI_SEPTINIAL[k])
                for k in range(3))
        U = _expm_h2(0.0, 0.5 * Delta0 + w, v, dt) @ U
    # eigenphases -> quasi-energies folded to (0, Omega_0/2]
    ev = np.linalg.eigvals(U)
    ph = np.mod(np.angle(ev), 2.0 * math.pi)      # in [0, 2pi)
    eps = np.sort(ph) / T_PERIOD                  # quasi-energies in [0, Omega0)
    d = abs(eps[1] - eps[0])
    gap = min(d, OMEGA0 - d)
    return float(gap), {"eps": eps.tolist()}


# ============================================================================
# committed diagnostics (used by campaigns and validate)
# ============================================================================
def static_of_chain(N=N_CHAIN, kappa=KAPPA, q_pk=Q_PK):
    """Static block: (E0, E1, Delta_0, s, h, L)."""
    E0, E1, D0 = static_gap(N, kappa, q_pk)
    s = gap_response(N, kappa, q_pk)
    _, _, hstep, L = parabolic_profile(N, kappa, q_pk)
    return E0, E1, D0, s, hstep, L


def evenness_dev(Delta0, beta=0.21, M=M_STEPS):
    """Flip-symmetry diagnostics of the gap (theorem T2, honest form).

    Returns (max_dev, per-check devs) for three global flips:
      (i)   b -> -b :  U(-b, a) = sigma_z U(b, a) sigma_z   — EXACT evenness;
      (ii)  a -> -a :  NOT exact — the residual is the genuine odd-in-a
                        response through second-order a*b cross terms
                        (Magnus commutator [w sigma_z, v sigma_x]);
      (iii) both    :  same odd-in-a residual.
    The a-ONLY drive is separately all-order zero (integer-tone
    cancellation; see campaigns/run_c1.py check).  """
    b = tuple(beta * v for v in BERRY_TRIO)
    a = tuple(beta * v for v in BRAKING_TRIO)
    nb = tuple(-v for v in b)
    na = tuple(-v for v in a)
    g0, _ = floquet_gap(Delta0, b=b, a=a, M=M)
    checks = []
    for bb, aa in ((nb, a), (b, na), (nb, na)):
        g1, _ = floquet_gap(Delta0, b=bb, a=aa, M=M)
        checks.append(abs(g1 - g0))
    return max(checks), checks
