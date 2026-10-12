"""Artifact-level tests: figures, documents, per-profile and per-shape pins."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

BUILDERS = ["fig_gap", "fig_sigma", "fig_bridge", "fig_response", "fig_escape",
            "fig_ystring", "fig_wkb", "fig_bootstrap", "fig_phase_map",
            "fig_shares", "fig_vortex_spec", "fig_barrier", "fig_asymmetry",
            "fig_boot2", "fig_margin", "fig_cover"]

DOCS = ["README.md", "README.ru.md", "RESULTS.md", "RESULTS.ru.md",
        "ROADMAP.md", "ROADMAP.ru.md", "CHANGELOG.md", "CITATION.cff",
        "VERSION", "Makefile", "requirements.txt", "docs/theory.md",
        "docs/theory.ru.md", "docs/phase_map.md", "docs/phase_map.ru.md",
        "docs/evidence_engine.md", "docs/evidence_engine.ru.md",
        "docs/asymmetry_lock.md", "docs/asymmetry_lock.ru.md"]


@pytest.mark.parametrize("name", BUILDERS)
def test_figure_variants(name):
    figdir = ROOT / "docs" / "figures"
    for lang in ("ru", "en"):
        for theme in ("light", "dark"):
            assert (figdir / f"{name}_{lang}_{theme}.png").exists(), name


HIRES = ["fig_gap", "fig_sigma", "fig_bridge", "fig_response", "fig_escape",
         "fig_ystring", "fig_wkb", "fig_phase_map", "fig_shares",
         "fig_vortex_spec", "fig_barrier", "fig_asymmetry", "fig_cover"]


@pytest.mark.parametrize("name", HIRES)
def test_figure_hires(name):
    figdir = ROOT / "docs" / "figures"
    assert (figdir / f"{name}_ru_light_hires.png").exists(), name


@pytest.mark.parametrize("name", DOCS)
def test_doc_exists(name):
    assert (ROOT / name).exists(), name


PROFILES = ["step", "tent", "cosw", "quad", "expo", "sign2", "saw", "sgn3", "sinw"]


@pytest.mark.parametrize("name", PROFILES)
def test_profile_unit_and_drop(name):
    profs = {p["name"]: p for p in
             json.loads((ROOT / "data" / "c12_profiles.json").read_text())}
    p = profs[name]
    assert p["sup"] <= 1.0 + 1e-12
    assert -2.0 - 1e-12 <= p["drop_at_unit_eta"] <= 2.0 + 1e-12
    # at least the step profile must attain the exact worst case +2
    assert max(q["drop_at_unit_eta"] for q in profs.values()) == 2.0


@pytest.mark.parametrize("i", range(9))
def test_ystring_shapes_positive(i):
    shapes = json.loads((ROOT / "data" / "c6_y_spectrum.json").read_text())["shapes"]
    s = shapes[i]
    assert s["E_Y"] > 0 and s["arm_total"] > 0
    # vertex inside the triangle bounding box
    assert s["vertex"][0] >= 0.0 and s["vertex"][1] >= 0.0
