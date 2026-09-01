# Decomposition review 0.4.0 — MM-ART-010 Berlin display modes

Status: **human-approved by Stefan on 2026-09-01**.

Machine-readable candidate: `plan/hybrid-design-plan-v0.4.0.json`

Human-approved architecture baseline SHA-256: `985d17c584b13a0afc9da960f4ac731c8a07e77a377030ac2e7f359e93252561`

Current post-approval evidence-state SHA-256: `25d0d6d9528c44b3c4b9a8f640d3765f57980478fe17c869e9df02f8d2206a5b`. Only `DEC-SOURCE-040` and `DEC-PLACEMENT-040` changed from open/provisional to resolved, with links to the frozen source and deterministic placement evidence; component ownership, interfaces and manufacturing architecture are unchanged.

Planner evidence after source and placement closure: `reports/architecture-v0.4.0-source-placement-pass.json` and `reports/architecture-v0.4.0-source-placement-pass.md` — **PASS, 0 errors, 0 warnings**. The approval-recording PASS remains at `reports/architecture-v0.4.0-approved.*`; the pre-approval PASS remains at `reports/architecture-v0.4.0.*`; the initial fail-closed run with one invalid zero-height source-data envelope is preserved as `reports/architecture-v0.4.0-failure-r0.*`. A planner pass proves internal allocation and reference consistency, not printable geometry, physical fit or wall safety.

## Shared printed architecture per one-off

| Printed body | Quantity | Responsibility |
|---|---:|---|
| Main half | 2 | Mode-owned outer perimeter, flat rear datum, color relief, derived sockets, light openings and local lands |
| One-way seam connector | 3 | Shared qualified shape; mode-specific placement along the retained center seam |
| Upper hanger | 2 | Local self-weight path from a verified safe land to customer-selected wall hardware |
| Lower standoff | 2 | Establishes the common 18 mm wall plane |

There is still no rear grid, rear frame, adhesive, magnet, replaceable section or supplied electrical system.

## Variant ownership

| Authority | `boundary_crop` | `context_outline` |
|---|---|---|
| `MODE_OUTER_MASK_SET` | Berlin administrative polygon is the positive-body perimeter | Full 600 × 400 mm rectangle; default context is Berlin bounds plus 12% per side |
| `MAP_SOURCE_SET` | Reuses the frozen Berlin source after hash/coverage checks | Requires a new immutable Berlin/Brandenburg source covering the complete context extent |
| `MULTICOLOR_RELIEF_SET` | Orange remains an abstract transport/signal accent | Orange additionally owns the 2.4 mm Berlin boundary relief band |
| `MODE_INTERFACE_SKELETON` | Relocates sockets and rear lands only into an inward-offset safe portion of the irregular silhouette | May retain the rectangular placement pattern after the same ligament and collision checks |
| `LIGHTING_ENVELOPES` | Follows a safe inward perimeter route where the silhouette is wide enough | Uses a rectangular halo route plus the same three customer cable exits |

The common 0.3.0 connector and snap shapes remain reusable authorities; their old absolute positions do not. Each mode gets a distinct placement manifest derived from its retained outer mask.

## Manufacturing bodies and examples

- Two main composites per mode: four total DRAFT main-half meshes.
- Four named aligned color solids per half: sixteen solids across both examples.
- One Anycubic Slicer Next project 3MF per half: four target-slicer projects.
- Exact source/profile/slicer/output hashes and a new output directory for every Anycubic run.
- No standard-only 3MF is accepted as the manufacturing handoff unless it independently passes the exact destination-slicer import gate.

## Fail-closed gates before production geometry

1. Freeze and hash a larger context source; prove projected coverage for every required semantic layer.
2. Solve per-mode interface locations inside an eroded retained body and inspect connector, hanger, standoff, lighting, attribution and watermark ligaments.
3. Preserve one global transform and split only after semantic construction, mask application and protected-interface registration.
4. Reuse the existing connector/standoff coupon geometry but keep process compensation physically unqualified until printed on the exact production setup.
5. Keep all meshes and 3MFs `DRAFT`; physical fit, ACE preview, appearance, watermark, wall installation and release remain human-controlled.

## Approval effect

Approval authorizes source acquisition/freezing, per-mode proxy/interface solving, parameterized production source, mesh generation, target-slicer project packaging and deterministic digital validation for both examples. It does not authorize printer upload/start, physical fit claims, electrical equipment, wall anchors, watermark approval or commercial release.
