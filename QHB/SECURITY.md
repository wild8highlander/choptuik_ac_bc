# Security Policy

## Scope

This is a research artifact (numerics, proofs, documents). The security-relevant
surface is small but real:

1. **Supply chain**: `requirements.txt` pins the analysis stack; CI installs it verbatim.
2. **Reproducibility integrity**: `SHA256SUMS.txt` covers the release archive;
   `tools/check_release.py` verifies it.
3. **Claim integrity**: statuses (`exact` / `measured` / `honneg`) must not be
   upgraded without a machine-verifiable JSON layer behind them.

## Reporting

Open a private security advisory (Security tab) or contact the maintainers
directly. Please include the affected artifact and, if possible, a falsifier —
a minimal command whose output contradicts the release.

## Guarantees

We do not claim cryptographic security of any artifact. What we do guarantee:
any numerical claim in the release can be re-derived from the shipped scripts
with pinned seeds, and any mismatch fails the Iron-QA tools.
