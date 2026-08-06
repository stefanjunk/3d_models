# FDM Printability Assessment

## Verdict

**PASS for digital FDM geometry, with slicer and physical-test review required.**
The reloaded final STL is one watertight body, fits a 256 x 256 x 256 mm build
volume upright, and all declared structural features exceed two nozzle widths.
No slicer executable (`prusa-slicer`, `orca-slicer`, `CuraEngine`, Cura, or
SuperSlicer) is installed in this environment, so no layer-by-layer G-code
preview is claimed.

## Printer assumptions

- Exact orientation: unchanged STL coordinates, broad bottom disc on the bed,
  **+Z upward**, front toward **-Y**, back toward **+Y**.
- Build volume: 256 x 256 x 256 mm minimum.
- Material: PLA preferred; PETG is acceptable after bridge tuning.
- Nozzle: 0.4 mm.
- Layer height: 0.20 mm (0.16 mm if exterior detail is prioritized).
- Walls: 4-5 perimeters; 5 top/bottom layers minimum.
- Infill: 10-15% gyroid or grid; baffles and thin shell regions should be
  generated primarily from perimeters.

## Measured practical dimensions

- Minimum sampled shell wall away from openings: **3.061 mm** at the upper
  core-to-dome transition. Mid-height samples are 3.23-4.82 mm.
- Each rounded baffle: **4.493 mm measured** normal thickness; 4.5 mm nominal.
- Closed base/floor under the core: **21.964 mm measured**; 22 mm nominal.
- Smallest declared rounded detail: **1.5 mm**.
- Robust two-line target for a 0.4 mm nozzle: 0.8 mm. All values above pass.

## Automated normal analysis

The shared printability script found 765 downward candidate faces totaling
9,148.98 mm2, or 7.98% of surface area, beyond a 45-degree self-support limit.
The hard printability checks pass, but visual/slicer review remains required.
Candidate regions include imported exterior ornament/dome facets, rounded
opening crowns, and the lower surfaces of the three nominal 45-degree baffles.

## Overhang, bridge, and support guidance

- The baffles are nominally 45 degrees and intended to print without dense
  internal support. Their rounded noses can trigger small support suggestions.
- The flat portions at the tops of the 46 mm openings create approximately
  30-32 mm local bridges. For PLA use full bridge cooling, 20-30 mm/s bridge
  speed, and tuned bridge flow. PETG may sag more and should be test-sliced.
- Prefer **support blockers inside the core**. Automatic support between
  baffles can become difficult to remove even though the inlet and outlet are
  open. If support is needed, use organic/tree, build-plate-only support under
  accessible exterior lips and the outlet crown.
- Do not fill the core with conventional grid support. There is no sealed
  trapped cavity in the model, but generated support between alternating
  baffles would have a high removal risk.
- A 5-8 mm brim is optional for conservative adhesion. The underside provides
  12,405 mm2 of downward area within 0.2 mm of Z=0.

## Remaining manufacturing checks

Before final manufacturing approval, inspect an actual slicer layer preview for
bridge sag, omitted thin exterior ornament, internal support placement, and
first-layer contact. Print one PLA prototype and pass several real 22 mm dice
through it. The digital cube-sweep is not a gravity or bounce simulation.
