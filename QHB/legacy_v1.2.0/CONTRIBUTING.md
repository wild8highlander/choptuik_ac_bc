# Contributing

The discipline of the package is non-negotiable and part of its
license:

1. **Anchors are never fit targets.** No code path may be optimised
   toward gamma_Ch, the Wu anchor, T_QCD or any literature value.
2. **Machine-readable or it did not happen.** Every numerical claim
   must trace to a committed verdict file.
3. **Honest negatives are first-class results.** Do not bury them.
4. **Hypotheses are marked** — the mark travels with the number.
5. **Determinism.** The single seed is 20261010; a campaign re-run that
   changes its verdict is a bug — file it.
6. **Run the gates** before proposing a change:

```bash
make test && make validate && bash independent_verification/RUN_ALL.sh
```
