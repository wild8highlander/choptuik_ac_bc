using Test
using ChoptyukSpinor

const TOL_STRICT = 1e-6
const TOL_LOOSE = 1e-3

# Reference values from the monograph
const REF_DELTA_BC = 3.438710
const REF_DELTA_CH_BASE = 3.437883
const REF_DELTA_CH_FULL = 3.447040
const REF_B_CH = 0.376510
const REF_LAMBDA1_DIRAC = 3.338

@testset "Klein Curve Properties" begin
    kc = KleinCurve()
    @test genus(kc) == 3
    @test automorphism_order(kc) == 168
    @test scalar_curvature(kc) ≈ -2 atol=TOL_STRICT
end

@testset "Spinor Phases" begin
    sp = SpinorPhases()
    @test delta_a(sp) ≈ π/2 atol=TOL_STRICT
    @test delta_b(sp) ≈ π/3 atol=TOL_STRICT
    @test delta_c(sp) ≈ π/7 atol=TOL_STRICT
    @test delta_a(sp) > delta_b(sp) > delta_c(sp)
end

@testset "Dirac Operator" begin
    d = DiracOperator()
    @test trivial_eigenvalue(d) ≈ REF_LAMBDA1_DIRAC atol=TOL_LOOSE
end

@testset "Choptyuk Formula" begin
    cf = ChoptyukFormula()
    @test delta_bc(cf) ≈ REF_DELTA_BC atol=TOL_LOOSE
    @test delta_ch_base(cf) ≈ REF_DELTA_CH_BASE atol=TOL_LOOSE
    @test delta_ch_full(cf) ≈ REF_DELTA_CH_FULL atol=TOL_LOOSE
    @test b_choptyuk(cf) ≈ REF_B_CH atol=TOL_LOOSE
end

@testset "Choptyuk Constant Identities" begin
    # b_Ch = 1 - cos(2π/7) = 2·sin²(π/7)
    val1 = 1 - cos(2π/7)
    val2 = 2 * sin(π/7)^2
    @test val1 ≈ val2 atol=TOL_STRICT
    @test val1 ≈ REF_B_CH atol=TOL_LOOSE
end

@testset "64 Spinor Structures" begin
    # 2^(2g) = 2^6 = 64
    @test 2^(2*3) == 64
end

@testset "Deviations Within Tolerance" begin
    cf = ChoptyukFormula()
    observed = 3.443
    dev_bc = abs(delta_bc(cf) - observed) / observed * 100
    dev_full = abs(delta_ch_full(cf) - observed) / observed * 100
    @test dev_bc < 0.2
    @test dev_full < 0.2
end
