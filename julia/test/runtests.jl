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

@testset "Imaginary Correction" begin
    delta_C = π / 7
    ic = imaginary_correction(delta_C)
    @test ic ≈ 1 - delta_C / π^2 atol=TOL_STRICT
    @test 0.95 < ic < 1.0  # Should be close to 1
end

@testset "Kähler Correction" begin
    delta_C = π / 7
    kc = kahler_correction(delta_C)
    @test kc ≈ delta_C^2 / 2 - delta_C^5 / 22 atol=TOL_STRICT
    # Should be positive since δ_C²/2 dominates δ_C⁵/22
    @test kc > 0
end

@testset "Tyukovsky Correction" begin
    delta_C = π / 7
    delta_0 = 0.36
    tc = tyukovsky_correction(delta_0, delta_C)
    @test tc ≈ delta_0 + delta_C^2 / 2 - delta_C^5 / 22 atol=TOL_STRICT
    # Should be larger than delta_0 (correction is positive overall)
    @test tc > delta_0
end

@testset "Einstein QNM Corrections" begin
    delta_C = π / 7
    eqnm_corr = einstein_qnm_correction(delta_C)
    eqnm_factor = einstein_qnm_factor(delta_C)

    # Correction should be small and positive
    @test eqnm_corr > 0
    @test eqnm_corr < 0.001  # Very small correction

    # Factor should be close to 1
    @test eqnm_factor ≈ 1 - eqnm_corr atol=TOL_STRICT
    @test 0.999 < eqnm_factor < 1.0

    # Corrected QNM frequency
    omega = 251.0  # GW150914 frequency
    f_corr = corrected_qnm_frequency(omega, delta_C)
    @test f_corr ≈ omega * eqnm_factor atol=TOL_STRICT
    @test f_corr < omega  # Correction reduces frequency
    @test abs(f_corr - omega) / omega < 0.001  # Shift is tiny
end

@testset "QNM Braking Correction" begin
    delta_C = π / 7
    braking_corr = qnm_braking_correction(delta_C)
    braking_factor = qnm_braking_factor(delta_C)

    # Should match einstein_qnm_correction
    @test braking_corr ≈ einstein_qnm_correction(delta_C) atol=TOL_STRICT
    @test braking_factor ≈ einstein_qnm_factor(delta_C) atol=TOL_STRICT

    # Corrected frequency from qnm module
    f_obs = 251.0
    f_corr = corrected_qnm_frequency(f_obs, delta_C)
    @test f_corr ≈ f_obs * braking_factor atol=TOL_STRICT
end

@testset "K3 Surface" begin
    k3 = K3Surface()
    @test k3.b0 == 1
    @test k3.b1 == 0
    @test k3.b2 == 22
    @test k3.b3 == 0
    @test k3.b4 == 1
    @test k3.hodge_11 == 20
    @test k3.hodge_20 == 1
    @test k3.dirac_index == 2
    @test k3.b2_plus == 3

    # Verify K3 properties
    results = verify_k3(k3)
    @test results["b₂ = h^(1,1) + 2·h^(2,0)"]
    @test results["b₂/ind(D) = 11"]
    @test results["SW compatible (b₂⁺ > 1)"]
    @test results["χ = 24"]
    @test results["σ = -16"]
end

@testset "Tyukovsky Adapter" begin
    tyuk = TyukovskyAdapter()
    @test tyuk.delta_C ≈ π / 7 atol=TOL_STRICT

    # Corrected exponent
    delta_0 = 0.36
    delta_corr = tyukovsky_corrected_exponent(delta_0, tyuk.delta_C)
    @test delta_corr ≈ delta_0 + tyuk.delta_C^2 / 2 - tyuk.delta_C^5 / 22 atol=TOL_STRICT
    @test delta_corr > delta_0
end

@testset "b₂ Uniqueness" begin
    delta_C = π / 7
    results = verify_b2_uniqueness(delta_C)

    # b₂ = 22 should be the unique best choice
    @test results["best_b2"] == 22
    @test results["b2=22 is unique best"]
    @test results["best_deviation_pct"] < 1.0
end

@testset "Enhanced Verification All" begin
    results = verify_enhanced_all()

    # K3 checks should pass
    @test results["k3"]["b₂ = h^(1,1) + 2·h^(2,0)"]
    @test results["k3"]["b₂/ind(D) = 11"]

    # QNM braking should be consistent with Einstein QNM
    @test results["qnm_einstein_consistent"]

    # b₂ = 22 should be unique best
    @test results["b2_uniqueness"]["b2=22 is unique best"]

    # Braking factor should be close to 1
    @test 0.999 < results["qnm_braking_factor"] < 1.0
end
