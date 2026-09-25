"""
    Interactive REPL menu for the Choptyuk spinor monograph.

Provides a full interactive menu with options for running verification,
simulation, configuring parameters, generating reports and plots,
and more.
"""
module InteractiveMenu

using ..ChoptyukSpinor
using Printf
using JSON

"""
    MenuState

State of the interactive menu session.

# Fields
- `simulator::Simulator`: Active simulator instance
- `running::Bool`: Whether the menu loop is active
- `output_dir::String`: Output directory for reports and plots
"""
mutable struct MenuState
    simulator::Simulator
    running::Bool
    output_dir::String
end

"""
    MenuState(; kwargs...) -> MenuState

Construct a menu state with default or custom parameters.
"""
function MenuState(; output_dir::String = "output", kwargs...)
    sim = Simulator(; kwargs...)
    return MenuState(sim, true, output_dir)
end

"""
    print_header()

Print the menu header.
"""
function print_header()
    println()
    println("=" ^ 70)
    println("  CHOPTYUK SPINOR MONOGRAPH — Interactive Verification System")
    println("  Spinor corrections b-C and a-C on the Klein quartic curve")
    println("=" ^ 70)
    println()
end

"""
    print_menu()

Print the main menu options.
"""
function print_menu()
    println("Main Menu:")
    println("-" ^ 40)
    println("  1. Run verification")
    println("  2. Run simulation")
    println("  3. Configure parameters")
    println("  4. Custom hypothesis")
    println("  5. Generate reports")
    println("  6. Generate plots")
    println("  7. View results")
    println("  8. Load preset")
    println("  9. Save config")
    println("  0. Exit")
    println("-" ^ 40)
end

"""
    get_input(prompt::String; default::String="") -> String

Get user input with an optional default value.
"""
function get_input(prompt::String; default::String = "")
    if isempty(default)
        print("$prompt: ")
    else
        print("$prompt [$default]: ")
    end
    input = readline()
    input = strip(input)
    return isempty(input) ? default : input
end

"""
    get_float(prompt::String; default::Float64=0.0) -> Float64

Get a float from user input.
"""
function get_float(prompt::String; default::Float64 = 0.0)
    input = get_input(prompt; default = string(default))
    try
        return parse(Float64, input)
    catch
        println("  Invalid number, using default: $default")
        return default
    end
end

"""
    get_int(prompt::String; default::Int=0) -> Int

Get an integer from user input.
"""
function get_int(prompt::String; default::Int = 0)
    input = get_input(prompt; default = string(default))
    try
        return parse(Int, input)
    catch
        println("  Invalid number, using default: $default")
        return default
    end
end

"""
    run_verification(state::MenuState)

Run all verification checks and display results.
"""
function run_verification(state::MenuState)
    println("\n--- Running Verification ---")
    cfg = state.simulator.config

    # Klein curve
    println("\n[1] Klein Curve:")
    K = KleinCurve(lambda_1 = cfg.lambda_1, R = Int(cfg.R))
    kv = verify_relations(K)
    all_pass = true
    for (key, val) in sort(collect(pairs(kv)))
        status = val ? "PASS" : "FAIL"
        val || (all_pass = false)
        @printf("  [%s] %s\n", status, key)
    end
    @printf("\n  Overall: %s\n", all_pass ? "ALL PASS" : "SOME FAILURES")

    # Spinor phases
    println("\n[2] Spinor Phases:")
    phases = SpinorPhases(delta_C = cfg.delta_C)
    pv = verify_phase_relations(phases)
    all_pass = true
    for (key, val) in sort(collect(pairs(pv)))
        status = val ? "PASS" : "FAIL"
        val || (all_pass = false)
        @printf("  [%s] %s\n", status, key)
    end
    @printf("\n  Overall: %s\n", all_pass ? "ALL PASS" : "SOME FAILURES")

    # Dirac operator
    println("\n[3] Dirac Operator:")
    D = DiracOperator(lambda_D2_triv = cfg.lambda_D2_triv, lambda_1 = cfg.lambda_1, R = cfg.R)
    dv = verify_dirac_relations(D)
    all_pass = true
    for (key, val) in sort(collect(pairs(dv)))
        status = val ? "PASS" : "FAIL"
        val || (all_pass = false)
        @printf("  [%s] %s\n", status, key)
    end
    @printf("\n  Overall: %s\n", all_pass ? "ALL PASS" : "SOME FAILURES")

    # Choptyuk formula
    println("\n[4] Choptyuk Formula:")
    cf = ChoptyukFormula(lambda_D2_triv = cfg.lambda_D2_triv, delta_C = cfg.delta_C)
    cv = verify_choptyuk_formula(cf; observed = cfg.observed_delta)
    for (key, val) in sort(collect(pairs(cv)))
        if isa(val, Bool)
            @printf("  [%s] %s\n", val ? "PASS" : "FAIL", key)
        else
            @printf("  %s = %.6f\n", key, Float64(val))
        end
    end

    # QNM
    println("\n[5] QNM Predictions:")
    qv = verify_qnm()
    for (key, val) in sort(collect(pairs(qv)))
        @printf("  [%s] %s\n", val ? "PASS" : "FAIL", key)
    end

    # Surfaces
    println("\n[6] Surface Verification:")
    for S in ALL_SURFACES
        sv = verify_surface(S)
        n_pass = count(values(sv))
        @printf("  %s: %d/%d checks passed\n", S.name, n_pass, length(sv))
    end

    println("\n--- Verification Complete ---")
end

"""
    run_simulation(state::MenuState)

Run the full simulation.
"""
function run_simulation(state::MenuState)
    println("\n--- Running Full Simulation ---")
    results = run_full_simulation(state.simulator)
    println("  Simulation complete.")
    @printf("  Results keys: %s\n", join(sort(collect(keys(results))), ", "))
    @printf("  Log entries: %d\n", length(state.simulator.log))
    println("\n--- Simulation Complete ---")
end

"""
    configure_parameters(state::MenuState)

Interactively configure simulation parameters.
"""
function configure_parameters(state::MenuState)
    cfg = state.simulator.config

    println("\n--- Configure Parameters ---")
    println("  Current values shown in brackets. Press Enter to keep.")

    cfg.lambda_D2_triv = get_float("  λ_{D²,triv}"; default = cfg.lambda_D2_triv)
    cfg.lambda_1 = get_float("  λ₁ (Laplacian eigenvalue)"; default = cfg.lambda_1)
    cfg.delta_C = get_float("  δ_C (spinor phase)"; default = cfg.delta_C)
    cfg.R = get_float("  R (scalar curvature)"; default = cfg.R)
    cfg.observed_delta = get_float("  Δ_obs (observed)"; default = cfg.observed_delta)
    cfg.tolerance = get_float("  Tolerance"; default = cfg.tolerance)
    cfg.n_sweep = get_int("  N_sweep (sweep points)"; default = cfg.n_sweep)

    println("\n  Parameters updated.")
    println("--- Configuration Complete ---")
end

"""
    custom_hypothesis(state::MenuState)

Run a custom hypothesis test with user-specified parameters.
"""
function custom_hypothesis(state::MenuState)
    println("\n--- Custom Hypothesis Test ---")

    lambda_D2 = get_float("  λ_{D²,triv}"; default = state.simulator.config.lambda_D2_triv)
    delta_C = get_float("  δ_C"; default = state.simulator.config.delta_C)
    observed = get_float("  Δ_obs"; default = state.simulator.config.observed_delta)
    tolerance = get_float("  Tolerance"; default = state.simulator.config.tolerance)

    tester = HypothesisTester(
        lambda_D2_triv = lambda_D2,
        delta_C = delta_C,
        observed_delta = observed,
        tolerance = tolerance,
    )
    result = test_hypothesis(tester)

    @printf("\n  Results:\n")
    @printf("    Δ_Ch = %.6f\n", result.delta_ch)
    @printf("    Δ_obs = %.6f\n", result.delta_obs)
    @printf("    Deviation = %.6f\n", result.deviation)
    @printf("    Relative deviation = %.6f\n", result.relative_deviation)
    status = result.accepted ? "ACCEPTED" : "REJECTED"
    @printf("    Hypothesis: %s (tolerance = %.6f)\n", status, result.tolerance)

    # Sensitivity analysis
    sens = sensitivity_analysis(tester)
    println("\n  Sensitivity Analysis:")
    for (param, val) in sort(collect(pairs(sens)))
        @printf("    ∂Δ_Ch/∂%s = %.6f\n", param, val)
    end

    println("\n--- Custom Hypothesis Complete ---")
end

"""
    generate_reports(state::MenuState)

Generate reports in all formats.
"""
function generate_reports(state::MenuState)
    println("\n--- Generating Reports ---")

    if isempty(state.simulator.results)
        println("  No results yet. Running simulation first...")
        run_full_simulation(state.simulator)
    end

    Reporting.generate_all_reports(
        state.simulator.results,
        state.simulator.log;
        dir = state.output_dir,
    )

    println("  Reports saved to: $(state.output_dir)")
    println("--- Reports Complete ---")
end

"""
    generate_plots(state::MenuState)

Generate all visualization plots.
"""
function generate_plots(state::MenuState)
    println("\n--- Generating Plots ---")

    if isempty(state.simulator.results)
        println("  No results yet. Running simulation first...")
        run_full_simulation(state.simulator)
    end

    Visualization.generate_all_plots(
        state.simulator.results;
        dir = state.output_dir,
    )

    println("  Plots saved to: $(state.output_dir)")
    println("--- Plots Complete ---")
end

"""
    view_results(state::MenuState)

View the current results.
"""
function view_results(state::MenuState)
    println("\n--- Current Results ---")

    if isempty(state.simulator.results)
        println("  No results yet. Run verification or simulation first.")
        return
    end

    for (key, val) in sort(collect(pairs(state.simulator.results)))
        if isa(val, HypothesisResult)
            @printf("  %s:\n", key)
            @printf("    Δ_Ch = %.6f, Δ_obs = %.6f\n", val.delta_ch, val.delta_obs)
            @printf("    Deviation = %.6f, %s\n", val.deviation, val.accepted ? "ACCEPTED" : "REJECTED")
        elseif isa(val, Dict{String, Bool})
            n_pass = count(values(val))
            @printf("  %s: %d/%d checks passed\n", key, n_pass, length(val))
        else
            @printf("  %s: (%s)\n", key, typeof(val))
        end
    end

    println("\n--- End of Results ---")
end

"""
    load_preset(state::MenuState)

Load a preset configuration.
"""
function load_preset(state::MenuState)
    println("\n--- Load Preset ---")
    println("  Available presets:")
    println("    1. standard (canonical Klein curve values)")
    println("    2. custom JSON file")

    choice = get_input("  Select preset"; default = "1")

    if choice == "1"
        # Look for standard.json in presets directory
        preset_path = joinpath(@__DIR__, "..", "presets", "standard.json")
        if isfile(preset_path)
            _load_preset_file(state, preset_path)
        else
            # Use built-in defaults
            println("  Loading built-in standard preset...")
            cfg = state.simulator.config
            cfg.lambda_D2_triv = 3.338
            cfg.lambda_1 = 3.838
            cfg.delta_C = π / 7
            cfg.R = -2.0
            cfg.observed_delta = 3.443
            cfg.tolerance = 0.01
            cfg.n_sweep = 100
            println("  Standard preset loaded.")
        end
    elseif choice == "2"
        filepath = get_input("  Enter preset file path")
        if isfile(filepath)
            _load_preset_file(state, filepath)
        else
            println("  File not found: $filepath")
        end
    else
        println("  Invalid choice.")
    end

    println("--- Preset Loading Complete ---")
end

"""
    _load_preset_file(state::MenuState, filepath::String)

Load a preset from a JSON file.
"""
function _load_preset_file(state::MenuState, filepath::String)
    try
        data = JSON.parsefile(filepath)
        cfg = state.simulator.config
        haskey(data, "lambda_D2_triv") && (cfg.lambda_D2_triv = Float64(data["lambda_D2_triv"]))
        haskey(data, "lambda_1") && (cfg.lambda_1 = Float64(data["lambda_1"]))
        haskey(data, "delta_C") && (cfg.delta_C = Float64(data["delta_C"]))
        haskey(data, "R") && (cfg.R = Float64(data["R"]))
        haskey(data, "observed_delta") && (cfg.observed_delta = Float64(data["observed_delta"]))
        haskey(data, "tolerance") && (cfg.tolerance = Float64(data["tolerance"]))
        haskey(data, "n_sweep") && (cfg.n_sweep = Int(data["n_sweep"]))
        println("  Preset loaded from: $filepath")
    catch e
        println("  Error loading preset: $e")
    end
end

"""
    save_config(state::MenuState)

Save the current configuration to a JSON file.
"""
function save_config(state::MenuState)
    println("\n--- Save Configuration ---")

    filepath = get_input("  Save to file"; default = joinpath(state.output_dir, "config.json"))

    cfg = state.simulator.config
    data = Dict(
        "lambda_D2_triv" => cfg.lambda_D2_triv,
        "lambda_1" => cfg.lambda_1,
        "delta_C" => cfg.delta_C,
        "R" => cfg.R,
        "observed_delta" => cfg.observed_delta,
        "tolerance" => cfg.tolerance,
        "n_sweep" => cfg.n_sweep,
    )

    try
        mkpath(dirname(filepath))
        write(filepath, JSON.json(data, 2))
        println("  Configuration saved to: $filepath")
    catch e
        println("  Error saving configuration: $e")
    end

    println("--- Save Complete ---")
end

"""
    run_interactive(; output_dir::String="output", kwargs...)

Run the interactive menu loop.
"""
function run_interactive(; output_dir::String = "output", kwargs...)
    state = MenuState(; output_dir = output_dir, kwargs...)

    print_header()

    while state.running
        print_menu()
        choice = get_input("Select option"; default = "0")

        try
            if choice == "1"
                run_verification(state)
            elseif choice == "2"
                run_simulation(state)
            elseif choice == "3"
                configure_parameters(state)
            elseif choice == "4"
                custom_hypothesis(state)
            elseif choice == "5"
                generate_reports(state)
            elseif choice == "6"
                generate_plots(state)
            elseif choice == "7"
                view_results(state)
            elseif choice == "8"
                load_preset(state)
            elseif choice == "9"
                save_config(state)
            elseif choice == "0" || lowercase(choice) == "exit"
                println("\nExiting. Goodbye!")
                state.running = false
            else
                println("  Invalid option: $choice")
            end
        catch e
            println("  Error: $e")
            @error "Menu error" exception = (e, catch_backtrace())
        end
    end
end

end # module InteractiveMenu
