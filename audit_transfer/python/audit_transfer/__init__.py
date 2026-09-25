#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_transfer — пакет «Аудит и перенос» фреймворка Исаева–Чоптьюка.

Модули:
    monograph_audit   — аудиторское ядро: поправки b-C/a-C и каталог E1–E7.
    dsi_closure       — Задача 2: DSI-замыкание c_K3 = 0.04018 (λ = 22 = b₂(K3)).
    stability_lemma   — Задача 3: лемма Ш.3 (равномерная устойчивость дефекта).
    figures           — генерация всех PNG (figures/) и JSON (results/).

Точка входа оркестратора: ../run_all.py
"""

__version__ = "1.0.0"
__all__ = ["monograph_audit", "dsi_closure", "stability_lemma", "figures"]
