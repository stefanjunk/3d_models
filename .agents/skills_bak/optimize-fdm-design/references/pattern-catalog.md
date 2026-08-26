# FDM time- and material-efficient pattern catalog

## Contents

- [Selection principle](#selection-principle)
- [Core structural patterns](#core-structural-patterns)
- [Path-compatible dimensions](#path-compatible-dimensions)
- [Support and toolpath patterns](#support-and-toolpath-patterns)
- [Exposed infill lattice](#exposed-infill-lattice)
- [Patterns to avoid](#patterns-to-avoid)
- [Verification questions](#verification-questions)

## Selection principle

Replace material only after identifying what it does. A successful FDM pattern carries the required load through continuous extrusions, supports top surfaces, protects interfaces, and prints without excessive support or short fragmented paths.

Use a pattern because it matches a load or manufacturing role—not because it looks generatively optimized.

## Core structural patterns

| Pattern | Use | Time/material benefit | Main risks | Required check |
|---|---|---|---|---|
| Thin shell plus ribs | Tray, organizer, housing, broad side wall | Removes internal bulk while keeping surface and bending stiffness | Rib-root cracking, local wall print-through, too many ribs | Deflection, root radius, wall paths, slicer time |
| Large radiused windows plus straps | Hidden drawer sides, rack webs, covers | Removes full-height wall area | Shear/torsion loss, snagging, corner cracks | Load directions, diagonal/edge continuity, edge comfort |
| Ribbed skin/floor | Drawer/tray bottoms, panels | Thin closed skin spans only between ribs | Rib telegraphing, sagging, warp, poor first layer | Span coupon, bottom flatness, load distribution |
| Hollow box or hat section | Long beams, racks, stands, bars | High bending/torsional stiffness per mass | Unsupported internal roof, trapped support | Orientation, bridges, diaphragms, drainage |
| Edge beam/flange | Tray rim, panel perimeter, rack rail | Moves material away from neutral axis | Warp, bulky corner junctions | Corner radius, bed adhesion, local section |
| Diaphragm/bulkhead | Long hollow section, duct, filter body | Stabilizes shell against ovalization/buckling | Blocks flow/cleaning, inaccessible cavity | Spacing by load, access, drain path |
| Triangular gusset | Wall/base, boss, bracket transition | Short direct load path with little volume | Unsupported lower face, sharp root | Self-supporting angle, root fillet, stress path |
| Local pad/boss | Screws, inserts, bearings, magnets, rail ends | Concentrates material only at interface | Stress concentration, heat-set damage | Pull-out/bearing coupon, tool access, wall tie-in |
| Tapered transition | Thick-to-thin load transfer | Avoids abrupt stress and thermal/mass change | Long overhang if oriented poorly | Section gradient, orientation, slicer paths |
| Corrugation/fold | Long thin panels, clip bars | Raises section stiffness without thickening | Cosmetic ripple, cleaning difficulty | Print direction, minimum radius, contact surfaces |
| Replaceable wear insert | Guides, pusher edges, bushings, seals | Keeps main body light and serviceable | Assembly complexity, loose part | Retention, wear test, replacement access |
| Open frame with skins only where needed | Stands, docks, equipment frames | Removes nonfunctional enclosure area | Torsion, cable snagging, appearance | Bracing, edge comfort, tip stability |
| Framed exposed infill | Porous screens, lamp panels, vents, decorative or flexible inserts | Creates repeatable nozzle-scale strands without modeled cell geometry | Weak/ragged edges, pattern loss outside slicer project, crossing buildup | Exact 3MF/profile, layer preview, frame-joint coupon |

### Thin shell plus ribs

Use a continuous skin to define the outer surface and ribs on the hidden or low-cosmetic side. Align ribs with known bending/shear paths. Add edge beams around large openings and fillet every rib root.

Do not copy injection-molding rib ratios blindly. FDM ribs are extrusion paths with anisotropic joints, layer seams, and minimum path widths. Start with two or three printable paths and validate the actual section.

### Large windows plus straps

Prefer a small number of large rounded openings. Orient their long axes and remaining straps for the print orientation and known load/shear paths. Retain:

- a continuous top/bottom edge strip where it carries bending;
- a front solid zone for handles, appearance, and drawer attachment;
- rail/guide zones and end stops;
- diagonal straps when shear direction is known;
- radiused window corners and comfortable exposed edges.

Compare sliced time. A finer honeycomb can use less CAD volume yet take longer because it creates much more perimeter length and acceleration-limited motion.

### Ribbed skins and floors

Use a closed skin for containment, cleaning, or small-item retention. Put ribs on the non-contact side. For a drawer floor, keep the inside smooth and place ribs underneath unless bed orientation or abrasion argues otherwise.

Use ribs to shorten unsupported spans rather than thickening the whole floor. Check concentrated loads from narrow tools, feet, or dividers; a distributed-load design can fail under a point load.

### Hollow sections and diaphragms

A hollow rectangular/rounded box or hat section is efficient for long racks and stands. Add sparse diaphragms only where they prevent shell buckling, transfer a load, or support a roof. Keep drain/cleaning paths open.

Avoid a fully enclosed hollow section when support, debris removal, moisture, or inspection is a concern. Split, vent, or use an open hat profile.

## Path-compatible dimensions

Use `scripts/plan_shell_ribs.py` as a starting point. For a constant-width extrusion model:

```text
path_spacing ~= line_width - layer_height * (1 - pi/4)
section_thickness(N paths) ~= line_width + (N - 1) * path_spacing
```

This explains why an exact multi-path wall is usually slightly thinner than `N * line_width`. Arachne/variable-width generators may choose another solution, so inspect the sliced paths.

Starting roles, not universal requirements:

- cosmetic non-load skin: two reliable paths;
- ordinary functional shell: three or more paths;
- sealed/wetted barrier: usually at least three to four paths, then leak-test;
- rib/web: usually two or three paths so it is not a fragile single seam;
- fastener/bearing/clip root: local additional paths/pad plus a coupon;
- top/bottom skin: enough layers to bridge the local span without pillowing or leakage.

Do not make every wall the maximum role thickness. Separate exterior shell, internal divider, rib, sealing wall, and interface parameters.

### Opposing wall paths in thin plates

Before reducing infill in a thin CAD plate, estimate:

```text
wall_stack_per_side ~= section_thickness(wall_lines_per_side)
remaining_infill_core ~= plate_thickness - 2 * wall_stack_per_side
```

Run `scripts/plan_shell_ribs.py --plate-thickness-mm ... --wall-lines-per-side ...`. If the result is `NO_INFILL_CORE`, the two wall stacks already consume the nominal plate and an infill percentage change cannot remove a distinct interior. `SUB_LINE_WIDTH_CORE` normally becomes variable-width or gap-fill behavior rather than ordinary infill. Always confirm in the exact slicer because Arachne/variable-width allocation can differ from the constant-width estimate.

Use rounded transitions. As a first printable root radius, one nominal line width is better than a sharp corner; increase it when loads or space justify it. Determine rib spacing from span, buckling/deflection, load, and coupon—not a decorative cadence.

## Support and toolpath patterns

### Self-supporting transitions

Use chamfers, arches, teardrop holes, gradual ramps, and short bridges. Treat 45 degrees as a conservative starting shape, not a universal process limit. Validate the exact material/nozzle/cooling with a coupon.

### Split and reorient

Split when each piece gains:

- a better layer load direction;
- a broad bed face;
- no trapped support;
- simpler walls or a faster nozzle;
- accessible assembly and service.

Account for fasteners/joints and the risk that two prints replace one.

### Local slicer modifiers

Use modifiers for extra perimeters, denser infill, slower bridges, or different layer height only where the geometry requires it. Preserve the 3MF project and profile; modifier behavior is part of manufacturing evidence.

### Infill as roof support

Use sparse/adaptive infill when a large enclosed volume needs top-layer support and no explicit ribs define the structure. Use support-oriented infill when mechanical properties do not depend on it. Do not add infill to open shells with no roofs simply because a default profile has 15%.

## Exposed infill lattice

For a deliberately porous or decorative region, a slicer can omit walls/perimeters and top/bottom solid layers so that only infill paths remain. Represent that region as a named closed envelope and keep it distinguishable from the separate solid frame until slicing. Group both as parts of one multi-part object, assign settings per part, and connect their toolpaths through a verified capture/interface band so the result prints as one physical object. Keep fits, edges, attachments, seals, and primary load paths in modeled geometry.

This is not stored in STL geometry. Preserve the exact 3MF/project, slicer version, pattern, density, angle, infill line width, layer height/count, overlap, material, speed, flow, and cooling. Inspect every generated layer: a flat panel, vertical wall, and curved volume expose very different parts of the layer-space infill.

Read `references/exposed-infill-patterns.md` before selecting this method. It defines the CAD partition, slicer contract, pattern/orientation choices, anchoring, acceptance coupon, and failure limits.

## Patterns to avoid

- Hundreds of modeled honeycomb/gyroid cells used as decorative pseudo-infill.
- Thick walls that contain sparse infill instead of intentional shell paths.
- Global 100% infill to strengthen one boss, rail end, or clip.
- Single-path ribs carrying a meaningful load without process evidence.
- Sharp rib/boss roots and abrupt thick-to-thin steps.
- Windows that cut through rails, seal lands, handles, anti-tip mass, or divider joints.
- Material removal started before structural runners, perimeter frames, smooth sliding faces, stops, and connecting load paths were named and protected.
- Enclosed cavities that trap support, water, debris, or uncured coating.
- Decorative holes on surfaces that must be cleaned, sealed, or remain comfortable.
- Extremely short repeated segments that are acceleration- and cooling-limited.
- CAD lattices assumed stronger than slicer infill without equal-mass testing.

## Verification questions

Before accepting a pattern, answer:

1. Which load, containment, surface, or manufacturing role does every remaining wall/rib serve?
2. Are loads continuous through extrusion paths and across layer interfaces?
3. Did removed material create a longer/weaker unsupported span?
4. Are local pads connected into the shell instead of floating as thick islands?
5. Did openings increase perimeter time, retractions, seams, or warp?
6. Can all supports, water, debris, and service parts be removed?
7. Are fits, rails, seals, bed planes, and visible relief untouched?
8. Did the exact slicer generate the intended number of paths?
9. Do opposing wall stacks leave a real infill core, or is the nominal infill already absent?
10. Is the candidate still on the favorable side of time, material, and measured performance?
11. Has the uncertain feature been isolated in a coupon before the long print?
