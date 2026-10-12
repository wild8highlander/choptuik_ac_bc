"""Continued-fraction machinery behind the 9/224 observation (exp2/exp6).

The measured c_K3 has the continued fraction whose convergent 9/224 is the
DSI-4 observation; experiment 2 ranked its exclusivity and experiment 6
proved the census-uniqueness lemma. This module keeps the canonical,
reusable implementation.
"""

from __future__ import annotations

from fractions import Fraction

from dsilab.constants import C_K3_MEASURED


def continued_fraction(x: float, max_terms: int = 24) -> list[int]:
    """Simple continued fraction [a0; a1, a2, ...] of a positive float.

    Deterministic; stops at max_terms or when the remainder is exhausted.
    """
    terms: list[int] = []
    r = x
    for _ in range(max_terms):
        a = int(r)
        terms.append(a)
        frac = r - a
        if frac < 1e-13:
            break
        r = 1.0 / frac
    return terms


def convergents_of(cf: list[int]) -> list[Fraction]:
    """Convergents h_k/k_k of a continued fraction, exact rationals."""
    convs: list[Fraction] = []
    h_prev, h = 1, cf[0]  # h_{-2}, h_{-1}
    k_prev, k = 0, 1  # k_{-2}, k_{-1}
    convs.append(Fraction(h, k))
    for a in cf[1:]:
        h_prev, h = h, a * h + h_prev
        k_prev, k = k, a * k + k_prev
        convs.append(Fraction(h, k))
    return convs


def c_k3_convergents() -> list[tuple[Fraction, Fraction]]:
    """(convergent, |p/q − c_meas|·q) for the CF of the measured c_K3.

    The rank of the observation: 9/224 = [0; 24, 1, 8, ...] is a convergent
    whose |error|·q is minimal among small denominators (rank #1 for
    q <= 2000 per exp2 B).
    """
    cf = continued_fraction(C_K3_MEASURED)
    out: list[tuple[Fraction, Fraction]] = []
    target = Fraction(C_K3_MEASURED).limit_denominator(10**9)
    for conv in convergents_of(cf):
        err_q = abs(conv - target) * conv.denominator
        out.append((conv, err_q))
    return out


def is_census_fraction(fr: Fraction) -> bool:
    """Census filter of exp6 C: denominator 7-smooth within the census
    budget v2 <= 6, v3 <= 1, v7 <= 1 (so 224 = 2^5·7 qualifies)."""
    q = fr.denominator
    for p, vmax in ((2, 6), (3, 1), (7, 1)):
        v = 0
        while q % p == 0:
            q //= p
            v += 1
        if v > vmax:
            return False
    return q == 1
