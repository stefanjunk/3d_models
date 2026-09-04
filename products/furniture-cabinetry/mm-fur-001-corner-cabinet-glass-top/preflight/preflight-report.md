# Preflight report — MM-FUR-001 Corner cabinet with glass display top

`MM-FUR-001 Eckkommode | C3 (55.75/100) | R1 | K2 | Lane E | LOW_UNKNOWN | CONCEPT_ONLY`

Assessment `PF-MM-FUR-001-2026-09-04-001` v1.0.0, mode `PROSPECTIVE`, 2026-09-04.
Machine-readable source: `preflight-result.json` (validates against the skill schema).

## 1. Decision and why

Complexity C3 and criticality K2 on their own would put this work in **Lane C**,
iterative engineering. It sits in **Lane E** instead, and the reason is narrow and
fixable: **readiness is R1** because the host niche — the single datum from which
all thirteen panel sizes and every hole position derive — exists only as a verbal
nominal ("both walls 1 m"), and the skirting-board clearance is at **E0**,
completely unknown. Hard gate **G2 fails**, and a failed hard gate forces Lane E.

What Lane E / `CONCEPT_ONLY` permits is exactly the requested deliverable: a
complete, dimensioned, parametric build package plus a concept image, generated
against an explicitly nominal 1000 × 1000 mm niche. What it does **not** permit is
cutting panels or ordering glass.

One measurement session closes it. Measuring both wall widths, the corner angle,
the wall flatness, the skirting and the floor lifts the three blocking interfaces
to E3, raises readiness to R3 or better, and moves the project to Lane C with
`CONDITIONAL` confidence. Nothing about the design has to change — the geometry is
parametric and re-derives from `source/params.yaml`.

## 2. A note on the schema

The preflight schema is written for FDM printing. Custom-cut timber panels are
recorded with `kind: PRINTED_PART`, which is the enum's nearest category for
"custom-fabricated part"; each such entity name says explicitly that it is cut
timber. There is no printed part, nozzle, slicer profile or mesh in this product,
and the FDM-specific gates are recorded as `not-applicable` in `design-spec.yaml`
rather than left blank. Warning code `NON_FDM_PROCESS` carries this.

## 3. Interface register

Eleven interfaces. Project INT score 3 derives from N=11, mean IC 9.6, max IC 14.

| ID | Interface | Ev. | IC / tier | K | Status |
|---|---|---|---|---|---|
| `IF-EXT-GEO-CLR-VOLUME-001` | Cabinet envelope → room niche | **E1** | 8 / I2 | K1 | **BLOCKING** |
| `IF-EXT-GEO-SUP-PLN-002` | Feet → floor: support, levelling, load | **E1** | 9 / I2 | K2 | **BLOCKING** |
| `IF-INT-KIN-ROT-CYL-003` | Door → centre partition, 35 mm cup hinge | E2 | **14 / I3** | K1 | open |
| `IF-EXT-KIN-KOT-VOLUME-004` | Open-door swing envelope → niche | E1 | 10 / I2 | K1 | analysed |
| `IF-EXT-GEO-SUP-PLN-005` | Glass plate → timber top plate | E2 | 12 / I3 | K2 | open |
| `IF-HUM-USR-USR-EDGE-006` | Glass edge/corners → user hand | E1 | 9 / I2 | K2 | purchase-spec |
| `IF-INT-GEO-LOD-PLN-007` | Mid shelf → battens and partition | E2 | 7 / I1 | K1 | open |
| `IF-EXT-GEO-CON-PLN-008` | Panel blanks → cutting-service capability | E2 | 7 / I1 | K1 | open |
| `IF-ENV-PHY-CON-BODY-009` | Panel material → indoor climate, flatness | E1 | **14 / I3** | K1 | open |
| `IF-HUM-USR-USR-VOLUME-010` | Stability → user, climbing, leaning | E1 | 9 / I2 | K2 | open |
| `IF-EXT-GEO-CLR-PLN-011` | Skirting / wall build-up → rear clearance | **E0** | 7 / I1 | K1 | **BLOCKING** |

The two hardest interfaces are worth naming. `-003` (IC 14) is hard because a
half-overlay cup hinge on a shared 18 mm partition couples the door size, the
reveal, the overlay, the plate position and the collision of mounting-plate screws
from both faces — the design resolves the last one by staggering the left and right
cup heights by 16 mm. `-009` (IC 14) is hard because the flatness the glass plate
depends on is a long-term timber-moisture property with no local evidence at all.

## 4. Functional FMEA (required at K2)

| Failure | Local effect | Final effect | Detection | Countermeasure in the design | Verification |
|---|---|---|---|---|---|
| Niche narrower or not square than assumed | Back panels bind | Cabinet does not go in; ~6.1 m² of panel scrap | Dry fit, too late | `back_gap` / `end_gap` / `leg` are parameters, not constants | A-01, A-03 |
| Skirting thicker than the 10 mm rear gap | Carcass stands off the wall | Front rotates out of the niche mouth; visible gap | Tape measure, before cutting | `back_gap = skirting + 3 mm`, or notch P03/P04 | A-01 |
| Floor out of level | Only 3 of 6 feet bear | Cabinet rocks; glass slides toward the low side | Spirit level | Height-adjustable feet; level the top plate, not the base | A-04 |
| Foot plate tears out of the 18 mm bottom panel | Local panel failure | Corner drops | Visible sag | 4-screw plate feet placed near the vertical panels; screw positions kept ≥ 45 mm clear of every foot | A-04 |
| Top plate cups | Rigid glass bears on 3 points | Glass rocks, cards will not lie flat, bending stress in the glass | Straightedge | Cross-banded plywood specified; both faces and all edges sealed equally | A-05, A-10 |
| Glass ordered before the top plate is measured | — | ESG cannot be recut; plate is scrap | — | Hard rule in `PURPOSE.md` and `bom.yaml`: build, level, measure, then order | A-05, A-07 |
| Sharp glass edge or point corner | — | Cut to hand at every card exchange | Hand inspection | ESG + polished edges + ground corners written into the order as a requirement, not a finish option | A-07 |
| Half-overlay range misses 7.5 mm | Doors touch or gap opens | Front looks wrong, doors rub | First door hung | Door gap is a parameter; hinge overlay is adjustable ±2 mm | A-06 |
| Cup hole breaks through the door | Visible damage on the show face | Door scrap | During drilling | Cup depth 12.5 mm in 18 mm leaves 5.5 mm; depth stop mandatory | A-06 |
| Mounting-plate screws collide inside the partition | Split panel, loose plate | Door drops | During drilling | Left/right cup heights staggered 16 mm; no hole pair is coaxial | A-06 |
| Child climbs an open lower door | Hinge or door overload | Possible tipping | — | Deep footprint, ~81 kg mass; optional anti-tip bracket | A-09 |
| Mid shelf creeps under load | Sagging shelf | Upper partition drops, reveals close | Straightedge over years | Perimeter battens on all four surrounding panels plus the partition; field ≤ 450 mm | A-08 |
| Store will not cut the three diagonals | — | Pentagon panels unbuildable there | Ask at the counter | Each diagonal is ONE straight cut from a square blank; guide-rail fallback documented | A-02 |

## 5. Hard gates

| Gate | Result | Reason |
|---|---|---|
| G0 scope / variant / use known | **WARN** | Scope and use are clear; the host variant is a nominal only |
| G1 entities and interfaces discovered | PASS | 13 entities, 11 interfaces with contracts |
| G2 critical evidence sufficient | **FAIL** | Niche at E1, skirting at E0, floor at E1 |
| G3 material / process known | **WARN** | Material, thickness and cut route documented from named sources; the store's diagonal-cut capability and the hinge article are unconfirmed |
| G4 acceptance criteria and methods defined | PASS | Ten criteria, A-01…A-10, all with a method |
| G5 criticality admissible for the workflow | PASS | K2 |
| G6 assembly, service, lifecycle considered | PASS | In-place assembly at ~81 kg, hinge readjustment after one heating season, shelf and glass removable, no bonded-in hardware |

## 6. Warnings

- `VARIANT_UNKNOWN` **BLOCKER** — the niche is the only dimensional datum and is unmeasured.
- `CRITICAL_INTERFACE_UNKNOWN` **BLOCKER** — skirting E0; floor level and foot rating E1.
- `AUTONOMOUS_RELEASE_PROHIBITED` **BLOCKER** — Lane E; no agent may record a release, build approval or glass order.
- `HIDDEN_GEOMETRY` WARN — wall build-up behind the skirting, plaster fillets, floor covering.
- `PURCHASED_PART_REVISION_UNKNOWN` WARN — hinge, foot, handle and glass articles specified by function only.
- `GLASS_INJURY_RISK` WARN — 11 kg plate handled by hand; the safety spec lives on the order.
- `DYNAMIC_OR_FATIGUE_LOAD` INFO — door hinge cycles and long-term shelf creep, neither tested.
- `NON_FDM_PROCESS` INFO — the FDM gates are not applicable and are recorded as such.

## 7. Minimum next proof

**Measure the niche.** One session, a tape measure, a 1 m straightedge, an angle
finder and a spirit level. Exit criterion: a measurement record in this folder,
`source/params.yaml` updated, the generator re-run, and
`IF-EXT-GEO-CLR-VOLUME-001` plus `IF-EXT-GEO-CLR-PLN-011` at E3.

Everything else in `preflight-result.json → next_actions` follows in order:
re-generate, fix the hinge article, confirm the cut service, build and level, then
measure the top plate and order the glass, then run the physical acceptance set.

## 8. Recommended path

Lane C once the measurement gate closes: build the carcass first, prove the door
reveal on one door before drilling the other three, and treat the glass as the last
purchase in the project rather than the first.
