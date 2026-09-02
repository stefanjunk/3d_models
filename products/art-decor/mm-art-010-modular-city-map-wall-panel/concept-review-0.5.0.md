# Concept review 0.5.0 — Berlin site marker

Status: **pending human approval**.

Review artifact: `concepts/berlin-site-marker-concept-v05.png`

Artifact SHA-256: `0a564352f7f9d471c9e1b0a53fb1d244ae1777001ac0d01de8ff00720a8cad36`

Parameter source: `source/v0.5.0/berlin/site-marker-parameters.json`

The concept retains the approved Berlin map, two display modes, permanent two-half split, plug connectors and optional halo/front-through lighting. The only new visible geometry is the compact single-color metriCreate M mark centered on the frozen address point.

## Requirement-to-feature correspondence

- Sterkrader Straße 24 maps to X 204.057 / Y 283.519 mm in `boundary_crop` and X 222.626 / Y 267.354 mm in `context_outline`.
- The selected compact mark is 16.5 × 15.97 mm and has a calculated minimum source-grid feature of about 1.20 mm, above the 0.9 mm design minimum.
- The mark rises 0.60 mm, equal to three nominal 0.20 mm layers, and uses existing tool 4 rather than adding a fifth filament.
- Both instances remain wholly on the left main print and more than 50 mm from the center seam.
- Address/coordinate, artwork kind/path, width, orientation, relief height and tool are independent parameters.
- A later bitmap replacement is a monochrome silhouette/mask input, not unrestricted full-color image printing.

## Palette correspondence

The map views use the existing Oak/Mint Green/Midnight/Sky Blue product variant, so the mark appears in Sky Blue. The lower-right card records the proposed third non-geometric palette `metricreate_forge`: Midnight, Mint Green, White and Orange. In that variant the same tool-4 marker prints Orange.

## Deliberate limitations

- This is visual concept evidence, not manufacturing geometry or a 3MF.
- Display colors are photographic approximations and are not measured swatches.
- The official WFS point confirms the address; headquarters occupancy is user-supplied content.
- The selected metriCreate logo asset is clearance-pending.
- Physical relief readability, purge contamination and lit/unlit appearance remain open tests.

Production CAD, meshes and Anycubic project 3MFs remain blocked until this exact concept is approved.
