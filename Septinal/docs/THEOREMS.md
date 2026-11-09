<p align="center">
  <img src="../assets/banners/banner_theorems.svg" alt="theorem atlas" width="100%">
</p>

# docs/THEOREMS.md — the theorem atlas

![theorems](https://img.shields.io/badge/top--level_theorems-145-4CC9F0.svg)
![headline](https://img.shields.io/badge/audited_headline-95-brightgreen.svg)
![axioms](https://img.shields.io/badge/permitted-propext·choice·Quot.sound-6b2c8f.svg)

Every top-level theorem of the two Lean libraries, scanned from the
committed sources (regenerate: `python scripts/generate_docs.py`).
Line numbers point into the module files; the headline lists are the
exact `#print axioms` orders of the two audit files.

## Geometry — the double-null arena

| Theorem | Source |
|---|---|
| `Choptuik.Geometry.Curvature.critical_singularity_is_strong_and_isotropic` | [Choptuik/Geometry/Curvature.lean:80](../lean/Choptuik/Geometry/Curvature.lean#L80) |
| `Choptuik.Geometry.Curvature.divergence_invariant_under_rescaling` | [Choptuik/Geometry/Curvature.lean:116](../lean/Choptuik/Geometry/Curvature.lean#L116) |

## Analysis — field equations, PDE, intervals

| Theorem | Source |
|---|---|
| `Choptuik.Analysis.FieldEquations.minkowski_isSolution` | [Choptuik/Analysis/FieldEquations.lean:276](../lean/Choptuik/Analysis/FieldEquations.lean#L276) |
| `Choptuik.Analysis.FieldEquations.schwarzschild_isSolution` | [Choptuik/Analysis/FieldEquations.lean:481](../lean/Choptuik/Analysis/FieldEquations.lean#L481) |
| `Choptuik.Analysis.FieldEquations.hawking_mass_v_deriv` | [Choptuik/Analysis/FieldEquations.lean:698](../lean/Choptuik/Analysis/FieldEquations.lean#L698) |
| `Choptuik.Analysis.FieldEquations.hawking_mass_u_deriv` | [Choptuik/Analysis/FieldEquations.lean:778](../lean/Choptuik/Analysis/FieldEquations.lean#L778) |
| `Choptuik.Analysis.FieldEquations.hawking_mass_monotone_v` | [Choptuik/Analysis/FieldEquations.lean:861](../lean/Choptuik/Analysis/FieldEquations.lean#L861) |
| `Choptuik.Analysis.FieldEquations.hawking_mass_monotone_u` | [Choptuik/Analysis/FieldEquations.lean:882](../lean/Choptuik/Analysis/FieldEquations.lean#L882) |
| `Choptuik.Analysis.HyperbolicPDE.local_wellposedness` | [Choptuik/Analysis/HyperbolicPDE.lean:84](../lean/Choptuik/Analysis/HyperbolicPDE.lean#L84) |
| `Choptuik.Analysis.Interval.add_sound` | [Choptuik/Analysis/Interval.lean:55](../lean/Choptuik/Analysis/Interval.lean#L55) |
| `Choptuik.Analysis.Interval.mul_sound` | [Choptuik/Analysis/Interval.lean:104](../lean/Choptuik/Analysis/Interval.lean#L104) |
| `Choptuik.Analysis.Interval.certificate_principle` | [Choptuik/Analysis/Interval.lean:128](../lean/Choptuik/Analysis/Interval.lean#L128) |

## Existence — DSS solutions and Newton–Kantorovich

| Theorem | Source |
|---|---|
| `Choptuik.Existence.DSS.critical_solution_exists` | [Choptuik/Existence/DSS.lean:107](../lean/Choptuik/Existence/DSS.lean#L107) |
| `Choptuik.Existence.DSS.dss_fundamental_domain_determination` | [Choptuik/Existence/DSS.lean:131](../lean/Choptuik/Existence/DSS.lean#L131) |
| `Choptuik.Existence.DSS.critical_solution_unique` | [Choptuik/Existence/DSS.lean:282](../lean/Choptuik/Existence/DSS.lean#L282) |
| `Choptuik.Existence.DSS.dss_reparametrization_invariance` | [Choptuik/Existence/DSS.lean:302](../lean/Choptuik/Existence/DSS.lean#L302) |
| `Choptuik.Existence.DSSBoundary.minkowski_dss` | [Choptuik/Existence/DSSBoundary.lean:64](../lean/Choptuik/Existence/DSSBoundary.lean#L64) |
| `Choptuik.Existence.DSSBoundary.minkowski_css` | [Choptuik/Existence/DSSBoundary.lean:71](../lean/Choptuik/Existence/DSSBoundary.lean#L71) |
| `Choptuik.Existence.DSSBoundary.existence_vacuous_without_nondegeneracy` | [Choptuik/Existence/DSSBoundary.lean:78](../lean/Choptuik/Existence/DSSBoundary.lean#L78) |
| `Choptuik.Existence.DSSBoundary.minkowski_fails_nondegeneracy` | [Choptuik/Existence/DSSBoundary.lean:108](../lean/Choptuik/Existence/DSSBoundary.lean#L108) |
| `Choptuik.Existence.DSSBoundary.dss_iff_periodic` | [Choptuik/Existence/DSSBoundary.lean:172](../lean/Choptuik/Existence/DSSBoundary.lean#L172) |
| `Choptuik.Existence.DSSBoundary.css_iff_constant` | [Choptuik/Existence/DSSBoundary.lean:250](../lean/Choptuik/Existence/DSSBoundary.lean#L250) |
| `Choptuik.Existence.DSSBoundary.dss_solution_iff_periodic_bvp` | [Choptuik/Existence/DSSBoundary.lean:286](../lean/Choptuik/Existence/DSSBoundary.lean#L286) |
| `Choptuik.Existence.ImplicitFunction.derivIsomorphism_iff` | [Choptuik/Existence/ImplicitFunction.lean:76](../lean/Choptuik/Existence/ImplicitFunction.lean#L76) |
| `Choptuik.Existence.ImplicitFunction.newton_map_contractive` | [Choptuik/Existence/ImplicitFunction.lean:95](../lean/Choptuik/Existence/ImplicitFunction.lean#L95) |
| `Choptuik.Existence.ImplicitFunction.existence_via_implicit_function` | [Choptuik/Existence/ImplicitFunction.lean:141](../lean/Choptuik/Existence/ImplicitFunction.lean#L141) |
| `Choptuik.Existence.ImplicitFunction.newton_zero_unique` | [Choptuik/Existence/ImplicitFunction.lean:333](../lean/Choptuik/Existence/ImplicitFunction.lean#L333) |
| `Choptuik.Existence.ImplicitFunction.existence_persists_under_perturbation` | [Choptuik/Existence/ImplicitFunction.lean:364](../lean/Choptuik/Existence/ImplicitFunction.lean#L364) |
| `Choptuik.Existence.TruncatedDSS.trunc_certificate` | [Choptuik/Existence/TruncatedDSS.lean:53](../lean/Choptuik/Existence/TruncatedDSS.lean#L53) |
| `Choptuik.Existence.TruncatedDSS.truncated_dss_solution_exists_unique` | [Choptuik/Existence/TruncatedDSS.lean:97](../lean/Choptuik/Existence/TruncatedDSS.lean#L97) |

## Stability — linearization and the spectrum

| Theorem | Source |
|---|---|
| `Choptuik.Stability.Gershgorin.gershgorin_disc` | [Choptuik/Stability/Gershgorin.lean:37](../lean/Choptuik/Stability/Gershgorin.lean#L37) |
| `Choptuik.Stability.Spectrum.echoingPeriod_gundlach1997` | [Choptuik/Stability/Spectrum.lean:72](../lean/Choptuik/Stability/Spectrum.lean#L72) |
| `Choptuik.Stability.Spectrum.gamma_eq_inv_lambda0` | [Choptuik/Stability/Spectrum.lean:80](../lean/Choptuik/Stability/Spectrum.lean#L80) |
| `Choptuik.Stability.Spectrum.echoingPeriod_pos` | [Choptuik/Stability/Spectrum.lean:83](../lean/Choptuik/Stability/Spectrum.lean#L83) |
| `Choptuik.Stability.Spectrum.lambda0_pos` | [Choptuik/Stability/Spectrum.lean:88](../lean/Choptuik/Stability/Spectrum.lean#L88) |
| `Choptuik.Stability.Spectrum.mem_certifiedSpectrum` | [Choptuik/Stability/Spectrum.lean:106](../lean/Choptuik/Stability/Spectrum.lean#L106) |
| `Choptuik.Stability.Spectrum.certified_decaying_re_neg` | [Choptuik/Stability/Spectrum.lean:123](../lean/Choptuik/Stability/Spectrum.lean#L123) |
| `Choptuik.Stability.Spectrum.unique_unstable_mode` | [Choptuik/Stability/Spectrum.lean:148](../lean/Choptuik/Stability/Spectrum.lean#L148) |
| `Choptuik.Stability.Spectrum.echo_family_structure` | [Choptuik/Stability/Spectrum.lean:242](../lean/Choptuik/Stability/Spectrum.lean#L242) |
| `Choptuik.Stability.Spectrum.mass_scaling_law` | [Choptuik/Stability/Spectrum.lean:282](../lean/Choptuik/Stability/Spectrum.lean#L282) |

## Scaling — the law, the echo, universality

| Theorem | Source |
|---|---|
| `Choptuik.Scaling.gamma_close_to_published` | [Choptuik/Scaling.lean:72](../lean/Choptuik/Scaling.lean#L72) |
| `Choptuik.Scaling.universality` | [Choptuik/Scaling.lean:106](../lean/Choptuik/Scaling.lean#L106) |
| `Choptuik.Scaling.echoing_formula` | [Choptuik/Scaling.lean:142](../lean/Choptuik/Scaling.lean#L142) |
| `Choptuik.ScalingDerivation.wiggle_periodic` | [Choptuik/ScalingDerivation.lean:129](../lean/Choptuik/ScalingDerivation.lean#L129) |
| `Choptuik.ScalingDerivation.scaling_law_derived` | [Choptuik/ScalingDerivation.lean:168](../lean/Choptuik/ScalingDerivation.lean#L168) |
| `Choptuik.ScalingDerivation.wiggle_period` | [Choptuik/ScalingDerivation.lean:190](../lean/Choptuik/ScalingDerivation.lean#L190) |
| `Choptuik.ScalingDerivation.wiggle_physical_check` | [Choptuik/ScalingDerivation.lean:202](../lean/Choptuik/ScalingDerivation.lean#L202) |
| `Choptuik.ScalingDerivation.wiggle_published_check` | [Choptuik/ScalingDerivation.lean:227](../lean/Choptuik/ScalingDerivation.lean#L227) |

## Bridge — the certificate channel

| Theorem | Source |
|---|---|
| `Choptuik.Bridge.Certificates.realMem_of_mem` | [Choptuik/Bridge/Certificates.lean:67](../lean/Choptuik/Bridge/Certificates.lean#L67) |
| `Choptuik.Bridge.Certificates.certified_unstable_pos` | [Choptuik/Bridge/Certificates.lean:124](../lean/Choptuik/Bridge/Certificates.lean#L124) |
| `Choptuik.Bridge.Certificates.certified_decaying_neg` | [Choptuik/Bridge/Certificates.lean:130](../lean/Choptuik/Bridge/Certificates.lean#L130) |
| `Choptuik.Bridge.Certificates.im_odd_multiple` | [Choptuik/Bridge/Certificates.lean:142](../lean/Choptuik/Bridge/Certificates.lean#L142) |
| `Choptuik.Bridge.Certificates.spectrum_shape_of_certificate` | [Choptuik/Bridge/Certificates.lean:173](../lean/Choptuik/Bridge/Certificates.lean#L173) |
| `Choptuik.Bridge.Certificates.newton_kantorovich_local` | [Choptuik/Bridge/Certificates.lean:212](../lean/Choptuik/Bridge/Certificates.lean#L212) |
| `Choptuik.Bridge.Discharge.bridge_unique_unstable_mode` | [Choptuik/Bridge/Discharge.lean:78](../lean/Choptuik/Bridge/Discharge.lean#L78) |
| `Choptuik.Bridge.Discharge.correction_inv_deriv` | [Choptuik/Bridge/Discharge.lean:126](../lean/Choptuik/Bridge/Discharge.lean#L126) |
| `Choptuik.Bridge.Discharge.correction_deriv_inv` | [Choptuik/Bridge/Discharge.lean:131](../lean/Choptuik/Bridge/Discharge.lean#L131) |
| `Choptuik.Bridge.Discharge.correction_inv_bound` | [Choptuik/Bridge/Discharge.lean:137](../lean/Choptuik/Bridge/Discharge.lean#L137) |
| `Choptuik.Bridge.Discharge.correction_lip` | [Choptuik/Bridge/Discharge.lean:145](../lean/Choptuik/Bridge/Discharge.lean#L145) |
| `Choptuik.Bridge.Discharge.correction_residual` | [Choptuik/Bridge/Discharge.lean:174](../lean/Choptuik/Bridge/Discharge.lean#L174) |
| `Choptuik.Bridge.Discharge.correction_root_exists` | [Choptuik/Bridge/Discharge.lean:185](../lean/Choptuik/Bridge/Discharge.lean#L185) |
| `Choptuik.Bridge.Discharge.correction_root_eq_sqrt` | [Choptuik/Bridge/Discharge.lean:196](../lean/Choptuik/Bridge/Discharge.lean#L196) |
| `Choptuik.Bridge.Discharge.correction_root_in_band` | [Choptuik/Bridge/Discharge.lean:225](../lean/Choptuik/Bridge/Discharge.lean#L225) |
| `Choptuik.Bridge.Discharge.correction_band_image_sound` | [Choptuik/Bridge/Discharge.lean:262](../lean/Choptuik/Bridge/Discharge.lean#L262) |
| `Choptuik.Bridge.Discharge.scaling_agreement` | [Choptuik/Bridge/Discharge.lean:307](../lean/Choptuik/Bridge/Discharge.lean#L307) |
| `Choptuik.Bridge.Generated.check_unstable_pos` | [Choptuik/Bridge/Generated.lean:53](../lean/Choptuik/Bridge/Generated.lean#L53) |
| `Choptuik.Bridge.Generated.check_decaying_neg` | [Choptuik/Bridge/Generated.lean:56](../lean/Choptuik/Bridge/Generated.lean#L56) |
| `Choptuik.Bridge.Generated.check_im_pos` | [Choptuik/Bridge/Generated.lean:60](../lean/Choptuik/Bridge/Generated.lean#L60) |
| `Choptuik.Bridge.Generated.check_fundamental` | [Choptuik/Bridge/Generated.lean:64](../lean/Choptuik/Bridge/Generated.lean#L64) |
| `Choptuik.Bridge.Generated.check_lam0_agree` | [Choptuik/Bridge/Generated.lean:67](../lean/Choptuik/Bridge/Generated.lean#L67) |
| `Choptuik.Bridge.Generated.check_re_agree` | [Choptuik/Bridge/Generated.lean:70](../lean/Choptuik/Bridge/Generated.lean#L70) |
| `Choptuik.Bridge.Generated.check_odd_lo` | [Choptuik/Bridge/Generated.lean:75](../lean/Choptuik/Bridge/Generated.lean#L75) |
| `Choptuik.Bridge.Generated.check_odd_hi` | [Choptuik/Bridge/Generated.lean:80](../lean/Choptuik/Bridge/Generated.lean#L80) |
| `Choptuik.Bridge.Generated.check_lam0_width` | [Choptuik/Bridge/Generated.lean:85](../lean/Choptuik/Bridge/Generated.lean#L85) |
| `Choptuik.Bridge.Generated.check_re_width` | [Choptuik/Bridge/Generated.lean:88](../lean/Choptuik/Bridge/Generated.lean#L88) |
| `Choptuik.Bridge.Generated.check_im_width` | [Choptuik/Bridge/Generated.lean:92](../lean/Choptuik/Bridge/Generated.lean#L92) |
| `Choptuik.Bridge.Generated.spectrumChecks_generated` | [Choptuik/Bridge/Generated.lean:97](../lean/Choptuik/Bridge/Generated.lean#L97) |
| `Choptuik.Bridge.Generated.newtonChecks_generated` | [Choptuik/Bridge/Generated.lean:104](../lean/Choptuik/Bridge/Generated.lean#L104) |
| `Choptuik.Bridge.Generated.nkConstants_generated` | [Choptuik/Bridge/Generated.lean:111](../lean/Choptuik/Bridge/Generated.lean#L111) |
| `Choptuik.Bridge.Generated.scalingChecks_generated` | [Choptuik/Bridge/Generated.lean:117](../lean/Choptuik/Bridge/Generated.lean#L117) |
| `Choptuik.Bridge.Generated.intervalChecks_generated` | [Choptuik/Bridge/Generated.lean:126](../lean/Choptuik/Bridge/Generated.lean#L126) |

## The audited headline declarations

### `Choptuik` — 33 declarations, all `[propext, Classical.choice, Quot.sound]`

- `Choptuik.Geometry.divergence_invariant_under_rescaling`
- `Choptuik.Geometry.critical_singularity_is_strong_and_isotropic`
- `Choptuik.Analysis.add_sound`
- `Choptuik.Analysis.mul_sound`
- `Choptuik.Analysis.certificate_principle`
- `Choptuik.Analysis.local_wellposedness`
- `Choptuik.Existence.critical_solution_exists`
- `Choptuik.Existence.dss_fundamental_domain_determination`
- `Choptuik.Existence.critical_solution_unique`
- `Choptuik.Existence.dss_reparametrization_invariance`
- `Choptuik.Existence.newton_map_contractive`
- `Choptuik.Existence.existence_via_implicit_function`
- `Choptuik.Existence.newton_zero_unique`
- `Choptuik.Existence.existence_persists_under_perturbation`
- `Choptuik.Existence.derivIsomorphism_iff`
- `Choptuik.Stability.unique_unstable_mode`
- `Choptuik.Stability.echo_family_structure`
- `Choptuik.Stability.mass_scaling_law`
- `Choptuik.Scaling.gamma_close_to_published`
- `Choptuik.Scaling.universality`
- `Choptuik.Scaling.echoing_formula`
- `Choptuik.Bridge.im_odd_multiple`
- `Choptuik.Bridge.spectrum_shape_of_certificate`
- `Choptuik.Bridge.newton_kantorovich_local`
- `Choptuik.Bridge.Generated.spectrumChecks_generated`
- `Choptuik.Bridge.Generated.newtonChecks_generated`
- `Choptuik.Bridge.Generated.scalingChecks_generated`
- `Choptuik.Bridge.Generated.intervalChecks_generated`
- `Choptuik.Bridge.Discharge.bridge_unique_unstable_mode`
- `Choptuik.Bridge.Discharge.correction_root_exists`
- `Choptuik.Bridge.Discharge.correction_root_in_band`
- `Choptuik.Bridge.Discharge.correction_band_image_sound`
- `Choptuik.Bridge.Discharge.scaling_agreement`

### `Satellite` — 62 declarations, all `[propext, Classical.choice, Quot.sound]`

- `Satellite.Dial.card_dial`
- `Satellite.Dial.effective`
- `Satellite.Dial.beta_A`
- `Satellite.Dial.beta_B`
- `Satellite.Dial.beta_C`
- `Satellite.Dial.alpha_A`
- `Satellite.Dial.alpha_B`
- `Satellite.Dial.alpha_C`
- `Satellite.Chiral.card_left`
- `Satellite.Chiral.card_right`
- `Satellite.Chiral.disjoint_left_right`
- `Satellite.Chiral.chiral_split`
- `Satellite.Chiral.cover`
- `Satellite.Chiral.refl_involutive`
- `Satellite.Chiral.refl_left_to_right`
- `Satellite.Chiral.refl_right_to_left`
- `Satellite.Chiral.refl_blocked`
- `Satellite.Chiral.refl_bijective`
- `Satellite.Corrections.k_betti`
- `Satellite.Corrections.denom_A`
- `Satellite.Corrections.denom_B`
- `Satellite.Corrections.denom_C`
- `Satellite.Corrections.vib_carrier`
- `Satellite.Corrections.carrier_98`
- `Satellite.Corrections.cos_septinial_gt_half`
- `Satellite.Corrections.b_Ch_bounds`
- `Satellite.Corrections.gamma3_bounds`
- `Satellite.Berry.sqrt_ge_one`
- `Satellite.Berry.lambdaLower_rationalized`
- `Satellite.Berry.lambdaLower_is_lower_root`
- `Satellite.Berry.remainder_eq`
- `Satellite.Berry.remainder_pos`
- `Satellite.Berry.remainder_le`
- `Satellite.Cascade.rot_preserves_iff`
- `Satellite.Cascade.refl_preserves_iff`
- `Satellite.Cascade.rot12_rot12`
- `Satellite.Cascade.rfl0_rfl0`
- `Satellite.Cascade.rfl12_rfl12`
- `Satellite.Cascade.rot12_rfl0`
- `Satellite.Cascade.rfl0_rot12`
- `Satellite.Cascade.survivors_commute`
- `Satellite.Cascade.exactly_two_rotations`
- `Satellite.Cascade.exactly_two_reflections`
- `Satellite.Cascade.rot12_val`
- `Satellite.Unlock.alpha_pos`
- `Satellite.Unlock.beta_pos`
- `Satellite.Unlock.gamma_exact`
- `Satellite.Unlock.gamma_bounds`
- `Satellite.Unlock.k_exact`
- `Satellite.Unlock.quanta`
- `Satellite.Unlock.orientation_tail`
- `Satellite.Unlock.unlock`
- `Satellite.Klein.order_dist_sum`
- `Satellite.Klein.subgroup_lattice_orders`
- `Satellite.Klein.s4_count`
- `Satellite.Klein.faces_times_stab`
- `Satellite.Klein.flags_split`
- `Satellite.Klein.euler_klein`
- `Satellite.Klein.antipodal_triples`
- `Satellite.Klein.sphere_profile`
- `Satellite.Klein.k3_bridge`
- `Satellite.Klein.involution_action`

---

*Audit logs: `logs/choptuik_audit.log` (`AUDIT_EXIT=0`) and
`logs/sat_final.log` (`Build completed successfully`).*
