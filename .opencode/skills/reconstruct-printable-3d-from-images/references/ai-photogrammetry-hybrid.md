# AI, photogrammetry, and hybrid reconstruction

## Contents

1. [Select the method](#1-select-the-method)
2. [Single-image AI reconstruction](#2-single-image-ai-reconstruction)
3. [Photogrammetry](#3-photogrammetry)
4. [Hybrid mesh and CAD](#4-hybrid-mesh-and-cad)
5. [Cleanup and print conversion](#5-cleanup-and-print-conversion)
6. [Failure patterns](#6-failure-patterns)

## 1. Select the method

| Need | AI image-to-3D | Photogrammetry | Manual/parametric | Hybrid |
| --- | --- | --- | --- | --- |
| One concept image | Good draft, hidden areas invented | Not applicable | Good for simple/functional forms | Usually best |
| Many photos of a real object | Optional completion | Strong choice | Useful for measured interfaces | Strong choice |
| Exact dimensions | Weak unless constrained later | Scale must be added | Strong | Strong |
| Organic exterior | Strong starting point | Strong when capturable | Labor-intensive | Strong |
| Functional/mating geometry | Unreliable | Surface only | Strong | Strong |
| Color/PBR appearance | Often available | Photo texture available | Limited | Strong |
| Low memory/CPU-only | Older/light models or manual | Possible but slow/heavy | Usually strongest | Moderate |

Do not call a generated mesh a reconstruction without qualifying that unseen geometry is synthesized. Do not call a photogrammetry result dimensionally calibrated until scale is solved and checked.

## 2. Single-image AI reconstruction

### Suitable use

Use AI generation for:

- organic toys, figurines, decorative shells, and concept exploration;
- a fast base mesh whose proportions will be corrected against the source;
- generating several hidden-geometry hypotheses;
- texture/PBR drafts for appearance comparison.

Avoid using the raw result as final engineering geometry for clips, threads, snap fits, bearings, seals, load paths, or dimensional interfaces.

### Input preparation

Prepare an object-centered image with:

- clean or transparent background;
- full silhouette and no crop at extremities;
- moderate perspective and minimal occlusion;
- even illumination and recoverable shadow detail;
- sufficient resolution for identifying shape, but not artificial upscaling presented as evidence;
- a separate note describing thin parts, holes, backside, and symmetry that the model cannot see.

Generate multiple candidates with fixed input, record seed/settings when supported, and compare all candidates using matched views. Select topology and massing before texture sharpness.

### Current open examples

The ecosystem changes quickly. Verify the official repository, license, platform, weights, and memory before installing.

| Tool/model | Use | Officially reported memory notes | Caution |
| --- | --- | --- | --- |
| TripoSR | Fast single-image shape draft | About 6 GB VRAM for default single-image inference | Older, simpler appearance pipeline; backside remains inferred |
| Stable Fast 3D | Fast UV-unwrapped mesh and material draft | About 6 GB VRAM for default single-image inference | Gated weights/license conditions; remeshing adds CPU work |
| Hunyuan3D 2.1 | Higher-detail shape plus PBR texture | Project reports about 10 GB shape, 21 GB texture, 29 GB combined | Heavy installation and VRAM; verify current code and license |
| TRELLIS.2 | High-resolution topology and PBR research workflow | Official repository requires at least 24 GB GPU memory; high resolutions tested on H100 | Large 4B model; output may include open/non-manifold surfaces unsuitable for printing |

See [research-sources.md](research-sources.md) for official links and dates. These memory figures describe model inference, not Blender cleanup, texture baking, export, or concurrent applications.

### Acceptance of an AI draft

Reject or repair:

- filled openings and fused gaps;
- melted or duplicated limbs/features;
- false symmetry;
- thin sheets, open surfaces, non-manifold junctions, and internal shells;
- texture painted across geometric boundaries;
- view-dependent geometry that matches only the input camera;
- high polygon count without corresponding physical detail;
- incorrect scale and unit metadata.

Run a clay render first. If the clay render fails, texture quality is irrelevant.

## 3. Photogrammetry

### Capture

Follow the reconstruction tool's current capture guidance. In general:

- keep high visual overlap and observe each surface in at least several images;
- walk the camera around the object rather than rotating in place;
- add high and low rings plus close-ups where needed;
- keep focus, exposure, zoom, and white balance stable;
- use diffuse lighting and avoid moving shadows, specular highlights, transparency, and motion;
- capture textured surroundings or removable markers when the surface lacks keypoints;
- include a scale bar or measured distance that remains rigid;
- avoid redundant video frames; downsample a video to useful baseline changes.

COLMAP explicitly recommends high overlap, similar illumination, non-specular surfaces, and seeing each object in at least three images. More images are not automatically better; they increase matching and dense-reconstruction cost.

### Pipeline

1. Preserve and organize images; keep camera groups/intrinsics consistent.
2. Calibrate or recover intrinsics; verify EXIF assumptions.
3. Extract and match features.
4. Solve camera poses and sparse structure.
5. Inspect registered-image coverage and reprojection error.
6. Compute dense depth/normal maps.
7. Fuse the point cloud.
8. Reconstruct a surface.
9. Remove environment/turntable fragments.
10. Scale and orient from measured references.
11. Fill only justified holes; keep a raw scan copy.
12. Retopologize/decimate with error comparison.
13. Create thickness and functional geometry.
14. Texture if appearance is needed.

Use COLMAP for explicit SfM/MVS control or Meshroom/AliceVision for a node-based open pipeline. Commercial/mobile scanners can be efficient, but verify export, scale, privacy, licensing, and raw-camera access.

### Memory controls

For out-of-memory conditions:

- reduce maximum input image size before lowering geometric quality elsewhere;
- reduce source images per reference image;
- reduce feature or match counts only with awareness that robustness may fall;
- reduce dense stereo/fusion cache sizes, accepting slower disk use;
- split large captures into overlapping clusters;
- reconstruct a representative subset first;
- close render and AI applications competing for VRAM.

Record the downsample factor so image-space errors can be converted back to source pixels and physical dimensions.

## 4. Hybrid mesh and CAD

Use hybrid construction when appearance and function need different representations.

### Recommended architecture

- Keep a high-resolution source mesh immutable.
- Make a cleaned working mesh with reduced faces.
- Define datum planes, axes, envelopes, and interface dimensions in CAD.
- Build functional solids parametrically.
- Reserve a controlled overlap or clearance between mesh and CAD regions.
- Join only at the final print-master stage; retain separate editable masters.

### Interface strategies

1. **Cut-and-replace:** Remove an unreliable region and replace it with a BRep solid.
2. **Insert:** Cut a keyed pocket into the organic body and print/assemble a separate parametric insert.
3. **Shell over core:** Retain a decorative mesh shell around a parametric structural core.
4. **Boolean envelope:** Use a simplified proxy of the organic mesh for CAD clearance and keep the detailed mesh for the final Boolean.
5. **Split manufacturing:** Export separate aligned bodies for materials, color, or easier supports.

Avoid converting millions of mesh triangles directly to one BRep face per triangle. That creates huge, fragile CAD documents. Simplify, segment, or use a mesh-aware Boolean/SDF/voxel method.

### Registration

Register mesh and CAD using:

- three or more non-collinear landmarks;
- a fitted plane/cylinder/sphere on measured regions;
- iterative closest point only after a sensible initial alignment;
- known datum dimensions;
- explicit unit conversion.

Save the transformation matrix and RMS/maximum residual. Check critical interfaces manually; a low global residual can hide local mismatch.

## 5. Cleanup and print conversion

### Topology cleanup

Check:

- disconnected islands;
- open boundaries and holes;
- non-manifold edges and vertices;
- flipped normals and inconsistent winding;
- self-intersections and internal faces;
- zero-area/needle triangles;
- thin sheets and accidental double walls;
- texture seams before/after remeshing.

Use voxel remeshing to regularize severely broken organic meshes, but choose voxel size from physical detail and validate shrinkage. Use decimation for a sound mesh when topology quality is less important than surface fidelity. Reproject color/detail only when the tool supports it and inspect the result.

### Create a solid

Generated or scanned assets are often surfaces. Create a printable volume by:

- closing boundaries with evidence-backed patches;
- adding controlled wall thickness;
- adding a flat or keyed base;
- unioning intended components;
- removing trapped internal shells;
- adding drain/vent holes for hollow resin prints;
- ensuring every printed body represents a valid volume or a supported slicer-specific surface mode.

Do not use a global “make solid” operation without comparing before/after silhouettes and sections.

### Decimation acceptance

Keep a decimated mesh only if:

- critical dimensions stay within tolerance;
- matched-view silhouette and boundary errors remain acceptable;
- negative spaces and thin parts survive;
- surface deviation remains below the process/detail budget;
- texture coordinates and material boundaries remain valid where needed;
- file/runtime reduction is material.

## 6. Failure patterns

| Symptom | Likely cause | Response |
| --- | --- | --- |
| Front matches, side is bloated | single-view depth prior | add side evidence or manually constrain sections |
| Back invents random detail | hidden-region synthesis | simplify, enforce symmetry, or model a deliberate back |
| Photogrammetry has holes on glossy areas | view-dependent highlights/weak features | dull removable coating where permitted, diffuse light, more angles |
| Model is lumpy after scan cleanup | noisy dense cloud or over-small remesh voxel | filter outliers, use larger voxel, preserve sharp boundaries separately |
| CAD freezes after mesh import | triangle-to-BRep conversion | use proxy mesh, decimate, segment, or mesh Boolean workflow |
| Texture looks detailed but print is smooth | detail stored only in texture or below process limit | convert selected bands to relief and print a coupon |
| Boolean deletes ornament | coplanar/tiny triangles or tolerance conflict | use overlap, repair mesh, simplify local region, or voxel/SDF Boolean |
| Slicer reports many parts | disconnected shells/internal fragments | inspect components and union/delete intentionally |
