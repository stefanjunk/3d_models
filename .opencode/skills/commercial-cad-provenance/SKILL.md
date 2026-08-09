---
name: commercial-cad-provenance
description: Use when a commercial 3D model may include third-party CAD, libraries, standards data, downloaded STEP files, attribution, or uncertain asset licensing.
---

# Commercial CAD Provenance

## Core Rule

Do not infer asset rights from repository visibility or a repository-level
license. Validate library code, embedded data, and every imported CAD asset
separately before geometry work.

This workflow is a technical compliance gate, not legal advice.

## Allowed Production Licenses

- `MIT`, `Apache-2.0`, `BSD-2-Clause`, `BSD-3-Clause`, `CC0-1.0`
- `CC-BY-3.0` and `CC-BY-4.0` only with complete automatic attribution
- `LicenseRef-Proprietary` only for geometry owned by the project/user

Block GPL, LGPL, AGPL, Creative Commons Share-Alike, Non-Commercial,
No-Derivatives, custom/unknown licenses, and assets without file-level rights.

## Workflow

1. Create `provenance.json` from `references/provenance-schema.json`.
2. Record origin, artifact kind, exact license, source URL, version/commit, and
   SHA-256 for each external file or library.
3. For CC-BY, record title, author, license URL, and modifications.
4. Run `scripts/check_provenance.py`.
5. Continue only on `COMMERCIAL_LICENSE_PASS`.
6. Include generated `ATTRIBUTIONS.md` and maintained
   `THIRD_PARTY_NOTICES.md` with the commercial product package when applicable.

If an imported asset is blocked, select another clearly licensed asset or
create an original parametric interface/envelope from documented dimensions.
Do not copy the blocked geometry.

## Command

```bash
python3 scripts/check_provenance.py provenance.json \
  --attributions ATTRIBUTIONS.md \
  --report reports/commercial-license.json
```

## Completion Gate

`COMMERCIAL_LICENSE_PASS` means the manifest satisfies this project's
conservative allowlist. It does not prove patent clearance, trademark rights,
regulatory compliance, or the accuracy of third-party dimensions.
