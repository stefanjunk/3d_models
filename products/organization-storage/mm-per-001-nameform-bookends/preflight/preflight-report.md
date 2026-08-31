# Prospective 3D-design preflight — NameForm 0.4.0

`NameForm letter-dominant split-pair bookends | C3 (41.25/100) | R3 | K1 | Lane C | CONDITIONAL`

## Decision

- Release route: `GO_WITH_CONTROLS`
- Lane: `C — Iterative Engineering`
- The retained functional core and the physically preferred direct-sampled C
  texture make the redesign feasible.
- Requirements 0.4.0 are approved. Concept approval still gates CAD. The new
  rear connector, textured glyph geometry, exact slice, and complete pair
  remain test items.

## Assessed revision

The visible rectangular wing is replaced by large outline-packed glyphs. A
glyph-shaped rear layer and local bridges connect adjacent glyphs 6.0 mm behind
their front faces. The existing side blade and inward foot retain the book load;
the glyph facade remains visually and structurally secondary to that load path.

Candidate C is carried forward unchanged on glyph fronts:

- full 1254 x 1254 16-bit master sampled directly at mesh vertices;
- 120 x 45 mm physical patch and 24 px seam blend;
- 0.6 mm maximum front relief and 0.45 mm surface grid;
- upright front face pointing toward `-Y`;
- 0.4 mm nozzle and 0.12 mm layer height.

The physical statement “variant C already looks quite good” supports this route,
but exact filament identity, conditioning, complete profile, and the new glyph
mask remain unresolved.

## Complexity and readiness

| Dimension | Score | Rationale |
|---|---:|---|
| REQ | 3 | Appearance, personalized glyphs, hidden connection, load path, texture fidelity, and print limits are coupled. |
| CTX | 1 | One known indoor use context and one target printer dominate the current revision. |
| PAR | 2 | Two mirrored manufacturing parts contain logical functional-core and glyph-facade subsystems. |
| INT | 2 | Shelf, books, facade bond, and human visual/handling interfaces require separate acceptance. |
| CPL | 2 | Font, gap, bridge, texture mask, footprint, and side-blade junction share datums. |
| MOT | 0 | No mechanism. |
| GEO | 2 | Vector glyphs, local connector synthesis, and masked image relief are more than simple primitives. |
| PHY | 1 | Modest static book load and handling only. |
| MAT | 2 | Upright FFF orientation and appearance are process/material sensitive. |
| EXT | 0 | No purchased parts or electronics. |
| VER | 3 | Deterministic checks plus texture, connector, handling, and full-pair physical tests are required. |

Readiness is `R3`: scope, requirements, and manufacturing route are defined,
but the generated concept still awaits approval and the glyph connector has no
CAD or physical evidence.

## Interface register

| Contract | Interface | Evidence | Criticality | Verification |
|---|---|---:|---:|---|
| `IF-EXT-MEC-SUP-PLN-001` | Inward foot to shelf | E3 | K1 | planned pair test |
| `IF-EXT-MEC-LOD-PLN-002` | Side blade/foot to book row | E3 | K1 | planned proof load |
| `IF-INT-MEC-FST-EDGE-001` | Glyph facade to core | E1 | K1 | planned connector coupon |
| `IF-HUM-OPT-VIS-BODY-001` | Letter-only wood appearance | E3 | K0 | planned concept and textured-letter review |

## Hard gates

| Gate | Status | Reason |
|---|---|---|
| G0 | PASS | Product, user, default text, and indoor use are defined. |
| G1 | PASS | Functional, structural, host, and visual interfaces are registered. |
| G2 | WARN | The new connector has requirement-level evidence only. |
| G3 | WARN | Printer/nozzle/layer/orientation are known; exact physical-C filament and full profile are not. |
| G4 | PASS | Requirements 0.4.0 and their measurable acceptance methods are approved. |
| G5 | PASS | K1 permits Lane C with physical gates. |
| G6 | PASS | Transport, handling, cleaning, service, and storage are included. |

## Required next evidence

1. Approve the generated concept sheet with front, rear three-quarter, and connector section.
2. Print one representative textured glyph/bridge coupon; require visible gaps,
   open counters, one connected body, recognizable C texture, and handling pass.
3. Build, exactly slice, and physically test the complete pair before release.

The preceding prospective assessment is `PREFLIGHT-MM-PER-001-002`; this
post-requirements Gate 0B update is `PREFLIGHT-MM-PER-001-003`.
