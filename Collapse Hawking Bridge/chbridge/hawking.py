"""
hawking.py — closed-form thermodynamics of Schwarzschild black holes.

The thermodynamic side of the bridge.  For a mass M every quantity is an
exact closed form in CODATA constants:

    r_s      Schwarzschild radius            r_s = 2GM/c^2
    A_H      horizon area                    A = 4*pi*r_s^2
    S_BH     Bekenstein-Hawking entropy      S = k_B c^3 A / (4 G hbar)
    T_H      Hawking temperature             T = hbar c^3 / (8 pi G M k_B)
    P_H      Hawking luminosity (photons)    P = hbar c^6 / (15360 pi G^2 M^2)
    t_evap   idealised evaporation time      t = 5120 pi G^2 M^3 / (hbar c^4)
    rho_bar  mean density inside horizon     rho = 3M / (4 pi r_s^3)
    kappa    surface gravity                 kappa = c^4 / (4 G M)

and the Page time of the unitary entropy-flux model:

    t_Page = (1 - 2^{-3/2}) * t_evap,     PAGE_FRACTION = 0.6464466...

The contact point with cosmology is the CMB-equal mass:

    T_H(M) = T_CMB  <=>  M_CMB = hbar c^3 / (8 pi G k_B T_CMB) ~ 4.50e22 kg
"""
import math

from .constants import AU, T_CMB, G, Gyr, c, hbar, k_B, lyr, yr

PAGE_FRACTION = 1.0 - 2.0 ** (-1.5)   # 0.6464466094067262...


# ----------------------------------------------------------------------------
# Core closed-form relations (Schwarzschild, photon-only, neutral)
# ----------------------------------------------------------------------------
def r_s(M):
    """Schwarzschild radius [m]."""
    return 2.0 * G * M / c**2


def horizon_area(M):
    """Horizon area A = 4 pi r_s^2 [m^2]."""
    return 4.0 * math.pi * r_s(M) ** 2


def S_BH(M):
    """Bekenstein-Hawking entropy [J/K]."""
    return k_B * c**3 * horizon_area(M) / (4.0 * G * hbar)


def T_H(M):
    """Hawking temperature [K]."""
    return hbar * c**3 / (8.0 * math.pi * G * M * k_B)


def P_H(M):
    """Hawking luminosity assuming photon-only emission [W]."""
    return hbar * c**6 / (15360.0 * math.pi * G**2 * M**2)


def t_evap(M):
    """Idealised photon-only lifetime [s]."""
    return 5120.0 * math.pi * G**2 * M**3 / (hbar * c**4)


def t_page(M):
    """Page time of the unitary entropy-flux model [s]."""
    return PAGE_FRACTION * t_evap(M)


def rho_mean(M):
    """Mean density inside the horizon [kg/m^3]."""
    return 3.0 * M / (4.0 * math.pi * r_s(M) ** 3)


def equal_CMB_mass():
    """Mass whose Hawking temperature equals T_CMB [kg]."""
    return hbar * c**3 / (8.0 * math.pi * G * k_B * T_CMB)


def surface_gravity(M):
    """Schwarzschild surface gravity kappa = c^4/(4 G M) [m/s^2]."""
    return c**4 / (4.0 * G * M)


# ----------------------------------------------------------------------------
# Human-readable formatting helpers
# ----------------------------------------------------------------------------
def fmt_len(x):
    """Format a length in human units."""
    if x < 1e-3:
        return f"{x*1e6:.3g} um"
    if x < 1.0:
        return f"{x*1e3:.3g} mm"
    if x < 1e3:
        return f"{x:.4g} m"
    if x < 1e3 * AU:
        return f"{x:.4g} m"
    return f"{x/lyr:.4g} ly"


def fmt_time(x):
    """Format a time in human units."""
    if x < 1e-6:
        return f"{x:.3g} s"
    if x < 1e3 * yr:
        return f"{x/yr:.4g} yr"
    if x < 1e6 * yr:
        return f"{x/(1e3*yr):.4g} kyr"
    if x < 1e9 * yr:
        return f"{x/(1e6*yr):.4g} Myr"
    if x < 1e12 * yr:
        return f"{x/Gyr:.4g} Gyr"
    return f"{x/yr:.3e} yr"


def fmt_entropy(x):
    """Format dimensionless entropy S/k_B."""
    return f"{x:.4e}"
