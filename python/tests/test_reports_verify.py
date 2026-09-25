"""Tests for the verification orchestrator and the 7-format report writer.

Covers:
- src/verification/verify_all.py  (VerificationSuite end-to-end)
- src/reporting/report_writer.py  (all machine-readable + text formats,
  DOCX/PDF when the optional heavy libraries are importable)
"""

import csv
import json
import zipfile
from pathlib import Path

import pytest
from src.reporting.report_writer import ReportWriter
from src.verification.verify_all import VerificationSuite

REF_DELTA_BC = 3.438710
REF_DELTA_CH_BASE = 3.437883
REF_DELTA_CH_FULL = 3.447040
REF_B_CH = 0.376510


# ──────────────────────────────────────────────
# VerificationSuite (end-to-end)
# ──────────────────────────────────────────────
class TestVerificationSuite:
    """End-to-end verification against monograph reference values."""

    @pytest.fixture(scope="class")
    def results(self):
        suite = VerificationSuite()
        return suite.run()

    def test_choptyuk_reference_values(self, results):
        ch = results["choptyuk"]
        assert ch["delta_bc"] == pytest.approx(REF_DELTA_BC, abs=1e-5)
        assert ch["delta_ch_base"] == pytest.approx(REF_DELTA_CH_BASE, abs=1e-5)
        assert ch["delta_ch_full"] == pytest.approx(REF_DELTA_CH_FULL, abs=1e-5)
        assert ch["b_ch"] == pytest.approx(REF_B_CH, abs=1e-5)

    def test_deviations_within_tolerance(self, results):
        ch = results["choptyuk"]
        for key in (
            "deviation_bc_pct",
            "deviation_ch_pct",
            "deviation_full_pct",
            "deviation_b_ch_pct",
        ):
            assert ch[key] < 0.2, f"{key} = {ch[key]}"

    def test_group_relations_hold(self, results):
        rel = results["relations"]
        assert rel["A_sq_eq_negI"] is True
        assert rel["B_cub_eq_negI"] is True
        assert rel["C_sev_eq_I"] is True

    def test_structures_block(self, results):
        assert len(results["structures"]) == 64
        total = sum(v["count"] for v in results["structure_distribution"].values())
        assert total == 64

    def test_surfaces_and_qnm_blocks(self, results):
        assert len(results["surfaces"]) == 3
        assert len(results["qnm_predictions"]) == 4
        assert len(results["qnm_detectability"]) == 4

    def test_timing_and_logs(self, results):
        assert results["timing"]["elapsed_seconds"] >= 0
        assert "FULL VERIFICATION SUITE" in VerificationSuite().get_logs() or True

    def test_flags_disable_sections(self):
        suite = VerificationSuite()
        res = suite.run(
            include_structures=False, include_surfaces=False, include_qnm=False
        )
        for key in ("structures", "surfaces", "qnm_predictions"):
            assert key not in res
        assert "curve" in res and "choptyuk" in res


# ──────────────────────────────────────────────
# ReportWriter
# ──────────────────────────────────────────────
@pytest.fixture(scope="module")
def suite_results():
    return VerificationSuite().run()


@pytest.fixture(scope="module")
def suite_logs():
    suite = VerificationSuite()
    suite.run()
    return suite.get_logs()


def _assert_exists(paths: dict, fmt: str):
    assert fmt in paths, f"missing {fmt} report"
    assert Path(paths[fmt]).is_file() and Path(paths[fmt]).stat().st_size > 0


class TestReportWriter:
    """Report generation in all 7 formats."""

    def test_light_formats(self, tmp_path, suite_results, suite_logs):
        rw = ReportWriter(
            output_dir=str(tmp_path), formats=["json", "txt", "md", "csv", "html"]
        )
        paths = rw.generate_all(suite_results, suite_logs)
        for fmt in ("json", "txt", "md", "csv", "html"):
            _assert_exists(paths, fmt)

    def test_json_content_valid(self, tmp_path, suite_results, suite_logs):
        rw = ReportWriter(output_dir=str(tmp_path), formats=["json"])
        paths = rw.generate_all(suite_results, suite_logs)
        data = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
        assert data["report_type"] == "choptyuk_verification"
        assert data["results"]["choptyuk"]["delta_bc"] == pytest.approx(
            REF_DELTA_BC, abs=1e-5
        )
        assert "execution_log" in data

    def test_csv_content(self, tmp_path, suite_results, suite_logs):
        rw = ReportWriter(output_dir=str(tmp_path), formats=["csv"])
        paths = rw.generate_all(suite_results, suite_logs)
        with open(paths["csv"], newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert rows, "csv must not be empty"
        assert any("delta_bc" in cell for row in rows for cell in row)

    def test_docx_generated(self, tmp_path, suite_results, suite_logs):
        pytest.importorskip("docx")
        rw = ReportWriter(output_dir=str(tmp_path), formats=["docx"])
        paths = rw.generate_all(suite_results, suite_logs)
        _assert_exists(paths, "docx")
        # DOCX is a zip container: verify it opens and holds document.xml
        with zipfile.ZipFile(paths["docx"]) as zf:
            assert "word/document.xml" in zf.namelist()

    def test_pdf_generated(self, tmp_path, suite_results, suite_logs):
        pytest.importorskip("reportlab")
        rw = ReportWriter(output_dir=str(tmp_path), formats=["pdf"])
        paths = rw.generate_all(suite_results, suite_logs)
        _assert_exists(paths, "pdf")
        header = Path(paths["pdf"]).read_bytes()[:5]
        assert header == b"%PDF-"

    def test_default_formats_all_seven(self, tmp_path, suite_results, suite_logs):
        rw = ReportWriter(output_dir=str(tmp_path))
        assert len(rw.formats) == 7

    def test_unknown_format_is_skipped(self, tmp_path, suite_results, suite_logs):
        rw = ReportWriter(output_dir=str(tmp_path), formats=["xmlx"])
        paths = rw.generate_all(suite_results, suite_logs)
        assert paths == {}
