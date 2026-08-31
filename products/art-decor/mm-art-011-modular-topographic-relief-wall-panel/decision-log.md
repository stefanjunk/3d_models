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

## 2026-08-30 — Concept v01 approved

- Human decision: Stefan explicitly approved the displayed concept v01 in chat.
- Scope: approved appearance direction, both palettes, 3 × 2 composition, removable-module intent, 18 mm halo and deliberate front-through terrain paths for specification revision 0.2.0.
- The concept remains non-dimensional evidence; `design-spec.yaml` continues to control all dimensions and acceptance limits.
- Next gate: review and approval of `plan/hybrid-design-plan.json`; production CAD and terrain processing remain blocked until that decomposition is approved.

## 2026-08-30 — Decomposition candidate generated

- Planner result: `PASS`, zero errors and zero warnings; unresolved evidence remains fail-closed in `reports/architecture.json`.
- Shared service interface: grid-owned gravity shoulder and three-point datum with four captive 6 × 2 mm magnet envelopes and steel counterparts per tile.
- Terrain route: separate 16-bit global masters, seam-locked tiles, adaptive meshes and three global Z color changes per pilot.
- Conservative per-tile mesh-budget planning passes at 898,890 triangles, approximately 42.9 MiB and 0.86 GiB estimated working memory; measured mesh and exact-slicer evidence remain pending.
- Decomposition approval remains pending; no production geometry or source download has been generated.

## 2026-08-30 — User correction reopens requirements as revision 0.3.0

- Human correction: no rear grid, no replaceable sections and no magnets; Harz and Rheinisches Braunkohlerevier are each one permanently assembled 3D-printed one-off.
- Confirmed target: Anycubic Kobra 3 Max Combo in its four-color configuration. The official product page reports a 420 × 420 × 500 mm build volume and four colors with one ACE Pro.
- Recommended new split: two 300 × 400 mm main prints per pilot with one permanent vertical center seam, replacing six 200 mm service tiles and reducing visible internal seams from seven to one.
- Recommended joining/mounting: a shallow tongue/groove, three small local rear bridge keys, process-qualified adhesive and isolated bonded hanger/standoff blocks. These are local parts, not a rear raster or service interface.
- The continuous 16-bit terrain master, abstract four-band color strategy and optional customer-added halo/front-through lighting remain. Each one-off keeps its own immutable global source and transform.
- Gate effect: revision 0.2.0 concept, decomposition, relief jobs and multicolor jobs are superseded. Revision 0.3.0 requirements are awaiting approval; no data acquisition, replacement concept or production geometry is authorized yet.

## 2026-08-31 — Glue-free revision 0.3.0 requirements approved

- Human decision: Stefan explicitly approved plug connectors instead of structural adhesive and instructed creation of the models and coupon.
- Current interface intent: three concealed loose one-way spring/tenon connectors register each pair of main halves; isolated hanger/standoff parts snap into local rear sockets. Destructive removal is acceptable; replaceable sections remain prohibited.
- Preflight `PREFLIGHT-MM-ART-011-002` supersedes the earlier backfill as the current retrospective assessment: `C3 (59.0)`, `R2`, `K2`, Lane C, `LOW_UNKNOWN`, `GO_WITH_CONTROLS`.
- Concept v02 was generated at `concepts/permanent-relief-collection-concept-v02.png`; it shows Harz, the Rheinisches Revier and the shared glue-free rear assembly and awaits human concept approval.
- Gate effect: requirements are approved for 0.3.0; terrain acquisition, production CAD and the connector coupon remain blocked until concept v02 approval.

## 2026-08-31 — Concept v02 approved and decomposition 0.3.0 prepared

- Human decision: Stefan explicitly approved concept v02 in chat (`konzept 2 freigegebene`).
- Per pilot, the replacement decomposition uses two 300 × 400 mm main halves, exactly three loose one-way seam connectors, two upper local hangers and two lower local standoffs. It contains no rear grid, magnets, adhesive or replaceable section.
- One off-product coupon can qualify both pilots only if connector/standoff material, nozzle, orientation and process profile are identical; otherwise it must be reprinted.
- Harz and Rheinisches Revier retain separate immutable 16-bit height authorities, separate pilot light cutters and exactly three global model-Z color changes each.
- Planner result for `plan/hybrid-design-plan-v0.3.0.json`: `PASS`, zero errors and zero warnings. Unknown spring, snap, source and wall-hardware dimensions remain fail-closed.
- Next gate: human approval of `decomposition-review-0.3.0.md`. The guided autonomy policy keeps terrain acquisition, CAD and coupon geometry blocked until that approval.

## 2026-08-31 — Decomposition 0.3.0 approved

- Human decision: Stefan explicitly approved the revision 0.3.0 decomposition in chat.
- Authorized work: shared connector/standoff interface calculation, shared multi-clearance coupon, frozen Harz and Rhenish terrain acquisition, 16-bit processing, proxy assemblies and production-model generation.
- Remaining boundaries: no printer upload/start; physical connector fit, installed wall proof, terrain/lighting appearance, watermark and final release remain human-controlled.
