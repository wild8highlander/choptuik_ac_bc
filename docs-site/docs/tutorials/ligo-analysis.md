# LIGO Analysis Tutorial

This tutorial demonstrates how to apply spinor-phase corrections from the Klein quartic curve to LIGO–Virgo gravitational-wave data, and compare the corrected quasi-normal mode (QNM) predictions against observed ringdown signals.

## Background

After the merger of two black holes, the resulting remnant emits gravitational radiation in the form of a **ringdown**—a superposition of quasi-normal modes. The frequencies and damping times of these modes are determined entirely by the remnant's mass and spin, making them a clean probe of strong-field gravity.

The Choptuik AC/BC framework introduces **spinor-phase corrections** that modify the standard QNM frequencies. These corrections arise from the geometry of the Klein quartic curve and the associated Dirac operator spectrum, and they produce frequency shifts of order

\[
\Delta f \sim \frac{\gamma}{2\pi M} \cos(\varphi_k),
\]

where \(\gamma\) is the Choptuik critical exponent and \(\varphi_k\) is the spinor phase. While these shifts are small compared to current detector sensitivity, they represent a theoretically motivated departure from the Kerr QNM spectrum that could become relevant at higher precision.

## Prerequisites

Before starting this tutorial, ensure you have:

- The Choptuik AC/BC package installed (see [Quick Start](quick-start.md))
- LIGO data files in a local directory (or network access to the LIGO Data Repository)
- The `ligo` optional dependency group installed:

```bash
pip install "choptuik-ac-bc[ligo]"
```

## Step 1 — Load Gravitational-Wave Data

The package can read LIGO–Virgo strain data from GWTC catalog files:

```python
from choptuik_ac_bc.hypothesis import load_gw_event

# Load a specific event from the GWTC-3 catalog
event = load_gw_event("GW150914")
print(f"Event: {event.name}")
print(f"Peak strain: {event.peak_strain:.2e}")
print(f"Detector: {event.detector}")
```

Alternatively, load from a local file:

```python
event = load_gw_event(path="data/GW150914_H1_strain.txt")
```

## Step 2 — Extract Ringdown Parameters

From the event data, extract the post-merger ringdown parameters:

```python
from choptuik_ac_bc.qnm import extract_ringdown

ringdown = extract_ringdown(
    event,
    fit_start_time="peak",    # start at peak strain
    duration=0.05,            # 50 ms of ringdown
    n_modes=2                 # fundamental + first overtone
)

print(f"Remnant mass:  {ringdown.final_mass:.2f} M☉")
print(f"Remnant spin:  {ringdown.final_spin:.4f}")
print(f"Fundamental QNM frequency: {ringdown.f_220:.2f} Hz")
print(f"Fundamental QNM damping:   {ringdown.tau_220:.4f} ms")
```

## Step 3 — Apply Spinor-Phase Corrections

Apply the Klein quartic spinor corrections to the extracted QNM frequencies:

```python
from choptuik_ac_bc.spinor_phases import apply_corrections

corrected = apply_corrections(
    ringdown,
    precision=50,
    include_subleading=True   # include all 8 spinor phases
)

print(f"Corrected f_220: {corrected.f_220:.6f} Hz")
print(f"Standard   f_220: {ringdown.f_220:.6f} Hz")
print(f"Shift Δf:        {corrected.f_220 - ringdown.f_220:.2e} Hz")
```

## Step 4 — Compare with Observed Data

Perform a Bayesian comparison between the standard Kerr prediction and the spinor-corrected prediction:

```python
from choptuik_ac_bc.hypothesis import bayesian_comparison

result = bayesian_comparison(
    event=event,
    standard_prediction=ringdown,
    corrected_prediction=corrected,
    n_samples=10000
)

print(f"Bayes factor (corrected/standard): {result.bayes_factor:.4f}")
print(f"Log Bayes factor:                  {result.log_bayes_factor:.4f}")
```

A Bayes factor near 1.0 indicates that the data does not strongly prefer either model—consistent with expectations given current detector sensitivity.

## Step 5 — Generate Comparison Plots

Visualize the ringdown fit with both the standard and corrected QNM predictions:

```python
from choptuik_ac_bc.plots import plot_ringdown_comparison

plot_ringdown_comparison(
    event=event,
    standard=ringdown,
    corrected=corrected,
    output="ringdown_comparison.pdf",
    dpi=300
)
```

!!! example "Expected Output"
    The comparison plot shows the observed strain (gray), the standard Kerr QNM fit (blue dashed), and the spinor-corrected fit (red solid). The two fits are nearly indistinguishable at current noise levels, with the correction producing sub-percent-level frequency shifts.

## Limitations and Caveats

!!! warning "Current Sensitivity"
    The spinor-phase corrections produce frequency shifts of order \(10^{-4}\) relative to the fundamental QNM frequency. Current LIGO–Virgo noise levels (SNR ~ 10–20 for ringdown) cannot resolve these shifts. This analysis is primarily of theoretical interest and may become testable with next-generation detectors (Einstein Telescope, Cosmic Explorer).

!!! note "Systematic Errors"
    When comparing against LIGO data, be aware of systematic uncertainties in the ringdown start time, final mass/spin estimates, and waveform model systematics. These can dominate over the spinor-phase correction at current precision.

## Next Steps

- Read about the [Spinor Phases](../mathematics/spinor-phases.md) theory in detail.
- Explore the [QNM API](../api/qnm.md) for the full quasi-normal mode computation interface.
- See the [Hypothesis API](../api/hypothesis.md) for Bayesian model comparison details.
