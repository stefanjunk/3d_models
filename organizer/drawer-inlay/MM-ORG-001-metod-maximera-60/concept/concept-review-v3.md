# MM-ORG-001 concept review — Gate 0B

Specification revision: `0.3.0-requirements`  
Concept candidate: `MM-ORG-001-concept-sheet-v3.png`  
Editable visual source: `MM-ORG-001-concept-sheet-v3.svg`  
Status: `SUPERSEDED / NOT APPROVABLE`  
Superseded by: explicit rollback to `0.1.0-requirements` on `2026-08-26`

This sheet visualizes the now-inactive 0.3.0 Kobra branch. The user explicitly returned the active project to revision 0.1.0, so this image is historical evidence only and must not be approved or used as production-CAD input.

## Correspondence to the approved requirements

| Visible feature | Approved requirement represented |
|---|---|
| Four trays in one 2 × 2 organizer | Minimum four-part segmentation and therefore largest practical rectangular Kobra-profile trays |
| One open tray | One general-purpose open compartment |
| One tray split in two | One two-compartment tray |
| Two trays split 2 × 2 | Two four-compartment trays; eleven compartments total |
| Four dashed internal seam segments A–D | Only the manufacturing seams required by the four-part 2 × 2 layout |
| Exactly two aqua connector markers on every seam segment | Approved connector density: eight mating locations total |
| Exploded male tabs and matching female sockets | Seam-relative planar-jigsaw gender mapping; no separate hardware |
| Enlarged tab/socket detail | Round-ended planar-jigsaw principle inherited only conceptually from R1.6 |
| Common aqua datum in the side view | Connector bodies remain inside the floor plane; nothing protrudes below the drawer-contact surface |
| Three-quarter crop | R1.6-derived calm rounded form, matte PETG direction and assembled visual hierarchy |

## Binding geometry beside the image

- Packed nominal envelope: `512 × 491 × 50 mm`.
- Four-tray Kobra grid: `2 × 2`; each tray is approximately `256 × 245.5 × 50 mm` before detailed wall and connector resolution.
- Selected layout: one open, one two-compartment and two four-compartment trays.
- Connector allocation: four shared seam segments × two connector pairs = eight mating locations.
- Connector clearance coupon sweep: `0.30 / 0.40 / 0.50 mm`; no value is qualified before printing and measurement.
- Kobra-profile bed-fit gate: every complete tray including male lugs must stay within `416 × 416 mm`.

## Deliberate simplifications and visual ambiguity

- The deterministic upper schema is authoritative for tray count, compartment count, seam mapping, connector count and male/female assignment.
- The image-generated three-quarter crop communicates form and material only. Its small connector glyphs are not authoritative geometry and may hide or stylize individual mating features because of perspective.
- Connector radii, neck dimensions, edge offsets, wall interruptions and clearance are deliberately not dimensioned in the concept. CadQuery and physical coupons will determine them after concept approval.
- The connector detail is a planar design principle, not fit, strength, flatness or printability evidence.
- The assembled set is shown without drawer hardware or fit shims. Real-drawer measurement, perimeter clearance and optional shims remain separate fit evidence.
- Surface texture and the final `MM-WM-001-R1` underside mark remain blocked until plain geometry and connector qualification pass.

## Historical approval request — withdrawn

The former 0.3.0 approval request is withdrawn. Gate 0B now points to `concept/MM-ORG-001-concept-sheet-v1.png` for the reactivated 0.1.0 baseline.
