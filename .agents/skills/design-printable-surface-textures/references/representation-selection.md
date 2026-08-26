# Surface-texture representation selection

## Contents

1. Separate the intended effects
2. Use the physical resolution ladder
3. Select the representation
4. Handle concept images and written concepts
5. Decide whether texture is a component
6. Avoid false economy

## 1. Separate the intended effects

A surface reference can encode several independent effects:

| Effect | Evidence | Suitable representation |
|---|---|---|
| Silhouette or macro form | outline, section, cast shadow confirmed by views | exact or parametric geometry |
| Tactile relief | measured/high-confidence ridges, pits, grooves | vector/procedural geometry or adaptive relief |
| Directed gloss | highlight changes with viewing angle or stroke direction | top/perimeter toolpath direction, material, finish |
| Color/material | hue, fleck, translucency, sparkle | filament/material assignment, paint, film, coating |
| Porosity/openwork | visible holes, light/air passage | modeled opening or framed exposed infill |
| Image content | portrait, logo, irregular depth field | vector outline or localized heightmap |

Do not use one displacement map to approximate all rows. For example, a carbon reference may need a shallow stylized weave plus directed glossy paths and a dark material. A wood reference may need sparse grain curves, local knot relief, a filled filament, and a matte finish.

## 2. Use the physical resolution ladder

Classify the smallest intended physical feature against measured line width and layer height. The following ratios are starting categories for coupon design, not universal printer limits:

| Band | XY starting classification | Prefer | Main risk |
|---|---:|---|---|
| Sub-path optical | below about `0.75 × line_width` | material, color, gloss, film, coating, bed imprint | geometry aliases, vanishes, or becomes random roughness |
| Path-scale | about `0.75–3 × line_width` | slicer path direction, Fuzzy Skin, authored paths | broken short segments, flow/cooling variation |
| Macro geometry | above about `3 × line_width` | vector/procedural ribs, grooves, cells, petals | too many repeated Booleans or perimeters |
| Continuous local relief | multiple printable samples across important gradient | localized adaptive heightmap | excessive triangles and loss during simplification |

Run an analogous Z check:

- below roughly half a layer: likely to quantize away or become process variation;
- roughly half to two layers: useful starting range for subtle texture;
- several layers: visible/tactile macro relief requiring snagging, cleanability, wall, and support review.

Use actual first-layer and regular-layer behavior. A side-wall texture is sampled differently along Z than a top surface in XY.

## 3. Select the representation

Use this order and stop at the first method that satisfies the intent:

1. **Material/finish:** use when the target is mainly color, sparkle, sheen, translucency, microfibres, or sub-nozzle visual noise.
2. **Slicer/toolpath:** use when extrusion direction, regular nozzle-scale strands, or controlled perimeter perturbation creates the effect.
3. **Vector/procedural CAD:** use when the motif has centerlines, repetition, symmetry, a direction field, a seed, or a compact mathematical description.
4. **Localized adaptive relief:** use when continuous irregular height is the evidence-bearing feature and vectorization would destroy it.
5. **Dense mesh/freeform:** reserve for irreducibly sculptural texture at a physical scale the process can preserve.

Prefer a hybrid when different bands contribute. Do not force one method to carry every cue.

### Method matrix

| Source/effect | Primary | Secondary | Avoid |
|---|---|---|---|
| Carbon photo | vector twill or directed paths | black/gloss material or film | whole-patch photo displacement |
| Wood photo | grain curves plus localized knots | wood-filled material, wall roughness, finish | unfiltered full-surface heightmap |
| Stone/concrete | low-frequency procedural field | subtle Fuzzy Skin/material | white-noise displacement at pixel pitch |
| Leather | simplified cell/fold network | material and low-amplitude wall roughness | modeled microscopic pores |
| Brushed metal | aligned surface paths | metallic material/finish | geometric scratches below line width |
| Knurl/grip | parametric macro ribs | process-compatible path sizing | image engraving |
| Lotus/floral ornament | vector petals or organic macro relief | multi-color or open framed lattice | dense grayscale when boundaries are explicit |
| Portrait/logo | vector outline or local heightmap | color/material | repeating-texture workflow |

## 4. Handle concept images and written concepts

### Concept image

Create an evidence table before geometry:

- **Observed across views:** strong shape evidence.
- **Plausible relief:** supported by occlusion, silhouette, or repeated lighting behavior.
- **Likely shading/reflection:** highlight or shadow without geometric confirmation.
- **Material/color cue:** reproduce through material or finish unless physical relief is required.
- **Ambiguous:** keep as a candidate and isolate on a coupon.

Crop a texture swatch only after deciding whether it is seamless, directional, stochastic, or a single motif. Correct perspective and illumination before extracting curves or height.

### Written concept

Translate words into parameters:

| Phrase | Parameter questions |
|---|---|
| “carbon look” | twill/plain weave, cell scale, gloss, color, top or side surface? |
| “natural wood” | grain direction, ring spacing, knots, roughness, color variation, finish? |
| “organic stone” | pit size distribution, isotropy, sharp or eroded edges, cleanability? |
| “lotus effect” | visual petal motif, raised relief, porous lattice, hydrophobic function, or all? |

Do not infer a functional lotus-effect water-repellent claim from a decorative lotus motif. Functional wetting behavior requires material/process measurement.

## 5. Decide whether texture is a component

Create `TEXTURE_SKIN` as a separate component when it enables:

- per-part slicer parameters or material/color;
- independent orientation or flat printing;
- replacement/personalization;
- source-image swapping without regenerating the core;
- local mesh repair without touching fits and load paths;
- controlled backer, wall reserve, and seam.

Keep a same-material texture fused into `CORE` only when the Boolean remains compact, interfaces are protected, and no manufacturing distinction is needed.

For a one-piece in-place print with different slicer settings, retain logical separation through slicing. Use common origins, named parts, a defined overlap/capture band, and a process-matched joint coupon. The physical object may be one body even though the manufacturing model contains several selectable parts.

## 6. Avoid false economy

- A low triangle count can still produce thousands of tiny acceleration-limited segments.
- A vector honeycomb can print slower than a solid wall because every cell adds perimeters and corners.
- A photo-real render can rely on normals and material maps that have no printable geometry.
- Carbon-filled filament usually changes material appearance and handling; it does not encode woven-laminate geometry.
- A slicer setting saved only in memory or screenshots is not a reproducible manufacturing definition.
- A decorative texture can reduce remaining wall, concentrate dirt, abrade skin, or weaken a flexure even when it looks shallow.
