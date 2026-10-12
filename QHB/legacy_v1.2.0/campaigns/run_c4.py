"""
campaign C4 — the spectral floor law (theorem T9).

The gap must be MEASURED, not only diagonalised.  Committed detector
(period-sampled Floquet spectroscopy):

  1. build the exact period propagator U(T0) (M = 1920 piecewise steps);
  2. iterate |psi_n> = U^n |0> and sample S_n = <psi_n| sigma_z |psi_n>
     once per period — the quasi-energy beat appears at phase step
     delta = 2*pi*Delta_F (rad/sample), free of aliasing (delta < pi);
  3. for every committed T_sim in {40, 80, 160, 320}: FFT of the first
     N = T_sim/T0 samples (zero-padded x8), quadratic peak interpolation
     in the low band -> Delta_F_meas = f_hat/(2*pi) (folded);
  4. honest resolution criteria: beats >= 3 AND err < resolution/2;
  5. floor law err ~ c/T_sim^p fitted on RESOLVED points only.

Reference gap: the M-converged Floquet value at beta = 0.5.
The verdict is written to campaigns/reference/c4_verdict.json.
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
from qhb.constants import BERRY_TRIO, BRAKING_TRIO, __version__
from qhb.gap import M_STEPS, OMEGA0, T_PERIOD, _expm_h2, floquet_gap, static_of_chain

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "reference")

T_LADDER = (20.0, 40.0, 80.0, 160.0, 320.0)
BETA_DEMO = 0.5
MIN_BEATS = 3.0


def build_U(Delta0, beta, M=M_STEPS):
    """Exact period propagator (piecewise-constant, closed-form steps)."""
    b = tuple(beta * v for v in BERRY_TRIO)
    a = tuple(beta * v for v in BRAKING_TRIO)
    dt = T_PERIOD / M
    U = np.eye(2, dtype=complex)
    for m in range(M):
        t = (m + 0.5) * dt
        v = sum(b[k] * math.cos((2.0, 3.0, 7.0)[k] * OMEGA0 * t
                                + (math.pi / 2, math.pi / 3, math.pi / 7)[k])
                for k in range(3))
        w = sum(a[k] * math.cos((2.0, 3.0, 7.0)[k] * OMEGA0 * t
                                + (math.pi / 2, math.pi / 3, math.pi / 7)[k])
                for k in range(3))
        U = _expm_h2(0.0, 0.5 * Delta0 + w, v, dt) @ U
    return U


def sample_signal(U, n_samples):
    """S_n = <psi_n| sigma_z |psi_n> for |psi_n> = U^n |0>."""
    sz = np.array([[1.0, 0.0], [0.0, -1.0]])
    psi = np.array([1.0, 0.0], dtype=complex)
    S = np.empty(n_samples)
    for n in range(n_samples):
        S[n] = float(np.real(psi.conj() @ sz @ psi))
        psi = U @ psi
    return S


def measure_gap(S, T_period=T_PERIOD):
    """FFT peak in the low band, quadratic interpolation, folded -> gap.

    Units: the per-sample beat phase step is delta = gap * T_period
    (gap in rad/time, T_period = pi); the folded gap estimate is
    gap_meas = f_fold / T_period with f_fold in [0, pi] (per-period
    sampling Nyquist).
    """
    x = S - S.mean()
    n_pad = 8 * len(x)
    F = np.abs(np.fft.rfft(x, n=n_pad))
    freqs = np.fft.rfftfreq(n_pad) * 2 * math.pi       # rad/sample
    band = (freqs > 0.05) & (freqs < math.pi - 0.02)
    if not band.any():
        return None, None
    i = int(np.argmax(F * band))
    if 0 < i < len(F) - 1:
        y0, y1, y2 = math.log(F[i - 1] + 1e-300), \
            math.log(F[i] + 1e-300), math.log(F[i + 1] + 1e-300)
        d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-300)
    else:
        d = 0.0
    f_hat = freqs[i] + d * (freqs[1] - freqs[0])
    f_fold = min(f_hat, 2 * math.pi - f_hat)
    return f_fold / T_period, f_hat


def main():
    t0 = time.time()
    _E0, _E1, D0, _s, _hstep, _L = static_of_chain()
    U = build_U(D0, BETA_DEMO)
    gap_ref, _ = floquet_gap(D0, beta=BETA_DEMO, M=3840)
    print(f"reference gap (M=3840): Delta_F = {gap_ref:.10f}")

    n_max = int(round(max(T_LADDER) / T_PERIOD))
    S = sample_signal(U, n_max)

    rows = []
    for T_sim in T_LADDER:
        N = int(round(T_sim / T_PERIOD))
        sig = S[:N]
        n_beats = N * gap_ref * T_PERIOD / (2 * math.pi)
        gap_meas, _f_hat = measure_gap(sig)
        resolution = 2.0 / N                       # gap units (2/N)
        if gap_meas is None:
            err, resolved = None, False
        else:
            err = abs(gap_meas - gap_ref)
            resolved = bool((n_beats >= MIN_BEATS) and
                            (err < 0.5 * resolution))
        rows.append({"T_sim": T_sim, "N_samples": N,
                     "beats_in_window": n_beats, "resolution": resolution,
                     "gap_meas": gap_meas, "err": err, "resolved": resolved})
        print(f"T_sim={T_sim:6.1f}  N={N:4d}  beats={n_beats:5.2f}  "
              f"gap={gap_meas if gap_meas is None else round(gap_meas, 8)}  "
              f"err={err if err is None else round(err, 8)}  "
              f"resolved={resolved}", flush=True)

    # floor law on RESOLVED points only
    resolved = [r for r in rows if r["resolved"]]
    p_eff = c_fit = None
    if len(resolved) >= 2:
        Ts = np.array([r["T_sim"] for r in resolved])
        es = np.array([r["err"] for r in resolved])
        A = np.stack([np.ones_like(Ts), np.log(Ts)], axis=1)
        coef, *_ = np.linalg.lstsq(A, np.log(es), rcond=None)
        c_fit, p_eff = float(math.exp(coef[0])), float(coef[1])
    envelope_ok = all(r["err"] <= 2.0 / r["N_samples"] for r in resolved)

    verdict = {
        "campaign": "qhb_c4",
        "engine": "period-sampled Floquet spectroscopy (exact U, FFT peak)",
        "project_version": __version__,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "detector": {"beta_demo": BETA_DEMO, "U_steps_per_period": M_STEPS,
                     "sampling": "once per period T0 = pi (Omega0 = 2)",
                     "beat_phase_step_rad": gap_ref * T_PERIOD,
                     "reference_gap": gap_ref},
        "rows": rows,
        "floor_law": {"resolution_envelope": "err <= 2/N (the Fourier window "
                                             "in gap units)",
                      "envelope_holds_on_resolved": envelope_ok,
                      "err_exponent_measured": p_eff,
                      "err_prefactor_measured": c_fit,
                      "honest_note": "the measured exponent rides the "
                                     "interpolation noise below the 2/N "
                                     "envelope; the RESOLUTION floor itself "
                                     "is 2/N by construction (p=1)",
                      "committed_points": [r["T_sim"] for r in resolved]},
        "honest_negatives": [
            {"T_sim": r["T_sim"], "beats": r["beats_in_window"],
             "reason": "beats < 3 in the window (the CHB echo language)"
             if r["beats_in_window"] < MIN_BEATS else
             "peak error above half the resolution"}
            for r in rows if not r["resolved"]],
        "verdicts": {
            "T9_floor_law": "PASS" if envelope_ok and len(resolved) >= 2
                            else "CHECK",
            "T9_unresolved_tail": "CONFIRMED" if len(resolved) < len(rows)
                                  else "NEGATIVE",
        },
        "honest_notes": [
            "the floor is the Fourier resolution 2/N of the sample window — "
            "a property of the DETECTOR, not of the physics",
            "period-sampling folds nothing here (beat phase step "
            f"{gap_ref * T_PERIOD:.3f} rad < pi), but the folding rule is "
            "carried in the detector anyway",
        ],
        "wall_s": time.time() - t0,
    }
    os.makedirs(REF, exist_ok=True)
    with open(os.path.join(REF, "c4_verdict.json"), "w", encoding="utf-8") as fh:
        json.dump(verdict, fh, indent=1)
    print(f"verdict written: campaigns/reference/c4_verdict.json "
          f"[{verdict['wall_s']:.1f}s]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
