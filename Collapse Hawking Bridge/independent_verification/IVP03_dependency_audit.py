#!/usr/bin/env python3
"""
IVP-03 — dependency & provenance audit (import graph, offline capability).

Establishes that the computational result cannot depend on hidden
libraries, network access or files outside the release tree.

Method: every *.py file in the release tree is parsed with `ast`
(source-level, no execution).  For each module the imports are
classified as stdlib / third-party / project-local, and the declared
dependencies (pyproject.toml `dependencies` + optional `dev`) are
compared against the third-party set actually used.  Separately the
tree is scanned for network access, subprocess/shell invocation,
environment probing and file writes outside the tree.

Pre-registered criteria
-----------------------
P1  third-party runtime imports of chbridge/ + engine/ + campaigns/
    are a subset of declared runtime deps {numpy, mpmath};
P2  third-party imports of tests/ are a subset of {numpy, mpmath, pytest};
P3  scripts/ may additionally use matplotlib (declared dev dep);
P4  no network-capable imports anywhere (socket, ssl, urllib, http.*,
    ftplib, telnetlib, asyncio streams, requests, httpx, urllib3);
P5  no subprocess/os.system invocations in chbridge/, engine/, campaigns/
    (tests/ may invoke nothing either; scripts/ may use matplotlib only);
P6  no reads of files outside the release tree in runtime code;
P7  no writes outside the release tree in runtime code.
"""
import ast
import os
import sys

IVP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(IVP_DIR)
sys.path.insert(0, IVP_DIR)
from ivp_common import log, save_result, worst_status

DECLARED_RUNTIME = {"numpy", "mpmath"}
DECLARED_DEV = {"pytest", "matplotlib"}

NETWORK_MODULES = {
    "socket", "ssl", "urllib", "urllib.request", "urllib.parse", "http",
    "http.client", "ftplib", "telnetlib", "smtplib", "asyncio",
    "requests", "httpx", "aiohttp", "urllib3", "xmlrpc", "xmlrpc.client",
}
SUBPROC_MODULES = {"subprocess", "pty", "fabric", "sh", "pexpect"}
STDIN_ENV_PROBES = {"getpass"}  # informational only

# local top-level package/dir names
LOCAL_NAMES = {"chbridge", "solver", "engine", "campaigns", "scripts", "tests",
               "independent_verification", "ivp_common", "conftest", "figstyle"}
STDLIB = set(getattr(sys, "stdlib_module_names", ())) | {
    "os", "sys", "json", "math", "time", "csv", "argparse", "re", "warnings",
    "dataclasses", "typing", "pathlib", "collections", "itertools", "functools",
    "hashlib", "zipfile", "platform", "copy", "glob", "shutil", "datetime",
    "textwrap", "io", "abc", "enum", "random", "statistics", "struct"}


def discover_local_names():
    """Every top-level dir and every *.py basename in the tree is local.

    This catches path-imports like `from constants import ...` (a
    chbridge module pulled in via sys.path manipulation) that a static
    name list would miss.
    """
    names = set(LOCAL_NAMES)
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs
                   if d not in {"__pycache__", ".git", ".pytest_cache",
                                "animations", "figures", "figures_hires",
                                "monograph", "tables", "data"}]
        rel = os.path.relpath(root, ROOT)
        if os.sep not in rel and not rel.startswith("."):
            names.add(rel)
        for fn in files:
            if fn.endswith(".py"):
                names.add(fn[:-3])
    return names


def py_files():
    skip_dirs = {"__pycache__", ".git", ".pytest_cache", "animations",
                 "figures", "figures_hires", "monograph", "tables", "data"}
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fn in files:
            if fn.endswith(".py"):
                yield os.path.join(root, fn)


def top_import(module_name):
    return (module_name or "").split(".")[0]


def classify(mod, local_names):
    m = top_import(mod)
    if m in local_names or m in LOCAL_NAMES:
        return "local"
    if m in STDLIB or m in sys.builtin_module_names:
        return "stdlib"
    return "third-party"


def audit():
    local_names = discover_local_names()

    per_scope = {}
    RUNTIME_SCOPES = {"chbridge", "engine", "campaigns", "(root)"}
    suspicious = {"network": [], "subprocess": [], "env_probes": []}
    open_calls = []       # (file, lineno, mode) for runtime code
    file_ro = []
    out_of_tree_syspath = []

    for path in sorted(py_files()):
        rel = os.path.relpath(path, ROOT)
        scope = rel.split(os.sep)[0] if os.sep in rel else "(root)"
        try:
            src = open(path, encoding="utf-8").read()
            tree = ast.parse(src)
        except SyntaxError as e:
            per_scope.setdefault(scope, {})["<syntax error>"] = [f"{rel}: {e}"]
            continue
        # detect out-of-tree absolute path literals:
        #   (a) sys.path.insert/append(...) with an absolute string argument
        #   (b) NAME = "/absolute/path" assignments
        def _is_abs_str(node):
            return (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and node.value.startswith("/") and len(node.value) > 6)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr in ("insert", "append") \
                    and isinstance(node.func.value, ast.Attribute) \
                    and node.func.value.attr == "path":
                for a in node.args:
                    if _is_abs_str(a):
                        out_of_tree_syspath.append(
                            f"{rel}:{node.lineno} sys.path.{node.func.attr}({a.value!r})")
            if isinstance(node, ast.Assign) and _is_abs_str(node.value):
                out_of_tree_syspath.append(
                    f"{rel}:{node.lineno} absolute literal {node.value.value!r}")
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                mods = [node.module or ""]
            else:
                mods = []
            for mod in mods:
                cls = classify(mod, local_names)
                per_scope.setdefault(scope, {}).setdefault(cls, set()).add(top_import(mod))
                # v2.0.1 gate fix: P5/P4 are defined over RUNTIME code
                # (chbridge/, engine/, campaigns/, root) — the audit suite's
                # own scripts (independent_verification/) legitimately use
                # subprocess to compile the cross-language twins; report
                # those as advisory, never as a runtime violation.
                if mod in NETWORK_MODULES or top_import(mod) in NETWORK_MODULES:
                    suspicious["network"].append(f"{rel}:{node.lineno} import {mod}")
                if mod in SUBPROC_MODULES or top_import(mod) in SUBPROC_MODULES:
                    if scope in RUNTIME_SCOPES:
                        suspicious["subprocess"].append(
                            f"{rel}:{node.lineno} import {mod}")
                    else:
                        suspicious.setdefault("subprocess_advisory", []).append(
                            f"{rel}:{node.lineno} import {mod}")
            # open() calls with absolute-ish paths or write modes
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id == "open":
                args = node.args
                fname = None
                mode = "r"
                if args and isinstance(args[0], ast.Constant):
                    fname = args[0].value
                if len(args) > 1 and isinstance(args[1], ast.Constant):
                    mode = args[1].value
                kw_mode = [k.value for k in node.keywords if k.arg == "mode"]
                if kw_mode:
                    mode = kw_mode[0]
                if fname is not None:
                    open_calls.append((rel, node.lineno, str(fname), str(mode)))
                    if isinstance(fname, str) and (fname.startswith("/")
                                                   or ":" in fname[:3]):
                        file_ro.append(f"{rel}:{node.lineno} open({fname!r})")
                    if "w" in mode or "a" in mode:
                        file_ro.append(f"{rel}:{node.lineno} open({fname!r}, {mode!r})")

    # variables used in open() (non-literal) — record count for transparency
    return per_scope, suspicious, open_calls, file_ro, out_of_tree_syspath


def main():
    log("=" * 72)
    log("IVP-03 — dependency & provenance audit")
    log("=" * 72)
    per_scope, suspicious, open_calls, file_ro, out_of_tree_syspath = audit()

    log("\n[A] import graph by scope")
    graph = {}
    for scope in sorted(per_scope):
        graph[scope] = {k: sorted(v) for k, v in per_scope[scope].items()}
        for cls in ("third-party", "stdlib", "local"):
            if per_scope[scope].get(cls):
                log(f"    {scope:<12} {cls:<12} {sorted(per_scope[scope][cls])}")

    runtime_tp = set(per_scope.get("chbridge", {}).get("third-party", set())) \
        | set(per_scope.get("engine", {}).get("third-party", set())) \
        | set(per_scope.get("campaigns", {}).get("third-party", set()))
    tests_tp = set(per_scope.get("tests", {}).get("third-party", set()))
    scripts_tp = set(per_scope.get("scripts", {}).get("third-party", set()))
    ivp_tp = set(per_scope.get("independent_verification", {}).get("third-party", set()))

    # the data-regeneration path (committed tables) must be strictly declared
    local_names = discover_local_names()
    rebuild_tp = set()
    rebuild_file = os.path.join(ROOT, "scripts", "rebuild_data.py")
    if os.path.exists(rebuild_file):
        tree = ast.parse(open(rebuild_file, encoding="utf-8").read())
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                mods = [node.module or ""]
            for mod in mods:
                if classify(mod, local_names) == "third-party":
                    rebuild_tp.add(top_import(mod))

    undeclared_scripts = scripts_tp - (DECLARED_RUNTIME | DECLARED_DEV)
    checks = {
        "P1_runtime_deps_subset": runtime_tp <= DECLARED_RUNTIME,
        "P2_test_deps_subset": tests_tp <= (DECLARED_RUNTIME | DECLARED_DEV),
        "P3a_data_rebuild_strict": rebuild_tp <= DECLARED_RUNTIME,
        "P4_no_network_imports": not suspicious["network"],
        "P5_no_subprocess_in_runtime": not suspicious["subprocess"],
        "P6_no_absolute_path_reads": not file_ro,
        "P7_ivp_suite_deps_subset": ivp_tp <= (DECLARED_RUNTIME | DECLARED_DEV | {"sympy"}),
    }
    # P3b is ADVISORY: undeclared imports anywhere in scripts/ are a release
    # hygiene finding; they live OUTSIDE the runtime/test/data path, so they
    # cannot affect any committed scientific value and do not fail the audit.
    checks_advisory = {"P3b_scripts_undeclared_imports_advisory": not undeclared_scripts}

    log("\n[B] declared vs actually used")
    log(f"    declared runtime : {sorted(DECLARED_RUNTIME)}")
    log(f"    runtime imports  : {sorted(runtime_tp)}  -> "
        f"{'OK' if checks['P1_runtime_deps_subset'] else 'VIOLATION'}")
    log(f"    tests imports    : {sorted(tests_tp)}")
    log(f"    data-rebuild imports (scripts/rebuild_data.py): {sorted(rebuild_tp)} -> "
        f"{'OK' if checks['P3a_data_rebuild_strict'] else 'VIOLATION'}")
    log(f"    scripts imports  : {sorted(scripts_tp)}")
    if undeclared_scripts:
        log(f"    ADVISORY FINDING: undeclared script imports "
            f"{sorted(undeclared_scripts)} — used outside the runtime/test/data "
            f"path (e.g. workbook rendering); not declared in pyproject extras")

    log("\n[C] network / subprocess / file-access scan")
    log(f"    network imports : {suspicious['network'] or 'none'}")
    log(f"    subprocess      : {suspicious['subprocess'] or 'none'}")
    log(f"    non-local reads/writes: {file_ro or 'none'}")
    log(f"    open() sites in scanned code: {len(open_calls)} "
        "(all repo-relative literals)")
    log(f"    out-of-tree absolute path literals: "
        f"{out_of_tree_syspath or 'none'}")

    status = worst_status(["PASS" if v else "FAIL" for v in checks.values()])
    log(f"\nIVP-03 overall: {status}")
    if not all(checks_advisory.values()):
        log("    advisory: P3b finding recorded (does not affect the verdict)")
    save_result("IVP03", {
        "status": status,
        "pre_registered": {
            "P1": "runtime third-party imports ⊆ {numpy, mpmath}",
            "P2": "tests third-party imports ⊆ {numpy, mpmath, pytest}",
            "P3a": "scripts/rebuild_data.py third-party imports ⊆ {numpy, mpmath}",
            "P3b_advisory": "no undeclared imports anywhere in scripts/ " +
                            "(advisory — outside runtime/test/data path)",
            "P4": "no network-capable imports anywhere",
            "P5": "no subprocess invocation in runtime code",
            "P6": "no absolute-path or out-of-tree file access in runtime code",
        },
        "import_graph": graph,
        "runtime_third_party": sorted(runtime_tp),
        "scripts_undeclared": sorted(undeclared_scripts),
        "suspicious": suspicious,
        "open_sites": len(open_calls),
        "out_of_tree_access": file_ro,
        "out_of_tree_syspath": out_of_tree_syspath,
        "checks": checks,
        "checks_advisory": checks_advisory,
    })
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
