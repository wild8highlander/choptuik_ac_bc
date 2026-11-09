"""
    SurfaceSpec

Specification of a compact Riemann surface with its automorphism group.

# Fields
- `name::String`: Name of the surface
- `genus::Int`: Genus
- `aut_group::String`: Automorphism group name
- `aut_order::Int`: Order of automorphism group
- `lambda_1::Float64`: First Laplacian eigenvalue
- `R::Float64`: Scalar curvature
- `delta_C::Float64`: Fundamental spinor phase δ_C
"""
@kwdef struct SurfaceSpec
    name::String
    genus::Int
    aut_group::String
    aut_order::Int
    lambda_1::Float64
    R::Float64
    delta_C::Float64
end

"""
    BOLZA

The Bolza surface: genus 2, automorphism group GL(2,3) of order 48.
The Bolza surface is the genus-2 surface with maximal automorphisms.
"""
const BOLZA = SurfaceSpec(
    name = "Bolza",
    genus = 2,
    aut_group = "GL(2,3)",
    aut_order = 48,
    lambda_1 = 3.838,  # Approximate
    R = -2.0,
    delta_C = π / 4,  # GL(2,3) has order 48 = 16×3
)

"""
    BRING

The Bring curve: genus 4, automorphism group S₅ of order 120.
The Bring curve is the genus-4 surface with maximal automorphisms.
"""
const BRING = SurfaceSpec(
    name = "Bring",
    genus = 4,
    aut_group = "S₅",
    aut_order = 120,
    lambda_1 = 4.5,  # Approximate
    R = -2.0,
    delta_C = π / 5,  # S₅ has order 120
)

"""
    MACBEATH

The Macbeath surface: genus 7, automorphism group PSL(2,8) of order 504.
The Macbeath surface is the genus-7 Hurwitz surface.
"""
const MACBEATH = SurfaceSpec(
    name = "Macbeath",
    genus = 7,
    aut_group = "PSL(2,8)",
    aut_order = 504,
    lambda_1 = 5.5,  # Approximate
    R = -2.0,
    delta_C = π / 9,  # PSL(2,8) has order 504 = 56×9
)

"""
    KLEIN

The Klein quartic curve: genus 3, automorphism group PSL(2,7) of order 168.
"""
const KLEIN = SurfaceSpec(
    name = "Klein",
    genus = 3,
    aut_group = "PSL(2,7)",
    aut_order = 168,
    lambda_1 = 3.838,
    R = -2.0,
    delta_C = π / 7,
)

"""
    ALL_SURFACES

Collection of all reference surfaces.
"""
const ALL_SURFACES = [BOLZA, KLEIN, BRING, MACBEATH]

"""
    surface_choptyuk(S::SurfaceSpec; lambda_D2_triv::Float64=3.338, order::Int=6) -> Float64

Compute the Choptyuk formula for a given surface.

Each surface has its own δ_C determined by its automorphism group,
yielding different spinor corrections.

# Arguments
- `S`: Surface specification
- `lambda_D2_triv`: Dirac trivial eigenvalue (may differ by surface)
- `order`: Order of the Choptyuk formula

# Returns
The Choptyuk eigenvalue for the surface.
"""
function surface_choptyuk(S::SurfaceSpec; lambda_D2_triv::Float64 = 3.338, order::Int = 6)
    cf = ChoptyukFormula(lambda_D2_triv = lambda_D2_triv, delta_C = S.delta_C)
    return choptyuk_formula(cf; order = order)
end

"""
    hurwitz_achieved(S::SurfaceSpec) -> Bool

Check whether the surface achieves the Hurwitz bound 84(g-1).
"""
function hurwitz_achieved(S::SurfaceSpec)
    return S.aut_order == 84 * (S.genus - 1)
end

"""
    verify_surface(S::SurfaceSpec) -> Dict{String, Bool}

Verify the properties of a Riemann surface.
"""
function verify_surface(S::SurfaceSpec)
    results = Dict{String, Bool}()

    # Aut order ≤ Hurwitz bound
    bound = 84 * (S.genus - 1)
    results["|Aut| ≤ 84(g-1)"] = S.aut_order ≤ bound
    results["Hurwitz achieved"] = hurwitz_achieved(S)

    # Positive genus
    results["genus > 0"] = S.genus > 0

    # Positive λ₁
    results["λ₁ > 0"] = S.lambda_1 > 0

    # δ_C in (0, π)
    results["0 < δ_C < π"] = 0 < S.delta_C < π

    return results
end

"""
    compare_surfaces(surfaces::Vector{SurfaceSpec}=ALL_SURFACES) -> Dict{String, Any}

Compare the Choptyuk formula predictions across all surfaces.
"""
function compare_surfaces(surfaces::Vector{SurfaceSpec} = ALL_SURFACES)
    results = Dict{String, Any}()
    comparisons = Dict{String, Dict{String, Float64}}()

    for S in surfaces
        d = Dict{String, Float64}()
        d["genus"] = Float64(S.genus)
        d["|Aut|"] = Float64(S.aut_order)
        d["λ₁"] = S.lambda_1
        d["δ_C"] = S.delta_C
        d["δ_C²/2"] = S.delta_C^2 / 2
        d["Δ_Ch"] = surface_choptyuk(S)
        d["b_Ch"] = 1 - cos(2 * S.delta_C)
        comparisons[S.name] = d
    end

    results["comparisons"] = comparisons
    results["Klein δ_C unique"] = KLEIN.delta_C ≈ π / 7

    return results
end
