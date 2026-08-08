"""
    ChoptyukFormula

Struct encapsulating the parameters of the Choptyuk formula for
spinor corrections b-C and a-C on the Klein quartic curve.

The full formula to order δ_C⁶ is:

    Δ_Ch = λ_{D²,triv} + δ_C²/2 - δ_C⁵/22 + δ_C⁴/8 + δ_C⁶/2

where:
- The b-C correction contributes +δ_C²/2
- The a-C braking contributes -δ_C⁵/22
- Higher-order terms contribute +δ_C⁴/8 + δ_C⁶/2

# Fields
- `lambda_D2_triv::Float64`: Dirac trivial eigenvalue (≈ 3.338)
- `delta_C::Float64`: Fundamental spinor phase δ_C = π/7
- `b_Ch::Float64`: Choptyuk b-parameter = 1 - cos(2π/7) ≈ 0.377
"""
@kwdef struct ChoptyukFormula
    lambda_D2_triv::Float64 = 3.338
    delta_C::Float64 = π / 7
    b_Ch::Float64 = 1 - cos(2π / 7)
end

"""
    bC_correction(cf::ChoptyukFormula) -> Float64

Compute the b-C spinor correction: Δ_bC = λ_{D²,triv} + δ_C²/2.

This is the leading spinor correction arising from the b-C map
on the Klein curve.

# Arguments
- `cf`: Choptyuk formula parameters

# Returns
The b-C corrected eigenvalue.
"""
function bC_correction(cf::ChoptyukFormula = ChoptyukFormula())
    return cf.lambda_D2_triv + cf.delta_C^2 / 2
end

"""
    aC_braking(cf::ChoptyukFormula) -> Float64

Compute the a-C braking correction: δ_eff = δ_C⁵/22.

This term arises from the a-C map and represents a strong
suppression (braking) of the correction, approximately 1/1200.

# Arguments
- `cf`: Choptyuk formula parameters

# Returns
The effective a-C braking parameter δ_eff ≈ 1/1200.
"""
function aC_braking(cf::ChoptyukFormula = ChoptyukFormula())
    return cf.delta_C^5 / 22
end

"""
    aC_correction(cf::ChoptyukFormula) -> Float64

Compute the a-C corrected eigenvalue including braking:
Δ_aC = λ_{D²,triv} + δ_C²/2 - δ_C⁵/22.

# Arguments
- `cf`: Choptyuk formula parameters

# Returns
The a-C corrected eigenvalue.
"""
function aC_correction(cf::ChoptyukFormula = ChoptyukFormula())
    return cf.lambda_D2_triv + cf.delta_C^2 / 2 - cf.delta_C^5 / 22
end

"""
    choptyuk_formula(cf::ChoptyukFormula; order::Int=6) -> Float64

Compute the full Choptyuk formula to the specified order.

Orders:
- 2: λ_{D²,triv} + δ_C²/2 (b-C only)
- 4: ... + δ_C⁴/8 (quartic correction)
- 5: ... - δ_C⁵/22 (a-C braking, Choptyuk base)
- 6: ... + δ_C⁶/2 (full to order 6)

Default (order=6) gives the complete formula:
    Δ_Ch = λ_{D²,triv} + δ_C²/2 + δ_C⁴/8 - δ_C⁵/22 + δ_C⁶/2

# Arguments
- `cf`: Choptyuk formula parameters
- `order`: Maximum order to include (2, 4, 5, or 6)

# Returns
The Choptyuk eigenvalue to the specified order.
"""
function choptyuk_formula(cf::ChoptyukFormula = ChoptyukFormula(); order::Int = 6)
    result = cf.lambda_D2_triv

    # Order 2: b-C correction
    result += cf.delta_C^2 / 2

    if order ≥ 4
        # Order 4: quartic correction
        result += cf.delta_C^4 / 8
    end

    if order ≥ 5
        # Order 5: a-C braking (subtracted)
        result -= cf.delta_C^5 / 22
    end

    if order ≥ 6
        # Order 6: sextic correction
        result += cf.delta_C^6 / 2
    end

    return result
end

"""
    choptyuk_constant(cf::ChoptyukFormula=ChoptyukFormula()) -> Float64

Compute the Choptyuk constant Δ_Ch (full formula to order 6).

This is the central prediction of the monograph:
    Δ_Ch = λ_{D²,triv} + δ_C²/2 + δ_C⁴/8 - δ_C⁵/22 + δ_C⁶/2

# Returns
The Choptyuk constant Δ_Ch.
"""
function choptyuk_constant(cf::ChoptyukFormula = ChoptyukFormula())
    return choptyuk_formula(cf; order = 6)
end

"""
    imaginary_correction(delta_C::Float64) -> Float64

Compute the imaginary correction factor: 1 - δ_C / π².

This arises from the 4D spin manifold extension of the Choptyuk formula,
accounting for the imaginary part of the spinorial phase.

# Arguments
- `delta_C`: The fundamental spinor phase δ_C

# Returns
The imaginary correction factor.
"""
function imaginary_correction(delta_C::Float64)
    return 1 - delta_C / π^2
end

"""
    kahler_correction(delta_C::Float64) -> Float64

Compute the Kähler surface correction: δ_C²/2 - δ_C⁵/22.

This is the combined b-C and a-C correction on a Kähler surface,
representing the leading spinor correction minus the braking term.

# Arguments
- `delta_C`: The fundamental spinor phase δ_C

# Returns
The Kähler correction value.
"""
function kahler_correction(delta_C::Float64)
    return delta_C^2 / 2 - delta_C^5 / 22
end

"""
    tyukovsky_correction(delta_0::Float64, delta_C::Float64) -> Float64

Compute the Tyukovsky-corrected exponent: δ₀ + δ_C²/2 - δ_C⁵/22.

This adapts the Choptyuk spinorial corrections to the Tyukovsky critical
exponent, adding the Kähler correction to the bare critical exponent δ₀.

# Arguments
- `delta_0`: The bare critical exponent
- `delta_C`: The fundamental spinor phase δ_C

# Returns
The corrected critical exponent.
"""
function tyukovsky_correction(delta_0::Float64, delta_C::Float64)
    return delta_0 + delta_C^2 / 2 - delta_C^5 / 22
end

"""
    einstein_qnm_correction(delta_C::Float64) -> Float64

Compute the Einstein GR / QNM correction: δ_C⁵ / (22·π²).

This correction arises from the interplay between the Choptyuk spinorial
braking (δ_C⁵/22) and the Einstein GR framework, producing a small
correction to quasi-normal mode frequencies.

# Arguments
- `delta_C`: The fundamental spinor phase δ_C

# Returns
The Einstein QNM correction factor.
"""
function einstein_qnm_correction(delta_C::Float64)
    return delta_C^5 / (22 * π^2)
end

"""
    einstein_qnm_factor(delta_C::Float64) -> Float64

Compute the Einstein QNM frequency factor: 1 - δ_C⁵ / (22·π²).

This is the multiplicative factor applied to QNM frequencies to
account for the spinorial braking correction in the Einstein GR framework.

# Arguments
- `delta_C`: The fundamental spinor phase δ_C

# Returns
The Einstein QNM frequency factor (≈ 0.999916).
"""
function einstein_qnm_factor(delta_C::Float64)
    return 1 - einstein_qnm_correction(delta_C)
end

"""
    corrected_qnm_frequency(omega::Float64, delta_C::Float64) -> Float64

Compute the corrected QNM frequency: ω · (1 - δ_C⁵ / (22·π²)).

Applies the Einstein QNM braking factor to an observed or computed
QNM frequency.

# Arguments
- `omega`: The uncorrected QNM frequency
- `delta_C`: The fundamental spinor phase δ_C

# Returns
The spinorially-corrected QNM frequency.
"""
function corrected_qnm_frequency(omega::Float64, delta_C::Float64)
    return omega * einstein_qnm_factor(delta_C)
end

"""
    verify_choptyuk_formula(cf::ChoptyukFormula=ChoptyukFormula(); observed::Float64=3.443) -> Dict{String, Any}

Verify all relations of the Choptyuk formula and compare with observation.

# Arguments
- `cf`: Choptyuk formula parameters
- `observed`: The observed value of Δ from LIGO data (default: 3.443)

# Returns
Dictionary with computed values and comparison metrics.
"""
function verify_choptyuk_formula(cf::ChoptyukFormula = ChoptyukFormula(); observed::Float64 = 3.443)
    results = Dict{String, Any}()

    # Individual terms
    results["λ_{D²,triv}"] = cf.lambda_D2_triv
    results["δ_C"] = cf.delta_C
    results["δ_C²/2 (b-C)"] = cf.delta_C^2 / 2
    results["δ_C⁴/8"] = cf.delta_C^4 / 8
    results["δ_C⁵/22 (a-C braking)"] = cf.delta_C^5 / 22
    results["δ_C⁶/2"] = cf.delta_C^6 / 2
    results["b_Ch = 1 - cos(2π/7)"] = cf.b_Ch

    # Verify b_Ch ≈ 0.377
    results["b_Ch ≈ 0.377"] = abs(cf.b_Ch - 0.377) < 0.001

    # Verify a-C braking ≈ 1/1200
    braking = aC_braking(cf)
    results["δ_eff ≈ 1/1200"] = abs(braking - 1 / 1200) < 0.0001

    # Compute at each order
    for order in [2, 4, 5, 6]
        results["Δ(order=$order)"] = choptyuk_formula(cf; order = order)
    end

    # Choptyuk constant (full)
    delta_ch = choptyuk_constant(cf)
    results["Δ_Ch (full)"] = delta_ch

    # Comparison with observation
    results["Δ_observed"] = observed
    deviation = delta_ch - observed
    results["Deviation (Δ_Ch - Δ_obs)"] = deviation
    results["Relative deviation"] = deviation / observed

    # b-C and a-C corrections
    results["Δ_bC"] = bC_correction(cf)
    results["Δ_aC"] = aC_correction(cf)

    return results
end
