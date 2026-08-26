# Sources and further reading

Checked 2026-08-20. Tool behavior and slicer interoperability change; verify against installed versions.

## 3MF

- 3MF Consortium specification suite and ISO/IEC 25422:2025: https://3mf.io/spec/
- 3MF Core specification: https://github.com/3MFConsortium/spec_core/blob/master/3MF%20Core%20Specification.md
- Materials and Properties Extension: https://github.com/3MFConsortium/spec_materials
- Lib3MF: https://github.com/3MFConsortium/lib3mf

Key points used by this skill:

- 3MF supports defined units, components, materials, color, and extensions;
- component relative positions are normative;
- base-material names convey design intent;
- Core `displaycolor` is for rendering and does not itself guarantee physical printer-material mapping;
- the Materials extension is the standards route for richer full-color/multi-material properties.

## Slicers and texture conversion

- Bambu Studio releases, Texture-to-Color Painting in 2.7: https://github.com/bambulab/BambuStudio/releases
- Bambu Studio repository: https://github.com/bambulab/BambuStudio
- OrcaSlicer wiki: https://github.com/OrcaSlicer/OrcaSlicer/wiki
- Anycubic Slicer Next overview: https://wiki.anycubic.com/en/software-and-app/new-page-anycubic-slicer-beta%28orca-version%29
- Anycubic Slicer Next Color Painting: https://wiki.anycubic.com/en/software-and-app/new-page-anycubic-slicer-beta%28orca-version%29/color-painting
- Anycubic multicolor guide: https://wiki.anycubic.com/en/software-and-app/anycubicslicer/multi-color-printing

## Multi-material design and purge

- Prusa, modeling with multi-material printing in mind: https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135
- Prusa, importing multi-material models: https://help.prusa3d.com/article/importing-multi-material-model_121191
- Prusa, assigning tools/colors: https://help.prusa3d.com/article/assigning-tools-colors-extruders_124811
- Prusa, multi-material painting: https://help.prusa3d.com/article/multi-material-painting_262620
- Prusa, wipe tower: https://help.prusa3d.com/article/wipe-tower_125010
- Prusa, purging volumes: https://help.prusa3d.com/article/purging-volumes-mmu_125097
- Prusa, color change/material-family warning: https://help.prusa3d.com/article/color-change_1687
- Prusa, combining materials on multi-tool XL: https://help.prusa3d.com/article/combining-materials-xl_498103

## Blender and color science

- Blender OBJ import: https://docs.blender.org/manual/en/latest/files/import_export/obj.html
- Blender glTF import: https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html
- Blender Separate by Material: https://docs.blender.org/manual/en/latest/modeling/meshes/editing/mesh/separate.html
- scikit-image color API (`rgb2lab`, `deltaE_ciede2000`): https://scikit-image.org/docs/stable/api/skimage.color.html

## Interpretation notes

Desktop slicers often put private project data inside a 3MF package. The existence of a `.3mf` file does not imply every application will interpret paint data, purge settings, or printer profiles identically. This skill therefore prefers explicit solids for portable design intent and treats cross-slicer painted-project transfer as a manual acceptance gate.
