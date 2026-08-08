# Klein Quartic Curve

The Klein quartic curve is the central geometric object in the Choptyuk problem.

## Definition

The **Klein quartic** is the algebraic curve defined by:

$$
x^3 y + y^3 z + z^3 x = 0 \subset \mathbb{CP}^2
$$

This is a smooth plane curve of degree 4 with remarkable symmetry properties.

## Key Properties

| Property | Value |
|---|---|
| Genus | $g = 3$ |
| Degree | 4 |
| Automorphism group | $\mathrm{PSL}(2, 7)$ of order 168 |
| Scalar curvature | $R = -2$ (hyperbolic metric) |
| First homology | $H_1(\Sigma, \mathbb{Z}) \cong \mathbb{Z}^6$ |
| Euler characteristic | $\chi = -4$ |

## Automorphism Group

The automorphism group $\mathrm{Aut}(\Sigma) \cong \mathrm{PSL}(2, 7)$ has order 168,
which is the **maximum** possible for a genus-3 Riemann surface (Hurwitz bound:
$|\mathrm{Aut}| \leq 84(g-1) = 168$). This makes the Klein quartic a **Hurwitz surface**.

The group $\mathrm{PSL}(2, 7)$ is the simple group of order 168, isomorphic to
$\mathrm{GL}(3, 2)$. It has a presentation:

$$
\mathrm{PSL}(2, 7) = \langle a, b \mid a^2 = b^3 = (ab)^7 = [a, b]^4 = 1 \rangle
$$

## Spinor Phases

The spinor phases are determined by the automorphism group:

$$
\delta_A = \frac{\pi}{2}, \quad \delta_B = \frac{\pi}{3}, \quad \delta_C = \frac{\pi}{7}
$$

These correspond to the orders of the generators $a$, $b$, and $ab$ in the
presentation above.

## Computational Access

```python
from src.core.klein_curve import KleinCurve

curve = KleinCurve()
print(f"Genus: {curve.genus}")                    # 3
print(f"Automorphism order: {curve.aut_order}")   # 168
print(f"Scalar curvature: {curve.scalar_curvature}")  # -2
print(f"δ_C = π/7 = {curve.delta_C:.6f}")         # 0.448799
```

## References

- Klein, F. "Über die Transformationen siebenter Ordnung der elliptischen Funktionen." *Math. Ann.* 14, 1879.
- Elkies, N. "The Klein quartic in number theory." *The Eightfold Way*, MSRI, 1998.
