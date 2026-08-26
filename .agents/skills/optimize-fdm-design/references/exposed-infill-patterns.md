# Exposed slicer infill as a printable design pattern

## Contents

- [Definition and suitable uses](#definition-and-suitable-uses)
- [Make the lattice region explicit](#make-the-lattice-region-explicit)
- [Keep slicer parts distinct but print one object](#keep-slicer-parts-distinct-but-print-one-object)
- [Record the slicer contract](#record-the-slicer-contract)
- [Choose pattern and orientation](#choose-pattern-and-orientation)
- [Anchor the lattice](#anchor-the-lattice)
- [Validate the manufactured result](#validate-the-manufactured-result)
- [Limits and failure modes](#limits-and-failure-modes)

## Definition and suitable uses

An **exposed-infill region** is a closed CAD envelope deliberately sliced with no perimeter/wall paths and no top or bottom solid layers, leaving only the slicer's infill toolpaths. The envelope controls occupancy; the slicer profile creates the visible lattice. This can produce a very regular, nozzle-scale screen with much less CAD complexity than modeling every strand.

Consider it for:

- decorative windows, lamp shades, translucent or backlit panels;
- ventilation screens and lightweight guards;
- visual separation that should remain porous;
- flexible TPU meshes or compliant inserts after process testing;
- prototypes that intentionally expose their manufacturing language.

Treat it as a manufacturing pattern, not an ordinary STL feature. The lattice is absent from the CAD mesh and appears only after slicing. Preserve the exact 3MF/project and profile; an STL export alone is incomplete.

## Make the lattice region explicit

Partition the design into at least:

1. a parametric frame or structural body owning dimensions, interfaces, loads, safe edges, and attachment;
2. a simple closed `LATTICE_ENVELOPE` body defining where exposed infill may exist;
3. optional modifier bodies defining local pattern, density, angle, material, or layer ranges.

Do not let slicer infill own holes, snap fits, fastener seats, sealing lands, hinges, load introduction, or user-critical edges. Keep those as ordinary modeled solids.

For a local lattice inside a larger product, prefer a separately named printable body/part. Use a modifier workflow only when the chosen slicer cannot assign the required settings directly to parts or when testing proves the modifier boundary more reliable. Check whether either method creates new boundaries or moves perimeters at intersections.

The envelope thickness must contain enough layers to form the intended cross-layer network. A one-layer region can produce only the paths scheduled for that layer. A multi-layer region can alternate or evolve the pattern, but crossings and bonds must be inspected.

## Keep slicer parts distinct but print one object

Keep `FRAME` and `LATTICE_ENVELOPE` distinguishable in the manufacturing model even when they will become one physical object:

- model them as separate named bodies using the same project origin and axes;
- import or group them as parts/volumes of one multi-part object, not as unrelated objects that the slicer may auto-arrange;
- assign ordinary wall/top/bottom settings to `FRAME` and infill-only settings to `LATTICE_ENVELOPE`;
- do not Boolean-union the meshes before slicing, because the slicer would lose the boundary needed for per-part settings;
- do not physically separate them on the bed when the design calls for one fused print.

Create a controlled physical connection between their generated toolpaths. Use a shared interface, recessed capture band, or small intentional overlap compatible with the selected slicer's volume semantics. Require lattice strands to terminate inside or fuse to a sufficient length of frame extrusion. Verify this in feature-colored preview and with a frame-joint coupon; visual contact in CAD is not proof of fused extrusion.

Prefer 3MF because it can preserve names, transforms, grouping, per-part assignments, and process state. If the CAD workflow exports STL, export one file per part with the same origin—such as `FRAME.stl` and `LATTICE_ENVELOPE.stl`—then import them as one multi-part object and save the resulting production 3MF. A single fused STL destroys the manufacturing distinction; two independently auto-arranged STLs destroy registration.

The target state is therefore:

```text
logical manufacturing model: two or more selectable parts with different settings
printer job: one coordinated set of touching/interlocking toolpaths
physical result: one bonded object, unless replaceability was intentionally selected
```

For multi-material printing, retain the same part separation and assign extruders/materials explicitly. Validate inter-material adhesion, shrinkage, temperatures, purge behavior, and the selected slicer's overlap or interface rules.

## Record the slicer contract

Record these values for every exposed-infill region:

```text
slicer and version
printer/material/nozzle
object orientation
lattice-envelope revision and body name
multi-part object/group identity and sibling frame body
wall/perimeter count = 0 in lattice region
top solid layers = 0
bottom solid layers = 0
periodic/automatic solid infill = off in lattice region
infill pattern and nominal density
infill angle or rotation sequence
infill extrusion/line width
layer height and number of lattice layers
infill-to-frame overlap or anchoring method
speed, acceleration, flow and cooling limits
material/extruder assignment
```

Setting names differ between slicers. Verify the generated paths instead of assuming that `0 walls` also disables top/bottom skins.

When a flat lattice starts on the build plate and must contain exactly `N` layers, use the process geometry as the CAD starting point:

```text
lattice_thickness = first_layer_height + (N - 1) * regular_layer_height
```

Then verify the actual layer count after slicing. Also check gap fill, bridge skin, ironing, support, and any automatic solid-infill interval; one of these can reintroduce unexpected solid paths.

The visible strand width is the configured extrusion/line width under the actual flow process; it is not automatically equal to nozzle diameter. Cell pitch is pattern- and slicer-dependent, so measure the preview or coupon rather than deriving it from density alone.

## Choose pattern and orientation

| Pattern family | Visual/mechanical character | Main caution |
|---|---|---|
| Rectilinear | Fast; alternating directions across layers | One layer is directional; appearance changes with layer count |
| Aligned rectilinear/lines | Calm parallel screen; useful for controlled flex | Very weak across strands unless another feature braces it |
| Grid | Both principal directions in a layer; strong visual grid | Same-layer crossings accumulate material and may be struck by the nozzle |
| Triangles/stars | Dense, rigid-looking multi-directional motif | Many same-layer crossings and higher local buildup |
| Gyroid | Flowing 3D pattern with no same-layer self-crossing in documented Prusa behavior | Not a constant planar grid; silhouette changes by layer and section |
| Honeycomb | Familiar cellular appearance | More corners/short segments; toolpath and edge behavior vary by slicer |

Prusa's official pattern guide distinguishes rectilinear's alternating directions from grid's same-layer crossings and warns that grid buildup can cause nozzle contact. Treat this as slicer-specific evidence and verify the exact implementation: <https://help.prusa3d.com/article/infill-patterns_177130>

For a flat screen, place the desired lattice plane parallel to the bed whenever strength, appearance, and assembly permit. Infill is generated in layer space and clipped by each cross-section; it does not automatically follow a curved product surface. For a predictable curved surface pattern, use a separate flat/formed insert, a mapped modeled lattice, or another controlled method.

## Anchor the lattice

Prefer a solid perimeter frame around exposed infill even though the lattice region itself has no walls. The frame should:

- capture strand ends on all required sides;
- provide comfortable and non-snagging exterior edges;
- transfer loads through continuous modeled geometry;
- own assembly keys, tabs, screws, adhesive lands, and datum surfaces;
- tolerate the selected infill-to-frame overlap without creating a visible bulge.

Use a process-matched coupon to determine whether the slicer's nominal infill/perimeter overlap provides reliable fusion. If not, redesign the frame/envelope intersection or add modeled anchoring fingers. Do not release an unframed lattice with many exposed line endpoints unless fragility and snagging are intentional and tested.

## Validate the manufactured result

Create at least three comparable variants: coarse, medium, and fine pitch at the same envelope, frame, material, orientation, and layer count. Slice and record:

- actual line pattern on every lattice layer;
- measured line width and aperture distribution;
- continuous connection to the frame;
- crossing buildup, nozzle-contact risk, bridges, stringing, and loose endpoints;
- print time, material, retractions, short segments, cooling and peak flow;
- light transmission, airflow, flexibility, stiffness, or guard opening as required;
- bending/tear or frame pull-out result when the lattice carries any service load;
- appearance from the intended viewing distance and lighting direction.

Do not compare different pattern families at the same nominal density and call that equal openness. Tune or measure actual open-area ratio, aperture distribution, or pressure drop so visual and airflow comparisons use a meaningful common basis.

Inspect the first layer separately. If bottom solid layers are disabled and the lattice starts on the bed, its adhesion and visual finish are governed by sparse individual paths. Add a removable process frame, brim, or ordinary solid border where needed.

Acceptance requires the exact slicer preview and a representative coupon. A clean CAD render cannot prove the lattice because the CAD envelope does not contain its manufactured strands.

## Limits and failure modes

Do not use exposed infill as the only barrier or primary structure for:

- sealed, fluid-containing, washable-hygienic, food-contact, or contamination-controlled regions;
- critical impact, lifting, protective, fastener, bearing, or repeated-wear load paths;
- openings with a safety-critical finger, entrapment, particle, flame, or guard-size requirement;
- surfaces that must be smooth, abrasion-resistant, easy to clean, or dimensionally fitted;
- curved appearance fields that require a surface-conformal motif.

| Failure | Cause | Prevention |
|---|---|---|
| No lattice is generated | Envelope too thin, density/path spacing incompatible, or modifier did not apply | Inspect every layer; enlarge/reorient envelope or change pattern |
| Lattice detaches from frame | Insufficient overlap, short strand anchors, cooling or material mismatch | Coupon the joint; increase captured length or add modeled anchors |
| Ragged outer boundary | Wallless lines terminate directly at the product edge | Add a separate solid frame or hide the termination in a recess |
| Nozzle knocks at crossings | Same-layer path buildup, overextrusion, warp, or insufficient Z clearance | Prefer non-crossing pattern, tune flow, slow down, or increase layer clearance |
| Pattern is not visually uniform | Alternating layers, adaptive density, small clipped cells, or modifier boundaries | Use constant density/angle where supported and validate the full preview |
| Unexpected solid skins remain | Top/bottom layers, bridge skin, gap fill, or slicer boundary behavior | Disable each relevant feature locally and verify feature-color preview |
| Strength is overestimated | Attractive grid mistaken for a continuous engineered laminate | Keep load paths modeled; test equal-envelope coupons in service direction |
| Method is lost on export | Only STL/STEP was delivered | Deliver named bodies plus the exact 3MF/project/profile and screenshots/report |
| Different settings cannot be assigned | Frame and envelope were fused into one mesh or imported as one undifferentiated volume | Preserve named parts through slicing and group them as one multi-part object |
| Parts print separately | STLs were imported as unrelated objects or auto-arranged | Preserve common origin/transforms and import as parts of one object |
| CAD parts touch but do not bond | Tangential contact or slicer clipping leaves no shared extrusion region | Add a compatible capture/overlap contract and verify the joint in toolpaths and coupon |

Prusa documents that modifier meshes can apply local infill, layers/perimeters, extrusion-width, and related settings, including examples that remove top and bottom solid layers. Other slicers may expose different controls or boundary behavior: <https://help.prusa3d.com/article/modifiers_1767>
