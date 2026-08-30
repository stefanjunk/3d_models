# Optimization gate — 0.1.0-parametric.1

Status: **BLOCKED / no geometry optimization applied**

The current CadQuery solids are the unoptimized DRAFT baseline. Exact print
time and filament use cannot be compared because the required complete
Anycubic machine, process and filament JSON profiles do not yet exist for this
product. CAD volume alone is not accepted as a substitute for a slicer
baseline.

Protected invariants are the common axle datum, motor/bracket seats, metal
fastener ligaments, battery restraint and ±12 mm trim corridor, rigid IMU datum,
wheel/cable/tool keep-outs, landing load paths and the unresolved center-of-mass
criterion.

Candidates retained for a later controlled A/B comparison are:

1. Process-only changes with unchanged geometry.
2. Larger windows and local ribs in low-load deck regions.
3. A combined process and geometry candidate.

None was generated or selected. DRAFT STL meshes retain the direct CadQuery
tessellation; lossy mesh simplification is not applied. Optimization may resume
only after the mass criterion is clarified, exact purchased interfaces are
frozen and a reproducible exact-slicer baseline exists.
