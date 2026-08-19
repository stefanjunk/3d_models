# Worked optimization examples

## Contents

- [Desk organizer with relief](#desk-organizer-with-relief)
- [Charging-cable docking bar](#charging-cable-docking-bar)
- [Garden rainwater filter](#garden-rainwater-filter)
- [Photo relief panel](#photo-relief-panel)
- [Framed exposed-infill lamp panel](#framed-exposed-infill-lamp-panel)

The numbers below are illustrative experiment structures, not transferable strength or print-time promises.

## Desk organizer with relief

### Baseline symptoms

- two full drawer shelves and thick housing walls;
- solid drawer side/back walls;
- broad drawer/sorter floors;
- full-resolution photo-derived 0.30 mm displacement triangulation on large carbon-look surfaces;
- 0.4 mm nozzle and long PETG print.

### Protected regions

- 320 × 230 mm closed envelope and drawer offset/clearance;
- rail/stop/handle/front attachment;
- visible carbon-look walls, with the texture representation still open and safe remaining wall required for any geometric candidate;
- sorter dividers and drawer anti-tip behavior;
- flat clean item-contact surfaces.

Write these as a named protected-geometry map before editing: drawer guide runners, top/bottom edge frames, front/handle zones, rear stops, smooth sliding faces, divider junctions, exterior relief skin, and anti-tip mass.

### Candidate sequence

| Candidate | Changes | Primary question |
|---|---|---|
| A process | 0.6 mm nozzle, ~0.30 mm layer, calibrated flow; plain/material or directed-path texture coupon | How much time and appearance change without dense texture CAD? |
| B geometry | Side rails/crossmembers, large drawer windows, ribbed floors | Does explicit structure remove more material without excessive new perimeters? |
| C texture | Compare vector twill, directed surface paths/material, and localized adaptive relief only if continuous height remains necessary | Which compact representation preserves the intended carbon effect and wall reserve? |
| D combined | Best A+B+C | Is the combined candidate feasible and Pareto-efficient? |

Do not replace drawer walls with a fine honeycomb first. Slice two or three large radiused windows plus diagonal straps; retain the front zone, guide strip, top/bottom edge beams, and rear stop.

Before changing infill, run the opposing-wall check for each drawer side, back, divider, and floor thickness. If two wall stacks leave no full-line-width core, changing 10% infill to 0% is not the source of meaningful savings; geometry, wall-path count, or plate thickness must change instead.

For floors, put ribs underneath the smooth interior skin and align selected ribs with dividers. Test a point load between ribs and racking with the drawer extended.

For the housing, keep the exterior texture substrate closed. Use `design-printable-surface-textures` to select vector, toolpath/material, or localized relief representation before optimizing its mesh. Replace any unnecessary full intermediate slab with drawer support rails and crossmembers only after drawer sag/racking analysis.

The sample `examples/desk-organizer-variants.json` demonstrates constraints and Pareto comparison. Replace every illustrative metric with exact slicer/calculation/test data.

## Charging-cable docking bar

### Baseline

A solid 240 mm bar contains six cable sockets and uses 20% infill. The sockets need accurate local retention; the middle of the bar mostly spaces them.

### Candidate

- Convert the bar to an open-backed hat section with two continuous flanges.
- Keep each cable socket as a local solid/pad tied into both flanges.
- Add sparse diaphragms at mounting points and end caps only.
- Print replaceable clip inserts in an orientation favorable to flexing.
- Use 0% infill if the hat section has no unsupported top roof; otherwise compare support-cubic/adaptive infill.

### Verify

- cable insertion/retention force and cycle set;
- bar twist between mounting points;
- connector clearance after nozzle/profile change;
- actual time: the open section should reduce long infill paths without adding a dense cell perimeter network.

## Garden rainwater filter

### Baseline

A large printed three-stage body uses uniformly thick walls and solid cartridge/lamella frames. It is gravity-fed/low-head, outdoor, and connected to a hose.

### Candidate

- Keep the vortex cone and every wet wall even, continuous, and multi-perimeter.
- Add external vertical/circumferential ribs only at handling/buckling locations.
- Reinforce the tangential inlet, overflow, drain, and hose ports locally.
- Make the lamella pack from thin removable plates held by two or three open comb rails.
- Replace the solid filter cartridge with a skeletal cage and purchased filter media.
- Keep a clear sludge sump and flush/drain path; avoid internal ribs that trap solids.
- Use purchased hose fittings/gaskets/clamps when practical.

### Verify

- leak test at conservative head, hose-port proof load, and external-rib buckling/handling;
- 0–target flow path and head loss;
- actual separation/capture location and full drain/cleanout;
- UV/temperature/freeze/material inspection plan;
- slicer seams and path continuity around every wet interface.

Do not call this a pressure-rated or potable-water design.

## Photo relief panel

### Baseline

A 300 × 200 mm portrait relief is sampled uniformly despite a large smooth background and has a thick solid backer.

### Candidate

- Preserve the 16-bit master and physical aspect.
- Mask the irrelevant flat background or let adaptive triangulation span it coarsely.
- Use a thin continuous backer with a perimeter frame and four to six rear ribs.
- Keep face/eye/text regions and relief boundary in a protected mesh set.
- Run a physical simplification-tolerance sweep; compare robust relief amplitude, surface error, triangles, slicer time, and a small portrait coupon.

### Verify

- no rib telegraphing or panel warp;
- preserved eyes/mouth/silhouette and mapping aspect;
- retained wall reserve under deepest engraving;
- manifold final mesh and meaningful slicer-load reduction.

## Framed exposed-infill lamp panel

### Intent

Create a regular, translucent nozzle-scale pattern without modeling hundreds of strands. The panel is decorative and ventilated; it does not carry the lamp mount, protect mains voltage, or provide a sealed barrier.

### CAD and process split

- Model a rounded solid `FRAME` with the mounting tabs, safe outer edge, and continuous load path.
- Add a separately named closed `LATTICE_ENVELOPE` spanning the frame opening and extending into a hidden capture band.
- Keep `FRAME` and `LATTICE_ENVELOPE` selectable as parts of one multi-part object; do not Boolean-union them before slicing.
- In the saved slicer project set walls/perimeters and top/bottom solid layers to zero only for that envelope.
- Compare rectilinear, grid, and gyroid candidates with the same material, envelope, frame, layer count, and approximate material budget.
- Print the panel flat when possible; do not assume layer-space infill will follow a curved shade surface.

### Verify

- inspect every lattice layer and feature-colored toolpath;
- measure aperture range, strand width, frame capture, and loose endpoints;
- confirm that the lattice paths fuse continuously into the normally sliced frame and the slicer has not separated or clipped the parts;
- reject grid variants with unacceptable crossing buildup or nozzle strikes;
- compare light transmission, shadow pattern, airflow, material, time, and frame pull-out;
- preserve the exact 3MF/profile because the STL envelope does not contain the lattice.
