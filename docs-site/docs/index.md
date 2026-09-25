# Choptyuk Spinor Corrections

[![PyPI version](https://img.shields.io/badge/choptyuk--spinor-2.0.0-blue.svg)](https://github.com/wild8highlander/choptuik_ac_bc)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.15152720-blue.svg?logo=zenodo)](https://doi.org/10.5281/zenodo.15152720)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

Welcome to the documentation for **Choptyuk Spinor Corrections** — a computational framework
for the verification, simulation, and visualization of spinor corrections b-C and a-C
on the Klein quartic curve, with applications to gravitational wave physics.

## Overview

This project implements the mathematical results from the monograph
*"Spinor corrections b-C and a-C and the solution of the Choptyuk problem"*
by **Ishak Khamzatovich Isaev**.

The core result is the **Choptyuk formula**:

$$
\Delta_{\mathrm{Ch}} = \lambda_1(D^2_{\sigma_0}) + \frac{\delta_C^2}{2} - \frac{\delta_C^5}{22} + \frac{\delta_C^4}{8} + \frac{\delta_C^6}{2} \approx 3.447040
$$

where $\delta_C = \pi/7$ is the spinor phase of the Klein quartic curve, and
$\lambda_1(D^2_{\sigma_0}) = 3.338$ is the first eigenvalue of the squared
Dirac operator on the trivial spinor structure.

## Features

- :material-check-circle: **Full verification** of all monograph results (25+ tests)
- :material-chart-line: **Interactive visualization** via Next.js dashboard
- :material-file-document-multiple: **7 report formats**: DOCX, PDF, TXT, MD, CSV, HTML, JSON
- :material-image: **Publication-quality plots**: 600 DPI PNG + vector PDF/SVG
- :material-calculator-variant: **Four implementations**: Python, Julia, Java, Next.js
- :material-web: **Web API**: Spring Boot REST API with web UI
- :material-flask: **LIGO/Virgo QNM predictions**: gravitational wave frequency corrections

## Quick Links

| Section | Description |
|---|---|
| [Tutorials](tutorials/index.md) | Step-by-step guides for running verification, simulations, and analysis |
| [Mathematics](mathematics/index.md) | Mathematical background: Klein quartic, Dirac operator, Choptyuk formula |
| [API Reference](api/index.md) | Auto-generated Python API documentation from docstrings |
| [Development](development/index.md) | Contributing, testing, CI/CD, and release process |

## Implementations

| Language | Directory | Type |
|---|---|---|
| Python 3.10+ | `python/` | CLI + Interactive Menu |
| Julia 1.9+ | `julia/` | REPL + Interactive Menu |
| Java 17+ | `java-webapp/` | Spring Boot REST API |
| Next.js 15 | `interactive-viz/` | Real-time Dashboard |

## Installation

```bash
# Python (recommended for quick verification)
cd python/
pip install -r requirements.txt
python run.py

# Or use the Makefile
make all
```

## Citation

```bibtex
@book{isaev2024spinor,
  title     = {Spinor corrections b-C and a-C and the solution of the Choptyuk problem},
  author    = {Isaev, Ishak Khamzatovich},
  year      = {2024},
  address   = {Nalchik, Kabardino-Balkarian Republic},
  note      = {Monograph with verified computational implementations}
}
```
