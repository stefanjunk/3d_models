# Mechanical and fluid-system optimization

## Contents

- [Mechanical load paths](#mechanical-load-paths)
- [Interfaces and wear](#interfaces-and-wear)
- [Low-pressure ducts and water systems](#low-pressure-ducts-and-water-systems)
- [Garden rainwater-filter example](#garden-rainwater-filter-example)
- [Patterns by subsystem](#patterns-by-subsystem)
- [Verification and stopping rules](#verification-and-stopping-rules)

## Mechanical load paths

### Bending

Move material away from the neutral axis with flanges, edge beams, box/hat sections, and ribbed skins. Removing core material can preserve much of the bending stiffness only while the outer skins remain connected against shear and local buckling.

Check:

- primary bending axes and load reversal;
- flange continuity at holes/joints;
- web shear and local skin buckling;
- layer orientation at tensile surfaces;
- concentrated loads that invalidate a distributed-load assumption.

### Torsion

Prefer a closed or nearly closed section for long racks, stands, bars, and housings that twist. An open U-channel may be light in bending but poor in torsion. Add sparse diaphragms or close the section locally at joints.

Do not perforate all four faces in the same station. Stagger windows or preserve a continuous torsion path.

### Compression and buckling

Thin shells can fail by buckling before material strength is reached. Use beads, corrugations, ribs, curved shells, or shorter unsupported panels. Determine spacing from the actual span/load and validate; no universal decorative grid substitutes for buckling analysis.

### Impact and fatigue

Use gradual sections, large roots, replaceable bumpers/wear pieces, and ductile material/orientation. Avoid notches from window corners, abrupt rib ends, or seam alignment. Static stiffness retention does not prove fatigue or impact retention.

## Interfaces and wear

Keep these locally solid or explicitly reinforced:

- heat-set inserts, captive nuts, and screw heads;
- bearing/shaft seats and gear hubs;
- drawer rails, stops, latch noses, and hinge knuckles;
- flexure roots and hard stops;
- hose barbs, threaded ports, O-ring lands, and flange bolts;
- magnet pockets and thin capture lips.

Tie every boss/pad into the shell with a fillet and one or more load-oriented gussets. A thick isolated boss in a thin wall can peel the wall rather than use the boss material.

Prefer purchased metal shafts, screws, inserts, bearings, springs, O-rings, hose fittings, and clamps when they improve precision, wear, fatigue, sealing, or serviceability. Reducing printed material by using a standard component is often safer and faster than printing an elaborate substitute.

## Low-pressure ducts and water systems

Separate the design into:

1. **containment barrier** — continuous, even, inspectable wall;
2. **structural reinforcement** — external ribs/flanges/gussets;
3. **flow geometry** — smooth passages, separators, lamellae, drains;
4. **interfaces** — hose, gasket, fastener, cartridge, lid, valve;
5. **service path** — cleaning, sediment removal, filter replacement, inspection.

### Containment rules

- Do not use sparse infill as part of a wetted barrier. Thick walls with an infill cavity can leak internally and become impossible to clean.
- Start with an even wall sliced into at least three to four continuous perimeters for ordinary watertight trials; increase only from leak-test evidence and process capability.
- Keep seams away from the highest head, seal lands, and hose-bending loads where the slicer permits.
- Put ribs on the dry/outside face so the wet surface stays smooth and cleanable.
- Avoid nubs, abrupt wall changes, tiny text, and decorative perforation on sealing walls.
- Add drain/vent paths to every intentional cavity. Never create a blind wet pocket to save visible material.

Watertight is not pressure-rated, food-safe, potable-water-approved, or biologically clean. Treat gravity-fed garden systems separately from pressurized plumbing.

### Flow-path rules

- Maintain hydraulic area and avoid many small sharp turns that raise pressure loss and trap debris.
- Use smooth tapers and large radii at transitions; avoid rib intrusions into the wet path unless they have a hydraulic purpose.
- Make separator vanes, lamellae, and filter cages removable when fouling is expected.
- Keep sediment paths downhill toward an accessible sump/drain.
- Use standard mesh/mat/filter media for fine filtration; print the holder and flow distributor, not a fragile microscopic filter lattice.
- Reinforce hose ports for external bending and clamp loads without thickening the entire vessel.

## Garden rainwater-filter example

For a gravity/low-head three-stage garden filter such as vortex separator → lamella settler → removable media cartridge:

### Stage 1 — vortex/separation chamber

Preserve a continuous round/conical wet wall. Use circumferential or vertical external ribs only where shell buckling/handling requires them. Keep the tangential inlet and central overflow locally reinforced with pads/gussets.

Do not replace the cone with a lattice. Its smooth shape and sediment slope are functional. Save material by reducing uniform excess thickness, using outside ribs, and making the sludge sump/drain fitting local and replaceable. Provide an accessible drain/flush port; separation without sediment removal only stores dirt.

### Stage 2 — lamella settler

Use thin removable plates supported by a sparse frame rather than a solid printed block. Keep each flow channel open and cleanable. Support plates at edges or a few comb rails; too many cross-ties catch debris.

Maintain a distinct sludge space below the plate pack and an accessible drain/cleanout. Do not let ribs or infill cavities become unintended sediment traps.

### Stage 3 — filter cartridge

Use a skeletal cage with a few large openings and solid sealing/handle interfaces. Let purchased mesh/filter mat perform particle capture. Keep the cartridge removable from above and avoid fine printed grids that multiply toolpaths and clog immediately.

### Cascade and 25 mm hose interfaces

Use a standard purchased hose barb, bulkhead fitting, gasket, or clamp when available. Print the adapter/body around a known interface. Add local external gussets for hose leverage, and keep the internal bore/taper smooth. Coupon the fit and leak-test before the full vessel.

### Outdoor environment

Record UV, temperature, standing-water, cleaning-chemical, freeze, and biological-fouling exposure. A material marketed as UV-resistant still needs product-specific data and field inspection. Design replaceable seals/media and access before reducing wall mass.

## Patterns by subsystem

| Subsystem | Efficient pattern | Preserve | Avoid |
|---|---|---|---|
| Housing/enclosure | Thin shell, edge flange, local ribs | Datum, gasket land, screw zones | Global thick wall/high infill |
| Bracket | Box/hat section, triangular gusset | Load and mounting faces | Solid block or sharp root |
| Long rail/rack | Closed section, sparse diaphragms | Straight rail and joints | Fully solid bar or open floppy web |
| Gear/shaft support | Local bearing pads tied by ribs | Center distance, alignment | Lightweighting around seats |
| Flexure/clip | Long tapered beam, root radius, stop | Strain path/orientation | Short thick snap or single-path root |
| Duct | Smooth thin wall, external ribs | Cross-section and access | Internal decorative lattice |
| Gravity vessel | Even multi-perimeter wall, dry-side ribs | Leak barrier, drain, ports | Wetted infill cavity |
| Filter media holder | Open frame, replaceable media | Seal, handle, flow area | Fine printed filter mesh |

## Verification and stopping rules

For mechanical parts, record load cases and compare maximum stress/strain/deflection at equal boundary conditions. Use printed anisotropic properties only when measured for the exact process. Follow with interface and full-orientation coupons.

For water/duct parts, verify:

- manifold/wall thickness and no hidden cavities;
- slicer paths around seams, ports, ribs, and roof bridges;
- leak test at a head/pressure above normal service with a safe nonhazardous fluid;
- flow rate/head loss and separator/filter behavior;
- drain/cleaning access and retained sediment location;
- hose/port proof load and repeated service;
- UV/temperature/freeze inspection plan.

Stop before claiming readiness for pressure vessels, potable/food systems, fire protection, hazardous chemicals, or any failure with serious consequences. Use certified conventional components and qualified engineering.
