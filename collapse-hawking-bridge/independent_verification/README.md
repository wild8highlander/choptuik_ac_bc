# independent_verification/

Independent verification suite (protocol **IVP-15**) for the
Collapse-Hawking Bridge release.  Fifteen standalone checks whose
source of truth lies **outside** the project's own committed results —
see [PROTOCOL.md](PROTOCOL.md) for the contract and
[RESULTS.md](RESULTS.md) for the committed audit report of the
v2.0.0-IVP run (remediated at 2.0.1; fully aligned at 2.1.0 — see RESULTS.md).

## Quick start

```bash
# full suite (~35-45 min, single core)
bash independent_verification/RUN_ALL.sh

# fast pass (skip the heavy numerical ladders)
IVP_FAST=1 bash independent_verification/RUN_ALL.sh

# verify a specific release archive with IVP-01
IVP_ZIP=/path/to/Collapse-Hawking-Bridge-2.1.0.zip \
  bash independent_verification/RUN_ALL.sh
```

Extra requirements beyond the package's own: `sympy` (IVP-06), and at
least one CPython on PATH for IVP-02 (every 3.9–3.13 found is
clean-room tested).  IVP-15 uses whatever toolchains exist (`gcc`,
`g++`, `node`; optionally `julia`, `rustc`, `go`).

## What "independent" means here

* no committed verdict or reference value is read **before** a check's
  own measurement (comparison happens only in an explicit final phase);
* all closed forms and exact solutions are re-implemented inside the
  suite;
* engine instrumentation never touches the evolution step;
* every check pre-registers its acceptance criteria and reports
  `PASS / PARTIAL / INCONCLUSIVE / FAIL` honestly — a `FAIL` is a
  first-class, documented result.

Outputs land in `results/` (one verdict JSON + log per check);
`summarize.py` rebuilds the verdict table.
