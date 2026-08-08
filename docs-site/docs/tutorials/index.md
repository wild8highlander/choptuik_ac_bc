# Tutorials

Welcome to the **Choptuik AC/BC** tutorials! This section provides step-by-step guides to help you get started with the package, run verifications, explore the interactive menu system, and perform specialized analyses.

## Overview

The Choptuik AC/BC package is a computational physics toolkit for studying **spinor corrections on the Klein quartic curve**, **Dirac operator spectral analysis**, **Choptuik critical exponent computation**, and **quasi-normal mode (QNM) analysis** on K3 surfaces. These tutorials will walk you through the core workflows from installation to advanced usage.

## Available Tutorials

| Tutorial | Description |
|----------|-------------|
| [Quick Start](quick-start.md) | Install the package and run your first verification in under 5 minutes |
| [Verification](verification.md) | Run the full mathematical verification suite and interpret results |
| [Interactive Menu](interactive-menu.md) | Navigate the interactive CLI menu for exploratory analysis |
| [Custom Parameters](custom-parameters.md) | Configure precision, numerical methods, and output formats |
| [LIGO Analysis](ligo-analysis.md) | Apply spinor-phase corrections to LIGO gravitational-wave data |

## Prerequisites

Before starting, ensure you have:

- **Python 3.10+** installed and available on your `PATH`
- Basic familiarity with command-line interfaces
- (Optional) A virtual environment for isolated installation

!!! tip "Recommended Workflow"
    New users should follow the tutorials in the order listed above. The **Quick Start** guide covers essential installation and a minimal verification run. Subsequent tutorials build on that foundation with progressively more advanced features and customization options.

!!! note "Computational Requirements"
    Some verification steps—particularly the enhanced verification suite and LIGO analysis—can be computationally intensive. For best results, we recommend at least 4 GB of available RAM and a multi-core processor. Parallel execution is supported and documented in the [Custom Parameters](custom-parameters.md) tutorial.

## Getting Help

If you encounter issues while following these tutorials, please:

1. Check the [API Reference](../api/index.md) for detailed function signatures and docstrings.
2. Review the [Mathematics](../mathematics/index.md) section for theoretical background.
3. Open an issue on the project repository with a minimal reproducible example.
