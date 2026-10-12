#!/usr/bin/env python3
"""Iron-QA: static gate for the Lean scaffolds.

1. Closed-kernel registry: every kernel theorem must exist and contain no
   `sorry` before the next top-level declaration.
2. No `axiom NAME : T := body` (axioms with bodies do not compile).
3. `import Mathlib` present in both scaffolds.
4. QHB_AxiomAudit.lean must reference every registered kernel.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAIL = []

CORE = ROOT / "monolith/lean/QHB_Theorems.lean"
MATHLIB = ROOT / "monolith/lean/QHB_T19_Mathlib.lean"
AUDIT = ROOT / "monolith/lean/QHB_AxiomAudit.lean"

REGISTRY = {
    "QHB_T19_Mathlib.lean": [
        "T19_M_charpoly", "UBlock_charpoly", "SBlock_charpoly",
        "T19_M_spectrum", "T19_M_splitting", "T19_M_degenerate",
        "T19_M_variance", "T19_M_synge",
    ],
    "QHB_Theorems.lean": [
        "T14_sup_lemma", "T14_worst_case", "T16_gamma",
        "T17_gamma1_degenerate", "T17_split_quadratic",
        "T19_splitting_identity", "T19_variance_kernel",
        "T19_synge_kernel", "T20_stall_monotone", "T20_cooling_deadline",
    ],
}

def body_of(txt, name):
    m = re.search(rf"^theorem {re.escape(name)}\b.*?^", txt, re.MULTILINE | re.DOTALL)
    if not m:
        return None
    start = m.start()
    nxt = re.search(r"^(?:theorem|axiom|def|noncomputable def|structure|inductive|namespace|end) ",
                    txt[m.end():], re.MULTILINE)
    return txt[start: m.end() + (nxt.start() if nxt else len(txt))]

def check_file(path, kernels, need_import=True):
    if not path.exists():
        FAIL.append(f"missing file: {path.name}")
        return
    txt = path.read_text(encoding="utf-8")
    if need_import and "import Mathlib" not in txt:
        FAIL.append(f"{path.name}: `import Mathlib` missing")
    for k in kernels:
        b = body_of(txt, k)
        if b is None:
            FAIL.append(f"{path.name}: closed kernel `{k}` not found")
        elif "sorry" in b:
            FAIL.append(f"{path.name}: closed kernel `{k}` contains sorry")
        else:
            print(f"  [OK] {path.name} :: {k}")
    # axiom with body
    for m in re.finditer(r"^axiom\s+(\w+)\s*:.*?:=\s*\S", txt, re.MULTILINE):
        FAIL.append(f"{path.name}: axiom with body `{m.group(1)}` does not compile")
    n_sorry = len(re.findall(r"\bsorry\b", txt))
    print(f"  · {path.name}: {n_sorry} data-anchored `sorry` markers (declared pattern)")

if not AUDIT.exists():
    FAIL.append("missing file: QHB_AxiomAudit.lean")
else:
    audit = AUDIT.read_text(encoding="utf-8")
    for kernels in REGISTRY.values():
        for k in kernels:
            if f".{k}" not in audit:
                FAIL.append(f"QHB_AxiomAudit.lean: kernel `{k}` not audited")

check_file(CORE, REGISTRY["QHB_Theorems.lean"])
check_file(MATHLIB, REGISTRY["QHB_T19_Mathlib.lean"])

# audit file must not itself contain the `sorry` tactic (mentions in prose are OK)
if AUDIT.exists() and re.search(r"^\s*sorry\s*$|^\s*sorry\s+--", AUDIT.read_text(encoding="utf-8"), re.MULTILINE):
    FAIL.append("QHB_AxiomAudit.lean contains sorry")

print(f"[check_lean_kernels] {len(FAIL)} failures")
for f in FAIL:
    print("  FAIL:", f)
sys.exit(1 if FAIL else 0)
