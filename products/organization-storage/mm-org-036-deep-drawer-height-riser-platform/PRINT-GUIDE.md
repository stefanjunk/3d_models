# Print guide

1. Measure drawer internal width, depth, usable height under any rail or handle, and the complete upper tray footprint.
2. Confirm the closed drawer has at least the selected lift plus the loaded upper tray height and 5 mm top clearance.
3. Print the coupon plate first. It contains the corner-post and rib-support A/B specimens plus the separate Full identity-mark coupon. Mark each structural coupon and follow `tests/physical-test-plan.md`; the 30-day creep comparison and mark legibility cannot be inferred from CAD.
4. Preview the exact G-code for layers, support state, seam, first-layer placement, and tool assignment. Supports remain disabled.
5. Print the full platform top-face-down as supplied. Flip it only after cooling.
6. Use only with a flat-bottomed tray at least 80 x 70 mm. Keep the total distributed tray-and-content mass at or below 2 kg until the physical program qualifies a higher value.
7. Do not use as a step, seat, shelf, food-contact surface, child product, safety support, or in a drawer that can exceed 40 °C.

Printable handoff:

- Full platform: `exports/3mf/DRAFT-MM-ORG-036-liftdeck-full-0.1.0-draft.2.3mf`
- Structural plus Full-mark coupon plate: `exports/3mf/DRAFT-MM-ORG-036-creep-coupons-0.1.0-draft.2.3mf`
- Exact full-platform G-code evidence: 9,357 s, approximately 65.3 g PLA, SHA-256 `75ee3648ed11f48c6e5941b160ab2e83aeeb2cff96c2cf9581c8c2e18332b057`
- Exact coupon-plate G-code evidence: 6,495 s, approximately 48.1 g PLA, SHA-256 `96e1984fe3bee6134fb880f10dcd69d3e67a26a2f4b5c2539be008d58a1d442c`

Supplied G-code is local validation evidence, not authorization to upload or start a printer.
