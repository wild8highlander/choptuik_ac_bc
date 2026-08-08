# Running Verification

Learn how to run the full verification suite with custom parameters and tolerances.

## Default Verification

The default verification checks all core results from the monograph:

```python
from src.verification.verify_all import verify_all

results = verify_all()
for name, result in results.items():
    print(f"{name}: {'PASS' if result.passed else 'FAIL'} (dev: {result.deviation:.4f}%)")
```

## Custom Tolerance

Adjust the tolerance for deviation checks:

```bash
python run.py --mode verify --tolerance 0.001 --non-interactive
```

Or programmatically:

```python
from src.verification.verify_all import verify_all

results = verify_all(tolerance=0.001)  # 0.1% tolerance
```

## Enhanced Verification (v2.0)

The enhanced verification suite covers the v2.0 extensions:

- 4D spin manifold conformal invariance
- Kähler surface Dolbeault correspondence
- K3 surface hyperkähler verification
- Tyukovsky equations (zero free parameters)
- Einstein GR QNM corrections
- Criticism response (b₂ = 22 uniqueness)

```python
from src.verification.verify_enhanced import verify_enhanced

results = verify_enhanced()
```

## Verification Results Reference

| Constant | Computed | Observed | Deviation | Status |
|---|---|---|---|---|
| $\Delta_{bC}$ | 3.438710 | 3.443 | 0.125% | :verified:{ .verified } |
| $\Delta_{Ch}$ (base) | 3.437883 | 3.443 | 0.149% | :verified:{ .verified } |
| $\Delta_{Ch}$ (full) | 3.447040 | 3.443 | 0.117% | :verified:{ .verified } |
| $b_{Ch}$ | 0.376510 | 0.377 | 0.130% | :verified:{ .verified } |

## Output Formats

Verification results can be exported in all 7 report formats. The JSON format
is particularly useful for automated processing:

```python
from src.reporting.report_writer import ReportWriter

writer = ReportWriter(output_dir="output/reports")
writer.write(results, formats=["json", "csv", "pdf"])
```
