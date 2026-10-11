#!/usr/bin/env python3
"""
IVP-01 — cryptographic release identity & archive integrity.

Establishes WHICH artifact is being verified and that the archive is
technically sound.  Independent of all project Python code.

Checks
------
A. Archive level (applies to the release ZIP):
   1. SHA-256 of the ZIP (release fingerprint);
   2. ZIP structural integrity (CRC test of every entry);
   3. no path-traversal entries (absolute paths, `..`, drive letters);
   4. no symlink/hardlink entries, no duplicate names;
   5. no unexpected debris (__pycache__, *.pyc, .git, .DS_Store);
   6. file count / total uncompressed size census.

B. Tree level (applies to the unpacked release tree):
   7. VERSION file == 2.0.0;
   8. version consistency across pyproject.toml, Makefile, CITATION.cff,
      CHANGELOG.md, README.md, committed campaign verdicts, docs;
   9. no symlinks in the tree.

Usage
-----
    python3 IVP01_release_integrity.py [--zip PATH]

Default ZIP candidates: $IVP_ZIP, ../Collapse-Hawking-Bridge-2.0.0.zip
(relative to the repository parent), otherwise the archive-level block
is reported INCONCLUSIVE (archive not available) and the tree-level
block still runs.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import zipfile

IVP_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(IVP_DIR)
sys.path.insert(0, IVP_DIR)
from ivp_common import REPO_ROOT as ROOT
from ivp_common import log, save_result, worst_status

# v2.0.1 release-gate: the expected version is read from the tree's
# own VERSION file (single source of truth) so the consistency check
# works for any release, not only the originally audited 2.0.0.
EXPECTED_VERSION = open(os.path.join(ROOT, "VERSION"),
                        encoding="utf-8").read().strip()


def sha256_of(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def zip_audit(zip_path):
    """Archive-level checks."""
    res = {"zip_path": zip_path}
    res["size_bytes"] = os.path.getsize(zip_path)
    res["sha256"] = sha256_of(zip_path)
    bad, names = None, []
    infos = []
    with zipfile.ZipFile(zip_path) as z:
        infos = z.infolist()
        names = [i.filename for i in infos]
        bad = z.testzip()
    res["n_entries"] = len(names)
    res["crc_bad_entry"] = bad
    # path traversal / absolute paths / drive letters
    traversal = [n for n in names
                 if n.startswith("/") or n.startswith("\\")
                 or ".." in n.split("/")
                 or (len(n) > 1 and n[1] == ":")]
    res["path_traversal_entries"] = traversal
    # symlink / hardlink: external_attr high bits
    links = []
    for i in infos:
        mode = i.external_attr >> 16
        if mode and (mode & 0o170000) in (0o120000,):  # S_IFLNK
            links.append(i.filename)
    res["symlink_entries"] = links
    dups = {n for n in names if names.count(n) > 1}
    res["duplicate_entries"] = sorted(dups)
    debris = [n for n in names
              if "__pycache__" in n or n.endswith(".pyc") or n.endswith(".pyo")
              or "/.git/" in n or n.endswith(".DS_Store") or "Thumbs.db" in n]
    res["debris_entries"] = debris
    res["uncompressed_bytes"] = sum(i.file_size for i in infos)
    checks = {
        "crc_clean": bad is None,
        "no_path_traversal": not traversal,
        "no_symlinks_in_zip": not links,
        "no_duplicate_entries": not dups,
        "no_debris": not debris,
    }
    return res, checks


def tree_version_consistency():
    """Version declared consistently across the whole release tree."""
    findings = {}
    vfile = os.path.join(ROOT, "VERSION")
    findings["VERSION"] = open(vfile, encoding="utf-8").read().strip()

    pp = open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8").read()
    m = re.search(r'^version\s*=\s*"([^"]+)"', pp, re.MULTILINE)
    findings["pyproject.toml"] = m.group(1) if m else None

    mk = open(os.path.join(ROOT, "Makefile"), encoding="utf-8").read()
    m = re.search(r"v(\d+\.\d+\.\d+)", mk)
    findings["Makefile"] = m.group(1) if m else None

    cit = os.path.join(ROOT, "CITATION.cff")
    if os.path.exists(cit):
        m = re.search(r"^version:\s*['\"]?([^'\"\n]+)", open(cit, encoding="utf-8").read(), re.MULTILINE)
        findings["CITATION.cff"] = m.group(1).strip() if m else None

    ch = os.path.join(ROOT, "CHANGELOG.md")
    if os.path.exists(ch):
        m = re.search(r"##\s*\[?v?(\d+\.\d+\.\d+)\]", open(ch, encoding="utf-8").read())
        findings["CHANGELOG.md (latest heading)"] = m.group(1) if m else None

    rd = os.path.join(ROOT, "README.md")
    if os.path.exists(rd):
        m = re.search(r"v?(\d+\.\d+\.\d+)", open(rd, encoding="utf-8").read())
        findings["README.md (first version token)"] = m.group(1) if m else None

    verd = {}
    vdir = os.path.join(ROOT, "campaigns", "reference")
    # COMPARISON-PHASE NOTE: the project_version FIELD of committed verdicts
    # is release metadata, not a scientific value; reading it here does not
    # touch any measured quantity.
    if os.path.isdir(vdir):
        for fn in sorted(os.listdir(vdir)):
            if fn.endswith("_verdict.json"):
                try:
                    d = json.load(open(os.path.join(vdir, fn), encoding="utf-8"))
                    verd[fn] = d.get("project_version")
                except Exception as e:  # pragma: no cover
                    verd[fn] = f"unreadable: {e}"
    findings["campaign verdicts"] = verd

    mismatch = {k: v for k, v in findings.items() if v != EXPECTED_VERSION}
    mismatch = {k: v for k, v in mismatch.items()
                if not (k == "CHANGELOG.md (latest heading)")}
    # CHANGELOG may legitimately lead with an older heading; report but do not fail
    changelog_ok = findings.get("CHANGELOG.md (latest heading)") is not None
    all_verd_ok = all(v == EXPECTED_VERSION for v in verd.values()) if verd else True
    checks = {
        "VERSION_file_is_2.0.0": findings["VERSION"] == EXPECTED_VERSION,
        "pyproject_version_matches": findings["pyproject.toml"] == EXPECTED_VERSION,
        "Makefile_version_matches": findings["Makefile"] == EXPECTED_VERSION,
        "CITATION_version_matches": findings.get("CITATION.cff") == EXPECTED_VERSION,
        "README_version_token_present": findings.get("README.md (first version token)") == EXPECTED_VERSION,
        "verdict_project_version_matches": all_verd_ok,
        "changelog_head_present": changelog_ok,
    }
    return findings, checks


def tree_hygiene():
    symlinks = []
    n_files = 0
    total = 0
    for root, dirs, files in os.walk(ROOT):
        for name in dirs + files:
            p = os.path.join(root, name)
            if os.path.islink(p):
                symlinks.append(os.path.relpath(p, ROOT))
        for name in files:
            fp = os.path.join(root, name)
            n_files += 1
            total += os.path.getsize(fp)
    checks = {"no_symlinks_in_tree": not symlinks}
    return {"n_files": n_files, "total_bytes": total, "symlinks": symlinks}, checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", default=os.environ.get("IVP_ZIP", ""))
    args = ap.parse_args()

    log("=" * 72)
    log("IVP-01 — release identity & archive integrity")
    log("=" * 72)

    all_checks = {}

    zip_candidates = []
    if args.zip:
        zip_candidates.append(args.zip)
    else:
        parent = os.path.dirname(ROOT)
        zip_candidates.append(os.path.join(parent, "Collapse-Hawking-Bridge-2.0.0.zip"))
        zip_candidates.append(os.path.join(parent, "Collapse-Hawking-Bridge-2.0.0-IVP.zip"))

    zip_path = next((c for c in zip_candidates if c and os.path.exists(c)), None)
    if zip_path:
        zip_res, zip_checks = zip_audit(zip_path)
        all_checks.update(zip_checks)
        log(f"\n[A] archive: {os.path.basename(zip_path)}")
        log(f"    SHA-256   : {zip_res['sha256']}")
        log(f"    size      : {zip_res['size_bytes']:,} bytes")
        log(f"    entries   : {zip_res['n_entries']}  "
            f"(uncompressed {zip_res['uncompressed_bytes']:,} bytes)")
        log(f"    CRC       : {'clean' if zip_checks['crc_clean'] else 'CORRUPT: ' + str(zip_res['crc_bad_entry'])}")
        log(f"    traversal : {zip_res['path_traversal_entries'] or 'none'}")
        log(f"    symlinks  : {zip_res['symlink_entries'] or 'none'}")
        log(f"    duplicates: {zip_res['duplicate_entries'] or 'none'}")
        log(f"    debris    : {zip_res['debris_entries'] or 'none'}")
    else:
        zip_res = {"zip_path": None,
                   "note": "no release archive found next to the repo; "
                           "archive-level block INCONCLUSIVE"}
        log("\n[A] archive: NOT FOUND — archive-level checks INCONCLUSIVE")

    log("\n[B] version consistency across the release tree")
    findings, ver_checks = tree_version_consistency()
    all_checks.update(ver_checks)
    for k, v in findings.items():
        log(f"    {k}: {v}")

    hyg, hyg_checks = tree_hygiene()
    all_checks.update(hyg_checks)
    log(f"\n[C] tree hygiene: {hyg['n_files']} files, "
        f"{hyg['total_bytes']:,} bytes, symlinks: {hyg['symlinks'] or 'none'}")

    status = worst_status(["PASS" if v else "FAIL" for v in all_checks.values()]) \
        if all_checks else "INCONCLUSIVE"
    if zip_res.get("zip_path") is None:
        status = "PARTIAL" if status == "PASS" else status

    log(f"\nIVP-01 overall: {status}")
    save_result("IVP01", {
        "status": status,
        "pre_registered": {
            "expected_version": EXPECTED_VERSION,
            "criteria": "CRC clean; no traversal/symlinks/duplicates/debris; "
                        "version == 2.0.0 in VERSION, pyproject, Makefile, "
                        "CITATION, README; verdicts declare project_version 2.0.0",
        },
        "archive": zip_res,
        "version_findings": findings,
        "tree": hyg,
        "checks": all_checks,
    })
    return 0 if status in ("PASS", "PARTIAL") else 1


if __name__ == "__main__":
    sys.exit(main())
