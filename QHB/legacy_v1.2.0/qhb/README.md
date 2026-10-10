# qhb — the Python core

![v1.0.0](https://img.shields.io/badge/version-1.0.0-8C6D1F) ![validate](https://img.shields.io/badge/mpmath-9%2F9_PASS-blue)

**TL;DR**

- `qhb` is the importable core: constants (Parts A/B/C), the G-model gap
  (`gap.py`), the Gascheau layer and the wall (`trio.py`), the Wu door
  (`wu.py`), the bridge mapping with BOTH contact points (`bridge.py`),
  comparison ladders (`ladder.py`) and the 50-digit verification layer
  (`validate.py`, 9/9 PASS).
- Nothing here is fitted. Literature values are anchors; machine values
  point to the verdict files they came from.

Import surface:

```python
import qhb
qhb.__version__                       # "1.0.0"
from qhb.gap import static_of_chain, floquet_gap
from qhb.wu import residual
from qhb.bridge import equal_qcd_mass, master_table
from qhb.trio import gascheau_verdict
```

Module map:

```
constants.py ──> gap.py ──> (campaigns C1, C4, C5) ──> data/qhb
     │             trio.py ──> (campaign C2)
     │             wu.py   ──> (campaign C3)
     └──> bridge.py (master table, contacts) ──> ladder.py
                    v
              validate.py (mpmath, 50 digits) — re-checks everything
```

Honesty notes: `CAMPAIGN` values mirror the committed verdicts; the
Wu anchor 0.9 is marked APPROXIMATE; the confinement mechanism is a
marked hypothesis of the package, not a derivation.
