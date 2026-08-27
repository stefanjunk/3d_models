# Functional decomposition

Decision: `AUTO_APPROVED` for the `2.0.0-draft.1` concept.

## Product bodies

- `CORE-HOUSING`: owns the 210 × 190 mm footprint, two controlled drawer bays, rear stops, intermediate shelf, top registration pattern, side texture badges and anti-tip footprint.
- `DRAWER`: one parametric source body printed twice; owns containment, 0.45 mm/side nominal clearance, front reveal, finger scoop and front texture badge.
- `TOP-SORTER`: owns the shared footprint, bottom registration sockets, six open bins and exterior texture badges.
- `FIT-COUPON`: isolates side-clearance choices without a full housing print.
- `TEXTURE-COUPON`: isolates groove pitch/depth and keeps appearance testing out of the full build.

No custom metal hardware is needed. Optional commercial feet remain outside the geometry and carry no retention or load claim.

## Interfaces and assembly

1. Print the housing on its rear wall, each drawer bottom-down and the sorter bottom-down.
2. Slide two identical drawers into the bays; the housing surfaces own the nominal clearance.
3. Place the sorter on the housing registration features; its sockets own the mating clearance.
4. Optional feet may be added only after the bed face and tip behavior are inspected.

The product remains serviceable: drawers and sorter are independently replaceable. Every manufacturing part is smaller than the configured 220 × 220 × 250 mm volume.

## Source ownership

- Exact dimensions, bodies, texture geometry and export transforms: `cad/build_compact_organizer.py` plus `model-parameters.json`.
- Product requirement truth: `design-spec.yaml`.
- Appearance intent only: concept PNG; it owns no dimensions.
- Slicer settings: `PRINT-GUIDE.md`; no exact slicer project is claimed in this draft.
