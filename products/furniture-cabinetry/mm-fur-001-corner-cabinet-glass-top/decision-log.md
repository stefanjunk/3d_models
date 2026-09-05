# Decision log — MM-FUR-001

Revision 0.1.0, 2026-09-04. Each entry records what was decided, what it was
decided against, and what would overturn it.

## D-01 — Footprint: pentagon with one flat 45° diagonal front

**Decided:** two sides along the walls, two short 340 mm returns, one flat
diagonal front, 883.9 mm wide.
**Against:** a full right triangle (front 1365 mm → doors 680 mm wide, absurd
swing) and a rectangular box set diagonally with triangular fillers (needs a
separate rear support frame for the cantilevered top plate, more parts).
**Why:** a 2 × 2 door grid is only coherent on a single plane, and the pentagon
lets the bottom, top and shelf be produced by *one* straight cut each from a
square blank.
**Overturned by:** a measured niche that is strongly asymmetric.

## D-02 — Doors hinge on the centre partition, not at the outer ends

**Decided:** half-overlay (Mittelanschlag) cup hinges on the central partition;
each row opens outward from the middle; handles on the outer door edges.
**Against:** conventional end hinging.
**Why:** computed swing envelope. End-hinged, the 90° door tip lands at
(1299, 655) mm from the corner — outside a 1 m niche. Centre-hinged it lands at
(973, 975) mm, inside. Both doors of a row open together to reveal the full
884 mm opening, which matters for a 923 mm deep corner cabinet.
**Cost of the choice:** needs half-overlay hinges, and the mounting plates on the
two partition faces have to be staggered — see D-06.

## D-03 — One panel thickness (18 mm) for everything

**Decided:** every carcass panel, door, shelf and partition is 18 mm.
**Against:** 12 mm hidden back panels (saves ~€25 and 20 kg), or a 22 mm top
plate for a heavier look.
**Why:** one material order, one cut service, one drill-depth regime, one hinge
geometry. The 18 mm back panels also carry the shelf battens and support the
rear of the top plate directly, which removes the need for wall-fixed cleats and
therefore any wall drilling. The lightweight variant (battens + 6 mm back skins
+ posts) is documented in `bom.yaml` but not dimensioned.
**Cost:** assembled mass ~81 kg. Mitigated by assembling in place.

## D-04 — Birch plywood as the specified material, not solid softwood

**Decided:** 18 mm birch plywood (Multiplex) for all panels; glued solid
spruce/pine offered as variant B.
**Against:** the literal reading of the brief, "weißes Echtholz", as Massivholz.
**Why:** flatness is a functional requirement, not a preference. A rigid 11 kg
glass plate lies directly on the top plate; a cupped plate makes the glass rock
and the cards will not lie flat (`IF-EXT-GEO-SUP-PLN-005`, IC 12). Cross-banded
plywood holds flat, single-layer glued softwood does not reliably. Plywood is
real wood — solid rotary-cut veneers, no fibre or chip board — and under opaque
white lacquer the species is invisible. Screw-holding in the panel edge is also
much better, which matters because 26 screws go into panel edges.
**Concession:** variant B is fully costed and uses the identical cut list. If it
is chosen, use plywood for P02 anyway and a shellac knot blocker.
**This is a recommendation over a user-stated preference and is flagged as such
in `design-spec.yaml → function.requirements.recommended`.**

## D-05 — Mid shelf is fixed and structural, not adjustable

**Decided:** one full inner-pentagon shelf, fixed at the door-division height on
perimeter battens, carrying the upper partition.
**Against:** a height-adjustable shelf on 5 mm pins, which would require a
full-height partition and split the shelf into two awkward quadrilaterals.
**Why:** the shelf height is *determined* by the 2 × 2 door layout, so
adjustability buys nothing; and as a fixed member it ties the 884 mm wide
diagonal front against racking and gives the upper partition a base. It also
keeps the shelf a single clean pentagon.
**Note:** "Einlegeboden" in the brief is read as "a shelf between the rows", not
as a demand for adjustability.

## D-06 — Left and right cup heights staggered by 16 mm

**Decided:** variant A cups at 88/351 mm from the door ends, variant B at
72/367 mm.
**Why:** Ø 5 mm mounting-plate holes 10 mm deep, drilled from both faces of an
18 mm partition, would total 20 mm and break through if coaxial. Staggering by
16 mm removes every coaxial pair while keeping both patterns symmetric on their
own door.
**Consequence:** 4 identical door blanks, 2 drill variants.

## D-07 — Top plate has no holes at all

**Decided:** P02 is fixed only by glue plus 8 angle brackets screwed from inside
with 16 mm screws.
**Against:** screwing down through the top, or dowels.
**Why:** it is the display surface under glass. Dowels were rejected as well —
they need a jig and precision for no benefit here, and the brackets are more
forgiving. The 11 kg glass plate holds the plate down anyway.

## D-08 — Six feet, positioned under the vertical panels, kept clear of screws

**Decided:** 6 adjustable feet; the front-centre foot sits under the partition,
55 mm behind the front plane.
**Why:** load path lands under the vertical panels rather than in the middle of
an 18 mm plate. The generator enforces a 45 mm keep-out between every carcass
screw and every foot centre — the first run put a foot dead-centre on a partition
screw at (613.6, 613.6).
**Levelling rule:** level the *top plate*, not the base, because the glass sits
on the top plate.

## D-09 — Glass: 6 mm ESG, loose, inset 2 mm, polished edges, ground corners

**Decided:** as above; no routed recess, no frame.
**Against:** a 2 mm routed recess (needs a router and template, out of scope for
a cut-service build) and a raised retaining frame (would prevent sliding the
cards in from the front).
**Why:** 10.9 kg plus friction holds it. Optional stainless stops at the two
wall-side edges are offered for the sliding concern, leaving the front edge free
for inserting cards.
**Not negotiable:** ESG rather than float glass, polished edges, ground corners.
The plate is lifted by hand at every card change, so the safety mitigation lives
entirely in the purchase specification.

## D-10 — Everything except the precision holes is drilled in place

**Decided:** the drill plan contains only the hinge cups, the mounting-plate
holes, the handle holes, the bottom-panel through-holes and the foot transfer
marks. Battens, brackets and edge pilots are drilled during dry assembly.
**Why:** drilling through an existing hole into a dry-assembled joint is more
accurate than any nominal, and it absorbs the ±1 mm cut tolerance instead of
fighting it. This is why P03–P06 and P08 have no pre-drilled holes.

## D-11 — Per-piece cut-to-size ordering over full sheets

**Decided:** order the 13 blanks individually (6.084 m²).
**Why:** computed. Three blanks are 927–965 mm wide; guillotine nesting on
2500 × 1250 sheets reaches only ~49 % utilisation and needs 4 sheets (12.5 m²).
The nesting result is in `exports/geometry-summary.json` and is honest about the
packer being a simple shelf algorithm — a careful manual nest reaches 3 sheets.

## D-12 — New product family `furniture-cabinetry`

**Decided:** a new family rather than filing this under `furniture-systems`.
**Why:** `furniture-systems` is defined in `products/README.md` as "one
self-contained package for each system-furniture SKU" — inserts that adapt an
existing host such as IKEA. This is the furniture itself, and its whole artifact
set differs: cut list, drill plan, hardware register, glass order; no nozzle,
slicer profile or mesh. `organization-storage` was considered and rejected as a
weaker fit.
**Also required:** a `family_base` score row in
`tools/backfill_product_preflights.py`, the host-object interface branch, and a
reviewed trend-family decision in `business/tools/score_product_directories.py`.
The trend decision is **None**: every research trend family in this repository
surveys 3D-printed products, so none is a truthful comparator for a cut-list
cabinet.

## D-13 — FDM-shaped schema fields filled with labelled surrogates

**Decided:** `printer.build_volume_mm: [2500, 1250, 18]` = the panel-stock
envelope; `manufacturing.nozzle_mm: 4.0` = the assumed saw kerf. Each carries a
`SURROGATE_NOTE` on the following line. `branding.depth_mm` is set to the schema
default and marked not applicable.
**Against:** leaving the required fields blank and letting
`validate_design_spec.py` fail.
**Why:** the validator is fail-closed and other tooling depends on it. A
documented surrogate is visible; a blank field or a plausible fake FDM value is
not. The validator's residual warning "nonstandard nozzle" is expected and
correct — there is no nozzle.
**Overturned by:** a schema revision that admits non-FDM manufacturing routes.

## D-14 — Aggregate backfill tool NOT run

**Decided:** the audit entry in `products/PRODUCT-PREFLIGHT-AUDIT-2026-08-31.json`
and its markdown table row were added by hand.
**Why:** the dry run of `tools/backfill_product_preflights.py` proposed writing
33 files across `art-decor/mm-art-001/004/006/010`, `home-kitchen-garden/
mm-bth-003` and two `organization-storage` products — concurrent work by other
sessions — and would also have overwritten this product's own hand-written
preflight and created a competing `design-spec.yaml`. CLAUDE.md requires stopping
in exactly this case. `--write` was never run.

## D-15 — Concept image generated before the requirements gate was approved

**Recorded as a process deviation, not hidden.** The functional-design skill
wants the concept image after requirements approval. The owner brief explicitly
asked for a concept image, so one draft was generated in the same phase as the
requirements synthesis. `workflow.concept_approval.status` is therefore
`blocked`, and the image is labelled a draft for review. One candidate only, to
respect the shared Codex rate limit. Provenance:
`evidence/imagegen-record.json`. The image was **not** used as geometry input;
no dimension derives from it, so the deterministic alpha step did not apply.

## D-16 — Side returns shortened 340 → 200 mm (revision 0.2.0)

**Decided:** on owner request, shorten the side returns so the cabinet projects
less into the room. Legs stay at 965 mm.
**Measured first, then decided.** The number that actually mattered was not the
depth from the corner but how far the front stands past the line joining the two
wall ends: **230 mm, 248 mm including the door leaf**. A six-point sweep showed
the side return is a weak and expensive lever, because shortening it by 1 mm
widens the diagonal front by √2 mm:

| side return | projects past the wall ends | door width | top plate |
|---|---|---|---|
| 322 mm (0.1.0) | 230 mm | 440 mm | 0.736 m² |
| 182 mm (chosen) | 131 mm | 539 mm | 0.639 m² |
| 102 mm | 74 mm | 596 mm | 0.574 m² |

**Against:** shortening the legs together with the returns, which holds the doors
at 440 mm and reaches 67 mm projection at 850 mm legs, or 0 mm at 802 mm legs.
The owner chose to keep the niche filled and pay for it in door width.
**Consequences carried through:** doors 440 → 539 mm, front 884 → 1082 mm, depth
923 → 824 mm, top plate 0.736 → 0.639 m², glass 10.9 → 9.5 kg, assembled mass
81 → 76 kg, handle x 400 → 499 mm, side-return part 322 → 182 mm, batten L03
283 → 143 mm. The partition drill patterns are unchanged, because door height and
the vertical layout did not move.
**Open consequence:** the 539 mm door puts its centre of gravity 270 mm from the
hinge axis instead of 220 mm. The hinge article's door weight and width limit is
now part of the open purchased-part item, not only its overlay range.

## D-17 — Foot placement re-anchored to the front

**Decided:** the two front feet are positioned relative to the front plane
(150 mm in from each end, 70 mm behind the front) instead of relative to the side
return.
**Why:** the old rule placed them at `side_return − 35 mm` along the wall. With
the return cut to 182 mm they would have landed 130 mm from the rear feet and
stopped spreading the load. The new rule is stable for any return length; the
closest foot pair is now 252 mm apart.
**Guarded by:** new check C-19, which fails below 200 mm spacing or if any foot
plate leaves the bottom panel.

## D-18 — Swept door path added to the checks, and an earlier claim corrected

**Found:** check C-02 tested only the *parked* 90° door position and reported
"the door tip stays inside the niche". That was true but incomplete, and it was
stated that way in the revision 0.1.0 handoff. A hinged door must swing through
the room to get there.
**Corrected:** C-02 now says explicitly that it covers the end position only, and
new check **C-18** samples the whole 0→90° sweep at four points along each leaf.
It asserts what is genuinely assertable — the leaf never strikes either niche
wall — and reports the required clear space instead of pretending to pass or fail
against unmeasured surroundings: a 539 mm radius quarter circle about the front
midpoint, reaching 1130 mm along each wall direction, i.e. 130 mm past each 1 m
wall end, 1377 mm from the corner at its furthest.
**Note:** this was already true in revision 0.1.0 at a 440 mm radius reaching
1102 mm; the wider door made it worse and the incomplete check made it invisible.

## D-19 — Revision 0.2.0 landed inside another session's commit (provenance note)

**What happened:** the revision 0.2.0 files were staged, and before `git commit`
ran, a concurrent session in this shared worktree committed with a whole-tree
stage. All 44 staged MM-FUR-001 files, the audit-JSON revision bump and the
portfolio row were swept into **`b5056bd6` "MM-ART-010 v0.5.4: Anycubic 3MF
packaging and boundary-crop slices"**, which is not about this product at all.

**Verified before writing this:** all 69 files listed in `build-manifest.json`
hash-match `HEAD` exactly, `preflight-result.json` validates against project
revision 0.2.0, and `design-spec.yaml` validates with
`--require-current-preflight`. Nothing is lost or corrupted; only the commit
attribution is wrong.

**Not corrected by rewriting history.** `AGENTS.md` forbids force-pushing or
rewriting `main`, and the commit is already on `origin/main`. This entry is the
correction: if you are tracing why revision 0.2.0 has no commit of its own, it is
in `b5056bd6`, and the reasoning for the change itself is D-16 to D-18.

**For anyone else working in this worktree:** stage explicit paths. `git add -A`,
`git add .` and `git commit -a` in a worktree shared by several agent sessions
will absorb another session's staged work into your commit.
