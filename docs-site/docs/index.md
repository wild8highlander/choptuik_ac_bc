# Choptuik AC/BC

Computational framework for spinor corrections on the Klein quartic curve.

## Features

- **Klein Quartic Curve**: Complete implementation with spinor phase corrections
- **Dirac Operator**: Spectral computation on the Klein quartic
- **Choptyuk Formula**: Critical exponent calculations with enhanced verification
- **Quasi-Normal Modes**: QNM analysis for gravitational wave physics
- **K3 Surfaces**: Extension to Calabi-Yau manifolds
- **Enhanced Verification**: Multi-precision numerical cross-checks
- **Interactive Menu**: User-friendly CLI for all computations
- **Visualization**: Publication-quality plots and phase diagrams

## Quick Links

| Resource | Link |
|----------|------|
| Tutorials | [Quick Start Guide](tutorials/quick-start/) |
| API Reference | [Python API](api/) |
| Mathematics | [Theory Background](mathematics/) |
| Development | [Contributing Guide](development/contributing/) |

## Installation

```bash
pip install choptuik-ac-bc
```

## Quick Example

```python
from choptuik_ac_bc import choptyuk_formula, klein_curve

# Compute on the Klein quartic
curve = klein_curve.KleinCurve()
result = choptyuk_formula.compute(curve, precision=50)
print(f"Critical exponent: {result}")
```

## Citation

If you use this software in your research, please cite:

```bibtex
@software{choptuik_ac_bc,
  author = {Isaev, Ishak Khamzatovich},
  title = {Choptuik AC/BC: Spinor Corrections on the Klein Quartic},
  year = {2024},
  url = {https://github.com/wild8highlander/choptuik_ac_bc}
}
```
