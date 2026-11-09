"""
    Simulator

Main simulation engine for the Choptyuk spinor monograph.

Runs parameter sweeps, convergence analysis, and produces
detailed numerical results.

# Fields
- `config::HypothesisConfig`: Simulation configuration
- `results::Dict{String, Any}`: Accumulated simulation results
- `log::Vector{String}`: Execution log
"""
mutable struct Simulator
    config::HypothesisConfig
    results::Dict{String, Any}
    log::Vector{String}
end

"""
    Simulator(; kwargs...) -> Simulator

Construct a simulator with the given configuration.
"""
function Simulator(; kwargs...)
    config = HypothesisConfig(; kwargs...)
    return Simulator(config, Dict{String, Any}(), String[])
end

"""
    _log!(sim::Simulator, msg::String)

Add a timestamped message to the simulation log.
"""
function _log!(sim::Simulator, msg::String)
    timestamp = Dates.format(Dates.now(), "yyyy-mm-dd HH:MM:SS")
    push!(sim.log, "[$timestamp] $msg")
end

"""
    sweep_delta_C(sim::Simulator; n_points::Int=200,
                  delta_C_min::Float64=0.1, delta_C_max::Float64=1.5) -> Dict{String, Vector{Float64}}

Sweep the fundamental spinor phase δ_C and compute the Choptyuk formula
at each point.
"""
function sweep_delta_C(
    sim::Simulator;
    n_points::Int = 200,
    delta_C_min::Float64 = 0.1,
    delta_C_max::Float64 = 1.5,
)
    _log!(sim, "Starting δ_C sweep: $delta_C_min to $delta_C_max, $n_points points")

    delta_C_vals = Float64[]
    delta_ch_vals = Float64[]
    deviation_vals = Float64[]
    order2_vals = Float64[]
    order4_vals = Float64[]
    order5_vals = Float64[]
    order6_vals = Float64[]
    bCh_vals = Float64[]

    step = (delta_C_max - delta_C_min) / (n_points - 1)

    for i in 1:n_points
        dc = delta_C_min + (i - 1) * step
        cf = ChoptyukFormula(
            lambda_D2_triv = sim.config.lambda_D2_triv,
            delta_C = dc,
        )

        push!(delta_C_vals, dc)
        push!(delta_ch_vals, choptyuk_constant(cf))
        push!(deviation_vals, choptyuk_constant(cf) - sim.config.observed_delta)
        push!(order2_vals, choptyuk_formula(cf; order = 2))
        push!(order4_vals, choptyuk_formula(cf; order = 4))
        push!(order5_vals, choptyuk_formula(cf; order = 5))
        push!(order6_vals, choptyuk_formula(cf; order = 6))
        push!(bCh_vals, 1 - cos(2 * dc))
    end

    result = Dict{String, Vector{Float64}}(
        "delta_C" => delta_C_vals,
        "delta_Ch" => delta_ch_vals,
        "deviation" => deviation_vals,
        "order_2" => order2_vals,
        "order_4" => order4_vals,
        "order_5" => order5_vals,
        "order_6" => order6_vals,
        "b_Ch" => bCh_vals,
    )

    sim.results["sweep_delta_C"] = result
    _log!(sim, "δ_C sweep complete: $(length(delta_C_vals)) points computed")

    return result
end

"""
    sweep_lambda_1(sim::Simulator; n_points::Int=200,
                   lambda_min::Float64=2.0, lambda_max::Float64=6.0) -> Dict{String, Vector{Float64}}

Sweep the first Laplacian eigenvalue λ₁ and study its effect
on the Choptyuk formula via the Lichnerowicz relation.
"""
function sweep_lambda_1(
    sim::Simulator;
    n_points::Int = 200,
    lambda_min::Float64 = 2.0,
    lambda_max::Float64 = 6.0,
)
    _log!(sim, "Starting λ₁ sweep: $lambda_min to $lambda_max, $n_points points")

    lambda_vals = Float64[]
    d2_vals = Float64[]
    delta_ch_vals = Float64[]
    deviation_vals = Float64[]

    step = (lambda_max - lambda_min) / (n_points - 1)

    for i in 1:n_points
        lam = lambda_min + (i - 1) * step
        d2 = lam + sim.config.R / 4

        cf = ChoptyukFormula(
            lambda_D2_triv = d2,
            delta_C = sim.config.delta_C,
        )

        push!(lambda_vals, lam)
        push!(d2_vals, d2)
        push!(delta_ch_vals, choptyuk_constant(cf))
        push!(deviation_vals, choptyuk_constant(cf) - sim.config.observed_delta)
    end

    result = Dict{String, Vector{Float64}}(
        "lambda_1" => lambda_vals,
        "lambda_D2" => d2_vals,
        "delta_Ch" => delta_ch_vals,
        "deviation" => deviation_vals,
    )

    sim.results["sweep_lambda_1"] = result
    _log!(sim, "λ₁ sweep complete: $(length(lambda_vals)) points computed")

    return result
end

"""
    convergence_analysis(sim::Simulator; max_order::Int=10) -> Dict{String, Any}

Analyze the convergence of the Choptyuk formula as higher-order terms are included.
"""
function convergence_analysis(sim::Simulator; max_order::Int = 10)
    _log!(sim, "Starting convergence analysis up to order $max_order")

    cf = ChoptyukFormula(
        lambda_D2_triv = sim.config.lambda_D2_triv,
        delta_C = sim.config.delta_C,
    )

    dc = cf.delta_C

    terms = Float64[]
    partial_sums = Float64[]

    # Order 0: base term
    push!(terms, cf.lambda_D2_triv)
    push!(partial_sums, cf.lambda_D2_triv)

    # Order 2: +δ_C²/2
    t2 = dc^2 / 2
    push!(terms, t2)
    push!(partial_sums, partial_sums[end] + t2)

    # Order 4: +δ_C⁴/8
    t4 = dc^4 / 8
    push!(terms, t4)
    push!(partial_sums, partial_sums[end] + t4)

    # Order 5: -δ_C⁵/22
    t5 = -dc^5 / 22
    push!(terms, t5)
    push!(partial_sums, partial_sums[end] + t5)

    # Order 6: +δ_C⁶/2
    t6 = dc^6 / 2
    push!(terms, t6)
    push!(partial_sums, partial_sums[end] + t6)

    # Higher orders (extrapolated pattern)
    for k in 7:max_order
        sign = (k % 2 == 0) ? 1.0 : -1.0
        denom = 2^(k - 5)
        tk = sign * dc^k / denom
        push!(terms, tk)
        push!(partial_sums, partial_sums[end] + tk)
    end

    # Convergence rates
    convergence_rates = Float64[]
    for i in 2:length(terms)
        if abs(terms[i - 1]) > 1e-15
            push!(convergence_rates, abs(terms[i] / terms[i - 1]))
        else
            push!(convergence_rates, 0.0)
        end
    end

    limit_estimate = partial_sums[end]

    result = Dict{String, Any}(
        "terms" => terms,
        "partial_sums" => partial_sums,
        "convergence_rates" => convergence_rates,
        "limit_estimate" => limit_estimate,
        "final_value" => choptyuk_constant(cf),
        "max_order" => max_order,
        "observed_delta" => sim.config.observed_delta,
        "deviation_at_limit" => limit_estimate - sim.config.observed_delta,
    )

    sim.results["convergence"] = result
    _log!(sim, "Convergence analysis complete: limit ≈ $(round(limit_estimate; digits=6))")

    return result
end

"""
    run_full_simulation(sim::Simulator) -> Dict{String, Any}

Run the complete simulation suite.
"""
function run_full_simulation(sim::Simulator)
    _log!(sim, "=== Starting full simulation ===")

    # Sweep δ_C
    sweep_delta_C(sim)

    # Sweep λ₁
    sweep_lambda_1(sim)

    # Convergence analysis
    convergence_analysis(sim)

    # Hypothesis test
    tester = HypothesisTester(
        lambda_D2_triv = sim.config.lambda_D2_triv,
        delta_C = sim.config.delta_C,
        observed_delta = sim.config.observed_delta,
    )
    hyp_result = test_hypothesis(tester)
    sim.results["hypothesis"] = hyp_result

    # Verification checks
    K = KleinCurve(lambda_1 = sim.config.lambda_1, R = Int(sim.config.R))
    sim.results["klein_verification"] = verify_relations(K)

    phases = SpinorPhases(delta_C = sim.config.delta_C)
    sim.results["phase_verification"] = verify_phase_relations(phases)

    D = DiracOperator(
        lambda_D2_triv = sim.config.lambda_D2_triv,
        lambda_1 = sim.config.lambda_1,
        R = sim.config.R,
    )
    sim.results["dirac_verification"] = verify_dirac_relations(D)

    cf = ChoptyukFormula(
        lambda_D2_triv = sim.config.lambda_D2_triv,
        delta_C = sim.config.delta_C,
    )
    sim.results["choptyuk_verification"] = verify_choptyuk_formula(cf; observed = sim.config.observed_delta)

    # QNM analysis
    pred = QNMPredictor(
        delta_ch = choptyuk_constant(cf),
        observed_delta = sim.config.observed_delta,
    )
    sim.results["qnm_detectability"] = detectability(pred)

    # Surface comparison
    sim.results["surface_comparison"] = compare_surfaces()

    _log!(sim, "=== Full simulation complete ===")

    return sim.results
end
