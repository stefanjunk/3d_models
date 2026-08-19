# Geometry, parting, and demolding

A cavity is not a usable mold until every mold part and the cast have a collision-free removal path.

## Vocabulary

- **Pull direction:** translation direction used to remove a mold section or cast.
- **Parting surface:** interface between mold parts; it need not be planar.
- **Parting line:** trace of the parting surface on the article.
- **Undercut:** geometry that mechanically locks the cast or another mold part relative to its pull path.
- **Draft:** intentional taper that increases clearance during removal.
- **Core:** tool element that creates an internal void.
- **Loose piece:** separately removable insert that resolves a local undercut.
- **Witness/seam:** mark transferred from a parting line, gate, vent, or insert.

## A practical pull-direction analysis

For each proposed mold section:

1. Choose a candidate pull vector.
2. Project the article silhouette along that vector.
3. Identify surfaces facing away from the pull and pockets hidden behind the silhouette.
4. Sweep the mold section along the full extraction distance and check intersection with the article and neighboring sections.
5. Repeat after adding draft, keys, flanges, and the actual cast wall thickness.
6. Inspect the inverse operation: can the cast leave the assembled cavity after shrinkage or elastic deformation?

A face-normal “draft map” is useful but not sufficient. It cannot reliably identify all global shadowing, hooks, tunnels, or interlocking features. Use swept collision or incremental transformed-intersection checks for critical molds.

## Draft starting points

Draft depends on depth, texture, stiffness, surface finish, green strength, and mold material. For a rigid printed or plaster mold, begin with:

- smooth shallow walls: about 1–2°;
- deeper or visibly textured walls: about 3–5°;
- coarse texture, fragile greenware, or long draw depth: more draft or more mold sections.

These are prototype heuristics, not universal ceramic standards. A 30 mm-deep coarse relief can need more clearance than a 150 mm-high polished taper. Print a representative strip with the same depth and texture.

## Parting-line placement

Prefer:

- natural ridges, edges, corners, molding bands, or changes of ornament;
- hidden rear faces, the underside, or regions intended for trimming;
- low-curvature zones where seam sanding will not flatten detail;
- paths that minimize the number of undercuts and mold parts;
- parting surfaces that can be supported and sealed during mold manufacture.

Avoid:

- splitting through faces, lettering, narrow floral detail, or critical sealing rims;
- long zig-zag seams that are difficult to clamp and clean;
- paper-thin plaster knife edges;
- parting lines that form dams trapping air or slip;
- intersections where three or more mold parts meet without a deliberate assembly sequence.

## Planar versus sculpted parting surfaces

A planar split is easiest to model, print, seal, and clamp. Use it when it does not create undercuts or objectionable seams.

A sculpted parting surface can follow a crest line through organic geometry. It can reduce the part count and hide seams, but requires:

- a clean, non-self-intersecting surface;
- enough flange width on both sides;
- no reverse hooks along the pull direction;
- a clear assembly order;
- robust registration that does not scrape the cast.

## Registration keys

Use a deliberately asymmetric pattern. Common shapes:

- tapered round or conical keys for easy alignment;
- broad truncated pyramids for planar mold sections;
- tongue-and-groove rails for long seams;
- external dowel bushes where the casting face must remain clean.

Design rules:

- place keys in thick structural regions, not fragile edges;
- keep them clear of gates, vents, clamp pads, and pry points;
- provide printer/process clearance between male and female features;
- add lead-in chamfers and avoid sharp internal corners;
- use enough keys to prevent shear and rotation, but do not over-constrain warped parts;
- make at least one key different or offset so assembly cannot be reversed.

For FDM prototypes, a starting radial clearance of roughly 0.15–0.30 mm per side may be appropriate, but calibrate it on the actual printer, orientation, material, and post-finish.

## Flanges, clamps, and opening force

A reliable mold needs load paths. Add broad flanges around seams and locate clamp zones directly over ribs or bosses. Do not concentrate clamp force on thin cavity skins.

Provide controlled opening features:

- external pry tabs with rounded tool access;
- paired jacking-screw pads outside the casting area;
- threaded inserts only where they cannot leak or contaminate;
- lifting handles on heavy plaster sections;
- a cradle that supports the cast while the last section is removed.

Never drive a screwdriver into the casting seam itself.

## Sprues, reservoirs, vents, and drains

### Sprue/feed inlet

- Put the witness mark where it can be trimmed.
- Taper the channel toward the cavity to reduce locking.
- Use a removable printed funnel/spout when repeated cleanup would damage plaster.
- Avoid abrupt steps that trap bubbles or break greenware.

### Reservoir/spare

A reservoir above the article can keep the inlet full as material settles or as a slip-cast rim continues to build. It also gives an accessible place to top up. Make it removable without tearing the rim.

### Vents

Place vents at every local high point in the actual fill orientation. A single top vent cannot clear a separated air pocket. Use the shortest path possible and make it cleanable.

### Drain path

For hollow casting, prove that all liquid reaches the drain when the mold is inverted. Avoid shelves that retain pools. Design a drain stand so the mold is stable and drips into a controlled container.

## Thin walls and knife edges

A negative mold can create thin blades where two cavity surfaces approach. These print poorly, chip in plaster, and cause casting defects. Add:

- minimum edge radii;
- local thickening outside the article surface;
- removable inserts instead of fragile permanent blades;
- deliberate trim stock on the cast rather than attempting a perfect zero-thickness rim.

## Closed loops and trapped cores

Handles, chain links, pierced ornament, and closed internal channels cannot be demolded by simple two-part tooling. Options:

- split the article into separately cast pieces;
- use a loose core with a defined removal order;
- use a flexible or collapsible core;
- use a soluble/sacrificial core;
- redesign the feature as a blind relief rather than a through-hole.

Document the assembly and removal sequence as numbered steps before printing.

## Demolding proof record

For each mold part, save:

```yaml
part: capital_front_left
pull_vector: [0, -1, 0]
removal_order: 3
minimum_clearance_mm: 0.8
resolved_undercuts:
  - acanthus_leaf_07: loose_insert_A
remaining_risks:
  - fragile_green_tip_near_z_242
witness_surfaces:
  - rear_leaf_valley
```

A screenshot of the exploded assembly is helpful, but it is not a substitute for collision checking.
