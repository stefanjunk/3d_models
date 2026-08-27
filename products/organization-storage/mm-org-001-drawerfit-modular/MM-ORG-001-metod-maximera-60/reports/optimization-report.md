# DRAFT optimization report — 0.1.0-draft.1

The 2.6 mm plain full floor is the exact active baseline. Manifold3D was rerun with only the floor thickness changed; envelope, nine-module grid, layout, walls, connector count and comb were held constant.

| Variant | Solid volume | PETG solid-volume equivalent | Change |
|---|---:|---:|---:|
| 2.6 mm baseline | 1,398,020 mm³ | 1,775.5 g | baseline |
| 2.2 mm study | 1,304,079 mm³ | 1,656.2 g | −6.72%, −119.3 g equivalent |
| 2.0 mm study | 1,257,109 mm³ | 1,596.5 g | −10.08%, −179.0 g equivalent |

These masses are full-solid volume equivalents, not slicer filament predictions. Exact time, filament, cost and support remain `NOT_RUN` because no supported slicer executable or fixed common-220 PETG profile is available.

Neither thin-floor study is promoted: lowering the full floor also thins every connector and wall root before connector/handling/load evidence exists. The active DRAFT instead applies the lower-risk connector simplification: twelve mating locations, one per necessary seam segment, versus the inherited double-location comparator of 24. That is a 50% feature-count reduction while retaining connection on every seam segment. Rotational restraint and rocking still require the representative seam test.

No post-tessellation mesh simplification was applied. Manufacturing meshes are already only 420–1,156 triangles per module; simplification has negligible file/time value and would add unnecessary connector/profile deviation.
