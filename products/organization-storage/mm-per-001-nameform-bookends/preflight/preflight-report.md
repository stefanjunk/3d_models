# Prospective 3D-design preflight — NameForm 0.4.1

`NameForm letter-dominant split-pair bookends | C3 (41.25/100) | R3 | K1 | Lane C | CONDITIONAL`

Assessment: `PREFLIGHT-MM-PER-001-008`, version `0.4.4`.

## Decision

- Design route: `GO_WITH_CONTROLS` through the sectioned concept and coupon gates.
- The 0.4.1 reinforcement requirements are approved; the generated reinforced concept is still pending human concept approval.
- Production CAD, manufacturing exports, and release remain blocked until concept approval, a process-matched glyph/connector coupon, exact slicing, and complete-pair physical tests pass.

## Assessed revision

The 0.4.1 proposal preserves the letter-dominant `MA | RITA` appearance, the retained side-blade/inward-foot book-load path, and the physically preferred direct-sampled candidate-C texture on glyph fronts. It changes the insufficiently stable-looking 0.4.0 facade to:

- 12.0 mm glyph depth;
- a 4.0 mm rear connector beginning 10.0 mm behind the front datum;
- at least 2.0 mm positive glyph/connector overlap;
- at least 12.0 mm local bridge bands;
- at least 1.2 mm finished glyph gaps, open counters, and no rectangular front panel.

The concept image makes this architecture reviewable but is not dimensional CAD or strength evidence.

## Complexity and readiness

| Dimension | Result | Boundary |
|---|---:|---|
| Complexity | C3 · 41.25/100 | Personalized glyph layout, hidden connection, texture, load path, and verification are coupled. |
| Readiness | R3 · 76% | Scope, requirements, process route, and nominal interfaces are defined; the changed connection lacks generated and physical evidence. |
| Criticality | K1 | Credible failures are appearance/function loss, limited item damage, or a sharp decorative break edge. |
| Lane | C | Iterative engineering with concept, coupon, slice, and pair-test controls. |

Readiness does not advance beyond R3 because the 0.4.1 connector has no measured deflection/fracture result and the exact filament product, batch, conditioning, and complete profile remain unknown.

## Interface register

| Contract | Interface | Evidence | Criticality | Required verification |
|---|---|---:|---:|---|
| `IF-EXT-MEC-SUP-PLN-001` | Inward foot to shelf | E3 | K1 | complete-pair test |
| `IF-EXT-MEC-LOD-PLN-002` | Side blade/foot to book row | E3 | K1 | representative proof load |
| `IF-INT-MEC-FST-EDGE-001` | Reinforced glyph facade to core | E1 | K1 | sectioned concept, generated-body checks, and connector coupon |
| `IF-HUM-OPT-VIS-BODY-001` | Letter-only wood appearance | E3 | K0 | concept and textured-letter review |

## Hard gates

`G0 PASS · G1 PASS · G2 WARN · G3 WARN · G4 PASS · G5 PASS · G6 PASS`

- `G2 WARN`: the revised connector remains requirement/concept evidence only.
- `G3 WARN`: printer, nozzle, layer height, and orientation are known, but the exact successful filament/profile identity is incomplete.
- The remaining gates permit controlled concept work; they do not authorize production geometry or release.

## Required next evidence

1. Obtain explicit human approval for `concept/nameform-bookends-v0.4.1-reinforced-concept.png` against the approved dimensions.
2. Generate and test one reinforced glyph/bridge coupon; require visible gaps, open counters, one connected body, recognizable candidate-C texture, and the approved handling/deflection result.
3. Rebuild, exactly slice, and physically test the complete `MA | RITA` pair before release.

Previous assessment: `PREFLIGHT-MM-PER-001-007`. Canonical machine-readable evidence: `preflight-result.json`; input trace: `preflight-input.yaml`.
