# MM-ART-010 — Permanent One-off City Map Wall Relief

Status: **revision 0.5.0 `digital-candidate-r7` is the current DRAFT geometry authority. Concept v05 is human-approved, the parameterized raised site marker is integrated into Sky Blue/tool 4 at Sterkrader Straße 24, and all four native Anycubic project files contain four non-empty tool bodies and slice successfully. Oak/Mint Green/Midnight/Sky Blue remains a non-geometric product colorway; other palette presets only change filament/tool loading. Only 600 × 400 mm and the frozen Berlin extent are currently production-supported. No human print candidate, physical qualification, watermark or commercial release approval exists**.

The planned pilot is a unique Berlin street-map wall relief with two parameterized appearance modes. `boundary_crop` removes every printed body outside the Berlin administrative boundary and produces an irregular silhouette inside a maximum 600 × 400 mm envelope. `context_outline` keeps the 600 × 400 mm rectangle, maps surrounding context and marks Berlin with a Sky Blue boundary relief. Both use Oak as the base, Mint Green as the middle relief, Midnight for streets and Sky Blue for boundary/accents. They retain two permanent main prints, glue-free concealed connectors, isolated rear standoffs, an 18 mm halo-light cavity and protected light-through openings without a rear grid. Lighting and electrical hardware remain customer add-ons and are not part of the product.

The authoritative requirements are in `design-spec.yaml`; parameter axes and configured examples are in `product-variants.json`. Concept v05 is recorded in `concept-review-0.5.0.md`. The approved mode-aware decomposition remains `decomposition-review-0.4.0.md` and `plan/hybrid-design-plan-v0.4.0.json`. The current DRAFT evidence is summarized in `validation/v0.5.0/berlin/digital-candidate-r7/digital-candidate-summary.md`.

Native Anycubic project files:

- `boundary_crop`: `exports/v0.5.0/berlin/digital-candidate-r7/boundary-crop/berlin-boundary-crop-left-oak-mint-midnight-sky-anycubic.3mf` and `berlin-boundary-crop-right-oak-mint-midnight-sky-anycubic.3mf`
- `context_outline`: `exports/v0.5.0/berlin/digital-candidate-r7/context-outline/berlin-context-outline-left-oak-mint-midnight-sky-anycubic.3mf` and `berlin-context-outline-right-oak-mint-midnight-sky-anycubic.3mf`

The generic standard-only 3MF parser does not follow Anycubic production-extension `p:path` references. Product-local vendor-aware geometry reports resolve those paths and prove four non-empty bodies in every file; native Anycubic Slicer Next then produces non-empty G-code from all four projects. Physical marker readability, connector fit, opacity, final ACE mapping/purge, wall proof, watermark and release remain open.

Historical concept: `concepts/modular-relief-collection-concept-v01.png`; controlled notes: `concept-review.md`. It documents the rejected six-tile rear-grid direction and is not current design authority.

Historical decomposition: `decomposition-review.md` and `plan/hybrid-design-plan.json`. Both are superseded by revision 0.3.0 and cannot authorize CAD.
