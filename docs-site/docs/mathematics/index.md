# Mathematics

This section presents the theoretical foundations underlying the Choptuik AC/BC package. Each page provides a self-contained treatment of a key mathematical structure, with formal definitions, key results, and connections to the computational modules.

## Mathematical Framework

The Choptuik AC/BC project sits at the intersection of **algebraic geometry**, **spinor geometry**, **spectral theory**, and **general relativity**. The central object is the **Klein quartic curve**—a genus-3 algebraic curve with the maximum possible number of automorphisms—which serves as the geometric substrate for spinor corrections to black hole quasi-normal modes.

The logical dependency chain is:

```
Klein Quartic  →  Spinor Phases  →  Dirac Operator  →  Choptuik Formula
                                                           ↓
                                                  K3 Surfaces  →  QNM Corrections
```

## Topics

| Topic | Description |
|-------|-------------|
| [Klein Quartic Curve](klein-quartic.md) | The genus-3 curve \(x^3y + y^3z + z^3x = 0\) and its 168 automorphisms |
| [Spinor Phases](spinor-phases.md) | Eight spinor phases \(\varphi_k\) derived from the Klein quartic geometry |
| [Dirac Operator](dirac-operator.md) | Spectral theory of the Dirac operator on the Klein quartic |
| [Choptuik Formula](choptyuk-formula.md) | The critical exponent formula linking geometry to scaling behavior |
| [Enhanced Verification](enhanced-verification.md) | Rigorous verification with certified error bounds |
| [K3 Surfaces](k3-surfaces.md) | K3 surfaces associated to the Klein quartic and their lattice structure |

## Notation and Conventions

Throughout these pages we use the following conventions:

- **Field**: All algebraic varieties are defined over \(\mathbb{C}\) unless otherwise stated.
- **Coordinates**: Homogeneous coordinates on \(\mathbb{CP}^2\) are denoted \([x : y : z]\).
- **Metric**: The Klein quartic is equipped with the unique Poincaré-type metric compatible with its automorphism group.
- **Spinors**: We work with the complex spinor bundle \(S \to \Sigma\) where \(\Sigma\) is the Klein quartic, using the convention where the Dirac operator is formally self-adjoint.
- **Precision**: Numerical values are given to the precision available from the computational modules; exact algebraic expressions are provided wherever possible.

!!! tip "Cross-References"
    Mathematical results that are verified by the computational modules are marked with a ✓ symbol and linked to the corresponding [API documentation](../api/index.md). This allows you to trace every theoretical claim to its computational implementation.
