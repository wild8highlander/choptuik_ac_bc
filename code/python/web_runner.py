#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
web_runner.py — stdin/stdout bridge between the Next.js API and the canonical
qcd_bridge_engine. Designed to be invoked via subprocess from /api/run and
/api/report.

Usage (run mode):
    echo '{"mode":"custom","sections":[1,2],...}' | python3 web_runner.py run

Usage (report mode — writes files to --output-dir, prints a JSON manifest):
    echo '{"mode":"custom","sections":[1,2,3],"format":"pdf",...}' | \
        python3 web_runner.py report --output-dir /path/to/web/output

Author: Ishak Khamzatovich Isaev (ORCID 0009-0003-7299-0701)
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

# Add this directory to sys.path so we can import the engine & report modules.
sys.path.insert(0, str(Path(__file__).parent))

from qcd_bridge_engine import QCDBridgeConfig, run_all  # type: ignore
from report_engine import ReportEngine                    # type: ignore  # noqa: E402


def _to_serializable(obj: Any) -> Any:
    """Recursively convert numpy / dataclass objects to JSON-safe types."""
    try:
        import numpy as np  # type: ignore
    except ImportError:
        np = None
    if isinstance(obj, dict):
        return {k: _to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_serializable(v) for v in obj]
    if np is not None:
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
    if isinstance(obj, (bool, int, float, str)) or obj is None:
        return obj
    try:
        from dataclasses import is_dataclass, asdict as _asdict
        if is_dataclass(obj):
            return _to_serializable(_asdict(obj))
    except Exception:
        pass
    return str(obj)


def _build_config(payload: Dict[str, Any]) -> QCDBridgeConfig:
    """Map a JSON payload (from the web app) onto QCDBridgeConfig."""
    sections = payload.get("sections") or list(range(1, 10))
    cfg = QCDBridgeConfig(
        mode=payload.get("mode", "custom"),
        sections=list(sections),
        kappa_values=list(payload.get("kappa_values", QCDBridgeConfig().kappa_values)),
        N_values=list(payload.get("N_values", QCDBridgeConfig().N_values)),
        kappa_T_custom=float(payload.get("kappa_T_custom", 8.45)),
        N_custom=int(payload.get("N_custom", 28)),
        n_flavors=int(payload.get("n_flavors", 6)),
        seed=int(payload.get("seed", 42)),
        language=str(payload.get("language", "en")),
        output_dir=str(payload.get("output_dir", "reports")),
        report_formats=list(payload.get("report_formats",
                                        ["txt", "csv", "md", "pdf", "html", "docx", "json"])),
    )
    return cfg


def _read_payload() -> Dict[str, Any]:
    """Read a JSON payload from stdin (or empty dict if no stdin)."""
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON on stdin: {e}"}), file=sys.stderr)
        sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Web runner for the Choptuik-QCD bridge engine.")
    parser.add_argument("command", choices=["run", "report"],
                        help="'run' emits the full QCDResult JSON to stdout; "
                             "'report' writes report files to --output-dir and prints a manifest.")
    parser.add_argument("--output-dir", type=str, default="/home/z/my-project/choptuik_ac_bc/code/web/output",
                        help="Output directory for report files (report mode only).")
    parser.add_argument("--format", type=str, default=None,
                        help="Single report format (report mode only). Overrides report_formats.")
    args = parser.parse_args()

    payload = _read_payload()
    try:
        cfg = _build_config(payload)
        if args.command == "report":
            # Allow single-format override.
            if args.format:
                cfg.report_formats = [args.format]
            # Always write to the web output dir.
            cfg.output_dir = args.output_dir
        result = run_all(cfg)
    except Exception as e:
        traceback.print_exc()
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 1

    serializable = _to_serializable(asdict(result))

    if args.command == "run":
        # Emit the full result JSON to stdout.
        sys.stdout.write(json.dumps(serializable, ensure_ascii=False, default=str))
        sys.stdout.write("\n")
        return 0

    # report mode: write files, then print a manifest with paths.
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    engine = ReportEngine(output_dir=str(out_dir), language=cfg.language)
    paths = engine.generate(result, formats=cfg.report_formats)
    manifest = {
        "ok": True,
        "output_dir": str(out_dir),
        "paths": paths,
        "formats_requested": list(cfg.report_formats),
        "timestamp": result.timestamp,
        "elapsed_s": result.elapsed_s,
    }
    sys.stdout.write(json.dumps(manifest, ensure_ascii=False, default=str))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
