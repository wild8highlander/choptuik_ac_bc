# -*- coding: utf-8 -*-
"""Smoke-проверки пакета: импорты, двуязычные метки, результаты и фигуры."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_all_experiment_modules_import():
    import exp1_sh3_bridge  # noqa: F401
    import exp2_dsi4  # noqa: F401
    import exp3_hurwitz  # noqa: F401
    import exp4_qnm  # noqa: F401
    import exp5_qcd  # noqa: F401
    import exp6_census_224  # noqa: F401
    import exp7_e1_threshold  # noqa: F401


def test_figlabels_bilingual():
    from figlabels import L
    assert "ru" in L and "en" in L
    for key in ("ladder_title", "dsi_title"):
        for lang in ("ru", "en"):
            if key in L[lang]:
                assert isinstance(L[lang][key], str)


def test_results_jsons_present_and_parse():
    rdir = os.path.join(ROOT, "results")
    files = sorted(f for f in os.listdir(rdir) if f.endswith(".json"))
    assert len(files) == 7, files
    for fn in files:
        with open(os.path.join(rdir, fn), encoding="utf-8") as f:
            json.load(f)


def test_figures_committed():
    for lang in ("fig_ru", "fig_en"):
        d = os.path.join(ROOT, lang)
        pngs = [f for f in os.listdir(d) if f.endswith(".png")]
        assert len(pngs) == 15, (lang, len(pngs))


def test_reports_present():
    r = os.path.join(ROOT, "reports")
    expected = [
        "Choptyuk_OpenProblems_Report_RU.pdf",
        "Choptyuk_OpenProblems_Report_EN.pdf",
        "Choptyuk_OpenProblems_Report_RU.docx",
        "Choptyuk_OpenProblems_Report_EN.docx",
        "Choptyuk_Analytic_Attack_RU.pdf",
        "Choptyuk_Analytic_Attack_EN.pdf",
        "Choptyuk_Analytic_Attack_RU.docx",
        "Choptyuk_Analytic_Attack_EN.docx",
    ]
    for fn in expected:
        assert os.path.exists(os.path.join(r, fn)), fn
