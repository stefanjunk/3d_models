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

## 2026-08-31 — Concept v02 approved and decomposition 0.3.0 prepared

- Human decision: Stefan explicitly approved concept v02 in chat (`konzept 2 freigegebene`).
- The replacement decomposition uses two 300 × 400 mm main halves, exactly three loose one-way seam connectors, two upper local hangers and two lower local standoffs. It contains no rear grid, magnets, adhesive or replaceable section.
- The off-product coupon combines four 0.15/0.25/0.35/0.45 mm per-side pocket/locating variants, one calculated seam connector and one representative hanger snap in production orientation.
- Planner result for `plan/hybrid-design-plan-v0.3.0.json`: `PASS`, zero errors and zero warnings. Unknown spring, snap and wall-hardware dimensions remain explicitly unselected and block source generation until their named calculation/evidence exists.
- Next gate: human approval of `decomposition-review-0.3.0.md`. The guided autonomy policy keeps CAD and coupon geometry blocked until that approval.

## 2026-08-31 — Decomposition 0.3.0 approved

- Human decision: Stefan explicitly approved the revision 0.3.0 decomposition in chat.
- Authorized work: shared connector/standoff interface calculation, multi-clearance coupon, Berlin source freeze, proxy assembly and production-model generation.
- Remaining boundaries: no printer upload/start; physical connector fit, installed wall proof, lighting appearance, watermark and final release remain human-controlled.

## 2026-08-31 — Shared interface and coupon digital candidate generated

- Family source: `source/v0.3.0/interface_geometry.py` with frozen `interface-parameters.json`; it owns the three double-ended seam springs, rear-open derived pockets, local slide/snap sockets, two upper hangers and two lower 18 mm standoffs.
- Geometry estimate: 0.75% nominal connector-arm surface strain and 0.74% socket-detent surface strain using `epsilon = 1.5*t*delta/L^2`. No material allowable, retention force, fatigue life or wall-load rating is claimed.
- Coupon: one 184 × 118 × 3 mm build with exactly 20 watertight bodies covers 0.15, 0.25, 0.35 and 0.45 mm clearance per side. The product source uses 0.25 mm only provisionally.
- Deterministic checks: all four functional meshes are watertight single bodies; the coupon audit passes with 20 components. The first relative-path slicer attempt failed closed and produced no G-code; the preserved absolute-path rerun passes in Anycubic Slicer Next 1.3.9.4 with the exact Kobra 3 Max 0.4/0.20 mm Standard/Anycubic PLA Matte profile set.
- Slicer metrics: 15 layers, one tool, zero tool changes, 4,139.45 mm estimated filament and 1,771 s normal-mode estimate. This is local export evidence only; physical fit and final slicer preview remain open.

## 2026-08-31 — Berlin four-color digital artwork generated and optimized

- Frozen source: verified 99,132,753-byte Geofabrik Berlin PBF snapshot, SHA-256 `44878bac7391c7d1e9d86e583a0cbd9713a69d164ac47ad1e4ab7e7d374d407c`; derived EPSG:25833 layers contain one Berlin boundary, 34,057 major-road, 1,466 accent-road, 8,588 rail and 247 river/canal features.
- The initial direct vector union was stopped after memory exceeded 8.7 GiB. The accepted rebuild uses a protected 0.25 mm manufacturing mask, below the 0.45 mm target line width, then vectorizes exact contours for Manifold3D extrusion.
- Output: two 299.875 × 400 × 4.6 mm watertight composites, eight named watertight color bodies and two portable four-material 3MFs. Triangle counts are 71,996 left and 59,326 right, both below the 750,000 target.
- Color strategy: Bone White 0–3.0 mm, Nardo Grey 3.0–3.6 mm, Black 3.6–4.2 mm and Orange 4.2–4.6 mm. Both halves have exactly three estimated global changes and zero multi-color layers; no dithering is present.
- Through-light water paths occupy 1.52% left and 1.88% right, below the 12% limit, after seam and connector/hanger keep-outs.
- Optimization: reducing the rejected 3.4 mm source baseline to the approved 3.0 mm backer cuts the measured left single-material preflight from 105,158.03 to 102,400.49 mm filament (-2.62%) and from 45,072 to 43,695 s (-3.06%) without changing the visible field.
- Final geometry-only Anycubic preflight passes for both halves with exact profiles: 102,400.49 mm / 43,695 s left and 99,093.48 mm / 41,553 s right. These composite slices validate bed fit, layers and apertures only; ACE slot mapping, purge tower and final color preview remain human-controlled.

## 2026-09-01 — Anycubic 3MF import failure reproduced and repaired

- User observation: the right Berlin 3MF opened without usable geometry in the target slicer.
- Reproduction: both original standards-only 3MFs pass the repository structural validator but Anycubic Slicer Next 1.3.9.4 exits with native `return_code=-6` before loading a model. The failure is therefore a target-slicer interoperability defect, not an empty right-hand mesh.
- Repair: `package_anycubic_project.py` asks Anycubic Slicer Next to author its own vendor project container, keeps the four aligned source STLs as distinct volumes, assigns tools 1–4 in the project metadata, expands the embedded filament arrays to four palette entries and centres the assembled half on the configured bed.
- Result: native import and slicing succeed for both replacement 3MFs. Each G-code contains tools 0–3 and exactly three material changes; source STL hashes are recorded in the build reports.
- Validation limitation: the generic G-code analyzer double-counts 23 canonical `;LAYER_CHANGE` markers plus 19 supplemental `; layer #` comments and therefore reports 42 versus the correct 23 layers. Product-local regression reports verify the canonical markers, unique Z sequence, header/footer counts, tools and changes without rewriting G-code. The aggregate adapter status remains transparently `FAIL` pending a reviewed validator fix.
- Human gates: final ACE slot identity, wipe/purge preview, appearance and physical printing remain unapproved; no upload or print start occurred.

## 2026-09-01 — Berlin display-mode requirements 0.4.0 approved; concept v03 pending

- User correction: the existing rectangular Berlin field contains too much unintended free area and the right-hand 3MF appeared geometry-free in the target slicer.
- The 3MF defect was closed separately in revision 0.3.0 by replacing both portable packages with native Anycubic Slicer Next project 3MFs; exact import/slice evidence is retained as the required 0.4.0 interoperability pattern.
- New parameter authority: `display_mode = boundary_crop | context_outline` in `source/v0.4.0/berlin/display-mode-parameters.json`.
- `boundary_crop` removes all bodies outside the Berlin administrative polygon. The artwork becomes an irregular silhouette inside a maximum 600 × 400 mm envelope, with zero printed free area outside Berlin.
- `context_outline` retains the rectangular 600 × 400 mm field, defaults to 12% context margin per side and marks Berlin with a 2.4 mm Orange relief band.
- The frozen Berlin-only extract cannot cover the selected Umland margin. Production `context_outline` therefore requires a larger immutable Berlin/Brandenburg snapshot after concept approval.
- Concept v03 is generated from the frozen boundary/network vectors and stored at `concepts/berlin-display-modes-concept-v03.png`. Requirements are approved by the user's explicit request; concept, mode-aware decomposition and production examples remain gated by separate human approval.

## 2026-09-01 — Concept v03 approved; mode-aware decomposition prepared

- Human decision: Stefan explicitly wrote `freigegeben` in direct response to the boundary-crop/context-outline concept v03.
- The concept approval advances revision 0.4.0 to decomposition; it does not itself authorize production CAD under the guided project policy.
- `MODE_OUTER_MASK_SET` owns the physical perimeter and context extent. `MODE_INTERFACE_SKELETON` derives mode-specific connector, hanger, standoff, LED, attribution and future watermark lands only inside the retained safe body.
- The shared 0.3.0 connector/snap shapes remain reusable, but their absolute placements do not. `boundary_crop` and `context_outline` receive separate placement manifests.
- `context_outline` remains fail-closed until a larger immutable Berlin/Brandenburg source covers the approved 12% default context margin.
- The first planner run correctly failed on a zero-height non-product source envelope. That report is retained as `reports/architecture-v0.4.0-failure-r0.*`; the corrected candidate passes with zero errors and zero warnings.
- Next gate: explicit human approval of `decomposition-review-0.4.0.md` and `plan/hybrid-design-plan-v0.4.0.json`. Source acquisition, CAD, mesh and 3MF work remain blocked until then.

## 2026-09-01 — Mode-aware decomposition 0.4.0 approved

- Human decision: Stefan explicitly wrote `freigegeben` in direct response to `decomposition-review-0.4.0.md` and `plan/hybrid-design-plan-v0.4.0.json`.
- Authorized digital work: acquisition/freezing of the expanded Berlin/Brandenburg source, mode-specific safe-land and interface solving, parameterized CAD/mesh generation, four-color Anycubic project 3MF packaging and deterministic local validation for both display examples.
- Continuing boundaries: the connector/snap compensation remains physically unqualified; exact filament batches, ACE/purge preview, physical print, wall installation, appearance, watermark, safety, rights and commercial release remain human-controlled.
- No printer upload or print start is authorized.

## 2026-09-01 — Expanded source and mode placements frozen

- Frozen transport authority: Geofabrik/GWDG `germany-260830.osm.pbf`, 4,828,999,134 bytes, provider MD5 `67f6fe1597784796ebe0d36ac5fb990f`, SHA-256 `505860193092ce58cc8e4bb7f3b657b5f7de5f6d329d2b1bed44561cdfa7da55`.
- `source-data/v0.4.0/berlin/source-manifest.json` passes strict extraction/context containment and records 126,806 major-road, 4,356 accent-road, 14,659 rail and 422 river/canal features plus the approved Berlin boundary.
- The default context preserves the approved 12% vertical margin; the source extent expands horizontally to 26.6545805% per side so it fills the 600 × 400 mm frame at one uniform scale without distortion, crop or letterboxing.
- `validation/v0.4.0/berlin/interface-placement-report.json` passes for both modes. The boundary silhouette uses connector stations Y 120/232/344 mm and relocated local mounts; the context rectangle retains the 0.3.0 positions. Minimum modeled perimeter ligament is 5.307 mm.
- Exact connector/snap process compensation, light appearance, wall hardware and proof load remain physical human gates.

## 2026-09-01 — Both Berlin display examples completed as digital candidate r9

- `boundary_crop` now removes every positive body outside the Berlin administrative silhouette. The two physical halves retain 99,990.59 mm² base area in total; compared with the full rectangular context example this reduces same-profile positive extrusion by 56.29% and the native slicer estimate by 54.88%.
- `context_outline` retains the full 600 × 400 mm Berlin-plus-Umland field and marks the Berlin boundary as an Orange relief band. Both modes use the approved Bone White, Nardo Grey, Black and Orange Z bands without dithering.
- Closed waterway aperture loops initially created loose positive islands. Candidate r9 inserts 4/2/2/2 local 2.0 mm material bridges in boundary-left, boundary-right, context-left and context-right; each final half has one connected backer and one watertight composite while remaining below the 12% open-area limit.
- All sixteen serialized color bodies and four reconstructed composites are watertight, positive-volume and free of boundary, nonmanifold, degenerate and duplicate faces. The exact composites contain 143,300, 116,648, 309,948 and 283,342 triangles.
- Four native Anycubic project 3MFs import and slice successfully in Anycubic Slicer Next 1.3.9.4. Every retained exact G-code has 23 canonical layers, tools 0–3 and three tool changes. The generic standard-only 3MF parser does not follow the vendor object-part relationship layout, and the generic G-code analyzer counts 19 supplemental vendor comments; both limitations remain visible and are not rewritten away.
- Digital perimeter and aperture evidence removes their blocks from component, integration and manufacturing gates. Physical connector/light coupon, exact filament/ACE/purge GUI review, full prints, wall proof, lit/unlit appearance, watermark and release remain human-controlled.
- No printer upload or print start was performed.

## 2026-09-01 — Physical SUNLU palette selected as revision 0.4.1

- User-selected mapping: Oak (`FIL-0005`) for the light base, Mint Green (`FIL-0001`) for the middle relief/area level, Midnight (`FIL-0003`) for the dark street network and Sky Blue (`FIL-0002`) for the Berlin boundary and accents.
- All four photographed rolls are 1.75 mm SUNLU PLA-family products, but the mix of PLA+ and PLA+2.0 remains supplier-specific. Exact batches, conditioning, common-process compatibility, opacity and directed purge behavior require physical evidence.
- The revision 0.4.0 digital-candidate-r9 topology remains the geometry baseline. Revision 0.4.1 changes the appearance/material mapping and therefore reopens the human concept gate before production solids and Anycubic project 3MFs may be remapped.
- Concept v04 was generated at `concepts/berlin-display-modes-concept-v04.png`; display RGB values are photo-derived approximations and not colorimetric claims.
- The product-specific preflight is restored as `PREFLIGHT-MM-ART-010-009`: `C3 (62.0)`, `R2`, `K2`, Lane C, `LOW_UNKNOWN`, `GO_WITH_CONTROLS`. Digital concept work is allowed, while print-candidate and release gates remain blocked.

## 2026-09-02 — Palette corrected to a non-geometric product variant

- User correction: changing only the four filament colors must not trigger redesign. A new picture may preview the colorway, but concept v03 and revision 0.4.0 `digital-candidate-r9` remain the design and geometry authorities.
- `product-variants.json` now separates four axes: `palette_preset`, `display_mode`, `assembled_size_mm` and `map_extent`.
- `palette_preset` is implemented as a slicer/ACE assignment only. Oak/Mint Green/Midnight/Sky Blue map to the existing tools 1/2/3/4; no CAD, mesh, relief, split, connector, mount or light geometry is regenerated or renamed.
- Both Berlin examples are registered under the same SKU as configured product variants. No new portfolio product identity is created.
- Size is reserved as a parameter axis, but only 600 × 400 mm is currently production-supported. Arbitrary uniform slicer scaling is prohibited because it would also scale clearances, wall gap, relief depth and printable minima. Future sizes must regenerate the X/Y artwork while preserving functional dimensions.
- Map-extent selection remains deferred. A new city or crop requires frozen geospatial data and renewed placement, interface, mesh and slicer validation.
- Concept v04 is retained as an informational palette preview and no longer blocks product configuration. Physical filament-profile, ACE/purge, opacity, fit, appearance and release gates remain open.
