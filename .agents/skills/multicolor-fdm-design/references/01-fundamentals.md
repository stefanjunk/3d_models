# Multicolor FDM fundamentals

## Five representations

### 1. Layer changes

A color change occurs at one or more Z heights. This is the cheapest and most portable route because a layer normally uses one filament. It is ideal for plaques, top labels, signs, and accent bands. It cannot create side-by-side colors within the same layer.

### 2. Separate solids

Each filament region is a watertight body in a common coordinate system. A 3MF assembly preserves relative placement and each part is assigned to a material/tool in the slicer. This is the preferred design-time representation.

### 3. Slicer painting

The slicer tags surface facets or generated regions with a tool. It is fast and expressive but typically changes only the slicing result. The underlying CAD/mesh remains one body, and painted regions may not export as reusable solids.

### 4. Texture-to-color painting

A UV texture is sampled and converted to slicer painting. Bambu Studio 2.7 introduced this for textured OBJ, glTF and GLB. Its release notes recommend single-texture models, one model at a time, no Draco-compressed glTF/GLB, and repair before import. Treat the output as a slicer-project fast path, not as guaranteed portable geometry.

### 5. Volumetric partitions

The model is discretized into voxels or another volume representation; surface colors are propagated inward for a controlled shell depth; each color volume is remeshed as a separate solid. This is slower and resolution-limited but yields explicit parts and a more portable 3MF.

## Color is not the same as material assignment

A color displayed in CAD or 3MF is design intent. The physical result depends on filament pigment, opacity, layer thickness, neighboring colors, purge quality, and the destination slicer’s slot mapping. Maintain two mappings:

```text
semantic region → filament ID
filament ID → temporary machine slot
```

Never encode the product as `extruder_1`, `extruder_2`, etc. Machine slot order changes; semantic intent should not.

## Surface color versus volume color

Single-nozzle multicolor slicers often care about the surface and then generate internal toolpaths. Parametric CAD must still provide a well-defined volume partition. A zero-thickness colored face is not a printable body. A robust color region is one of:

- a through-body partition;
- a top/side inlay with defined depth;
- a separate insert;
- a shell of defined thickness;
- a slicer paint region whose project file is authoritative.

## Resolution limits

- Z resolution is governed by layer height.
- XY color resolution is governed by extrusion width, toolpath generation, wall ordering, and purge stability.
- A high-resolution texture cannot force the printer to reproduce sub-line-width islands.
- Dithering increases apparent image colors in 2D but usually creates pathological color switching in FDM.

Start with broad semantic regions. Preserve small source details in a report even when they are intentionally removed from the printable build.
