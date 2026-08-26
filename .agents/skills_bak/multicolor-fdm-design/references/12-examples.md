# Worked examples

## 1. Parametric inlay nameplate

Purpose: demonstrate the preferred reusable architecture.

- OpenSCAD master with `part` selector.
- Four semantic solids: charcoal base, cyan border, white text, orange icon.
- Accents occupy only the top 0.6 mm, reducing active-color layers.
- Base is Boolean-cut so solids do not overlap.
- Build script exports STLs, preview, part manifest, and 3MF.

Acceptance:

- all parts share origin;
- no accent stroke below the configured minimum width;
- one component assembly imports without auto-arrangement;
- final slicer uses four colors only in the top band.

## 2. Four-color fox badge

Purpose: show semantic color regions on an organic-looking but parametric 2.5D object.

- orange silhouette/base;
- white muzzle/chest/tail inlays;
- black eyes/nose inlays;
- blue scarf inlay;
- all accents are broad, support-free, and limited to the upper layers.

Pitfall demonstrated: black eye/nose details can be too small. Parameters expose their physical diameter so a 0.4 or 0.8 mm nozzle profile can enlarge them.

## 3. Textured OBJ to four-color 3MF

Purpose: exercise the full automated fallback.

- script generates a watertight UV-mapped cylinder and one texture image;
- texture is quantized to a fixed four-filament palette;
- surface colors are propagated into a shell on a filled voxel grid;
- each color mask is remeshed and exported in the same coordinate frame;
- parts are packaged as one standard 3MF assembly;
- reports include source inspection, palette error, part metrics, and 3MF validation.

This example is intentionally coarse enough to build in a normal test environment. Production jobs should first run a proxy, then choose pitch from required geometric deviation, nozzle resolution, and memory.
