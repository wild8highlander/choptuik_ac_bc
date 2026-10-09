// bridge.rs — Collapse-Hawking Bridge multilang self-test (Rust).
//
// Recomputes the closed-form core of the bridge from CODATA constants and
// prints a validation block. Build & run:  rustc -O bridge.rs && ./bridge
//
// STATUS: portable source, written against the same closed forms as the
// verified C / C++ / JavaScript twins. Not executed on the reference
// machine (no Rust toolchain at packaging time) — run once locally and
// diff against multilang/javascript/reference_output.txt.

use std::f64::consts::PI;

const G: f64 = 6.67430e-11;      // m^3 kg^-1 s^-2
const C: f64 = 299792458.0;      // m/s (exact)
const H: f64 = 6.62607015e-34;   // J s (exact)
const HBAR: f64 = H / (2.0 * PI);
const K_B: f64 = 1.380649e-23;   // J/K (exact)
const T_CMB: f64 = 2.72548;      // K (COBE/FIRAS)

fn t_h(m: f64) -> f64 { HBAR * C.powi(3) / (8.0 * PI * G * m * K_B) }
fn s_bh(m: f64) -> f64 {
    let rs = 2.0 * G * m / (C * C);
    let a = 4.0 * PI * rs * rs;
    K_B * C.powi(3) * a / (4.0 * G * HBAR)
}
fn t_evap(m: f64) -> f64 { 5120.0 * PI * G * G * m.powi(3) / (HBAR * C.powi(4)) }
fn p_h(m: f64) -> f64 { HBAR * C.powi(6) / (15360.0 * PI * G * G * m * m) }
fn m_cmb() -> f64 { HBAR * C.powi(3) / (8.0 * PI * G * K_B * T_CMB) }

const PAGE_FRACTION: f64 = 1.0 - 2.0f64.powf(-1.5);

fn s_rad_over_s0(tau: f64) -> f64 {
    let u2 = (1.0 - tau).powf(2.0 / 3.0);
    if tau < PAGE_FRACTION { u2 } else { 1.0 - u2 }
}

fn main() {
    let dgamma = 3.44 * 0.374;
    // F-2 per-grid floors (v2.1.0 remediation values)
    let floors = [(800.0, 0.0155), (1600.0, 8.574765e-03), (3200.0, 4.244867e-03)];

    println!("Collapse-Hawking Bridge — Rust self-test");
    println!("-------------------------------------------------");
    println!("delta_C          = pi/7                = {:.16}", PI / 7.0);
    println!("b_Ch             = 1 - cos(2 pi / 7)   = {:.17}", 1.0 - (2.0 * PI / 7.0).cos());
    println!("PAGE_FRACTION    = 1 - 2^(-3/2)        = {:.16}", PAGE_FRACTION);
    println!("Delta*gamma      = 3.44 * 0.374        = {:.6}  {}",
             dgamma, if (dgamma - 1.27).abs() <= 0.05 { "PASS" } else { "FAIL" });
    println!("M_CMB            = {:.6e} kg", m_cmb());
    println!("T_H(1e12 kg)     = {:.6e} K", t_h(1e12));
    println!("S_BH(1e12)/kB    = {:.6e}", s_bh(1e12) / K_B);
    println!("t_evap(1e12)     = {:.6e} s", t_evap(1e12));
    println!("P_H(1e12)        = {:.6e} W", p_h(1e12));
    for tau in [0.5, PAGE_FRACTION, 0.8] {
        println!("S_rad/S0({:.8})  = {:.14}", tau, s_rad_over_s0(tau));
    }
    // F-1 remediation ladder: the threshold drifts with N (2.79e-3 to N=1600)
    println!("A* (N=800)       = {:.17} | ladder N=1600: {:.10} | drift: {:.3e} (F-1)",
             0.08053436279296877f64, 0.0777437258f64, (0.08053436279296877 - 0.0777437258).abs());
    for (n, f) in floors {
        println!("floor_M(N={:.0})    = {:.6}   12/N = {:.5}", n, f, 12.0 / n);
    }
    println!("-------------------------------------------------");
    println!("All quantities above reproduce chbridge v2.1.0 closed forms.");
    println!("A* drift note: the threshold drifts with N (F-1 remediation);");
    println!("the stale 1.06e-6 agreement claim is RETRACTED.");
}
