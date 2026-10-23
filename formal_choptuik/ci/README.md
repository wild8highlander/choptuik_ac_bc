# ci/ — continuous verification templates

![ci](https://img.shields.io/badge/CI-template-8A8272?style=flat-square)
![lean](https://img.shields.io/badge/lake-build·axiom_audit-E8B44A?style=flat-square)
![python](https://img.shields.io/badge/pytest-14_tests-8FB7A4?style=flat-square)

`formal_choptuik` is a subfolder of the parent repository, so its
workflows cannot live in `.github/` of this folder.  Install step:

```bash
cp ci/lean-ci.yml <repo-root>/.github/workflows/formal-choptuik-ci.yml
```

## What the workflow enforces

| Job | Steps | Gate |
|---|---|---|
| `lean` | install elan → `lake exe cache get!` → `lake build` → axiom audit | build green; `grep -E '^\s*axiom ' lean/Choptuik/**` returns nothing outside the three standard axioms |
| `python` | pip install → `pytest tests/ -v` | 14/14 green |
| `regen` | `generate_data.py` → `git diff --exit-code data/` | committed CSVs are reproducible |

The axiom audit is the CI shadow of
[`blueprint/axiomatic_base.md`](../blueprint/axiomatic_base.md): no
project-specific axioms, ever.
