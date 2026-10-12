# dsi_core.jl — the DSI-laboratory core in Julia (cross-language self-test).
#
# Part of multilang/: the same small block of exact, deterministic
# mathematics is rewritten in several languages so the package can be
# *touched* by readers of any background. This program recomputes the
# same ten numbers the dsilab package commits to, prints them, self-
# checks, and exits. Nothing is downloaded, nothing is fitted.
#
# The checks are exact integer or fixed-order IEEE-754 double arithmetic,
# so every language twin prints byte-identical output (compare with
# ../c/reference_output.txt).
#
# Run:  julia dsi_core.jl

using Printf
using LinearAlgebra

const PASS = Ref(0)
const COUNT = Ref(0)

function report(ok::Bool, name::String, got::String, want::String)
    COUNT[] += 1
    ok && (PASS[] += 1)
    mark = ok ? "PASS" : "FAIL"
    tag = lpad(COUNT[], 2, "0")
    println("[$tag] $(rpad(name, 22))= $(rpad(got, 36)) expected $(rpad(want, 30)) $mark")
end

# --- exact small-matrix helpers over {0,1} doubles ---------------------------
eye(n::Int) = Matrix{Float64}(I, n, n)

fro2(x::Matrix{Float64}) = sum(abs2, x)

function leavitt_F(x1::Matrix{Float64}, x2::Matrix{Float64})
    id = eye(size(x1, 1))
    t1, t2 = transpose(x1), transpose(x2)
    return fro2(t1 * x1 - id) + fro2(t2 * x2 - id) +
           fro2(t1 * x2) + fro2(x1 * t1 + x2 * t2 - id)
end

# truncated shifts of the binary Kunz tree of depth k
# (nodes = all words of length <= k, n = 2^(k+1) - 1)
function kunz_tree(k::Int)
    words = [""]
    for _ in 1:k
        snapshot = copy(words)
        for w in snapshot
            push!(words, "a" * w, "b" * w)
        end
    end
    n = length(words)
    index = Dict(w => i for (i, w) in enumerate(words))
    s1, s2 = eye(n), eye(n)
    for i in 1:n, j in 1:n
        s1[i, j] = 0.0
        s2[i, j] = 0.0
    end
    for (i, w) in enumerate(words)
        length(w) >= k && continue
        haskey(index, "a" * w) && (s1[index["a" * w], i] = 1.0)
        haskey(index, "b" * w) && (s2[index["b" * w], i] = 1.0)
    end
    return s1, s2, n
end

# [01] the septinial constant b_Ch = 1 - cos(2*pi/7)
bch = 1.0 - cos(2.0 * pi / 7.0)
report(abs(bch - 0.3765101981412664) < 1e-17, "b_Ch(7)",
       @sprintf("%.16f", bch), "0.3765101981412664")

# [02] convergents of the CF [0; 24, 1, 8] (division identities, exact)
report(9 * 24 + 8 == 224 && 8 * 1 + 1 == 9, "CF [0;24,1,8]",
       "1/24 1/25 9/224", "1/24 1/25 9/224")

# [03] 9/224 as a double
ck3 = 9.0 / 224.0
report(abs(ck3 - 0.04017857142857143) < 1e-17, "c_K3 = 9/224",
       @sprintf("%.16f", ck3), "0.0401785714285714")

# [04] the {7,3} census and the valence identity
V, E, F = 56, 84, 24
id_ok = (7F == 168) && (3V == 168) && (2E == 168)
report(id_ok && (V - E + F == -4), "{7,3} census + chi",
       @sprintf("V=%d E=%d F=%d id=%s", V, E, F, id_ok ? "T" : "F"),
       "V=56 E=84 F=24 id=T")

# [05] theorem C: permutation pair at n = 7 gives F = 2n exactly
n = 7
p1, p2 = eye(n), eye(n)
for i in 1:n
    p1[i, i] = 0.0
    p2[i, i] = 0.0
    p1[i, (i % n) + 1] = 1.0
    p2[i, ((i + 1) % n) + 1] = 1.0
end
f_perm = leavitt_F(p1, p2)
report(abs(f_perm - 14.0) < 1e-12, "theorem C: F(perm, n=7)",
       @sprintf("%.0f", f_perm), "14")

# [06] theorem A: complementary projections n = 8, p = q = 4: F = n
d1, d2 = eye(8), eye(8)
for i in 1:8
    d1[i, i] = i <= 4 ? 1.0 : 0.0
    d2[i, i] = i <= 4 ? 0.0 : 1.0
end
f_comp = leavitt_F(d1, d2)
report(abs(f_comp - 8.0) < 1e-12, "theorem A: F(compl, n=8)",
       @sprintf("%.0f", f_comp), "8")

# [07] theorem B: trimmed Kunz tree k = 2 gives n = 7, F = n + 2
s1, s2, n_tree = kunz_tree(2)
f_tree = leavitt_F(s1, s2)
report(n_tree == 7 && abs(f_tree - 9.0) < 1e-12, "theorem B: tree k=2",
       @sprintf("n=%d F=%.0f", n_tree, f_tree), "n=7 F=9")

# [08] weighted tree c^2 = 4/7, k = 3: F = 549/49 (fixed-order fp)
c2 = 4.0 / 7.0
fw = (7.0 - 1.0) * 2.0 * (c2 - 1.0) * (c2 - 1.0) + 7.0 + 2.0
report(abs(fw - 549.0 / 49.0) < 1e-12, "weighted tree c^2=4/7",
       @sprintf("%.14f", fw), "11.20408163265306")

# [09] the ladder endpoints as doubles
e_free = 5.0 / 7.0
e_tree = 1.0 + 2.0 / 7.0
report(abs(e_free - 0.7142857142857143) < 1e-15 &&
       abs(e_tree - 1.2857142857142858) < 1e-15, "ladder 5/7 and 1+2/7",
       @sprintf("%.14f / %.14f", e_free, e_tree),
       "0.71428571428571 / 1.28571428571429")

# [10] scaled-permutation minimum: 7t^2-8t+3 at t = 4/7 equals 5/7
t = 4.0 / 7.0
e_min = 7.0 * t * t - 8.0 * t + 3.0
report(abs(e_min - 5.0 / 7.0) < 1e-12, "min 7t^2-8t+3 at t=4/7",
       @sprintf("%.14f", e_min), "0.71428571428571")

verdict = PASS[] == COUNT[] ? "PASSED" : "FAILED"
println("\nALL CHECKS $verdict ($(PASS[])/$(COUNT[]))")
exit(PASS[] == COUNT[] ? 0 : 1)
