# MM-BTH-003 — Linear Shower Drain Hair Trap

Status: **DRAFT 3.1 concept review; existing 3.0 geometry remains the last digitally validated candidate**.

Official portfolio identity: `MM-BTH-003` — **Linear Shower Drain Hair Trap**.

## Proposed 3.1 marked assembly

- 16 unchanged 52.5 mm single-funnel segments
- 1 new 105.0 mm double segment with two unchanged funnel fields
- Canonical `metriMade.com` / `MM-BTH-003 · v3.1.0-draft.1` mark recessed 0.4 mm into one inner side wall of the double segment
- Preserved installed envelope: 945 × 65 × 21 mm
- Preserved catcher count: 18

The double segment is required because the exact 80.97 × 12.8 mm canonical profile cannot fit a 52.5 × 16.8 mm single-segment inner wall at scale 1.0. The revised requirements were approved by the user on 2026-08-27; production CAD and exports remain blocked until the revision 3.1 concept is approved.

## Geometry

- Nominal installed envelope: **945.0 × 65.0 × 21.0 mm**
- Loose identical segments: **18**
- Segment size in assembly orientation: **52.5 × 65.0 × 21.0 mm**
- One centered 46.0 mm funnel per segment
- Solid end margin: **3.25 mm per end**
- Nominal length equation: `18 × 52.5 = 945.0 mm`
- Connectors: **none**

## Preserved catcher geometry

- 55 sieve holes per catcher, 990 total
- Hole diameter 2.8 mm on 4.3 mm hexagonal pitch
- Five edge-start swirl ribs and one center boss per funnel
- Gross circular hole area across all segments: approximately 6096 mm² before rib overlap

## Print orientation

`exports/manufacturing/DRAFT-SHOWER-DRAIN-HAIRTRAP-3.0.0-draft.1-segment-on-end.stl` is already rotated +90° about assembly Y and translated to the bed. Its envelope is **21.0 × 65.0 × 52.5 mm**. The original X=max U-profile end is the bed-contact cross-section.

The user reports that the earlier coupon worked after a 90° rotation. Anycubic Slicer Next 1.3.9.4 is selected for the revised candidate; the exact Kobra 3 Max unit/firmware, PETG product, nozzle identity and successful process profile are not recorded, so support-free behavior remains a slicer and physical test gate.

## Files

- `concept/DRAFT-concept-sheet-3.1.0-draft.1.png`: current revision 3.1 concept-review image; not manufacturing geometry
- `concept/CONCEPT-NOTES-3.1.0-draft.1.md`: feature correspondence, hashes, and depiction limits for the current concept
- `build_shower_drain_hairtrap_v3.py`: current revision 3.0 parametric CadQuery source; unchanged until the 3.1 concept is approved
- `exports/master/DRAFT-SHOWER-DRAIN-HAIRTRAP-3.0.0-draft.1-segment-master.step`: editable STEP master in assembly orientation
- `exports/master/DRAFT-SHOWER-DRAIN-HAIRTRAP-3.0.0-draft.1-segment-master.stl`: high-fidelity STL master in assembly orientation
- `exports/master/DRAFT-SHOWER-DRAIN-HAIRTRAP-3.0.0-draft.1-18x-assembly-reference.step`: eighteen-part nominal assembly reference
- `exports/manufacturing/DRAFT-SHOWER-DRAIN-HAIRTRAP-3.0.0-draft.1-segment-on-end.stl`: DRAFT on-end manufacturing STL; print 18 copies after validation
- `exports/validation/DRAFT-SHOWER-DRAIN-HAIRTRAP-3.0.0-draft.1-segment-manufacturing-tessellation-reference.stl`: byte-identical validation copy of the master tessellation
- `build/parameters.json`: machine-readable parameter contract
- `build/build-report.json`: deterministic source/export evidence

Do not add a gap, connector or scaling compensation to all eighteen pieces without a measured installed-fit test; cumulative process error must be handled from physical evidence.

## Existing 3.0 release status

The canonical `MM-WM-001-R1` product watermark for the superseded provisional identity `SHOWER-DRAIN-HAIRTRAP · v3.0.0-draft.1` measures 113.466 × 12.8 mm and does not fit at scale 1.0 on a 52.5 mm single-funnel segment. The existing 3.0 functional geometry remains unchanged and digitally validated; final release is blocked by the pending 3.1 concept approval, exact-slicer review, and physical installed-fit/function tests.
