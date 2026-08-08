# Interactive Menu

The Python implementation includes an interactive CLI menu for exploring
all features without memorizing command-line arguments.

## Starting the Menu

```bash
python run.py
```

This launches the interactive menu:

```
╔══════════════════════════════════════════════════╗
║   Choptyuk Spinor Corrections — Interactive Menu  ║
╠══════════════════════════════════════════════════╣
║  [1] Run Full Verification                        ║
║  [2] Run Enhanced Verification (v2.0)             ║
║  [3] Run Simulation Sweep                         ║
║  [4] Generate Plots                               ║
║  [5] Generate Reports                             ║
║  [6] Custom Hypothesis Test                       ║
║  [7] LIGO QNM Analysis                            ║
║  [8] Show Current Parameters                      ║
║  [9] Load Preset                                  ║
║  [0] Exit                                         ║
╚══════════════════════════════════════════════════╝
```

## Menu Options

### [1] Full Verification
Runs the complete verification suite and displays results with color-coded
pass/fail status and deviation percentages.

### [2] Enhanced Verification
Runs the v2.0 enhanced verification covering 4D spin manifolds, K3 surfaces,
Tyukovsky equations, and Einstein GR corrections.

### [3] Simulation Sweep
Performs parameter sweeps over $\delta_C$ and $\lambda_1$ values to explore
the Choptyuk formula landscape.

### [4] Generate Plots
Creates all publication-quality plots (600 DPI PNG + PDF/SVG).

### [5] Generate Reports
Generates reports in all 7 supported formats.

### [6] Custom Hypothesis Test
Configure custom spinor structures and group configurations for hypothesis testing.

### [7] LIGO QNM Analysis
Computes quasi-normal mode frequency corrections for LIGO/Virgo events.

### [8] Show Current Parameters
Displays all current parameter values and their sources (default/config/preset).

### [9] Load Preset
Load a parameter preset: `standard`, `high_precision`, or `ligo_analysis`.
