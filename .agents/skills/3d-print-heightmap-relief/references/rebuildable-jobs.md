# Rebuildable relief jobs and source exchange

## Stable job structure

```text
job/
├── relief-job.json
├── source/
│   ├── source-spec.json
│   ├── generation-prompt.txt
│   ├── source-master.png
│   └── source-master.png.source.json
└── build/
    ├── current-heightmap.png
    ├── current-heightmap.png.json
    ├── current-heightmap.preview.png
    ├── current-heightmap.build.json
    ├── reference-master-mesh.stl
    ├── manufacturing-mesh.stl
    ├── relief-mesh-budget.json
    ├── relief-mesh-comparison.json
    └── slicer-report.json / 3MF
```

The CAD/mesh build references only the stable `build/current-heightmap.png` path plus its metadata.

## No accumulated resizing

Every rebuild starts from `source/source-master.png`. Never use a previous `build/current-heightmap.png` as the next input. This guarantees a single target resampling and preserves detail/aspect provenance.

## Initialize

```bash
python scripts/init_relief_job.py jobs/unicorn-box \
  --name unicorn-box \
  --target-size-mm 75x55 \
  --source-size-mm 75x55 \
  --authoring-ppi 450 \
  --description "unicorn bas-relief image" \
  --image-class motif \
  --surface-type cylinder \
  --placement-mode front_patch \
  --process fdm --nozzle-mm 0.4 --layer-height-mm 0.12 \
  --axis-mode xy-z --fit contain \
  --mode engrave --depth-mm 0.6 \
  --triangle-target 1000000 --triangle-stop 5000000 \
  --memory-budget-gib 8 --max-mesh-mib 100 \
  --max-slicer-seconds 120
```

The generated job defaults to `aspect_policy=preserve`.

## Register and rebuild

```bash
python scripts/rebuild_relief_job.py jobs/unicorn-box/relief-job.json \
  --source generated-unicorn.png \
  --register-source --source-kind ai-generated
```

The register step contains/crops a mismatched raw generator raster rather than anisotropically stretching it.

## Replace later

```bash
python scripts/rebuild_relief_job.py jobs/unicorn-box/relief-job.json \
  --source replacement-unicorn.png \
  --register-source --source-kind ai-generated \
  --run-geometry
```

Rebuild sequence:
1. raw replacement → canonical source master;
2. source master → target geometry heightmap using physical-coordinate fit;
3. physical aspect validation;
4. build manifest with new source/hash;
5. optional geometry command writing separate reference/manufacturing artifacts;
6. independent mesh-quality and exact-slicer reports.

## Geometry command contract

`geometry.command` is a JSON array, never a shell string. It may use:
- `{heightmap}`
- `{heightmap_metadata}`
- `{build_manifest}`
- `{source}`
- `{source_manifest}`
- `{job}` / `{job_dir}`
- `{output_model}`
- `{reference_mesh}` / `{manufacturing_mesh}`
- `{mesh_comparison_report}` / `{mesh_budget_report}` / `{slicer_report}`
- `{mode}`
- `{depth_mm}`

The geometry script must interpret target physical width/height from metadata or explicit job fields, not derive scale from the PNG's raw pixel aspect.
