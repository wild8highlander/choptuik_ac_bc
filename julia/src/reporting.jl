"""
    Reporting module for the Choptyuk spinor monograph.

Generates reports in TXT, MD, CSV, HTML, and JSON formats.
Results are presented first, followed by execution logs.
"""
module Reporting

using ..ChoptyukSpinor
using Printf
using JSON

"""
    format_number(x::Float64; digits::Int=6) -> String

Format a number for display in reports.
"""
function format_number(x::Float64; digits::Int = 6)
    return @sprintf("%.*f", digits, x)
end

"""
    generate_txt_report(sim_results::Dict, sim_log::Vector{String};
                        filepath::String="output/report.txt")

Generate a plain text report.
"""
function generate_txt_report(sim_results::Dict, sim_log::Vector{String};
                             filepath::String = "output/report.txt")
    mkpath(dirname(filepath))

    io = IOBuffer()

    println(io, "=" ^ 80)
    println(io, "CHOPTYUK SPINOR MONOGRAPH - VERIFICATION REPORT")
    println(io, "=" ^ 80)
    println(io, "Generated: $(Dates.format(Dates.now(), "yyyy-mm-dd HH:MM:SS"))")
    println(io)

    # Results section
    println(io, "-" ^ 80)
    println(io, "SECTION 1: RESULTS")
    println(io, "-" ^ 80)
    println(io)

    # Klein curve verification
    if haskey(sim_results, "klein_verification")
        println(io, "Klein Curve Verification:")
        for (key, val) in sort(collect(pairs(sim_results["klein_verification"])))
            status = val ? "PASS" : "FAIL"
            println(io, "  [$status] $key")
        end
        println(io)
    end

    # Phase verification
    if haskey(sim_results, "phase_verification")
        println(io, "Spinor Phase Verification:")
        for (key, val) in sort(collect(pairs(sim_results["phase_verification"])))
            status = val ? "PASS" : "FAIL"
            println(io, "  [$status] $key")
        end
        println(io)
    end

    # Dirac verification
    if haskey(sim_results, "dirac_verification")
        println(io, "Dirac Operator Verification:")
        for (key, val) in sort(collect(pairs(sim_results["dirac_verification"])))
            status = val ? "PASS" : "FAIL"
            println(io, "  [$status] $key")
        end
        println(io)
    end

    # Choptyuk formula verification
    if haskey(sim_results, "choptyuk_verification")
        println(io, "Choptyuk Formula Verification:")
        for (key, val) in sort(collect(pairs(sim_results["choptyuk_verification"])))
            if isa(val, Bool)
                status = val ? "PASS" : "FAIL"
                println(io, "  [$status] $key")
            else
                println(io, "  $key = $(format_number(Float64(val)))")
            end
        end
        println(io)
    end

    # Hypothesis result
    if haskey(sim_results, "hypothesis")
        hyp = sim_results["hypothesis"]
        println(io, "Hypothesis Test:")
        println(io, "  Δ_Ch = $(format_number(hyp.delta_ch))")
        println(io, "  Δ_obs = $(format_number(hyp.delta_obs))")
        println(io, "  Deviation = $(format_number(hyp.deviation))")
        println(io, "  Relative deviation = $(format_number(hyp.relative_deviation))")
        status = hyp.accepted ? "ACCEPTED" : "REJECTED"
        println(io, "  Hypothesis: $status (tolerance = $(format_number(hyp.tolerance)))")
        println(io)
    end

    # Convergence
    if haskey(sim_results, "convergence")
        conv = sim_results["convergence"]
        println(io, "Convergence Analysis:")
        println(io, "  Limit estimate = $(format_number(conv["limit_estimate"]))")
        println(io, "  Final value = $(format_number(Float64(conv["final_value"])))")
        println(io, "  Deviation at limit = $(format_number(conv["deviation_at_limit"]))")
        println(io)
    end

    # QNM
    if haskey(sim_results, "qnm_detectability")
        qnm = sim_results["qnm_detectability"]
        println(io, "QNM Detectability:")
        if haskey(qnm, "Predicted relative shift")
            println(io, "  Predicted relative shift = $(format_number(Float64(qnm["Predicted relative shift"])))")
        end
        if haskey(qnm, "Detectable by LIGO")
            det = qnm["Detectable by LIGO"] ? "YES" : "NO"
            println(io, "  Detectable by LIGO: $det")
        end
        if haskey(qnm, "Estimated SNR")
            println(io, "  Estimated SNR = $(format_number(Float64(qnm["Estimated SNR"])))")
        end
        println(io)
    end

    # Execution log
    println(io, "-" ^ 80)
    println(io, "SECTION 2: EXECUTION LOG")
    println(io, "-" ^ 80)
    println(io)
    for entry in sim_log
        println(io, "  $entry")
    end
    println(io)
    println(io, "=" ^ 80)
    println(io, "END OF REPORT")
    println(io, "=" ^ 80)

    content = String(take!(io))
    write(filepath, content)
    @info "TXT report saved: $filepath"
    return content
end

"""
    generate_md_report(sim_results::Dict, sim_log::Vector{String};
                       filepath::String="output/report.md")

Generate a Markdown report.
"""
function generate_md_report(sim_results::Dict, sim_log::Vector{String};
                            filepath::String = "output/report.md")
    mkpath(dirname(filepath))

    io = IOBuffer()

    println(io, "# Choptyuk Spinor Monograph — Verification Report")
    println(io)
    println(io, "_Generated: $(Dates.format(Dates.now(), "yyyy-mm-dd HH:MM:SS"))_")
    println(io)

    # Results section
    println(io, "## Results")
    println(io)

    # Klein curve
    if haskey(sim_results, "klein_verification")
        println(io, "### Klein Curve Verification")
        println(io)
        println(io, "| Check | Status |")
        println(io, "|-------|--------|")
        for (key, val) in sort(collect(pairs(sim_results["klein_verification"])))
            status = val ? "✅ PASS" : "❌ FAIL"
            println(io, "| $key | $status |")
        end
        println(io)
    end

    # Phase verification
    if haskey(sim_results, "phase_verification")
        println(io, "### Spinor Phase Verification")
        println(io)
        println(io, "| Check | Status |")
        println(io, "|-------|--------|")
        for (key, val) in sort(collect(pairs(sim_results["phase_verification"])))
            status = val ? "✅ PASS" : "❌ FAIL"
            println(io, "| $key | $status |")
        end
        println(io)
    end

    # Dirac verification
    if haskey(sim_results, "dirac_verification")
        println(io, "### Dirac Operator Verification")
        println(io)
        println(io, "| Check | Status |")
        println(io, "|-------|--------|")
        for (key, val) in sort(collect(pairs(sim_results["dirac_verification"])))
            status = val ? "✅ PASS" : "❌ FAIL"
            println(io, "| $key | $status |")
        end
        println(io)
    end

    # Choptyuk formula
    if haskey(sim_results, "choptyuk_verification")
        println(io, "### Choptyuk Formula")
        println(io)
        println(io, "| Parameter | Value |")
        println(io, "|-----------|-------|")
        for (key, val) in sort(collect(pairs(sim_results["choptyuk_verification"])))
            if isa(val, Bool)
                status = val ? "✅ PASS" : "❌ FAIL"
                println(io, "| $key | $status |")
            else
                println(io, "| $key | $(format_number(Float64(val))) |")
            end
        end
        println(io)
    end

    # Hypothesis
    if haskey(sim_results, "hypothesis")
        hyp = sim_results["hypothesis"]
        println(io, "### Hypothesis Test")
        println(io)
        println(io, "- **Δ_Ch** = $(format_number(hyp.delta_ch))")
        println(io, "- **Δ_obs** = $(format_number(hyp.delta_obs))")
        println(io, "- **Deviation** = $(format_number(hyp.deviation))")
        println(io, "- **Relative deviation** = $(format_number(hyp.relative_deviation))")
        status = hyp.accepted ? "✅ ACCEPTED" : "❌ REJECTED"
        println(io, "- **Hypothesis**: $status (tolerance = $(format_number(hyp.tolerance)))")
        println(io)
    end

    # Execution log
    println(io, "## Execution Log")
    println(io)
    for entry in sim_log
        println(io, "- `$entry`")
    end
    println(io)

    content = String(take!(io))
    write(filepath, content)
    @info "MD report saved: $filepath"
    return content
end

"""
    generate_csv_report(sim_results::Dict; filepath::String="output/report.csv")

Generate a CSV report with key numerical results.
"""
function generate_csv_report(sim_results::Dict; filepath::String = "output/report.csv")
    mkpath(dirname(filepath))

    io = IOBuffer()

    # Header
    println(io, "category,parameter,value")

    # Klein curve
    if haskey(sim_results, "klein_verification")
        for (key, val) in sim_results["klein_verification"]
            println(io, "klein_curve,$key,$val")
        end
    end

    # Phases
    if haskey(sim_results, "phase_verification")
        for (key, val) in sim_results["phase_verification"]
            println(io, "spinor_phases,$key,$val")
        end
    end

    # Dirac
    if haskey(sim_results, "dirac_verification")
        for (key, val) in sim_results["dirac_verification"]
            println(io, "dirac_operator,$key,$val")
        end
    end

    # Choptyuk formula
    if haskey(sim_results, "choptyuk_verification")
        for (key, val) in sim_results["choptyuk_verification"]
            println(io, "choptyuk_formula,$key,$val")
        end
    end

    # Hypothesis
    if haskey(sim_results, "hypothesis")
        hyp = sim_results["hypothesis"]
        println(io, "hypothesis,delta_ch,$(hyp.delta_ch)")
        println(io, "hypothesis,delta_obs,$(hyp.delta_obs)")
        println(io, "hypothesis,deviation,$(hyp.deviation)")
        println(io, "hypothesis,relative_deviation,$(hyp.relative_deviation)")
        println(io, "hypothesis,accepted,$(hyp.accepted)")
    end

    # Convergence
    if haskey(sim_results, "convergence")
        conv = sim_results["convergence"]
        println(io, "convergence,limit_estimate,$(conv["limit_estimate"])")
        println(io, "convergence,deviation_at_limit,$(conv["deviation_at_limit"])")
    end

    content = String(take!(io))
    write(filepath, content)
    @info "CSV report saved: $filepath"
    return content
end

"""
    generate_html_report(sim_results::Dict, sim_log::Vector{String};
                         filepath::String="output/report.html")

Generate an HTML report.
"""
function generate_html_report(sim_results::Dict, sim_log::Vector{String};
                              filepath::String = "output/report.html")
    mkpath(dirname(filepath))

    io = IOBuffer()

    println(io, """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Choptyuk Spinor Monograph - Verification Report</title>
<style>
body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
h2 { color: #2980b9; margin-top: 30px; }
h3 { color: #27ae60; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; background: white; }
th, td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
th { background: #3498db; color: white; }
tr:nth-child(even) { background: #f2f2f2; }
.pass { color: #27ae60; font-weight: bold; }
.fail { color: #e74c3c; font-weight: bold; }
.log { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 12px; overflow-x: auto; }
.log-entry { margin: 2px 0; }
.section { background: white; padding: 15px; border-radius: 5px; margin: 10px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
</style>
</head>
<body>
<h1>Choptyuk Spinor Monograph &mdash; Verification Report</h1>
<p><em>Generated: $(Dates.format(Dates.now(), "yyyy-mm-dd HH:MM:SS"))</em></p>
""")

    # Results
    println(io, "<h2>Results</h2>")

    # Helper to render verification table
    function render_verif(io, title, data)
        println(io, """<div class="section"><h3>$title</h3>
<table><tr><th>Check</th><th>Status</th></tr>""")
        for (key, val) in sort(collect(pairs(data)))
            cls = val ? "pass" : "fail"
            status = val ? "PASS" : "FAIL"
            println(io, "<tr><td>$key</td><td class=\"$cls\">$status</td></tr>")
        end
        println(io, "</table></div>")
    end

    haskey(sim_results, "klein_verification") && render_verif(io, "Klein Curve", sim_results["klein_verification"])
    haskey(sim_results, "phase_verification") && render_verif(io, "Spinor Phases", sim_results["phase_verification"])
    haskey(sim_results, "dirac_verification") && render_verif(io, "Dirac Operator", sim_results["dirac_verification"])

    # Choptyuk formula (mixed types)
    if haskey(sim_results, "choptyuk_verification")
        println(io, """<div class="section"><h3>Choptyuk Formula</h3>
<table><tr><th>Parameter</th><th>Value</th></tr>""")
        for (key, val) in sort(collect(pairs(sim_results["choptyuk_verification"])))
            if isa(val, Bool)
                cls = val ? "pass" : "fail"
                status = val ? "PASS" : "FAIL"
                println(io, "<tr><td>$key</td><td class=\"$cls\">$status</td></tr>")
            else
                println(io, "<tr><td>$key</td><td>$(format_number(Float64(val)))</td></tr>")
            end
        end
        println(io, "</table></div>")
    end

    # Hypothesis
    if haskey(sim_results, "hypothesis")
        hyp = sim_results["hypothesis"]
        cls = hyp.accepted ? "pass" : "fail"
        status = hyp.accepted ? "ACCEPTED" : "REJECTED"
        println(io, """<div class="section"><h3>Hypothesis Test</h3>
<table>
<tr><td><strong>Δ_Ch</strong></td><td>$(format_number(hyp.delta_ch))</td></tr>
<tr><td><strong>Δ_obs</strong></td><td>$(format_number(hyp.delta_obs))</td></tr>
<tr><td><strong>Deviation</strong></td><td>$(format_number(hyp.deviation))</td></tr>
<tr><td><strong>Relative deviation</strong></td><td>$(format_number(hyp.relative_deviation))</td></tr>
<tr><td><strong>Hypothesis</strong></td><td class="$cls">$status (tolerance = $(format_number(hyp.tolerance)))</td></tr>
</table></div>""")
    end

    # Execution log
    println(io, "<h2>Execution Log</h2>")
    println(io, "<div class=\"log\">")
    for entry in sim_log
        println(io, "<div class=\"log-entry\">$(entry)</div>")
    end
    println(io, "</div>")

    println(io, "</body></html>")

    content = String(take!(io))
    write(filepath, content)
    @info "HTML report saved: $filepath"
    return content
end

"""
    generate_json_report(sim_results::Dict, sim_log::Vector{String};
                         filepath::String="output/report.json")

Generate a JSON report.
"""
function generate_json_report(sim_results::Dict, sim_log::Vector{String};
                              filepath::String = "output/report.json")
    mkpath(dirname(filepath))

    # Convert HypothesisResult to a serializable dict
    serializable = Dict{String, Any}()
    for (key, val) in sim_results
        if isa(val, HypothesisResult)
            serializable[key] = Dict(
                "delta_ch" => val.delta_ch,
                "delta_obs" => val.delta_obs,
                "deviation" => val.deviation,
                "relative_deviation" => val.relative_deviation,
                "accepted" => val.accepted,
                "tolerance" => val.tolerance,
                "details" => val.details,
            )
        else
            serializable[key] = val
        end
    end

    report = Dict(
        "timestamp" => Dates.format(Dates.now(), "yyyy-mm-dd HH:MM:SS"),
        "results" => serializable,
        "execution_log" => sim_log,
    )

    content = JSON.json(report, 4)
    write(filepath, content)
    @info "JSON report saved: $filepath"
    return content
end

"""
    generate_all_reports(sim_results::Dict, sim_log::Vector{String};
                         dir::String="output")

Generate reports in all supported formats.
"""
function generate_all_reports(sim_results::Dict, sim_log::Vector{String};
                              dir::String = "output")
    mkpath(dir)
    @info "Generating all reports in $dir"

    generate_txt_report(sim_results, sim_log; filepath = joinpath(dir, "report.txt"))
    generate_md_report(sim_results, sim_log; filepath = joinpath(dir, "report.md"))
    generate_csv_report(sim_results; filepath = joinpath(dir, "report.csv"))
    generate_html_report(sim_results, sim_log; filepath = joinpath(dir, "report.html"))
    generate_json_report(sim_results, sim_log; filepath = joinpath(dir, "report.json"))

    @info "All reports generated"
end

end # module Reporting
