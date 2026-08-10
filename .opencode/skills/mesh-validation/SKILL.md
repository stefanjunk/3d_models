---
name: mesh-validation
description: Use when inspecting or validating exported STL, OBJ, PLY, 3MF, or GLB triangle meshes for topology, bounds, bodies, winding, volume, degenerate faces, bed fit, and memory planning without silently repairing geometry.
---

# Mesh Validation

This skill owns generic triangle-mesh evidence. Domain skills add their own
checks for protected surfaces, relief mapping, demolding, interfaces, and
printability, but must not redefine baseline topology vocabulary.

Load without Trimesh processing by default. Baseline topology is calculated on
an in-memory copy with coincident vertices merged and unreferenced vertices
removed because facet-based STL files otherwise appear disconnected. The
report records raw counts and this analysis normalization; no source file is
changed. Use `--process` only for an explicit derived repair candidate and
retain the original report.

```bash
python3 scripts/validate_mesh.py model.stl \
  --require-watertight --require-volume --require-single-body \
  --report reports/mesh.json

python3 scripts/estimate_memory.py --mesh model.stl --voxel-mm 0.4
```

Watertightness is not proof of printability, wall thickness, strength, fit,
protected-surface preservation, or demoldability. Repair must write a new file
and preserve before/after evidence.
