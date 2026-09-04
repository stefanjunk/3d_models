# digital-candidate-r1 — rejected, retained as evidence

Build status `FAIL`. Retained deliberately; do not reuse for production.

Cause: `boundary_crop` right half reached an aperture fraction of 0.12966 against
the inherited 0.12 per-half open-area guard. Every other check passed:

- `context_outline` status `PASS`
- water gate `PASS` in both modes — Tegeler See 95.4 % / 93.7 % of its mapped
  area open, Havel corridor 89.6 % / 98.1 %
- all sixteen tool bodies and all four composites watertight, positive volume,
  one connected component, zero boundary, nonmanifold, degenerate and duplicate
  faces; pairwise tool overlap at numerical zero
- marker anchor and seam clearance as designed (41.94 mm / 23.37 mm)

The guard, not the geometry, was the blocker. See
`source/v0.5.4/berlin/hydrography-parameters.json`
→ `water.maximum_open_area_fraction_change_reason`. The retry is
`digital-candidate-r2`.

## Why the exports and composite-raw of r1 are not retained

All twenty exported meshes of r1 are byte-identical to `digital-candidate-r2`;
the per-file SHA-256 comparison is kept in `r1-vs-r2-export-equivalence.json`.
Nothing in the geometry pipeline reads
`water.maximum_open_area_fraction_per_half` — it is only a check — so r2 is the
same build with the guard raised. The r1 mesh and composite binaries were
therefore removed rather than stored twice; the machine-readable failure
evidence (`build-report.json`, both hydrography accountings,
`exported-water-verification.json`, the previews and the hash comparison) is
complete and retained.
