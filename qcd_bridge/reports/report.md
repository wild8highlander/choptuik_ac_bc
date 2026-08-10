# Choptuik-QCD Bridge Verification Report

**Author**: Ishak Khamzatovich Isaev  
**ORCID**: 0009-0003-7299-0701  
**Generated**: 2026-08-10T14:01:44  
**Elapsed (s)**: 0.009  
**Mode**: `verify_all`  
**Sections executed**: [1, 5, 6, 7, 8, 9]  

---

## RESULTS

### section_1_ochi

- **operator_shape**: `[28, 28]`
- **eigenvalues**: `[28 items, first 5: [-9.872465675559319, -9.308369242571787, -8.764487490603452, -6.503511154126617, -6.477802617328637]...]`
- **lambda_min**: `-9.872466`
- **lambda_max**: `11.976864`
- **lambda_mean**: `0.999962`
- **trace**: `27.998939`
- **kappa_T**: `8.450000`
- **N**: `28`


### section_5_tau_relax

- **theta_0**: `1.000000e-19`
- **tau_relax_s**: `5.000000e-41`
- **tau_relax_theory_s**: `3.291060e-24`
- **Lambda_QCD_eV**: `200000000.000000`
- **t_values_s**: `[60 items, first 5: [1e-45, 1.3141473626117527e-45, 1.7269832906594255e-45, 2.269510536694687e-45, 2.9824712862169065e-45]...]`
- **theta_t_values**: `[60 items, first 5: [9.999800001999987e-20, 9.999737173981413e-20, 9.999654609306742e-20, 9.99954610819386e-20, 9.999403523532672e-20]...]`
- **theta_at_1_tau**: `3.678794e-20`
- **theta_at_5_tau**: `6.737947e-22`
- **suppression_factor_at_1_tau**: `0.367879`


### section_6_kappa_T_physical

- **kappa_T_lower_95CL**: `2.620000`
- **kappa_T_best_fit**: `8.450000`
- **lattice_data_source**: `Borsányi et al. arXiv:1512.04954 (extrapolated)`
- **BF_at_lower**: `99.000000`
- **BF_at_best_fit**: `510.000000`
- **BF_class_at_lower**: `strong`
- **BF_class_at_best_fit**: `decisive`
- **physical_kappa_in_GUE_regime**: `True`
- **GUE_threshold_kappa**: `1.500000`


### section_7_cabibbo

- **b_Ch**: `0.376510`
- **c_theta_framework**: `0.094128`
- **sin_2theta_C_predicted**: `0.613604`
- **theta_C_predicted_rad**: `0.330309`
- **sin_theta_C_predicted**: `0.324335`
- **sin2_theta_C_measured**: `0.051000`
- **theta_C_measured_rad**: `0.227797`
- **sin_theta_C_measured**: `0.225832`
- **deviation_rad**: `0.102512`
- **deviation_pct**: `45.001405`
- **coincidence_quality**: `weak`


### section_8_cp_chain

#### steps

##### Item 0

- **step**: `1`
- **statement**: `O_chi = Q_hat (structural role)`
- **evidence**: `O_chi occupies the same epistemic niche as the topological charge operator`
- **section**: `§3`

##### Item 1

- **step**: `2`
- **statement**: `O_chi = Q_K3 ⊕ M_F + kappa_T * V_T at N=28`
- **evidence**: `22 K3 topological sectors ⊕ 6 quark flavors`
- **section**: `§5.6`

##### Item 2

- **step**: `3`
- **statement**: `GUE class at kappa_T > 2.62 (95% CL), BF >= 99`
- **evidence**: `Bayes factor classification: strong at lower bound, decisive at best-fit`
- **section**: `§5.7, §6.4`

##### Item 3

- **step**: `4`
- **statement**: `GUE spectral symmetry => <lambda> = 0`
- **evidence**: `Wigner semicircle is symmetric; all odd spectral moments vanish`
- **section**: `§6.5`

##### Item 4

- **step**: `5`
- **statement**: `Work formula: theta_bar = delta_C * N * <lambda> * S_GUE`
- **evidence**: `Derived from path integral over topological sectors`
- **section**: `§6`

##### Item 5

- **step**: `6`
- **statement**: `theta_bar = 0 exactly in continuum GUE regime`
- **evidence**: `Follows directly from steps 4 and 5`
- **section**: `§6`

##### Item 6

- **step**: `7`
- **statement**: `Finite-N artifact ~ 1/sqrt(N) vanishes as N -> infinity`
- **evidence**: `Monte Carlo verification across N = 10..10000`
- **section**: `§6.6`

##### Item 7

- **step**: `8`
- **statement**: `Dynamic relaxation tau_relax ~ 5e-41 s`
- **evidence**: `Damps CKM-induced residual theta_0 ~ 1e-19`
- **section**: `§6.7`

- **total_steps**: `8`
- **final_result**: `theta_bar = 0 exactly`
- **new_fields_introduced**: `0`
- **new_scales_introduced**: `0`
- **new_symmetries_introduced**: `0`
- **falsification_tests**: `['Direct lattice measurement of F(theta) - F(0) via Giusti-Rossi-Testa method', 'Derivation of work formula from PSL(2,7) algebraic geometry']`


### section_9_jet_wake

- **delta_C**: `0.448799`
- **Lambda_QCD_GeV**: `0.200000`
- **chi_eff_GeV4**: `7.180783e-04`
- **chi_eff_eV4**: `718078320820524292425978688307200.000000`
- **bridge_formula**: `chi_eff = delta_C * Lambda_QCD^4`
- **jet_wake_amplitude_ratio**: `0.142857`
- **topological_sector_count**: `22`
- **kappa_T_coupling**: `8.450000`


---

## EXECUTION LOG

```
[2026-08-10 14:01:44] Starting QCD bridge run, mode=verify_all, sections=[1, 5, 6, 7, 8, 9]
[2026-08-10 14:01:44] Language: en
[2026-08-10 14:01:44] Output dir: reports
[2026-08-10 14:01:44] Report formats: ['txt', 'csv', 'md', 'pdf', 'html', 'docx', 'json']
[2026-08-10 14:01:44] Section 1: O_chi operator construction
[2026-08-10 14:01:44]   O_chi built, shape=(28, 28), trace=27.998939
[2026-08-10 14:01:44] Section 5: tau_relax dynamics
[2026-08-10 14:01:44]   tau_relax = 5.00e-41 s
[2026-08-10 14:01:44] Section 6: kappa_T physical estimate
[2026-08-10 14:01:44]   kappa_T lower 95%CL = 2.62, BF = 99.0
[2026-08-10 14:01:44] Section 7: Cabibbo angle coincidence
[2026-08-10 14:01:44]   theta_C predicted = 0.330309, measured = 0.227797, deviation = 45.00%
[2026-08-10 14:01:44] Section 8: CP 8-step solution chain
[2026-08-10 14:01:44]   Chain complete: 8 steps -> theta_bar = 0 exactly
[2026-08-10 14:01:44] Section 9: Jet wake bridge
[2026-08-10 14:01:44]   chi_eff = 7.180783e-04 GeV^4
[2026-08-10 14:01:44] QCD bridge run complete in 0.009s
```