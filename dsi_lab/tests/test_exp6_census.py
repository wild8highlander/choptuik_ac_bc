# -*- coding: utf-8 -*-
"""Эксперимент 6: перепись тилинга {7,3} из G = GL(3,2) ~= PSL(2,7).

Проверяем (одним прогоном part_A — она сама детерминирована):
  |G| = 168; перепись по порядкам {1:1, 2:21, 3:56, 4:42, 7:48};
  силовские n2=21, n3=28, n7=8; косеты V=56, E=84, F=24;
  Эйлер V-E+F = -4 (род 3); тождество 7F = 3V = 2E = |G|;
  граф Клейна: 56 вершин, степень 3, обхват 7, 84 ребра;
  граневая смежность: 24 вершины, степень 7.
Плюс провенанс: 224 = 4V = 8*n3, 672 = 4|G| = 3*224.
"""
import pytest

from exp6_census_224 import part_A


@pytest.fixture(scope="module")
def census():
    return part_A()


def test_group_and_census(census):
    assert census["group_order"] == 168
    assert census["count_by_order"] == {1: 1, 2: 21, 3: 56, 4: 42, 7: 48}


def test_sylow_numbers(census):
    assert census["sylow"] == {"n2": 21, "n3": 28, "n7": 8}


def test_cosets_and_euler(census):
    assert (census["V"], census["E"], census["F"]) == (56, 84, 24)
    assert census["euler"] == -4  # род 3


def test_valence_identity(census):
    assert 7 * census["F"] == 3 * census["V"] == 2 * census["E"] == 168


def test_klein_graph(census):
    kg = census["klein_graph"]
    assert kg["vertices"] == 56
    assert kg["degree"] == 3
    assert kg["edges"] == 84
    assert kg["girth"] == 7


def test_face_adjacency(census):
    fa = census["face_adjacency"]
    assert fa["vertices"] == 24
    assert fa["degree"] == 7
    assert fa["edges"] == 84


def test_provenance_224_672(census):
    V, F, n3, G = census["V"], census["F"], census["sylow"]["n3"], \
        census["group_order"]
    assert 4 * V == 224           # 4 * вершины
    assert 8 * n3 == 224          # 8 * силовские 3-подгруппы
    assert 4 * G == 672           # 4 * |PSL(2,7)|
    assert 3 * 224 == 672
    assert F * 28 == 672          # 24 * 28 (грани * n3)
