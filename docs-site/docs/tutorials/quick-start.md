# Quick Start Guide

Get the Choptuik AC/BC package installed and run your first verification in under five minutes.

## Step 1 — Installation

Install the package from PyPI using `pip`:

```bash
pip install choptuik-ac-bc
```

!!! tip "Virtual Environments"
    We strongly recommend installing inside a virtual environment to avoid dependency conflicts:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install choptuik-ac-bc
    ```

Verify the installation was successful:

```bash
python -c "import choptuik_ac_bc; print(choptuik_ac_bc.__version__)"
```

You should see the current version number printed to the console (e.g., `2.0.0`).

## Step 2 — Run a Minimal Verification

The fastest way to confirm the package is working is to run the core verification suite:

```bash
python -m choptuik_ac_bc.verify_all
```

This executes a series of mathematical checks that validate the spinor-phase corrections, Klein quartic arithmetic, and Dirac operator spectral properties. A successful run produces output similar to:

```
✓ Klein quartic: 168 automorphisms verified
✓ Spinor phases: all 8 phases match theoretical values
✓ Dirac operator: spectral gap within tolerance (ε = 1e-12)
✓ Choptuik formula: critical exponent γ = 0.355802...
ALL VERIFICATIONS PASSED
```

## Step 3 — Run the Interactive Menu

For a more exploratory experience, launch the interactive menu:

```bash
python -m choptuik_ac_bc.simulator
```

Use the arrow keys to navigate between modules and press Enter to select. The menu provides access to every major feature without writing code.

## Step 4 — Quick Python API Usage

You can also use the package programmatically:

```python
from choptuik_ac_bc.choptyuk_formula import compute_critical_exponent

gamma = compute_critical_exponent(precision=50)
print(f"Critical exponent γ = {gamma}")
# Output: Critical exponent γ = 0.355802...
```

!!! warning "Precision Settings"
    The `precision` parameter controls the number of decimal digits used in arbitrary-precision arithmetic. Higher values increase accuracy but also computation time. For most use cases, `precision=50` provides more than sufficient accuracy. See [Custom Parameters](custom-parameters.md) for details.

## What's Next?

- Follow the [Verification](verification.md) tutorial for a detailed walkthrough of every verification check.
- Explore the [Interactive Menu](interactive-menu.md) tutorial for guided feature discovery.
- Read the [Mathematics](../mathematics/index.md) section to understand the theory behind the computations.
