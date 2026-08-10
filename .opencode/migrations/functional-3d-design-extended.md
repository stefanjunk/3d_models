# Functional 3D Design Extended Migration

The incoming `functional-3d-design-extended` package declared the already-used
skill name `functional-3d-design` and defined a conflicting YAML design
contract. It was retired as a loadable skill.

Retained in the canonical `functional-3d-design` skill:

- evidence-backed local parts-library workflow and scripts;
- simulation/model-fidelity guidance;
- local qualification status vocabulary.

Delegated to existing authoritative skills:

- materials and nozzle classes: `fdm-process-envelope`;
- fits: `fdm-joints-and-fits`;
- snap calculations: `snap-fit-design`;
- gears and transmission: `power-transmission-design`;
- organic mesh operations: `organic-mesh-functionalization`;
- generic mesh checks: `mesh-validation`.

Not retained:

- the conflicting YAML design contract and validator;
- duplicate material, fit, snap, gear, mesh, and routing implementations;
- its parallel subagent architecture and examples tied to the retired schema.

The original package archive remains an immutable provenance artifact at
`.opencode/opencode-functional-3d-design.zip`; it is not a runtime source of
truth. Its SHA-256 is
`fbf59c139f7c0700e0ea95b14c348994077ccda3d9be59261c8b7ba5e0853471`.

The other incoming package archives remain immutable as well:

| Package | SHA-256 |
|---|---|
| `opencode-organic-mesh-functionalization.zip` | `7e0f0c94818b4a7bdd05dfcfef37b288c6a030014a2ee8572a93725026330f31` |
| `opencode-heightmap-relief-skill.zip` | `ce3362cb9d15f6c0f531373e34f2d893fec86c616a1930f012ef839cf2bb307b` |
| `casting-negative-molds-opencode-skill.zip` | `1fd2aff8c9a58f90c68c8a60b4da3e6debe83f8fc67d2d97805994bdad85910d` |
