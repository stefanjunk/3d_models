# Concept review — revision 3.0.0-draft.1

Asset: `DRAFT-concept-sheet-3.0.0-draft.1.png`

SHA-256: `fc5d1c8900ae88322e49c87f31e488605cfb81fdd3b4456d962b9da414aeb69a`

Generation route: built-in image generation (`imagegen` skill), use case `infographic-diagram`.

## Requirement-to-feature correspondence

- The upper overview represents the 945 mm installed row as eighteen separate, identical, butt-jointed modules with deliberate exploded gaps at selected joints.
- The lower-left detail represents one short segment with one centered funnel, a small solid margin at each cut end, and an open-bottom inverted-U section.
- The funnel visualization represents the preserved shallow funnel, sieve-hole field, five inward swirl ribs, and center boss from the approved v1.3 basis.
- The lower-right view represents a rigid 90° rotation about assembly Y, with one complete U-shaped end cross-section on the printer bed and the 52.5 mm segment length becoming print height.
- No connector, key, snap, tongue, rail, magnet, separate side-wall part, or fastener is intended or shown.

## Deliberate simplifications and visual limits

- This raster concept is not dimensional or count proof. `design-spec.yaml` remains authoritative for exactly 18 segments, 52.5 mm segment length, 46 mm funnel diameter, 3.25 mm end margins, 65 mm width, 21 mm height, hole count/pitch, and nominal total length.
- The visible `21`, `65`, and `90°` annotations are explanatory only and do not substitute for CAD validation.
- Perspective and image generation may stylize funnel slope, hole layout, rib curves, wall radii, and gaps. Production CAD must reproduce the approved parameters rather than trace the pixels.
- The drain-channel outline is contextual only; no channel geometry or fixture is part of the deliverable.
- The concept communicates the intended print orientation, not a slicer result or proof that brim/support settings are unnecessary.

## Final generation prompt

```text
Use case: infographic-diagram
Asset type: design-gate concept sheet for a functional FFF shower-drain hair trap
Primary request: Create one clean landscape technical concept sheet showing the approved design intent for eighteen loose, identical shower-drain hair-trap segments arranged end-to-end. Each segment is a short inverted-U profile with an open bottom and exactly one centered circular shallow funnel on the top face. The funnel has many small sieve holes and five curved inward swirl ribs. There must be no connectors, tabs, keys, slots, rails, magnets, overlap, or interlocking geometry between segments.
Scene/backdrop: neutral light-gray engineering presentation background, subtle build plate only in the print-orientation panel
Subject and composition: three coordinated views in one sheet: (1) large three-quarter overview of a long 945 mm drain row visibly decomposed into eighteen separate butt-jointed modules; use slight exploded spacing at a few joints so the loose pieces are unmistakable, (2) close three-quarter detail of one short segment showing its 65 mm width, 21 mm installed height, open-bottom inverted-U cross-section, one large centered funnel and small solid margin at both cut ends, (3) a single identical segment rotated 90 degrees onto one complete U-shaped end cross-section on a printer build plate, making the short segment length vertical as print height and showing support-free intent.
Style/medium: precise industrial-design CAD concept render, realistic but schematic, matte pale gray PETG, crisp edges, restrained blue arrows only for separation and the 90-degree rotation
Lighting/mood: soft studio lighting, high legibility, technical and neutral
Constraints: preserve identical repeated segments; exactly one funnel per segment; the overview must clearly communicate many loose pieces rather than a monolithic rail; open bottom must be visible in the detail and print view; no fasteners or joining features; no people; no plumbing fixtures beyond a minimal channel outline; no misleading exact dimension labels because dimensions will be supplied beside the image; no logo, no watermark, no decorative text
Avoid: fused segments, connector features, multiple funnels per piece, closed box profiles, snap joints, separate side walls, inaccurate product branding, dramatic perspective, clutter, excessive shadows
```
