# The gap-drift law (theorem T10) — full derivation

The scientific heir of CHB theorem T10.  In the Collapse-Hawking
Bridge the question was: *why does one formula give different
thresholds at different grid scales?*  Here the same phenomenon is
transplanted to the GAP: *why does one gap measured on one sampled
geometry differ from the gap of the continuum geometry?*  The answer
is the same two exact lemmas, and the honest channel-share analysis
survives the transplantation verbatim.

---

## 1. The exact lemmas (inherited from CHB, re-verified here)

**Lemma A (chord flattening).** A parabola
`q = q_pk - kappa (x - x0)^2 / 2` sampled on a grid with step `h`
loses, in the worst alignment, exactly `kappa h^2 / 8` of its peak
(and `kappa h^2 / 24` on average over alignments).

*Machine status in this package.*  The committed chain is CENTRED:
for even N the summit sits exactly between two sites — the worst
alignment.  `campaigns/run_c5.py` verifies
`max q_n = q_pk - kappa h^2/8` for even N and `= q_pk` for odd N to
**0.0** (exact float arithmetic) — see
`c5_verdict.json::lemma_A_machine_check`.

**Lemma B (tension).** The chord chain of the sampled structure is
strictly shorter than the continuum arc; the sampled structure is
compressed under the curvature of its tension.  (Carried from CHB
T10 verbatim; the kinetic-dispersion channel below is its local
avatar in this model.)

## 2. The two drift channels

Let `Delta(q_pk, N)` be the measured two-level gap of the chain.
The continuum target is `Delta_cont = lim_{N->inf} Delta(q_pk, N)`.
Two independent O(h^2) channels separate the measured value:

**(i) The Lemma-A channel (exact).**  The sampled well is SHALLOWER
than the continuum well by `kappa h^2 / 8`.  With the measured
response `s = d(Delta_0)/d(q_pk)`:

```
Delta^{(A)}_N = Delta_cont + s * (kappa h^2 / 8) + O(h^3)
```

With the committed numbers `s = -1.00398294`, `kappa = 0.05`:

```
C_exact = s * kappa / 8 = -6.2749e-3 .
```

**(ii) The kinetic-dispersion channel.**  The discrete second
difference approximates `-d^2/dx^2` with O(h^2) spectral error
(the local face of Lemma B); the levels shift accordingly.
This channel is real, of the same order, and NOT reducible to a
closed form in this package — it is measured.

## 3. The law and its measurement

By the implicit-function structure of the two channels,

```
Delta_cont - Delta_N = C h^2 + O(h^3)
```

with `C = C^{kin} - C_exact` (the signs oppose each other here —
see below).  The committed measurement (exact tridiagonal
eigensolver, N = 32..512):

| N | h | Delta_N |
|---|---|---|
| 32 | 0.24242424 | 0.521692147813 |
| 64 | 0.12307692 | 0.523004556028 |
| 128 | 0.06201550 | 0.523344719799 |
| 256 | 0.03112840 | 0.523431317627 |
| 512 | 0.01559454 | 0.523453164838 |

```
p_eff = 1.948 / 1.974 / 1.987      (climbing to 2)
C_measured = +3.0089e-2
exact-channel share = C_exact / C_measured = -0.209
max fit residual = 9.8e-8
```

**The honest reading.**  The exact Lemma-A channel carries a
SIGNED share of about one fifth of the observed drift and OPPOSES
the kinetic channel: the flattened peak alone would push the
measured gap ABOVE the continuum target (`s < 0`), while the
dispersion pulls it below; the net ladder approaches from below.
No dominance claim is made — the two-channel decomposition is the
committed hypothesis for the remaining 79%, exactly as in CHB T10
where the exact channel carried 2.6e-3..9.1e-3 of the drift.

## 4. The sign mirror

CHB: the threshold ladder `A*_N` approaches the continuum threshold
FROM ABOVE.  Here: the gap ladder approaches FROM BELOW.  Both are
consequences of the same lemmas applied to observables with opposite
sensitivities (`dq_max/dA > 0` there, `s < 0` here).  The sign is
carried, not hidden — a law that only ever produced positive drifts
would be a fit, not a law.

## 5. The honest negative

`Delta_cont` is displayed as a two-parameter fit value
(0.523460440588) and **NOT claimed**: the ladder is pre-asymptotic
(five points, the two-term extrapolation is not protected by the
climbing-`p_eff` discipline — the same rejection that CHB applied to
`A*_inf`).  What IS claimed: the h^2 law, the climbing orders, the
exact Lemma A, and the signed exact-channel share.
