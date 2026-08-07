"""Interactive CLI menu for the Choptyuk verification suite.

Provides a full interactive menu with:
- Run full verification
- Run simulations
- Configure all parameters
- Build custom hypotheses
- Generate reports in any format
- Generate plots
- View results
- Save/load configurations
"""

from __future__ import annotations
import json
import sys
import os
from pathlib import Path
from typing import Dict, Optional
import numpy as np
import logging

from ..core.klein_curve import KleinCurve
from ..core.spinor_phases import SpinorPhases
from ..core.dirac_operator import DiracOperator
from ..core.choptyuk_formula import ChoptyukFormula
from ..core.surfaces import SurfaceSpec, BOLZA, BRING, MACBEATH
from ..core.qnm import QNMPredictor
from ..core.hypothesis import HypothesisTester, HypothesisConfig
from ..verification.verify_all import VerificationSuite
from ..simulation.simulator import Simulator
from ..visualization.plots import PlotGenerator
from ..reporting.report_writer import ReportWriter

logger = logging.getLogger(__name__)


class InteractiveMenu:
    """Full interactive CLI menu system."""

    def __init__(self, output_base: str = "output"):
        self.output_base = Path(output_base)
        self.output_base.mkdir(parents=True, exist_ok=True)

        # Default parameters (all customizable)
        self.params = {
            "genus": 3, "K": -1.0, "psl_order": 168, "lambda_1": 3.838,
            "delta_A": None, "delta_B": None, "delta_C": None,
            "k_struct": 22, "c4": 0.125, "c6": 0.5,
            "delta_obs": 3.443, "b_ch_obs": 0.377,
            "dpi": 600, "precision": 15,
        }
        self.results = None
        self.sim_results = None
        self.logs = ""
        self.plot_paths = []
        self.report_paths = {}

    def run(self):
        """Main menu loop."""
        while True:
            self._print_header()
            choice = input("\n  Select option [1-10]: ").strip()
            if choice == "1":
                self._run_verification()
            elif choice == "2":
                self._run_simulation()
            elif choice == "3":
                self._configure_params()
            elif choice == "4":
                self._custom_hypothesis()
            elif choice == "5":
                self._generate_reports()
            elif choice == "6":
                self._generate_plots()
            elif choice == "7":
                self._view_results()
            elif choice == "8":
                self._load_preset()
            elif choice == "9":
                self._save_config()
            elif choice == "10" or choice.lower() == "q":
                print("\n  Exiting. All outputs saved to:", self.output_base)
                break
            else:
                print("  Invalid choice. Try again.")

    def _print_header(self):
        print("\n" + "=" * 60)
        print("  CHOPTYUK SPINOR CORRECTIONS - Interactive Menu")
        print("=" * 60)
        print("  1. Run Full Verification")
        print("  2. Run Simulations (parameter sweeps)")
        print("  3. Configure Parameters")
        print("  4. Build Custom Hypothesis")
        print("  5. Generate Reports (docx/pdf/txt/md/csv/html/json)")
        print("  6. Generate Plots (600 DPI PNG + PDF + SVG)")
        print("  7. View Results")
        print("  8. Load Preset Configuration")
        print("  9. Save Current Configuration")
        print("  10. Exit")

    def _run_verification(self):
        print("\n--- Running Full Verification ---")
        suite = VerificationSuite(
            genus=self.params["genus"], K=self.params["K"],
            psl_order=self.params["psl_order"], lambda_1=self.params["lambda_1"],
            delta_A=self.params["delta_A"], delta_B=self.params["delta_B"],
            delta_C=self.params["delta_C"], k_struct=self.params["k_struct"],
            c4=self.params["c4"], c6=self.params["c6"],
            delta_obs=self.params["delta_obs"], b_ch_obs=self.params["b_ch_obs"],
        )
        self.results = suite.run()
        self.logs = suite.get_logs()
        print("  Verification complete.")
        ch = self.results.get("choptyuk", {})
        print(f"  Delta_bC = {ch.get('delta_bc', 0):.6f} (dev {ch.get('deviation_bc_pct', 0):.3f}%)")
        print(f"  Delta_Ch (full) = {ch.get('delta_ch_full', 0):.6f} (dev {ch.get('deviation_full_pct', 0):.3f}%)")

    def _run_simulation(self):
        print("\n--- Running Simulations ---")
        sim = Simulator(delta_obs=self.params["delta_obs"])

        print("  1. Sweep delta_C")
        print("  2. Sweep lambda_1")
        print("  3. Convergence analysis")
        print("  4. Run all simulations")
        choice = input("  Select [1-4]: ").strip()

        dC = self.params["delta_C"] or np.pi / 7
        if choice in ("1", "4"):
            print("  Sweeping delta_C [0.1, 1.0]...")
            sim.sweep_delta_C(n_points=200, lambda_D2=self.params["lambda_1"] + self.params["K"])
        if choice in ("2", "4"):
            print("  Sweeping lambda_1 [2.0, 6.0]...")
            sim.sweep_lambda_1(delta_C=dC, R=2 * self.params["K"])
        if choice in ("3", "4"):
            print("  Convergence analysis (order 1..10)...")
            sim.convergence_analysis(max_order=10, delta_C=dC)

        self.sim_results = sim.results
        self.logs += "\n" + sim.get_logs()
        print("  Simulations complete.")

    def _configure_params(self):
        print("\n--- Configure Parameters ---")
        print("  Current values:")
        for k, v in self.params.items():
            print(f"    {k} = {v}")
        print("\n  Enter parameter name and value (e.g., 'lambda_1 4.0')")
        print("  Enter 'done' to finish, 'reset' for defaults")
        while True:
            inp = input("  > ").strip()
            if inp.lower() == "done":
                break
            if inp.lower() == "reset":
                self.params = {
                    "genus": 3, "K": -1.0, "psl_order": 168, "lambda_1": 3.838,
                    "delta_A": None, "delta_B": None, "delta_C": None,
                    "k_struct": 22, "c4": 0.125, "c6": 0.5,
                    "delta_obs": 3.443, "b_ch_obs": 0.377,
                    "dpi": 600, "precision": 15,
                }
                print("  Reset to defaults.")
                break
            try:
                parts = inp.split()
                key = parts[0]
                if key in self.params:
                    val = float(parts[1]) if parts[1] not in ("None", "none") else None
                    if key in ("genus", "psl_order", "k_struct", "dpi", "precision"):
                        val = int(parts[1])
                    self.params[key] = val
                    print(f"    {key} = {val}")
                else:
                    print(f"    Unknown parameter: {key}")
            except (IndexError, ValueError):
                print("    Invalid input. Use: parameter_name value")

    def _custom_hypothesis(self):
        print("\n--- Build Custom Hypothesis ---")
        name = input("  Hypothesis name: ").strip() or "custom"
        desc = input("  Description: ").strip() or ""

        print("  Custom delta_C (enter value or 'default' for pi/7):")
        dC_input = input("  > ").strip()
        dC = None if dC_input in ("default", "") else float(dC_input)

        print("  Custom lambda_D2 (enter value or 'default' for 3.338):")
        lam_input = input("  > ").strip()
        lam = None if lam_input in ("default", "") else float(lam_input)

        print("  Custom k_struct (enter value or 'default' for 22):")
        k_input = input("  > ").strip()
        k = None if k_input in ("default", "") else int(k_input)

        config = HypothesisConfig(name=name, description=desc,
                                  custom_delta_C=dC,
                                  custom_lambda_D2=lam,
                                  custom_k_struct=k)
        tester = HypothesisTester(delta_obs=self.params["delta_obs"])
        result = tester.test_hypothesis(config)

        print(f"\n  Result: Delta_Ch = {result.delta_ch_full:.6f}")
        print(f"  Deviation = {result.deviation:.3f}%")
        print(f"  Status: {'PASS' if result.passed else 'FAIL'} (tolerance {tester.tolerance}%)")

        print("\n  Parameter sweep? (y/n):")
        if input("  > ").strip().lower() == "y":
            print("  Sweep parameter (delta_C / lambda_D2 / k_struct):")
            param = input("  > ").strip()
            print("  Start value:")
            start = float(input("  > "))
            print("  End value:")
            end = float(input("  > "))
            print("  Number of points:")
            n = int(input("  > "))
            values = np.linspace(start, end, n).tolist()
            results = tester.parameter_sweep(param, values, config)
            print(f"  Sweep complete: {len(results)} points tested")
            best = min(results, key=lambda r: r.deviation)
            print(f"  Best: {best.name}, deviation = {best.deviation:.3f}%")

    def _generate_reports(self):
        if not self.results:
            print("  Run verification first (option 1).")
            return
        print("\n--- Generate Reports ---")
        print("  Formats: docx, pdf, txt, md, csv, html, json")
        fmt_input = input("  Enter formats (comma-separated, or 'all'): ").strip()
        if fmt_input.lower() in ("all", ""):
            formats = ["docx", "pdf", "txt", "md", "csv", "html", "json"]
        else:
            formats = [f.strip() for f in fmt_input.split(",")]

        writer = ReportWriter(str(self.output_base / "reports"), formats)
        self.report_paths = writer.generate_all(self.results, self.logs)
        print(f"  Generated {len(self.report_paths)} reports:")
        for fmt, path in self.report_paths.items():
            print(f"    {fmt}: {path}")

    def _generate_plots(self):
        print("\n--- Generate Plots ---")
        plotter = PlotGenerator(str(self.output_base / "plots"), self.params["dpi"])
        self.plot_paths = plotter.generate_all(
            self.results or {}, self.sim_results
        )
        print(f"  Generated {len(self.plot_paths)} plot files:")
        for p in self.plot_paths:
            print(f"    {p}")

    def _view_results(self):
        if not self.results:
            print("  No results yet. Run verification first.")
            return
        print("\n--- Results Summary ---")
        ch = self.results.get("choptyuk", {})
        print(f"  Delta_bC = {ch.get('delta_bc', 0):.6f} (dev {ch.get('deviation_bc_pct', 0):.3f}%)")
        print(f"  Delta_Ch (base) = {ch.get('delta_ch_base', 0):.6f} (dev {ch.get('deviation_ch_pct', 0):.3f}%)")
        print(f"  Delta_Ch (full) = {ch.get('delta_ch_full', 0):.6f} (dev {ch.get('deviation_full_pct', 0):.3f}%)")
        print(f"  b_Ch = {ch.get('b_ch', 0):.6f} (dev {ch.get('deviation_b_ch_pct', 0):.3f}%)")
        if self.plot_paths:
            print(f"\n  Plot files: {len(self.plot_paths)}")
        if self.report_paths:
            print(f"  Report files: {len(self.report_paths)}")

    def _load_preset(self):
        print("\n--- Load Preset ---")
        print("  Available: standard, high_precision, ligo_analysis")
        name = input("  Preset name: ").strip()
        preset_dir = Path(__file__).parent.parent.parent / "presets"
        preset_file = preset_dir / f"{name}.json"
        if preset_file.exists():
            with open(preset_file) as f:
                preset = json.load(f)
            print(f"  Loaded preset: {preset.get('name', name)}")
            print(f"  Description: {preset.get('description', '')}")
        else:
            print(f"  Preset not found: {preset_file}")

    def _save_config(self):
        print("\n--- Save Configuration ---")
        name = input("  Config name: ").strip() or "custom"
        config_path = self.output_base / f"config_{name}.json"
        with open(config_path, 'w') as f:
            json.dump(self.params, f, indent=2, default=str)
        print(f"  Saved to: {config_path}")
