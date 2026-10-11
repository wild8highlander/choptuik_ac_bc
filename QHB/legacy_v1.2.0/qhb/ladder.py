"""
ladder.py — comparison ladders and the constants registry.

Three comparison tables (densities, temperatures, gaps) that place the
bridge quantities next to the anchors of physics — as COMPARISONS, with
no derivation claimed in either direction:

  density ladder     mean horizon density rho(M) vs the Planck density,
                     for the born ensemble at every input scale — the
                     "binding furnace" column of the hypothesis (H1);
  temperature ladder T_H vs T_CMB and T_QCD — the two contact points;
  gap ladder         Lambda_QCD, the electroweak scale and the Planck
                     energy as frequency anchors next to the code-unit
                     gap mapped through the QCD contact (marked
                     hypothesis; same-order comparison, never a claim).

Plus qhb_constants.csv — the machine-readable registry of the package
constants (the "bridge_constants.csv" of CHB, mirrored).
"""

from .bridge import (
    PAGE_FRACTION,
    T_H,
    bridge_scales,
    equal_cmb_mass,
    equal_qcd_mass,
    nu_of_T,
    rho_mean,
)
from .constants import (
    A_WU_ANCHOR,
    BERRY_TRIO,
    BRAKING_TRIO,
    E_P,
    FTILDE_MEMBERS,
    SEED,
    T_CMB,
    T_QCD_K,
    LAMBDA_QCD_MeV,
    MeV_J,
    b_Ch,
    delta_A,
    delta_B,
    delta_C,
    echo_delta,
    eta_baryon,
    gamma_Ch,
    h,
    rho_P,
)


def density_ladder():
    """rho_mean/rho_P for every scale x member (the binding furnace)."""
    rows = []
    for name, M_in in bridge_scales():
        for label, ftd in zip(("near_floor", "mid", "saturated"),
                              FTILDE_MEMBERS):
            M = M_in * ftd
            rows.append({
                "input_scale": name, "member": label, "M_BH_kg": M,
                "rho_mean_kg_m3": rho_mean(M),
                "rho_over_rhoP": rho_mean(M) / rho_P,
            })
    return rows


def temperature_ladder():
    """T_H vs the two contact temperatures for every scale x member."""
    rows = []
    for name, M_in in bridge_scales():
        for label, ftd in zip(("near_floor", "mid", "saturated"),
                              FTILDE_MEMBERS):
            M = M_in * ftd
            rows.append({
                "input_scale": name, "member": label, "M_BH_kg": M,
                "T_H_K": T_H(M), "T_H_over_TCMB": T_H(M) / T_CMB,
                "T_H_over_TQCD": T_H(M) / T_QCD_K,
            })
    return rows


def gap_ladder(gap_static=None):
    """Frequency anchors of physics next to the mapped code-unit gap."""
    anchors = [
        ("Lambda_QCD (332 MeV)", LAMBDA_QCD_MeV * MeV_J / h),
        ("T_QCD crossover (155.16 MeV)", nu_of_T(T_QCD_K)),
        ("CMB photon (2.72548 K)", nu_of_T(T_CMB)),
        ("Planck energy (as Hz)", E_P / h),
    ]
    rows = []
    for name, nu in anchors:
        rows.append({"anchor": name, "nu_Hz": nu})
    if gap_static is not None:
        # marked-hypothesis mapping: Delta_code [Omega0=2 rad/unit] -> Hz
        # through the QCD contact frequency.  A SCALE CHOICE, not a result.
        nu_qcd = nu_of_T(T_QCD_K)
        rows.append({"anchor": "gap_code_Delta0 mapped via nu_QCD (HYPOTHESIS)",
                     "nu_Hz": gap_static * nu_qcd})
    return rows


def constants_registry(gap_static=None, B2=None):
    """The dimensionless registry of the package (machine-readable)."""
    cmb = equal_cmb_mass()
    qcd = equal_qcd_mass()
    rows = [
        ("delta_A", "pi/2", delta_A, "exact"),
        ("delta_B", "pi/3", delta_B, "exact"),
        ("delta_C", "pi/7", delta_C, "exact"),
        ("bA_berry", "pi^2/8", BERRY_TRIO[0], "exact"),
        ("bB_berry", "pi^2/18", BERRY_TRIO[1], "exact"),
        ("bC_berry", "pi^2/98", BERRY_TRIO[2], "exact"),
        ("aA_braking", "pi^5/704", BRAKING_TRIO[0], "exact"),
        ("aB_braking", "pi^5/5346", BRAKING_TRIO[1], "exact"),
        ("aC_braking", "pi^5/369754", BRAKING_TRIO[2], "exact"),
        ("b_Ch", "1-cos(2pi/7)", b_Ch, "exact"),
        ("gap_b_Ch_gammaCh_pct", "|gamma_Ch-b_Ch|/b_Ch",
         abs(gamma_Ch - b_Ch) / b_Ch, "comparison (CHB)"),
        ("page_fraction", "1-2^(-3/2)", PAGE_FRACTION, "exact"),
        ("Delta_gamma_anchor", "3.44*0.374", echo_delta * gamma_Ch,
         "comparison (CHB)"),
        ("M_CMB_kg", "hbar c^3/(8 pi G kB T_CMB)", cmb, "closed form"),
        ("M_QCD_kg", "hbar c^3/(8 pi G kB T_QCD)", qcd, "closed form (T8)"),
        ("M_QCD_vs_literature", "M_QCD/1e11 kg", qcd / 1e11,
         "comparison (PBH@QCD ~ 1e11 kg)"),
        ("A_Wu_anchor", "approximate", A_WU_ANCHOR, "literature anchor (approx)"),
        ("eta_baryon", "PDG anchor", eta_baryon, "literature anchor"),
        ("gap_static", "code units (C1)", gap_static, "committed [C1]"),
        ("gap_B2", "code units (C1)", B2, "committed [C1]"),
        ("seed", "MC seed", float(SEED), "determinism"),
    ]
    return rows


def write_outputs(density, temperature, gap, registry, out_dir):
    """Write the four ladder CSVs (byte-deterministic)."""
    import os
    os.makedirs(out_dir, exist_ok=True)

    def dump(name, header, rows):
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(",".join(header) + "\n")
            fh.writelines(",".join(
                    (r[c] if isinstance(r[c], str) else f"{r[c]:.10e}")
                    for c in header) + "\n" for r in rows)
        return path

    dump("scale_ladder_density.csv",
         ["input_scale", "member", "M_BH_kg", "rho_mean_kg_m3",
          "rho_over_rhoP"], density)
    dump("scale_ladder_temperature.csv",
         ["input_scale", "member", "M_BH_kg", "T_H_K", "T_H_over_TCMB",
          "T_H_over_TQCD"], temperature)
    with open(os.path.join(out_dir, "scale_ladder_gaps.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("anchor,nu_Hz\n")
        fh.writelines(f'"{r["anchor"]}",{r["nu_Hz"]:.10e}\n' for r in gap)
    with open(os.path.join(out_dir, "qhb_constants.csv"), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("constant,formula,value,status\n")
        fh.writelines(f'{name},"{formula}",{value:.17g},{status}\n' for name, formula, value, status in registry)
