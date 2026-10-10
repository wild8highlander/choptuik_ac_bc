# Evidence Engine — the 30-claim registry

Every statement the package makes lives in `data/claims.json` with:

- **id** — stable identifier (T1–T15 theorem ledger + campaign results + audit);
- **status** — one of `exact`, `measured-law`, `honest-negative`, `hypothesis`,
  `comparison`;
- **statement** — RU and EN mirrors;
- **falsifier** — the single cheapest observation that would kill the claim;
- **budget** — five fields: statistical, systematic, model, numerical, external;
- **source** — campaign and table pointers.

Statuses (v1.3.0): exact ×7, measured-law ×12, honest-negative ×9,
hypothesis ×1, comparison ×1.

Design rules:

1. A claim without a falsifier is not admitted.
2. Hypotheses are stored but never cited as results.
3. External values (Planck η_B, nugget-search bounds) are comparison-only:
   they can support consistency, never the model itself.
4. Honest negatives are first-class results: the unresolved tail (T5), the
   free three-body escape (T6), the out-of-window failure (C10-NEG), the
   absence of nondeterminism (DETERM) and the impossibility of free quarks
   (T15) are all stated as negatives.

The IVP-12 audit (12/12 PASS) is the exact-status backbone: every headline
number has an independent second derivation (symbolic, 100-digit, quadrature,
or algorithmic). See `data/audit_ivp12.json` and `docs/theory.md` §7 for the
falsification policy.
