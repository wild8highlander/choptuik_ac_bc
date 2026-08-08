# LIGO QNM Analysis

Compute quasi-normal mode frequency corrections for LIGO/Virgo
gravitational wave events using the Choptyuk formula.

## Theory

The Choptyuk correction modifies quasi-normal mode frequencies as:

$$
\omega^{\mathrm{corr}} = \omega \cdot \left(1 - \frac{1}{1200\pi^2}\right) \approx 0.999916 \cdot \omega
$$

This produces a frequency shift of approximately $\Delta f / f \approx 8.4 \times 10^{-5}$.

## Quick Analysis

Use the LIGO analysis preset:

```bash
python run.py --preset ligo_analysis --non-interactive
```

## Programmatic Usage

```python
from src.core.qnm import QNMPredictor

predictor = QNMPredictor()
results = predictor.predict_all_events()

for event, data in results.items():
    print(f"{event}:")
    print(f"  f_QNM  = {data.f_qnm:.3f} Hz")
    print(f"  f_corr = {data.f_corrected:.3f} Hz")
    print(f"  Δf     = {data.delta_f:.4f} Hz")
```

## Results

| Event | $f_{\mathrm{QNM}}$ (Hz) | $f^{\mathrm{corr}}$ (Hz) | $\Delta f$ (Hz) |
|---|---|---|---|
| GW150914 | 251.000 | 250.979 | −0.0210 |
| GW170104 | 293.000 | 292.975 | −0.0246 |
| GW170814 | 319.000 | 318.973 | −0.0268 |
| GW190521 | 110.000 | 109.991 | −0.0092 |

## Enhanced QNM (v2.0)

The v2.0 enhanced predictor includes:

- Einstein GR corrections via Tyukovsky equations
- K3 surface constraints (b₂ = 22)
- Conformal invariance checks in 4D

```python
from src.core.enhanced_verification import EnhancedQNMPredictor

enhanced = EnhancedQNMPredictor()
results = enhanced.predict_with_corrections(
    event="GW150914",
    include_einstein_gr=True,
    include_k3_constraints=True,
)
```

## Physical Interpretation

The correction $\delta_C^5 / 22 \approx 1/1200$ arises from the second-order
spinor braking mechanism on the Klein quartic. This is a purely geometric
effect — it depends only on the automorphism group PSL(2,7) and the genus-3
topology, not on the specific gravitational wave parameters.

The correction is small ($\sim 10^{-4}$) but potentially detectable with
next-generation gravitational wave observatories (Einstein Telescope, Cosmic Explorer).
