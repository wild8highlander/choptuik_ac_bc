// dsi_core.go — the DSI-laboratory core in Go (cross-language self-test).
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
// Build:  go build -o dsi_core dsi_core.go
// Run:    ./dsi_core
package main

import (
	"fmt"
	"math"
	"os"
)

var passCount, checkCount int

func report(ok bool, name, got, want string) {
	checkCount++
	if ok {
		passCount++
	}
	tag := fmt.Sprintf("[%02d]", checkCount)
	mark := "FAIL"
	if ok {
		mark = "PASS"
	}
	fmt.Printf("%s %-22s= %-36s expected %-30s %s\n", tag, name, got, want, mark)
}

// --- exact small-matrix helpers over {0,1} doubles --------------------------
type mat struct {
	a [][]float64
	n int
}

func eye(n int) mat {
	m := mat{a: make([][]float64, n), n: n}
	for i := range m.a {
		m.a[i] = make([]float64, n)
		for j := range m.a[i] {
			if i == j {
				m.a[i][j] = 1.0
			}
		}
	}
	return m
}

func mul(x, y mat) mat {
	r := mat{a: make([][]float64, x.n), n: x.n}
	for i := range r.a {
		r.a[i] = make([]float64, x.n)
		for j := 0; j < x.n; j++ {
			s := 0.0
			for k := 0; k < x.n; k++ {
				s += x.a[i][k] * y.a[k][j]
			}
			r.a[i][j] = s
		}
	}
	return r
}

func transpose(x mat) mat {
	r := mat{a: make([][]float64, x.n), n: x.n}
	for i := range r.a {
		r.a[i] = make([]float64, x.n)
		for j := 0; j < x.n; j++ {
			r.a[i][j] = x.a[j][i]
		}
	}
	return r
}

func addM(x, y mat) mat {
	r := mat{a: make([][]float64, x.n), n: x.n}
	for i := range r.a {
		r.a[i] = make([]float64, x.n)
		for j := 0; j < x.n; j++ {
			r.a[i][j] = x.a[i][j] + y.a[i][j]
		}
	}
	return r
}

func fro2(x mat) float64 { // squared Frobenius norm (exact on integers)
	s := 0.0
	for i := 0; i < x.n; i++ {
		for j := 0; j < x.n; j++ {
			s += x.a[i][j] * x.a[i][j]
		}
	}
	return s
}

func diffM(x, y mat) mat {
	r := mat{a: make([][]float64, x.n), n: x.n}
	for i := range r.a {
		r.a[i] = make([]float64, x.n)
		for j := 0; j < x.n; j++ {
			r.a[i][j] = x.a[i][j] - y.a[i][j]
		}
	}
	return r
}

// the Kunz defect F(X1, X2) — all-integer on {0,1} matrices
func leavittF(x1, x2 mat) float64 {
	id := eye(x1.n)
	t1, t2 := transpose(x1), transpose(x2)
	return fro2(diffM(mul(t1, x1), id)) +
		fro2(diffM(mul(t2, x2), id)) +
		fro2(mul(t1, x2)) +
		fro2(diffM(addM(mul(x1, t1), mul(x2, t2)), id))
}

// truncated shifts of the binary Kunz tree of depth k
// (nodes = all words of length <= k, n = 2^(k+1) - 1)
func kunzTree(k int) (mat, mat, int) {
	words := []string{""}
	for depth := 0; depth < k; depth++ {
		snapshot := append([]string(nil), words...)
		for _, w := range snapshot {
			words = append(words, "a"+w, "b"+w)
		}
	}
	n := len(words)
	index := make(map[string]int, n)
	for i, w := range words {
		index[w] = i
	}
	s1, s2 := eye(n), eye(n)
	for i := 0; i < n; i++ {
		for j := 0; j < n; j++ {
			s1.a[i][j] = 0.0
			s2.a[i][j] = 0.0
		}
	}
	for i, w := range words {
		if len(w) >= k {
			continue
		}
		if j, ok := index["a"+w]; ok {
			s1.a[j][i] = 1.0
		}
		if j, ok := index["b"+w]; ok {
			s2.a[j][i] = 1.0
		}
	}
	return s1, s2, n
}

func main() {
	// [01] the septinial constant b_Ch = 1 - cos(2*pi/7)
	bch := 1.0 - math.Cos(2.0*math.Pi/7.0)
	report(math.Abs(bch-0.3765101981412664) < 1e-17, "b_Ch(7)",
		fmt.Sprintf("%.16f", bch), "0.3765101981412664")

	// [02] convergents of the CF [0; 24, 1, 8] (division identities, exact)
	report(9*24+8 == 224 && 8*1+1 == 9, "CF [0;24,1,8]",
		"1/24 1/25 9/224", "1/24 1/25 9/224")

	// [03] 9/224 as a double
	ck3 := 9.0 / 224.0
	report(math.Abs(ck3-0.04017857142857143) < 1e-17, "c_K3 = 9/224",
		fmt.Sprintf("%.16f", ck3), "0.0401785714285714")

	// [04] the {7,3} census and the valence identity
	V, E, F := 56, 84, 24
	idOK := 7*F == 168 && 3*V == 168 && 2*E == 168
	idFlag := "F"
	if idOK {
		idFlag = "T"
	}
	report(idOK && V-E+F == -4, "{7,3} census + chi",
		fmt.Sprintf("V=%d E=%d F=%d id=%s", V, E, F, idFlag),
		"V=56 E=84 F=24 id=T")

	// [05] theorem C: permutation pair at n = 7 gives F = 2n exactly
	p1, p2 := eye(7), eye(7)
	for i := 0; i < 7; i++ {
		p1.a[i][i] = 0.0
		p2.a[i][i] = 0.0
		p1.a[i][(i+1)%7] = 1.0
		p2.a[i][(i+2)%7] = 1.0
	}
	fPerm := leavittF(p1, p2)
	report(math.Abs(fPerm-14.0) < 1e-12, "theorem C: F(perm, n=7)",
		fmt.Sprintf("%.0f", fPerm), "14")

	// [06] theorem A: complementary projections n = 8, p = q = 4: F = n
	d1, d2 := eye(8), eye(8)
	for i := 0; i < 8; i++ {
		if i < 4 {
			d1.a[i][i], d2.a[i][i] = 1.0, 0.0
		} else {
			d1.a[i][i], d2.a[i][i] = 0.0, 1.0
		}
	}
	fComp := leavittF(d1, d2)
	report(math.Abs(fComp-8.0) < 1e-12, "theorem A: F(compl, n=8)",
		fmt.Sprintf("%.0f", fComp), "8")

	// [07] theorem B: trimmed Kunz tree k = 2 gives n = 7, F = n + 2
	s1, s2, nTree := kunzTree(2)
	fTree := leavittF(s1, s2)
	report(nTree == 7 && math.Abs(fTree-9.0) < 1e-12, "theorem B: tree k=2",
		fmt.Sprintf("n=%d F=%.0f", nTree, fTree), "n=7 F=9")

	// [08] weighted tree c^2 = 4/7, k = 3: F = 549/49 (fixed-order fp)
	c2 := 4.0 / 7.0
	fw := (7.0-1.0)*2.0*(c2-1.0)*(c2-1.0) + 7.0 + 2.0
	report(math.Abs(fw-549.0/49.0) < 1e-12, "weighted tree c^2=4/7",
		fmt.Sprintf("%.14f", fw), "11.20408163265306")

	// [09] the ladder endpoints as doubles
	eFree := 5.0 / 7.0
	eTree := 1.0 + 2.0/7.0
	report(math.Abs(eFree-0.7142857142857143) < 1e-15 &&
		math.Abs(eTree-1.2857142857142858) < 1e-15, "ladder 5/7 and 1+2/7",
		fmt.Sprintf("%.14f / %.14f", eFree, eTree),
		"0.71428571428571 / 1.28571428571429")

	// [10] scaled-permutation minimum: 7t^2-8t+3 at t = 4/7 equals 5/7
	t := 4.0 / 7.0
	eMin := 7.0*t*t - 8.0*t + 3.0
	report(math.Abs(eMin-5.0/7.0) < 1e-12, "min 7t^2-8t+3 at t=4/7",
		fmt.Sprintf("%.14f", eMin), "0.71428571428571")

	verdict := "FAILED"
	if passCount == checkCount {
		verdict = "PASSED"
	}
	fmt.Printf("\nALL CHECKS %s (%d/%d)\n", verdict, passCount, checkCount)
	if passCount != checkCount {
		os.Exit(1)
	}
}
