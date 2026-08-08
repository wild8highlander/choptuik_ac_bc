# Interactive Menu Tutorial

The Choptuik AC/BC package includes a full-featured interactive command-line menu that lets you explore every module without writing code. This tutorial covers navigation, module selection, and common workflows.

## Launching the Menu

Start the interactive simulator from the command line:

```bash
python -m choptuik_ac_bc.simulator
```

You will be greeted with a header and a list of available modules:

```
╔══════════════════════════════════════════════════════╗
║       Choptuik AC/BC — Interactive Simulator          ║
║       Spinor Corrections on the Klein Quartic         ║
╚══════════════════════════════════════════════════════╝

  1. Klein Quartic Curve
  2. Spinor Phases
  3. Dirac Operator
  4. Choptuik Formula
  5. Quasi-Normal Modes (QNM)
  6. K3 Surfaces
  7. Enhanced Verification
  8. Hypothesis Testing
  9. Plots & Visualization
  0. Exit

  Select a module [0-9]:
```

## Navigation

Use the **number keys** (0–9) to select a module, or type the module name. Press `Enter` to confirm your selection. At any sub-menu, press `q` or `Esc` to return to the previous level.

## Module Workflows

### Klein Quartic Curve (Option 1)

After selecting the Klein quartic module, you can:

- **Display the defining equation**: Shows \(x^3 y + y^3 z + z^3 x = 0\) in homogeneous coordinates.
- **Compute automorphisms**: Lists the generators of \(\mathrm{PSL}(2,7)\) and verifies the group order is 168.
- **Evaluate at a point**: Given homogeneous coordinates \([x:y:z]\), evaluates the Klein polynomial and checks whether the point lies on the curve.

### Spinor Phases (Option 2)

- **Show all 8 phases**: Displays the spinor phases \(\varphi_0, \ldots, \varphi_7\) with their numerical values.
- **Verify closure**: Confirms \(\sum_k \varphi_k \equiv 0 \pmod{2\pi}\).
- **Apply to QNM**: Demonstrates how spinor-phase corrections modify quasi-normal mode frequencies.

### Dirac Operator (Option 3)

- **Compute spectrum**: Calculates the first \(N\) eigenvalues of the Dirac operator on the Klein quartic.
- **Show spectral gap**: Reports the smallest non-zero eigenvalue \(\lambda_1\).
- **Kernel dimension**: Verifies that the Dirac kernel is trivial (dimension 0).

### Choptuik Formula (Option 4)

- **Compute critical exponent**: Evaluates \(\gamma\) to the specified precision.
- **Show formula derivation**: Prints a summary of the theoretical derivation linking the critical exponent to the Klein quartic geometry.

!!! example "Session Example"
    ```
    Select a module [0-9]: 4

    ── Choptuik Formula ──

    (a) Compute critical exponent
    (b) Show formula derivation
    (c) Back

    Choose [a-c]: a
    Precision (digits) [30]: 50

    Computing γ to 50 digits ...
    γ = 0.3558024155217529188045154998139906...

    Time: 0.42s
    ```

### Quasi-Normal Modes (Option 5)

- **Compute Schwarzschild QNMs**: Calculates the fundamental quasi-normal mode frequencies for Schwarzschild black holes with spinor-phase corrections.
- **Compare with LIGO data**: Loads reference gravitational-wave data and compares observed ringdown frequencies against the corrected QNM predictions.

## Customizing the Session

You can pass configuration flags when launching the simulator:

```bash
python -m choptuik_ac_bc.simulator --precision 50 --log-level DEBUG
```

| Flag | Default | Description |
|------|---------|-------------|
| `--precision` | 30 | Decimal digits for arbitrary-precision arithmetic |
| `--log-level` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `--color` | `auto` | Terminal color output (`auto`, `always`, `never`) |

!!! tip "Persisting Settings"
    The simulator reads a configuration file at `~/.choptuik/config.toml` if it exists. You can set default precision, log level, and other preferences there so they apply to every session. See [Custom Parameters](custom-parameters.md) for the full list of configurable options.
