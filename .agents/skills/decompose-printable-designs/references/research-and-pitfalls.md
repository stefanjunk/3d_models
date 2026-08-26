# Research basis, experience reports, and pitfalls

Research checked 2026-08-16. Prefer primary papers, official project repositories, and official documentation. Re-check model versions, supported inputs, licenses, hardware, and file-format behavior before acting.

## Contents

1. [Why decomposition and interface control come first](#1-why-decomposition-and-interface-control-come-first)
2. [What part-aware 3D research supports](#2-what-part-aware-3d-research-supports)
3. [What single-view generation cannot establish](#3-what-single-view-generation-cannot-establish)
4. [Registration evidence](#4-registration-evidence)
5. [Mesh/CAD integration evidence](#5-meshcad-integration-evidence)
6. [FDM fit and file-format evidence](#6-fdm-fit-and-file-format-evidence)
7. [Published implementation reports](#7-published-implementation-reports)
8. [Pitfall catalogue](#8-pitfall-catalogue)
9. [Claims this skill does not make](#9-claims-this-skill-does-not-make)

## 1. Why decomposition and interface control come first

NASA's Systems Engineering Handbook separates logical decomposition, design solution definition, product integration, verification, and interface management. Interface work products include interface requirements/control documents, responsibilities, change rationale, anomalies, and verification support. This supports treating the interface graph and integration plan as controlled artifacts rather than informal CAD cleanup.

- NASA, *Systems Engineering Handbook*, Rev. 2: logical decomposition, product integration, and interface management. <https://science.nasa.gov/wp-content/uploads/2023/04/nasa_systems_engineering_handbook_0.pdf>
- NASA, *System Design Processes*: identify physical and functional interfaces while defining system behavior and external/enabling systems. <https://www.nasa.gov/reference/4-0-system-design-processes/>
- NASA, *System Engineering Handbook Appendix*: integration planning should state which elements are integrated, in what sequence, with which verification and anomaly handling. <https://www.nasa.gov/reference/system-engineering-handbook-appendix/>

Design implication: use linked functional, physical, appearance, manufacturing, and lifecycle decompositions. A visual part hierarchy alone is not sufficient for a printable product.

## 2. What part-aware 3D research supports

### 2.1 Explicit parts improve editability and control

PartGen reconstructs/generates meaningful parts from text, images, or an unstructured 3D object. It uses multiview segmentation and reconstructs parts in context so they remain coherent. This supports generating component families with contextual awareness instead of repeatedly regenerating a monolithic object.

- Chen et al., *PartGen: Part-level 3D Generation and Reconstruction with Multi-view Diffusion Models*. <https://arxiv.org/abs/2412.18608>
- Official project page. <https://silent-chen.github.io/PartGen/>

OmniPart accepts an image plus a part-identity mask, plans part layout, and generates structured parts. Its official command-line flow requires a segmentation mask. This supports stable semantic IDs and masks in generation briefs.

- Yang et al., *OmniPart: Part-Aware 3D Generation with Semantic Decoupling and Structural Cohesion*. <https://arxiv.org/abs/2507.06165>
- Official repository and mask input format. <https://github.com/HKU-MMLab/OmniPart>

More recent work reports that part identity and layout can become entangled, causing slot swapping or part merging. Identity-aligned semantic tokens and one-to-one layout allocation are proposed to improve stability.

- Hao et al., *ISAP-3D: Identity-Slot Aligned Part-Aware 3D Generation*. <https://arxiv.org/abs/2606.12099>

Design implication: assign stable component IDs, repeated-part indices, consistent mask colors, target envelopes, and local frames before generation. Do not rely on an automatic segmentation's unnamed slots.

### 2.2 Coarse spatial scaffolds help composition

CompoSE uses coarse primitives/bounding boxes as part layouts; Assembler uses part geometry plus a reference image to infer plausible assembly. Compos3D reports that remixing selected components gives users more control than repeated whole-object regeneration.

- *CompoSE: Compositional Synthesis and Editing of 3D Shapes via Part-Aware Control*. <https://arxiv.org/abs/2605.19350>
- Zhao et al., *Assembler: Scalable 3D Part Assembly via Anchor Point Diffusion*. <https://arxiv.org/abs/2506.17074>
- *Compos3D: Interactive Part-Based Composition for Generative 3D Modeling*. <https://arxiv.org/abs/2607.12193>

Design implication: make a coarse parametric assembly and target envelopes before high-resolution organic generation. Use generated layouts as candidates, not as authoritative mechanical placement.

### 2.3 Part-aware does not mean manufacturing-aware

These papers optimize semantic structure, visual cohesion, editability, or plausible assembly. They do not establish FDM wall thickness, precise clearances, anisotropic strength, seal performance, or verified Boolean topology. Keep manufacturing interfaces parametric and validate them independently.

## 3. What single-view generation cannot establish

Single-view 3D is inherently ambiguous: different shape/pose combinations can project similarly, and hidden geometry has multiple plausible completions.

- Wu et al., *Shape-Pose Ambiguity in Learning 3D Reconstruction from Images*. <https://cdn.aaai.org/ojs/16405/16405-13-19899-1-2-20210518.pdf>
- Fan, Su, and Guibas, *A Point Set Generation Network for 3D Object Reconstruction from a Single Image*. <https://arxiv.org/abs/1612.00603>
- Yao et al., *Front2Back: Single View 3D Shape Reconstruction via Front to Back Prediction*. <https://arxiv.org/abs/1912.10589>

Official current image-to-3D projects likewise describe single-image inputs or optional multiview control, but output an asset/mesh rather than a tolerance-controlled CAD solid:

- Tencent Hunyuan3D 2.1 official repository. <https://github.com/tencent-hunyuan/hunyuan3d-2.1>
- Hunyuan3D multiview model card and named view API. <https://huggingface.co/tencent/Hunyuan3D-2mv>
- Microsoft TRELLIS.2 official repository. <https://github.com/microsoft/trellis.2>

Design implication: label hidden backs and interfaces as designed, not recovered. Generate sacrificial material and replace the interface with an authoritative CAD body.

## 4. Registration evidence

Open3D documents ICP as a local registration method that requires a rough initial alignment; global registration is used to obtain initialization before local refinement. Robust kernels reduce outlier influence but do not remove symmetry or low-overlap ambiguity.

- Open3D, *ICP registration*. <https://www.open3d.org/docs/latest/tutorial/pipelines/icp_registration.html>
- Open3D, *Global registration*. <https://www.open3d.org/docs/release/tutorial/pipelines/global_registration.html>
- Open3D, *Robust kernels*. <https://www.open3d.org/docs/0.17.0/tutorial/pipelines/robust_kernels.html>
- Trimesh registration API: Procrustes/landmarks for initial placement, ICP for refinement. <https://trimesh.org/trimesh.registration.html>

Design implication: align from explicit datums/landmarks or fitted primitives, crop to the true overlap region, then use ICP. Save the transform and inspect local interface residuals; a low global RMSE can hide a wrong symmetric placement.

## 5. Mesh/CAD integration evidence

### 5.1 Boolean robustness and manifold input

Blender documents different Boolean solvers; the Exact solver is intended for difficult/coplanar cases, while the Manifold solver requires manifold input. Manifold3D emphasizes guaranteed-manifold output given valid manifold inputs and exposes failures rather than silently accepting arbitrary broken meshes.

- Blender Python API, Boolean solver behavior. <https://docs.blender.org/api/current/bpy.types.BooleanModifier.html>
- Blender Manual, Mesh Boolean. <https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/mesh/operations/mesh_boolean.html>
- Manifold3D official repository. <https://github.com/elalish/manifold>
- Trimesh official documentation and Boolean routing. <https://trimesh.org/>

Design implication: ensure clear positive overlap, avoid tangent/coplanar interfaces, keep cutters/backers as separate artifacts, and validate the exported result. Do not assume a Boolean preview is a valid solid.

### 5.2 Remeshing trades topology for detail

Blender's voxel remesh rebuilds geometry from a volume/grid and can lose mesh attributes and detail depending on voxel size. Decimation/remeshing should therefore be localized or quantitatively compared.

- Blender Manual, voxel remesh. <https://docs.blender.org/manual/en/latest/sculpt_paint/sculpting/tool_settings/remesh.html>
- Blender Manual, remeshing overview. <https://docs.blender.org/manual/en/latest/modeling/meshes/retopology.html>
- Trimesh proximity/signed-distance API. <https://trimesh.org/trimesh.proximity.html>

Design implication: preserve a source mesh, remesh only the seam ROI where possible, and measure surface deviation outside the edit band.

### 5.3 Parametric assemblies need defined constraints

CadQuery supports explicit assembly locations and constraints. Its documentation notes that underconstrained assemblies can have multiple solutions and initial placement can influence the solved result.

- CadQuery, *Assemblies*. <https://cadquery.readthedocs.io/en/latest/assy.html>

Design implication: fully constrain interface datums, orientation, and anti-rotation. Do not rely on visual placement or a single coincident point.

## 6. FDM fit and file-format evidence

Prusa's official design guidance states that there is no universal fit tolerance; geometry, orientation, calibration, settings, material, and model size matter. It recommends test iterations, lead-in chamfers, manifold solids, and separate closed meshes for multi-material work.

- Prusa Research, *Modeling with 3D printing in mind*. <https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135>

Experimental studies likewise show dimensional error depends on printer/process parameters and feature geometry, supporting process-matched coupons instead of one global clearance number.

- Grgić et al., *Accuracy of FDM PLA Polymer 3D Printing Technology in the Context of Assembly*. <https://www.mdpi.com/2227-9717/11/10/2810>
- Passeraub et al., *A Study of Fit and Friction Force as a Function of Clearance in Material Extrusion*. <https://www.mdpi.com/2504-4494/8/6/249>

The 3MF Consortium defines a manufacturing format with units, object resources, transforms, materials/properties, and extensions beyond STL's triangle-only role. Actual slicer support must still be verified.

- 3MF Consortium specification suite. <https://3mf.io/spec/>
- 3MF Core Specification repository. <https://github.com/3MFConsortium/spec_core>

Design implication: keep nominal and process compensation separate; print an orientation/material-specific fit series; use 3MF for named/material-aware assemblies when the target tool preserves it.

## 7. Published implementation reports

Official project issue trackers are primary field reports, not universal benchmarks. Use them to identify what must be verified locally.

- A Hunyuan3D 2.1 issue reports multiview implementation/code paths that were not usable with the released model/config at that time. This supports verifying an advertised or discoverable input mode end-to-end before basing a production workflow on it. <https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1/issues/143>
- Another Hunyuan3D 2.1 issue reports a severe texture-inpainting runtime bottleneck for a custom workflow. This supports separating shape and texture stages and benchmarking on representative assets. <https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1/issues/139>
- Manifold3D's repository and discussions document that arbitrary implicit/triangle inputs can stress Boolean pipelines and that valid manifold input remains important. <https://github.com/elalish/manifold> and <https://github.com/elalish/manifold/discussions/340>

Do not bake these reports into permanent capability claims. Re-check issue status, current release, hardware, and reproducibility.

## 8. Pitfall catalogue

### 8.1 Source and decomposition

| Pitfall | Detection | Prevention/recovery |
|---|---|---|
| shadow or material boundary becomes a part seam | boundary changes with lighting/view | classify geometry vs appearance; compare views |
| concept image treated as dimensioned drawing | unknown camera/scale or inconsistent views | state visual claim; add known dimension and blockout |
| text implementation guess treated as requirement | no underlying function stated | extract use scenarios and verbs first |
| automatic part segmentation controls manufacturing split | parts cannot be printed/assembled | regroup by authority, material, orientation, and lifecycle |
| decomposition too fine | many weak seams and style drift | use largest component with one coherent authority |
| decomposition too coarse | monolithic regeneration and interface edits | split at authority/material/service boundaries |

### 8.2 Organic generation

| Pitfall | Detection | Prevention/recovery |
|---|---|---|
| background or neighbour fused into mesh | extra geometry/components | separate evidence crop from isolated generation plate |
| part identities swap or merge | repeated/mirrored parts inconsistent | fixed IDs, masks, indices, target boxes; generate separately if needed |
| generated back collides with core | hidden volume exceeds envelope | declare backside sacrificial; trim with CAD keep-out/seat |
| prompt requests exact dimensions but output drifts | bounds do not match | scale/register after generation; never assign interface ownership to prompt |
| texture hides bad massing | clay render fails | approve silhouette/negative space before texture |
| separate components have style drift | inconsistent detail/edge character | shared style sheet, same model/settings, calibration component |
| thin decorative roots break | narrow neck at seam | generate a thick sacrificial root; add parametric backer/load spreader |

### 8.3 Registration and integration

| Pitfall | Detection | Prevention/recovery |
|---|---|---|
| ICP locks onto wrong symmetric region | low global RMSE but wrong landmarks | landmark initialization, crop ROI, inspect local residuals |
| STL imported at wrong scale | bounds differ by 10×/25.4×/1000× | explicit units and source-to-mm scale in manifest |
| triangle-to-BRep freezes CAD | huge face count/fragile document | retain mesh; use proxy or mesh Boolean; CAD only for exact parts |
| coplanar/tangent Boolean creates slivers | non-manifold edges or missing faces | positive overlap and through-cutters; change seam/solver |
| global remesh erases ornament | distance/texture loss outside seam | local ROI remesh; preserve source; measure deviation |
| organic detail is trimmed unexpectedly | seam cut crosses protected feature | no-detail sacrificial band and trim preview on proxy |
| hidden duplicate/internal shells survive | slicer reports many parts/odd volume | inspect components, section, and volume accounting |

### 8.4 Parametric counterpart and assembly

| Pitfall | Detection | Prevention/recovery |
|---|---|---|
| both sides own same nominal interface | duplicated dimensions drift | third skeleton or single owner with derived bodies |
| zero-tolerance CAD fit | parts do not assemble | separate nominal/compensation; print exact-process coupon |
| adhesive is the only locator | part floats while curing | shoulder/pins/key plus controlled bond gap |
| assembly order traps a component | motion/access collision | model exploded sequence, tools, fingers, and removal path |
| visible ornament carries structural load accidentally | load path passes only through mesh union | continuous parametric core or separately engineer/test root |
| multi-material bodies double-extrude/leave gaps | slicer boundary preview fails | follow target slicer's overlap/coincident-body semantics |
| curved relief stretches after conforming | motif width/spacing varies | parameter-space mapping, multiple patches, or rigid inlay |
| process correction pollutes nominal CAD | future printer/profile breaks fit | store compensation in manufacturing configuration |

### 8.5 Validation and release

| Pitfall | Detection | Prevention/recovery |
|---|---|---|
| attractive render accepted as geometry proof | no sections/mesh report | independent topology, distance, wall, and slicer gates |
| one coupon reused for all orientations/materials | inconsistent real fits | match process, orientation, material, and feature family |
| final STL becomes only master | impossible to revise interface | retain parametric/organic authorities and transforms |
| stale interface kit assembled with new core | revision mismatch | version interface bodies and transforms together |
| imported multi-part file loses names/materials | slicer shows one body | verify 3MF/GLB/STEP behavior in target tool and retain manifest |

## 9. Claims this skill does not make

- Part-aware AI output is not automatically dimensionally accurate, watertight, or printable.
- A specific numeric FDM clearance is not universal.
- ICP residual alone does not prove correct semantic registration.
- A manifold Boolean does not prove adequate wall thickness or load performance.
- A matched hero-view render does not recover hidden geometry.
- A high-resolution mesh does not guarantee physically printable detail.
- A successful prototype does not create a certified load, safety, food, medical, or regulatory claim.
