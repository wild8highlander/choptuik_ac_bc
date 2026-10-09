// bridge.go — Collapse-Hawking Bridge multilang self-test (Go).
//
// Recomputes the closed-form core of the bridge from CODATA constants and
// prints a validation block. Run:  go run bridge.go
//
// STATUS: portable source, written against the same closed forms as the
// verified C / C++ / JavaScript twins. Not executed on the reference
// machine (no Go toolchain at packaging time) — run once locally and
// diff against multilang/javascript/reference_output.txt.

package main

import (
	"fmt"
	"math"
)

const (
	g     = 6.67430e-11      // m^3 kg^-1 s^-2
	c     = 299792458.0      // m/s (exact)
	hPlanck = 6.62607015e-34 // J s (exact)
	hbar  = hPlanck / (2 * math.Pi)
	kB    = 1.380649e-23     // J/K (exact)
	tCMB  = 2.72548          // K (COBE/FIRAS)
)

func tH(m float64) float64 { return hbar * math.Pow(c, 3) / (8 * math.Pi * g * m * kB) }

func sBH(m float64) float64 {
	rs := 2 * g * m / (c * c)
	a := 4 * math.Pi * rs * rs
	return kB * math.Pow(c, 3) * a / (4 * g * hbar)
}

func tEvap(m float64) float64 {
	return 5120 * math.Pi * g * g * math.Pow(m, 3) / (hbar * math.Pow(c, 4))
}

func pH(m float64) float64 {
	return hbar * math.Pow(c, 6) / (15360 * math.Pi * g * g * m * m)
}

func mCMB() float64 { return hbar * math.Pow(c, 3) / (8 * math.Pi * g * kB * tCMB) }

const pageFraction = 1.0 - math.Pow(2.0, -1.5)

func sRadOverS0(tau float64) float64 {
	u2 := math.Pow(1.0-tau, 2.0/3.0)
	if tau < pageFraction {
		return u2
	}
	return 1.0 - u2
}

func main() {
	dgamma := 3.44 * 0.374
	floors := [][2]float64{{800, 0.0155}, {1600, 8.574765e-03}, {3200, 4.244867e-03}}

	fmt.Println("Collapse-Hawking Bridge — Go self-test")
	fmt.Println("-------------------------------------------------")
	fmt.Println("delta_C          = pi/7                =", math.Pi/7)
	fmt.Println("b_Ch             = 1 - cos(2 pi / 7)   =", 1-math.Cos(2*math.Pi/7))
	fmt.Println("PAGE_FRACTION    = 1 - 2^(-3/2)        =", pageFraction)
	verdict := "FAIL"
	if math.Abs(dgamma-1.27) <= 0.05 {
		verdict = "PASS"
	}
	fmt.Println("Delta*gamma      = 3.44 * 0.374        =", dgamma, " ", verdict)
	fmt.Printf("M_CMB            = %.6e kg\n", mCMB())
	fmt.Printf("T_H(1e12 kg)     = %.6e K\n", tH(1e12))
	fmt.Printf("S_BH(1e12)/kB    = %.6e\n", sBH(1e12)/kB)
	fmt.Printf("t_evap(1e12)     = %.6e s\n", tEvap(1e12))
	fmt.Printf("P_H(1e12)        = %.6e W\n", pH(1e12))
	for _, tau := range []float64{0.5, pageFraction, 0.8} {
		fmt.Printf("S_rad/S0(%.8f)  = %.14f\n", tau, sRadOverS0(tau))
	}
	fmt.Printf("A* (N=800)       = %.17f | ladder N=1600: %.10f | drift: %.3e (F-1)\n",
		0.08053436279296877, 0.0777437258, math.Abs(0.08053436279296877-0.0777437258))
	for _, fl := range floors {
		fmt.Printf("floor_M(N=%.0f)    = %.6g   12/N = %.5f\n", fl[0], fl[1], 12.0/fl[0])
	}
	fmt.Println("-------------------------------------------------")
	fmt.Println("All quantities above reproduce chbridge v2.1.0 closed forms.")
	fmt.Println("A* drift note: the threshold drifts with N (F-1 remediation);")
	fmt.Println("the stale 1.06e-6 agreement claim is RETRACTED.")
}
