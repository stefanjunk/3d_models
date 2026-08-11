# Tool decision: OpenSCAD, CadQuery, FreeCAD, Blender

## Decision summary

| Need | Primary tool | Secondary/hybrid tool |
|---|---|---|
| precise functional part, STEP, fillets, assemblies | CadQuery | FreeCAD for interactive review/FEM |
| simple CSG, repeated layout, text/SVG relief, CLI parameters | OpenSCAD | Blender for organic finishing |
| interactive STEP editing, drawings, FEM, GUI workflow | FreeCAD | CadQuery for reproducible generation |
| organic STL/OBJ/GLB, scans, sculpt, remesh, texture | Blender | CadQuery for precise inserts/interfaces |
| dense field-driven cells or image height maps | NumPy/SDF/mesh pipeline | CadQuery for functional edges |

Run:

```bash
python scripts/select_tool.py --help
```

## OpenSCAD

Choose OpenSCAD when the design is naturally described as primitives, 2D profiles, extrusion, hull, Minkowski/offset, difference, and arrays.

Strong uses:

- boxes, organizers, trays, simple enclosures;
- lattice-like repeated 2D patterns;
- embossed/debossed text or imported SVG/DXF relief;
- compact Customizer parameters;
- deterministic CLI STL/3MF/PNG generation;
- BOSL2/NopSCADlib components.

Avoid as the main tool when:

- STEP/B-Rep is a required master;
- local fillets/face references are central;
- the input is a damaged organic mesh;
- thousands of high-resolution booleans make the CSG tree slow;
- equal wall offsets on complex organic surfaces are required.

## CadQuery

Choose CadQuery as the default source-first tool for functional parts.

Strong uses:

- exact workplanes, sketches, extrusions, revolves, lofts, holes, fillets, chamfers;
- STEP and assembly output;
- reusable Python calculations and tests;
- interfaces around bearings, shafts, inserts, fasteners, and electronics;
- `cq_warehouse`, `cq_gears`, and other Python libraries.

Best practices:

- create local workplanes from existing geometry;
- avoid brittle selectors where named construction geometry is possible;
- keep feature counts and booleans reasonable;
- export STEP as the design-neutral master and tessellate separately for printing;
- validate that fillets and shells work across the full parameter range.

Avoid as the main tool when:

- editing dense imported organic triangle meshes;
- generating millions of texture facets;
- voxel/SDF topology is the natural representation.

## FreeCAD

Choose FreeCAD when GUI inspection and engineering workbenches matter.

Strong uses:

- human-editable STEP/B-Rep refinement;
- TechDraw and documentation;
- FEM workflows with Gmsh/CalculiX or Elmer where available;
- importing a CadQuery-generated STEP for loads, constraints, meshes, and result review;
- mixed manual/automated workflows through Python.

Cautions:

- workbench and API behavior may vary by FreeCAD version;
- automate with version checks and deterministic documents;
- FEM quality depends more on material data, contacts, mesh convergence, and boundary conditions than on the solver button.

## Blender

Choose Blender for organic and mesh-first geometry.

Strong uses:

- STL/OBJ/GLB import and visual repair;
- Voxel Remesh for dirty generated meshes;
- Boolean cutting of cavities in organic models;
- Solidify for suitable surfaces;
- sculpting, retopology, reliefs, displacement, and rendering;
- Blender Python for repeatable headless processing;
- 3D Print Toolbox checks.

Cautions:

- preserve units and apply transforms before export;
- exact functional holes and interfaces should be measured or generated parametrically;
- Voxel Remesh trades detail for robustness and has cubic memory growth;
- a visually smooth mesh can still have non-manifold, thickness, or fit problems.

## Hybrid patterns

### Precise interface plus organic body

```text
CadQuery creates STEP/STL interface cutter
→ Blender modifies/remeshes organic body
→ Boolean union/difference
→ Trimesh validates final mesh
```

### CadQuery master plus FreeCAD FEM

```text
CadQuery parameters → STEP
→ FreeCAD import → mesh/loads/solver
→ numeric result report
→ revise CadQuery parameters
```

### OpenSCAD relief plus precise hardware

```text
CadQuery body and mounting interfaces
→ export neutral geometry
→ Blender/OpenSCAD add noncritical decorative relief
→ final mesh validation
```

### Dense cellular/height-map geometry

```text
CAD boundary → raster/SDF
→ NumPy/scikit-image surface extraction
→ Trimesh cleanup/validation
→ preserve separate CAD interface definition
```
