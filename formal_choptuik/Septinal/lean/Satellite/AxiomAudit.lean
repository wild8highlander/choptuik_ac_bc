/-
  Septinial braking satellite · AxiomAudit: mechanical proof that every
  headline theorem of the satellite depends only on the three standard axioms
  of Lean (propext, Classical.choice, Quot.sound) — no sorryAx anywhere.
  Run: lake env lean Satellite/AxiomAudit.lean
-/
import Satellite
import Satellite.C5_Klein

#print axioms Satellite.Dial.card_dial
#print axioms Satellite.Dial.effective
#print axioms Satellite.Dial.beta_A
#print axioms Satellite.Dial.beta_B
#print axioms Satellite.Dial.beta_C
#print axioms Satellite.Dial.alpha_A
#print axioms Satellite.Dial.alpha_B
#print axioms Satellite.Dial.alpha_C
#print axioms Satellite.Chiral.card_left
#print axioms Satellite.Chiral.card_right
#print axioms Satellite.Chiral.disjoint_left_right
#print axioms Satellite.Chiral.chiral_split
#print axioms Satellite.Chiral.cover
#print axioms Satellite.Chiral.refl_involutive
#print axioms Satellite.Chiral.refl_left_to_right
#print axioms Satellite.Chiral.refl_right_to_left
#print axioms Satellite.Chiral.refl_blocked
#print axioms Satellite.Chiral.refl_bijective
#print axioms Satellite.Corrections.k_betti
#print axioms Satellite.Corrections.denom_A
#print axioms Satellite.Corrections.denom_B
#print axioms Satellite.Corrections.denom_C
#print axioms Satellite.Corrections.vib_carrier
#print axioms Satellite.Corrections.carrier_98
#print axioms Satellite.Corrections.cos_septinial_gt_half
#print axioms Satellite.Corrections.b_Ch_bounds
#print axioms Satellite.Corrections.gamma3_bounds
#print axioms Satellite.Berry.sqrt_ge_one
#print axioms Satellite.Berry.lambdaLower_rationalized
#print axioms Satellite.Berry.lambdaLower_is_lower_root
#print axioms Satellite.Berry.remainder_eq
#print axioms Satellite.Berry.remainder_pos
#print axioms Satellite.Berry.remainder_le
#print axioms Satellite.Cascade.rot_preserves_iff
#print axioms Satellite.Cascade.refl_preserves_iff
#print axioms Satellite.Cascade.rot12_rot12
#print axioms Satellite.Cascade.rfl0_rfl0
#print axioms Satellite.Cascade.rfl12_rfl12
#print axioms Satellite.Cascade.rot12_rfl0
#print axioms Satellite.Cascade.rfl0_rot12
#print axioms Satellite.Cascade.survivors_commute
#print axioms Satellite.Cascade.exactly_two_rotations
#print axioms Satellite.Cascade.exactly_two_reflections
#print axioms Satellite.Cascade.rot12_val
#print axioms Satellite.Unlock.alpha_pos
#print axioms Satellite.Unlock.beta_pos
#print axioms Satellite.Unlock.gamma_exact
#print axioms Satellite.Unlock.gamma_bounds
#print axioms Satellite.Unlock.k_exact
#print axioms Satellite.Unlock.quanta
#print axioms Satellite.Unlock.orientation_tail
#print axioms Satellite.Unlock.unlock
#print axioms Satellite.Klein.order_dist_sum
#print axioms Satellite.Klein.subgroup_lattice_orders
#print axioms Satellite.Klein.s4_count
#print axioms Satellite.Klein.faces_times_stab
#print axioms Satellite.Klein.flags_split
#print axioms Satellite.Klein.euler_klein
#print axioms Satellite.Klein.antipodal_triples
#print axioms Satellite.Klein.sphere_profile
#print axioms Satellite.Klein.k3_bridge
#print axioms Satellite.Klein.involution_action
