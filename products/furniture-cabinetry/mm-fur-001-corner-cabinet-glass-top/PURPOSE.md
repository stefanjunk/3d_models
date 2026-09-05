# Purpose — MM-FUR-001 Corner cabinet with glass display top (Eckkommode)

**Assessed revision: 0.2.0 · Release state: CONCEPT_ONLY · Preflight: Lane E, C3 / R1 / K2**

## What this product is

A single, owner-commissioned piece of built furniture: a 1000 mm high corner
cabinet that fills a right-angled room niche whose two walls are nominally 1 m
wide. The footprint is a pentagon — two sides run along the walls, two short
returns close the ends, and the fifth side is one flat 45° diagonal front.

That diagonal front carries four doors, 539 × 439 mm, in a 2 × 2 grid. Both
doors of a row hinge on the central vertical partition, so they open outwards
from the middle and the *parked* open door stays inside the 1 m niche — though
the swept path does reach 130 mm past each wall end, which is the clear space
the room has to provide. A fixed mid shelf at the door-division height splits
the interior into two 423 mm compartments and ties the 1082 mm wide front
together. Six adjustable 100 mm feet hold the lower doors clear of the floor.

Revision 0.2.0 shortened the side returns from 340 to 200 mm on owner request so
the cabinet projects less into the room: the front now stands 131 mm past the
line joining the two wall ends instead of 230 mm. The legs stay at 965 mm, so
the niche is still filled. The cost of that trade is door width — 440 mm became
539 mm, because shortening a side return widens the diagonal front by √2 mm per
millimetre.

At exactly 1000 mm sits a flat timber top plate with no holes in it at all, and
laid loose on top of that is a five-sided 6 mm toughened glass plate. Postcards
and other flat paper go between the two.

## Intended use and scope limits

- Indoor, dry, heated living space. One unit, one niche, adult users.
- Storage of ordinary household items; display of flat paper under the glass.
- **Manufacturing route is timber panel cutting, not 3D printing.** There is no
  printed part, no nozzle, no slicer profile and no mesh in this product. The
  FDM calibration gate, mesh-simplification gate and slicer dry run are
  `not-applicable`, and are recorded as such rather than left blank.
- Not in scope: wall anchoring as a structural load path, lighting, electrics,
  locks, drawers, and any commercial release of either the design or the object.

## Evidence basis — read this before cutting anything

The design is fully parametric and internally consistent, but it rests on **one
unmeasured datum**: the niche. Both wall widths, the corner angle, the wall
flatness, the skirting-board thickness and the floor level are owner-stated or
unknown. Every one of the thirteen panel sizes and every hole position derives
from that datum.

The preflight therefore fails hard gate G2 and places the work in Lane E with
`CONCEPT_ONLY`. What is released here is a complete, dimensioned, parametric
build package. What is **not** released is permission to cut panels or order
glass.

To close it: measure the niche, put the measured values into
`source/params.yaml`, re-run `source/corner_cabinet.py`, and re-read the cut
list. That single measurement session lifts readiness to R3 or better and moves
the project to Lane C.

Two further blocking rules, both recorded in the preflight:

- **Toughened glass cannot be recut.** Build and paint the carcass, level it in
  place, measure the finished top plate, and only then order the glass.
- **The glass safety specification is not a finish option.** ESG, polished
  edges and ground corners must appear on the order; the plate is lifted by
  hand at every card change.

## Authoritative artifacts

| Question | File |
|---|---|
| What do I have cut, and how big? | `exports/cut-list.csv` |
| Where does every hole go? | `exports/drill-plan.csv` |
| Where do the panels land on each other? | `exports/layout-lines.csv` |
| What do I buy, and roughly what does it cost? | `bom.yaml` |
| How do I build it? | `docs/bauanleitung.md` |
| Outlines for the cut service and the glazier | `exports/dxf/` |
| Drawings | `exports/drawings/` |
| Concept image and its provenance | `renders/concept-r2/`, `evidence/imagegen-record-r2.json` |
| Why the design is the way it is | `decision-log.md` |
| What is still unknown | `preflight/preflight-report.md` |

Nothing in `exports/` may be hand-edited. Change `source/params.yaml` and
re-run the generator; every dimension is derived.
