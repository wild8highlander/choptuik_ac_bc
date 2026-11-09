"""
    K3Surface

The K3 surface as a 4D spin manifold with Betti numbers and Hodge numbers.

The K3 surface is the unique simply-connected compact 4-manifold with
b₂ = 22 and trivial canonical bundle. It plays a central role in the
Choptyuk framework via the Seiberg-Witten equations and the Dirac index.

# Fields
- `b0::Int`: 0th Betti number (default: 1)
- `b1::Int`: 1st Betti number (default: 0)
- `b2::Int`: 2nd Betti number (default: 22)
- `b3::Int`: 3rd Betti number (default: 0)
- `b4::Int`: 4th Betti number (default: 1)
- `hodge_11::Int`: Hodge number h^(1,1) (default: 20)
- `hodge_20::Int`: Hodge number h^(2,0) (default: 1)
- `dirac_index::Int`: Dirac index Â(K3) (default: 2)
- `b2_plus::Int`: b₂⁺ for Seiberg-Witten theory (default: 3)
"""
@kwdef struct K3Surface
    b0::Int = 1
    b1::Int = 0
    b2::Int = 22
    b3::Int = 0
    b4::Int = 1
    hodge_11::Int = 20
    hodge_20::Int = 1
    dirac_index::Int = 2  # Â(K3)
    b2_plus::Int = 3      # For Seiberg-Witten
end

"""
    TyukovskyAdapter

Adaptation of spinorial corrections to Tyukovsky equations.

The Tyukovsky adapter applies the Choptyuk b-C and a-C corrections
to the critical exponent of the Tyukovsky equation for black hole
critical collapse.

# Fields
- `delta_C::Float64`: The fundamental spinor phase δ_C (default: π/7)
"""
@kwdef struct TyukovskyAdapter
    delta_C::Float64 = π / 7
end

"""
    verify_k3(k3::K3Surface) -> Dict{String, Any}

Verify K3 surface properties and Hodge number identities.

Checks:
- b₂ = h^(1,1) + 2·h^(2,0) (Hodge decomposition)
- b₂ / ind(D) = 11 (Dirac index ratio)
- Seiberg-Witten compatibility (b₂⁺ > 1)

# Arguments
- `k3`: K3 surface parameters

# Returns
Dictionary with verification results.
"""
function verify_k3(k3::K3Surface = K3Surface())
    results = Dict{String, Any}()

    # Hodge decomposition: b₂ = h^(1,1) + 2·h^(2,0)
    b2_check = k3.hodge_11 + 2 * k3.hodge_20
    results["b₂ = h^(1,1) + 2·h^(2,0)"] = k3.b2 == b2_check
    results["b₂ computed"] = b2_check
    results["b₂ actual"] = k3.b2

    # Dirac index ratio: b₂ / ind(D) = 11
    b2_over_index = k3.b2 / k3.dirac_index
    results["b₂/ind(D)"] = b2_over_index
    results["b₂/ind(D) = 11"] = b2_over_index ≈ 11.0

    # Seiberg-Witten compatibility
    results["SW compatible (b₂⁺ > 1)"] = k3.b2_plus > 1

    # Hyperkähler (always true for K3)
    results["is_hyperkähler"] = true

    # Euler characteristic: χ = Σ (-1)^i b_i
    euler = k3.b0 - k3.b1 + k3.b2 - k3.b3 + k3.b4
    results["Euler characteristic"] = euler
    results["χ = 24"] = euler == 24

    # Signature: σ = b₂⁺ - b₂⁻ = 2b₂⁺ - b₂ (for K3: b₂⁺=3, b₂⁻=19)
    b2_minus = k3.b2 - k3.b2_plus
    signature = k3.b2_plus - b2_minus
    results["Signature"] = signature
    results["σ = -16"] = signature == -16

    return results
end

"""
    tyukovsky_corrected_exponent(delta_0::Float64, delta_C::Float64) -> Float64

Compute the Tyukovsky-corrected critical exponent.

Applies the Choptyuk spinorial corrections to the bare critical
exponent δ₀ of the Tyukovsky equation:

    δ_corr = δ₀ + δ_C²/2 - δ_C⁵/22

The first correction (δ_C²/2) is the b-C spinor correction, and the
second (δ_C⁵/22) is the a-C braking term.

# Arguments
- `delta_0`: The bare critical exponent
- `delta_C`: The fundamental spinor phase δ_C

# Returns
The corrected critical exponent δ_corr.
"""
function tyukovsky_corrected_exponent(delta_0::Float64, delta_C::Float64)
    return delta_0 + delta_C^2 / 2 - delta_C^5 / 22
end

"""
    verify_b2_uniqueness(delta_C::Float64=π/7) -> Dict{String, Any}

Verify that b₂ = 22 is the unique choice giving the best match to 1/1200.

For different values of b₂ (used as denominator in δ_C⁵/b₂), we check
which gives the closest agreement with 1/1200.

# Arguments
- `delta_C`: The fundamental spinor phase δ_C (default: π/7)

# Returns
Dictionary with b₂ uniqueness verification results.
"""
function verify_b2_uniqueness(delta_C::Float64 = π / 7)
    results = Dict{String, Any}()
    target = 1 / 1200

    b2_results = Dict{Int, Dict{String, Float64}}()
    best_dev = Inf
    best_b2 = 0

    for k in [20, 21, 22, 23, 24]
        approx = delta_C^5 / k
        dev_pct = abs(approx - target) / target * 100
        b2_results[k] = Dict{String, Float64}(
            "approximation" => approx,
            "deviation_pct" => dev_pct,
            "compatible" => dev_pct < 1.0 ? 1.0 : 0.0,
        )
        if dev_pct < best_dev
            best_dev = dev_pct
            best_b2 = k
        end
    end

    results["b2_sweep"] = b2_results
    results["best_b2"] = best_b2
    results["best_deviation_pct"] = best_dev
    results["b2=22 is unique best"] = best_b2 == 22

    return results
end

"""
    verify_enhanced_all() -> Dict{String, Any}

Run all enhanced verification checks and return comprehensive results.

This function verifies:
- K3 surface Hodge number identities
- Tyukovsky correction properties
- b₂ uniqueness for the 1/1200 agreement
- QNM braking corrections
- Imaginary and Kähler corrections

# Returns
Dictionary with all enhanced verification results.
"""
function verify_enhanced_all()
    results = Dict{String, Any}()

    delta_C = π / 7

    # K3 surface verification
    k3 = K3Surface()
    results["k3"] = verify_k3(k3)

    # Tyukovsky adapter
    tyuk = TyukovskyAdapter()
    delta_0 = 0.36  # Reference bare critical exponent
    delta_corr = tyukovsky_corrected_exponent(delta_0, tyuk.delta_C)
    results["tyukovsky"] = Dict{String, Any}(
        "delta_0" => delta_0,
        "delta_C" => tyuk.delta_C,
        "delta_corr" => delta_corr,
        "echo_period" => 1.0 / delta_corr,
    )

    # b₂ uniqueness
    results["b2_uniqueness"] = verify_b2_uniqueness(delta_C)

    # Imaginary correction
    results["imaginary_correction"] = imaginary_correction(delta_C)

    # Kähler correction
    results["kahler_correction"] = kahler_correction(delta_C)

    # QNM braking corrections
    results["qnm_braking_correction"] = qnm_braking_correction(delta_C)
    results["qnm_braking_factor"] = qnm_braking_factor(delta_C)

    # Einstein QNM corrections
    results["einstein_qnm_correction"] = einstein_qnm_correction(delta_C)
    results["einstein_qnm_factor"] = einstein_qnm_factor(delta_C)

    # Consistency check: qnm_braking_correction == einstein_qnm_correction
    results["qnm_einstein_consistent"] =
        abs(qnm_braking_correction(delta_C) - einstein_qnm_correction(delta_C)) < 1e-15

    return results
end
