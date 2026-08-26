# Integration and validation

## Contents

1. [Preserve authorities and make proxies](#1-preserve-authorities-and-make-proxies)
2. [Normalize and register organic meshes](#2-normalize-and-register-organic-meshes)
3. [Select an integration route](#3-select-an-integration-route)
4. [Execute with a fallback ladder](#4-execute-with-a-fallback-ladder)
5. [Validate architecture and components](#5-validate-architecture-and-components)
6. [Validate integrated geometry](#6-validate-integrated-geometry)
7. [Validate manufacturing and use](#7-validate-manufacturing-and-use)
8. [Package reproducibly](#8-package-reproducibly)

## 1. Preserve authorities and make proxies

Retain:

- immutable evidence images/text and raw generated mesh;
- parametric product/core master;
- interface skeleton and exported interface kit;
- registered organic working mesh;
- integration scene/project;
- final manufacturing bodies.

Never overwrite the only high-resolution organic mesh or the only parametric master.

Use low-resolution proxies for placement, assembly sequence, interface design, and Boolean rehearsals. Preserve seam boundaries and target envelopes more accurately than distant cosmetic detail. Apply the final operation to full-resolution sources only after the proxy path passes.

## 2. Normalize and register organic meshes

### 2.1 Intake

Record:

- file checksum and source tool/model/settings;
- source unit assumption and scale factor to millimetres;
- axes/handedness and transform convention;
- vertices/faces/components;
- bounds/extents, area, volume, and center of mass;
- watertightness, winding, open boundaries, internal shells, and self-intersection status where available;
- texture/material dependencies.

Flatten a scene only after preserving object names and transforms. A GLB may contain several nodes even when it looks like one object.

### 2.2 Initial registration

Use strongest evidence first:

1. parametric datums and matching engineered landmarks;
2. three or more manually identified non-collinear landmark pairs;
3. fitted plane/cylinder/sphere or multiple cross-sections;
4. known envelope dimensions and symmetry;
5. PCA/bounds as an initial guess only.

Solve scale separately from rigid pose. Apply transforms in a declared order and save the final 4×4 matrix.

### 2.3 ICP refinement

Use ICP only after rough alignment. It is a local registration method and can converge to the wrong repeated, symmetric, or low-overlap surface.

- crop to the intended overlap/interface region;
- reject outliers or use robust kernels;
- compare point-to-point and point-to-plane where appropriate;
- report fitness, inlier RMSE, maximum/local residual, and the final transform;
- inspect critical landmarks and sections even if the global residual is small.

Do not let ICP deform a rigid part. If non-rigid warping is required, make it an explicit, bounded design operation and revalidate detail distortion.

### 2.4 Normalize topology only as needed

Fix duplicated vertices/faces, normals, tiny holes, and disconnected debris first. Use local remesh around a damaged seam before global voxel remesh. Preserve textures/attributes or acknowledge their loss.

Do not convert millions of triangles to one B-Rep face per triangle. Use the mesh as a mesh, a simplified proxy for CAD clearance, and exact parametric solids for interfaces.

## 3. Select an integration route

| Situation | Preferred route | Main risk |
|---|---|---|
| replaceable ornament, different color/material | separate keyed insert/backer | fit and visible seam |
| one-material sculpture on exact core | organic root + parametric backer, final mesh union | Boolean slivers/detail loss |
| decorative exterior around mechanisms | shell over parametric core | wall reserve and hidden collisions |
| locally defective AI base | cut-and-replace with CAD body | seam transition |
| shallow 2.5D motif | height map/relief on parametric substrate | banding and excessive triangles |
| dirty/self-intersecting mesh near union | local SDF/voxel reconstruction | shrinkage/detail loss |
| exact thread/snap/bearing | separate parametric insert | load transfer into organic body |
| multi-material print | aligned closed bodies/3MF assembly | slicer overlap/material semantics |

### Separate assembly is often the safer default

Prefer a separate insert when it enables a fit coupon, replacement, support-friendly orientation, material/color separation, or avoids destructive global remeshing. Fuse only when a continuous body is required and the union can be validated.

## 4. Execute with a fallback ladder

### 4.1 Direct mesh Boolean

Use when both bodies are valid closed solids and intersect with clear positive volume. Extend trim/cutter bodies through the target. Avoid coplanar and tangent faces.

Preferred route: Blender Exact/Manifold or Manifold3D, then independent topology validation.

### 4.2 Repair and retry

Repair only diagnosed defects: normals, duplicate faces, tiny holes, non-manifold edges, loose islands, or source components. Re-run the same controlled operation and compare results.

### 4.3 Local remesh

Duplicate/crop the seam ROI with an overlap band, remesh it, preserve the rest of the exterior, and join at a designed boundary. Compare outside-ROI surface distance before accepting.

### 4.4 SDF/voxel route

Use for pervasive self-intersections, hollowing/offsetting, or topologically difficult unions. Choose voxel size from the smallest required physical detail and available memory. Validate shrinkage, smoothing, wall thickness, and volume change.

### 4.5 Redesign the interface

When repeated solver changes fail, change the seam, increase overlap/root thickness, add a backer, or split into an assembly. Do not accumulate random repair operations.

## 5. Validate architecture and components

Separate **plan integrity** from **release readiness**. A clean cross-reference/interface validation only proves that the declared architecture is internally coherent. It does not resolve missing source images, COTS dimensions, materials, loads, printer profiles, fit coupons, or physical tests. Carry those items in `decision_log`, show their blocked gates in every report, and prevent downstream release while `release` remains blocked.

### Architecture gate

Require:

- every critical requirement allocated to one or more components;
- every component linked to a function, appearance role, or manufacturing reason;
- every interface has one nominal owner and a verification method;
- assembly/disassembly sequence is possible;
- loads and functional flows cross defined interfaces;
- safety-critical behavior does not depend on unverified generated geometry.

Run:

```bash
python scripts/plan_hybrid_design.py project.json --validate-only
```

### Proxy gate

Check:

- master envelope and printer/transport constraints;
- component occupancy and target envelopes;
- functional keep-outs and swept volumes;
- mount/tool/finger access;
- center of mass/stability where relevant;
- assembly order and trapped components.

### Organic component intake gate

Check:

- semantic identity and handedness;
- expected component count;
- bounds/extents after the saved transform;
- required negative spaces and silhouettes;
- sacrificial seam reserve;
- watertightness/topology appropriate to the next operation;
- no collision with keep-outs;
- no valuable detail in the edit band.

The bundled mesh checker reports topology, bounds, approximate AABB keep-out hits, and seam-plane statistics. Treat vertex-based keep-out checks as a fast screen, not exact collision proof.

## 6. Validate integrated geometry

### 6.1 Topology and body count

Verify after export round-trip:

- expected number of watertight components;
- consistent winding and positive volume;
- no duplicate/internal faces, zero-area triangles, or loose islands;
- no unintended self-intersections;
- units and bounds unchanged.

Multi-material designs can intentionally contain several bodies; encode the expected count and names.

### 6.2 Interface geometry

Measure:

- contact/seat position;
- gap or positive overlap as applicable;
- insertion/motion clearance;
- anti-rotation engagement and end stop;
- lead-in and assembly direction;
- minimum ligament and edge distance;
- adhesive channel/bond area;
- tool and finger access.

Inspect cross-sections around the full boundary, not one attractive section.

### 6.3 Keep-out and swept-volume collision

Test exact or conservative proxies for:

- moving parts and user paths;
- stored objects, cables, ventilation, fluids, and light paths;
- fastener/tool access;
- support removal and assembly motion.

Use a clearance body larger than the nominal moving object by the selected allowance. Static visual non-intersection is insufficient for motion.

### 6.4 Surface preservation

Outside the permitted edit/seam region, sample bidirectional nearest-surface or signed distance between source and result. Report median, P95/P99, maximum, and location. A small P95 can hide one severe local breach.

Use matched orthographic and hero-view clay renders, section overlays, and distance heat maps. Texture must not conceal geometry changes.

### 6.5 Volume accounting

Compare expected cutter intersection, removed volume, inserted/backer volume, and final volume delta. Unexpected differences reveal missed cuts, duplicate shells, or unjoined bodies.

## 7. Validate manufacturing and use

### 7.1 Slicer gate

Inspect every layer around:

- thin relief, small gaps, and negative spaces;
- seam/backer/root transition;
- pins, sockets, dovetails, clips, and adhesive channels;
- multi-material body boundaries;
- support contacts and inaccessible support;
- wall count and local gaps;
- layer direction across transferred loads.

The CAD/mesh result is not accepted merely because the slicer imports it.

### 7.2 Coupon hierarchy

Test in this order:

1. printer/material calibration relevant to the feature;
2. fit series for the exact interface orientation;
3. seam/backer/root subassembly with representative layers and material;
4. mechanism/load/use test where relevant;
5. full product.

Do not reuse a horizontal-hole clearance coupon as proof for a vertical dovetail or TPU interference fit.

### 7.3 Use-case gate

Define measurable tests: cycles, drops, loads, jam clearing, wash/heat/moisture exposure, leak/airflow/light check, wear, or user access. Preserve failed samples and feed measured process compensation back into the manufacturing profile, not into the nominal interface definition.

## 8. Package reproducibly

Recommended structure:

```text
evidence/                 original images, text, masks, camera notes
plan/                     design plan, requirements, interface graph
proxies/                  envelopes, keep-outs, swept volumes
parametric/               editable core, interfaces, backers, cutters
organic/raw/              immutable AI/scan outputs and checksums
organic/registered/       working meshes and transform records
integration/              Blender/mesh project and operation config
manufacturing/            separated 3MF/STL/STEP/GLB bodies
reports/                  architecture, mesh, distance, slicer, test data
coupons/                  sources, profile, measurements, chosen allowance
```

Include software/model versions, units, coordinate convention, transform matrices, interface revision, and exact commands. Keep final manufacturing files derived; do not make them the only editable authority.

Use STEP for exact parametric solids, GLB for textured mesh review, and 3MF for named/material-aware print assemblies when supported. STL carries triangles and no reliable unit/material semantics.
