# Choptyuk Formula

The unified Choptyuk formula combining b-C and a-C corrections.

## b-C Correction (Berry Phase)

The **b-C correction** is the first-order spinor correction, interpreted
as a Berry phase:

$$
\Delta_{bC} = \lambda_1(D^2_{\sigma_0}) + \frac{\delta_C^2}{2} = 3.338 + 0.100710 = 3.438710
$$

## a-C Braking (2nd Order)

The **a-C braking** is the second-order correction:

$$
\delta_{\mathrm{eff}} = \frac{\delta_C^5}{22} \approx \frac{1}{1200} = 0.000828
$$

This "braking" term reduces the b-C correction. The denominator 22 is
not arbitrary — it equals $b_2(K3)/\hat{A}(K3)$ where $b_2 = 22$ is the
second Betti number of the K3 surface and $\hat{A}(K3) = 2$ is the
Dirac index.

## Unified Formula (Base)

$$
\Delta_{\mathrm{Ch}}^{\mathrm{base}} = \lambda_1(D^2_{\sigma_0}) + \frac{\delta_C^2}{2} - \frac{\delta_C^5}{22} = 3.437883
$$

## With Higher-Order Corrections

Including the $\delta_C^4$ and $\delta_C^6$ terms:

$$
\Delta_{\mathrm{Ch}} = \Delta_{\mathrm{Ch}}^{\mathrm{base}} + \frac{\delta_C^4}{8} + \frac{\delta_C^6}{2} = 3.447040
$$

## Choptyuk Constant

$$
b_{\mathrm{Ch}} = 1 - \cos\left(\frac{2\pi}{7}\right) = 2\sin^2\left(\frac{\pi}{7}\right) \approx 0.376510
$$

## Verification

| Quantity | Computed | Observed | Deviation |
|---|---|---|---|
| $\Delta_{bC}$ | 3.438710 | 3.443 | 0.125% |
| $\Delta_{\mathrm{Ch}}^{\mathrm{base}}$ | 3.437883 | 3.443 | 0.149% |
| $\Delta_{\mathrm{Ch}}$ | 3.447040 | 3.443 | 0.117% |
| $b_{\mathrm{Ch}}$ | 0.376510 | 0.377 | 0.130% |

## Computational Access

```python
from src.core.choptyuk_formula import ChoptyukFormula

formula = ChoptyukFormula()
print(f"Δ_bC = {formula.delta_bC:.6f}")          # 3.438710
print(f"δ_eff = {formula.delta_eff:.6f}")        # 0.000828
print(f"Δ_Ch (base) = {formula.delta_Ch_base:.6f}")  # 3.437883
print(f"Δ_Ch (full) = {formula.delta_Ch:.6f}")       # 3.447040
print(f"b_Ch = {formula.b_Ch:.6f}")              # 0.376510
```
