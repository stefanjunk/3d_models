# DfAM dimensions for color features

The values here are conservative starting heuristics, not universal limits. Validate them with the actual nozzle, line width, layer height, filament opacity, slicer, and printer.

## Minimum isolated color width

A robust isolated region should normally be at least **two extrusion widths** across. With a 0.4 mm nozzle and 0.42–0.48 mm line width, start around 0.8–1.0 mm. One-line details can work but are sensitive to Arachne/thin-wall behavior, XY compensation, seam placement, and surface-paint segmentation.

For text:

- use bold, open counters, and generous spacing;
- avoid strokes narrower than the selected line-width strategy;
- inspect every glyph in the sliced toolpath, not only the CAD render.

## Inlay depth

Start with at least **two to three layers** of physical depth:

- 0.2 mm layers: 0.4–0.6 mm;
- 0.12 mm layers: 0.24–0.36 mm.

Use more depth when top-surface ironing, elephant-foot compensation, surface finishing, or translucent filaments could reduce visual separation.

## Interface clearance

For co-sliced multicolor bodies intended as one object, use shared boundaries with no intentional assembly clearance unless the destination slicer requires a workaround. For separately printed inserts, use the fit/tolerance rules from `functional-3d-design` and a coupon.

Do not create tiny positive overlaps between color solids. 3MF component overlap semantics can be consumer-dependent and the last material may win in overlaps. Prefer disjoint volumes.

## Shell depth for texture conversion

A colored surface shell must be deep enough to survive wall generation and surface approximation. Start with:

- at least 2 line widths for visible side color;
- at least 2–3 layers for top-facing color;
- more for translucent/light filaments over a dark base.

The voxel converter uses a physical `shell_depth`, not a number of texture pixels.

## Small island cleanup

Define both:

- minimum physical area, e.g. 0.5–1.0 mm²;
- minimum width, e.g. 0.8 mm for a 0.4 mm nozzle.

Reassign removed islands to the nearest surrounding printable region and record their count/area. Do not silently delete semantic features such as eyes, labels, or safety markings; redesign or enlarge them.

## Opacity and show-through

Light and translucent colors can reveal a dark base or purge-in-infill. Countermeasures:

- increase light-color shell depth;
- add more perimeters;
- avoid dark purge inside light exterior regions;
- use opaque filaments;
- place a white underlayer/underprint region where the process supports it;
- print a thickness/opacity swatch.

## Boundary orientation

Vertical boundaries cause color changes on many layers but can be sharp in XY. Horizontal boundaries are cheap but have one-layer Z quantization. Sloped color boundaries create stair-stepped tool changes and may produce small islands; simplify or align them with product seams.
