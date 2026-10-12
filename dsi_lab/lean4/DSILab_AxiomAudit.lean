/-
  DSILab_AxiomAudit.lean — аудит аксиом формализации DSI Lab.
  =====================================================================

  Запуск (после `lake build` в dsi_lab/lean4):

      lake env lean DSILab_AxiomAudit.lean

  Ожидаемый вывод: для каждой теоремы — список используемых аксиом.
  · Точный слой (перепись {7,3}, цепные дроби 9/224, лестница e,
    минимум масштабированных перестановок, взвешенное дерево) —
    только аксиомы типов/арифметики Lean (propext, Classical.choice,
    Quot.sound), т.е. доказуем без численных данных.
  · Теоремы A/B/C опираются на аксиомы leavittF / MatrixPosSub / rankM,
    за которыми стоят численные верификации эксперимента 7
    (results/exp7_e1_threshold.json: 24000 пар, тождество 5.9e-16).
-/

import DSILab

#print axioms DSILab.census_valence_identity
#print axioms DSILab.census_euler
#print axioms DSILab.cf_9_224_divisions
#print axioms DSILab.cf_9_224_step
#print axioms DSILab.cf_8_9_step
#print axioms DSILab.cK3_eq_cf
#print axioms DSILab.eFree_lt_one
#print axioms DSILab.tree_e_le_two
#print axioms DSILab.tree_e_ge_one
#print axioms DSILab.ladder_free_lt_tree
#print axioms DSILab.scaled_permutation_minimum
#print axioms DSILab.weighted_tree_549_49
#print axioms DSILab.corollary_D_class_closure
