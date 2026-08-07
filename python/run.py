#!/usr/bin/env python3
"""Entry point for the Choptyuk Spinor Corrections verification suite.

Usage:
  Interactive mode:     python run.py
  Non-interactive:      python run.py --mode verify --non-interactive --output-dir output
  With config:          python run.py --config config/default_config.json
  Specific preset:      python run.py --preset standard
"""

import argparse
import json
import sys
import os
from pathlib import Path
import logging

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent))

from src.verification.verify_all import VerificationSuite
from src.simulation.simulator import Simulator
from src.visualization.plots import PlotGenerator
from src.reporting.report_writer import ReportWriter
from src.ui.interactive_menu import InteractiveMenu


def setup_logging(output_dir: str, level: str = "INFO"):
    """Configure logging to both console and file."""
    log_dir = Path(output_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "execution.log", encoding="utf-8"),
        ],
    )


def run_non_interactive(args):
    """Run in non-interactive mode (for CI/scripting)."""
    output_dir = args.output_dir or "output"
    setup_logging(output_dir)

    # Load config if provided
    config = {}
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    # Load preset if provided
    preset = {}
    if args.preset:
        preset_file = Path(__file__).parent / "presets" / f"{args.preset}.json"
        if preset_file.exists():
            with open(preset_file) as f:
                preset = json.load(f)

    # Create output directory
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Run verification
    suite = VerificationSuite()
    results = suite.run()
    logs = suite.get_logs()

    # Run simulations
    sim = Simulator()
    sim.sweep_delta_C()
    sim.sweep_lambda_1()
    sim.convergence_analysis()

    # Generate plots
    plotter = PlotGenerator(str(out / "plots"))
    plot_paths = plotter.generate_all(results, sim.results)

    # Generate reports
    writer = ReportWriter(str(out / "reports"))
    report_paths = writer.generate_all(results, logs)

    # Save raw results
    with open(out / "results.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    logging.info(f"Output saved to: {out}")
    logging.info(f"Plots: {len(plot_paths)} files")
    logging.info(f"Reports: {len(report_paths)} files")


def main():
    parser = argparse.ArgumentParser(
        description="Choptyuk Spinor Corrections - Verification & Simulation"
    )
    parser.add_argument("--mode", choices=["verify", "simulate", "interactive"],
                        default="interactive", help="Run mode")
    parser.add_argument("--non-interactive", action="store_true",
                        help="Run without interactive prompts")
    parser.add_argument("--output-dir", default="output",
                        help="Output directory")
    parser.add_argument("--config", default=None,
                        help="Path to configuration JSON")
    parser.add_argument("--preset", default=None,
                        help="Preset name (standard, high_precision, ligo_analysis)")
    parser.add_argument("--log-level", default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    args = parser.parse_args()

    if args.non_interactive or args.mode != "interactive":
        run_non_interactive(args)
    else:
        setup_logging(args.output_dir, args.log_level)
        menu = InteractiveMenu(args.output_dir)
        menu.run()


if __name__ == "__main__":
    main()
