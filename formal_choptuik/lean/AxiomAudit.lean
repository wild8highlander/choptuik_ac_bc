/-
   FORMAL CHOPTUIK · AxiomAudit.lean — axiom audit of all headline theorems
   (the QHB-style discipline: `sorryAx` must NOT appear in the output).
   Run: lake env lean AxiomAudit.lean
-/
import Choptuik

-- Geometry
#print axioms Choptuik.Geometry.divergence_invariant_under_rescaling
#print axioms Choptuik.Geometry.critical_singularity_is_strong_and_isotropic
-- Analysis
#print axioms Choptuik.Analysis.add_sound
#print axioms Choptuik.Analysis.mul_sound
#print axioms Choptuik.Analysis.certificate_principle
#print axioms Choptuik.Analysis.local_wellposedness
-- Existence
#print axioms Choptuik.Existence.critical_solution_exists
#print axioms Choptuik.Existence.dss_fundamental_domain_determination
#print axioms Choptuik.Existence.critical_solution_unique
#print axioms Choptuik.Existence.dss_reparametrization_invariance
#print axioms Choptuik.Existence.newton_map_contractive
#print axioms Choptuik.Existence.existence_via_implicit_function
#print axioms Choptuik.Existence.newton_zero_unique
#print axioms Choptuik.Existence.existence_persists_under_perturbation
#print axioms Choptuik.Existence.derivIsomorphism_iff
-- Stability
#print axioms Choptuik.Stability.unique_unstable_mode
#print axioms Choptuik.Stability.echo_family_structure
#print axioms Choptuik.Stability.mass_scaling_law
-- Scaling
#print axioms Choptuik.Scaling.gamma_close_to_published
#print axioms Choptuik.Scaling.universality
#print axioms Choptuik.Scaling.echoing_formula
