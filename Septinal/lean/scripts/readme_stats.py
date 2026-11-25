#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
readme_stats.py — статистика Lean-исходников пакета SEPTINAL для README.

Считает из файлов (ничего не набирается руками): строки, байты, объявления
(theorem / lemma / def / instance / structure …) с пространствами имён, импорты
проекта, секции `/-! … -/`, сорри-маркеры, принадлежность к корням сборки.

  python3 scripts/readme_stats.py                 #_digest в stdout
  python3 scripts/readme_stats.py --json docs/source_stats.json

Правило дома: числа в README перегенерируются этим скриптом; руками их не править.
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

LEAF = r"(theorem|lemma|def|abbrev|instance|structure|inductive|class|axiom|opaque|example)"
MODS = r"(?:private\s+|protected\s+|noncomputable\s+|unsafe\s+|partial\s+|scoped\s+)*"
DECL = re.compile(r"^(@\[[^\]]*\]\s*)*" + MODS + LEAF + r"\s+([^\s(:{\[\]>!]+)")
NS = re.compile(r"^namespace\s+([\w'.«»_]+)")
PRIVATE = re.compile(r"^(@\[[^\]]*\]\s*)*private\s")
SECTION = re.compile(r"^(?:section|mutable\s+section|noncomputable\s+section)\b")
END = re.compile(r"^end\b\s*([\w'.«»_]*)")
IMPORT = re.compile(r"^import\s+([\w'.]+)")
DOC = re.compile(r"^/--(?!-)(.*?)-/is", re.S)
SORRY = re.compile(r"(?<![\w.])sorry(?![\w])")
ADMIT = re.compile(r"(?<![\w.])(?:admit|native_decide)(?![\w])")


def strip_comments(src):
    """Вернуть (код без комментариев с сохранением строк, список блоков комментариев).

    Каждый блок: (start_line, kind, text), kind ∈ {'doc', 'module', 'block'}.
    'module' — `/-!` (заголовки секций), 'doc' — `/--` (документация объявления).
    """
    out, blocks = [], []
    i, line, n = 0, 1, len(src)
    mode = None  # None | 'line' | 'block' | 'str' | 'char' | 'rawstr'
    raw_hashes = 0
    start_line, kind, buf = 0, "", []
    while i < n:
        c = src[i]
        nxt = src[i + 1] if i + 1 < n else ""
        if mode is None:
            if c == "/" and nxt == "-":
                if src.startswith("/-!", i):
                    kind = "module"
                elif src.startswith("/--", i) and not src.startswith("/---", i):
                    kind = "doc"
                else:
                    kind = "block"
                start_line, buf, depth = line, [], 1
                i += 2
                # вложенные блоки комментариев
                while i < n and depth:
                    if src.startswith("/-", i):
                        depth += 1
                        i += 2
                    elif src.startswith("-/", i):
                        depth -= 1
                        i += 2
                    else:
                        if src[i] == "\n":
                            line += 1
                        buf.append(src[i])
                        i += 1
                blocks.append((start_line, kind, "".join(buf)))
                out.append(" ")
                continue
            if c == "-" and nxt == "-":
                while i < n and src[i] != "\n":
                    i += 1
                continue
            if c == '"':
                if src.startswith('r"', i):
                    j = i + 2
                    raw_hashes = 0
                    while j < n and src[j] == "#":
                        raw_hashes += 1
                        j += 1
                    mode = "rawstr"
                    i = j
                else:
                    mode = "str"
                out.append(c)
                i += 1
                continue
            if c == "'":
                mode = "char"
            if c == "\n":
                line += 1
            out.append(c)
            i += 1
        elif mode == "str":
            if c == "\\":
                out.append(src[i:i + 2])
                i += 2
                continue
            if c == '"':
                mode = None
            if c == "\n":
                line += 1
            out.append(c)
            i += 1
        elif mode == "rawstr":
            if c == '"' and src[i + 1:i + 1 + raw_hashes] == "#" * raw_hashes:
                out.append('"' + "#" * raw_hashes)
                i += 1 + raw_hashes
                mode = None
                continue
            if c == "\n":
                line += 1
            out.append(c)
            i += 1
        else:  # char
            if c == "\\":
                out.append(src[i:i + 2])
                i += 2
                continue
            if c == "'":
                mode = None
            out.append(c)
            i += 1
    return "".join(out), blocks


def clean_block(text):
    text = text.lstrip("!")
    lines = [re.sub(r"^\s*[║│]", "", l).strip() for l in text.strip().splitlines()]
    lines = [l for l in lines if not re.match(r"^[╔╚╠═─╡╞╧╨╤╥╥]*$", l) and l]
    return " ".join(lines)


def first_sentence(text, limit=220):
    t = clean_block(text)
    m = re.match(r"(.+?[.!?](?=\s|$))", t)
    s = m.group(1) if m else t
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def analyse(path, root):
    src = path.read_text(encoding="utf-8")
    code, blocks = strip_comments(src)
    code_lines = code.split("\n")
    raw_lines = src.split("\n")
    docs = {ln: t for ln, k, t in blocks if k == "doc"}
    stack, decls, sections, imports = [], [], [], []
    orphan_doc = None
    for idx, l in enumerate(code_lines):
        ln = idx + 1
        s = l.strip()
        m = NS.match(l)
        if m:
            stack = m.group(1).split(".")
            continue
        if END.match(l):
            name = END.match(l).group(1)
            if name:
                base = name.split(".")[-1]
                while stack and stack[-1] != base:
                    stack.pop()
                if stack:
                    stack.pop()
            elif stack:
                stack.pop()
            continue
        if SECTION.match(l):
            continue
        m = IMPORT.match(l)
        if m:
            imports.append(m.group(1))
            continue
        m = DECL.match(l)
        if m:
            kind, name = m.group(2), m.group(3)
            # подпись: от строки объявления до ':=' или ' by' на верхнем уровне
            sig_parts, sig = [], ""
            for j in range(idx, min(idx + 40, len(code_lines))):
                part = code_lines[j]
                cut = re.search(r":=|(?<=\s):(?=\s*=|\s*by)|\sby\s*$|\sby\s", part)
                if cut:
                    sig_parts.append(part[: cut.start()])
                    sig = " ".join(sig_parts)
                    break
                sig_parts.append(part)
            else:
                sig = " ".join(sig_parts)
            sig = re.sub(r"\s+", " ", sig).strip()
            doc = docs.get(idx) or docs.get(idx - 1) or ""
            if idx == 0:
                doc = blocks[0][2] if blocks and blocks[0][1] == "doc" else ""
            decls.append({
                "kind": kind, "name": ".".join(stack + [name]) if kind != "example" else "example",
                "short": name, "line": ln, "private": PRIVATE.match(l) is not None,
                "doc": first_sentence(doc) if doc else "",
                "sig": sig[:320],
            })
    for ln, k, t in blocks:
        if k == "module":
            sections.append({"line": ln, "text": clean_block(t)[:200]})
    header = ""
    if blocks and blocks[0][0] <= 12 and blocks[0][1] in ("block", "module"):
        header = clean_block(blocks[0][2])
    elif blocks and blocks[0][0] <= 12 and blocks[0][1] == "doc":
        header = first_sentence(blocks[0][2], 400)
    rel = path.relative_to(root).as_posix()
    module = rel[:-5].replace("/", ".")
    code_nostr = "\n".join(re.sub(r'"(?:[^"\\]|\\.)*"', '""', l) for l in code_lines)
    counts = {}
    for d in decls:
        counts[d["kind"]] = counts.get(d["kind"], 0) + 1
    return {
        "path": rel, "module": module, "lines": len(raw_lines) - (1 if src.endswith("\n") else 0),
        "bytes": len(src.encode("utf-8")), "sha": hashlib.sha256(src.encode()).hexdigest()[:12],
        "imports": imports, "sections": sections, "header": header,
        "decls": decls, "counts": counts,
        "sorry": len(SORRY.findall(code_nostr)), "unsafe_tactics": len(ADMIT.findall(code_nostr)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parents[1]))
    ap.add_argument("--json")
    ap.add_argument("--digest", default="full", choices=["full", "short", "none"])
    a = ap.parse_args()
    root = pathlib.Path(a.root)
    files = sorted(p for p in root.rglob("*.lean") if ".lake" not in p.parts)
    data = [analyse(p, root) for p in files]
    mods = {d["module"]: d for d in data}

    def closure(roots):
        seen, todo = set(), list(roots)
        while todo:
            m = todo.pop()
            if m in seen or m not in mods:
                continue
            seen.add(m)
            todo.extend(mods[m]["imports"])
        return seen

    targets = {
        "Choptuik (default)": closure(["Choptuik"]),
        "Satellite": closure(["Satellite"]),
        "SeptinalYM": closure(["SeptinalYM"]),
        "SeptinalYM_root (alt)": closure(["SeptinalYM_root"]),
        "SeptinalYM.Stage4d": closure(["SeptinalYM.Stage4d"]),
    }
    # что реально собирается: все перечисленные цели вместе
    targets["*all*"] = set().union(*targets.values())
    project = {"Choptuik", "Satellite", "SeptinalYM"}
    for d in data:
        d["targets"] = sorted(k for k, v in targets.items() if k != "*all*" and d["module"] in v)
        d["built"] = d["module"] in targets["*all*"]
        d["in_project"] = d["module"].split(".")[0] in project
        d["imports_project"] = [i for i in d["imports"] if i.split(".")[0] in project and i in mods]
        d["imports_mathlib"] = sum(1 for i in d["imports"] if i in mods or i.startswith(("Mathlib", "Std", "Batteries", "Aesop", "Qq", "Lean")))
        d["imports_external_missing"] = [i for i in d["imports"] if i not in mods and i.split(".")[0] not in
                                         ("Mathlib", "Std", "Batteries", "Aesop", "Qq", "Lean")]
        del d["imports_mathlib"]
        d["n_imports"] = len(d["imports"])
    # дубликаты по содержимому
    by_sha = {}
    for d in data:
        by_sha.setdefault(d["sha"], []).append(d["path"])
    for d in data:
        d["duplicates"] = [p for p in by_sha[d["sha"]] if p != d["path"]]
    # пары модулей: кто кого импортирует (для графа)
    edges = sorted({(d["module"], i) for d in data for i in d["imports_project"]})
    built = [d for d in data if d["built"]]
    tot = {
        "files": len(data),
        "files_in_targets": len(built),
        "files_orphans": len(data) - len(built),
        "lines": sum(d["lines"] for d in data),
        "lines_in_targets": sum(d["lines"] for d in built),
        "bytes": sum(d["bytes"] for d in data),
        "bytes_in_targets": sum(d["bytes"] for d in built),
        "sorry": sum(d["sorry"] for d in data),
        "sorry_in_targets": sum(d["sorry"] for d in built),
        "counts": {}, "counts_in_targets": {},
        "targets": {k: len(v) for k, v in targets.items()},
        "edges": edges,
    }
    for d in data:
        for k, v in d["counts"].items():
            tot["counts"][k] = tot["counts"].get(k, 0) + v
            if d["built"]:
                tot["counts_in_targets"][k] = tot["counts_in_targets"].get(k, 0) + v
    result = {"root": str(root), "targets": {k: sorted(v) for k, v in targets.items()},
              "files": data, "totals": tot}
    if a.json:
        out = pathlib.Path(a.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"→ {out} ({out.stat().st_size} байт)")
    t = tot
    print(f"файлов {t['files']} (в целях сборки {t['files_in_targets']}, вне {t['files_orphans']}); "
          f"строк {t['lines']} (в целях {t['lines_in_targets']}); sorry всего {t['sorry']} "
          f"(в целях {t['sorry_in_targets']})")
    print("цели:", {k: v for k, v in t["targets"].items()}, "| рёбра:", len(edges))
    print("объявления (всего):", t["counts"])
    print("объявления (в целях):", t["counts_in_targets"])
    if a.digest == "none":
        return
    for d in data:
        c = d["counts"]
        kinds = " ".join(f"{k}={v}" for k, v in sorted(c.items()) if k != "example")
        if a.digest == "short" or not d["built"]:
            print(f"\n## {d['path']}  [{d['lines']} стр.; {kinds}; sorry={d['sorry']}; цели={len(d['targets'])}"
                  f"{' ДУБЛЬ=' + ','.join(d['duplicates']) if d['duplicates'] else ''}]")
            print("   имп:", ", ".join(d["imports_project"]) or "—", f"(всего {d['n_imports']})")
            print("   заголовок:", d["header"][:300])
            for s in d["sections"]:
                print("   §", s["line"], s["text"][:120])
            continue
        print(f"\n## {d['path']}  [{d['lines']} стр.; {kinds}; sorry={d['sorry']}; цели={d['targets']}"
              f"{' ДУБЛЬ=' + ','.join(d['duplicates']) if d['duplicates'] else ''}]")
        print("   импорт(проект):", ", ".join(d["imports_project"]) or "—", "| всего импортов", d["n_imports"])
        print("   заголовок:", d["header"][:600])
        for s in d["sections"]:
            print("   §", s["line"], s["text"][:140])
        for x in d["decls"]:
            if x["kind"] == "example":
                continue
            print(f"   L{x['line']:<5} {x['kind']:<10} {x['name']}"
                  + (f"  — {x['doc'][:150]}" if x["doc"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
