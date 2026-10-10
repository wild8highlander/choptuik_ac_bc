// bridge.cpp — the Quark-Hawking Bridge twin (C++, self-test).
// Recomputes the closed-form core from the CODATA constants, prints the
// validation block, exits.  Build: g++ -O2 -std=c++17 -o bridge bridge.cpp
#include <cmath>
#include <cstdio>
#include <string>

static double residual(double alpha, double x) {
    auto f = [&](double u) {
        return (u < 1e-300) ? x : -std::expm1(-x * u) / u;
    };
    double fp = f(1.0 - alpha), fm = f(1.0 + alpha);
    return (fp - fm) / (fp + fm);
}

int main() {
    const double pi = 3.14159265358979323846;
    const double G = 6.67430e-11, c = 299792458.0, h = 6.62607015e-34;
    const double hbar = h / (2.0 * pi), kB = 1.380649e-23;
    const double MeV_J = 1.602176634e-13;
    const double T_CMB = 2.72548;
    const double T_QCD = 155.16 * MeV_J / kB;

    const double delta_C = pi / 7.0;
    const double b_Ch = 1.0 - std::cos(2.0 * pi / 7.0);
    const double bC = pi * pi / 98.0, aC = std::pow(pi, 5) / 369754.0;
    const double bB = pi * pi / 18.0, aB = std::pow(pi, 5) / 5346.0;
    const double PAGE = 1.0 - std::pow(2.0, -1.5);
    const double M_QCD = hbar * std::pow(c, 3) / (8.0 * pi * G * kB * T_QCD);
    const double M_CMB = hbar * std::pow(c, 3) / (8.0 * pi * G * kB * T_CMB);
    const double TH12 = hbar * std::pow(c, 3) / (8.0 * pi * G * 1e12 * kB);
    const double growth = std::sqrt(1.5);
    const double DELTA0 = 0.523004556028;
    const double B2 = -5.49670294e-2;
    const double GAPQ = DELTA0 + B2 * 0.2 * 0.2;

    struct Row { std::string name; double val; double ref; };
    Row rows[] = {
        {"delta_C = pi/7", delta_C, 0.44879895051282761},
        {"b_Ch = 1-cos(2pi/7)", b_Ch, 0.37651019814126640},
        {"bC = pi^2/98", bC, 0.10071024899070774},
        {"aC = pi^5/369754", aC, 0.0008276304915843546},
        {"bB = pi^2/18", bB, 0.54831135561607551},
        {"aB = pi^5/5346", aB, 0.057242739391186152},
        {"Page fraction", PAGE, 0.64644660940672620},
        {"M_QCD [kg]", M_QCD, 6.814006e10},
        {"M_CMB [kg]", M_CMB, 4.501595e22},
        {"T_H(1e12 kg) [K]", TH12, 1.226901e11},
        {"r_Wu(0.9, 100)", residual(0.9, 100.0), 0.899995686821},
        {"Gascheau growth sqrt(3/2)", growth, 1.22474487139158905},
        {"gap law Delta_F(0.2)", GAPQ, 0.520805874852},
        {"vortex Lagrange 3/(2pi)", 3.0 / (2.0 * std::acos(-1.0)), 0.477464829275686},
    };
    int pass = 0, n = sizeof(rows) / sizeof(rows[0]);
    for (const auto &r : rows) {
        double rel = std::fabs(r.val - r.ref) / std::fabs(r.ref);
        bool ok = rel < 1e-6;
        if (ok) pass++;
        printf("%-30s = %-20.12g %s (rel %.2e)\n", r.name.c_str(), r.val,
               ok ? "PASS" : "FAIL", rel);
    }
    printf("%d/%d checks PASS (qhb twin, C++)\n", pass, n);
    return 0;
}
