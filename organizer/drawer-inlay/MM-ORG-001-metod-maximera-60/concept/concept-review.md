# MM-ORG-001 concept review — Gate 0B

Specification revision: `0.1.0-requirements`  
Concept candidate: `MM-ORG-001-concept-sheet-v1.png`  
Editable visual source: `MM-ORG-001-concept-sheet-v1.svg`  
Status: `APPROVED 2026-08-26`  
Active specification: `0.1.0-requirements`

The user explicitly rolled the active project back from the later 0.3.0 branch to revision `0.1.0` on 2026-08-26. This original concept sheet is therefore the active Gate-0B candidate again. The 0.2.0/0.3.0 general-purpose tray concepts remain historical only.

## Correspondence to the approved requirements

| Visible feature | Approved requirement represented |
|---|---|
| Continuous sand-colored lane on the left | One full-depth screwdriver/hand-tool lane derived from R1.6 |
| Removable comb shown inside the lane | Retained screwdriver-holder concept; final position remains parametric |
| Three hardware columns by six rows | Exactly 18 small-parts compartments |
| Aqua dashed grid and module numbers 1–9 | Exact 3-column × 3-row manufacturing grid for nine common-printer modules |
| Aqua seam markers and connector inset | Low-profile, hand-assembled planar connector direction; seam-relative placement |
| Navy, teal, aqua, sand and warm-canvas palette | Current metriMade palette direction |
| Rounded bins, high perimeter and lower internal walls | R1.6 functional form language |

## Deliberate simplifications and ambiguity

- The sheet is a design-intent diagram, not dimensional evidence. The binding envelope remains `512 × 491 × 50 mm` in `design-spec.yaml`.
- Wall thickness, wall height, corner radii and divider pitches are illustrative and will be generated from the specification in CAD.
- The connector inset shows only the planar joining principle. Lug profile, neck geometry, clearance and count per seam are unresolved until the parametric architecture and coupon sweep are built.
- Manufacturing seams intentionally cross some functional compartments. Production CAD must preserve usable floors and prevent proud edges or snagging at those crossings.
- The screwdriver-comb location is illustrative; access and module-boundary clearance will determine its final datum.
- Surface texture and the final `MM-WM-001-R1` underside mark are omitted because both are gated after fit/connector geometry stabilizes.

## Approval record

Stefan Junk approved this reactivated concept explicitly in chat with `freigegebne` on 2026-08-26. Gate 0B is passed for specification revision `0.1.0-requirements`; production CAD may proceed as DRAFT geometry. This approval does not approve connector fit, drawer compatibility, the later watermark geometry or a commercial release.
