// bridge.go — the Quark-Hawking Bridge twin (Go, self-test).
// Run: go run bridge.go   (source twin; verified where a toolchain exists)
package main

import (
	"fmt"
	"math"
)

func residual(alpha, x float64) float64 {
	f := func(u float64) float64 {
		if u < 1e-300 {
			return x
		}
		return -math.Expm1(-x*u) / u
	}
	fp, fm := f(1-alpha), f(1+alpha)
	return (fp - fm) / (fp + fm)
}

func main() {
	pi := math.Pi
	G, c, h := 6.67430e-11, 299792458.0, 6.62607015e-34
	hbar := h / (2 * pi)
	kB := 1.380649e-23
	MeVJ := 1.602176634e-13
	TCMB := 2.72548
	TQCD := 155.16 * MeVJ / kB

	bCh := 1 - math.Cos(2*pi/7)
	bC := math.Pi * math.Pi / 98
	aC := math.Pow(math.Pi, 5) / 369754
	PAGE := 1 - math.Pow(2, -1.5)
	MQCD := hbar * math.Pow(c, 3) / (8 * pi * G * kB * TQCD)
	MCMB := hbar * math.Pow(c, 3) / (8 * pi * G * kB * TCMB)
	TH12 := hbar * math.Pow(c, 3) / (8 * pi * G * 1e12 * kB)
	growth := math.Sqrt(1.5)
	DELTA0, B2 := 0.523004556028, -5.49670294e-2
	GAPQ := DELTA0 + B2*0.2*0.2

	rows := []struct {
		name    string
		val     float64
		ref     float64
	}{
		{"delta_C = pi/7", pi / 7, 0.44879895051282761},
		{"b_Ch = 1-cos(2pi/7)", bCh, 0.37651019814126640},
		{"bC = pi^2/98", bC, 0.10071024899070774},
		{"aC = pi^5/369754", aC, 0.0008276304915843546},
		{"Page fraction", PAGE, 0.64644660940672620},
		{"M_QCD [kg]", MQCD, 6.814006e10},
		{"M_CMB [kg]", MCMB, 4.501595e22},
		{"T_H(1e12 kg) [K]", TH12, 1.226901e11},
		{"r_Wu(0.9, 100)", residual(0.9, 100), 0.899995686821},
		{"Gascheau growth sqrt(3/2)", growth, 1.22474487139158905},
		{"gap law Delta_F(0.2)", GAPQ, 0.520805874852},
	{"vortex Lagrange 3/(2pi)", 3.0 / (2.0 * math.Pi), 0.477464829275686},
	}
	pass := 0
	for _, r := range rows {
		rel := math.Abs(r.val-r.ref) / math.Abs(r.ref)
		ok := rel < 1e-6
		if ok {
			pass++
		}
		status := "FAIL"
		if ok {
			status = "PASS"
		}
		fmt.Printf("%-30s = %-20.12g %s (rel %.2e)\n", r.name, r.val, status, rel)
	}
	fmt.Printf("%d/%d checks PASS (qhb twin, Go)\n", pass, len(rows))
}
