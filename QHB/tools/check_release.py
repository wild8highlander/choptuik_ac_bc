#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Iron-QA: release consistency — VERSION / CHANGELOG / README / checksums / links."""
import re, sys, hashlib, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAIL = []

def fail(msg):
    FAIL.append(msg)
    print("  FAIL:", msg)

def note(msg):
    print("  ·", msg)

ver_file = ROOT / "VERSION"
version = ver_file.read_text().strip() if ver_file.exists() else None
note(f"VERSION = {version}")
if not version:
    fail("VERSION file missing")
if not re.fullmatch(r"\d+\.\d+\.\d+", version or ""):
    fail(f"VERSION malformed: {version!r}")

ch = (ROOT / "CHANGELOG.md")
if ch.exists():
    head_lines = ch.read_text(encoding="utf-8").splitlines()[:10]
    if version and not any(version in l for l in head_lines):
        fail(f"CHANGELOG head does not mention {version}")
    note("CHANGELOG head OK")
else:
    fail("CHANGELOG.md missing")

versioned_docs = ("README.md", "README.ru.md", "ROADMAP.md", "ROADMAP.ru.md",
                  "RESULTS.md", "RESULTS.ru.md", "CITATION.cff")
conduct_docs = ("CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md", "LICENSE")
for rd in versioned_docs + conduct_docs:
    p = ROOT / rd
    if not p.exists():
        fail(f"required release file missing: {rd}")
    elif version and rd in versioned_docs and version not in p.read_text(encoding="utf-8"):
        fail(f"{rd} does not mention {version}")
    else:
        note(f"{rd} OK")

# checksums (if shipped)
sums = ROOT / "SHA256SUMS.txt"
if sums.exists():
    ok = 0
    for line in sums.read_text().splitlines():
        if not line.strip():
            continue
        h, rel = line.split(None, 1)
        rel = rel.strip().lstrip("*").replace("QHB_Unified_" + version + "/", "")
        p = ROOT / rel
        if not p.exists():
            fail(f"checksum target missing: {rel}")
            continue
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        if got == h:
            ok += 1
        else:
            fail(f"checksum mismatch: {rel}")
    note(f"SHA256SUMS: {ok} entries verified")
else:
    note("SHA256SUMS.txt not present (built at release time)")

# README relative links resolve
for rd in ("README.md", "README.ru.md"):
    p = ROOT / rd
    if not p.exists():
        continue
    txt = p.read_text(encoding="utf-8")
    for m in re.finditer(r"\]\(([^)#]+?)(?:#[^)]*)?\)", txt):
        link = m.group(1).strip()
        if link.startswith(("http://", "https://", "mailto:")):
            continue
        target = (ROOT / link).resolve()
        if not str(target).startswith(str(ROOT)):
            continue  # outside link
        if not target.exists():
            fail(f"{rd}: broken relative link -> {link}")

# monograph files agree with VERSION
mono = ROOT / "MONOGRAPH"
if mono.exists() and version:
    for f in mono.iterdir():
        if f.is_file() and version not in f.name:
            fail(f"MONOGRAPH/{f.name} does not match version {version}")

# Lean scaffolds present
for lf in ("monolith/lean/QHB_Theorems.lean", "monolith/lean/QHB_T19_Mathlib.lean",
           "monolith/lean/lakefile.toml", "monolith/lean/lean-toolchain"):
    if not (ROOT / lf).exists():
        fail(f"Lean file missing: {lf}")
    else:
        note(f"{lf} OK")

print(f"[check_release] {len(FAIL)} failures")
sys.exit(1 if FAIL else 0)
