# NameForm 0.4.1 reinforced facade — concept review

Status: `PENDING HUMAN CONCEPT APPROVAL`

This concept sheet visualizes the requirements approved by Stefan on
2026-08-31. It is an appearance and architecture review artifact, not
dimensional CAD, a strength result, or manufacturing evidence.

## Asset

- Image: `nameform-bookends-v0.4.1-reinforced-concept.png`
- SHA-256: `0dfabffa0554a51f41493ab729c1239f6fb8e71b9cc2674b62f865c73c5a1651`
- Size: 1642 x 958 px, RGB PNG
- Generated with: built-in image generation tool
- Geometry/appearance reference:
  `../validation/v0.4.0/generated/MARITA/run02/renders/DRAFT-nameform-MARITA-three-quarter-v0.4.0.png`

## Approved dimensions outside the image

- Glyph depth: 12.0 mm from the front datum.
- Rear connector front: y = 10.0 mm.
- Rear connector thickness: 4.0 mm; rear extent y = 14.0 mm.
- Positive glyph/connector depth overlap: at least 2.0 mm.
- Local bridge-band width: at least 12.0 mm.
- Nominal/finished glyph gap: 1.8 mm / at least 1.2 mm.
- Candidate-C wood relief remains limited to glyph fronts: 0.6 mm relief,
  0.45 mm manufacturing pitch, 120 x 45 mm physical repeat.

## Requirement-to-feature correspondence

1. The top row is the intended direct front view: `MA | RITA`, open counters,
   visible glyph gaps, and no rectangular plaque.
2. The middle row is the rear three-quarter review: visibly deeper glyph
   bodies, glyph-shaped rear reinforcement, and separate short local bridges
   between neighboring glyphs and the side blade.
3. The bottom row enlarges representative local bridges and their location at
   the rear of the deep glyph bodies.
4. Dark brown identifies the rear connector only for review clarity. The
   intended product remains one fused print unless a later manufacturing
   decision explicitly changes that architecture.
5. The wood appearance remains on the visible glyph fronts; connector bonds,
   counters, gaps, side blades, feet, and structural keep-outs remain smooth.

## Deliberate simplifications and ambiguity

- Depth and connector contrast are exaggerated so the relationship is visible.
- Bridge locations and rounded shapes are illustrative. Production geometry
  must derive them from exact glyph outlines and verify every section.
- The bottom row is an enlarged connection detail, not a dimensionally clipped
  CAD section.
- The image does not prove overlap, stiffness, layer bonding, support freedom,
  slicability, or physical appearance.

## Prompt trace

Initial generation requested a three-view MARITA sheet with deeper glyphs and
a stronger recessed connector. It incorrectly produced a continuous rear rail.
The selected correction changed only that system: remove every long rail and
use a glyph-shaped rear layer plus short, wide local bridges at the backs of
neighboring glyphs, while preserving the exact `MA | RITA` text, open counters,
front gaps, wood fronts, side blades, feet, cameras, and lighting.

Approval of this image authorizes production CAD only for specification 0.4.1;
it does not approve a manufacturing release.
