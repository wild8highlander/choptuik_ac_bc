"""Page model: unitary entropy-flux curves and the Haar-averaging check."""
import math

import numpy as np
from chbridge import page as P
from chbridge.hawking import PAGE_FRACTION


def test_member_profile_values():
    ft = P.member_f_tilde()
    assert abs(ft["near_floor"] - 0.287708) < 1e-5
    assert abs(ft["mid"] - 0.268393) < 1e-5
    assert ft["saturated"] == 1.0


def test_curve_structure():
    """S_rad = S_BH before the Page time, S0 - S_BH after; kink at S0/2."""
    M0 = 4.5e22
    tau, S_bh, S_rad, S0 = P.curves(M0, n=240)
    assert len(tau) == 240
    young = tau < PAGE_FRACTION
    old = ~young
    assert np.allclose(S_rad[young], S_bh[young])
    assert np.allclose(S_rad[old], S0 - S_bh[old])
    # the kink meets at S0/2: at t_Page, S_BH = S0 * (1-tau)^{2/3} = S0/2
    u = (1.0 - PAGE_FRACTION) ** (1.0 / 3.0)
    assert abs(u ** 2 - 0.5) < 1e-12


def test_haar_formula_known_case():
    """Page formula for 2 x 2: S = 1/3 nats = 0.48016... bits."""
    S = P.haar_avg_entropy(2, 2)
    assert abs(S - (1.0 / 3.0) / math.log(2)) < 1e-12


def test_haar_known_case_2x4():
    """Page formula for 2 x 4 (m<=n): 0.509524 nats = 0.735105 bits (Sen)."""
    S = P.haar_avg_entropy(2, 4)
    assert abs(S - 0.509524 / math.log(2)) < 1e-5


def test_haar_requires_m_le_n():
    """The exact Page/Sen branch assumes m <= n; the project always
    orders the factors (lo, hi) before calling — mirrored here."""
    for a, b in ((3, 8), (8, 3)):
        lo, hi = min(a, b), max(a, b)
        S = P.haar_avg_entropy(lo, hi)
        assert S > 0


def test_haar_monotonic_in_partition():
    """Entropy of the smaller factor is maximal at the balanced cut."""
    dims = [(2 ** i, 2 ** (6 - i)) for i in range(1, 3)]
    lo = [P.haar_avg_entropy(min(a, b), max(a, b)) for a, b in dims]
    bal = P.haar_avg_entropy(2 ** 3, 2 ** 3)
    assert all(s < bal for s in lo)


def test_haar_mc_small_deviation():
    """Haar MC (seeded) agrees with the formula to < 0.02 bits (N<=5)."""
    rng = np.random.default_rng(7)
    for Ntot in (3, 4, 5):
        for Nbh in range(1, Ntot):
            d1, d2 = 2 ** Nbh, 2 ** (Ntot - Nbh)
            lo, hi = min(d1, d2), max(d1, d2)
            S_exact = P.haar_avg_entropy(lo, hi)
            vals = []
            for _ in range(400):
                psi = rng.normal(size=2 ** Ntot) + 1j * rng.normal(size=2 ** Ntot)
                psi /= np.linalg.norm(psi)
                rho = (psi.reshape(d1, d2) @ psi.reshape(d1, d2).conj().T)
                ev = np.linalg.eigvalsh(rho)
                ev = ev[ev > 1e-12]
                vals.append(-float(np.sum(ev * np.log(ev))) / math.log(2))
            assert abs(np.mean(vals) - S_exact) < 0.02, (Ntot, Nbh)
