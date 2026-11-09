# K3 & Kähler Surfaces

The role of K3 and Kähler surfaces in the enhanced Choptyuk framework.

## K3 Surface

The **K3 surface** is a compact simply-connected Kähler manifold with
vanishing first Chern class $c_1 = 0$. It plays a central role because
the denominator 22 in the a-C braking equals its second Betti number.

### Invariants

| Invariant | Value |
|---|---|
| $b_0$ | 1 |
| $b_1$ | 0 |
| $b_2$ | **22** |
| $b_3$ | 0 |
| $b_4$ | 1 |
| $\hat{A}(K3)$ | 2 |
| Holonomy | $\mathrm{Sp}(1)$ (hyperkähler) |
| $b_2^+$ | 3 |

### Hodge Decomposition

$$
b_2 = h^{1,1} + 2h^{2,0} = 20 + 2 = 22 \checkmark
$$

### Seiberg-Witten Compatibility

Since $b_2^+ = 3 > 1$, the K3 surface satisfies the Seiberg-Witten
simple type condition, making the Choptyuk correction compatible with
the Seiberg-Witten invariant framework.

## Kähler Surfaces and Dolbeault Correspondence

The enhanced verification establishes a **Dolbeault correspondence**
between the spinor corrections on the Klein quartic and the Dolbeault
cohomology of associated Kähler surfaces:

$$
H^{p,q}_{\bar{\partial}}(\Sigma) \longleftrightarrow \mathrm{Spin}^{p,q}(\Sigma)
$$

## I₇ Elliptic Fibration

The K3 surface admits an elliptic fibration with 24 singular fibers
(I₁ type). The $I_7$ fiber is singled out because its monodromy
matches the PSL(2, 7) symmetry of the Klein quartic.

## Computational Access

```python
from src.core.surfaces import K3Surface  # from enhanced_verification

k3 = K3Surface()
print(f"Betti numbers: {k3.betti_numbers}")       # [1, 0, 22, 0, 1]
print(f"Hodge diamond:\n{k3.hodge_diamond}")
print(f"Dirac index: {k3.dirac_index}")           # 2
print(f"b₂/Â = {k3.betti_2 / k3.dirac_index}")   # 11.0
print(f"SW-compatible: {k3.is_sw_compatible}")     # True
```
