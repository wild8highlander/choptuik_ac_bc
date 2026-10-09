#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
postprocess_pagenum.py — footer instrText format switches (WPS compat).

Per docx skill toc.md: patch Roman-section footers to `PAGE \\* ROMAN
\\* MERGEFORMAT` and Arabic-section footers to `PAGE \\* arabic \\*
MERGEFORMAT`, and strip empty <w:pgNumType/> from the cover section.

Usage: python3 postprocess_pagenum.py file.docx
"""
import re
import shutil
import sys
import tempfile
import zipfile
import os

def main(path):
    tmp = tempfile.mkdtemp()
    with zipfile.ZipFile(path) as z:
        z.extractall(tmp)

    doc_path = os.path.join(tmp, "word", "document.xml")
    with open(doc_path, encoding="utf-8") as f:
        doc = f.read()

    # 1) strip empty pgNumType (cover section)
    doc = doc.replace("<w:pgNumType/>", "")

    # find footer references per section in document.xml
    # section order: cover (no footer), front (ROMAN), body (arabic)
    sect_footers = re.findall(r'<w:footerReference w:type="default" r:id="(rId\d+)"/>', doc)
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(doc)

    # resolve rIds -> footer files
    rels_path = os.path.join(tmp, "word", "_rels", "document.xml.rels")
    with open(rels_path, encoding="utf-8") as f:
        rels = f.read()
    rid2file = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="(footer\d+\.xml)"', rels))

    fmts = ["ROMAN", "arabic"]  # first referenced footer = front matter, second = body
    for rid, fmt in zip(sect_footers, fmts):
        fname = rid2file.get(rid)
        if not fname:
            continue
        fpath = os.path.join(tmp, "word", fname)
        with open(fpath, encoding="utf-8") as f:
            fx = f.read()
        fx2 = re.sub(r'(<w:instrText[^>]*>)\s*PAGE\s*(</w:instrText>)',
                     r'\1 PAGE \\* ' + fmt + r' \\* MERGEFORMAT \2', fx)
        if fx2 != fx:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(fx2)
            print(f"patched {fname} -> {fmt}")

    # rezip
    out = path + ".tmp"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(tmp):
            for name in files:
                full = os.path.join(root, name)
                arc = os.path.relpath(full, tmp)
                z.write(full, arc)
    shutil.move(out, path)
    shutil.rmtree(tmp)
    print("done", path)

if __name__ == "__main__":
    main(sys.argv[1])
