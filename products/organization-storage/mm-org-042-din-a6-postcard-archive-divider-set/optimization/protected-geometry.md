# MM-ORG-042 — protected geometry map and optimization constraints

Written before any lightweighting variant was generated. Baseline master:
`source/divider.py` → `source/generated/divider-block.stl`
(sha256 `e0d437c30ed9516fd42f0ea13429c730144ad5e61822f2e39f286454f2e23928`, 7124 triangles).

## Why infill is not a lever here

`scripts/plan_shell_ribs.py` at the exact process (0.4 mm nozzle, 0.42 mm line width,
0.20 mm layer, `wall_loops: 4`, arachne) reports for the 1.6 mm divider plate:

| quantity | value |
|---|---|
| wall depth per side | 1.551 mm |
| combined opposing wall depth | 3.102 mm |
| remaining infill core | −1.502 mm |
| status | `NO_INFILL_CORE` |
| `infill_percentage_can_change_bulk` | `false` |

Confirmed against the baseline G-code: extruded volume 93 283.9 mm³ versus CAD solid
volume 93 961.0 mm³ — 99.3 %. The part is deposited essentially solid because every
wall is thinner than two opposing 4-line wall stacks, and the 2.0 mm floor is thinner
than `bottom_shell_thickness` + `top_shell_thickness` (1.2 + 1.2 = 2.4 mm). Changing
`sparse_infill_density` from its 5 % setting cannot move material on this part.
Material can only come out of the *geometry* or out of the *layer count*.

## Where the material actually is

| region | volume mm³ | share |
|---|---:|---:|
| 7 divider walls (2 outer + 5 internal), 1.6 × 45 × 105.6 | 53 222 | 56.6 % |
| floor, 133.6 × 108.8 × 2.0 | 29 071 | 30.9 % |
| rear wall spine, 133.6 × 1.6 × 45 | 9 619 | 10.2 % |
| 6 index tabs, 18 × 1.6 × 12 | 2 074 | 2.2 % |

## Protected — no variant may change these

| region | why | source |
|---|---|---|
| lane clear length 105.6 mm along the card edge | A6 105 mm nominal + named clearance | `IF-EXT-GEO-LOC-SLOT-001` DIM-A6-W-001, datum A |
| lane floor top face (card seating plane) | datum B | `IF-EXT-GEO-LOC-SLOT-001` |
| divider inner faces (card sliding surfaces) | loose guided slot, no clamping | `IF-EXT-GEO-LOC-SLOT-001` assembly |
| continuity of every divider wall across the full lane length | constrained DOF "cards falling between lanes" | `IF-EXT-GEO-LOC-SLOT-001` |
| rear wall spine | ties all 7 divider walls; carries the index tabs | structural |
| index tab faces, 18 × 12 mm blank | labelling function | `IF-HUM-GEO-ACC-EDGE-001` |
| flat underside (bed face) | support-free printing, drawer seating | manufacturing |
| outer envelope ≤ 220 × 180 × 80 mm | customer drawer | `IF-EXT-GEO-CON-VOLUME-001` |
| `lane_clearance_mm` = 0.60 `UNQUALIFIED_PROVISIONAL` | calibration registry returns `NO_MATCHING_PROCESS` | `parameters/divider.json` |

**No through-windows in the divider walls.** A window in an internal divider opens a
path between adjacent lanes, and "cards falling between lanes" is an explicitly
constrained degree of freedom. The usual organizer lever — large radiused windows plus
straps — is therefore rejected here on a functional constraint, not on cost.

## Redundant bulk — removal candidates

| region | lever | risk |
|---|---|---|
| floor thickness above the 1.2 mm bottom shell | 2.0 → 1.4 mm | low: the floor spans only 20.4 mm between walls; block stiffness comes from the 45 mm deep walls, not the floor |
| internal divider thickness above `minimum_wall_mm` | 1.6 → 1.35 mm | low: still ≥ minimum wall; widens the lane clear width 20.4 → 20.61 mm, which only adds card capacity |
| upper front corner of every divider | scoop from 45 mm at the rear down to 22 mm at the open side over 75 mm | medium: reduces card retention at the open side; it is also the classic index-card-file scoop and improves the allowed "browsing by tilting cards forward" DOF. Visible change → concept re-approval required |

## Rejected before slicing

- **Floor windows / grid floor.** Cards would reach the drawer bottom through the
  openings and sit at unequal heights; loose contents would fall through.
- **Divider through-windows.** See above — violates a constrained DOF.
- **Lane depth reduction 45 → 38 mm.** 26 % engagement on a 148 mm card is not
  supportable without a physical stability test; the coupon programme for this product
  does not cover it.
- **Infill density change.** `NO_INFILL_CORE`; no core exists to make sparser.
