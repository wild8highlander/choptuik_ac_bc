"""
    ChoptyukSpinor

Julia module for the verification and simulation of the Choptyuk monograph
on **Spinor corrections b-C and a-C on the Klein quartic curve**.

# Author

- **Ishak Khamzatovich Isaev** (Исаев Исхак Хамзатович)
- Email: aslan08_05@mail.ru
- GitHub: https://github.com/wild8highlander
- Repository: https://github.com/wild8highlander/choptuik_ac_bc

# Key Mathematical Objects

- **Klein curve**: Genus 3, PSL(2,7) order 168, λ₁ ≈ 3.838, R = -2
- **Spinor phases**: δ_A = π/2, δ_B = π/3, δ_C = π/7
- **Dirac trivial**: λ_{D²,triv} = 3.338
- **b-C correction**: Δ_bC = λ_{D²,triv} + δ_C²/2
- **a-C braking**: δ_eff = δ_C⁵/22 (≈ 1/1200)
- **Choptyuk base**: Δ_Ch = λ_{D²,triv} + δ_C²/2 - δ_C⁵/22
- **Full formula**: Δ_Ch = λ_{D²,triv} + δ_C²/2 + δ_C⁴/8 - δ_C⁵/22 + δ_C⁶/2
- **b_Ch**: 1 - cos(2π/7) ≈ 0.377
- **64 spinor structures**: 2⁶ combinations
- **Observed Δ**: 3.443 (from LIGO QNM data)

# Exports

## Structures
- `KleinCurve`, `PSL27Generator`
- `SpinorPhases`, `SpinorStructure`
- `DiracOperator`
- `ChoptyukFormula`
- `SurfaceSpec`, `BOLZA`, `BRING`, `MACBEATH`, `KLEIN`, `ALL_SURFACES`
- `QNMPredictor`, `LIGOEvent`, `LIGO_EVENTS`
- `HypothesisConfig`, `HypothesisResult`, `HypothesisTester`
- `Simulator`

## Klein Curve Functions
- `klein_generators`, `mat_power_mod`, `mat_eq_projective`
- `verify_relations`, `hurwitz_bound`, `is_hurwitz_curve`

## Spinor Phase Functions
- `enumerate_64_structures`, `verify_phase_relations`, `phase_symmetry_classes`

## Dirac Operator Functions
- `lichnerowicz`, `dirac_spectrum`, `verify_dirac_relations`

## Choptyuk Formula Functions
- `bC_correction`, `aC_braking`, `aC_correction`
- `choptyuk_formula`, `choptyuk_constant`, `verify_choptyuk_formula`

## Surface Functions
- `surface_choptyuk`, `hurwitz_achieved`, `verify_surface`, `compare_surfaces`

## QNM Functions
- `qnm_frequency`, `predict_shift`, `detectability`, `verify_qnm`

## Hypothesis Functions
- `test_hypothesis`, `parameter_sweep`, `sensitivity_analysis`

## Simulation Functions
- `sweep_delta_C`, `sweep_lambda_1`, `convergence_analysis`, `run_full_simulation`

## Submodules
- `Visualization`: Plot generation
- `Reporting`: Report generation (TXT, MD, CSV, HTML, JSON)
- `InteractiveMenu`: Interactive REPL menu
"""
module ChoptyukSpinor

using LinearAlgebra
using Printf
using Dates

# Include source files
include("klein_curve.jl")
include("spinor_phases.jl")
include("dirac_operator.jl")
include("choptyuk_formula.jl")
include("surfaces.jl")
include("qnm.jl")
include("hypothesis.jl")
include("simulation.jl")
include("enhanced_verification.jl")

# Submodules (must come after main includes)
include("visualization.jl")
include("reporting.jl")
include("interactive_menu.jl")

# Export all public types
export KleinCurve, PSL27Generator
export SpinorPhases, SpinorStructure
export DiracOperator
export ChoptyukFormula
export SurfaceSpec, BOLZA, BRING, MACBEATH, KLEIN, ALL_SURFACES
export QNMPredictor, LIGOEvent, LIGO_EVENTS
export HypothesisConfig, HypothesisResult, HypothesisTester
export Simulator
export K3Surface, TyukovskyAdapter

# Export Klein curve functions
export klein_generators, mat_power_mod, mat_eq_projective
export verify_relations, hurwitz_bound, is_hurwitz_curve

# Export spinor phase functions
export enumerate_64_structures, verify_phase_relations, phase_symmetry_classes

# Export Dirac operator functions
export lichnerowicz, dirac_spectrum, verify_dirac_relations

# Export Choptyuk formula functions
export bC_correction, aC_braking, aC_correction
export choptyuk_formula, choptyuk_constant, verify_choptyuk_formula
export imaginary_correction, kahler_correction, tyukovsky_correction
export einstein_qnm_correction, einstein_qnm_factor, corrected_qnm_frequency

# Export surface functions
export surface_choptyuk, hurwitz_achieved, verify_surface, compare_surfaces

# Export QNM functions
export qnm_frequency, predict_shift, detectability, verify_qnm
export qnm_braking_correction, qnm_braking_factor

# Export hypothesis functions
export test_hypothesis, parameter_sweep, sensitivity_analysis

# Export simulation functions
export sweep_delta_C, sweep_lambda_1, convergence_analysis, run_full_simulation
export verify_k3, tyukovsky_corrected_exponent, verify_b2_uniqueness, verify_enhanced_all

# Export submodules
export Visualization, Reporting, InteractiveMenu

end # module ChoptyukSpinor
