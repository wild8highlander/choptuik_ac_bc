#!/usr/bin/env julia
#
# Entry point for the Choptyuk Spinor Monograph verification and simulation.
#
# Author: Ishak Khamzatovich Isaev (Исаев Исхак Хамзатович)
# Email:  aslan08_05@mail.ru
# GitHub: https://github.com/wild8highlander
# Repo:   https://github.com/wild8highlander/choptuik_ac_bc
#
# Usage:
#   julia run.jl                    # Interactive mode (default)
#   julia run.jl --non-interactive  # Run full simulation and exit
#   julia run.jl --verify           # Run verification only
#   julia run.jl --output DIR       # Set output directory
#   julia run.jl --help             # Show help
#

using Pkg
using Printf

# Determine project root
const PROJECT_ROOT = dirname(@__FILE__)

# Activate project environment
Pkg.activate(PROJECT_ROOT)

# Load the module
using ChoptyukSpinor

"""
    parse_args(args::Vector{String}) -> Dict{Symbol, Any}

Parse command-line arguments.
"""
function parse_args(args::Vector{String})
    parsed = Dict{Symbol, Any}(
        :mode => :interactive,
        :output_dir => "output",
        :help => false,
    )

    i = 1
    while i ≤ length(args)
        arg = args[i]
        if arg == "--non-interactive" || arg == "-n"
            parsed[:mode] = :noninteractive
        elseif arg == "--verify" || arg == "-v"
            parsed[:mode] = :verify
        elseif arg == "--output" || arg == "-o"
            i += 1
            if i ≤ length(args)
                parsed[:output_dir] = args[i]
            else
                @warn "--output requires a directory argument"
            end
        elseif arg == "--help" || arg == "-h"
            parsed[:help] = true
        else
            @warn "Unknown argument: $arg"
        end
        i += 1
    end

    return parsed
end

"""
    print_help()

Print usage information.
"""
function print_help()
    println("""
    Choptyuk Spinor Monograph — Verification and Simulation

    Usage:
      julia run.jl [OPTIONS]

    Options:
      --non-interactive, -n   Run full simulation non-interactively and exit
      --verify, -v            Run verification checks only and exit
      --output DIR, -o DIR    Set output directory (default: output)
      --help, -h              Show this help message

    Modes:
      interactive (default)   Launch the interactive REPL menu
      non-interactive         Run the full simulation suite and generate
                              all reports and plots, then exit
      verify                  Run all verification checks and print results

    Examples:
      julia run.jl
      julia run.jl --non-interactive --output results/
      julia run.jl --verify
    """)
end

"""
    run_non_interactive(output_dir::String)

Run the full simulation non-interactively.
"""
function run_non_interactive(output_dir::String)
    @info "Running in non-interactive mode"

    # Create simulator
    sim = Simulator()

    # Run full simulation
    @info "Running full simulation..."
    results = run_full_simulation(sim)

    # Print summary
    println("\n" * "=" ^ 70)
    println("  SIMULATION SUMMARY")
    println("=" ^ 70)

    # Choptyuk constant
    cf = ChoptyukFormula()
    @printf("  Δ_Ch (Choptyuk constant) = %.6f\n", choptyuk_constant(cf))
    @printf("  Δ_obs (observed)         = %.6f\n", 3.443)
    @printf("  Deviation                = %.6f\n", choptyuk_constant(cf) - 3.443)
    @printf("  b_Ch = 1 - cos(2π/7)    = %.6f\n", cf.b_Ch)

    # b-C and a-C corrections
    @printf("  Δ_bC (b-C correction)    = %.6f\n", bC_correction(cf))
    @printf("  Δ_aC (a-C correction)    = %.6f\n", aC_correction(cf))
    @printf("  δ_eff (a-C braking)      = %.6f\n", aC_braking(cf))

    println()

    # Verification summary
    if haskey(results, "klein_verification")
        kv = results["klein_verification"]
        n = length(kv)
        p = count(values(kv))
        @printf("  Klein curve:  %d/%d checks passed\n", p, n)
    end

    if haskey(results, "phase_verification")
        pv = results["phase_verification"]
        n = length(pv)
        p = count(values(pv))
        @printf("  Spinor phases: %d/%d checks passed\n", p, n)
    end

    if haskey(results, "dirac_verification")
        dv = results["dirac_verification"]
        n = length(dv)
        p = count(values(dv))
        @printf("  Dirac operator: %d/%d checks passed\n", p, n)
    end

    # Hypothesis
    if haskey(results, "hypothesis")
        hyp = results["hypothesis"]
        @printf("  Hypothesis: %s (deviation = %.6f)\n",
                hyp.accepted ? "ACCEPTED" : "REJECTED",
                hyp.deviation)
    end

    println("=" ^ 70)

    # Generate reports
    @info "Generating reports..."
    Reporting.generate_all_reports(results, sim.log; dir = output_dir)

    # Generate plots
    @info "Generating plots..."
    try
        Visualization.generate_all_plots(results; dir = output_dir)
    catch e
        @warn "Plot generation failed (Plots backend may not be available): $e"
    end

    @info "Non-interactive run complete. Output in: $output_dir"
end

"""
    run_verify_only(output_dir::String)

Run verification checks only.
"""
function run_verify_only(output_dir::String)
    @info "Running verification checks"

    println("\n" * "=" ^ 70)
    println("  CHOPTYUK SPINOR MONOGRAPH — VERIFICATION")
    println("=" ^ 70)

    all_pass = true

    # Klein curve
    println("\n[1] Klein Curve (genus 3, PSL(2,7), order 168)")
    K = KleinCurve()
    kv = verify_relations(K)
    for (key, val) in sort(collect(pairs(kv)))
        @printf("    [%s] %s\n", val ? "PASS" : "FAIL", key)
        val || (all_pass = false)
    end

    # Spinor phases
    println("\n[2] Spinor Phases (δ_A=π/2, δ_B=π/3, δ_C=π/7)")
    phases = SpinorPhases()
    pv = verify_phase_relations(phases)
    for (key, val) in sort(collect(pairs(pv)))
        @printf("    [%s] %s\n", val ? "PASS" : "FAIL", key)
        val || (all_pass = false)
    end

    # Dirac operator
    println("\n[3] Dirac Operator (λ_{D²,triv} ≈ 3.338)")
    D = DiracOperator()
    dv = verify_dirac_relations(D)
    for (key, val) in sort(collect(pairs(dv)))
        @printf("    [%s] %s\n", val ? "PASS" : "FAIL", key)
        val || (all_pass = false)
    end

    # Choptyuk formula
    println("\n[4] Choptyuk Formula")
    cf = ChoptyukFormula()
    cv = verify_choptyuk_formula(cf)
    for (key, val) in sort(collect(pairs(cv)))
        if isa(val, Bool)
            @printf("    [%s] %s\n", val ? "PASS" : "FAIL", key)
            val || (all_pass = false)
        else
            @printf("    %s = %.6f\n", key, Float64(val))
        end
    end

    # QNM
    println("\n[5] QNM Predictions")
    qv = verify_qnm()
    for (key, val) in sort(collect(pairs(qv)))
        @printf("    [%s] %s\n", val ? "PASS" : "FAIL", key)
        val || (all_pass = false)
    end

    # Surfaces
    println("\n[6] Reference Surfaces")
    for S in ALL_SURFACES
        sv = verify_surface(S)
        n_pass = count(values(sv))
        n_total = length(sv)
        all_ok = n_pass == n_total
        @printf("    [%s] %s: %d/%d checks passed\n",
                all_ok ? "PASS" : "FAIL", S.name, n_pass, n_total)
        all_ok || (all_pass = false)
    end

    println("\n" * "=" ^ 70)
    @printf("  OVERALL: %s\n", all_pass ? "ALL CHECKS PASSED" : "SOME CHECKS FAILED")
    println("=" ^ 70)

    # Key numerical values
    println("\nKey Values:")
    @printf("  Δ_Ch (Choptyuk constant) = %.6f\n", choptyuk_constant())
    @printf("  Δ_bC (b-C correction)    = %.6f\n", bC_correction())
    @printf("  Δ_aC (a-C correction)    = %.6f\n", aC_correction())
    @printf("  δ_eff (a-C braking)      = %.6f\n", aC_braking())
    @printf("  b_Ch = 1 - cos(2π/7)    = %.6f\n", cf.b_Ch)
    @printf("  Δ_obs (observed)         = 3.443000\n")
    @printf("  Deviation (Δ_Ch - Δ_obs) = %.6f\n", choptyuk_constant() - 3.443)
end

"""
    main()

Main entry point.
"""
function main()
    args = parse_args(ARGS)

    if args[:help]
        print_help()
        return
    end

    output_dir = args[:output_dir]
    mkpath(output_dir)

    mode = args[:mode]

    if mode == :interactive
        InteractiveMenu.run_interactive(; output_dir = output_dir)
    elseif mode == :noninteractive
        run_non_interactive(output_dir)
    elseif mode == :verify
        run_verify_only(output_dir)
    end
end

# Run main
main()
