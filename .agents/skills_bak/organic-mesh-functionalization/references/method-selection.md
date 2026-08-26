# Method selection

## Identify the actual representation

An image-to-3D result is usually a triangulated surface, not a CAD solid. It may look closed while containing self-intersections, duplicate shells, inverted components, internal faces, or holes. Determine whether the file is:

- a valid closed manifold solid;
- an open surface shell;
- several overlapping solids;
- a textured scene with multiple objects;
- a dense mesh with disconnected ornamental fragments;
- a volume/SDF or CAD source rather than only a mesh.

## Editing modes

### 1. Direct mesh Boolean

Use when the target and cutter are closed positive-volume meshes, the intersection is well separated from coplanar surfaces, and the high-resolution mesh is otherwise valid.

Best tools: Blender Exact/Manifold, Manifold3D, Trimesh as orchestrator.

### 2. Local remesh plus Boolean

Use when only the edit region is defective. Preserve the untouched exterior and remesh a duplicated/cropped ROI with an overlap band. Join at a deliberately designed seam.

Best tools: Blender, MeshLab/PyMeshLab, OpenVDB/SDF.

### 3. Global voxel/SDF reconstruction

Use when the source has pervasive self-intersections or hollowing/offsetting is more important than preserving microscopic detail. Select voxel size from the smallest feature that must survive and from available RAM.

Best tools: Blender voxel remesh/OpenVDB, custom SDF pipeline, OpenVDB/NanoVDB.

### 4. Skin-preserving replacement

Retain the visible outer shell in a defined band, remove its interior, then add a functional core. Use for decorated dice towers and shoe sidewalls when exterior detail matters more than preserving the original internal topology.

### 5. Envelope replacement

Define a replacement envelope that removes the old region completely. Fit a new CAD body to a seam. Use for soles, bases, battery compartments, mounting planes, and damaged AI-generated geometry.

### 6. Reference-only reconstruction

Do not Boolean the original mesh. Measure cross-sections, silhouette, and landmarks, then rebuild the functional object parametrically. Use when the generated mesh is geometrically unreliable or when dimensional accuracy dominates surface fidelity.

## Decision matrix

| Condition | Direct mesh | Local remesh | Global SDF | CAD rebuild |
|---|---:|---:|---:|---:|
| Clean closed manifold | Best | Optional | Usually unnecessary | For exact parts |
| Local defects near edit | Risky | Best | Possible | Possible |
| Pervasive self-intersection | Poor | Poor | Best | Best if simple envelope |
| Fine ornament outside ROI | Good | Best | Risk of loss | Preserve as separate skin |
| Constant wall thickness needed | Limited | Possible | Best | Good for simple forms |
| Exact interfaces/threads | Poor | Poor | Approximate | Best |
| Millions of triangles | Solver-dependent | Good with ROI | Memory-dependent | Do not convert entire mesh |
| STEP required | No | No | No | Yes |

## Selection questions

1. Is the visible exterior itself required, or only its overall silhouette?
2. Is the operation local or global?
3. What is the smallest detail that must remain?
4. What is the minimum wall and clearance?
5. Does the result need STEP/B-Rep, or is 3MF/STL sufficient?
6. Can the part be split at a natural seam?
7. Are moving parts or assembly access required?
8. Is the source valid enough for a robust Boolean?
9. Can the operation be verified quantitatively?
10. Does the available RAM support the selected voxel resolution?
