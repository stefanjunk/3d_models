# Printable surface-texture families

## Contents

1. Carbon and woven composites
2. Wood grain
3. Stone, concrete, and ceramic
4. Leather and skin-like textures
5. Brushed, hammered, and cast metal
6. Fabric, basket, and textile motifs
7. Knurling and functional grip
8. Lotus and floral effects
9. Material-first effects
10. Common pitfalls

## 1. Carbon and woven composites

Separate three cues:

1. diagonal tow/band geometry;
2. over-under/twill phase;
3. directional specular reflection.

For a flat horizontal patch, first test directed top-surface paths or a thin `TEXTURE_SKIN` with alternating `+45°/-45°` zones. Extrusion direction can provide a changing highlight without a dense mesh. For a side wall or curved surface, map vector bands in physical surface coordinates and use one- or two-layer-scale relief.

Stylize the cell. Real fibres are normally below ordinary FDM resolution. Start motif-pitch coupons around `3–8 × line_width`, keep each printable band at least one reliable path wide, and compare one- versus two-layer relief. These are test ranges, not universal dimensions.

Do not model every fibre or use a full-resolution carbon photograph as displacement. Do not claim a carbon-look print has laminate stiffness. Carbon-filled filament may be abrasive and visually matte; validate nozzle compatibility and distinguish material fill from weave appearance.

## 2. Wood grain

Decompose wood into:

- long low-curvature grain centerlines;
- growth-ring spacing and drift;
- localized knots/eyes;
- shallow pores/roughness;
- color and finish.

Use procedural splines for the long grain, with bounded wavelength/amplitude and a saved seed. Add knots as a few nested vector contours or localized adaptive relief patches. Use material, finish, or subtle wall perturbation for pore-scale roughness.

Keep grain direction coherent across adjacent faces. On a cylinder or rounded perimeter, define one arc-length coordinate and a seam in a low-attention region. Do not stretch a square image independently to fill every face.

Wood-filled filament can support color/tactile cues but does not replace geometric validation. Filled materials may require abrasion, flow, drying, and nozzle checks. Treat temperature-driven color variation as process-specific and coupon it; thermal lag makes small precise motifs unreliable.

## 3. Stone, concrete, and ceramic

Use a band-limited procedural field:

- sparse macro pits or chips;
- medium undulation;
- material/finish for micrograin.

Avoid white-noise displacement. It consumes triangles, creates tiny toolpath segments, and often prints as uncontrolled roughness. Place high-amplitude features away from thin walls, sealing faces, sliding surfaces, and hand-contact edges.

For ceramic or carved-stone motifs, use vector grooves, low-frequency relief, or a small organic insert. Test whether grooves trap dirt or require inaccessible support.

## 4. Leather and skin-like textures

Model only the visible cell/fold network at printable scale. Use a simplified Voronoi-like crack network, sparse wrinkles, or adaptive low-frequency relief. Move pores and fine grain into material or finish.

Keep the network irregular but band-limited. Randomness requires a stored seed and minimum edge spacing. Avoid sharp crack tips near flexures or thin shells; fillet groove roots and preserve wall reserve.

## 5. Brushed, hammered, and cast metal

### Brushed metal

Prefer aligned top paths, one-direction finishing strokes, metallic filament, or post-processing. Microscopic modeled scratches are usually below the process scale and create no controlled optical advantage.

### Hammered metal

Use sparse shallow dimples with bounded diameter, depth, spacing, and seed. Generate analytic or instanced cutters before tessellation. Avoid tangential Boolean contacts and excessive overlap between dimples.

### Cast or bead-blasted metal

Use subtle wall roughness/material for microtexture and a few low-frequency waviness terms for macro character. Preserve exact interface and bed faces.

## 6. Fabric, basket, and textile motifs

Use vector centerlines and a compact repeat definition. Decide whether the effect is closed relief, open lattice, or only directional gloss. For an open textile-like panel, consider framed exposed infill only when layer-space paths produce the desired view and a solid frame captures every edge.

Same-layer crossings can accumulate material. Stagger crossings across layers, use non-crossing path families, or enlarge the stylized weave. Inspect every layer rather than judging the top view only.

## 7. Knurling and functional grip

Treat functional grip as macro geometry:

- select groove/rib direction from hand force and print orientation;
- size ribs for reliable extrusion and cleaning;
- round roots and hand-contact peaks;
- protect flexures, seals, and insertion paths;
- test wet/dry grip, abrasion, and comfort.

Do not substitute a photographic bump map for a functional knurl. Fuzzy Skin can improve grip in some applications, but coupon thickness, snagging, wear, and cleaning.

## 8. Lotus and floral effects

Clarify the intended meaning:

- **decorative lotus:** vector petal outlines, shallow relief, or colored insert;
- **open lotus lattice:** petal-shaped `LATTICE_ENVELOPE` or modeled openings inside a solid frame;
- **sculptural lotus:** organic macro component on a parametric backer;
- **functional lotus effect:** hydrophobic wetting behavior requiring material/surface testing, not merely a flower pattern.

For a vector motif, preserve petal centerlines, symmetry count, minimum neck width, tip radius, and protected border. Use `scripts/generate_surface_pattern_svg.py --pattern lotus` as an editable starting source.

For exposed infill, the CAD petal envelope defines occupancy while slicer infill defines strands. Keep `FRAME` and `LATTICE_ENVELOPE` distinguishable, assign zero walls/top/bottom only to the envelope, and verify capture at the petal boundary. Use `optimize-fdm-design` for the full exposed-infill contract.

## 9. Material-first effects

Prefer material or finish when the cue is below printable geometry:

| Effect | First candidates |
|---|---|
| sparkle/metal flake | metallic or glitter filament, paint |
| iridescence/color shift | specialty filament, coating, film |
| carbon laminate realism | glossy dark material plus path direction or film |
| wood color/fibres | wood-filled filament, stain/paint, controlled finish |
| translucent frost | translucent material plus wall/path strategy or surface finish |
| soft-touch | TPU/TPE, coating, material-compatible texture |

Record abrasion, nozzle, drying, adhesion, temperature, UV, cleaning, skin-contact, and multi-material compatibility where relevant.

## 10. Common pitfalls

- Reproducing photographic illumination as pits and ridges.
- Choosing motif size from image pixels rather than millimetres and viewing distance.
- Scaling a repeat anisotropically until weave cells or wood rings distort.
- Applying Fuzzy Skin to a whole part when only one named surface should change.
- Assuming a horizontal top-pattern method works on a vertical or freeform exterior.
- Unioning a texture skin before slicer-specific parameters are assigned.
- Relying on tangent contact between texture and core.
- Making shallow grooves on a wall already at minimum thickness.
- Judging only a rendered normal map or only a single slicer layer.
- Failing to preserve the vector/procedural seed, tile size, project frame, or exact 3MF.
