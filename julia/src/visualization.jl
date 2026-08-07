"""
    Visualization module for the Choptyuk spinor monograph.

Generates publication-quality plots at 600 DPI in PNG, PDF, and SVG formats.
Each plot is saved as a separate file.
"""
module Visualization

using ..ChoptyukSpinor
using Plots
using Printf

const DEFAULT_DPI = 600
const DEFAULT_FORMATS = (:png, :pdf, :svg)

"""
    output_path(name::String, fmt::Symbol, dir::String="output") -> String

Generate output file path for a plot.
"""
function output_path(name::String, fmt::Symbol, dir::String = "output")
    ext = string(fmt)
    return joinpath(dir, "$(name).$(ext)")
end

"""
    save_plot(p, name::String; dir::String="output", dpi::Int=DEFAULT_DPI,
              formats::Tuple=DEFAULT_FORMATS)

Save a plot in multiple formats at the specified DPI.
"""
function save_plot(p, name::String; dir::String = "output", dpi::Int = DEFAULT_DPI,
                   formats::Tuple = DEFAULT_FORMATS)
    mkpath(dir)
    for fmt in formats
        filepath = output_path(name, fmt, dir)
        try
            savefig(p, filepath)
            @info "Saved plot: $filepath"
        catch e
            @warn "Failed to save plot $filepath: $e"
        end
    end
end

"""
    plot_spinor_phases(phases::SpinorPhases=SpinorPhases();
                       dir::String="output") -> Plot

Plot the three spinor phases on the unit circle.
"""
function plot_spinor_phases(phases::SpinorPhases = SpinorPhases(); dir::String = "output")
    θ = range(0, 2π; length = 200)

    p = plot(; aspect_ratio = :equal, size = (800, 800),
             title = "Spinor Phases on the Klein Curve",
             xlabel = "Re", ylabel = "Im",
             legend = :topright,
             framestyle = :zerolines,
             grid = true,
             dpi = DEFAULT_DPI)

    # Unit circle
    plot!(p, cos.(θ), sin.(θ); label = "S¹", lw = 1, color = :gray, ls = :dash)

    # Phase points
    phase_data = [
        (phases.delta_A, "δ_A = π/2", :red),
        (phases.delta_B, "δ_B = π/3", :blue),
        (phases.delta_C, "δ_C = π/7", :green),
    ]

    for (δ, label, color) in phase_data
        x, y = cos(δ), sin(δ)
        scatter!(p, [x], [y]; label = label, ms = 10, color = color, markershape = :circle)
        plot!(p, [0, x], [0, y]; lw = 2, color = color, ls = :solid, label = "")
    end

    save_plot(p, "spinor_phases"; dir = dir)
    return p
end

"""
    plot_eigenvalue_landscape(sim_results::Dict; dir::String="output") -> Plot

Plot the eigenvalue landscape as a function of δ_C.
"""
function plot_eigenvalue_landscape(sim_results::Dict; dir::String = "output")
    if !haskey(sim_results, "sweep_delta_C")
        @warn "No δ_C sweep data found"
        return nothing
    end

    data = sim_results["sweep_delta_C"]
    dc = data["delta_C"]

    p = plot(; size = (1000, 600),
             title = "Choptyuk Formula: Eigenvalue Landscape",
             xlabel = "δ_C",
             ylabel = "Δ",
             legend = :topleft,
             dpi = DEFAULT_DPI)

    plot!(p, dc, data["order_2"]; label = "Order 2 (b-C)", lw = 2, color = :red)
    plot!(p, dc, data["order_4"]; label = "Order 4", lw = 2, color = :orange)
    plot!(p, dc, data["order_5"]; label = "Order 5 (a-C)", lw = 2, color = :purple)
    plot!(p, dc, data["order_6"]; label = "Order 6 (full)", lw = 3, color = :blue)

    # Mark observed value
    hline!(p, [3.443]; label = "Δ_obs = 3.443", lw = 2, color = :black, ls = :dash)

    # Mark δ_C = π/7
    vline!(p, [π / 7]; label = "δ_C = π/7", lw = 1, color = :gray, ls = :dot)

    save_plot(p, "eigenvalue_landscape"; dir = dir)
    return p
end

"""
    plot_structure_heatmap(phases::SpinorPhases=SpinorPhases();
                           dir::String="output") -> Plot

Plot a heatmap of the 64 spinor structures grouped by phase signature.
"""
function plot_structure_heatmap(phases::SpinorPhases = SpinorPhases(); dir::String = "output")
    structures = enumerate_64_structures(phases)

    # Create an 8×8 matrix of phase signatures
    heatmap_data = Matrix{Float64}(undef, 8, 8)
    for (idx, s) in enumerate(sort(structures; by = x -> x.index))
        row = (idx - 1) ÷ 8 + 1
        col = (idx - 1) % 8 + 1
        heatmap_data[row, col] = s.phase_signature
    end

    p = heatmap(heatmap_data;
                title = "64 Spinor Structures: Phase Signature Heatmap",
                xlabel = "Structure index (mod 8)",
                ylabel = "Structure index (÷ 8)",
                color = :RdBu,
                size = (800, 700),
                dpi = DEFAULT_DPI,
                clims = (-maximum(abs.(heatmap_data)), maximum(abs.(heatmap_data))))

    save_plot(p, "structure_heatmap"; dir = dir)
    return p
end

"""
    plot_qnm_comparison(pred::QNMPredictor=QNMPredictor();
                        dir::String="output") -> Plot

Plot QNM predictions compared to LIGO observations.
"""
function plot_qnm_comparison(pred::QNMPredictor = QNMPredictor(); dir::String = "output")
    events = LIGO_EVENTS
    names = [e.name for e in events]
    masses = [e.mass for e in events]
    spins = [e.spin for e in events]
    freqs = [e.freq for e in events]

    # Compute predicted shifts
    shifts = Float64[]
    for event in events
        result = predict_shift(pred, event)
        push!(shifts, result["Predicted freq shift (Hz)"])
    end

    p1 = bar(names, freqs;
             title = "QNM Frequencies (Hz)",
             ylabel = "Frequency (Hz)",
             color = :steelblue,
             legend = false,
             size = (800, 400),
             dpi = DEFAULT_DPI)

    p2 = bar(names, shifts;
             title = "Predicted Spinor Shift (Hz)",
             ylabel = "Frequency shift (Hz)",
             color = :coral,
             legend = false,
             size = (800, 400),
             dpi = DEFAULT_DPI)

    p3 = scatter(masses, spins;
                 title = "Black Hole Parameters",
                 xlabel = "Mass (M☉)",
                 ylabel = "Spin a/M",
                 label = "",
                 ms = 8,
                 color = :darkgreen,
                 size = (800, 400),
                 dpi = DEFAULT_DPI)

    for (i, name) in enumerate(names)
        annotate!(p3, [(masses[i], spins[i] + 0.02, text(name, 8)))])
    end

    p = plot(p1, p2, p3; layout = (3, 1), size = (800, 1200))

    save_plot(p, "qnm_comparison"; dir = dir)
    return p
end

"""
    plot_deviation_analysis(sim_results::Dict; dir::String="output") -> Plot

Plot the deviation from observation as a function of δ_C.
"""
function plot_deviation_analysis(sim_results::Dict; dir::String = "output")
    if !haskey(sim_results, "sweep_delta_C")
        @warn "No δ_C sweep data found"
        return nothing
    end

    data = sim_results["sweep_delta_C"]
    dc = data["delta_C"]
    dev = data["deviation"]

    p = plot(; size = (1000, 600),
             title = "Deviation from Observed Δ = 3.443",
             xlabel = "δ_C",
             ylabel = "Δ_Ch - Δ_obs",
             legend = :topright,
             dpi = DEFAULT_DPI)

    plot!(p, dc, dev; label = "Δ_Ch - Δ_obs", lw = 2, color = :blue)
    hline!(p, [0.0]; label = "Zero deviation", lw = 1, color = :black, ls = :dash)
    vline!(p, [π / 7]; label = "δ_C = π/7", lw = 1, color = :red, ls = :dot)

    save_plot(p, "deviation_analysis"; dir = dir)
    return p
end

"""
    plot_convergence(sim_results::Dict; dir::String="output") -> Plot

Plot the convergence of the Choptyuk formula partial sums.
"""
function plot_convergence(sim_results::Dict; dir::String = "output")
    if !haskey(sim_results, "convergence")
        @warn "No convergence data found"
        return nothing
    end

    conv = sim_results["convergence"]
    partial = conv["partial_sums"]
    terms = conv["terms"]
    rates = conv["convergence_rates"]
    observed = conv["observed_delta"]

    # Partial sums
    orders = collect(0:(length(partial) - 1))
    p1 = scatter(orders, partial;
                 title = "Partial Sums Convergence",
                 xlabel = "Order",
                 ylabel = "Δ",
                 label = "Partial sums",
                 ms = 6,
                 color = :blue,
                 size = (800, 400),
                 dpi = DEFAULT_DPI)
    hline!(p1, [observed]; label = "Δ_obs = $(round(observed; digits=3))",
           lw = 2, color = :red, ls = :dash)

    # Term magnitudes
    p2 = bar(orders[1:length(terms)], abs.(terms);
             title = "Term Magnitudes |tₖ|",
             xlabel = "Order",
             ylabel = "|tₖ|",
             label = "",
             color = :steelblue,
             yscale = :log10,
             size = (800, 400),
             dpi = DEFAULT_DPI)

    # Convergence rates
    rate_orders = collect(1:length(rates))
    p3 = scatter(rate_orders, rates;
                 title = "Convergence Rates |tₖ/tₖ₋₁|",
                 xlabel = "Order",
                 ylabel = "Rate",
                 label = "",
                 ms = 6,
                 color = :darkgreen,
                 size = (800, 400),
                 dpi = DEFAULT_DPI)
    hline!(p3, [1.0]; label = "Rate = 1", lw = 1, color = :black, ls = :dash)

    p = plot(p1, p2, p3; layout = (3, 1), size = (800, 1200))

    save_plot(p, "convergence"; dir = dir)
    return p
end

"""
    plot_surface_comparison(dir::String="output") -> Plot

Compare the Choptyuk formula across reference surfaces.
"""
function plot_surface_comparison(dir::String = "output")
    surfaces = ALL_SURFACES
    names = [S.name for S in surfaces]
    genera = [S.genus for S in surfaces]
    aut_orders = [Float64(S.aut_order) for S in surfaces]
    delta_ch_vals = [surface_choptyuk(S) for S in surfaces]
    delta_C_vals = [S.delta_C for S in surfaces]
    bCh_vals = [1 - cos(2 * S.delta_C) for S in surfaces]

    p1 = bar(names, delta_ch_vals;
             title = "Choptyuk Constant Δ_Ch by Surface",
             ylabel = "Δ_Ch",
             color = :steelblue,
             legend = false,
             size = (800, 400),
             dpi = DEFAULT_DPI)
    hline!(p1, [3.443]; lw = 2, color = :red, ls = :dash, label = "Δ_obs")

    p2 = bar(names, delta_C_vals;
             title = "Fundamental Phase δ_C by Surface",
             ylabel = "δ_C",
             color = :coral,
             legend = false,
             size = (800, 400),
             dpi = DEFAULT_DPI)

    p3 = bar(names, bCh_vals;
             title = "b_Ch = 1 - cos(2δ_C) by Surface",
             ylabel = "b_Ch",
             color = :seagreen,
             legend = false,
             size = (800, 400),
             dpi = DEFAULT_DPI)

    p4 = scatter(genera, aut_orders;
                 title = "Automorphism Group Orders",
                 xlabel = "Genus",
                 ylabel = "|Aut|",
                 label = "",
                 ms = 10,
                 color = :purple,
                 size = (800, 400),
                 dpi = DEFAULT_DPI)
    # Hurwitz bound
    g_range = collect(2:maximum(genera))
    hurwitz_bounds = [84 * (g - 1) for g in g_range]
    plot!(p4, g_range, hurwitz_bounds; label = "84(g-1)", lw = 2, color = :red, ls = :dash)

    p = plot(p1, p2, p3, p4; layout = (2, 2), size = (1200, 1000))

    save_plot(p, "surface_comparison"; dir = dir)
    return p
end

"""
    generate_all_plots(sim_results::Dict; dir::String="output")

Generate all visualization plots.
"""
function generate_all_plots(sim_results::Dict; dir::String = "output")
    mkpath(dir)
    @info "Generating all plots in $dir"

    plot_spinor_phases(; dir = dir)
    plot_eigenvalue_landscape(sim_results; dir = dir)
    plot_structure_heatmap(; dir = dir)
    plot_qnm_comparison(; dir = dir)
    plot_deviation_analysis(sim_results; dir = dir)
    plot_convergence(sim_results; dir = dir)
    plot_surface_comparison(; dir = dir)

    @info "All plots generated"
end

end # module Visualization
