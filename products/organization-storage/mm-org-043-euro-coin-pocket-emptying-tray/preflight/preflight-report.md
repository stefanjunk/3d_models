# MM-ORG-043 prospective preflight report

Companion reconstructed on 2026-09-05 from `PREFLIGHT-MM-ORG-043-001` / `0.1.0`. The existing assessment remains the authority; no new evaluation or approval is recorded.

Source: `preflight/preflight-result.json`, SHA-256 `25f97323ff326363cc39683ac182e73dfa402cffed541854915a40c4f62ad116`.

`Euro circulation-coin pocket-emptying tray | C2 (31.0/100) | R3 | K1 | Lane B | CONDITIONAL`

## Decision

`GO_WITH_CONTROLS` — C2 with K1 and R3 gives Lane B, whose method is an interface master plus a fit coupon. All hard gates pass: coin diameters are fixed by EU regulation (E3), the manufacturing profile is the pinned hashed baseline, and per-denomination acceptance criteria exist. The controls are that recess diameters stay UNQUALIFIED parameters until the hole delta is qualified on this exact process, and that the 2c/10c pair with its 1.00 mm step is verified explicitly before any separation claim.

## Scope

Let an adult sweep euro circulating coins out of a pocket across a shaped slope into open, labelled, denomination-separated recesses on a dry indoor desk or entryway surface.

## Open evidence

- Calibration registry returns NO_MATCHING_PROCESS for Anycubic Kobra 3 Max / SUNLU PETG / 0.4 mm; hole_delta_vertical and xy_clearance_sliding are UNQUALIFIED. Recess diameters must not be committed until a coupon qualifies the hole delta on this exact process.
- The 1.00 mm step between the 2c and 10c diameters is the tightest tolerance in the product and no process clearance is qualified.
- Finger-notch geometry has no measured basis and needs a real-hand test.
- No printed coupon, coin placement, separation, stability or 100-cycle result exists.

## Next actions

- Print the hole-gauge-vertical coupon on Anycubic Kobra 3 Max / SUNLU PETG Black / 0.4 mm / 0.20 mm, record a benchmark-measurement and update the calibration registry. Exit: hole_delta_vertical is QUALIFIED and provably below 0.50 mm so the 2c/10c pair can separate.
- Print the tightest three-recess coupon covering 2c, 10c and 5c and verify placement, removal by fingertip and cross-entry. Exit: All three acceptance criteria of IF-EXT-GEO-LOC-CYL-001 pass with recorded measurements.
- Run the real-hand notch test and the fully loaded 10-degree tilt test on a full tray. Exit: IF-HUM-GEO-ACC-EDGE-001 and IF-EXT-MEC-SUP-PLN-001 acceptance pass.

## Basis

- `business/02-portfolio/product-portfolio.csv#PORT-112`
- `business/02-portfolio/research-ideas-r3-variants.csv#SKU-540`
- `business/02-portfolio/research-idea-sources-additions.csv#S47`
- `business/02-portfolio/research-r3-process-baseline.json`
- `libraries/3d-learning/knowledge/processes/fff-calibration-registry.yaml`
- `commercial-clearance/project.json`
- `preflight/preflight-input.yaml`

Physical, fit, appearance and commercial release gates remain separate.
