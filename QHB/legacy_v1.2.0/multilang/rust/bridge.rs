// bridge.rs — the Quark-Hawking Bridge twin (Rust, self-test).
// Run: rustc -O bridge.rs && ./bridge   (source twin; no toolchain was
// available at packaging time — carried as a source, like CHB does).
use std::f64::consts::PI;

fn residual(alpha: f64, x: f64) -> f64 {
    let f = |u: f64| -> f64 {
        if u < 1e-300 { x } else { -(-x * u).exp_m1() / u }
    };
    let fp = f(1.0 - alpha);
    let fm = f(1.0 + alpha);
    (fp - fm) / (fp + fm)
}

fn main() {
    let g: f64 = 6.67430e-11;
    let c: f64 = 299792458.0;
    let h: f64 = 6.62607015e-34;
    let hbar = h / (2.0 * PI);
    let k_b: f64 = 1.380649e-23;
    let mev_j: f64 = 1.602176634e-13;
    let t_cmb: f64 = 2.72548;
    let t_qcd = 155.16 * mev_j / k_b;

    let b_ch = 1.0 - (2.0 * PI / 7.0).cos();
    let page = 1.0 - 2.0f64.powf(-1.5);
    let m_qcd = hbar * c.powi(3) / (8.0 * PI * g * k_b * t_qcd);
    let m_cmb = hbar * c.powi(3) / (8.0 * PI * g * k_b * t_cmb);
    let th12 = hbar * c.powi(3) / (8.0 * PI * g * k_b * 1e12);
    let growth = 1.5f64.sqrt();
    let (delta0, b2) = (0.523004556028, -5.49670294e-2);
    let gapq = delta0 + b2 * 0.2 * 0.2;

    let rows: [(&str, f64, f64); 11] = [
        ("delta_C = pi/7", PI / 7.0, 0.44879895051282761),
        ("b_Ch = 1-cos(2pi/7)", b_ch, 0.37651019814126640),
        ("Page fraction", page, 0.64644660940672620),
        ("M_QCD [kg]", m_qcd, 6.814006e10),
        ("M_CMB [kg]", m_cmb, 4.501595e22),
        ("T_H(1e12 kg) [K]", th12, 1.226901e11),
        ("r_Wu(0.9, 100)", residual(0.9, 100.0), 0.899995686821),
        ("Gascheau growth sqrt(3/2)", growth, 1.22474487139158905),
        ("gap law Delta_F(0.2)", gapq, 0.520805874852),
    ("vortex Lagrange 3/(2pi)", 3.0 / (2.0 * std::f64::consts::PI), 0.477464829275686),
        ("placeholder-a", 0.0, 0.0),
        ("placeholder-b", 0.0, 0.0),
    ];
    let mut pass = 0;
    for (name, val, r) in rows.iter() {
        if *name.starts_with("placeholder") { continue; }
        let rel = ((val - r).abs()) / r.abs();
        let ok = rel < 1e-6;
        if ok { pass += 1; }
        println!("{:<30} = {:<20.12} {} (rel {:.2e})",
                 name, val, if ok { "PASS" } else { "FAIL" }, rel);
    }
    println!("{}/9 checks PASS (qhb twin, Rust)", pass);
}
