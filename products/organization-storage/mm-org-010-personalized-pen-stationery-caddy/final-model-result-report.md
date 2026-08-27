# Draft final model result — MM-ORG-010 / 0.1.0-draft.1

## Design outcome

The fully parametric personalized stationery caddy is complete as a **DRAFT digital print candidate**. Requirements, concept, source, topology, fit-envelope logic, 3MF packaging and a local Kobra 3 Max reference-profile slice pass. The user-deferred physical tests and final watermark/release gate remain open.

## Model result

- Caddy manufacturing envelope: 150.0 x 123.3 x 128.0 mm including the front plate guides.
- Personalized plate: 136.0 x 27.0 x 2.0 mm, printed flat with 0.6 mm recessed glyphs.
- Coupon holder: 46.0 x 21.3 x 28.0 mm; coupon plate: 36.0 x 18.0 x 2.0 mm.
- Three rear stationery wells, one front small-item well and one passive angled phone position are integrated into one closed-base chassis.
- The nameplate slides from above and can be changed without reprinting the chassis.
- Embedded 5x7 glyphs support uppercase A-Z, digits, spaces, period, hyphen and ampersand. German umlauts and sharp S transliterate deterministically.
- Default `METRIMADE` pixel width is 1.825 mm; a 16-character boundary remains at 1.018 mm versus the 0.9 mm gate.
- The selected open shell reduces CAD volume by 89.89% against its full bounding block.

Previews: `renders/MM-ORG-010-digital-candidate.png` and `renders/MM-ORG-010-nameplate-detail.png`.

## Verification and print readiness

- Eight source, normalization, boundary and geometry tests pass.
- Chassis, nameplate and both coupon meshes are each one watertight, consistently wound, positive-volume component with zero boundary, nonmanifold, degenerate and duplicate faces.
- Manufacturing triangle counts are 2,546 for the chassis and 2,876 for the nameplate; coupon counts are 68 and 1,004.
- The millimetre 3MF contains exactly two watertight positive-volume mesh objects.
- Anycubic Slicer Next 1.3.9.4 successfully sliced the unchanged 3MF using bundled Kobra 3 Max 0.4 mm, 0.20 mm Standard and Anycubic PLA profiles.
- The reference slice has 640 consistent layer markers, one tool, no G-code warnings, a 25,561 s estimate and 191,527 mm3 extrusion volume.
- The full declared draft validation project is `PASS`; only the non-required physical block is `REVIEW_REQUIRED`.

## Deliverables

- Editable source: `cad/build.py`, `cad/finalize_candidate.py` and `config/model-parameters.json`.
- Neutral masters: `exports/master/`.
- Manufacturing meshes and first-print coupons: `exports/manufacturing/` and `exports/coupons/`.
- Geometry package: `exports/3mf/DRAFT-MM-ORG-010-personalized-stationery-caddy-0.1.0-draft.1.3mf`.
- Research signals, BOM, specification, concept correspondence, print guide, renders and machine-readable validation evidence are included.

## Open items and limitations

- Replace `personalization.name` and any compartment defaults, then rerun tests/build before printing.
- Print the two coupon STLs first; confirm insertion force, retention and engraved-pixel readability with the exact filament/process.
- Complete phone stability, asymmetric tall-item loading, edge/desk contact and 250 plate-cycle tests.
- The retained G-code is evidence in a temporary isolated run, not a release artifact or print authorization; regenerate after confirming the actual machine and filament.
- Keep files labeled `DRAFT` until physical and release gates pass.

## Kennzeichnung

`MM-WM-001-R1` is not integrated in this draft. Exact placement, marked-part coverage, slicer layers and physical coupon remain a release blocker, not a geometry-generation blocker.

Next model action: set the requested name in `config/model-parameters.json`, rebuild, print the fit coupon pair, then print the chassis and plate in their retained orientations.
