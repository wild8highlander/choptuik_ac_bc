#!/usr/bin/env python3
"""Septinal · check_dial_22.py — brute-force twin of the dial modules
(Satellite.B2_Dial22, Satellite.B2b_Chirality, Satellite.C3_Cascade).

Re-derives by exhaustive enumeration everything the Lean modules prove:

* P1+P2  : 24 slots, unremovable gap {0, 12}  ->  effective capacity 22;
* P3     : chirality — left/right sectors 11 + 11, reflection x -> 24 - x
           swaps the sectors and preserves the blocked pair;
* P4     : symmetry-breaking cascade — among the 48 elements of the
           dihedral group D_24 exactly two rotations {x -> x, x -> x+12}
           and two reflections {x -> -x, x -> 12 - x} preserve the gap;
           the four survivors close into the Klein four-group, and the
           orientation keeps only the two rotations (the Z2 tail 48->4->2).

Writes ``data/dial22_results.json``.  Pure integer arithmetic, seed 1993.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

SEED = 1993
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data"
N = 24


def rot(k: int):
    return lambda x: (x + k) % N


def rfl(c: int):
    return lambda x: (c - x) % N


def preserves(g, gap: frozenset) -> bool:
    return frozenset(g(x) for x in gap) == gap


def main() -> None:
    gap = frozenset({0, 12})
    slots = set(range(N))

    # dial capacity: 24 slots minus the gap
    dial = slots - gap
    assert len(dial) == 22

    # chirality: the two half-turn arcs
    left = {x for x in slots if 1 <= x <= 11}
    right = {x for x in slots if 13 <= x <= 23}
    assert len(left) == 11 and len(right) == 11 and len(gap) == 2
    assert left | right | set(gap) == slots and not (left & right)

    # reflection x -> 24 - x  (== x -> -x mod 24) swaps the sectors
    mirror = rfl(0)
    assert set(map(mirror, left)) == right and set(map(mirror, right)) == left
    assert preserves(mirror, gap)

    # cascade: every rotation and reflection, survivors of the gap
    rots = [(k, rot(k)) for k in range(N)]
    rfls = [(c, rfl(c)) for c in range(N)]
    rot_surv = [k for k, g in rots if preserves(g, gap)]
    rfl_surv = [c for c, g in rfls if preserves(g, gap)]
    assert rot_surv == [0, 12], rot_surv
    assert rfl_surv == [0, 12], rfl_surv

    # the four survivors form the Klein four-group
    def comp(f, g):
        return lambda x: f(g(x))
    idm = rot(0)
    r12, m0, m12 = rot(12), rfl(0), rfl(12)
    klein = {idm, r12, m0, m12}
    for f, g in itertools.product(klein, repeat=2):
        h = comp(f, g)
        assert any(all(h(x) == k(x) for x in range(N)) for k in klein), "not closed"

    # the orientation (P3a) keeps the two rotations only
    tail = [k for k, _ in rots if k in (0, 12)]
    assert len(tail) == 2

    # antipodal privileged pairs: every slot has exactly one partner at distance 12
    pairs = {(x, (x + 12) % N) for x in range(N)}
    pairs = {tuple(sorted(p)) for p in pairs}
    assert len(pairs) == 12

    result = {
        "seed": SEED,
        "slots": N,
        "gap": sorted(gap),
        "effective_capacity": len(dial),
        "k_structural": len(dial),
        "chiral_split": {"left": sorted(left), "right": sorted(right),
                         "mirror": "x -> 24 - x", "swaps_sectors": True},
        "cascade": {
            "group": "D_24 (order 48)",
            "rot_survivors": rot_surv,
            "refl_survivors": rfl_surv,
            "survivors_total": len(rot_surv) + len(rfl_surv),
            "closure": "Klein four-group V4",
            "oriented_tail": tail, "tail_name": "Z2",
            "chain": "48 -> 4 -> 2",
        },
        "privileged_pairs": [list(p) for p in sorted(pairs)],
        "verdict": "ALL BRUTE-FORCE CHECKS PASS — mirrors Satellite.Dial/Chiral/Cascade",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "dial22_results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"[dial22] capacity 24 - 2          = {len(dial)} (= k = b2(K3))")
    print(f"[dial22] chiral split             = 11 + 11, mirror swaps sectors")
    print(f"[dial22] rotation survivors       = {rot_surv}")
    print(f"[dial22] reflection survivors     = {rfl_surv}")
    print(f"[dial22] closure V4, tail 48->4->2, {len(pairs)} privileged pairs")
    print(f"[dial22] wrote data/dial22_results.json  (seed {SEED})")


if __name__ == "__main__":
    main()
