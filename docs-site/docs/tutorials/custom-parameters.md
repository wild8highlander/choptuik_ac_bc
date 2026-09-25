# Custom Parameters

Learn how to configure spinor structures, surfaces, and analysis parameters
for custom verification and hypothesis testing.

## Configuration File

The default configuration is stored in `config/default_config.json`:

```json
{
  "precision": 15,
  "tolerance": 0.005,
  "delta_A": null,
  "delta_B": null,
  "delta_C": null,
  "lambda_1": null,
  "scalar_curvature": -2
}
```

`null` values are computed from the mathematical definitions (e.g., $\delta_C = \pi/7$).

## Custom Spinor Phases

Override the default spinor phases:

```python
from src.core.choptyuk_formula import ChoptyukFormula

# Custom spinor phases (must satisfy group constraints)
formula = ChoptyukFormula(
    delta_A=3.14159 / 2,   # π/2
    delta_B=3.14159 / 3,   # π/3
    delta_C=3.14159 / 7,   # π/7
)
print(f"b-C correction: {formula.delta_bC:.6f}")
print(f"Choptyuk formula: {formula.delta_Ch:.6f}")
```

## Presets

Three presets are provided for common use cases:

### Standard (`presets/standard.json`)
Default precision and tolerance for general verification.

### High Precision (`presets/high_precision.json`)
Uses `mpmath` with 50 decimal digits for critical comparisons:

```json
{
  "precision": 50,
  "tolerance": 1e-10,
  "use_mpmath": true
}
```

### LIGO Analysis (`presets/ligo_analysis.json`)
Optimized for gravitational wave QNM corrections:

```json
{
  "precision": 15,
  "tolerance": 0.001,
  "events": ["GW150914", "GW170104", "GW170814", "GW190521"]
}
```

## Hypothesis Testing

Test custom spinor structures and group configurations:

```python
from src.core.hypothesis import HypothesisTester

tester = HypothesisTester()
result = tester.test_structure(
    genus=3,
    automorphism_order=168,
    n_spinor_structures=64,
)
print(f"Hypothesis: {'SUPPORTED' if result.supported else 'REJECTED'}")
print(f"Evidence: {result.evidence}")
```

## Surface Comparisons

Compare spectral invariants across different Riemann surfaces:

```python
from src.core.surfaces import BOLZA, BRING, MACBEATH

for name, surface in [("Bolza", BOLZA), ("Bring", BRING), ("Macbeath", MACBEATH)]:
    print(f"{name}: genus={surface.genus}, aut={surface.automorphism_order}")
    print(f"  b₂ = {surface.betti_2}, λ₁ = {surface.lambda_1:.4f}")
```
