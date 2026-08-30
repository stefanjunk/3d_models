# Decision log — MM-ART-011

## 2026-08-30 — Requirements draft initialized

- Decision: Treat Harz and Rheinisches Braunkohlerevier as two 600 × 400 mm pilots in one configurable topographic product family, each built from a 3 × 2 grid of 200 mm modules.
- Basis: User requested large multi-print height maps, up to four colors, and optional customer-added rear lighting.
- Recommended color route: four altitude bands as horizontal layer changes, retaining the continuous 16-bit geometry master and limiting purge to approximately three changes per tile.
- Recommended data route: Copernicus DEM GLO-30 for cross-state Harz coverage; current official GeoBasis NRW DGM1 for the materially changing mining region. Copernicus is only a smoke-test fallback for the mining pilot.
- Recommended assembly: share the removable-tile segmented rear grid and 18 mm halo-light interface with MM-ART-010.
- Evidence: official Copernicus collection/licence and GeoBasis NRW DGM1 information checked 2026-08-30; local toolchain doctor PASS; no validated local learning record matched this interface.
- Gate at initialization: requirements approval was pending; no concept image, CAD, source download, heightmap or manufacturing export could be created at that point.

## Open decisions for requirements approval

- Resolved 2026-08-30: user approved 600 × 400 mm overall size and 3 × 2 modules on a 200 mm pitch.
- Resolved 2026-08-30: user requested curated abstract four-color palettes rather than a pseudo-realistic treatment, with filament-waste reduction as a design objective.
- Resolved 2026-08-30: user approved halo lighting and additionally required deliberate openings that pass rear light to the front.

## 2026-08-30 — Requirements revision 0.2.0 approved

- Harz pilot palette: Anycubic PLA Matte Dark Green, Chocolate Brown, Caramel and Bone White (`harz_moss_stone`).
- Rheinisches Braunkohlerevier pilot palette: Anycubic PLA Matte Black, Chocolate Brown, Desert Tan and Orange (`rhenish_industrial_earth`).
- Color topology: broad elevation bands as horizontal layer changes, no dithering and approximately three planned changes per tile.
- Light architecture: 18 mm halo cavity plus protected through-apertures, optional rear diffuser land and 8/10 mm generic LED-strip keep-out; all electrical parts remain excluded.
- Next gate: concept image approval. Production CAD remains blocked.

## 2026-08-30 — Concept sheet v01 generated for review

- Artifact: `concepts/modular-relief-collection-concept-v01.png` (non-authoritative visual concept).
- Harz direction: stepped Dark Green/Chocolate Brown/Caramel/Bone White terrain with selective illuminated valley or contour openings.
- Rheinisches Revier direction: Black/Chocolate Brown/Desert Tan/Orange terraced geometry with restrained illuminated infrastructure traces.
- Shared construction direction shown: six removable tiles, segmented rear frame, halo-light cavity, customer-added LED route and cable exits.
- Exact controlled values remain 600 × 400 mm overall, 3 × 2 tiles, 200 mm pitch and 18 mm nominal wall standoff; concept approval is still pending.
