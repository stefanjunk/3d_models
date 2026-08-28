# Decomposition

| Component | Geometry authority | Function | Output |
|---|---|---|---|
| compact-six rack | JSON envelope preset + analytic CadQuery solids | six narrow measured slots | STEP + STL |
| extended-five rack | JSON envelope preset + analytic CadQuery solids | five deeper/wider measured slots | STEP + STL |
| clearance coupon | JSON nominal thickness + clearance series | test one cassette corner before full print | STEP + STL |
| virtual set | placements only | assembly/documentation view | STEP |
| print package | the three STL meshes | single-plate slicer handoff | 3MF |

Protected interfaces are cartridge cavity width/depth, base datum, rear-rest angle, label recess skin, connector tab/socket and coupon clearances. No purchased components, external meshes, vectors or fonts enter the geometry.
