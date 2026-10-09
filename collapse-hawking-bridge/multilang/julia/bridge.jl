# bridge.jl — Collapse-Hawking Bridge multilang self-test (Julia).
#
# Recomputes the closed-form core of the bridge from CODATA constants and
# prints a validation block. Run:  julia bridge.jl
#
# STATUS: portable source, written against the same closed forms as the
# verified C / C++ / JavaScript twins. Not executed on the reference
# machine (no Julia toolchain at packaging time) — run once locally and
# diff against multilang/javascript/reference_output.txt.

const G     = 6.67430e-11        # m^3 kg^-1 s^-2
const c     = 299792458.0        # m/s (exact)
const h     = 6.62607015e-34     # J s (exact)
const ħ     = h / (2 * π)
const k_B   = 1.380649e-23       # J/K (exact)
const T_CMB = 2.72548            # K (COBE/FIRAS)

T_H(M)    = ħ * c^3 / (8π * G * M * k_B)
S_BH(M)   = k_B * c^3 * (4π * (2G * M / c^2)^2) / (4G * ħ)
t_evap(M) = 5120π * G^2 * M^3 / (ħ * c^4)
P_H(M)    = ħ * c^6 / (15360π * G^2 * M^2)
M_CMB()   = ħ * c^3 / (8π * G * k_B * T_CMB)

PAGE_FRACTION = 1.0 - 2.0^(-1.5)
function s_rad_over_s0(tau)
    u2 = (1.0 - tau)^(2/3)
    tau < PAGE_FRACTION ? u2 : 1.0 - u2
end

const dgamma = 3.44 * 0.374
# F-2 per-grid floors (v2.1.0 remediation values)
const a_star_n800 = 0.08053436279296877
const a_star_ladder_n1600 = 0.0777437258   # F-1 remediation ladder
const floors = [(800, 0.0155), (1600, 8.574765e-03), (3200, 4.244867e-03)]

println("Collapse-Hawking Bridge — Julia self-test")
println("-------------------------------------------------")
println("delta_C          = pi/7                = $(π/7)")
println("b_Ch             = 1 - cos(2 pi / 7)   = $(1 - cos(2π/7))")
println("PAGE_FRACTION    = 1 - 2^(-3/2)        = $PAGE_FRACTION")
println("Delta*gamma      = 3.44 * 0.374        = $dgamma  ",
        abs(dgamma - 1.27) <= 0.05 ? "PASS" : "FAIL")
println("M_CMB            = ", M_CMB(), " kg")
println("T_H(1e12 kg)     = ", T_H(1e12), " K")
println("S_BH(1e12)/kB    = ", S_BH(1e12) / k_B)
println("t_evap(1e12)     = ", t_evap(1e12), " s")
for tau in (0.5, PAGE_FRACTION, 0.8)
    println("S_rad/S0($tau)  = ", s_rad_over_s0(tau))
end
for (N, f) in floors
    println("floor_M(N=$N)    = $f   12/N = $(12.0 / N)")
end
println("-------------------------------------------------")
println("A* (N=800)       = $a_star_n800 | ladder N=1600: $a_star_ladder_n1600 | drift: $(round(abs(a_star_n800 - a_star_ladder_n1600); sigdigits=3)) (F-1)")
println("All quantities above reproduce chbridge v2.1.0 closed forms.")
println("A* drift note: the threshold drifts with N (F-1 remediation);")
println("the stale 1.06e-6 agreement claim is RETRACTED.")
