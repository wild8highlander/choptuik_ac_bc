# REST API Reference

## Base URL

- **Local**: `http://localhost:8080`
- **Production**: Deployed via Docker Compose

## Core Endpoints

### Verification

#### `GET /api/verify`
Run full verification suite and return results.

**Response**:
```json
{
  "spinor_phases": {
    "delta_A": 1.570796,
    "delta_B": 1.047198,
    "delta_C": 0.448799
  },
  "choptyuk": {
    "delta_bc": 3.438710,
    "delta_eff": 0.000828,
    "delta_ch_base": 3.437883,
    "delta_ch_full": 3.447040,
    "b_ch": 0.376510
  },
  "deviations": {
    "bc_pct": 0.125,
    "ch_base_pct": 0.149,
    "ch_full_pct": 0.117
  },
  "all_passed": true
}
```

### Reports

#### `GET /api/reports?format=json`
Generate verification report in specified format.

**Query Parameters**:
| Parameter | Type | Values | Default |
|---|---|---|---|
| `format` | string | json, html, csv, txt, md | json |

### Simulation

#### `POST /api/simulate`
Run parameter sweep simulation.

**Request Body**:
```json
{
  "parameter": "delta_C",
  "range": [0.1, 1.0],
  "steps": 100,
  "lambda_D2_triv": 3.338,
  "k_struct": 22
}
```

## Enhanced Endpoints (v2.0)

### K3 Surface

#### `GET /api/enhanced/k3`
Return K3 surface data and verification.

**Response**:
```json
{
  "betti_numbers": { "b0": 1, "b1": 0, "b2": 22, "b3": 0, "b4": 1 },
  "hodge_decomposition": { "h11": 20, "h20": 1 },
  "dirac_index": 2,
  "b2_plus": 3,
  "b2_decomposition_valid": true,
  "seiberg_witten_compatible": true,
  "holonomy": "Sp(1) ≅ SU(2)",
  "b2_over_dirac_index": 11.0
}
```

### Tyukovsky Equations

#### `GET /api/enhanced/tyukovsky`
Return Tyukovsky equation adaptation data.

**Query Parameters**:
| Parameter | Type | Default | Description |
|---|---|---|---|
| `delta0` | float | 0.36 | Uncorrected critical exponent |

**Response**:
```json
{
  "delta_0": 0.36,
  "delta_C": 0.448799,
  "delta_corrected": 0.459883,
  "echo_period": 2.174468,
  "echo_shift_pct": -21.72,
  "free_parameters": 0,
  "gct_equation": "L_gCT φ = V'(φ) + γ_spin·φ + i·δ_eff·∂φ/∂t"
}
```

### Einstein GR QNM Correction

#### `GET /api/enhanced/einstein-qnm`
Return Einstein GR QNM frequency correction data.

**Response**:
```json
{
  "delta_eff": 0.000828,
  "qnm_correction": 8.386e-05,
  "qnm_factor": 0.999916,
  "correction_pct": 0.00839,
  "detectable_current_ligo": false,
  "detectable_next_gen": true,
  "events": [
    { "name": "GW150914", "f_uncorr": 251.0, "f_corr": 250.979, "shift_Hz": -0.0210 },
    { "name": "GW170104", "f_uncorr": 293.0, "f_corr": 292.975, "shift_Hz": -0.0246 },
    { "name": "GW170814", "f_uncorr": 319.0, "f_corr": 318.973, "shift_Hz": -0.0268 },
    { "name": "GW190521", "f_uncorr": 110.0, "f_corr": 109.991, "shift_Hz": -0.0092 }
  ]
}
```

### Full Enhanced Verification

#### `GET /api/enhanced/verify`
Run complete enhanced verification across all extensions.

**Response**:
```json
{
  "klein": { "delta_C": 0.448799, "effective_phase": 0.000828, "unified_formula": 3.437883 },
  "k3": { "b2": 22, "b2_check": 22, "sw_compatible": true },
  "qnm": { "correction": 8.386e-05, "factor": 0.999916 },
  "tyukovsky": { "delta_corr": 0.459883, "free_parameters": 0 },
  "criticism": {
    "non_coincidental": { "best_approx": "1/1207", "no_better_below_1200": true },
    "b2_uniqueness": { "22": { "deviation_pct": 0.68, "compatible": true } },
    "stability": { "epsilon": 0.001, "stable": true }
  },
  "all_passed": true
}
```

## Web UI Endpoints

| Path | Template | Description |
|---|---|---|
| `/` | dashboard.html | Main dashboard |
| `/verify` | verify.html | Verification results |
| `/simulate` | simulate.html | Interactive simulation |
| `/hypothesis` | hypothesis.html | Hypothesis testing |
| `/reports` | reports.html | Report generation |

## Error Responses

All endpoints return errors in the format:
```json
{
  "error": "Description of the error",
  "status": 400
}
```

Common HTTP status codes:
- `200` — Success
- `400` — Invalid input parameter
- `500` — Internal computation error
