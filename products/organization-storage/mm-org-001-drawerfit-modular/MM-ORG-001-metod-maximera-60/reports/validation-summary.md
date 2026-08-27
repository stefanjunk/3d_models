# DRAFT validation summary — 0.1.0-draft.1

Aggregate result: `REVIEW_REQUIRED`, correctly blocking print-candidate and release status.

- `37 PASS`: artifact presence/hash calculation, all sixteen module/comb/coupon mesh audits, 216 × 216 mm bed fit, and standards-structured ten-object 3MF validation.
- `3 REVIEW_REQUIRED`: exact slicer preflight; connector/comb physical fit; exact-drawer fit plus loaded-use/cycle evidence.
- Independent project checks also confirm the `512 × 491 × 50 mm` assembled envelope (within STL float tolerance), nine modules, eighteen declared bins, eight comb slots, twelve connector locations and watermark omission.
- Environment limitation: no PrusaSlicer/OrcaSlicer executable, no Python exact self-intersection/mesh-boolean backend and no physical evidence. Manifold3D reported `NoError` for every generated solid; the shared draft policy still avoids upgrading missing evidence into a release pass.

Authoritative machine-readable evidence is in `fdm-ci-draft-summary.json`, `validation-report.json`, `fdm-ci-3mf.json`, `environment.json`, `build-report.json` and `optimization-study.json`.
