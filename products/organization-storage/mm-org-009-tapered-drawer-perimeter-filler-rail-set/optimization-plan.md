# Efficiency decision plan

Protected functions are the two clearance datums, planar bed contact, top skin, removal scallops, rib continuity and gauge width law.

| Candidate | Geometry | Decision evidence |
|---|---|---|
| A baseline | Solid full-height wedge rail. | Exact CAD volume only; establishes the upper material envelope. |
| B selected | Open underside, perimeter walls, 2.0 mm roof and 1.8 mm cross-ribs at a maximum 11.5 mm pitch. | Must be one valid solid, watertight after tessellation, within the envelope and materially below A volume. |
| C process-only | Candidate B with an exact known slicer/profile. | Deferred because printer, filament and slicer profile are unknown. |

No mesh decimation is planned. The analytic faces and two small scallop cylinders produce a modest manufacturing mesh; downstream loss would add risk at protected fit surfaces without a measured benefit. The native STEP remains the master and STL is a deterministic tessellation at the declared physical tolerance.
