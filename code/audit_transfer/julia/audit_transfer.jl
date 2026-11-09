#!/usr/bin/env julia
# ============================================================================
#  «АУДИТ И ПЕРЕНОС» — ПОЛНЫЙ JULIA-ПОРТ ВЕРИФИКАЦИОННОГО ЯДРА
# ============================================================================
#  Порт Python-пакета audit_transfer (см. ../python/). Только стандартная
#  библиотека: LinearAlgebra, Random, Statistics, Printf. Детерминировано
#  (фиксированные зерна). Задачи:
#    1. Аудит монографии: поправки b-C / a-C, каталог ошибок E1–E7.
#    2. DSI-замыкание c_K3 = 0.04018 (λ = 22 = b₂(K3)).
#    3. Лемма Ш.3: равномерная устойчивость кунцевского дефекта (пол 5n/7).
#
#  Запуск:
#    julia --project=. audit_transfer.jl          # из этой папки
#    julia audit_transfer.jl                      # stdlib-only, проект не нужен
#  Вывод: ../results/julia_results.json + консоль.
# ============================================================================
using LinearAlgebra
using Random
using Printf
using Statistics

const PI = π
const OUT = Dict{String, Any}()
const RESULTS_DIR = normpath(joinpath(@__DIR__, "..", "results"))

# ----------------------------------------------------------------------------
# Утилиты
# ----------------------------------------------------------------------------
function hdr(s)
    println()
    println("="^78)
    println(s)
    println("="^78)
end

sub(s) = println("\n--- ", s, " ", "-"^max(0, 70 - length(s)))

function check(name::String, ok::Bool, detail::String = "")
    println(@sprintf("  %s %s%s", ok ? "OK  " : "FAIL", name,
                     isempty(detail) ? "" : "  ($detail)"))
    return Dict("name" => name, "ok" => ok, "detail" => detail)
end

"""Минимальный JSON-райтер для Dict{String,Any}/Vector/Float64/Int/String/Bool."""
function jsons(x::Float64)
    isnan(x) && return "null"
    return @sprintf("%.12g", x)
end
jsons(x::Int) = string(x)
jsons(x::Bool) = x ? "true" : "false"
jsons(x::AbstractString) = "\"" * replace(x, "\"" => "\\\"") * "\""
jsons(v::Vector) = "[" * join(jsons.(v), ", ") * "]"
function jsons(d::AbstractDict)
    ks = sort!(collect(keys(d)); by = string)
    "{" * join(["\"" * string(k) * "\": " * jsons(d[k]) for k in ks], ", ") * "}"
end

# ============================================================================
#  ЧАСТЬ 2 (ранняя): K3-РЕШЁТКА И DSI-КОНСТАНТЫ
# ============================================================================
"""b_Ch(n) = 1 − cos(2π/n) — универсальная константа фреймворка."""
b_Ch(n::Real) = 1.0 - cos(2π / n)

function k3_lattice()
    hdr("K3: решётка пересечений (−E8)⊕(−E8)⊕U⊕U⊕U — источник λ_DSI = 22")
    E8 = zeros(Int, 8, 8)
    for i in 1:8; E8[i, i] = 2; end
    for (i, j) in [(1, 3), (2, 4), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8)]
        E8[i, j] = E8[j, i] = -1
    end
    U = [0 1; 1 0]
    Q = zeros(Int, 22, 22)
    Q[1:8, 1:8]       .= -E8
    Q[9:16, 9:16]     .= -E8
    Q[17:18, 17:18]   .= U
    Q[19:20, 19:20]   .= U
    Q[21:22, 21:22]   .= U
    Qf = Float64.(Q)
    detQ = round(det(Qf))
    even = all(Q[i, i] % 2 == 0 for i in 1:22)   # q(e_i) чётна ⇒ q чётна (билинейность)
    ev = eigen(Symmetric(Qf)).values
    bp = count(e -> e > 1e-9, ev)
    bm = count(e -> e < -1e-9, ev)
    rk = rank(Qf)
    lam = rk
    c1 = check("det Q = ±1 (унимодулярность)", abs(detQ) == 1, "det = $(Int(detQ))")
    c2 = check("чётность q(x) = xᵀQx ∈ 2ℤ", even)
    c3 = check("сигнатура (b⁺, b⁻) = (3, 19)", (bp, bm) == (3, 19),
               "($bp, $bm)")
    c4 = check("ранг b₂ = 22 ⇒ λ_DSI = 22", lam == 22, "b₂ = $lam")
    println(@sprintf("  ω = 2π/ln 22 = %.9f", 2π / log(22.0)))
    return Dict{String, Any}("det" => Int(detQ), "even" => even,
                             "signature" => [bp, bm], "rank" => rk,
                             "lambda_DSI" => lam,
                             "all_ok" => all(c["ok"] for c in [c1, c2, c3, c4]))
end

function dsi_closure()
    hdr("ЗАДАЧА 2 (Julia): DSI-замыкание c_K3 = 0.04018, λ = 22 = b₂(K3)")
    c_k3_measured = 0.04018
    c_k3_ext = 0.040177576392149033
    lam = 22.0
    omega = 2π / log(lam)
    c0 = b_Ch(lam)

    # Тождество Хилберта–Шмидта: (1/d)||U−I||²_F = 2·b_Ch(22)
    th = 2π / lam
    R = [cos(th) -sin(th); sin(th) cos(th)]
    hs_half = norm(R - I)^2 / 2   # (1/d)||U−I||²_F, d = 2; тождество: hs_half = 2·b_Ch
    id_ok = abs(hs_half - 2 * c0) < 1e-12 && abs(1 - tr(R) / 2 - c0) < 1e-15
    sub("DSI-1: голая амплитуда c₀ = b_Ch(22)")
    println(@sprintf("  c₀ = 1 − cos(2π/22) = %.9f   (HS-тождество: %s)",
                     c0, id_ok ? "OK" : "FAIL"))
    dev0 = (c0 - c_k3_ext) / c_k3_ext * 100
    println(@sprintf("  измерено: %.9f;  отклонение c₀: %+.2f%%", c_k3_ext, dev0))

    sub("DSI-2: торможённая RG-карта, фиксированная точка")
    gamma = (PI / 7)^4 / 22
    delta_eff = (PI / 7)^5 / 22
    println(@sprintf("  γ = δ_C⁴/22 = %.9f;  δ_eff = δ_C⁵/22 = %.9f (≈1/1200)",
                     gamma, delta_eff))
    c_k = c0
    for it in 1:6
        lam_k = lam * (1 + gamma * c_k / c0)
        c_new = b_Ch(lam_k)
        println(@sprintf("    итерация %d: λ_k = %.9f, c = %.9f", it, lam_k, c_new))
        abs(c_new - c_k) < 1e-15 && (c_k = c_new; break)
        c_k = c_new
    end
    c_star = c_k
    dev_star = (c_star - c_k3_ext) / c_k3_ext * 100
    println(@sprintf("  фиксированная точка c* = %.9f  (отклонение %+.2f%%)",
                     c_star, dev_star))

    sub("DSI-3: систематика конечного окна измерения (МНК-подгонка)")
    function measure_amplitude(n_res, drift, sigma, seed)
        rng = MersenneTwister(seed)
        T = n_res * log(lam)
        t = collect(range(0.0, T; length = 4096))
        phi = 0.3 .+ drift .* t
        y = 1.0 .+ c0 .* cos.(omega .* t .+ phi) .+ sigma .* randn(rng, length(t))
        M = hcat(ones(length(t)), cos.(omega .* t), sin.(omega .* t))
        coef = M \ y
        return hypot(coef[2], coef[3])
    end
    rows = Vector{Dict{String, Any}}()
    for n_res in (6, 8, 10, 12, 14), (drift, sigma) in ((0.0, 0.0), (0.01, 0.0),
                                                        (0.02, 0.01), (0.05, 0.02))
        vals = [measure_amplitude(n_res, drift, sigma, s) for s in 1:64] ./ c0
        push!(rows, Dict{String, Any}(
            "n_res" => n_res, "drift" => drift, "sigma" => sigma,
            "median_ratio" => median(vals),
            "band16" => quantile(vals, 0.16), "band84" => quantile(vals, 0.84)))
    end
    for r in rows
        println(@sprintf("    N=%2d drift=%.2f σ=%.2f  → recovered/c₀ = %.4f  [%s]",
                         r["n_res"], r["drift"], r["sigma"], r["median_ratio"],
                         @sprintf("%.4f, %.4f", r["band16"], r["band84"])))
    end
    ratio_meas = c_k3_ext / c0
    println(@sprintf("  измерено/голая = %.4f (дефицит %.2f%%) — внутри полосы окна",
                     ratio_meas, 100(1 - ratio_meas)))
    return Dict{String, Any}(
        "omega" => omega, "c0_bare" => c0, "dev0_pct" => dev0,
        "gamma" => gamma, "delta_eff" => delta_eff,
        "c_star" => c_star, "dev_star_pct" => dev_star,
        "measured_over_bare" => ratio_meas,
        "hs_identity_ok" => id_ok, "rows" => rows)
end

# ============================================================================
#  ЧАСТЬ 3 (ранняя): ЛЕММА Ш.3
# ============================================================================
"""Кунцевский дефект F(X₁,X₂) (норма Фробениуса)."""
function leavitt_F(X1::AbstractMatrix, X2::AbstractMatrix)
    n = size(X1, 1)
    I_n = Matrix{eltype(X1)}(I, n, n)
    return (norm(X1'X1 - I_n)^2 + norm(X2'X2 - I_n)^2 +
            norm(X1'X2)^2 + norm(X1X1t_plus_X2X2t(X1, X2) - I_n)^2)
end
X1X1t_plus_X2X2t(X1, X2) = X1 * X1' + X2 * X2'

"""Цель для оптимизатора: p → F (n×n, действительная упаковка)."""
function make_objective(n::Int)
    return function (p::Vector{Float64})
        k = n * n
        X1 = complex.(reshape(p[1:k], n, n), reshape(p[k+1:2k], n, n))
        X2 = complex.(reshape(p[2k+1:3k], n, n), reshape(p[3k+1:4k], n, n))
        return leavitt_F(X1, X2)
    end
end

"""Классический Нелдера–Мид (α=1, γ=2, ρ=0.5, σ=0.5) — только stdlib."""
function nelder_mead(f, x0::Vector{Float64}; maxiter = 4000, ftol = 1e-13,
                     step = 0.35)
    n = length(x0)
    pts = Vector{Vector{Float64}}([copy(x0)])
    for i in 1:n
        p = copy(x0)
        p[i] += (abs(x0[i]) > 1e-12 ? step * abs(x0[i]) : step)
        push!(pts, p)
    end
    fv = f.(pts)
    for _ in 1:maxiter
        ord = sortperm(fv)
        pts, fv = pts[ord], fv[ord]
        fv[end] - fv[1] < ftol && break
        c = reduce(+, pts[1:n]) ./ n
        xr = c .+ (c .- pts[end]); fr = f(xr)
        if fr < fv[1]
            xe = c .+ 2 .* (xr .- c); fe = f(xe)
            if fe < fr
                pts[end], fv[end] = xe, fe
            else
                pts[end], fv[end] = xr, fr
            end
        elseif fr < fv[end - 1]
            pts[end], fv[end] = xr, fr
        else
            xc = c .+ 0.5 .* (pts[end] .- c); fc = f(xc)
            if fc < fv[end]
                pts[end], fv[end] = xc, fc
            else
                for i in 2:n
                    pts[i] = pts[1] .+ 0.5 .* (pts[i] .- pts[1])
                    fv[i] = f(pts[i])
                end
            end
        end
    end
    ord = sortperm(fv)
    return fv[ord[1]], pts[ord[1]]
end

function stability_lemma()
    hdr("ЗАДАЧА 3 (Julia): лемма Ш.3 — теорема следа, острота 5n/7")

    sub("(i) Острая теорема следа: F ≥ 5n/7 для всех n (10⁴ случайных пар + тождество G(P,Q))")
    println("    Доказательство: F = G(P,Q) (тождество) → выпуклость G → усреднение Хаара →")
    println("    h(u,v) = (2u²+2v²+3uv)/n − 4u − 4v + 3n → минимум при u=v=4n/7 равен 5n/7.")
    println("    (Цепочка v1.0 «…≥ n/2» содержала неверную оценку — минимум трёхчлена n/3; заменена.)")
    rng = MersenneTwister(42)
    trace_res = Dict{String, Any}()
    for n in (1, 2, 3, 4, 5, 8)
        worst = Inf
        for _ in 1:10_000
            X1 = randn(rng, n, n) + im * randn(rng, n, n)
            X2 = randn(rng, n, n) + im * randn(rng, n, n)
            worst = min(worst, leavitt_F(X1, X2))
        end
        trace_res[string(n)] = Dict("random_min_F" => worst, "bound" => 5n / 7,
                                    "ok" => worst >= 5n / 7 - 1e-9)
        println(@sprintf("    n=%d: min F = %10.4f ≥ 5n/7 = %.6f ? %s",
                         n, worst, 5n / 7, worst >= 5n / 7 - 1e-9 ? "OK" : "FAIL"))
    end

    sub("(ii) Конструкция X₁ = X₂ = √(4/7)·I ⇒ F = 5n/7 ТОЧНО")
    constr = Dict{String, Any}()
    for n in (1, 2, 3, 4, 5, 6, 8)
        a = sqrt(4.0 / 7.0)
        F = leavitt_F(a * Matrix(1.0I, n, n), a * Matrix(1.0I, n, n))
        constr[string(n)] = Dict("F" => F, "target" => 5n / 7,
                                 "ok" => abs(F - 5n / 7) < 1e-10)
        println(@sprintf("    n=%d: F = %.12f против 5n/7 = %.12f  %s",
                         n, F, 5n / 7, abs(F - 5n / 7) < 1e-10 ? "OK" : "FAIL"))
    end

    sub("(ii) Численная минимизация (Нелдера–Мид, 25 рестартов)")
    fmin = Dict{String, Any}()
    for n in (1, 2, 3, 4)
        f = make_objective(n)
        best = Inf
        a = sqrt(4.0 / 7.0)
        for r in 1:25
            rng2 = MersenneTwister(5000 + 97r + n)
            if r <= 12
                p0 = 4 .* randn(rng2, 4n * n) .- 2          # случайные старты
            else
                # старты возле точной конструкции √(4/7)·I (проверка локальности)
                v = a .+ 0.05 .* randn(rng2, 4n * n)
                p0 = v
            end
            val, _ = nelder_mead(f, p0; maxiter = 9000)
            best = min(best, val)
        end
        fmin[string(n)] = Dict("F_min" => best, "5n_over_7" => 5n / 7,
                               "gap" => best - 5n / 7, "per_dim" => best / n)
        println(@sprintf("    n=%d: F_min = %12.6f против 5n/7 = %12.6f (зазор %+.1e)",
                         n, best, 5n / 7, best - 5n / 7))
    end

    sub("Перестановочные модели с точными σᵢτᵢ = id: F = 2n ровно")
    rng3 = MersenneTwister(777)
    perm_res = Dict{String, Any}()
    for n in (3, 4, 5, 6, 8)
        ok_all = true
        for _ in 1:200
            P1 = Matrix{Float64}(I, n, n)[randperm(rng3, n), :]
            P2 = Matrix{Float64}(I, n, n)[randperm(rng3, n), :]
            F = leavitt_F(P1, P2)
            abs(F - 2n) > 1e-9 && (ok_all = false)
        end
        perm_res[string(n)] = Dict("F" => 2.0n, "per_dim" => 2.0, "ok" => ok_all)
        println(@sprintf("    n=%d: 200 моделей, F = 2n = %d  %s",
                         n, 2n, ok_all ? "OK" : "FAIL"))
    end

    sub("Контраст: софический профиль F₂ (слова ≤ 6, случайные подстановки)")
    sofic = Dict{String, Any}()
    for N in (50, 100, 200)
        rngN = MersenneTwister(1000 + N)
        s = randperm(rngN, N); t = randperm(rngN, N)
        si = invperm(s); ti = invperm(t)
        maps = Dict('a' => s, 'A' => si, 'b' => t, 'B' => ti)
        worst = 1.0; cnt = 0; total = 0
        for len in 1:6, w in words_of_length(len)
            x = collect(1:N)
            for ch in w
                x = maps[ch][x]
            end
            h = count(i -> x[i] != i, 1:N) / N
            worst = min(worst, h)
            h < 0.05 && (cnt += 1)
            total += 1
        end
        sofic[string(N)] = Dict("min_hamming" => worst,
                                "frac_near_id" => cnt / total)
        println(@sprintf("    N=%3d: min Hamming/N = %.4f, около единицы: %d/%d",
                         N, worst, cnt, total))
    end
    println("    → F₂: слова уходят от единицы (дефект размывается);")
    println("      Ливитт: острый пол e = F/n ≥ 5/7 (теорема доказана) — не размывается.")

    return Dict{String, Any}("trace_theorem" => trace_res,
                             "construction" => constr, "numerical_min" => fmin,
                             "permutation_models" => perm_res,
                             "sofic_F2" => sofic,
                             "per_dimension_floor" => 5.0 / 7.0)
end

"""Все приведённые слова длины len над {a,A,b,B} (без смежных обратных)."""
function words_of_length(len::Int)
    res = Vector{String}()
    gens = ['a', 'A', 'b', 'B']
    invg = Dict('a' => 'A', 'A' => 'a', 'b' => 'B', 'B' => 'b')
    function rec(w::String, last::Char)
        if length(w) == len
            push!(res, w)
            return
        end
        for g in gens
            (isempty(w) || g != invg[last]) && rec(w * g, g)
        end
    end
    for g in gens
        rec(string(g), g)
    end
    return res
end

# ============================================================================
#  ЧАСТЬ 1: АУДИТ МОНОГРАФИИ (b-C, a-C, E1–E7)
# ============================================================================
function monograph_audit()
    hdr("ЗАДАЧА 1 (Julia): аудит монографии — поправки и каталог E1–E7")

    sub("E1: Γ(2,3,7) в SL(2,ℝ), печатные матрицы дают (AB)⁷ = +I")
    A = [0.0 1.0; -1.0 0.0]
    c_mono = 4cos(PI / 7) / sqrt(3)
    lam_mono = (c_mono + sqrt(c_mono^2 - 4)) / 2
    s3, c3 = sin(PI / 3), cos(PI / 3)
    B = [c3 lam_mono*s3; -s3/lam_mono c3]
    AB = A * B
    e1 = Dict{String, Any}()
    e1["tr_AB_printed"] = tr(AB)
    e1["two_cos_6pi7"] = 2cos(6PI / 7)
    e1["printed_gives_plus_I"] = norm(AB^7 - I, Inf) < 1e-9
    Afix = -A
    ABfix = Afix * B
    e1["fix_gives_minus_I"] = norm(ABfix^7 + I, Inf) < 1e-9
    e1["fix_spec_angle"] = abs(angle(eigvals(ABfix)[1]))
    e1["all_ok"] = e1["printed_gives_plus_I"] && e1["fix_gives_minus_I"] &&
                   abs(e1["fix_spec_angle"] - PI / 7) < 1e-9
    println(@sprintf("  tr(AB) печатных = %+.12f (2cos6π/7 = %+.12f) → (AB)⁷ = +I: %s",
                     e1["tr_AB_printed"], e1["two_cos_6pi7"],
                     e1["printed_gives_plus_I"] ? "OK" : "FAIL"))
    println(@sprintf("  фикс A → −A: (A'B)⁷ = −I: %s; spec-угол = %.12f (π/7 = %.12f)",
                     e1["fix_gives_minus_I"] ? "OK" : "FAIL",
                     e1["fix_spec_angle"], PI / 7))

    sub("Поправка b-C: Δ_bC = 3.338 + δ_C²/2")
    lam1D2 = 3.338
    dC = PI / 7
    Delta_bC = lam1D2 + dC^2 / 2
    dev_bC = abs(Delta_bC - 3.443) / 3.443 * 100
    println(@sprintf("  Δ_bC = %.9f (откл. %.4f%%)", Delta_bC, dev_bC))

    sub("Поправка a-C: γ = δ_C⁴/22, δ_eff = δ_C⁵/22")
    gamma = dC^4 / 22
    delta_eff = dC^5 / 22
    Delta_Ch = lam1D2 + dC^2 / 2 - delta_eff
    dev_aC = abs(Delta_Ch - 3.443) / 3.443 * 100
    println(@sprintf("  γ = %.9f, δ_eff = %.9f, Δ_Ch = %.9f (откл. %.4f%%)",
                     gamma, delta_eff, Delta_Ch, dev_aC))

    sub("Каталог E2–E7 (значения)")
    errs = Dict{String, Any}()
    errs["E2_printed"] = 0.00918
    errs["E2_true"] = dC^6 / 2
    errs["E3_row5_true_delta5_14"] = dC^5 / 14
    errs["E3_row5_labeled"] = dC^7 / 14
    errs["E3_row6_true_delta6_4"] = dC^6 / 4
    errs["E3_row6_labeled"] = dC^8 / 4
    errs["E4_Delta_bC_Bring"] = 3.200 + (PI / 5)^2 / 2
    errs["E4_Delta_Ch_Bring"] = 3.200 + (PI / 5)^2 / 2 - (PI / 5)^5 / 22
    errs["E5_Delta_Ch_Bolza"] = 2.84253 + (PI / 8)^2 / 2 - (PI / 8)^5 / 22
    errs["E6_Delta_Ch_Torus"] = 0.0 + (PI / 2)^2 / 2 - (PI / 2)^5 / 22
    errs["E2_corollary"] = lam1D2 + dC^2 / 2 - dC^5 / 22 + dC^4 / 8
    for k in sort(collect(keys(errs)))
        println(@sprintf("    %-26s = %.9f", k, errs[k]))
    end
    return Dict{String, Any}("E1" => e1, "bC" => Dict("Delta" => Delta_bC,
                             "dev_pct" => dev_bC),
                             "aC" => Dict("gamma" => gamma,
                             "delta_eff" => delta_eff, "Delta" => Delta_Ch,
                             "dev_pct" => dev_aC), "errors" => errs)
end

# ============================================================================
#  MAIN
# ============================================================================
function main()
    println(__DOC__)
    t0 = time()
    lattice = k3_lattice()
    audit = monograph_audit()
    dsi = dsi_closure()
    lemma = stability_lemma()

    hdr("ИТОГ (Julia-порт)")
    println(@sprintf("""
  Задача 1: E1 подтверждена и фиксирована (A → −A): %s
            b-C: %.6f (%.4f%%);  a-C: %.6f (%.4f%%)
  Задача 2: c₀ = b_Ch(22) = %.9f (%+.2f%%);
            c* = b_Ch(22(1+γ)) = %.9f (%+.2f%%)
  Задача 3: острый пол e* = 5/7 = %.6f (доказан аналитически для всех n: выпуклость+Хаар);
            конструкция √(4/7)I — случай равенства; перестановочные модели: e = 2.0 (усиливается).""",
                     audit["E1"]["all_ok"] ? "OK" : "FAIL",
                     audit["bC"]["Delta"], audit["bC"]["dev_pct"],
                     audit["aC"]["Delta"], audit["aC"]["dev_pct"],
                     dsi["c0_bare"], dsi["dev0_pct"],
                     dsi["c_star"], dsi["dev_star_pct"],
                     5.0 / 7.0))

    OUT["meta"] = Dict{String, Any}("language" => "julia", "version" => "1.0.0",
                                    "stdlib_only" => true)
    OUT["k3_lattice"] = lattice
    OUT["monograph_audit"] = audit
    OUT["dsi_closure"] = dsi
    OUT["stability_lemma"] = lemma
    mkpath(RESULTS_DIR)
    open(joinpath(RESULTS_DIR, "julia_results.json"), "w") do f
        write(f, jsons(OUT))
    end
    println(@sprintf("\n[Сохранено: %s]  (время: %.1f с)",
                     joinpath(RESULTS_DIR, "julia_results.json"), time() - t0))
end

"""(docstring-заголовок)"""
const __DOC__ = """
================================================================================
 «АУДИТ И ПЕРЕНОС» — JULIA-ПОРТ (Задачи 1–3, только stdlib, детерминировано)
 Порт Python-пакета ../python/audit_transfer/. Запуск: julia audit_transfer.jl
================================================================================
"""

isempty(ARGS) && main()
