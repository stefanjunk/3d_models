# MM-FUR-001 — Corner cabinet with glass display top (Eckkommode)

`C3 (55.75) | R1 | K2 | Lane E | LOW_UNKNOWN | CONCEPT_ONLY | revision 0.2.0`

1000 mm high pentagonal corner cabinet for a right-angled niche with two
nominally 1 m walls. One flat 45° diagonal front, 1081.9 mm wide, with four
identical 539 × 439 × 18 mm doors in a 2 × 2 grid on centre-mounted half-overlay
cup hinges. Fixed mid shelf, two 423 mm compartments, six adjustable 100 mm feet,
and a hole-free timber top plate at exactly 1000 mm carrying a loose five-sided
6 mm ESG glass plate for displaying postcards. The front stands 131 mm past the
line joining the two wall ends; the doors sweep a 539 mm radius quarter circle
that reaches 130 mm beyond each wall end.

**Not a 3D print.** Manufacturing route is a DIY-store panel cutting service plus
hand assembly. No printed part, nozzle, slicer profile or mesh exists in this
product.

## Start here

1. `PURPOSE.md` — what it is, scope limits, and why the release state is
   `CONCEPT_ONLY`.
2. `docs/bauanleitung.md` — the build manual (German). **Step 0 is mandatory:
   measure the niche.**
3. `exports/cut-list.csv` and `exports/drill-plan.csv` — the authoritative
   numbers.
4. `bom.yaml` — what to buy, with cost estimates.

## Layout

```
source/params.yaml            every input parameter; the only file you edit
source/corner_cabinet.py      generates the cut list, drill plan, DXF, STEP/STL
source/drawings.py            generates the five drawings
source/checks.py              19 deterministic geometry checks, fail-closed
exports/cut-list.csv          13 blanks: sizes, thickness, cut notes, drill datums
exports/drill-plan.csv        54 holes: part, face, x, y, diameter, depth
exports/layout-lines.csv      where each panel lands on its neighbour
exports/geometry-summary.json all derived geometry, material and mass figures
exports/geometry-checks.json  geometry check results (19/19 PASS)
exports/dxf/                  one outline per part, incl. P11-glass.dxf for the glazier
exports/drawings/             plan, front elevation, section, panel plan, drill patterns
exports/MM-FUR-001-assembly.{step,stl}   visualization and collision check only
renders/concept-r2/           current concept image (0.2.0), prompt, event stream
renders/concept-r1/           superseded concept image (0.1.0 proportions)
evidence/imagegen-record*.json  concept-image provenance and terms basis
preflight/                    C/R/K assessment, interface register, FMEA, gates
design-spec.yaml              requirements, loads, acceptance criteria A-01…A-10
decision-log.md               16 decisions with their alternatives
commercial-clearance/         rights and provenance workspace (status BLOCK)
```

## Regenerating

```bash
python3 source/corner_cabinet.py     # all exports
python3 source/drawings.py           # all drawings
python3 source/checks.py             # geometry checks; exits 1 on any failure
```

Nothing in `exports/` may be hand-edited — every value is derived from
`source/params.yaml`.

## Open blockers

- **The niche is unmeasured.** Both wall widths, corner angle, wall flatness and
  skirting thickness are owner-stated or unknown, and every panel size derives
  from them. Do not cut anything before closing acceptance criterion A-01.
- **Toughened glass cannot be recut.** Build, paint, level, measure the finished
  top plate, then order.
- The concrete cup-hinge article, the foot load rating and the store's
  diagonal-cut capability are unconfirmed.
- All ten acceptance criteria are `NOT_RUN`. Nothing has been built.
