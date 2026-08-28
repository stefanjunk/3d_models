# Print guide

1. Confirm both inserts are ordinary paper or card stock between `0.25` and `1.2 mm` thick. Keep important content at least `12 mm` above the rear photo edge and `10 mm` above the front card edge so the deepest expected insertion cannot hide it.
2. Print `exports/3mf/DRAFT-MM-ORG-038-fit-and-mark-coupons-0.1.0-draft.1.3mf` first. It contains the exact `10 mm` / `8 mm` tapered-slot gauge and the separate R2 Full identity coupon.
3. Test the actual rear photo in the `10 mm` groove and the intended milestone card in the `8 mm` groove. Each must enter without forced creasing, remain upright during gentle desk handling, release without torn coating or visible edge marking, and survive 100 normal insert/remove cycles. Reject the full print if either stock is loose, damaged, or conceals important content.
4. Check the Full identity coupon for complete, readable text and clean recesses. This is a physical process gate.
5. Open `exports/3mf/DRAFT-MM-ORG-038-momentpair-base-0.1.0-draft.1.3mf` or preview the preserved exact base G-code. Verify first-layer placement, layer paths, seam, tool assignment, and that generated support remains disabled. The validated orientation is base-down.
6. Print the base only after the gauge passes. After cooling, insert both final cards and verify that the loaded display does not tip or slide during ordinary desk handling and that the card edges do not contact the desk.
7. Inspect the underside identity, recessed `YOUR MOMENT` front placeholder, groove lips, connector bridges, and all desk-contact edges. Stop use if any edge is sharp, cracked, or delaminated. Keep the PLA product below `40 °C` and out of child-use contexts.

Exact PLA planning evidence:

- Fit and mark coupons: `2,180 s` (`36 min 20 s`), approximately `15.3 g`, G-code SHA-256 `170ff678dfe3cff7990aa1e65b2589cab7e504a567e0856aef5007799c4a2911`.
- MomentPair base: `5,755 s` (`1 h 35 min 55 s`), approximately `42.0 g`, G-code SHA-256 `e63a73b34364716bc1dc23df4af02f1a192789ab6501b720ff4d563a5c251748`.

Supplied G-code is local validation evidence for the named Anycubic Kobra 3 Max, process, and PLA profiles. It is not authorization to upload or start a printer.
