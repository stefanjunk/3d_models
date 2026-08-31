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

## 2026-08-30 — Concept v01 approved

- Human decision: Stefan explicitly approved the displayed concept v01 in chat.
- Scope: approved appearance direction, palettes, 3 × 2 composition, removable-module intent, 18 mm halo and deliberate front-through light paths for specification revision 0.2.0.
- The concept remains non-dimensional evidence; `design-spec.yaml` continues to control all dimensions and acceptance limits.
- Next gate: review and approval of `plan/hybrid-design-plan.json`; production CAD remains blocked until that decomposition is approved.

## 2026-08-30 — Decomposition candidate generated

- Planner result: `PASS`, zero errors and zero warnings; unresolved evidence remains fail-closed in `reports/architecture.json`.
- Recommended service interface: grid-owned gravity shoulder and three-point datum with four captive 6 × 2 mm magnet envelopes and steel counterparts per tile.
- Berlin color route: named disjoint color solids; the validated planning contract is `multicolor-job.yaml`.
- Decomposition approval remains pending; no production geometry has been generated.

## 2026-08-30 — User correction reopens requirements as revision 0.3.0

- Human correction: no rear grid, no replaceable sections and no magnets; every pilot is one permanently assembled 3D-printed one-off.
- Confirmed target: Anycubic Kobra 3 Max Combo in its four-color configuration. The official product page reports a 420 × 420 × 500 mm build volume and four colors with one ACE Pro.
- Recommended new split: two 300 × 400 mm main prints with one permanent vertical center seam, replacing six 200 mm service tiles and reducing visible internal seams from seven to one.
- Recommended joining/mounting: a shallow tongue/groove, three small local rear bridge keys, process-qualified adhesive and isolated bonded hanger/standoff blocks. These are local parts, not a rear raster or service interface.
- Lighting remains optional customer equipment. The printed artwork reserves an 18 mm open halo cavity, local strip lands/clips, cable routes and deliberate front-through openings.
- Gate effect: the revision 0.2.0 concept, decomposition and multicolor job are superseded. Revision 0.3.0 requirements are awaiting approval; no replacement concept or production CAD is authorized yet.

## 2026-08-31 — Glue-free revision 0.3.0 requirements approved

- Human decision: Stefan explicitly approved plug connectors instead of structural adhesive and instructed creation of the models and coupon.
- Current interface intent: three concealed loose one-way spring/tenon connectors register the two main halves; isolated hanger/standoff parts snap into local rear sockets. Destructive removal is acceptable; replaceable sections remain prohibited.
- Preflight `PREFLIGHT-MM-ART-010-002` supersedes the earlier backfill as the current retrospective assessment: `C3 (59.0)`, `R2`, `K2`, Lane C, `LOW_UNKNOWN`, `GO_WITH_CONTROLS`.
- Concept v02 was generated at `concepts/permanent-relief-collection-concept-v02.png`; it shows Berlin plus the shared glue-free rear assembly and awaits human concept approval.
- Gate effect: requirements are approved for 0.3.0; production CAD and the connector coupon remain blocked until concept v02 approval.
