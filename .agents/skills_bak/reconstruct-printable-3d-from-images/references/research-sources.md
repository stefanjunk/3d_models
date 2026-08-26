# Research sources

Research checked 2026-08-09. Prefer these primary or official sources over derivative tutorials. Re-check versions, licenses, hardware requirements, UI paths, and format support before acting because several projects evolve quickly.

## Skill format

- OpenCode, **Agent Skills**: official `SKILL.md` format, discovery locations, frontmatter and naming constraints, permissions, and troubleshooting. <https://opencode.ai/docs/skills/>

## Reconstruction limits and evaluation

- Wu et al., **Shape-Pose Ambiguity in Learning 3D Reconstruction from Images** (AAAI 2021): documents how an incorrect 3D shape and pose can still match a single projection, supporting explicit single-view uncertainty. <https://cdn.aaai.org/ojs/16405/16405-13-19899-1-2-20210518.pdf>
- Fan, Su, and Guibas, **A Point Set Generation Network for 3D Object Reconstruction from a Single Image**: discusses inherent ground-truth ambiguity and multiple plausible outputs. <https://arxiv.org/abs/1612.00603>
- Yao et al., **Front2Back: Single View 3D Shape Reconstruction via Front to Back Prediction**: uses opposite views, symmetry, silhouettes, depth, and normals to constrain single-view completion. <https://arxiv.org/abs/1912.10589>
- Wang et al., **Image Quality Assessment: From Error Visibility to Structural Similarity**: original SSIM paper; use SSIM only as one image diagnostic. <https://www.cns.nyu.edu/pub/lcv/wang03-reprint.pdf>
- scikit-image metrics API: implementation reference for `structural_similarity`. <https://scikit-image.org/docs/stable/api/skimage.metrics.html>

## Photogrammetry and image processing

- COLMAP, **Structure-from-Motion and Multi-View Stereo**: project overview. <https://colmap.github.io/>
- COLMAP tutorial: official capture guidance, SfM/MVS stages, dense fusion, meshing, simplification, and texturing. <https://colmap.github.io/tutorial.html>
- COLMAP FAQ: official memory/performance controls, calibration guidance, mapper selection, dense source images, image-size and cache controls. <https://colmap.github.io/faq.html>
- AliceVision: official photogrammetric computer-vision framework. <https://alicevision.org/>
- Meshroom: official open-source reconstruction application based on AliceVision. <https://alicevision.org/view/meshroom.html>
- OpenCV repository and official documentation index: image calibration, thresholding, edge detection, morphology, color conversion, and geometric transforms. <https://github.com/opencv/opencv> and <https://docs.opencv.org/>
- OpenCV, **Canny Edge Detection** tutorial. <https://docs.opencv.org/4.13.0/da/d22/tutorial_py_canny.html>
- Inkscape Beginners' Guide, **Tracing an Image**: official/community-maintained Inkscape documentation for bitmap vectorization. <https://inkscape-manuals.readthedocs.io/en/latest/tracing-an-image.html>

## Current open image-to-3D examples

- VAST AI Research and Stability AI, **TripoSR** official repository: single-image reconstruction; README reports about 6 GB VRAM for default inference and optional texture baking. <https://github.com/VAST-AI-Research/TripoSR>
- Stability AI, **Stable Fast 3D** official repository: UV-unwrapped mesh/material reconstruction; README reports about 6 GB VRAM for the default single-image path and documents remeshing options. <https://github.com/Stability-AI/stable-fast-3d>
- Tencent Hunyuan, **Hunyuan3D 2.1** official repository and report: shape plus PBR texturing; repository reports approximately 10 GB VRAM for shape, 21 GB for texture, and 29 GB combined. <https://github.com/tencent-hunyuan/hunyuan3d-2.1> and <https://arxiv.org/abs/2506.15442>
- Microsoft, **TRELLIS.2** official repository/project: high-resolution image-to-3D with PBR materials; README requires at least 24 GB GPU memory and notes support for topology that may be non-manifold/open and therefore needs print cleanup. <https://github.com/microsoft/TRELLIS.2> and <https://microsoft.github.io/TRELLIS.2/>

Do not infer that “state of the art” or high render fidelity means dimensionally accurate or printable. Verify each license against the intended commercial/non-commercial use.

## Blender and mesh processing

- Blender Manual, **Remeshing**: topology regeneration and scan/print cleanup context. <https://docs.blender.org/manual/en/latest/modeling/meshes/retopology.html>
- Blender Manual, **Voxel Remesh**: voxel-size controls and color-attribute reprojection behavior. <https://docs.blender.org/manual/en/latest/sculpt_paint/sculpting/tool_settings/remesh.html>
- Blender Manual, **Decimate Modifier**: face-count reduction with limited shape change. <https://docs.blender.org/manual/en/latest/modeling/modifiers/generate/decimate.html>
- Blender Manual, **Clean Up**: loose geometry, degenerates, and related mesh operations. <https://docs.blender.org/manual/en/latest/modeling/meshes/editing/mesh/cleanup.html>
- Blender Manual, **Cameras**: perspective/orthographic camera behavior and lens shift. <https://docs.blender.org/manual/en/latest/render/cameras.html>
- Blender Manual 4.0, **3D Print Toolbox**: mesh analysis for slicing problems; current releases may distribute it as an extension. <https://docs.blender.org/manual/en/4.0/addons/mesh/3d_print_toolbox.html>
- MeshLab official site: mesh cleaning, processing, simplification, and texture-preserving decimation overview. <https://www.meshlab.net/>
- trimesh official documentation: watertight mesh analysis and repair API used by the bundled audit script. <https://trimesh.org/> and <https://trimesh.org/trimesh.repair.html>

## OpenSCAD, CadQuery, and FreeCAD

- OpenSCAD official cheat sheet: `surface()`, SVG/DXF import, extrusion/revolution, `$fa`, `$fs`, `$fn`, Boolean operations, and mesh formats. <https://openscad.org/cheatsheet/>
- OpenSCAD user manual, **Importing Geometry**: image height maps through `surface()` and geometry import. <https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Importing_Geometry>
- CadQuery official documentation, **Importing and Exporting Files**: DXF profile import, STEP units, STL/AMF/3MF tessellation tolerances, and current color/material limitations. <https://cadquery.readthedocs.io/en/latest/importexport.html>
- CadQuery official examples: loft, sweep, shell, and parametric modeling patterns. <https://cadquery.readthedocs.io/en/latest/examples.html>
- FreeCAD documentation repository: current project-authored manuals/tutorial index, including 3D-print preparation. <https://github.com/FreeCAD/FreeCAD-documentation>
- FreeCAD wiki, **Image CreateImagePlane**, **Image Scaling**, **Mesh**, and **Preparing models for 3D printing**; UI availability varies by release. <https://wiki.freecad.org/Image_CreateImagePlane> <https://wiki.freecad.org/Image_Scaling> <https://wiki.freecad.org/Mesh_Workbench> <https://wiki.freecad.org/Manual:Preparing_models_for_3D_printing>

## Print resolution and file formats

- Prusa Knowledge Base, **Layers and perimeters**: official FDM relationship between nozzle and maximum layer height; use as one process constraint, not a full XY accuracy model. <https://help.prusa3d.com/article/layers-and-perimeters_1748>
- Prusa Knowledge Base, **Modeling with 3D printing in mind**: orientation, overhang, splitting, and FDM design considerations. <https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135>
- Formlabs, **Design specifications for 3D models (Form 4 generation)**: printer/material/test-specific feature and dimensional guidance; illustrates why limits must be tied to a process. <https://formlabs.com/support/Design-specifications-for-3D-models-Form-4-generation/>
- Formlabs, **What Does Resolution Mean in 3D Printing?**: distinguishes XY minimum feature from Z layer resolution and overall accuracy. <https://formlabs.com/blog/3d-printer-resolution-meaning/>
- 3MF Consortium specification suite: core plus materials/properties, displacement, production, and other extensions. <https://3mf.io/spec/>
- 3MF Core Specification repository: official format definition and resource model. <https://github.com/3MFConsortium/spec_core/blob/master/3MF%20Core%20Specification.md>

## How to use the evidence

- Cite a source for tool capability, version-dependent behavior, or published hardware requirement.
- Treat manufacturer minimum features as printer/material/orientation-specific test results, not universal process physics.
- Treat AI project quality claims as project claims; validate on the user's own images and print constraints.
- Prefer the formulas and measured coupons in this skill for project planning, then revise them with actual test data.
