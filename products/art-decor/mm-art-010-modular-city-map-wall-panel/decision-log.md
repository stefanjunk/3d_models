# Decision log — MM-ART-010

## 2026-08-30 — Requirements draft initialized

- Decision: Treat the Berlin pilot as a 600 × 400 mm, 3 × 2 modular indoor wall picture with up to four semantic color bodies.
- Basis: User requested a large multi-print street-map picture, four-color planning, and optional customer-added rear lighting.
- Recommended architecture: removable 200 mm art modules on a common segmented rear rail/grid, with an 18 mm halo-light gap and generic LED/cable keep-outs.
- Data route: OpenStreetMap vector snapshot in EPSG:25833, transformed once in the global panel frame and only then split into tiles.
- Rights state: ODbL attribution/share-alike duties must be documented; commercial release remains blocked pending reviewed source/produced-work treatment.
- Evidence: official OpenStreetMap copyright/licence page checked 2026-08-30; local toolchain doctor PASS; no validated local learning record matched this interface.
- Gate at initialization: requirements approval was pending; no concept image, CAD, code, source download or manufacturing export could be created at that point.

## Open decisions for requirements approval

- Resolved 2026-08-30: user approved 600 × 400 mm overall size and 3 × 2 modules on a 200 mm pitch.
- Resolved 2026-08-30: user requested curated abstract four-color palettes rather than a pseudo-realistic treatment, with filament-waste reduction as a design objective.
- Resolved 2026-08-30: user approved halo lighting and additionally required deliberate openings that pass rear light to the front.

## 2026-08-30 — Requirements revision 0.2.0 approved

- Selected pilot palette: Anycubic PLA Matte Bone White, Nardo Grey, Black and Orange (`urban_signal`).
- Color topology: broad semantic bodies, no dithering, no photographic color approximation and no sub-print decorative islands.
- Light architecture: 18 mm halo cavity plus protected through-apertures, optional rear diffuser land and 8/10 mm generic LED-strip keep-out; all electrical parts remain excluded.
- Next gate: concept image approval. Production CAD remains blocked.

## 2026-08-30 — Concept sheet v01 generated for review

- Artifact: `concepts/modular-relief-collection-concept-v01.png` (non-authoritative visual concept).
- Berlin direction: warm Bone White/Nardo Grey ground, Black primary routes and Orange accent fields; selected route/void lines transmit warm rear light.
- Shared construction direction shown: six removable tiles, segmented rear frame, halo-light cavity, customer-added LED route and cable exits.
- Exact controlled values remain 600 × 400 mm overall, 3 × 2 tiles, 200 mm pitch and 18 mm nominal wall standoff; concept approval is still pending.
