# Concept review — MM-TOY-003 v0.1.0-r1

Concept asset: `trailcam-b2-balance-concept-v0.1.0-r1.png`

Specification authority: `../design-spec.yaml`, revision `0.1.0`

Status: `PENDING HUMAN CONCEPT APPROVAL`

## Requirement-to-feature correspondence

| Approved intent | Visible evidence in r1 | Review status |
|---|---|---|
| One geometric axis and exactly two wheels | Hero and exploded views show two total wheels; side view shows one near-wheel silhouette with the far wheel coaxially occluded | PASS for concept consistency |
| Independent balance and differential steering | Exploded view separates two coaxial motor pods; no mechanical differential or steering linkage is shown | PASS as architecture intent |
| No suspension, second axle or caster | Rigid motor/frame interfaces and no forbidden running gear appear in any panel | PASS |
| Compact inverted-pendulum body | Upright ribbed cage is centered between the wheels with its mass stack above the axle | PASS for massing only |
| Battery above axle and serviceable electronics | Side/cutaway and hero views expose the strapped battery and stacked removable controller/electronics trays | PASS for arrangement intent |
| Protected FPV camera | Orange forward camera guard and pale side-view field cone are visible | PASS |
| Independent RF/video placement | Two separated antenna mounts are visible; electrical independence is not image-verifiable | REVIEW_REQUIRED in later electrical architecture |
| Non-rolling landing protection | Orange front/rear protective members are visible and have no rollers | PASS for feature presence; exact clearance remains CAD-owned |
| TrailCam-related visual language | Graphite open FDM ribs, black purchased parts, orange guards and studio presentation relate to MM-TOY-002 without copying its chassis | PASS |

## Deliberate simplifications and ambiguity

- The image is generated concept art. It is not dimensional evidence and does
  not prove the 260 x 190 x 250 mm envelope or a center of mass 70–110 mm above
  the axis.
- Purchased wheels, motors, encoders, hubs, battery, boards, camera and antennas
  are generic proxies. Exact products and measured envelopes remain unresolved.
- The visible landing-member gap is illustrative and may appear smaller than
  intended. CAD must enforce no contact through +/-12 degrees and the declared
  22 degree minimum landing-contact tilt.
- Board stacking, cable routing, cooling, motor alignment and the pale camera
  cone are appearance cues only.
- No balance performance, torque, structural strength, printability or safety
  conclusion may be inferred from this render.

## Approval consequence

Approving r1 freezes the shown architecture and appearance direction for the
next decomposition phase: two coaxial wheels/motors, compact upright ribbed
core, mass above the axle, protected front camera, separated antennas and
non-rolling landing protection. It does not approve exact component selection,
dimensions, CAD, manufacturing, firmware, physical operation or release.
