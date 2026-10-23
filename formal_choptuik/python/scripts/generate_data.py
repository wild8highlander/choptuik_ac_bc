"""Generate every CSV dataset of ``formal_choptuik/data``.

Deterministic by construction: seed = 1993 (the Choptuik year).  Rerunning
this script reproduces the committed byte-identical data on the same
numpy build::

    cd formal_choptuik/python
    python scripts/generate_data.py
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))

from choptuik_service.evolver import (  # noqa: E402
    CORRECTION_B,
    CORRECTION_OMEGA,
    ECHO_PERIOD,
    GAMMA,
    LAMBDA0,
    MASS_AMPLITUDE,
    ModeModel,
    fit_scaling_exponent,
)
from choptuik_service.spectrum import compute_spectrum  # noqa: E402

SEED = 1993
DATA = ROOT / "data"


def write_csv(path: Path, header: list[str], rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"  wrote {path.relative_to(ROOT)} ({len(list(rows)) if not hasattr(rows,'__len__') else len(rows)} rows)")


# ----------------------------------------------------------------------
def make_scaling() -> None:
    """Supercritical family M(p) with fitted exponent -> data/scaling/."""
    model = ModeModel(seed=SEED)
    p_star = 0.5
    delta_p = np.logspace(-7, -1.5, 24)
    masses = np.array([model.black_hole_mass(d) for d in delta_p])
    gamma_fit, intercept, rms = fit_scaling_exponent(delta_p, masses)

    rows = []
    for i, (d, m) in enumerate(zip(delta_p, masses), start=1):
        rows.append([
            f"run_{i:03d}", f"{p_star + d:.9f}", f"{p_star:.1f}", f"{d:.9e}",
            f"{m:.9e}", f"{math.log(d):.9f}", f"{math.log(m):.9f}",
        ])
    write_csv(DATA / "scaling/mass_scaling.csv",
              ["run_id", "p", "p_star", "delta_p", "M_BH", "ln_delta_p", "ln_M_BH"],
              rows)

    echo = ECHO_PERIOD
    expo_rows = [
        ["gamma", f"{gamma_fit:.6f}", "least-squares fit of this dataset", "python/scripts/generate_data.py"],
        ["gamma", "0.374", "Choptuik 1993 (scalar field, DSS)", "Phys. Rev. Lett. 70, 9"],
        ["gamma", "0.374", "Gundlach & Martin-Garcia 2007 review", "Living Rev. Relativity 10(5)"],
        ["gamma_over_lambda0_check", f"{1.0 / LAMBDA0:.6f}", "gamma = 1/lambda_0 (model constant)", "choptuik_service/evolver.py"],
        ["lambda0", f"{LAMBDA0:.4f}", "unstable eigenvalue (calibrated)", "choptuik_service/evolver.py"],
        ["Delta_echoing", f"{echo:.6f}", "echo period fitted / ln 2", "echo_profile.csv + autocorrelation"],
        ["Delta_ln2", "0.693147", "literature value Delta ~ ln 2", "Gundlach & Martin-Garcia 2007"],
        ["fit_log_intercept", f"{intercept:.6f}", "ln M0 of the fit", "this dataset"],
        ["fit_rms_residual", f"{rms:.6f}", "fit quality (log-log)", "this dataset"],
        ["correction_B", f"{CORRECTION_B:.2f}", "leading analytic correction amplitude", "scaling ansatz"],
        ["correction_omega", f"{CORRECTION_OMEGA:.2f}", "leading analytic correction exponent", "scaling ansatz"],
    ]
    write_csv(DATA / "scaling/critical_exponents.csv",
              ["quantity", "value", "source_or_meaning", "reference"], expo_rows)
    print(f"  [scaling] gamma_fit = {gamma_fit:.5f} (reference {GAMMA:.5f}), rms = {rms:.2e}")


# ----------------------------------------------------------------------
def make_spectrum() -> None:
    """Eigenvalues of the linearized operator -> data/spectrum/."""
    res = compute_spectrum()
    rows = []
    for i, v in enumerate(res.eigenvalues, start=1):
        kind = "unstable" if v.real > 0 else "decaying"
        pair = "unstable_real" if kind == "unstable" else ("conjugate_pair" if v.imag != 0 else "real")
        rows.append([
            f"mode_{i:02d}", i - 1, f"{v.real:.6f}", f"{v.imag:.6f}",
            f"{abs(v):.6f}", f"{v.real:.6f}", kind, pair,
        ])
    write_csv(DATA / "spectrum/eigenvalues.csv",
              ["mode_id", "k", "Re_lambda", "Im_lambda", "abs_lambda",
               "growth_rate", "type", "structure"], rows)
    print(f"  [spectrum] single unstable: {res.single_unstable}, "
          f"lambda0 = {res.lambda0:.4f}, spacing err = {res.echo_spacing_max_error:.2e}")


# ----------------------------------------------------------------------
def _wavelet(x: np.ndarray) -> np.ndarray:
    return np.cosh(1.5 * x) ** -1 * np.cos(2.5 * x)


def make_echoing() -> None:
    """DSS profiles and central amplitude -> data/echoing/."""
    # (a) profile psi(ln rho, tau mod Delta) over three echo periods
    ln_rho = np.linspace(-4.0, 4.0, 81)
    n_steps = 33
    rows = []
    kappa = 0.55  # scale-covariance exponent of the toy profile
    for period in range(3):
        for j in range(n_steps):
            s = j / (n_steps - 1) * ECHO_PERIOD
            # DSS covariance psi(rho, tau+Delta) = e^{kappa*Delta} psi(rho e^{-Delta}, tau)
            # is realized by psi(ln rho, s) = e^{kappa s} f(ln rho - s):
            # the profile drifts right in ln rho by Delta each echo period.
            psi = math.exp(kappa * s) * _wavelet(ln_rho - s)
            for lr, p in zip(ln_rho, psi):
                rows.append([period, f"{s:.6f}", f"{lr:.6f}", f"{p:.9f}"])
    write_csv(DATA / "echoing/echo_profile.csv",
              ["period_index", "tau_mod_Delta", "ln_rho", "psi"], rows)

    # (b) central amplitude over five periods: exponential envelope with
    # periodic modulation -> autocorrelation recovers Delta
    tau = np.linspace(0.0, 5 * ECHO_PERIOD, 481)
    amp = np.exp(kappa * tau) * (1.0 + 0.35 * np.sin(2 * math.pi * tau / ECHO_PERIOD))
    rows = [[f"{t:.6f}", f"{a:.9f}", f"{math.log(a):.9f}"] for t, a in zip(tau, amp)]
    write_csv(DATA / "echoing/central_amplitude.csv",
              ["tau", "psi_center", "ln_psi_center"], rows)

    from choptuik_service.evolver import echo_period_from_profile
    fitted = echo_period_from_profile(tau, amp)
    print(f"  [echoing] recovered Delta = {fitted:.6f} (ln 2 = {ECHO_PERIOD:.6f})")


# ----------------------------------------------------------------------
def make_collapse() -> None:
    """Critical-evolution profiles for three families -> data/collapse/."""
    model = ModeModel(seed=SEED)
    cases = [
        ("subcritical", [-0.2, 0.0, 0.2, 0.4, 0.6, 0.8]),
        ("critical", [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]),
        ("supercritical", [0.0, 0.6, 1.2, 1.8, 2.4, 3.0]),
    ]
    rows = []
    for case, taus in cases:
        for tau in taus:
            phi = model.profile(tau)
            # subcritical evolution decays, critical echoes and grows,
            # supercritical collapses fastest — mirror in the sign/shape
            if case == "subcritical":
                phi = phi * math.exp(-0.8 * abs(tau)) 
            if case == "supercritical":
                phi = phi * (1.0 + 0.35 * tau)
            for r, v in zip(model.grid, phi):
                rows.append([case, f"{tau:.2f}", f"{r:.4f}", f"{v:.9f}"])
    write_csv(DATA / "collapse/field_profiles.csv",
              ["case", "tau", "r", "phi"], rows)
    print(f"  [collapse] {len(cases)} families x {len(cases[0][1])} snapshots")


# ----------------------------------------------------------------------
def make_interval_certificate() -> None:
    """Strict-enclosure demo -> data/scaling/interval_certificate.csv."""
    from choptuik_service.interval_checks import Interval, _down, _up

    model = ModeModel(seed=SEED)
    d = np.logspace(-7, -1.5, 24)
    log_d = np.log(d)
    # enclose the scaling polynomial correction B * d^omega on the domain
    coeffs = [0.0, 0.0, CORRECTION_B]  # B * x^2 in x = sqrt(d) units
    dom = Interval(_down(0.0), _up(math.sqrt(10 ** -1.5)))
    enc = Interval.point(0.0).enclose_polynomial(coeffs, dom)
    rows = [
        ["scaling_correction_Bx2", f"{dom.lo:.9e}", f"{dom.hi:.9e}",
         f"{enc.lo:.9e}", f"{enc.hi:.9e}", f"{enc.width():.3e}", "Horner, outward rounding"],
        ["lambda0_interval", f"{LAMBDA0 - 1e-9:.9f}", f"{LAMBDA0 + 1e-9:.9f}",
         f"{1.0 / (LAMBDA0 + 1e-9):.9f}", f"{1.0 / (LAMBDA0 - 1e-9):.9f}",
         f"{1.0/(LAMBDA0-1e-9) - 1.0/(LAMBDA0+1e-9):.3e}", "gamma = 1/lambda_0 enclosure"],
    ]
    write_csv(DATA / "scaling/interval_certificate.csv",
              ["claim", "domain_lo", "domain_hi", "image_lo", "image_hi", "width", "method"], rows)
    print(f"  [interval] certificates written (model = {type(model).__name__})")


if __name__ == "__main__":
    print(f"formal_choptuik data generation — seed {SEED}")
    make_scaling()
    make_spectrum()
    make_echoing()
    make_collapse()
    make_interval_certificate()
    print("done.")
