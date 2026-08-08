# Dirac Operator

The Dirac operator and its spectral properties on the Klein quartic.

## Lichnerowicz Formula

For any spinor structure $\sigma$ on a spin Riemannian manifold, the
**Lichnerowicz formula** relates the squared Dirac operator to the
Laplacian and scalar curvature:

$$
D^2_\sigma = \Delta + \frac{R}{4}
$$

On the Klein quartic with $R = -2$:

$$
\lambda_1(D^2_{\sigma_0}) = \lambda_1(\Delta) + \frac{R}{4} = 3.838 + (-0.5) = 3.338
$$

## First Eigenvalue of the Laplacian

The value $\lambda_1(\Delta) = 3.838$ was rigorously computed by
**Bourque & Strohmaier (2024)** using Selberg trace formula methods
on the hyperbolic surface.

## Dirac Spectrum

The Dirac operator $D$ on a compact spin Riemannian manifold has a
discrete real spectrum symmetric about zero:

$$
\mathrm{Spec}(D_\sigma) = \{ \ldots, -\lambda_2, -\lambda_1, \lambda_1, \lambda_2, \ldots \}
$$

For the trivial spinor structure on the Klein quartic, the first
positive eigenvalue is:

$$
\lambda_1(D_{\sigma_0}) = \sqrt{3.338} \approx 1.827
$$

## Computational Access

```python
from src.core.dirac_operator import DiracOperator

dirac = DiracOperator()
print(f"λ₁(Δ) = {dirac.lambda_1_laplacian:.4f}")        # 3.838
print(f"λ₁(D²) = {dirac.lambda_1_dirac_squared:.4f}")   # 3.338
print(f"λ₁(D)  = {dirac.lambda_1_dirac:.4f}")           # 1.827
print(f"R      = {dirac.scalar_curvature}")               # -2
```
