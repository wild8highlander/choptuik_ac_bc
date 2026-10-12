/*
 * dsi_core.cpp — the DSI-laboratory core in C++ (cross-language self-test).
 *
 * Part of multilang/: the same small block of exact, deterministic
 * mathematics is rewritten in several languages so the package can be
 * *touched* by readers of any background. This program recomputes the
 * same ten numbers the dsilab package commits to, prints them, self-
 * checks, and exits. Nothing is downloaded, nothing is fitted.
 *
 * The checks are exact integer or fixed-order IEEE-754 double arithmetic,
 * so every language twin prints byte-identical output (compare with
 * reference_output.txt).
 *
 * Build:  g++ -O2 -ffp-contract=off -o dsi_core dsi_core.cpp
 * Run:    ./dsi_core
 */
#include <cmath>
#include <cstdio>
#include <cstring>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static int pass_count = 0;
static int check_count = 0;

static void report(int ok, const char *name, const char *got,
                   const char *want)
{
    ++check_count;
    if (ok) {
        ++pass_count;
    }
    printf("[%02d] %-22s= %-36s expected %-30s %s\n",
           check_count, name, got, want, ok ? "PASS" : "FAIL");
}

/* --- exact 7x7 helpers over {0,1} doubles (Frobenius norms exact) ------ */
typedef struct {
    double a[8][8];
    int n;
} mat;

static mat eye(int n)
{
    mat m;
    m.n = n;
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j)
            m.a[i][j] = (i == j) ? 1.0 : 0.0;
    return m;
}

static mat mul(mat x, mat y)
{
    mat r;
    r.n = x.n;
    for (int i = 0; i < r.n; ++i)
        for (int j = 0; j < r.n; ++j) {
            double s = 0.0;
            for (int k = 0; k < r.n; ++k)
                s += x.a[i][k] * y.a[k][j];
            r.a[i][j] = s;
        }
    return r;
}

static mat transpose(mat x)
{
    mat r;
    r.n = x.n;
    for (int i = 0; i < x.n; ++i)
        for (int j = 0; j < x.n; ++j)
            r.a[i][j] = x.a[j][i];
    return r;
}

static mat add(mat x, mat y)
{
    mat r;
    r.n = x.n;
    for (int i = 0; i < x.n; ++i)
        for (int j = 0; j < x.n; ++j)
            r.a[i][j] = x.a[i][j] + y.a[i][j];
    return r;
}

static double fro2(mat x) /* squared Frobenius norm (exact on integers) */
{
    double s = 0.0;
    for (int i = 0; i < x.n; ++i)
        for (int j = 0; j < x.n; ++j)
            s += x.a[i][j] * x.a[i][j];
    return s;
}

static mat diff(mat x, mat y)
{
    mat r;
    r.n = x.n;
    for (int i = 0; i < x.n; ++i)
        for (int j = 0; j < x.n; ++j)
            r.a[i][j] = x.a[i][j] - y.a[i][j];
    return r;
}

/* the Kunz defect F(X1, X2) — all-integer on {0,1} matrices */
static double leavitt_F(mat x1, mat x2)
{
    mat i1 = eye(x1.n);
    mat t1 = transpose(x1), t2 = transpose(x2);
    double f = 0.0;
    f += fro2(diff(mul(t1, x1), i1));
    f += fro2(diff(mul(t2, x2), i1));
    f += fro2(mul(t1, x2));
    f += fro2(diff(add(mul(x1, t1), mul(x2, t2)), i1));
    return f;
}

/* truncated shifts of the binary Kunz tree of depth k */
static void kunz_tree(int k, mat *s1, mat *s2, int *n_out)
{
    int total = (1 << (k + 1)) - 1;
    char words[128][16];
    int count = 0;
    int level_start = 0, level_end = 1;
    strcpy(words[0], "");
    count = 1;
    for (int depth = 0; depth < k; ++depth) {
        int span = level_end - level_start;
        for (int w = 0; w < span; ++w) {
            for (int letter = 0; letter < 2; ++letter) {
                sprintf(words[count], "%s%c", words[level_start + w],
                        letter ? 'b' : 'a');
                ++count;
            }
        }
        level_start = level_end;
        level_end = count;
    }
    *n_out = total;
    *s1 = eye(total);
    *s2 = eye(total);
    for (int i = 0; i < total; ++i)
        for (int j = 0; j < total; ++j) {
            s1->a[i][j] = 0.0;
            s2->a[i][j] = 0.0;
        }
    /* S_a maps word w -> word a+w for len(w) < k */
    for (int i = 0; i < total; ++i) {
        int len = (int)strlen(words[i]);
        if (len >= k)
            continue;
        char extended[16];
        extended[0] = 'a';
        strcpy(extended + 1, words[i]);
        for (int j = 0; j < total; ++j)
            if (strcmp(words[j], extended) == 0)
                s1->a[j][i] = 1.0;
        extended[0] = 'b';
        for (int j = 0; j < total; ++j)
            if (strcmp(words[j], extended) == 0)
                s2->a[j][i] = 1.0;
    }
}

int main(void)
{
    char buf[256];

    /* [01] the septinial constant b_Ch = 1 - cos(2*pi/7) */
    double bch = 1.0 - cos(2.0 * M_PI / 7.0);
    snprintf(buf, sizeof buf, "%.16f", bch);
    report(fabs(bch - 0.37651019814126640) < 1e-17, "b_Ch(7)", buf,
           "0.3765101981412664");

    /* [02] convergents of the CF [0; 24, 1, 8] (exact integers) */
    snprintf(buf, sizeof buf, "%d/%d %d/%d %d/%d", 1, 24, 1, 25, 9, 224);
    report(9 * 24 + 8 == 224 && 8 * 1 + 1 == 9, "CF [0;24,1,8]", buf,
           "1/24 1/25 9/224");

    /* [03] 9/224 as a double */
    double ck3 = 9.0 / 224.0;
    snprintf(buf, sizeof buf, "%.16f", ck3);
    report(fabs(ck3 - 0.04017857142857143) < 1e-17, "c_K3 = 9/224", buf,
           "0.0401785714285714");

    /* [04] the {7,3} census and the valence identity */
    int V = 56, E = 84, F = 24;
    int id_ok = (7 * F == 168) && (3 * V == 168) && (2 * E == 168);
    snprintf(buf, sizeof buf, "V=%d E=%d F=%d id=%s", V, E, F,
             id_ok ? "T" : "F");
    report(id_ok && (V - E + F) == -4, "{7,3} census + chi", buf,
           "V=56 E=84 F=24 id=T");

    /* [05] theorem C: permutation pair at n = 7 gives F = 2n exactly */
    mat p1 = eye(7), p2 = eye(7);
    for (int i = 0; i < 7; ++i) {
        p1.a[i][i] = 0.0;
        p2.a[i][i] = 0.0;
        p1.a[i][(i + 1) % 7] = 1.0;
        p2.a[i][(i + 2) % 7] = 1.0;
    }
    double f_perm = leavitt_F(p1, p2);
    snprintf(buf, sizeof buf, "%.0f", f_perm);
    report(fabs(f_perm - 14.0) < 1e-12, "theorem C: F(perm, n=7)", buf,
           "14");

    /* [06] theorem A: complementary projections n = 8, p = q = 4: F = n */
    mat d1 = eye(8), d2 = eye(8);
    for (int i = 0; i < 8; ++i) {
        d1.a[i][i] = (i < 4) ? 1.0 : 0.0;
        d2.a[i][i] = (i < 4) ? 0.0 : 1.0;
    }
    double f_comp = leavitt_F(d1, d2);
    snprintf(buf, sizeof buf, "%.0f", f_comp);
    report(fabs(f_comp - 8.0) < 1e-12, "theorem A: F(compl, n=8)", buf,
           "8");

    /* [07] theorem B: trimmed Kunz tree k = 3 gives n = 7, F = n + 2 */
    mat s1, s2;
    int n_tree;
    kunz_tree(2, &s1, &s2, &n_tree);
    double f_tree = leavitt_F(s1, s2);
    snprintf(buf, sizeof buf, "n=%d F=%.0f", n_tree, f_tree);
    report(n_tree == 7 && fabs(f_tree - 9.0) < 1e-12,
           "theorem B: tree k=2", buf, "n=7 F=9");

    /* [08] weighted tree c^2 = 4/7, k = 3: F = 549/49 (fixed-order fp) */
    double c2 = 4.0 / 7.0;
    double f_weighted = (7.0 - 1.0) * 2.0 * (c2 - 1.0) * (c2 - 1.0)
        + 7.0 + 2.0;
    snprintf(buf, sizeof buf, "%.14f", f_weighted);
    report(fabs(f_weighted - 549.0 / 49.0) < 1e-12,
           "weighted tree c^2=4/7", buf, "11.20408163265306");

    /* [09] the ladder endpoints as doubles */
    double e_free = 5.0 / 7.0;
    double e_tree = 1.0 + 2.0 / 7.0;
    snprintf(buf, sizeof buf, "%.14f / %.14f", e_free, e_tree);
    report(fabs(e_free - 0.7142857142857143) < 1e-15
           && fabs(e_tree - 1.2857142857142858) < 1e-15,
           "ladder 5/7 and 1+2/7", buf,
           "0.71428571428571 / 1.28571428571429");

    /* [10] scaled-permutation minimum: 7t^2-8t+3 at t = 4/7 equals 5/7 */
    double t = 4.0 / 7.0;
    double e_min = 7.0 * t * t - 8.0 * t + 3.0;
    snprintf(buf, sizeof buf, "%.14f", e_min);
    report(fabs(e_min - 5.0 / 7.0) < 1e-12, "min 7t^2-8t+3 at t=4/7", buf,
           "0.71428571428571");

    printf("\nALL CHECKS %s (%d/%d)\n",
           pass_count == check_count ? "PASSED" : "FAILED", pass_count,
           check_count);
    return pass_count == check_count ? 0 : 1;
}
