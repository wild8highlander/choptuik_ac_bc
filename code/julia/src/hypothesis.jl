"""
    HypothesisConfig

Configuration for the central hypothesis test: whether the Choptyuk
spinor correction Δ_Ch matches the observed value Δ_obs = 3.443.

# Fields
- `lambda_D2_triv::Float64`: Dirac trivial eigenvalue
- `lambda_1::Float64`: First Laplacian eigenvalue
- `delta_C::Float64`: Fundamental spinor phase
- `R::Float64`: Scalar curvature
- `observed_delta::Float64`: Observed Δ from LIGO
- `tolerance::Float64`: Tolerance for hypothesis acceptance
- `n_sweep::Int`: Number of parameter sweep points
"""
@kwdef mutable struct HypothesisConfig
    lambda_D2_triv::Float64 = 3.338
    lambda_1::Float64 = 3.838
    delta_C::Float64 = π / 7
    R::Float64 = -2.0
    observed_delta::Float64 = 3.443
    tolerance::Float64 = 0.01
    n_sweep::Int = 100
end

"""
    HypothesisResult

Result of a hypothesis test.

# Fields
- `delta_ch::Float64`: Computed Choptyuk constant
- `delta_obs::Float64`: Observed value
- `deviation::Float64`: Absolute deviation
- `relative_deviation::Float64`: Relative deviation
- `accepted::Bool`: Whether hypothesis is accepted within tolerance
- `tolerance::Float64`: Tolerance used
- `details::Dict{String, Any}`: Additional details
"""
struct HypothesisResult
    delta_ch::Float64
    delta_obs::Float64
    deviation::Float64
    relative_deviation::Float64
    accepted::Bool
    tolerance::Float64
    details::Dict{String, Any}
end

"""
    HypothesisTester

Tester for the Choptyuk hypothesis with parameter sweep capabilities.

# Fields
- `config::HypothesisConfig`: Test configuration
- `results::Vector{HypothesisResult}`: Accumulated test results
"""
mutable struct HypothesisTester
    config::HypothesisConfig
    results::Vector{HypothesisResult}
end

"""
    HypothesisTester(; kwargs...) -> HypothesisTester

Construct a hypothesis tester with the given configuration.
"""
function HypothesisTester(; kwargs...)
    config = HypothesisConfig(; kwargs...)
    return HypothesisTester(config, HypothesisResult[])
end

"""
    test_hypothesis(tester::HypothesisTester) -> HypothesisResult

Run the central hypothesis test.

Tests whether Δ_Ch (computed from the Choptyuk formula) matches
the observed value Δ_obs within the specified tolerance.

# Arguments
- `tester`: Hypothesis tester with configuration

# Returns
A `HypothesisResult` with the test outcome.
"""
function test_hypothesis(tester::HypothesisTester)
    cfg = tester.config

    # Compute Choptyuk constant
    cf = ChoptyukFormula(
        lambda_D2_triv = cfg.lambda_D2_triv,
        delta_C = cfg.delta_C,
    )
    delta_ch = choptyuk_constant(cf)

    # Compute deviation
    deviation = delta_ch - cfg.observed_delta
    relative_deviation = deviation / cfg.observed_delta

    # Test acceptance
    accepted = abs(deviation) < cfg.tolerance

    # Gather details
    details = Dict{String, Any}()
    details["bC_correction"] = bC_correction(cf)
    details["aC_correction"] = aC_correction(cf)
    details["aC_braking"] = aC_braking(cf)
    details["b_Ch"] = cf.b_Ch
    details["delta_C"] = cfg.delta_C
    details["formula_at_each_order"] = Dict(
        "order_2" => choptyuk_formula(cf; order = 2),
        "order_4" => choptyuk_formula(cf; order = 4),
        "order_5" => choptyuk_formula(cf; order = 5),
        "order_6" => choptyuk_formula(cf; order = 6),
    )

    result = HypothesisResult(
        delta_ch,
        cfg.observed_delta,
        deviation,
        relative_deviation,
        accepted,
        cfg.tolerance,
        details,
    )

    push!(tester.results, result)
    return result
end

"""
    parameter_sweep(tester::HypothesisTester; param::Symbol=:delta_C,
                    range::Tuple{Float64,Float64}=(0.1, 1.5)) -> Vector{HypothesisResult}

Perform a parameter sweep over a specified parameter.

# Arguments
- `tester`: Hypothesis tester
- `param`: Parameter to sweep (:delta_C, :lambda_D2_triv, :lambda_1, :R)
- `range`: (min, max) range for the sweep

# Returns
Vector of hypothesis results for each parameter value.
"""
function parameter_sweep(
    tester::HypothesisTester;
    param::Symbol = :delta_C,
    range::Tuple{Float64, Float64} = (0.1, 1.5),
)
    cfg = tester.config
    sweep_results = HypothesisResult[]

    values = range[1]:(range[2] - range[1]) / (cfg.n_sweep - 1):range[2]

    for val in values
        # Create a modified config
        sweep_cfg = HypothesisConfig(
            lambda_D2_triv = param == :lambda_D2_triv ? val : cfg.lambda_D2_triv,
            lambda_1 = param == :lambda_1 ? val : cfg.lambda_1,
            delta_C = param == :delta_C ? val : cfg.delta_C,
            R = param == :R ? val : cfg.R,
            observed_delta = cfg.observed_delta,
            tolerance = cfg.tolerance,
            n_sweep = cfg.n_sweep,
        )

        sweep_tester = HypothesisTester(sweep_cfg, HypothesisResult[])
        result = test_hypothesis(sweep_tester)
        push!(sweep_results, result)
    end

    append!(tester.results, sweep_results)
    return sweep_results
end

"""
    sensitivity_analysis(tester::HypothesisTester) -> Dict{Symbol, Float64}

Compute the sensitivity of Δ_Ch to each parameter.
"""
function sensitivity_analysis(tester::HypothesisTester)
    cfg = tester.config
    eps = 1e-6

    # Base value
    cf_base = ChoptyukFormula(lambda_D2_triv = cfg.lambda_D2_triv, delta_C = cfg.delta_C)
    base_val = choptyuk_constant(cf_base)

    sensitivities = Dict{Symbol, Float64}()

    # Sensitivity to λ_{D²,triv}
    cf_plus = ChoptyukFormula(lambda_D2_triv = cfg.lambda_D2_triv + eps, delta_C = cfg.delta_C)
    sensitivities[:lambda_D2_triv] = (choptyuk_constant(cf_plus) - base_val) / eps

    # Sensitivity to δ_C
    cf_plus2 = ChoptyukFormula(lambda_D2_triv = cfg.lambda_D2_triv, delta_C = cfg.delta_C + eps)
    sensitivities[:delta_C] = (choptyuk_constant(cf_plus2) - base_val) / eps

    return sensitivities
end
