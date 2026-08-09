# Library Allowlist

| Library | Code license | Production status | Notes |
|---|---|---|---|
| CadQuery | Apache-2.0 | approved | Primary B-Rep implementation stack |
| BOSL2 | BSD-2-Clause | approved at v2.0.747 / fbcdfdd | OpenSCAD 2021.01 smoke passed |
| cq_warehouse | Apache-2.0 | approved at 0.8.0 / daa4650 | Python 3.13 + CadQuery 2.8 smoke passed |
| cq_gears | Apache-2.0 | experimental | Project describes itself as alpha/WIP |
| build123d | Apache-2.0 | deferred | Avoid second Python CAD stack without measured benefit |
| bd_warehouse | Apache-2.0 | deferred | Same reason as build123d |

NopSCADlib and FreeCAD Gears are excluded from the proprietary commercial
production path because this project does not accept copyleft dependencies.

`step.parts` is not globally allowlisted. Its repository license does not
relicense every STEP asset. Approve only a file whose individual origin and
license are allowlisted and fully recorded.
