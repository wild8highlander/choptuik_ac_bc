# Custom Parameters Tutorial

This tutorial explains how to configure precision, numerical methods, output formats, and other parameters in the Choptuik AC/BC package. Fine-tuning these settings allows you to balance speed against accuracy and customize output for your specific workflow.

## Configuration Sources

The package reads settings from three sources, in order of increasing priority:

1. **Built-in defaults** — sensible values that work for most use cases.
2. **Configuration file** — `~/.choptuik/config.toml` (persisted across sessions).
3. **Command-line flags** — override all other sources for the current invocation.

## Precision Settings

### Arbitrary-Precision Arithmetic

The package uses `mpmath` for arbitrary-precision floating-point arithmetic. The `precision` parameter controls the number of **decimal digits** (not bits) of working precision:

```python
from choptuik_ac_bc.choptyuk_formula import compute_critical_exponent

# Default precision (30 digits)
gamma = compute_critical_exponent()

# High precision (200 digits) — slower but more accurate
gamma = compute_critical_exponent(precision=200)
```

!!! warning "Performance Scaling"
    Computation time scales roughly as \(O(p^2)\) where \(p\) is the precision in digits. Going from 30 to 200 digits can increase runtime by a factor of ~40 for some operations. Start with the default and increase only when needed.

### Tolerance

The `tolerance` parameter sets the absolute error bound for verification checks. By default, it is set to \(10^{-p}\) where \(p\) is the working precision. You can override it:

```bash
python -m choptuik_ac_bc.verify_all --precision 30 --tolerance 1e-25
```

## Numerical Method Selection

### Eigenvalue Solvers

The Dirac operator module supports two eigenvalue solvers:

| Solver | Method | Best For |
|--------|--------|----------|
| `arnoldi` | Implicitly restarted Arnoldi iteration | Large sparse matrices; fast for leading eigenvalues |
| `dense` | Full dense eigendecomposition via LAPACK | Small matrices; computes full spectrum exactly |

```python
from choptuik_ac_bc.dirac_operator import compute_spectrum

eigenvalues = compute_spectrum(
    n_modes=20,
    solver="arnoldi",   # or "dense"
    precision=30
)
```

### Integration Methods

The Choptuik formula module computes certain integrals numerically. Available methods:

- **Gauss–Legendre quadrature** (`gauss_legendre`) — default; high accuracy for smooth integrands.
- **Tanh-sinh quadrature** (`tanh_sinh`) — better for integrands with endpoint singularities.
- **Adaptive Simpson** (`adaptive_simpson`) — robust general-purpose fallback.

```python
from choptuik_ac_bc.choptyuk_formula import compute_critical_exponent

gamma = compute_critical_exponent(
    precision=50,
    integration_method="tanh_sinh",
    quadrature_nodes=200
)
```

## Parallel Execution

Long-running computations (enhanced verification, large spectral calculations) can be distributed across multiple CPU cores:

```bash
python -m choptuik_ac_bc.verify_enhanced --precision 50 --parallel 8
```

Programmatically:

```python
from choptuik_ac_bc.verify_enhanced import run_enhanced_verification

results = run_enhanced_verification(
    precision=50,
    n_workers=8,
    parallel=True
)
```

!!! note "Worker Count"
    Setting `n_workers` higher than the number of physical cores provides no benefit and may degrade performance due to overhead. Use `os.cpu_count()` to detect the available cores.

## Output Formats

### Report Formats

Verification results and analysis outputs can be exported in multiple formats:

| Format | Flag | Description |
|--------|------|-------------|
| `text` | `--format text` | Human-readable console output (default) |
| `json` | `--format json` | Structured JSON for programmatic consumption |
| `markdown` | `--format markdown` | Markdown table suitable for reports |
| `csv` | `--format csv` | Comma-separated values for spreadsheet import |

```bash
python -m choptuik_ac_bc.verify_all --format json --output results.json
```

### Plot Formats

When generating plots, you can control the output format and resolution:

```python
from choptuik_ac_bc.plots import plot_spectrum

plot_spectrum(
    n_modes=50,
    format="pdf",      # "png", "svg", "pdf"
    dpi=300,
    output="spectrum.pdf"
)
```

## Configuration File

Create or edit `~/.choptuik/config.toml` to persist your preferred settings:

```toml
[default]
precision = 50
tolerance = 1e-45
solver = "arnoldi"
integration_method = "gauss_legendre"
n_workers = 4
log_level = "INFO"
color = "auto"

[output]
format = "json"
dpi = 300
```

!!! example "Overriding Config at Runtime"
    Command-line flags always take precedence over the configuration file:
    ```bash
    # Config file says precision=50, but this run uses precision=100
    python -m choptuik_ac_bc.verify_all --precision 100
    ```

## Next Steps

- Return to the [Tutorials](index.md) overview for other guided workflows.
- Consult the [API Reference](../api/index.md) for the full list of configurable parameters on each function.
