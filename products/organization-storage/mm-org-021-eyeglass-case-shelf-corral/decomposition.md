# Decomposition

| Component | Source of truth | Role | Manufacturing output |
|---|---|---|---|
| slim-five corral | JSON lane list + analytic CadQuery | five equal slim-case lanes | STEP + STL |
| mixed-four corral | JSON lane list + analytic CadQuery | graduated rigid/soft-case lanes | STEP + STL |
| width gauge | JSON notch list + analytic CadQuery | low-cost 36/42/50/58 mm selection | STEP + STL |
| build package | audited STL meshes | arranged reference plate | 3MF |

Shared datums are X=left outside wall, Y=front face, Z=build plate. Lane widths are clear internal distances. The rear-falling floor is owned by `floor_back_lean_deg`; label fields are geometry-only recesses. No purchased or external geometry is used.
