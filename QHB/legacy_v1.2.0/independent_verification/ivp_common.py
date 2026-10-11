"""ivp_common.py — shared helpers of the IVP audit."""
import hashlib
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def write_verdict(name, payload):
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "results", name)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True)
    return out


def verdict(name):
    with open(os.path.join(ROOT, "campaigns", "reference", name),
              encoding="utf-8") as fh:
        return json.load(fh)
