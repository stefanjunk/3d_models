# Retrospective 3D-design preflight — MM-ART-010 Berlin

`Berlin wall relief | C3 (59.0/100) | R2 | K2 | Lane C | LOW_UNKNOWN`

## Decision

- Design route: `GO_WITH_CONTROLS` through concept approval, coupon-first interface CAD and controlled validation.
- Release remains blocked until exact filament/profile evidence, connector/snap coupons, assembled proof testing and human appearance review pass.
- This is a retrospective update of the earlier backfill after the approved connector-interface change; no historical measurement was inferred.

## Main drivers and interfaces

- Fit-sensitive concealed one-way center connectors and snap-in local wall standoffs.
- Coupled global map/color registration, one visible seam and protected lighting apertures.
- Four-color large-format FDM plus connector, mounting, light and appearance tests.

| Interface | Evidence | Criticality | Planned evidence |
|---|---:|---:|---|
| Glue-free one-way center seam | E1 | K2 | multi-clearance connector coupon |
| Local hanger/standoffs to wall | E1 | K2 | socket coupon and assembled proof load |
| Optional customer LED keep-outs | E1 | K2 | passive envelope/light gauge |

## Hard gates

`G0 PASS · G1 PASS · G2 WARN · G3 WARN · G4 PASS · G5 PASS · G6 PASS`

The warnings preserve unknown connector clearance, exact filament/profile identity, as-built mass and wall-anchor/substrate conditions. They permit the controlled concept/CAD path but not final release.

Canonical evidence: `preflight-result.json`; input trace: `preflight-input.yaml`.
