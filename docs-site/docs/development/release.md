# Release Process

## Creating a Release

Releases are automated via the `release.yml` workflow:

```bash
# 1. Update version in pyproject.toml, src/__init__.py, CITATION.cff
# 2. Commit and push
git add -A && git commit -m "chore: bump version to v2.x.x"
git push origin main

# 3. Create and push tag
git tag -a v2.x.x -m "Release v2.x.x"
git push origin v2.x.x

# 4. GitHub Actions handles the rest:
#    - Build sdist + wheel
#    - Run full test suite
#    - Sign with sigstore
#    - Create GitHub Release
#    - Upload artifacts + signatures
```

## Sigstore Signing

Each release artifact is signed using [sigstore](https://sigstore.dev/),
providing verifiable proof of origin:

```bash
# Verify a release artifact
pip install sigstore
sigstore verify \
  --certificate-identity=aslan08_05@mail.ru \
  --certificate-oidc-issuer=https://github.com/login/oauth \
  choptyuk-spinor-2.0.0.tar.gz \
  --signature choptyuk-spinor-2.0.0.tar.gz.sig \
  --certificate choptyuk-spinor-2.0.0.tar.gz.cert
```

## Zenodo DOI

When a GitHub Release is created, Zenodo automatically:

1. Archives a snapshot of the repository
2. Mints a versioned DOI
3. Updates the badge in README.md

## Changelog

The changelog is maintained in [CHANGELOG.md](https://github.com/wild8highlander/choptuik_ac_bc/blob/main/CHANGELOG.md)
following [Keep a Changelog](https://keepachangelog.com/) format.
