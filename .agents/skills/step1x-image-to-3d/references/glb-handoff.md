# GLB handoff to functional CAD and slicers

Read this reference before editing or exporting either Step1X GLB.

## What the two GLBs are

- `geometry.raw.glb`: highest-fidelity untextured generation result and preferred geometry master.
- `textured.raw.glb`: UV/albedo appearance master. In the current local app its working mesh is cleaned/reduced before texture generation, so it may have substantially fewer faces than the raw geometry.

Keep both immutable and hashed. Work from copies.

glTF/GLB is a scene-delivery format. Its specification uses a right-handed coordinate system, +Y up, +Z forward and metres for linear distances. Those declarations describe file semantics, but Step1X does not know the target product dimension. The generated physical scale is therefore non-authoritative until registered to a known datum or envelope.

## Format responsibilities

| Need | Deliverable | Rule |
|---|---|---|
| textured inspection, presentation, Blender source | GLB plus optional `.blend` | preserves nodes, transforms, UVs, textures/material appearance |
| dense organic working geometry | GLB/PLY/OBJ or native mesh project | remain mesh-native; save registration transform |
| exact functional solids/interfaces | native CAD plus STEP | rebuild authoritative surfaces/features parametrically |
| simple one-material slicer input | binary STL in documented millimetres | geometry only; no units, colors or texture |
| portable print assembly/material intent | 3MF | defined units/components/material metadata; verify receiver |
| destination slicer settings/paint/slots | slicer project 3MF | application-specific metadata is not generally portable |

Never create a `.step` filename from triangles and imply a useful B-Rep. A face-per-triangle conversion of a dense GLB is usually huge and fragile. Use the mesh as a visual/reference authority, simplify a proxy for clearances, and create exact CAD-owned faces, holes, threads, seats and load paths separately.

## Intake

```bash
python scripts/glb_to_print_mesh.py inspect geometry.raw.glb \
  --report reports/geometry-intake.json

python scripts/glb_to_print_mesh.py inspect textured.raw.glb \
  --report reports/textured-intake.json
```

Check nodes/transforms, bounds, components, vertices/faces, watertightness, winding, volume, materials/textures and finite coordinates. Inspect thin sheets, hidden shells, self-intersections, filled holes and backside invention in Blender or another mesh-native tool.

## Establish scale and orientation

1. Name semantic front/up and project frame from the approved design contract.
2. Choose at least one known target dimension; three non-collinear landmarks are stronger.
3. Solve uniform physical scale separately from rigid placement.
4. Register to CAD datums/landmarks or fitted primitives; use PCA/bounds only as an initial guess.
5. Save the complete 4×4 transform and residual/error checks.

For a simple disposable STL derivative, the bundled converter requires an explicit physical target and orientation decision:

```bash
python scripts/glb_to_print_mesh.py convert geometry.raw.glb \
  --output manufacturing/candidate.stl \
  --target-longest-mm 120 \
  --y-up-to-z-up --place-on-bed \
  --report reports/glb-to-stl.json
```

Use `--scale-factor-to-mm` instead when registration already produced an exact uniform conversion factor. The script refuses a manufacturing conversion without explicit scale and refuses non-watertight output unless `--allow-nonwatertight` is supplied for a diagnostic artifact.

The conversion report records the transform and hashes. It does not repair geometry, prove wall thickness or make the STL release-ready.

## Route by design intent

### Organic mesh plus precise post-processing

Load `organic-mesh-functionalization`:

1. preserve the raw GLB;
2. make a decimated proxy;
3. declare protected/edit/interface/keep-out regions;
4. create CAD cutters, backers or inserts parametrically;
5. use a mesh Boolean, local repair or narrow-band SDF fallback;
6. compare protected surfaces and validate topology;
7. export the final mesh body and keep the exact insert/cutter STEP sources.

Use this for holes, channels, cavities, mounting eyes, cable/air paths, soles and organic-to-CAD joints. Use modeled thread geometry only when justified and printable; otherwise use a tap drill, heat-set insert, captive nut or purchased threaded component.

### Exact CAD reconstruction

Use the GLB only as reference/proxy. Reconstruct critical profiles, sections, primitives and surfaces in CadQuery/FreeCAD/OpenSCAD. STEP is legitimate only for the rebuilt B-Rep solids. Retain a mesh overlay and deviation report to show how visible form was transferred.

### Textured/multicolor printing

PBR-looking pixels are not filament. The Step1X paper states the current texture pipeline is limited to albedo rather than a full PBR material system. Load `multicolor-fdm-design` to:

- normalize/bake the base-color texture;
- map it to an actual measured filament palette;
- remove physically unprintable micro-islands;
- produce explicit aligned color bodies or a tested slicer paint route;
- save portable 3MF and destination-slicer project 3MF separately when needed.

Direct STL export discards UVs, material and texture. Preserve the textured GLB as appearance evidence even when the manufacturing derivative is single-color.

## Slicer gate

Do not assume GLB import support. For the exact destination slicer:

- verify format import and scale with a known dimension;
- confirm one intended body/assembly and orientation;
- inspect every layer around thin features, openings and Boolean seams;
- confirm no disconnected/internal shells or auto-repair changed function;
- record slicer/version/profile and save a project 3MF;
- compare toolpaths to the accepted geometry, not only the shaded preview.

STL has no reliable unit or material semantics. 3MF has defined units and richer properties, but vendor paint, printer slots and profiles can still be application-specific.

## Primary sources

- [Khronos glTF 2.0 specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)
- [3MF Consortium specifications](https://3mf.io/spec/)
- [Blender glTF import/export manual](https://docs.blender.org/manual/en/4.0/addons/import_export/scene_gltf2.html)
- [Step1X-3D technical report](https://arxiv.org/abs/2505.07747)
