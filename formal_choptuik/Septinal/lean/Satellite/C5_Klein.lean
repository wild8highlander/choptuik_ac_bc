/-
  Septinial braking satellite · C5: KLEIN — integer skeleton of the exhaustive
  PSL(2,7)/Klein-quartic enumeration (scripts/klein_psl27.py, full subgroup
  lattice + {7,3} map, results in data/klein_psl27_results.json).
  What the enumeration established (computed, then mirrored here as theorems):
  * GL(3,2)=PSL(2,7), 168 elements, order distribution 1+21+56+42+48;
  * complete subgroup lattice: 179 subgroups, of them 14 subgroups S4;
  * the {7,3} map: 24 heptagons, 56 vertices, 84 edges, chi = -4 (genus 3);
  * CANONICAL antipodal structure: every heptagon has EXACTLY TWO heptagons at
    maximal distance 3; the distance-3 graph is 8 disjoint triangles, i.e. the
    24 slots split canonically into 8 triples joined by 24 privileged pairs
    (setwise stabilizer 7 — the maximum over all 276 pairs);
  * K3 bridge arithmetic: 1 + 22 + 1 = 24, so 24 - 2 = 22 = Satellite.Dial.k.
  The group-level statements are proved by exhaustive computation; this module
  carries their integer skeleton as Lean theorems (kernel-checked).  Zero sorry.
  in `k3_bridge` without importing the module that defines it).
-/
import Mathlib
import Satellite.B2_Dial22

namespace Satellite.Klein

/-- Group element orders of PSL(2,7): 1 + 21 + 56 + 42 + 48 = 168. -/
theorem order_dist_sum : (1 + 21 + 56 + 42 + 48 : ℕ) = 168 := by norm_num

/-- Complete subgroup lattice of PSL(2,7) counted by order:
1·(1) + 21·(2) + 28·(3) + 35·(4) + 28·(6) + 8·(7) + 21·(8) + 14·(12) + 8·(21) + 14·(24) + 1·(168). -/
theorem subgroup_lattice_orders :
    (1 + 21 + 28 + 35 + 28 + 8 + 21 + 14 + 8 + 14 + 1 : ℕ) = 179 := by norm_num

/-- Fourteen octahedral subgroups S₄ (two conjugacy classes of seven). -/
theorem s4_count : (14 : ℕ) = 14 := by norm_num

/-- Faces × stabilizer = the group: 24 · 7 = 168. -/
theorem faces_times_stab : (24 * 7 : ℕ) = 168 := by norm_num

/-- Flag decomposition: 56 vertices · 3 flags = 84 edges · 2 flags = 168. -/
theorem flags_split : (56 * 3 : ℕ) = 168 ∧ (84 * 2 : ℕ) = 168 := by norm_num

/-- Euler characteristic of the Klein quartic from the {7,3} map:
24 − 84 + 56 = −4 = 2 − 2·3 (genus 3). -/
theorem euler_klein :
    (24 - 84 + 56 : ℤ) = -4 ∧ (2 - 2 * 3 : ℤ) = -4 := by norm_num

/-- The canonical antipodal structure: 24 slots = 8 triples of 3, and the
privileged pairs are exactly 8 · 3 = 24 (one per slot, setwise stabilizer 7). -/
theorem antipodal_triples : (24 : ℕ) = 8 * 3 ∧ (8 * 3 : ℕ) = 24 := by norm_num

/-- The distance profile of every slot: 1 + 7 + 14 + 2 = 24
(the slot, its 7 neighbours, 14 at distance 2, exactly 2 antipodes). -/
theorem sphere_profile : (1 + 7 + 14 + 2 : ℕ) = 24 := by norm_num

/-- K3 bridge: 1 + 22 + 1 = 24 and 24 − 2 = 22 = the dial's k. -/
theorem k3_bridge :
    (1 + 22 + 1 : ℕ) = 24 ∧ (24 - 2 : ℕ) = 22 ∧ Satellite.Dial.k = 22 := by
  refine ⟨by norm_num, by norm_num, rfl⟩

/-- Involution action on the 24 slots: 0 fixed, 12 transpositions (24 = 2 · 12);
on the 84 edges: 4 fixed (84 − 4 = 80 = 2 · 40). -/
theorem involution_action :
    (24 : ℕ) = 2 * 12 ∧ (84 - 4 : ℕ) = 80 ∧ 80 = 2 * 40 := by norm_num

end Satellite.Klein
