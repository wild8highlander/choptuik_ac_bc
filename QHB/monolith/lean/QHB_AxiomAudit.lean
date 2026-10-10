/-
  QHB_AxiomAudit.lean — аудит аксиом всех закрытых ядер (v2.3.0)
  ==============================================================
  Запуск:  lake env lean QHB_AxiomAudit.lean
  Критерий CI: строка `sorryAx` НЕ должна появиться в выводе.
  Зависимости-якоря (численные данные кампаний) перечислены явно
  в основных файлах; здесь проверяется, что ЗАКРЫТЫЕ ядра на них
  не опираются.
-/
import QHB_T19_Mathlib
import QHB_Theorems

-- Mathlib-порт T19 (раздел 9; все ядра должны быть sorry-free)
#print axioms QHB.T19M.T19_M_charpoly
#print axioms QHB.T19M.UBlock_charpoly
#print axioms QHB.T19M.SBlock_charpoly
#print axioms QHB.T19M.T19_M_spectrum
#print axioms QHB.T19M.T19_M_splitting
#print axioms QHB.T19M.T19_M_degenerate
#print axioms QHB.T19M.T19_M_variance
#print axioms QHB.T19M.T19_M_synge

-- Основной каркас (закрытые ядра v1.x–v2.3.0)
#print axioms QHB.T14_sup_lemma
#print axioms QHB.T14_worst_case
#print axioms QHB.T16_gamma
#print axioms QHB.T17_gamma1_degenerate
#print axioms QHB.T17_split_quadratic
#print axioms QHB.T19_splitting_identity
#print axioms QHB.T19_variance_kernel
#print axioms QHB.T19_synge_kernel
#print axioms QHB.T20_stall_monotone
#print axioms QHB.T20_cooling_deadline
