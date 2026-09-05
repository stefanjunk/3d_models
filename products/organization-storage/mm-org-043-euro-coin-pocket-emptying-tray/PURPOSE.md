# Purpose — MM-ORG-043 Euro circulation-coin pocket-emptying tray

## Intended use

Let an adult sweep euro circulating coins out of a pocket across a shaped slope into open, labelled, denomination-separated recesses on a dry indoor desk or entryway surface.

## Who it is for

Adults who empty their pockets in the same place every day and want the change already sorted when they pick it up again.

## What it is not

- Not secure storage. No authentication, counting, or financial-protection function.
- Worn, foreign, commemorative, damaged and pre-issue coins are out of scope.
- Not for children — loose coins are a choking hazard and child use is excluded by scope, not by a safety feature.
- Not for wet, outdoor, load-bearing or vehicle use.
- No separation claim until the recess clearance is qualified by a coupon on the exact process.

## Why additive manufacturing

The denomination set, capacity per recess and footprint are chosen per customer. Only additive manufacturing makes a one-off tray whose recesses match exactly the coins one person actually carries.

## Evidence position

Euro coin diameters are fixed in EU law — the strongest interface evidence in the whole portfolio. The binding risk is elsewhere: the smallest step in the set is 1.00 mm, between 2c and 10c.

The calibration registry currently returns `NO_MATCHING_PROCESS` for
Anycubic Kobra 3 Max / SUNLU PETG / 0.4 mm. No clearance on this printer and material
has ever been qualified, so the clearance ships as an explicit parameter with an
`UNQUALIFIED` status and a named coupon as its gate.

## Current state

metriCreate MVP candidate at revision 0.1.0. Preflight is `C2 · R3 · K1 · Lane B · CONDITIONAL`
with all seven hard gates passing. **No physical print, no coupon and no test result exists.**

## Traceability

- Portfolio row: `business/02-portfolio/product-portfolio.csv`
- Research origin: `business/02-portfolio/research-ideas-r3-variants.csv#SKU-540`
- Preflight: `preflight/preflight-result.json`
- Rights workspace: `commercial-clearance/`
