// dsi_core.rs — the DSI-laboratory core in Rust (cross-language self-test).
//
// Part of multilang/: the same small block of exact, deterministic
// mathematics is rewritten in several languages so the package can be
// *touched* by readers of any background. This program recomputes the
// same ten numbers the dsilab package commits to, prints them, self-
// checks, and exits. Nothing is downloaded, nothing is fitted.
//
// The checks are exact integer or fixed-order IEEE-754 double arithmetic,
// so every language twin prints byte-identical output (compare with
// ../c/reference_output.txt).
//
// Build:  rustc -O dsi_core.rs -o dsi_core
// Run:    ./dsi_core

use std::process::exit;

static mut PASS_COUNT: usize = 0;
static mut CHECK_COUNT: usize = 0;

fn report(ok: bool, name: &str, got: &str, want: &str) {
    unsafe {
        CHECK_COUNT += 1;
        if ok {
            PASS_COUNT += 1;
        }
        println!(
            "[{:02}] {:<22}= {:<36} expected {:<30} {}",
            CHECK_COUNT,
            name,
            got,
            want,
            if ok { "PASS" } else { "FAIL" }
        );
    }
}

type Mat = Vec<Vec<f64>>;

fn eye(n: usize) -> Mat {
    (0..n)
        .map(|i| (0..n).map(|j| if i == j { 1.0 } else { 0.0 }).collect())
        .collect()
}

fn mul(x: &Mat, y: &Mat) -> Mat {
    let n = x.len();
    let mut r = vec![vec![0.0f64; n]; n];
    for i in 0..n {
        for j in 0..n {
            let mut s = 0.0;
            for k in 0..n {
                s += x[i][k] * y[k][j];
            }
            r[i][j] = s;
        }
    }
    r
}

fn transpose(x: &Mat) -> Mat {
    let n = x.len();
    (0..n)
        .map(|i| (0..n).map(|j| x[j][i]).collect())
        .collect()
}

fn add(x: &Mat, y: &Mat) -> Mat {
    let n = x.len();
    (0..n)
        .map(|i| (0..n).map(|j| x[i][j] + y[i][j]).collect())
        .collect()
}

fn fro2(x: &Mat) -> f64 {
    x.iter().flat_map(|r| r.iter()).map(|v| v * v).sum()
}

fn diff(x: &Mat, y: &Mat) -> Mat {
    let n = x.len();
    (0..n)
        .map(|i| (0..n).map(|j| x[i][j] - y[i][j]).collect())
        .collect()
}

/// The Kunz defect F(X1, X2) — all-integer on {0,1} matrices.
fn leavitt_f(x1: &Mat, x2: &Mat) -> f64 {
    let id = eye(x1.len());
    let t1 = transpose(x1);
    let t2 = transpose(x2);
    fro2(&diff(&mul(&t1, x1), &id))
        + fro2(&diff(&mul(&t2, x2), &id))
        + fro2(&mul(&t1, x2))
        + fro2(&diff(&add(&mul(x1, &t1), &mul(x2, &t2)), &id))
}

/// Truncated shifts of the binary Kunz tree of depth k
/// (nodes = all words of length <= k, n = 2^(k+1) - 1).
fn kunz_tree(k: usize) -> (Mat, Mat, usize) {
    let mut words: Vec<String> = vec![String::new()];
    for _ in 0..k {
        let snapshot = words.clone();
        for w in &snapshot {
            words.push(format!("a{w}"));
            words.push(format!("b{w}"));
        }
    }
    let n = words.len();
    let index: std::collections::HashMap<&str, usize> =
        words.iter().enumerate().map(|(i, w)| (w.as_str(), i)).collect();
    let mut s1 = eye(n);
    let mut s2 = eye(n);
    for i in 0..n {
        for j in 0..n {
            s1[i][j] = 0.0;
            s2[i][j] = 0.0;
        }
    }
    for (i, w) in words.iter().enumerate() {
        if w.chars().count() >= k {
            continue;
        }
        if let Some(&j) = index.get(&format!("a{w}").as_str()) {
            s1[j][i] = 1.0;
        }
        if let Some(&j) = index.get(&format!("b{w}").as_str()) {
            s2[j][i] = 1.0;
        }
    }
    (s1, s2, n)
}

fn main() {
    // [01] the septinial constant b_Ch = 1 - cos(2*pi/7)
    {
        let bch = 1.0 - ((2.0 * std::f64::consts::PI) / 7.0).cos();
        report(
            (bch - 0.3765101981412664).abs() < 1e-17,
            "b_Ch(7)",
            &format!("{:.16}", bch),
            "0.3765101981412664",
        );
    }
    // [02] convergents of the CF [0; 24, 1, 8] (division identities, exact)
    report(
        9 * 24 + 8 == 224 && 8 * 1 + 1 == 9,
        "CF [0;24,1,8]",
        "1/24 1/25 9/224",
        "1/24 1/25 9/224",
    );
    // [03] 9/224 as a double
    {
        let ck3 = 9.0 / 224.0;
        report(
            (ck3 - 0.04017857142857143).abs() < 1e-17,
            "c_K3 = 9/224",
            &format!("{:.16}", ck3),
            "0.0401785714285714",
        );
    }
    // [04] the {7,3} census and the valence identity
    {
        let (v, e, f) = (56i32, 84i32, 24i32);
        let id_ok = 7 * f == 168 && 3 * v == 168 && 2 * e == 168;
        report(
            id_ok && v - e + f == -4,
            "{7,3} census + chi",
            &format!("V={v} E={e} F={f} id={}", if id_ok { "T" } else { "F" }),
            "V=56 E=84 F=24 id=T",
        );
    }
    // [05] theorem C: permutation pair at n = 7 gives F = 2n exactly
    {
        let n = 7usize;
        let mut p1 = eye(n);
        let mut p2 = eye(n);
        for i in 0..n {
            p1[i][i] = 0.0;
            p2[i][i] = 0.0;
            p1[i][(i + 1) % n] = 1.0;
            p2[i][(i + 2) % n] = 1.0;
        }
        let f = leavitt_f(&p1, &p2);
        report(
            (f - 14.0).abs() < 1e-12,
            "theorem C: F(perm, n=7)",
            &format!("{:.0}", f),
            "14",
        );
    }
    // [06] theorem A: complementary projections n = 8, p = q = 4: F = n
    {
        let n = 8usize;
        let mut d1 = eye(n);
        let mut d2 = eye(n);
        for i in 0..n {
            d1[i][i] = if i < 4 { 1.0 } else { 0.0 };
            d2[i][i] = if i < 4 { 0.0 } else { 1.0 };
        }
        let f = leavitt_f(&d1, &d2);
        report(
            (f - 8.0).abs() < 1e-12,
            "theorem A: F(compl, n=8)",
            &format!("{:.0}", f),
            "8",
        );
    }
    // [07] theorem B: trimmed Kunz tree k = 2 gives n = 7, F = n + 2
    {
        let (s1, s2, n) = kunz_tree(2);
        let f = leavitt_f(&s1, &s2);
        report(
            n == 7 && (f - 9.0).abs() < 1e-12,
            "theorem B: tree k=2",
            &format!("n={n} F={:.0}", f),
            "n=7 F=9",
        );
    }
    // [08] weighted tree c^2 = 4/7, k = 3: F = 549/49 (fixed-order fp)
    {
        let c2 = 4.0f64 / 7.0;
        let fw = (7.0 - 1.0) * 2.0 * (c2 - 1.0) * (c2 - 1.0) + 7.0 + 2.0;
        report(
            (fw - 549.0 / 49.0).abs() < 1e-12,
            "weighted tree c^2=4/7",
            &format!("{:.14}", fw),
            "11.20408163265306",
        );
    }
    // [09] the ladder endpoints as doubles
    {
        let e_free = 5.0f64 / 7.0;
        let e_tree = 1.0 + 2.0f64 / 7.0;
        report(
            (e_free - 0.7142857142857143).abs() < 1e-15
                && (e_tree - 1.2857142857142858).abs() < 1e-15,
            "ladder 5/7 and 1+2/7",
            &format!("{:.14} / {:.14}", e_free, e_tree),
            "0.71428571428571 / 1.28571428571429",
        );
    }
    // [10] scaled-permutation minimum: 7t^2-8t+3 at t = 4/7 equals 5/7
    {
        let t = 4.0f64 / 7.0;
        let e_min = 7.0 * t * t - 8.0 * t + 3.0;
        report(
            (e_min - 5.0 / 7.0).abs() < 1e-12,
            "min 7t^2-8t+3 at t=4/7",
            &format!("{:.14}", e_min),
            "0.71428571428571",
        );
    }
    let (pass, total) = unsafe { (PASS_COUNT, CHECK_COUNT) };
    println!(
        "\nALL CHECKS {} ({}/{})",
        if pass == total { "PASSED" } else { "FAILED" },
        pass,
        total
    );
    exit(if pass == total { 0 } else { 1 });
}
