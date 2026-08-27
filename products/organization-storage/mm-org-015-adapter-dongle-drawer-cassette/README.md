# MM-ORG-015 Adapter-and-dongle drawer cassette

Parametric passive-storage cassette for twenty small adapters, card readers, wireless receivers and dongles. Each position owns an independent body envelope, connector keep-out and clearance record. Replace the supplied generic envelopes with measurements of the intended items before production use. A separate no-brand measurement card supports coarse intake before caliper entry.

## Primary files

- Edit `config/model-parameters.json`.
- Regenerate all CAD, STL, 3MF and reports with `python cad/build.py`.
- Run the thirteen deterministic parameter tests with `python -m pytest -q tests/test_parameters.py`.
- Slice `exports/3mf/DRAFT-MM-ORG-015-cassette-and-measurement-card-0.1.0-draft.1.3mf` or use the individual STL files.
- Review `PRINT-GUIDE.md` before printing and record physical results in `physical-validation-plan.md`.

## Digital candidate status

- Cassette: 220 × 160 × 8.4 mm, twenty class-owned U-cradles, watertight, 1,532 triangles.
- Measurement card: 150 × 88 × 2 mm, watertight, 556 triangles.
- Exact Anycubic Slicer Next preflight: PASS, 42 layers, 14,701 s estimate, no native object warnings.
- Aggregate draft validation: PASS; physical item fit, marking, connector load, drawer closure and cycling are deliberately deferred.

See `final-model-result-report.md` for hashes and evidence boundaries.

All outputs remain `DRAFT`. This product stores cool, undamaged, unpowered items only. It provides no charging, electrical, ESD, data-protection, waterproofing, impact, certified connector, child-use or universal-fit claim.
