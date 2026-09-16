# -*- coding: utf-8 -*-
"""Эксперимент 2 (DSI-4): c_K3 = 27/672 = 9/224.

Проверяем:
  b_Ch(7) = 1 - cos(2pi/7) и её связь с измеренным c_K3;
  сокращение 27/672 -> 9/224;
  9/224 — подходящая дробь цепной дроби измеренного c_K3;
  отклонение 9/224 от измеренного значения в пределах 0.1%.
"""
from fractions import Fraction

from exp2_dsi4 import C_K3_MEASURED, b_Ch, continued_fraction, convergents


def test_b_Ch_7_value():
    import math
    assert abs(b_Ch(7) - (1.0 - math.cos(2 * math.pi / 7))) < 1e-15
    assert abs(b_Ch(7) - 0.3765101981412664) < 1e-12


def test_fraction_reduction():
    assert Fraction(27, 672) == Fraction(9, 224)
    assert Fraction(9, 224).denominator == 224
    assert 224 == 4 * 56 and 56 == 8 * 7


def test_9_over_224_is_convergent():
    cf = continued_fraction(C_K3_MEASURED, 22)
    convs = convergents(cf, 12)
    pairs = {(p, q) for p, q in convs}
    assert (9, 224) in pairs, f"9/224 не найдена среди {sorted(pairs)}"
    assert (1, 24) in pairs, "1/24 должна быть предыдущей подходящей дробью"


def test_accuracy_within_0p1_percent():
    d = abs(Fraction(9, 224) - C_K3_MEASURED) / C_K3_MEASURED
    assert d < 1e-3, d  # < 0.1%
    # и жёстче: заявлено ~0.0025%
    assert d < 2.5e-5 * 10, d


def test_denominator_budget():
    """Переписной бюджет знаменателя: 224 = 2^5 * 7 (v2<=6, v3<=1, v7<=1)."""
    q = Fraction(9, 224).denominator
    assert q == 2 ** 5 * 7
    assert q % 3 != 0
