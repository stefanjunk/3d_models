# Research validation — SKU-197

Checked 2026-08-28. Result: **PASS for a differentiated digital prototype**.

## Demand and competition signals

- Etsy lists a printed six-slot organizer for measured cartridges up to 89 x 23 mm at USD 23.99+, with separate 12/18/24 mm variants. The broader Etsy result reports 381 reviews for the 12 mm listing. This validates a paid retrieval-and-visibility job while showing that fixed single-size products are crowded: <https://www.etsy.com/listing/1739617302/18mm-label-tape-organizer-for-brother-p>
- A long-running parametric OpenSCAD storage cabinet offers 9- and 13-slot variants and was revised in December 2025 because newer printers changed the needed fit. That is direct evidence that clearance must be explicit and printable source matters: <https://3dfinder.io/model/printables/44317-brother-p-touch-tz-tze-label-tape-holder>
- A two-slot Gridfinity holder has 123 downloads, 21 boosts and seven comments; one user explicitly asks for other 6/9/12/18/24 sizes. Its author also calls out wrapper clearance, confirming that the stored envelope is workflow-dependent: <https://makerworld.com/en/models/117336-gridfinity-vetical-p-touch-tze-tape-holder>
- A purpose-built carrying case priced at USD 39.77 stores 15–39 cartridges depending on size, demonstrating a professional inventory segment but a transport/protection job distinct from this open desk/drawer rack: <https://www.ptouchdirect.com/ptouch/tapecase.html>
- DYMO states that its D1 family spans multiple cassette/tape sizes and more than 40 color combinations. Mixed width and color visibility is therefore a real consumables-management problem, but this project makes no DYMO fit claim: <https://www.dymo.de/labelmanager.html>
- Brother describes its cassette family as available in varied widths, colors and materials and positions it for office, workplace and home labeling. This supports per-slot inventory fields without licensing cartridge geometry: <https://store.brother.ie/supplies/p-touch/tapes/tze/tze641>

## Qualified problem signals

1. Fixed racks are split into separate width variants.
2. Users request additional formats after downloading a fixed holder.
3. Wrapper-on storage changes the required clearance.
4. Fit was revised when printer capability changed.
5. Professional users stock many cartridges and need inventory visibility.
6. Color/material variants multiply selection errors even within one nominal family.
7. Existing products mostly target one ecosystem or Gridfinity rather than measured mixed envelopes.

## Selected opportunity

Build a brand-neutral generator from five measured inputs: envelope depth, thickness, height, slot count and storage clearance. Supply two transparent example envelopes, an interface coupon, common modular joints and adhesive label/status fields. Do not copy cartridge profiles, logos or fit claims. Physical fit with empty cartridges remains the user's deferred validation step.

## Gate decision

Evidence exceeds the portfolio minimum of five qualified signals. Differentiation is parameterized mixed-envelope workflow plus a bounded fit coupon, not the basic idea of parallel slots. Proceed as MM-ORG-019.
