# Testing Guide

The Choptuik AC/BC project maintains a comprehensive test suite that covers unit tests, integration tests, property-based tests, and verification consistency checks. This guide describes the test structure, how to run tests, and the coverage requirements.

## Test Structure

The test suite is organized into the following categories:

```
tests/
├── unit/                     # Unit tests for individual functions
│   ├── test_choptyuk_formula.py
│   ├── test_dirac_operator.py
│   ├── test_klein_curve.py
│   ├── test_spinor_phases.py
│   ├── test_qnm.py
│   ├── test_hypothesis.py
│   ├── test_surfaces.py
│   ├── test_enhanced_verification.py
│   ├── test_plots.py
│   └── test_report_writer.py
├── integration/              # Cross-module integration tests
│   ├── test_spinor_dirac_consistency.py
│   ├── test_choptyuk_dirac_consistency.py
│   ├── test_k3_klein_consistency.py
│   └── test_qnm_spinor_consistency.py
├── property/                 # Property-based tests (Hypothesis library)
│   ├── test_klein_invariants.py
│   └── test_spinor_properties.py
└── conftest.py               # Shared fixtures and configuration
```

## Running Tests

### Full Suite

```bash
pytest tests/ -v
```

### By Category

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Property-based tests only
pytest tests/property/ -v
```

### By Module

```bash
# Test only the choptyuk_formula module
pytest tests/unit/test_choptyuk_formula.py -v

# Test with a keyword filter
pytest tests/ -v -k "klein"
```

### With Coverage

```bash
pytest tests/ --cov=choptuik_ac_bc --cov-report=term-missing --cov-report=html
```

This generates a terminal report showing line-by-line coverage and an HTML report in `htmlcov/`.

## Coverage Requirements

The project maintains the following coverage thresholds:

| Category | Minimum Coverage |
|----------|-----------------|
| **Overall** | 95% |
| **Public API functions** | 100% |
| **Branch coverage** | 90% |
| **Integration tests** | N/A (existence required) |

These thresholds are enforced by the CI pipeline. PRs that decrease coverage below these levels will not be merged.

## Test Design Patterns

### Arbitrary-Precision Tests

Tests involving `mpmath` arbitrary-precision arithmetic should use the `precision` fixture:

```python
def test_critical_exponent(precision):
    """Test that γ is computed correctly at multiple precisions."""
    for p in [15, 30, 50]:
        gamma = compute_critical_exponent(precision=p)
        expected = mpf("0.3558024155217529188045154998139906557")
        assert abs(gamma - expected) < mpf(10) ** (-p + 1)
```

### Verification Consistency Tests

Integration tests should verify that results from different modules are consistent:

```python
def test_spinor_dirac_consistency():
    """Verify that spinor phases match Dirac eigenvalue data."""
    phases = compute_phases(precision=30)
    eigenvalues = compute_spectrum(n_modes=8, precision=30)
    for k, phi in enumerate(phases):
        delta_k = arctan2(eigenvalues[k].imag, eigenvalues[k].real)
        assert abs(phi - 2 * pi * k / 7 - delta_k) < 1e-25
```

### Property-Based Tests

The project uses the **Hypothesis** library for property-based testing, particularly for verifying invariants that should hold for all inputs:

```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=1, max_value=100))
def test_klein_automorphism_preserves_curve(k):
    """The k-th automorphism maps the Klein quartic to itself."""
    auto = klein_automorphism(k)
    assert auto.preserves(klein_polynomial)
```

## Continuous Integration

All tests run automatically on every push and pull request via GitHub Actions. See [CI/CD](ci-cd.md) for the full pipeline configuration.

!!! tip "Fast Feedback Loop"
    During development, use `pytest-watch` for automatic test re-execution on file changes:
    ```bash
    pip install pytest-watch
    ptw tests/unit/ -- -v
    ```

!!! warning "Numerical Tolerance"
    When comparing floating-point results, always use an explicit tolerance based on the working precision, never `==`. For `mpmath` values, use `abs(a - b) < mpf(10)**(-precision + 1)`.
