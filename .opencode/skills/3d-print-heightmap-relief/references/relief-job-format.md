# Persistent relief-job format v2.4

## Minimal FDM example

```json
{
  "schema": "heightmap-relief-job-v2.4",
  "source": {
    "spec": "source/source-spec.json",
    "master": "source/source-master.png",
    "manifest": "source/source-master.png.source.json"
  },
  "target": {
    "width_mm": 80,
    "height_mm": 40,
    "surface_type": "cylinder",
    "placement_mode": "front_patch",
    "axis_mode": "xy-z",
    "pitch_x_mm": 0.20,
    "pitch_y_mm": 0.12,
    "dpi_x": 127.0,
    "dpi_y": 211.67
  },
  "image": {
    "class": "person",
    "repeating": false,
    "fit_mode": "contain",
    "aspect_policy": "preserve",
    "allow_aspect_distortion": false,
    "aspect_tolerance_pct": 0.75,
    "bit_depth": 16
  },
  "printer": {
    "process": "fdm",
    "nozzle_mm": 0.6,
    "layer_height_mm": 0.3
  },
  "relief": {
    "mode": "emboss",
    "depth_mm": 0.32,
    "wall_thickness_mm": 2.4
  },
  "complexity_budget": {
    "triangle_target": 1000000,
    "triangle_stop": 5000000,
    "memory_budget_gib": 8.0,
    "working_bytes_per_triangle": 1024.0,
    "max_mesh_mib": 100.0,
    "max_slicer_seconds": 120.0
  },
  "mesh_acceptance": {
    "max_abs_volume_delta_pct": 0.1,
    "min_relief_correlation": 0.98,
    "max_relief_contrast_loss_pct": 5.0,
    "max_rms_nozzle_fraction": 0.05
  },
  "geometry": {
    "reference_mesh_path": "build/reference-master-mesh.stl",
    "manufacturing_mesh_path": "build/manufacturing-mesh.stl",
    "comparison_report_path": "build/relief-mesh-comparison.json",
    "budget_report_path": "build/relief-mesh-budget.json",
    "slicer_report_path": "build/slicer-report.json",
    "output_path": "build/manufacturing-mesh.stl",
    "cwd": ".",
    "command": []
  }
}
```

## Aspect fields are mandatory design intent

Store physical target size and pitch separately. Never replace them with only pixel dimensions or only DPI.

Default `allow_aspect_distortion` to false. Set it true only after explicit approval of distortion or for intentional anisotropic texture scaling.

## Resource budgets are mandatory design intent

Record before geometry generation:

- triangle target and hard stop;
- peak-memory budget in GiB and the calibrated planning coefficient used to estimate it;
- maximum manufacturing-mesh size in MiB;
- maximum total exact-slicer import/slice time in seconds.

Treat a planning estimate as a forecast. Record actual peak memory, file bytes, triangle count, slicer/version/profile, and elapsed slicer time before release. A mesh below the triangle target may still fail RAM or slicer limits.

## Mesh artifacts are separate

`reference_mesh_path` is the unsimplified comparison/master mesh. `manufacturing_mesh_path` is the selected optimized export. Never point both fields at the same mutable path and never overwrite the only reference artifact. Store geometry comparison, resource budget, and slicer reports separately.

## Acceptance starting values

For ordinary FDM relief, begin with:

- absolute volume change `< 0.1%`;
- relief-height correlation `>= 0.98` inside the registered relief mask;
- robust contrast loss `< 5%`, normally using the same `P95-P5` height span;
- RMS surface error `<= 0.05 * nozzle_diameter`.

These are starting values. Tighten them for shallow texture, faces, text, seams, fits, seals, or stricter approved appearance criteria. Record any project-specific override.

## Build metadata

`prepare_heightmap.py` writes source physical aspect, target physical/raster aspect, physical pixel aspect, placed/reconstructed aspect, aspect error, preview path, and warnings. The geometry stage must stop when `aspect_validation.passed=false` unless an explicit distortion override exists.

The v2.4 build manifest also carries the resource budgets, acceptance limits, and separate artifact paths so a later rebuild cannot silently collapse the reference and manufacturing stages.
