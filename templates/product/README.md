# PRODUCT-ID — Product name

Copy this complete template directory to
`products/<family>/<product-id-and-slug>/`. Do not link a new product to files
inside this template or to a sibling product.

Recommended roles:

- `preflight/`: mandatory pre-design input and current validated preflight result;
- `source/`: editable CAD, mesh, and generator source;
- `assets/`: reference images, measurements, textures, branding, and disclosed
  third-party inputs;
- `vendor/`: pinned code or geometry dependencies required for rebuilding;
- `profiles/`: exact slicer and material profiles;
- `exports/`: deliberate master, manufacturing, and coupon artifacts;
- `validation/`: machine-readable checks and approval ledgers;
- `tests/`: automated and physical plans/results;
- `build/`: reproducible temporary output;
- `releases/`: immutable approved packages.

Keep `README.md`, `design-spec.yaml`, `decision-log.md`, `bom.yaml`, and
`validation-project.json` at the product root when they apply. Complete
`preflight/preflight-result.json` with the `3d-design-preflight` skill before
concept, CAD, source, or manufacturing export work.
