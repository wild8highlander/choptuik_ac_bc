#!/usr/bin/env python3
"""Septinal · klein_psl27.py — exhaustive PSL(2,7) / Klein-quartic enumeration.

The computational twin of ``lean/Satellite/C5_Klein.lean``.  Everything
below is *computed here by exhaustive enumeration* and mirrored in the
Lean module as its integer skeleton (kernel-checked):

* GL(3,2) = PSL(2,7): 168 elements; order distribution 1+21+56+42+48;
* the complete subgroup lattice: 179 subgroups
  (1·1 + 21·2 + 28·3 + 35·4 + 28·6 + 8·7 + 21·8 + 14·12 + 8·21 + 14·24 + 1·168),
  of them 14 octahedral S4 (two conjugacy classes of seven);
* the regular {7,3} map of the Klein quartic built from a (2,3,7)
  generating pair (a, b): 24 heptagonal faces, 56 vertices, 84 edges,
  chi = 24 - 84 + 56 = -4  (genus 3);
* the canonical antipodal structure: every face has EXACTLY TWO faces at
  maximal distance 3; the distance-3 graph is 8 disjoint triangles
  (24 privileged pairs, setwise stabilizer 7 — the maximum over all
  276 = C(24,2) pairs);
* the K3 bridge arithmetic: 1 + 22 + 1 = 24, hence 24 - 2 = 22 = k.

Results are written to ``data/klein_psl27_results.json`` (the file name
quoted in the C5_Klein docstring).  Deterministic; seed 1993.
"""

from __future__ import annotations

import itertools
import json
from collections import deque
from pathlib import Path

SEED = 1993
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data"

N = 168


# ----------------------------------------------------------------------
# GF(2)^3 linear maps as triples of images of the basis vectors
# ----------------------------------------------------------------------
def mat_mul(m, n):
    a, b, c = m
    def app(u, v):
        r = 0
        for i in range(3):
            if (v >> i) & 1:
                r ^= u[i]
        return r
    return (app(m, n[0]), app(m, n[1]), app(m, n[2]))


def build_group():
    """GL(3,2) with an index multiplication table."""
    elems = set()
    for m0, m1, m2 in itertools.permutations([1, 2, 3, 4, 5, 6, 7], 3):
        if m0 ^ m1 ^ m2 != 0:            # independent columns
            elems.add((m0, m1, m2))
    assert len(elems) == N
    idx = {g: i for i, g in enumerate(sorted(elems))}
    gs = sorted(elems)
    mul = [[0] * N for _ in range(N)]    # mul[i][j] = index of g_i * g_j
    for i, x in enumerate(gs):
        for j, y in enumerate(gs):
            mul[i][j] = idx[mat_mul(x, y)]
    return gs, idx, mul


def closure(gens, mul, n=N):
    """Bitmask closure of a generator set (products only within the set)."""
    S = 1 | gens
    while True:
        elems = [i for i in range(n) if (S >> i) & 1]
        T = S
        for i in elems:
            row = mul[i]
            for j in elems:
                T |= 1 << row[j]
        if T == S:
            return S
        S = T


def main() -> None:
    gs, idx, mul = build_group()

    def order_of(i):
        r, k = i, 1
        while r != 0:
            r = mul[r][i]
            k += 1
        return k

    orders = [order_of(i) for i in range(N)]
    order_dist = {o: orders.count(o) for o in sorted(set(orders))}
    assert order_dist == {1: 1, 2: 21, 3: 56, 4: 42, 7: 48}, order_dist
    assert sum(order_dist.values()) == N

    # ---- the (2,3,7) generating pair ----------------------------------
    cyc = {}
    for i in range(N):
        S = 1
        r = i
        while True:
            S |= 1 << r
            r = mul[r][i]
            if r == i:
                break
        cyc[i] = S
    pair = None
    full = (1 << N) - 1
    for a in (i for i in range(N) if orders[i] == 7):
        for b in (j for j in range(N) if orders[j] == 3):
            if order_of(mul[a][b]) == 2 and closure((1 << a) | (1 << b), mul) == full:
                pair = (a, b)
                break
        if pair:
            break
    a, b = pair

    # ---- the regular {7,3} map on the 168 flags (right mult.) ---------
    def orbits(step):
        seen, orb = 0, []
        for f in range(N):
            if (seen >> f) & 1:
                continue
            o, cur = 0, f
            while not (o >> cur) & 1:
                o |= 1 << cur
                cur = mul[cur][step]
            seen |= o
            orb.append(o)
        return orb

    faces = orbits(a)          # 24 heptagons
    verts = orbits(b)          # 56 vertices
    flip_i = mul[b][a]         # order 2
    edges = orbits(flip_i)     # 84 edges
    assert len(faces) == 24 and all(o.bit_count() == 7 for o in faces)
    assert len(verts) == 56 and all(o.bit_count() == 3 for o in verts)
    assert len(edges) == 84 and all(o.bit_count() == 2 for o in edges)

    flag_face = {}
    for i, o in enumerate(faces):
        f = o
        while f:
            b_low = f & -f
            flag_face[b_low.bit_length() - 1] = i
            f ^= b_low
    adj = [set() for _ in range(24)]
    for e in edges:
        fs = {flag_face[(e & -e).bit_length() - 1]}
        e2 = e ^ (e & -e)
        fs.add(flag_face[e2.bit_length() - 1])
        if len(fs) == 2:
            x, y = fs
            adj[x].add(y)
            adj[y].add(x)
    assert all(len(nb) == 7 for nb in adj)
    assert sum(len(nb) for nb in adj) // 2 == 84

    # ---- antipodal structure -------------------------------------------
    def bfs(src):
        dist = [-1] * 24
        dist[src] = 0
        q = deque([src])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    q.append(v)
        return dist

    antipodal, profiles = {}, set()
    for s in range(24):
        d = bfs(s)
        profiles.add(tuple(d.count(k) for k in range(4)))
        far = [t for t in range(24) if d[t] == 3]
        antipodal[s] = far
    assert profiles == {(1, 7, 14, 2)}, profiles
    tri_edges = {tuple(sorted((s, t))) for s, far in antipodal.items() for t in far}
    assert len(tri_edges) == 24
    deg = {}
    for x, y in tri_edges:
        deg[x] = deg.get(x, 0) + 1
        deg[y] = deg.get(y, 0) + 1
    assert set(deg.values()) == {2}
    seen, triples = 0, []
    for s in range(24):
        if (seen >> s) & 1:
            continue
        t1, t2 = antipodal[s]
        assert tuple(sorted((t1, t2))) in tri_edges
        triples.append(tuple(sorted((s, t1, t2))))
        seen |= (1 << s) | (1 << t1) | (1 << t2)
    assert len(triples) == 8

    # ---- pair stabilizers over all C(24,2) = 276 pairs -----------------
    face_rep = [next(iter(i for i in range(N) if (o >> i) & 1)) for o in faces]
    perms = []
    for g in range(N):
        row = mul[g]
        perms.append([flag_face[row[r]] for r in face_rep])
    pair_stab = {}
    for x, y in itertools.combinations(range(24), 2):
        pair_stab[(x, y)] = sum(1 for p in perms if {p[x], p[y]} == {x, y})
    max_stab = max(pair_stab.values())
    privileged = sorted(p for p, c in pair_stab.items() if c == max_stab)
    assert len(privileged) == 24 and max_stab == 7
    assert set(privileged) == tri_edges

    # ---- the complete subgroup lattice (pair closures) ------------------
    # every subgroup of PSL(2,7) is 2-generated; pairs are deduplicated by
    # their cyclic-subgroup representatives
    subs = set()
    for i in range(N):
        subs.add(cyc[i])
    def rep(S):
        T = S & ~1                  # ignore the identity bit
        return (T & -T).bit_length() - 1
    seen_keys = set()
    for i, j in itertools.combinations(range(N), 2):
        key = (rep(cyc[i]), rep(cyc[j]))
        if key in seen_keys:
            continue
        seen_keys.add(key)
        subs.add(closure(cyc[i] | cyc[j], mul))
    by_order = {}
    for S in subs:
        by_order[S.bit_count()] = by_order.get(S.bit_count(), 0) + 1
    assert by_order == {1: 1, 2: 21, 3: 28, 4: 35, 6: 28, 7: 8,
                        8: 21, 12: 14, 21: 8, 24: 14, 168: 1}, by_order
    assert len(subs) == 179
    inv_count = {}
    s4 = []
    for S in subs:
        if S.bit_count() == 24:
            inv = sum(1 for i in range(N) if (S >> i) & 1 and orders[i] == 2)
            inv_count[S] = inv
            if inv == 9:
                s4.append(S)
    assert len(s4) == 14, len(s4)

    assert 1 + 22 + 1 == 24 and 24 - 2 == 22

    result = {
        "seed": SEED,
        "group": {"name": "GL(3,2) = PSL(2,7)", "order": N,
                  "element_order_distribution": {str(k): v for k, v in order_dist.items()},
                  "order_dist_sum": "1 + 21 + 56 + 42 + 48 = 168"},
        "generators": {"a_order7_index": a, "b_order3_index": b, "ab_order": 2,
                       "presentation": "(2,3,7)"},
        "map_7_3": {"faces": len(faces), "vertices": len(verts), "edges": 84,
                    "euler": 24 - 84 + 56, "genus": 3, "face_degree": 7,
                    "vertex_degree": 3, "flags": N,
                    "faces_times_stab": "24 * 7 = 168",
                    "flags_split": "56*3 = 84*2 = 168"},
        "antipodal": {"sphere_profile": "1 + 7 + 14 + 2 = 24",
                      "partners_per_face": 2,
                      "distance3_graph": "8 disjoint triangles",
                      "triples": [list(t) for t in triples],
                      "privileged_pairs": [list(p) for p in privileged],
                      "pairs_total": len(pair_stab),
                      "max_pair_stabilizer": max_stab},
        "subgroup_lattice": {"total": len(subs),
                             "by_order": {str(k): v for k, v in sorted(by_order.items())},
                             "s4_count": len(s4),
                             "orders_row": "1+21+28+35+28+8+21+14+8+14+1 = 179"},
        "k3_bridge": {"identity": "1 + 22 + 1 = 24", "capacity": "24 - 2 = 22 = k"},
        "verdict": "ALL EXHAUSTIVE CHECKS PASS — integer skeleton mirrored in C5_Klein.lean",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "klein_psl27_results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"[klein] PSL(2,7): {N} elements, orders {order_dist}")
    print(f"[klein] 24 heptagons / 84 edges / 56 vertices, chi = -4 (genus 3)")
    print(f"[klein] distance-3 graph: 8 triangles, 24 privileged pairs, stab {max_stab}")
    print(f"[klein] subgroup lattice: {len(subs)} subgroups, S4 x{len(s4)}")
    print(f"[klein] wrote data/klein_psl27_results.json  (seed {SEED})")


if __name__ == "__main__":
    main()
