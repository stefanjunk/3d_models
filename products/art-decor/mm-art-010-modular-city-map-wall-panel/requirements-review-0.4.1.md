# Requirements review 0.4.1 — MM-ART-010 Berlin physical palette

Status: **approved by Stefan on 2026-09-01; palette concept v04 requires separate visual approval before production remapping**.

## User-stated palette

| Semantic body | Physical filament | Inventory evidence | Intended visual role |
|---|---|---|---|
| `land_base` | SUNLU Oak, PLA+2.0 | `FIL-0005`, label code `05860601A` | light base plate |
| `medium_relief_and_areas` | SUNLU Mint Green, PLA+ | `FIL-0001`, label code `01160403Y` | middle relief and area level |
| `street_network` | SUNLU Midnight, PLA+2.0 | `FIL-0003`, label code `06660601A` | dark street network |
| `berlin_boundary_and_accents` | SUNLU Sky Blue, PLA+ | `FIL-0002`, label code `06860603A` | Berlin boundary and accents |

The canonical spool records are in `../../../business/10-inventory/README.md`.

## Controlled interpretation

- Revision 0.4.1 changes the physical filament mapping and visible palette, not the approved `boundary_crop` or `context_outline` geometry.
- The four existing sequential relief bodies remain broad, disjoint solids with no dithering: base, middle relief, street network, then boundary/accent.
- In `context_outline`, the 2.4 mm Berlin boundary changes from Orange to Sky Blue and remains nominally 0.4 mm above the Midnight street-network level.
- In `boundary_crop`, Sky Blue is reserved for the existing top accent body; the physical outer perimeter still follows the Berlin administrative boundary.
- All four rolls belong to the PLA family, but PLA+ and PLA+2.0 are supplier-specific blends. One common print process, color opacity and directed purge behavior require a physical coupon.
- Display hex values in planning images are approximated from the supplied spool photographs and are not colorimetric claims.
- Lighting, connector geometry, permanent two-part assembly, absence of a rear grid and non-replaceable construction remain unchanged.

## Gate effect

Stefan's exact role-to-filament instruction is recorded as requirements approval for revision 0.4.1. Because this is an appearance and manufacturing-material change, concept v03 remains the geometry reference but cannot approve the new palette. Concept v04 must be visually approved before named production solids or Anycubic project 3MFs are remapped.
