# Shower drain hair trap v3 — loose single-funnel segments

Status: **DRAFT print candidate; not physically validated and not released**.

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

The user reports that the earlier coupon worked after a 90° rotation. The exact printer, PETG product, nozzle and slicer profile are not recorded, so support-free behavior remains a slicer and physical test gate.

## Files

- `build_shower_drain_hairtrap_v3.py`: parametric CadQuery source
- `exports/master/DRAFT-SHOWER-DRAIN-HAIRTRAP-3.0.0-draft.1-segment-master.step`: editable STEP master in assembly orientation
- `exports/master/DRAFT-SHOWER-DRAIN-HAIRTRAP-3.0.0-draft.1-segment-master.stl`: high-fidelity STL master in assembly orientation
- `exports/master/DRAFT-SHOWER-DRAIN-HAIRTRAP-3.0.0-draft.1-18x-assembly-reference.step`: eighteen-part nominal assembly reference
- `exports/manufacturing/DRAFT-SHOWER-DRAIN-HAIRTRAP-3.0.0-draft.1-segment-on-end.stl`: DRAFT on-end manufacturing STL; print 18 copies after validation
- `exports/validation/DRAFT-SHOWER-DRAIN-HAIRTRAP-3.0.0-draft.1-segment-manufacturing-tessellation-reference.stl`: byte-identical validation copy of the master tessellation
- `build/parameters.json`: machine-readable parameter contract
- `build/build-report.json`: deterministic source/export evidence

Do not add a gap, connector or scaling compensation to all eighteen pieces without a measured installed-fit test; cumulative process error must be handled from physical evidence.
