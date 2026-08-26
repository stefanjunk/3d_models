# Evidence, official documentation, and limits

## Evidence classes

Use sources according to what they can prove:

- **Official slicer/firmware documentation:** feature existence, settings, and documented implementation behavior.
- **File-format specification:** representational capability, not universal slicer preservation.
- **Peer-reviewed toolpath research:** feasibility and demonstrated workflows, not plug-and-play safety for every printer.
- **Skill heuristics:** starting dimensions and workflow gates requiring exact-slicer and coupon validation.

Accessed 2026-08-18 unless otherwise noted.

## Official slicer and format sources

### Fuzzy Skin

Prusa documents that Fuzzy Skin resamples perimeter points and moves them randomly within a configured thickness, producing rough side surfaces:

<https://help.prusa3d.com/article/fuzzy-skin_246186>

Use this to support the algorithm/scope description. Do not generalize exact face selection or parameter names to another slicer/version.

### Modifier and per-model settings

Prusa documents modifier meshes and local settings including infill, layers/perimeters, Fuzzy Skin, extrusion width, and examples involving top/bottom solid layers:

<https://help.prusa3d.com/article/modifiers_1767>

<https://help.prusa3d.com/article/per-model-settings_1674>

Use this to justify keeping regions/parts distinguishable. Verify overlapping-volume semantics and available settings in the exact target slicer.

### Top/bottom and internal patterns

Prusa documents selectable top/bottom fill patterns and warns that same-layer grid crossings can accumulate material and risk nozzle contact:

<https://help.prusa3d.com/article/infill-patterns_177130>

Use this to support path-family cautions. Density, angles, cell pitch, and crossing behavior remain slicer/profile specific.

### Mesh simplification

Prusa documents that dense scan/sculpt meshes can slow import, slicing, and even printers through many short toolpaths, and provides a mesh-simplification feature:

<https://help.prusa3d.com/article/simplify-mesh_238941>

Use this as implementation evidence, not as permission to simplify by a percentage without physical error and protected-region checks.

### 3MF

The 3MF Consortium publishes the format specifications for units, geometry, transforms, metadata, materials/properties, slices, and extensions:

<https://3mf.io/spec/>

Use 3MF as the preferred manufacturing project/container when the slicer preserves named parts and settings. Do not assume every slicer writes or reads every extension or proprietary project field identically.

The beam-lattice extension illustrates that node/beam representations can be much more compact than triangulated lattice meshes:

<https://3mf.io/blog/2023/09/reducing-file-size-with-.3mf-beam-lattice/>

This is format evidence, not proof that the user's slicer can manufacture that extension directly.

## Direct-path and firmware sources

### FullControl

Gleadall, A. (2021), “FullControl GCode Designer: open-source software for unconstrained design in additive manufacturing,” *Additive Manufacturing*, 46, 102109:

<https://doi.org/10.1016/j.addma.2021.102109>

Project site:

<https://fullcontrolgcode.com/>

Use this as evidence that parametric direct print-path design and non-planar paths are feasible and have documented applications. It does not certify a generated file for a particular printer, firmware, material, or collision envelope.

### Marlin motion commands

Marlin documents linear moves and extrusion coordinates with `G0/G1`, arcs with `G2/G3`, and print/travel acceleration with `M204`:

<https://marlinfw.org/docs/gcode/G000-G001.html>

<https://marlinfw.org/docs/gcode/G002-G003.html>

<https://marlinfw.org/docs/gcode/M204.html>

Use the documentation only for the matching firmware/configuration. Other firmware may implement modes, limits, macros, leveling, arcs, and state differently.

## Workflow heuristics requiring validation

The following are conservative starting policies from the linked 3D-printing skills rather than universal standards:

- classify detail below about `0.75 × line_width` as material/optical first;
- explore `0.75–3 × line_width` with toolpath methods;
- explore macro vector geometry above about `3 × line_width`;
- begin subtle relief coupons around half to two nominal layers;
- target at most about one million relief triangles per manufacturing part, review one to five million, and stop/redesign above five million absent measured justification;
- sweep simplification by physical millimetre error and lock functional boundaries;
- retain separate manufacturing identities for regions with different slicer settings and verify their physical connection on a coupon.

Always replace these starting points with measured printer/material/slicer evidence when available.

## Experience-pattern synthesis

Repeated failure patterns across official documentation, research workflows, and practical slicing behavior support these recommendations:

- dense image displacement often spends facets on flat/noisy areas that do not survive FDM resolution;
- same-layer crossings and many short paths can cause buildup, nozzle contact, slow slicing, and controller burden;
- per-part/modifier workflows require project-state preservation and layer inspection;
- direct path design enables unique structures but transfers responsibility from the slicer to the path author;
- optical surface identity frequently depends on material and path direction as much as on geometric relief;
- a small process-matched coupon is the most efficient way to resolve uncertain scale, bond, sheen, and tactile behavior.

Treat these as design/process patterns, not universal quantitative laws.
