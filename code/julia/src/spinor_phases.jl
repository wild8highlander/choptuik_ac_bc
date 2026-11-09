"""
    SpinorPhases

Struct representing the three fundamental spinor phases δ_A, δ_B, δ_C
on the Klein quartic curve.

These phases arise from the spinor corrections b-C and a-C and are
determined by the geometry of the Klein curve and its automorphism group PSL(2,7).

# Fields
- `delta_A::Float64`: Phase δ_A = π/2 (from the b-C correction)
- `delta_B::Float64`: Phase δ_B = π/3 (from the intermediate structure)
- `delta_C::Float64`: Phase δ_C = π/7 (from PSL(2,7) symmetry, fundamental)
"""
@kwdef struct SpinorPhases
    delta_A::Float64 = π / 2
    delta_B::Float64 = π / 3
    delta_C::Float64 = π / 7
end

"""
    SpinorStructure

A single spinor structure representing one of the 64 = 2^6 possible
combinations of sign choices for the spinor bundle.

# Fields
- `index::Int`: Index from 1 to 64
- `signs::Vector{Int}`: Vector of 6 signs, each ±1
- `phase_signature::Float64`: Computed phase signature Σᵢ sᵢ δᵢ
"""
struct SpinorStructure
    index::Int
    signs::Vector{Int}
    phase_signature::Float64
end

"""
    enumerate_64_structures(phases::SpinorPhases=SpinorPhases()) -> Vector{SpinorStructure}

Enumerate all 64 = 2^6 spinor structures on the Klein curve.

Each structure corresponds to a choice of signs for 6 spinor components,
yielding 2^6 = 64 distinct spinor bundles. The phase signature is computed
as a weighted sum using the fundamental phases.

# Arguments
- `phases`: The spinor phases (default: canonical values)

# Returns
Vector of 64 `SpinorStructure` objects, sorted by phase signature.

# Mathematical Details
The 6 components correspond to the 6 nontrivial characters of the
spinor representation of PSL(2,7) on the Klein curve.
"""
function enumerate_64_structures(phases::SpinorPhases = SpinorPhases())
    structures = SpinorStructure[]

    # The 6 phase weights correspond to the spinor decomposition
    # on the Klein curve: δ_A, δ_B, δ_C appear with multiplicities
    weights = Float64[
        phases.delta_A,
        phases.delta_A,
        phases.delta_B,
        phases.delta_B,
        phases.delta_C,
        phases.delta_C,
    ]

    idx = 1
    # Iterate over all 2^6 sign combinations
    for mask in 0:63
        signs = Int[]
        signature = 0.0
        for bit in 0:5
            s = (mask >> bit) & 1 == 0 ? 1 : -1
            push!(signs, s)
            signature += s * weights[bit + 1]
        end
        push!(structures, SpinorStructure(idx, signs, signature))
        idx += 1
    end

    # Sort by phase signature for canonical ordering
    sort!(structures; by = s -> s.phase_signature)
    return structures
end

"""
    verify_phase_relations(phases::SpinorPhases=SpinorPhases()) -> Dict{String, Bool}

Verify the algebraic and numerical relations among the spinor phases.

Checks:
1. δ_A = π/2
2. δ_B = π/3
3. δ_C = π/7
4. δ_A + δ_B + δ_C < 2π
5. δ_A : δ_B : δ_C ratio consistency with 1/2 : 1/3 : 1/7
"""
function verify_phase_relations(phases::SpinorPhases = SpinorPhases())
    results = Dict{String, Bool}()

    # Check individual phase values
    results["δ_A = π/2"] = abs(phases.delta_A - π / 2) < 1e-10
    results["δ_B = π/3"] = abs(phases.delta_B - π / 3) < 1e-10
    results["δ_C = π/7"] = abs(phases.delta_C - π / 7) < 1e-10

    # Sum constraint
    phase_sum = phases.delta_A + phases.delta_B + phases.delta_C
    results["Σδ < 2π"] = phase_sum < 2π

    # Ratio consistency: δ_A : δ_B : δ_C = 1/2 : 1/3 : 1/7
    r_AB = phases.delta_A / phases.delta_B
    r_expected_AB = (1 / 2) / (1 / 3)
    results["δ_A/δ_B = 3/2"] = abs(r_AB - r_expected_AB) < 1e-10

    r_BC = phases.delta_B / phases.delta_C
    r_expected_BC = (1 / 3) / (1 / 7)
    results["δ_B/δ_C = 7/3"] = abs(r_BC - r_expected_BC) < 1e-10

    # 64 structures count
    structures = enumerate_64_structures(phases)
    results["64 structures"] = length(structures) == 64

    # Phase signatures are symmetric about zero
    sigs = [s.phase_signature for s in structures]
    results["Signatures symmetric"] = abs(sum(sigs)) < 1e-10

    return results
end

"""
    phase_symmetry_classes(phases::SpinorPhases=SpinorPhases()) -> Dict{Float64, Int}

Compute the symmetry classes of spinor structures grouped by phase signature.

Returns a dictionary mapping each distinct phase signature to its multiplicity.
"""
function phase_symmetry_classes(phases::SpinorPhases = SpinorPhases())
    structures = enumerate_64_structures(phases)
    classes = Dict{Float64, Int}()
    for s in structures
        key = round(s.phase_signature; digits = 10)
        classes[key] = get(classes, key, 0) + 1
    end
    return classes
end
