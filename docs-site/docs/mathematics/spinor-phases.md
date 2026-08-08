# Spinor Phases & Structures

Detailed treatment of spinor phases and the 64 spinor structures on the Klein quartic.

## Spinor Phases

On the Klein quartic curve, the spinor phases are determined by the
automorphism group $\mathrm{PSL}(2, 7)$:

| Phase | Value | Decimal | Source |
|---|---|---|---|
| $\delta_A$ | $\pi/2$ | 1.570796 | Order-2 element |
| $\delta_B$ | $\pi/3$ | 1.047198 | Order-3 element |
| $\delta_C$ | $\pi/7$ | 0.448799 | Order-7 element |

## Spinor Structures

A **spinor structure** on a Riemannian manifold $(M, g)$ is a lift of the
structure group $\mathrm{SO}(n)$ to $\mathrm{Spin}(n)$ in the frame bundle.

### Count on the Klein Quartic

The number of spinor structures on a genus-$g$ Riemann surface is:

$$
|\mathrm{Spin}(\Sigma_g)| = 2^{2g} = 2^6 = 64
$$

### Trivial Spinor Structure

The **trivial** spinor structure $\sigma_0$ is the one corresponding to the
trivial line bundle. It achieves the **minimum** first eigenvalue of the
squared Dirac operator:

$$
\lambda_1(D^2_{\sigma_0}) = \lambda_1(\Delta) + \frac{R}{4} = 3.838 + \frac{-2}{4} = 3.338
$$

This is a consequence of the **Lichnerowicz formula**:

$$
D^2_\sigma = \Delta + \frac{R}{4}
$$

which holds for the trivial spinor structure on any spin Riemannian manifold.

## Berry Phase Interpretation

The b-C correction can be interpreted as a **Berry phase** — a geometric
phase acquired by spinors under parallel transport around a closed loop
in the moduli space of spinor structures:

$$
\Delta_{bC} = \lambda_1(D^2_{\sigma_0}) + \frac{\delta_C^2}{2} = 3.338 + 0.100710 = 3.438710
$$

The Berry phase contribution $\delta_C^2 / 2 \approx 0.1007$ is the
first-order correction from the non-trivial holonomy of the spinor bundle.

## Computational Access

```python
from src.core.spinor_phases import SpinorPhases

phases = SpinorPhases()
print(f"δ_A = {phases.delta_A:.6f}")   # 1.570796
print(f"δ_B = {phases.delta_B:.6f}")   # 1.047198
print(f"δ_C = {phases.delta_C:.6f}")   # 0.448799
print(f"Berry phase = {phases.berry_phase:.6f}")  # 0.100710
```
