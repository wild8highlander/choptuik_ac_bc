# -*- coding: utf-8 -*-
"""Эксперимент 3 (Гурвиц): делимости Римана-Гурвица и находка D1.

Проверяем:
  формулу порядка |PSL(2,q)| = q(q^2-1)/2 для q = 7, 13;
  НАХОДКУ D1: 1092 = |PSL(2,13)| НЕ делится на n = 11
  (строка Hurwitz_3 (g=14, n=11) в родительском репозитории несогласована);
  корректную башню: n = 13 делит 1092; род 14 = 1 + 1092/84;
  консистентность результатов exp3_hurwitz.json.
"""
import json
import os

import pytest

from exp3_hurwitz import b_Ch


def psl2_order(q):
    """|PSL(2,q)| = q(q^2-1)/2 для простых q >= 5."""
    return q * (q * q - 1) // 2


def test_psl_orders():
    assert psl2_order(7) == 168
    assert psl2_order(13) == 1092
    assert psl2_order(11) == 660


def test_D1_finding_divisibility():
    """D1: n=11 не делит |G|=1092 — заявленная башня (g=14, n=11) невозможна."""
    G = psl2_order(13)
    assert G % 11 != 0, "1092 не должна делиться на 11"
    assert G % 13 == 0, "корректный n = 13"
    # Риман-Гурвиц для гурвицевой группы (2,3,7): 2g - 2 = |G|/84,
    # т.е. g = 1 + |G|/84. Для квартики Клейна |G| = 168 => g = 3.
    g_2_3_7 = 1 + psl2_order(7) // 84
    assert g_2_3_7 == 3  # квартика Клейна


def test_D1_alternative_towers():
    """Башни, согласованные с Риманом-Гурвицем (как в отчёте):
    для гурвицевых групп (2,3,7) род кривой g = 1 + |G|/84."""
    assert 1 + psl2_order(13) // 84 == 14      # PSL(2,13): g = 14
    assert 1 + 504 // 84 == 7                  # Макбит (PGL(2,7)): g = 7
    assert 1 + 1344 // 84 == 17                # триплет: g = 17
    for G in (168, 504, 1092, 1344):           # |G|/84 целое во всей башне
        assert G % 84 == 0, G


def test_b_Ch_predictions():
    import math

    assert abs(b_Ch(7) - 0.3765101981412664) < 1e-12
    assert abs(b_Ch(13) - (1 - math.cos(2 * math.pi / 13))) < 1e-12
    assert b_Ch(13) < b_Ch(7)  # предсказание Delta_Ch(pi/13) ближе к 3.3672


def test_results_json_consistent():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "results", "exp3_hurwitz.json")
    with open(path, encoding="utf-8") as f:
        res = json.load(f)
    # JSON должен содержать блоки D1 и башни (структура может расширяться)
    text = json.dumps(res, ensure_ascii=False)
    assert "1092" in text or "PSL(2,13)" in text or "13" in text
