# Decision log — MM-PUZ-002 Mystery Puzzle Box

| ID | Decision | Choice | Rationale / trade-off |
|---|---|---|---|
| D1 | Portfolio audit | Treat the project as `NO model` despite `P1` | The source path contained only concept/spec/test files; there was no CAD, STEP, STL, 3MF, OBJ, GLB or Blender model. |
| D2 | Version | Create `1.2.0 / 1.2.0-draft.1`; preserve v1.1 in `history/` | The mechanism architecture and branding identity change, so the prior approved spec is not overwritten. |
| D3 | Mechanism | Three independent direct latch sliders | Retains “three buttons, any order, all required” while making each interface independently modelable and coupon-testable. It trades the theatrical central ratchet for reliability and serviceability. |
| D4 | Return element | Three replaceable printed PETG leaf springs | Matches the no-metal/no-magnet concept and keeps failure replaceable. Force, strain, fatigue and creep remain physical blockers. |
| D5 | Texture | 40 deterministic vector/procedural question marks, 0.6 mm macro relief | Compact editable definition; avoids a dense image heightmap and keeps interfaces/bed face protected. Appearance and tactility require a coupon. |
| D6 | Tool route | CadQuery B-Rep with STEP/STL/3MF | Exact lid, guide and travel clearances dominate; relief remains compact enough for direct CAD. |
| D7 | Material/process | PLA body/lid, PETG sliders/leaves, 0.4 mm nozzle, 0.2 mm layer | The body benefits from stiffness/detail; PETG is a more credible first flexure candidate. Exact products and profiles remain unresolved. |
| D8 | Release status | DRAFT digital candidate only | Mesh/interface evidence cannot prove spring return, latch reliability, tactile camouflage or hidden seam. |

