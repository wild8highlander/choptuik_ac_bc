"""Preregistration pins (v2.2.0, external audit points 10, 15 and 4).

The preregistration document is the package's commitment device: the
falsification criteria are frozen BEFORE the next engine run. These pins
make the commitment machine-checkable:

  1. the document exists in both languages and carries the frozen
     numbers;
  2. the constants module actually carries the frozen values;
  3. the verdict-token discipline holds everywhere it must;
  4. the self-referential "literature anchor" b_Ch_lit stays removed.
"""
import os

import chbridge.constants as K

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read()


def test_preregistration_documents_exist_and_carry_frozen_target():
    """PREREGISTRATION.{md,ru.md} exist and freeze 1.27 +- 0.05."""
    for name in ("PREREGISTRATION.md", "PREREGISTRATION.ru.md"):
        text = _read(name)
        assert "1.27" in text or "1,27" in text
        assert "0.05" in text or "0,05" in text
        assert "RETRO-LABEL" in text          # the no-post-hoc protocol
        assert "ANCHOR_ARITHMETIC" in text    # the token discipline


def test_frozen_constants_in_constants_module():
    """DGAMMA_TARGET/DGAMMA_TOL match the preregistered values."""
    assert K.DGAMMA_TARGET == 1.27
    assert K.DGAMMA_TOL == 0.05
    assert K.gamma_Ch == 0.374
    assert K.echo_delta == 3.44
    assert abs(K.DGAMMA_LIT - 1.28656) < 1e-12


def test_verdict_token_discipline_in_sources():
    """The campaign sources classify the anchor product, never a PASS."""
    c3 = _read(os.path.join("campaigns", "run_c3.py"))
    c3b = _read(os.path.join("campaigns", "run_c3b.py"))
    assert 'P_anchor_verdict": "ANCHOR_ARITHMETIC"' in c3
    assert 'P_anchor_verdict": "ANCHOR_ARITHMETIC"' in c3b
    assert "INCONCLUSIVE" in c3 and "INCONCLUSIVE" in c3b
    validate_src = _read(os.path.join("chbridge", "validate.py"))
    assert "not a measurement" in validate_src


def test_b_ch_lit_label_stays_removed():
    """Audit point 4 regression pin: the b_Ch_lit label must not come back.

    The honest removal comment in constants.py is allowed to NAME the
    former label (that is documentation); what is forbidden is a live
    constant definition, any import/use, or a JSON key carrying it.
    """
    constants_src = _read(os.path.join("chbridge", "constants.py"))
    bridge_src = _read(os.path.join("chbridge", "bridge.py"))
    # no live constant definition (the honest removal comment may QUOTE
    # the former line — that is documentation, not a definition)
    import re as _re
    assert not _re.search(r"^b_Ch_lit\s*=", constants_src, _re.MULTILINE)
    assert not hasattr(K, "b_Ch_lit")
    # in bridge.py every occurrence of the former label must live inside
    # a comment (documentation of the removal), never in code
    bad = [ln for ln in bridge_src.splitlines()
           if "b_Ch_lit" in ln and not ln.strip().startswith("#")]
    assert not bad, bad
    # the honest comment explaining the removal must be there
    assert "self-referential" in constants_src
    # and the claim ledger documents the removal as well
    ledger = _read(os.path.join("docs", "claim_ledger.md"))
    assert "b_Ch_lit" in ledger and "NOT" in ledger
    # the regenerated data table must not carry the key either
    summary = _read(os.path.join("data", "bridge",
                                 "collapse_verdict_summary.json"))
    assert "b_Ch_lit" not in summary
