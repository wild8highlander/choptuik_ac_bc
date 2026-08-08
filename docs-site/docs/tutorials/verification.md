# Verification Tutorial

This tutorial provides a detailed walkthrough of the mathematical verification suite in Choptuik AC/BC. The verification system checks that all computed quantities satisfy their theoretical constraints to the specified numerical tolerance.

## Overview

The verification suite validates the following mathematical structures:

1. **Klein quartic automorphisms** — confirms the curve admits exactly 168 orientation-preserving automorphisms (the maximum for a genus-3 curve by the Hurwitz bound).
2. **Spinor-phase consistency** — verifies that the eight spinor phases \(\varphi_k\) satisfy the closure relation \(\sum_k \varphi_k = 2\pi \pmod{2\pi}\).
3. **Dirac operator spectrum** — checks that the computed eigenvalues \(\lambda_n\) of the Dirac operator on the Klein quartic match the theoretically predicted spectral gaps.
4. **Choptuik critical exponent** — confirms that the computed critical exponent \(\gamma\) agrees with the formula
\[
\gamma = \frac{1}{2} + \frac{1}{4\pi} \arctan\!\left(\frac{\sqrt{7}}{3}\right),
\]
to the requested precision.
5. **K3 surface intersection form** — validates the intersection pairing on the lattice \(H^2(X, \mathbb{Z})\) for the associated K3 surface \(X\).

## Running the Standard Verification

```bash
python -m choptuik_ac_bc.verify_all --precision 30
```

The `--precision` flag sets the number of decimal digits for arbitrary-precision arithmetic (default: 30). Output is structured as a series of labeled checks:

```
[CHECK] Klein quartic automorphism group
  Computing PSL(2,7) action on CP^2 ...
  Order = 168 ... ✓ PASS

[CHECK] Spinor-phase closure
  Σ φ_k = 6.283185307179586... = 2π (mod 2π) ... ✓ PASS

[CHECK] Dirac spectral gap
  λ_min = 0.0 (kernel dimension = 0) ... ✓ PASS
  λ_1 = 2.449489... (expected ≈ √6) ... ✓ PASS
```

## Running the Enhanced Verification

The enhanced verification suite performs deeper checks, including cross-module consistency and higher-precision recomputation:

```bash
python -m choptuik_ac_bc.verify_enhanced --precision 50 --parallel 4
```

!!! note "Enhanced Verification Duration"
    Enhanced verification is significantly more computationally intensive than the standard suite. At precision 50 with 4 parallel workers, expect runtime of 2–5 minutes depending on hardware. The `--parallel` flag distributes independent checks across CPU cores.

## Interpreting Results

Each check produces one of three outcomes:

| Outcome | Meaning |
|---------|---------|
| `✓ PASS` | The computed value matches the theoretical prediction within tolerance |
| `✗ FAIL` | The computed value deviates beyond the specified tolerance |
| `⚠ WARN` | The check completed but with reduced precision or a non-critical discrepancy |

!!! warning "Tolerance and Precision"
    A `PASS` result does not guarantee mathematical equality—it confirms agreement to `10^{-p}` where `p` is the specified precision. For formal verification, extremely high precision (e.g., 200+ digits) may be required. See [Enhanced Verification](../mathematics/enhanced-verification.md) for rigorous bounds.

## Generating a Report

To produce a structured JSON report of all verification results:

```python
from choptuik_ac_bc.verify_all import run_verification

results = run_verification(precision=30, output_format="dict")
for check in results:
    print(f"{check.name}: {check.status} (Δ = {check.error})")
```

## Next Steps

- See [Enhanced Verification](../mathematics/enhanced-verification.md) for the mathematical theory behind the checks.
- Learn how to adjust tolerances and numerical methods in [Custom Parameters](custom-parameters.md).
