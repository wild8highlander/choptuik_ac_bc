# Quick Start

Get up and running with Choptyuk Spinor Corrections in under 5 minutes.

## Installation

=== "pip"

    ```bash
    cd python/
    pip install -r requirements.txt
    ```

=== "pip (editable)"

    ```bash
    cd python/
    pip install -e ".[dev]"
    ```

=== "Makefile"

    ```bash
    make python-install
    ```

## First Verification

Run the complete verification suite in non-interactive mode:

```bash
python run.py --mode verify --non-interactive
```

Expected output:

```
═══════════════════════════════════════════════════
  Choptyuk Spinor Corrections — Verification
═══════════════════════════════════════════════════

[1/8] Klein curve parameters         ✓
[2/8] Spinor phase values            ✓
[3/8] Dirac operator eigenvalues     ✓
[4/8] b-C correction                 ✓ (dev: 0.125%)
[5/8] a-C braking                    ✓
[6/8] Choptyuk formula (base)        ✓ (dev: 0.149%)
[7/8] Choptyuk formula (full)        ✓ (dev: 0.117%)
[8/8] Choptyuk constant              ✓ (dev: 0.130%)

All verifications passed. ✓
```

## Run with Preset

Use a predefined parameter preset for specific analyses:

```bash
# Standard precision (default)
python run.py --preset standard --non-interactive

# High precision (mpmath 50 decimal digits)
python run.py --preset high_precision --non-interactive

# LIGO gravitational wave analysis
python run.py --preset ligo_analysis --non-interactive
```

## Generate Reports

Generate reports in all supported formats:

```bash
python run.py --mode verify --non-interactive --output-dir output/
# Reports saved to: output/reports/
#   ├── verification_report.docx
#   ├── verification_report.pdf
#   ├── verification_report.txt
#   ├── verification_report.md
#   ├── verification_report.csv
#   ├── verification_report.html
#   └── verification_report.json
```

## Generate Plots

Generate publication-quality visualizations:

```bash
python run.py --mode plots --non-interactive --output-dir output/
# Plots saved to: output/plots/ (600 DPI PNG + PDF/SVG)
```

## Next Steps

- [Running Verification](verification.md) — customize verification parameters
- [LIGO QNM Analysis](ligo-analysis.md) — gravitational wave predictions
- [API Reference](../api/index.md) — detailed function documentation
