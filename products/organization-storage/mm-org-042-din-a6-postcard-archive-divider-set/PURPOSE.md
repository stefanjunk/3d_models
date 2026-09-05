# Purpose — MM-ORG-042 DIN A6 postcard archive divider set

## Intended use

Sort DIN A6 postcards, prints and A6 cards by date or theme in a customer-owned dry indoor drawer, using labelled open-top lanes cut to the ISO 216 A6 trimmed size.

## Who it is for

Journalers, families, travellers and collectors who already own a drawer and want the inside of it organised by category.

## What it is not

- Not an archival system. No acid-free, moisture, UV, fire or privacy protection.
- Not a fixed-size product. The drawer envelope is always a customer input, never an assumed dimension.
- Not load-bearing, not for wall, vehicle, outdoor or wet use.
- Not a toy and not for children.
- No fit or compatibility claim until the lane clearance is qualified by a coupon on the exact process.

## Why additive manufacturing

The lane layout, count, depth, tab position and text follow from one customer's drawer and one customer's category list. That per-order pairing of an exact published media format with an unknown host is what mass production cannot do.

## Evidence position

ISO 216 fixes A6 at 105 x 148 mm — a published standard, not an estimate. What is NOT known is the process clearance that turns that nominal into a working lane.

The calibration registry currently returns `NO_MATCHING_PROCESS` for
Anycubic Kobra 3 Max / SUNLU PETG / 0.4 mm. No clearance on this printer and material
has ever been qualified, so the clearance ships as an explicit parameter with an
`UNQUALIFIED` status and a named coupon as its gate.

## Current state

metriCreate MVP candidate at revision 0.1.0. Preflight is `C2 · R3 · K1 · Lane B · CONDITIONAL`
with all seven hard gates passing. **No physical print, no coupon and no test result exists.**

## Traceability

- Portfolio row: `business/02-portfolio/product-portfolio.csv`
- Research origin: `business/02-portfolio/research-ideas-r3-variants.csv#SKU-507`
- Preflight: `preflight/preflight-result.json`
- Rights workspace: `commercial-clearance/`
