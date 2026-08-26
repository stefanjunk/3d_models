# Textured OBJ/GLB to multicolor 3MF

## 1. Preserve and inspect

Archive the original OBJ/MTL/texture set or GLB and record hashes. Inspect:

- units, bounds, orientation, applied transforms;
- watertightness, connected components, non-manifold/open edges;
- UV presence and range;
- number of materials and texture images;
- texture resolution, alpha, color space, and seams;
- whether the GLB uses Draco compression;
- whether the visual color comes from base-color texture, vertex color, procedural nodes, lighting, or baked shading.

Use:

```bash
python3 scripts/inspect_textured_asset.py model.glb --json-out inspect.json
```

If the model is not a valid printable solid, route repair through `organic-mesh-functionalization` before color conversion.

## 2. Normalize the visual source

For the most reliable conversion:

- apply object transforms;
- use one authoritative mesh/object where practical;
- bake procedural materials, vertex colors, and multiple maps into one base-color texture atlas;
- remove lighting, highlights, AO, and shadows if they should not become filament regions;
- resolve UV overlaps unless intentional;
- use broad semantic colors rather than photorealistic microvariation;
- retain the original texture and create a derived printable texture.

Blender imports glTF materials into node graphs and OBJ materials as material assignments. `Separate by Material` can help when source materials already correspond to desired filament bodies.

## 3. Map to the actual filament palette

Create a palette from printed swatches. Quantize the texture to those exact entries in CIE Lab using CIEDE2000 by default:

```bash
python3 scripts/quantize_texture.py texture.png \
  --palette filament-palette.yaml \
  --output texture-printable.png \
  --report quantization.json
```

Default policy:

- fixed palette, not unconstrained K-means;
- no dithering;
- connected-island cleanup in physical units;
- preserve a semantic mask for critical features;
- report mean, median, p95, and maximum Delta-E plus area fractions.

The display RGB values are only estimates. Printed swatches photographed under controlled light or measured with a color instrument are better.

## 4A. Fast Texture-to-Color Painting route

Bambu Studio 2.7 introduced Texture-to-Color Painting for OBJ, glTF, and GLB. The published limitations include:

- single-texture models recommended;
- import/convert one textured model at a time;
- Draco-compressed glTF/GLB unsupported at introduction;
- limited repair; fix serious mesh defects first.

Workflow:

1. import the normalized textured model into Bambu Studio;
2. invoke Texture-to-Color Painting;
3. remap to exactly the available filament colors;
4. remove or merge tiny paint islands;
5. save a 3MF project;
6. import the project into Anycubic Slicer Next;
7. remap colors to the four ACE slots;
8. reslice and compare against the quantized reference image.

**Interoperability gate:** slicer-painted project data may be vendor/application-specific. If Anycubic loses or changes the painting, do not patch it manually at scale; use the solid fallback.

## 4B. Headless voxel solid route

The included converter:

1. voxelizes a watertight mesh;
2. samples the texture at surface-adjacent voxels;
3. maps samples to the fixed palette;
4. propagates each surface color inward to a physical shell depth;
5. assigns the interior to a chosen base color;
6. removes tiny color components;
7. reconstructs each color mask with marching cubes;
8. exports aligned STL parts and a manifest;
9. packages them as one 3MF component assembly.

Example:

```bash
python3 scripts/texture_to_voxel_parts.py model.obj \
  --palette filament-palette.yaml \
  --pitch 0.6 --shell-depth 1.2 \
  --base-color body_orange \
  --minimum-component-voxels 8 \
  --output-dir build/parts
```

Trade-offs:

- smaller pitch improves boundary fidelity but increases memory and triangle count roughly cubically;
- voxelization can soften sharp edges and tiny details;
- UV sampling near seams requires review;
- a non-watertight mesh cannot define a reliable filled interior;
- color parts can be disconnected but each component must remain valid;
- the result is a manufacturing derivative, not a replacement for the original textured asset.

## 5. Final slicer verification

In Anycubic Slicer Next:

- confirm one assembled object with aligned parts;
- assign every semantic filament to an ACE slot;
- inspect color/tool view layer-by-layer;
- confirm thin regions were not merged or dropped;
- inspect wipe tower, purge destinations, and support colors;
- compare the sliced exterior with the quantized reference, not the photorealistic source;
- save the destination project alongside the standard 3MF.
