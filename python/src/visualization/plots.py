"""High-resolution plot generation for all monograph results.

Generates each plot as a SEPARATE file (no subplot blocks):
  - 600 DPI PNG for screen/documents
  - PDF for vector publication
  - SVG for web

Plot types:
  1. Spinor phase diagram
  2. Eigenvalue landscape (delta_C sweep)
  3. 64 spinor structure heatmap
  4. QNM frequency comparison
  5. Deviation analysis
  6. Convergence diagram
  7. Lambda_1 sweep
  8. Surface comparison
"""

from __future__ import annotations

import matplotlib
import numpy as np

matplotlib.use('Agg')
import logging
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

# Font setup for CJK + Latin
try:
    fm.fontManager.addfont('/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf')
except (OSError, ValueError):
    logger.warning("Custom font not available, using default")
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class PlotGenerator:
    """Generate all publication-quality plots.

    Each plot is saved as a separate file in both 600 DPI PNG and PDF/SVG.
    """

    def __init__(self, output_dir: str = "output/plots", dpi: int = 600):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
        self.fmt_vector = "pdf"
        logger.info(f"PlotGenerator: output={self.output_dir}, DPI={dpi}")

    def _save(self, fig: plt.Figure, name: str) -> list[str]:
        """Save figure in PNG + PDF + SVG.

        Returns:
            List of saved file paths.
        """
        paths = []
        png_path = self.output_dir / f"{name}.png"
        fig.savefig(png_path, dpi=self.dpi, bbox_inches='tight', facecolor='white')
        paths.append(str(png_path))

        pdf_path = self.output_dir / f"{name}.pdf"
        fig.savefig(pdf_path, bbox_inches='tight', facecolor='white')
        paths.append(str(pdf_path))

        svg_path = self.output_dir / f"{name}.svg"
        fig.savefig(svg_path, bbox_inches='tight', facecolor='white')
        paths.append(str(svg_path))

        plt.close(fig)
        logger.info(f"Saved: {name} -> {len(paths)} files")
        return paths

    def spinor_phase_diagram(self, delta_A: float, delta_B: float,
                              delta_C: float) -> list[str]:
        """Plot spinor phases on the unit circle."""
        fig, ax = plt.subplots(figsize=(8, 8))
        circle = plt.Circle((0, 0), 1, fill=False, color='gray', linewidth=1)
        ax.add_patch(circle)

        for delta, label, color in [
            (delta_A, r'$\delta_A = \pi/2$', '#e74c3c'),
            (delta_B, r'$\delta_B = \pi/3$', '#3498db'),
            (delta_C, r'$\delta_C = \pi/7$', '#2ecc71'),
        ]:
            x, y = np.cos(delta), np.sin(delta)
            ax.plot([0, x], [0, y], color=color, linewidth=2.5, label=label)
            ax.plot(x, y, 'o', color=color, markersize=10)
            ax.annotate(f'{delta:.4f}', (x, y), textcoords="offset points",
                       xytext=(10, 10), fontsize=10)

        ax.set_xlim(-1.3, 1.3)
        ax.set_ylim(-1.3, 1.3)
        ax.set_aspect('equal')
        ax.legend(fontsize=12, loc='upper left')
        ax.set_title('Spinor Phases on the Klein Curve', fontsize=14)
        ax.grid(True, alpha=0.3)
        return self._save(fig, 'spinor_phases')

    def eigenvalue_landscape(self, sweep_data: dict) -> list[str]:
        """Plot delta_C sweep showing eigenvalue landscape."""
        dC = np.array(sweep_data["delta_C"])
        delta_bc = np.array(sweep_data["delta_bc"])
        delta_ch = np.array(sweep_data["delta_ch_full"])
        deviation = np.array(sweep_data["deviation_pct"])

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), constrained_layout=True)

        ax1.plot(dC, delta_bc, 'b-', linewidth=2, label=r'$\Delta_{bC}$')
        ax1.plot(dC, delta_ch, 'r-', linewidth=2, label=r'$\Delta_{Ch}$ (full)')
        ax1.axhline(y=3.443, color='g', linestyle='--', label=r'$\Delta_{obs}$')
        ax1.axvline(x=np.pi/7, color='gray', linestyle=':', alpha=0.7, label=r'$\pi/7$')
        ax1.set_xlabel(r'$\delta_C$', fontsize=12)
        ax1.set_ylabel(r'$\Delta$', fontsize=12)
        ax1.legend(fontsize=11)
        ax1.set_title('Eigenvalue Landscape vs Spinor Phase', fontsize=13)
        ax1.grid(True, alpha=0.3)

        ax2.semilogy(dC, deviation + 1e-10, 'r-', linewidth=2)
        ax2.axvline(x=np.pi/7, color='gray', linestyle=':', alpha=0.7, label=r'$\pi/7$')
        ax2.set_xlabel(r'$\delta_C$', fontsize=12)
        ax2.set_ylabel('Deviation (%)', fontsize=12)
        ax2.set_title('Deviation from Observed', fontsize=13)
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)

        return self._save(fig, 'eigenvalue_landscape')

    def structure_heatmap(self, structures: list[dict]) -> list[str]:
        """Plot 64 spinor structures as a heatmap of deviations."""
        n = len(structures)
        side = int(np.ceil(np.sqrt(n)))
        data = np.full((side, side), np.nan)
        for s in structures:
            row, col = divmod(s["id"], side)
            if row < side and col < side:
                data[row, col] = s["deviation"]

        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(data, cmap='RdYlGn_r', aspect='equal', interpolation='nearest')
        ax.set_title('64 Spinor Structures: Deviation from Observed (%)', fontsize=13)
        ax.set_xlabel('Structure Index (mod)', fontsize=11)
        ax.set_ylabel('Structure Index (div)', fontsize=11)
        fig.colorbar(im, ax=ax, label='Deviation (%)')
        return self._save(fig, 'structure_heatmap')

    def qnm_comparison(self, predictions: list[dict]) -> list[str]:
        """Plot QNM frequency predictions vs observations."""
        names = [p["name"] for p in predictions]
        delta_f = [p["delta_f"] for p in predictions]
        f_qnm = [p["f_qnm"] for p in predictions]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

        ax1.bar(names, f_qnm, color='#3498db', alpha=0.7, label=r'$f_{QNM}$')
        ax1.bar(names, delta_f, color='#e74c3c', alpha=0.7, label=r'$\Delta f$ (predicted)')
        ax1.set_ylabel('Frequency (Hz)', fontsize=11)
        ax1.set_title('QNM Frequencies', fontsize=13)
        ax1.legend(fontsize=10)
        ax1.tick_params(axis='x', rotation=15)

        snrs = [p["snr"] for p in predictions]
        colors = ['#2ecc71' if s >= 1 else '#e74c3c' for s in snrs]
        ax2.bar(names, snrs, color=colors, alpha=0.8)
        ax2.axhline(y=1.0, color='gray', linestyle='--', label='SNR = 1')
        ax2.set_ylabel('SNR', fontsize=11)
        ax2.set_title('Signal-to-Noise Ratio', fontsize=13)
        ax2.legend(fontsize=10)
        ax2.tick_params(axis='x', rotation=15)

        return self._save(fig, 'qnm_comparison')

    def deviation_analysis(self, choptyuk_data: dict) -> list[str]:
        """Plot deviation analysis for b-C, base, full, b_Ch."""
        labels = [r'$\Delta_{bC}$', r'$\Delta_{Ch}^{(base)}$',
                  r'$\Delta_{Ch}^{(full)}$', r'$b_{Ch}$']
        deviations = [
            choptyuk_data["deviation_bc_pct"],
            choptyuk_data["deviation_ch_pct"],
            choptyuk_data["deviation_full_pct"],
            choptyuk_data["deviation_b_ch_pct"],
        ]

        fig, ax = plt.subplots(figsize=(8, 5))
        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
        bars = ax.bar(labels, deviations, color=colors, alpha=0.8, width=0.5)
        ax.set_ylabel('Deviation from Observed (%)', fontsize=11)
        ax.set_title('Deviation Analysis of Spinor Corrections', fontsize=13)
        for bar, val in zip(bars, deviations):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                   f'{val:.3f}%', ha='center', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        return self._save(fig, 'deviation_analysis')

    def convergence_diagram(self, convergence_data: dict) -> list[str]:
        """Plot convergence of the Choptyuk series."""
        sums = convergence_data["partial_sums"]
        orders = [s["order"] for s in sums]
        values = [s["value"] for s in sums]
        devs = [s["deviation"] for s in sums]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), constrained_layout=True)

        ax1.plot(orders, values, 'bo-', linewidth=2, markersize=6)
        ax1.axhline(y=3.443, color='g', linestyle='--', label=r'$\Delta_{obs}$')
        ax1.set_xlabel('Series Order', fontsize=11)
        ax1.set_ylabel(r'$\Delta$', fontsize=11)
        ax1.set_title('Partial Sums Convergence', fontsize=13)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)

        ax2.semilogy(orders, [d + 1e-10 for d in devs], 'ro-', linewidth=2, markersize=6)
        ax2.set_xlabel('Series Order', fontsize=11)
        ax2.set_ylabel('Deviation (%)', fontsize=11)
        ax2.set_title('Convergence of Deviation', fontsize=13)
        ax2.grid(True, alpha=0.3)

        return self._save(fig, 'convergence')

    def lambda_1_sweep(self, sweep_data: dict) -> list[str]:
        """Plot lambda_1 sweep results."""
        lam = np.array(sweep_data["lambda_1"])
        delta_ch = np.array(sweep_data["delta_ch"])
        deviation = np.array(sweep_data["deviation_pct"])

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), constrained_layout=True)

        ax1.plot(lam, delta_ch, 'b-', linewidth=2)
        ax1.axhline(y=3.443, color='g', linestyle='--', label=r'$\Delta_{obs}$')
        ax1.axvline(x=3.838, color='gray', linestyle=':', alpha=0.7, label=r'$\lambda_1=3.838$')
        ax1.set_xlabel(r'$\lambda_1(\Delta)$', fontsize=12)
        ax1.set_ylabel(r'$\Delta_{Ch}$', fontsize=12)
        ax1.set_title(r'Choptyuk Formula vs $\lambda_1$', fontsize=13)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)

        ax2.semilogy(lam, deviation + 1e-10, 'r-', linewidth=2)
        ax2.axvline(x=3.838, color='gray', linestyle=':', alpha=0.7)
        ax2.set_xlabel(r'$\lambda_1(\Delta)$', fontsize=12)
        ax2.set_ylabel('Deviation (%)', fontsize=12)
        ax2.grid(True, alpha=0.3)

        return self._save(fig, 'lambda_1_sweep')

    def surface_comparison(self, surfaces_data: list[dict]) -> list[str]:
        """Plot comparison across different surfaces."""
        names = [s["name"] for s in surfaces_data]
        delta_bc = [s["delta_bc"] for s in surfaces_data]
        delta_ch = [s["delta_ch"] for s in surfaces_data]

        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(names))
        w = 0.35
        ax.bar(x - w/2, delta_bc, w, label=r'$\Delta_{bC}$', color='#3498db', alpha=0.8)
        ax.bar(x + w/2, delta_ch, w, label=r'$\Delta_{Ch}$', color='#e74c3c', alpha=0.8)
        ax.axhline(y=3.443, color='g', linestyle='--', label=r'$\Delta_{obs}$')
        ax.set_xticks(x)
        ax.set_xticklabels(names, fontsize=11)
        ax.set_ylabel(r'$\Delta$', fontsize=12)
        ax.set_title('Spectral Invariants Across Surfaces', fontsize=13)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        return self._save(fig, 'surface_comparison')

    def generate_all(self, results: dict, sim_results: dict | None = None) -> list[str]:
        """Generate all plots from verification and simulation results.

        Returns:
            List of all saved file paths.
        """
        all_paths = []
        ch = results.get("choptyuk", {})
        ph = results.get("phases", {})

        # 1. Spinor phases
        if ph:
            all_paths.extend(self.spinor_phase_diagram(
                ph["delta_A"], ph["delta_B"], ph["delta_C"]))

        # 2. Deviation analysis
        if ch:
            all_paths.extend(self.deviation_analysis(ch))

        # 3. Structure heatmap
        structs = results.get("structures", [])
        if structs:
            all_paths.extend(self.structure_heatmap(structs))

        # 4. QNM comparison
        qnm = results.get("qnm_predictions", [])
        if qnm:
            all_paths.extend(self.qnm_comparison(qnm))

        # 5. Surface comparison
        surfaces = results.get("surface", [])
        if surfaces:
            all_paths.extend(self.surface_comparison(surfaces))

        # Simulation plots
        if sim_results:
            sweep_dC = sim_results.get("sweep_delta_C", {})
            if sweep_dC:
                all_paths.extend(self.eigenvalue_landscape(sweep_dC))

            conv = sim_results.get("convergence", {})
            if conv:
                all_paths.extend(self.convergence_diagram(conv))

            sweep_lam = sim_results.get("sweep_lambda_1", {})
            if sweep_lam:
                all_paths.extend(self.lambda_1_sweep(sweep_lam))

        logger.info(f"Generated {len(all_paths)} plot files")
        return all_paths
