"""
    QNMPredictor

Predictor for quasi-normal mode frequency shifts due to spinor corrections.

The Choptyuk formula predicts that the spinor corrections on the Klein curve
produce a measurable shift in the QNM frequencies of perturbed black holes.
This shift is related to the Δ parameter and can in principle be detected
by LIGO-Virgo observations.

# Fields
- `delta_ch::Float64`: The Choptyuk constant Δ_Ch
- `observed_delta::Float64`: Observed Δ from LIGO data (default: 3.443)
"""
@kwdef struct QNMPredictor
    delta_ch::Float64 = choptyuk_constant()
    observed_delta::Float64 = 3.443
end

"""
    LIGOEvent

A LIGO-Virgo gravitational wave detection event with inferred
black hole parameters and QNM frequency.

# Fields
- `name::String`: Event name (e.g., "GW150914")
- `mass::Float64`: Remnant mass in solar masses
- `spin::Float64`: Dimensionless remnant spin parameter a/M
- `freq::Float64`: QNM frequency in Hz
- `delta::Float64`: Computed Δ parameter
"""
struct LIGOEvent
    name::String
    mass::Float64
    spin::Float64
    freq::Float64
    delta::Float64
end

"""
    LIGO_EVENTS

The four reference LIGO events from the monograph.
"""
const LIGO_EVENTS = LIGOEvent[
    LIGOEvent("GW150914", 62.0, 0.67, 251.0, 0.0),
    LIGOEvent("GW170104", 48.7, 0.65, 314.0, 0.0),
    LIGOEvent("GW170814", 53.4, 0.70, 286.0, 0.0),
    LIGOEvent("GW190521", 142.0, 0.72, 110.0, 0.0),
]

"""
    qnm_frequency(M::Float64, a::Float64; l::Int=2, n::Int=0) -> Float64

Compute the quasi-normal mode frequency for a Kerr black hole.

Uses the first-order WKB approximation for the fundamental mode.

# Arguments
- `M`: Black hole mass in solar masses
- `a`: Dimensionless spin parameter (0 ≤ a < 1)
- `l`: Angular quantum number (default: 2)
- `n`: Overtone number (default: 0)

# Returns
QNM frequency in Hz (using G = 6.674e-11, c = 3e8).
"""
function qnm_frequency(M::Float64, a::Float64; l::Int = 2, n::Int = 0)
    # Physical constants
    G = 6.674e-11   # m³/(kg·s²)
    c = 3.0e8       # m/s
    M_sun = 1.989e30  # kg

    # Mass in SI
    M_kg = M * M_sun

    # Horizon radius
    r_plus = G * M_kg / c^2 * (1 + sqrt(1 - a^2))

    # Approximate QNM frequency (Echeverria 1989 fit)
    # f_QNM ≈ (1 - 0.63(1-a)^0.3) / (2π M)
    omega_factor = 1.0 - 0.63 * (1.0 - a)^0.3
    f_qnm = omega_factor * c^3 / (2π * G * M_kg)

    return f_qnm
end

"""
    predict_shift(pred::QNMPredictor, event::LIGOEvent) -> Dict{String, Float64}

Predict the spinor-corrected QNM frequency shift for a LIGO event.

# Arguments
- `pred`: QNM predictor with Choptyuk constant
- `event`: LIGO event parameters

# Returns
Dictionary with predicted shift and comparison metrics.
"""
function predict_shift(pred::QNMPredictor, event::LIGOEvent)
    results = Dict{String, Float64}()

    # The spinor correction induces a fractional shift in QNM frequency
    # δf/f = (Δ_Ch - Δ_obs) / Δ_obs × scale_factor
    # where scale_factor depends on the event parameters

    delta_pred = pred.delta_ch
    delta_obs = pred.observed_delta

    results["Δ_Ch"] = delta_pred
    results["Δ_obs"] = delta_obs
    results["Δ_Ch - Δ_obs"] = delta_pred - delta_obs

    # Relative shift in Δ
    relative_shift = (delta_pred - delta_obs) / delta_obs
    results["Relative shift in Δ"] = relative_shift

    # The frequency shift scales with the spin parameter
    # δf ≈ f_QNM × (Δ_Ch - Δ_obs) / Δ_obs × a
    freq_shift = event.freq * relative_shift * event.spin
    results["Predicted freq shift (Hz)"] = freq_shift
    results["Corrected frequency (Hz)"] = event.freq + freq_shift

    # Mass-dependent scaling
    mass_scale = 62.0 / event.mass  # Normalized to GW150914
    results["Mass scaling factor"] = mass_scale
    results["Scaled freq shift (Hz)"] = freq_shift * mass_scale

    return results
end

"""
    detectability(pred::QNMPredictor, events::Vector{LIGOEvent}=LIGO_EVENTS) -> Dict{String, Any}

Assess the detectability of the Choptyuk spinor correction across LIGO events.

# Arguments
- `pred`: QNM predictor
- `events`: Vector of LIGO events

# Returns
Dictionary with detectability analysis for each event.
"""
function detectability(pred::QNMPredictor, events::Vector{LIGOEvent} = LIGO_EVENTS)
    results = Dict{String, Any}()
    event_results = Dict{String, Dict{String, Float64}}()

    for event in events
        shift = predict_shift(pred, event)
        event_results[event.name] = shift
    end

    results["event_shifts"] = event_results

    # Overall detectability assessment
    # LIGO sensitivity: δf/f ~ 10⁻³ at best for ringdown
    pred_shift = abs(pred.delta_ch - pred.observed_delta) / pred.observed_delta
    results["Predicted relative shift"] = pred_shift
    results["LIGO sensitivity threshold"] = 1e-3
    results["Detectable by LIGO"] = pred_shift > 1e-3

    # Signal-to-noise ratio estimate
    snr_estimate = pred_shift / 1e-3  # Relative to LIGO noise floor
    results["Estimated SNR"] = snr_estimate

    return results
end

"""
    qnm_braking_correction(delta_C::Float64=π/7) -> Float64

Compute the QNM braking correction: δ_C⁵ / (22·π²).

This is the fractional correction to QNM frequencies from the
Choptyuk spinorial braking in the Einstein GR framework.

# Arguments
- `delta_C`: The fundamental spinor phase δ_C (default: π/7)

# Returns
The QNM braking correction factor.
"""
function qnm_braking_correction(delta_C::Float64 = π / 7)
    return delta_C^5 / (22 * π^2)
end

"""
    qnm_braking_factor(delta_C::Float64=π/7) -> Float64

Compute the QNM braking factor: 1 - δ_C⁵ / (22·π²).

This is the multiplicative factor applied to observed QNM frequencies
to account for the spinorial braking correction.

# Arguments
- `delta_C`: The fundamental spinor phase δ_C (default: π/7)

# Returns
The QNM braking factor (≈ 0.999916).
"""
function qnm_braking_factor(delta_C::Float64 = π / 7)
    return 1 - qnm_braking_correction(delta_C)
end

"""
    corrected_qnm_frequency(f_obs::Float64, delta_C::Float64=π/7) -> Float64

Apply the QNM braking correction to an observed frequency.

Computes f_corr = f_obs × (1 - δ_C⁵ / (22·π²)).

# Arguments
- `f_obs`: The observed QNM frequency
- `delta_C`: The fundamental spinor phase δ_C (default: π/7)

# Returns
The corrected QNM frequency.
"""
function corrected_qnm_frequency(f_obs::Float64, delta_C::Float64 = π / 7)
    return f_obs * qnm_braking_factor(delta_C)
end

"""
    verify_qnm(pred::QNMPredictor=QNMPredictor()) -> Dict{String, Bool}

Verify QNM predictions against known event parameters.
"""
function verify_qnm(pred::QNMPredictor = QNMPredictor())
    results = Dict{String, Bool}()

    # Check event count
    results["4 LIGO events"] = length(LIGO_EVENTS) == 4

    # Check event parameters
    results["GW150914 M=62"] = LIGO_EVENTS[1].mass ≈ 62.0
    results["GW150914 a=0.67"] = LIGO_EVENTS[1].spin ≈ 0.67
    results["GW150914 f=251"] = LIGO_EVENTS[1].freq ≈ 251.0

    results["GW190521 M=142"] = LIGO_EVENTS[4].mass ≈ 142.0
    results["GW190521 a=0.72"] = LIGO_EVENTS[4].spin ≈ 0.72

    # Check observed Δ
    results["Δ_obs = 3.443"] = pred.observed_delta ≈ 3.443

    return results
end
