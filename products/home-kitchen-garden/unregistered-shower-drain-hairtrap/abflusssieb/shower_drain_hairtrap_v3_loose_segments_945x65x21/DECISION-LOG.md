# Decision log — shower drain hair trap v3

Status: primary production candidate digitally validated; watermark, exact-slicer review, and physical tests remain open.

## 2026-08-27 — revision basis

- Use the integrated inverted-U `funnel_edge_v1_3` geometry as the proposed baseline because it contains the 46 mm funnel, edge-start swirl ribs, and the 80 mm functional test tile referenced by the user's successful coupon experience.
- Keep the installed envelope at 945 × 65 mm and make the height requirement explicitly 21 mm.
- The baseline source already has `TOTAL_HEIGHT = 21.0`; its generated functional coupon audits at 80 × 65 × 21 mm. The stale “20 mm” title and the old four-panel export structure must be replaced in v3 after approval.
- Remove all joiner keys and key slots. The pieces will be loose and will rely only on the drain channel for containment.
- Export a master in assembly orientation and a manufacturing STL rotated 90° about Y, standing on one complete U-profile end cross-section. The axis interpretation must be confirmed in the concept image before production CAD.

## Preliminary segment-count optimization

For `N` identical segments with one centered 46 mm funnel:

`segment_length = 945 / N`

`end_margin = (segment_length - 46) / 2`

The preliminary hard constraint is `end_margin >= 3.0 mm`, matching the nominal side-wall thickness and retaining a printable full-thickness top ligament at each cut end.

| Funnels / segments | Segment length | Margin per end | Decision |
|---:|---:|---:|---|
| 16 | 59.0625 mm | 6.5313 mm | Feasible, but two fewer catchers |
| 17 | 55.5882 mm | 4.7941 mm | Feasible, more conservative |
| 18 | 52.5000 mm | 3.2500 mm | Recommended maximum under the 3.0 mm constraint |
| 19 | 49.7368 mm | 1.8684 mm | Rejected; below the 3.0 mm end-ligament constraint |

Preliminary selection: **18 identical segments, 18 funnels, 52.5 mm per segment, 3.25 mm solid margin per end**. This raises the catcher count from 16 to 18 (+12.5%) while preserving the exact nominal total length because `18 × 52.5 = 945.0 mm`.

## Evidence state

- Digital baseline coupon audit: watertight, one component, positive volume, consistent winding, 80 × 65 × 21 mm.
- User observation: the coupon printed successfully when rotated 90°. Exact machine, material, nozzle, slicer, profile, and measured result are unknown and must not be inferred.
- The 18-segment selection was approved and has been produced as a digitally validated draft; it is not yet slicer- or physically validated.

## 2026-08-27 — approved production candidate

- Requirements and the concept sheet were explicitly approved by the user for revision `3.0.0-draft.1`.
- The deterministic count optimization selected 18 identical 52.5 mm segments with one 46 mm funnel and 3.25 mm solid material at each end. The adjacent 19-segment candidate was rejected because its 1.8684 mm end margin violates the approved 3.0 mm minimum.
- The generated STEP master re-imports as one valid solid. The nominal 18-part STEP reference re-imports as 18 valid, unconnected solids with a 945 × 65 × 21 mm envelope.
- Master and print-oriented meshes pass watertightness, winding, positive-volume, component-count, boundary-edge, non-manifold-edge, degenerate-face, duplicate-face, triangle-budget, file-budget, and build-volume checks.
- A coarser STL tessellation was evaluated but rejected because the exact indexed triangle-distance backend is unavailable. The nearest-vertex diagnostic is not a valid surface-error acceptance method. The selected manufacturing STL therefore uses the byte-identical master tessellation and only the approved rigid +90° Y rotation.
- The exact slicer/profile and physical installed-fit, drainage, cleaning, and hair-retention checks remain blocked. The candidate is still a draft and not a released manufacturing package.

## 2026-08-27 — watermark placement block

- Canonical asset `MM-WM-001-R1` generated the exact two-line profile `metriMade.com` / `SHOWER-DRAIN-HAIRTRAP · v3.0.0-draft.1` at 113.466 × 12.8 × 0.4 mm.
- The actual flat side wall provides 52.5 × 16.8 mm before clearance and 48.5 × 12.8 mm after the mandatory 2.0 mm edge clearance. The selector returns `BLOCK` in both allowed rotations.
- Even conservative rectangular over-approximations of the whole 52.5 × 65 mm top envelope and 65 × 21 mm print-bed envelope return `BLOCK`. Their true usable regions are smaller because of the funnel, holes, U-profile void, and required bed-contact lands.
- The profile must not be scaled, cropped, distorted, split across loose pieces, or placed in functional openings. No watermark was cut into the validated candidate.
- The 18-piece functional design remains unchanged. Final release is blocked until the user authorizes a materially different product geometry/identity strategy that produces a valid host region, followed by regenerated evidence, a slicer preview, an exact-process watermark coupon, and explicit watermark approval.
