# Requirements review 0.5.0 — parameterized Berlin site marker

Status: **approved from Stefan's explicit instructions on 2026-09-02**.

This revision adds one visible, slightly raised site marker to both existing Berlin display modes. It does not alter the map extent, center split, rear interfaces, light openings or the rule that palette changes alone never redesign geometry.

## Approved contract

| Item | Requirement | Source |
|---|---|---|
| Location | Sterkrader Straße 24, 13507 Berlin | user-stated; official address point frozen from Berlin WFS |
| Default artwork | selected compact `metriCreate` M mark, single-color | user-stated logo request; recommended FDM-safe asset |
| Default size | 16.5 × 15.97 mm, aspect ratio preserved | recommended; smallest logo grid feature resolves to about 1.20 mm |
| Relief | 0.60 mm above the highest local face | user-stated “ein wenig erhaben”; recommended as three 0.20 mm layers |
| Color/tool | existing semantic tool 4 | recommended; preserves the four-filament ceiling |
| Placement | artwork center at the frozen address point | inferred from “an der Berliner Adresse” |
| Display modes | same geographic address in `boundary_crop` and `context_outline` | inferred; coordinates are transformed separately per mode |
| Parameterization | address/coordinate, artwork asset, artwork kind, width, orientation, relief height and semantic tool | user-stated and expanded into a reusable contract |

The address is an editable input. A changed address must be resolved and frozen with coordinate, CRS, source, query and timestamp; it is not silently geocoded during a production build. A direct EPSG:25833 coordinate override is possible when provenance is supplied.

The artwork is an independent input. SVG/DXF logos and icons are preferred. A photograph or bitmap is accepted only after conversion to a rights-cleared monochrome silhouette/mask; arbitrary full-color raster printing would violate the four-tool and low-waste design.

## Location and fit

The official address point resolves to EPSG:25833 coordinate `383841.69199994, 5826269.76599965`. It maps to:

- `boundary_crop`: X 204.057 / Y 283.519 mm
- `context_outline`: X 222.626 / Y 267.354 mm

Both positions are wholly on the left 300 × 400 mm main print. The 16.5 mm mark stays more than 50 mm from the center seam, so it does not cross the permanent joint.

## Third palette variant

The closest inventory-backed four-color interpretation of the selected `metriCreate` palette is named `metricreate_forge`:

1. Midnight (`FIL-0003`) — dark land base
2. Mint Green (`FIL-0001`) — teal-like middle relief
3. White (`FIL-0009`) — high-contrast street network
4. High Speed Orange (`FIL-0007`) — Berlin boundary, accents and location mark

This deliberately omits the brand's fifth light-aqua color because the current Kobra 3 Max Combo job is limited to four filaments. It is an abstract brand-near interpretation, not a measured color match. The same new marker geometry remains valid under the Oak/Mint/Midnight/Sky product variant, where tool 4 prints the mark in Sky Blue.

## Gates and exclusions

- Concept approval is reopened because the visible site marker changes appearance and geometry.
- Production CAD/mesh/3MF generation remains blocked until concept v05 is approved.
- The visible site marker is separate from the required recessed rear `metriMade.com · MM-ART-010 · v0.5.0` release watermark.
- The official address dataset confirms the address point, not the user's statement that it is the company headquarters.
- Physical logo readability, color contamination and lit/unlit appearance remain coupon/print review items.
