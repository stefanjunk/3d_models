# Anycubic Slicer Next baseline import check

Date: 2026-08-27

Tool: `/usr/bin/AnycubicSlicerNext`, version `1.3.9.4` as reported in the CLI usage header.

Artifact: `exports/manufacturing/DRAFT-SHOWER-DRAIN-HAIRTRAP-3.0.0-draft.1-segment-on-end.stl`

Command:

```text
/usr/bin/AnycubicSlicerNext --info exports/manufacturing/DRAFT-SHOWER-DRAIN-HAIRTRAP-3.0.0-draft.1-segment-on-end.stl
```

Result: command exit code 0.

- Envelope: 21.000 × 65.000 × 52.500 mm
- Minimum: 0.000 × 0.000 × 0.000 mm
- Facets: 25,780
- Parts: 1
- Manifold: yes
- Reported volume: 16,256.623047 mm³

The CLI also emitted `calc_exclude_triangles:Unable to create exclude triangles`. The model-info operation still completed and reported the values above, but this warning is retained and not converted into a slicer PASS.

Decision: baseline STL import/info is available in the user-selected slicer. This is not a revision 3.1 slice, G-code result, support decision, first-layer preview, exact machine/filament/process profile, or physical qualification. Those checks remain blocked until concept approval and revised CAD generation.
