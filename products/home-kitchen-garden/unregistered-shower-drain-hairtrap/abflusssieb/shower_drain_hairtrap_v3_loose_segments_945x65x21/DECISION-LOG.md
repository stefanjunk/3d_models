# Decision log — shower drain hair trap v3

Status: requirements review; no v3 production CAD or manufacturing export exists yet.

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
- The 18-segment selection is a design recommendation pending explicit requirements approval; it is not yet a produced or physically validated model.
