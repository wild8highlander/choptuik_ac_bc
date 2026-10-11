"""
trio.py — the three-body rigidity layer.

The fourth link of the hypothesis (a marked HYPOTHESIS, see
docs/theory.md): a triplet bound at maximal density cannot shed one
member, because the UNSOLVED three-body problem shares energy chaotically
and no single body collects an escape channel — provided the geometric
gap of the drive stands as a wall.  The package measures exactly this,
and carries two exact honest negatives first:

T4 (exact, classical).  The equilateral Lagrange solution of the
three-body problem is linearly UNSTABLE for equal masses: the Gascheau
(1843) criterion requires

    nu = (m1 m2 + m2 m3 + m3 m1) / (m1 + m2 + m3)^2  <  1/27 ,

while equal masses give nu = 1/3.  The characteristic equation of the
rotating-frame linearization,

    lambda^4 + lambda^2 + (27/4) nu = 0 ,

then has complex roots with growth rate |lambda| = (9/4)^{1/4} = sqrt(3/2)
in units of the mean motion n.  No static rigid triangle exists.

T5 (measured, committed negative).  Without the dynamic wall (V0 = 0)
the Newtonian trio unbinds: P_esc > 0 on the committed ensemble
(campaign C2).  Static gravity does not confine; the trap needs the gap.

T6 (measured law).  With the oscillating geometric wall
    U(r, t) = V0 (1 + cos(Omega t)) * max(0, (r - R_b)/w)^2 ,
the escape probability collapses and the Lyapunov exponent stays
positive: BOUND CHAOS — chaotic inside, sealed outside (campaign C2).
"""
import math


def gascheau_nu(m1=1.0, m2=1.0, m3=1.0):
    """nu = (m1m2 + m2m3 + m3m1)/(sum m)^2 (exact)."""
    return (m1 * m2 + m2 * m3 + m3 * m1) / (m1 + m2 + m3) ** 2


GASCHEAU_THRESHOLD = 1.0 / 27.0   # exact stability bound


def gascheau_verdict(m1=1.0, m2=1.0, m3=1.0):
    """Stability verdict of the equilateral solution (theorem T4)."""
    nu = gascheau_nu(m1, m2, m3)
    stable = nu < GASCHEAU_THRESHOLD
    return {"nu": nu, "threshold": GASCHEAU_THRESHOLD,
            "stable": stable, "verdict": "STABLE" if stable else "UNSTABLE"}


def routh_roots(nu):
    """Roots of lambda^4 + lambda^2 + (27/4) nu = 0 (exact quadratic in z)."""
    disc = 1.0 - 27.0 * nu
    roots = []
    for sgn in (+1.0, -1.0):
        z = (-1.0 + sgn * math.sqrt(complex(disc))) / 2.0   # z = lambda^2
        lam = math.sqrt(complex(z))
        roots.extend([lam, -lam])
    return roots


def growth_rate_equal_masses():
    """|lambda|/n for equal masses = sqrt(3/2) (exact closed form)."""
    return math.sqrt(1.5)


# --- the geometric wall (the gap standing as a barrier) ----------------------
WALL_R = 8.0        # wall radius R_b (code units; bound region ~ r < 1)
WALL_W = 1.0        # wall width w
WALL_P = 2.0        # wall steepness (smooth quadratic shoulder)


def wall_U(r, V0, Omega, t, R_b=WALL_R, w=WALL_W, p=WALL_P):
    """Oscillating geometric wall U(r,t) = V0 (1 + cos Omega t) s(r)^p."""
    s = max(0.0, (r - R_b) / w)
    return V0 * (1.0 + math.cos(Omega * t)) * s ** p


def wall_U_vec(r, V0, Omega, t, R_b=WALL_R, w=WALL_W, p=WALL_P):
    """Vectorized wall over an array of radii."""
    import numpy as np
    s = np.maximum(0.0, (r - R_b) / w)
    return V0 * (1.0 + math.cos(Omega * t)) * s ** p
