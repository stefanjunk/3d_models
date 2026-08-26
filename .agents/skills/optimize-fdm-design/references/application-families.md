# Application-family guidance

## Contents

- [Drawer, tray, and vanity organizers](#drawer-tray-and-vanity-organizers)
- [Cable clips and docking bars](#cable-clips-and-docking-bars)
- [Phone stands and bedside docks](#phone-stands-and-bedside-docks)
- [Cosmetic grids and palette organizers](#cosmetic-grids-and-palette-organizers)
- [Relief portrait panels](#relief-portrait-panels)
- [Mahjong racks and pushers](#mahjong-racks-and-pushers)
- [Decorative art, toys, and figures](#decorative-art-toys-and-figures)

## Drawer, tray, and vanity organizers

Applies to:

- Exact-fit drawer grid organizer
- Modular desktop tray system
- Exact-fit vanity drawer insert
- General desk organizers and small drawer systems

### Preserve

- outer exact-fit envelope and removal clearance;
- drawer guides, stops, front attachment, handle zone, and anti-tip behavior;
- structural runners, perimeter/edge frames, their connecting load paths, and every smooth sliding/contact face;
- divider junctions and small-item containment;
- flat/clean inner surfaces and visible relief/texture;
- stacking rims, magnets, pins, or module interfaces.

### First variants

1. Parameterize visible shell, hidden shell, divider, floor skin, rib, and interface thickness separately.
2. Check whether opposing wall paths already consume each thin plate before changing infill; record `NO_INFILL_CORE`, `SUB_LINE_WIDTH_CORE`, or `INFILL_CORE_PRESENT` from the helper and confirm it in the slicer.
3. Replace full drawer side/back walls with two to four large print-oriented radiused windows while retaining edge beams, front zone, guide zones, and diagonal straps.
4. Replace thick floors with a closed inside skin plus underside ribs aligned to divider/load locations.
5. Replace full intermediate shelves in a drawer housing with side rails, front/rear crossmembers, and sparse transverse ties if drawer sag/racking remains acceptable.
6. Keep exterior carbon/wood/relief skins closed; add hidden interior ribs instead of thickening the relief wall globally.
7. Use 0–10% infill only if enclosed roofs need it after the explicit rib structure is modeled and a genuine infill core exists.

### Common failures

- Openings intersecting a drawer rail or handle load path.
- Thin floor flex causing dividers to peel at their roots.
- Window grids taking longer than solid walls because every cell is a perimeter.
- Removing lower/rear mass until the organizer tips with a drawer open.
- Relief engraving leaving too little wall after shell reduction.

## Cable clips and docking bars

Applies to:

- Desk-edge cable clip kit
- Charging-cable docking bar

### Preserve

- calibrated cable diameter and retention force;
- desk-edge fit, pad/contact surfaces, insertion path, and abrasion radii;
- flexure root, hard stop, and layer orientation;
- connector-head clearance and one-handed use.

### First variants

- Use an open C/leaf flexure instead of a thick solid clamp block.
- Lengthen and taper the compliant arm before thinning it aggressively.
- Use a hollow/hat-section docking bar with local solid clip sockets.
- Consolidate repeated clip geometry parametrically; print replacement clips separately if they are wear items.
- Use zero infill when every section is defined by wall paths and no unsupported roof remains.

### Common failures

- A nominally light single-path flexure splits at the seam.
- Global thickening raises insertion force and material without improving fatigue life.
- Clips are strongest in CAD but oriented so opening tension separates layers.

## Phone stands and bedside docks

Applies to:

- Adjustable passive phone stand
- Bedside passive device dock

### Preserve

- center-of-mass support polygon and anti-tip margin;
- viewing-angle range, hinge/slot fits, cable bend radius, and connector clearance;
- contact pads, soft insert pockets, and button/camera access;
- one-handed docking loads.

### First variants

- Use two thin triangular side frames tied by sparse crossmembers instead of a solid wedge.
- Use folded/hat sections for the backrest and base.
- Put mass only where anti-tip behavior needs it; allow a purchased steel plate/weights rather than printing bulk.
- Use gussets at hinge/angle-stop loads and keep adjustable teeth/slots locally solid.
- Split the base/back if each receives a stronger print orientation.

### Common failures

- Lightweighting removes the anti-tip mass that was doing real work.
- Hollow bases have long unsupported roofs or rattle with trapped support.
- A fine adjustment rack disappears with the faster nozzle.

## Cosmetic grids and palette organizers

Applies to:

- Custom lipstick and tube grid
- Vertical makeup-palette organizer

### Preserve

- tube/palette clearance, easy cleaning, rounded hand-contact edges, and product visibility;
- stable base and divider root strength;
- resistance to splaying when outer cells are loaded.

### First variants

- Model dividers as exact one-, two-, or three-path walls according to function rather than thick solids.
- Use an open-bottom grid on a separate thin tray when spills/cleaning allow.
- Replace individual closed cells with slotted combs or interlocking orthogonal dividers.
- Use edge frames and sparse transverse ties in vertical palette racks.
- Keep only the base perimeter and anti-tip feet locally thick.

### Common failures

- Many separate cell perimeters dominate time despite low material.
- One-path dividers are omitted or inconsistently widened by the slicer.
- A lightweight tall rack lacks torsional bracing or adequate footprint.

## Relief portrait panels

Applies to:

- Photo-to-relief portrait panel
- Decorative panels with a functional frame/backer

Use `3d-print-heightmap-relief` for image fidelity.

### First variants

- Use a thin continuous backer with perimeter frame and sparse rear ribs.
- Crop/mask the relief to the visible subject or intended texture patch.
- Keep the 16-bit master but generate an adaptive mesh with a physical error tolerance.
- Separate wall reserve, relief depth, frame, and rear-rib parameters.
- Use a coupon for the chosen nozzle/layer/depth before a full panel.

### Common failures

- Uniform 0.2–0.3 mm triangulation over large flat backgrounds.
- Decimation smoothing eyes, text, weave crossings, or tile seams.
- Rear ribs telegraphing through a thin visible face.
- A thin backer warps because the frame/ribs create asymmetric thermal mass.

## Mahjong racks and pushers

Applies to:

- Mahjong rack-and-pusher set
- Personalized modular Mahjong rack set

### Preserve

- straight tile rail, tile angle, end stops, pusher fit, module connection, and comfortable edges;
- sufficient torsional stiffness over the full rack length;
- personalization depth and legibility.

### First variants

- Use a hollow box/hat beam beneath a locally solid tile rail.
- Add sparse diaphragms at module joints, feet, and pusher guide loads.
- Use an open-backed rail if it keeps the top path supported and cleanable.
- Make end caps/connectors replaceable rather than thickening the entire rack.
- Use a thin ribbed pusher blade with a locally thick hand grip.

### Common failures

- Long rail bow from an open section without edge flanges.
- Connector clearance changes when switching nozzle/profile.
- Personalization creates dense mesh/toolpaths along the entire rack.

## Decorative art, toys, and figures

Do not assume slicer infill solves all efficiency concerns. It handles enclosed volume but not support-heavy poses, thick modeled limbs, dense scans, balance, or fragile interfaces.

Use this skill only as a secondary check:

- hollow or shell large volumes with drain/inspection access where appropriate;
- choose orientation and splits that reduce support while preserving visible surfaces;
- simplify meshes within a visual/process tolerance;
- preserve thin silhouettes, joints, balance, impact zones, and child-safety constraints;
- use adaptive layers/nozzle changes only after checking faces, fingers, text, and small details.

Do not impose functional ribs/windows on sculpture merely to satisfy an optimization template. Route organic geometry and toy safety to the corresponding specialist workflow.
