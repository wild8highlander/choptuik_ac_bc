# API Reference

This section provides the complete API reference for the Choptuik AC/BC package, auto-generated from the source code docstrings using **mkdocstrings**.

## Module Overview

The package is organized into the following top-level modules:

| Module | Description |
|--------|-------------|
| [`choptyuk_formula`](choptyuk-formula.md) | Choptuik critical exponent computation |
| [`dirac_operator`](dirac-operator.md) | Dirac operator spectrum on the Klein quartic |
| [`klein_curve`](klein-curve.md) | Klein quartic curve: equation, automorphisms, evaluation |
| [`spinor_phases`](spinor-phases.md) | Eight spinor phases and their properties |
| [`qnm`](qnm.md) | Quasi-normal mode computation with spinor corrections |
| [`hypothesis`](hypothesis.md) | Hypothesis testing and Bayesian model comparison |
| [`surfaces`](surfaces.md) | K3 surfaces: lattice, intersection form, Picard number |
| [`enhanced_verification`](enhanced-verification.md) | Interval-arithmetic enhanced verification |
| [`verify_all`](verify-all.md) | Full verification suite runner |
| [`verify_enhanced`](verify-enhanced.md) | Enhanced verification suite runner |
| [`simulator`](simulator.md) | Interactive command-line menu system |
| [`plots`](plots.md) | Visualization and plotting utilities |
| [`report_writer`](report-writer.md) | Report generation (JSON, Markdown, CSV, text) |

## Usage Patterns

All modules can be imported from the top-level package:

```python
from choptuik_ac_bc.choptyuk_formula import compute_critical_exponent
from choptuik_ac_bc.dirac_operator import compute_spectrum
from choptuik_ac_bc.klein_curve import KleinQuartic
from choptuik_ac_bc.spinor_phases import compute_phases
```

!!! tip "Type Hints"
    All public functions include complete type annotations. Use your IDE's type checker or `mypy` for static analysis:
    ```bash
    mypy --strict your_script.py
    ```

!!! note "Stability Guarantee"
    All functions documented in this API reference are part of the **public API** and are covered by the stability guarantee: breaking changes will only be introduced in major version releases, with deprecation warnings provided at least one minor version in advance. Internal functions (prefixed with `_`) are not covered by this guarantee.
