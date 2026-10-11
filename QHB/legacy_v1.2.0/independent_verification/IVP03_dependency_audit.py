"""IVP03 — dependency audit: the declared deps cover every import."""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ivp_common import ROOT, write_verdict

DECLARED = {"numpy", "scipy", "mpmath", "matplotlib", "openpyxl",
            "pytest", "sympy"}
STDLIB_OK = {"math", "os", "sys", "json", "time", "argparse", "subprocess",
             "hashlib", "ast", "collections", "itertools"}
used = set()
for dirpath, _, files in os.walk(ROOT):
    if any(x in dirpath for x in (".git", "__pycache__", "node_modules")):
        continue
    for f in files:
        if f.endswith(".py"):
            p = os.path.join(dirpath, f)
            try:
                tree = ast.parse(open(p, encoding="utf-8").read())
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    used |= {a.name.split(".")[0] for a in node.names}
                elif isinstance(node, ast.ImportFrom) and node.module \
                        and not node.level:          # skip relative imports
                    used.add(node.module.split(".")[0])
local = {"qhb", "engine", "scripts", "campaigns", "tests",
         "independent_verification", "figstyle", "workbook_style",
         "make_figures", "make_animations", "make_logo", "hires_figures",
         "rebuild_data", "build_workbook", "ivp_common"}
external = {u for u in used if u not in local and u not in STDLIB_OK}
undeclared = external - DECLARED
ok = not undeclared
write_verdict("IVP03.json", {"check": "dependency audit",
                             "verdict": "PASS" if ok else "FAIL",
                             "external_used": sorted(external),
                             "undeclared": sorted(undeclared)})
print("IVP03:", "PASS" if ok else "FAIL")
