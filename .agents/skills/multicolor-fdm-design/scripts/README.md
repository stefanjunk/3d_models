# Helper scripts

All commands are local, deterministic helpers. They do not upload assets and do not start a print.

```text
validate_job.py               validate multicolor-job.yaml
inspect_textured_asset.py     mesh/UV/material/texture report
quantize_texture.py           fixed real-filament palette mapping
texture_to_voxel_parts.py     texture to explicit color volumes
assemble_multicolor_3mf.py    aligned meshes to standard 3MF assembly
validate_multicolor_3mf.py    structural and mesh-reference checks
estimate_color_changes.py     Z-layer occupancy and purge estimate
render_parts_preview.py       simple colored PNG preview
build_examples.py             build all three worked examples
validate_skill.py             package structure and compile checks
```

The voxel converter is a fallback for portability and automation. It is not a substitute for a clean parametric partition when source CAD exists.
