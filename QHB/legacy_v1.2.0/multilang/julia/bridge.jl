# bridge.jl — the Quark-Hawking Bridge twin (Julia, self-test).
# Run: julia bridge.jl   (source twin; verified where a toolchain exists)

const G = 6.67430e-11
const c = 299792458.0
const h = 6.62607015e-34
const ħ = h / (2π)
const kB = 1.380649e-23
const MeV_J = 1.602176634e-13
const T_CMB = 2.72548
const T_QCD = 155.16 * MeV_J / kB

residual(α, x) = begin
    f(u) = u < 1e-300 ? x : -expm1(-x * u) / u
    fp, fm = f(1 - α), f(1 + α)
    (fp - fm) / (fp + fm)
end

b_Ch = 1 - cos(2π / 7)
PAGE = 1 - 2.0^(-1.5)
M_QCD = ħ * c^3 / (8π * G * kB * T_QCD)
M_CMB = ħ * c^3 / (8π * G * kB * T_CMB)
TH12 = ħ * c^3 / (8π * G * 1e12 * kB)
growth = sqrt(1.5)
Δ0, B2 = 0.523004556028, -5.49670294e-2
GAPQ = Δ0 + B2 * 0.2^2

rows = [
    ("delta_C = pi/7",        π / 7,       0.44879895051282761),
    ("b_Ch = 1-cos(2pi/7)",   b_Ch,        0.37651019814126640),
    ("Page fraction",         PAGE,        0.64644660940672620),
    ("M_QCD [kg]",            M_QCD,       6.814006e10),
    ("M_CMB [kg]",            M_CMB,       4.501595e22),
    ("T_H(1e12 kg) [K]",      TH12,        1.226901e11),
    ("r_Wu(0.9, 100)",        residual(0.9, 100.0), 0.899995686821),
    ("Gascheau growth",       growth,      1.22474487139158905),
    ("gap law Δ_F(0.2)",      GAPQ,        0.520805874852),
]
pass = 0
for (name, val, ref) in rows
    rel = abs(val - ref) / abs(ref)
    ok = rel < 1e-6
    global pass += ok ? 1 : 0
    println(@sprintf("%-24s = %-20.12g %s (rel %.2e)",
                     name, val, ok ? "PASS" : "FAIL", rel))
end
println("$pass/$(length(rows)) checks PASS (qhb twin, Julia)")
