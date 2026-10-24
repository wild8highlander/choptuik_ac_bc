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
-- Bridge (G4, v0.4.1)
#print axioms Choptuik.Bridge.im_odd_multiple
#print axioms Choptuik.Bridge.spectrum_shape_of_certificate
#print axioms Choptuik.Bridge.newton_kantorovich_local
#print axioms Choptuik.Bridge.Generated.spectrumChecks_generated
#print axioms Choptuik.Bridge.Generated.newtonChecks_generated
#print axioms Choptuik.Bridge.Generated.scalingChecks_generated
#print axioms Choptuik.Bridge.Generated.intervalChecks_generated
#print axioms Choptuik.Bridge.Discharge.bridge_unique_unstable_mode
#print axioms Choptuik.Bridge.Discharge.correction_root_exists
#print axioms Choptuik.Bridge.Discharge.correction_root_in_band
#print axioms Choptuik.Bridge.Discharge.correction_band_image_sound
#print axioms Choptuik.Bridge.Discharge.scaling_agreement
