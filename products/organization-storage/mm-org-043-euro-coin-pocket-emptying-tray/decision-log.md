# MM-ORG-043 decision log

## 2026-09-04 — Intake, preflight and parametric source, revision 0.1.0

| # | Decision | Reasoning | Alternatives rejected |
|---|---|---|---|
| 1 | Selected SKU-540 as metriCreate MVP model 3 | Trend 97, readiness R3, and euro coin diameters are fixed by EU regulation — the strongest interface evidence anywhere in the portfolio. Distinct product category from MVP 2. | Further divider variants, which would have made the MVP set repetitive |
| 2 | Preflight double-checked before design, as instructed | All seven hard gates PASS, C2 (31.0) · R3 · K1 · Lane B · CONDITIONAL. | Carrying the research-row scores over unchanged |
| 3 | **The 1.00 mm 2c-to-10c step is the binding constraint** | 2c is 18.75 mm and 10c is 19.75 mm. Any clearance at or above half that step lets a 2c coin fall into the 10c recess and sorting fails silently. This is recorded as `DENSE_INTERFACE_COUPLING` and hard-coded as an upper bound of 0.50 mm in the source. | Treating all eight denominations as one generic tolerance |
| 4 | Recess clearance ships as UNQUALIFIED, bounded at 0.50 mm | Same calibration gap as MM-ORG-042: `hole_delta_vertical` is not qualified on this process. 0.40 mm is a declared placeholder; `_check()` refuses to build if it ever reaches half the smallest coin step. | Any assumed hole compensation |
| 5 | Coupon targets the 2c/10c pair specifically | A generic hole gauge would not prove the thing that actually matters. The coupon prints exactly the failing pair at five clearances. | A generic five-hole gauge |
| 6 | Finger notch on every recess | A coin sitting flush in a pocket cannot be picked without a fingernail, which defeats the whole point of a pocket-emptying tray. Recorded as its own human interface with a user test. | Relying on recess depth alone |
| 7 | Three bugs found by asserting the real bounding box | The rear ramp was extruded along Y instead of X and grew the part to 188 mm; the recesses were cut into an already-hollowed pocket; and the intended-dimension check passed while the actual geometry was out of envelope. `_assert_envelope()` now measures the built solid. | Trusting a check that only validates the arithmetic |

## 2026-09-05 — FDM optimization pass on the coin tray

| # | Decision | Reasoning | Alternatives rejected |
|---|---|---|---|
| A | **Measured where the filament goes before choosing a lever** | 47.5 % of all filament is internal solid infill and another 11.1 % is internal bridging; walls together are 25.7 %. Eight recesses at eight different depths force eight separate 1.2 mm top-shell stacks, and every solid layer spans the full footprint. That reading picked the levers, not intuition. | Assuming this part behaves like MM-ORG-042, where the walls were the whole cost |
| B | Footprint shrunk by tightening the cell pitch 31 → 28 mm | Every skin layer spans the footprint, so shrinking it scales the dominant cost directly: −10.9 % time and −10.4 % material with no coin recess, clearance, notch, rim or ramp change. The inter-recess wall lands at 1.85 mm, above the 1.35 mm minimum, and `_check()` fails the build if a pitch ever violates it. | Hollowing the entry ramp, which would have replaced a support-free 7.4° slope with one needing support |
| C | Uniform recess depth generated, measured, and then **rejected** | It collapses eight staggered solid stacks into one, which sounded like the right answer — but it is worth only 6 minutes and 0.9 g over B1, and it sinks 1c, 2c and 5c coins up to 2.13 mm deeper. Bad ratio on a human-interface product. | Keeping it because it was the theoretically elegant fix |
| D | **A larger layer height rejected as a material lever** | At 0.28 mm the 1.2 mm bottom shell rounds up to 5 layers = 1.40 mm, so candidate A deposits 3.3 % *more* material than the baseline while saving 7.5 % of the time. On this part layer height buys time and costs material. | Assuming thicker layers are always cheaper |
| E | D1 selected: pitch 28 mm plus 0.8 mm shells | −19.1 % time and −20.0 % material on the **qualified** 0.20 mm layer height and 0.4 mm nozzle. The unqualified 0.28 mm alternative (C) is 6 minutes faster but 6.8 g heavier — not worth qualifying a new layer height for. | C, which the unrestricted Pareto set also contains |
| F | Thinner under-floor flagged, not hidden | With 0.8 mm shells the 2.0 mm floor under the 50c recess becomes 0.8 mm skin + ~0.4 mm sparse + 0.8 mm skin where it used to be fully solid. Coins impose almost no load, but it is a real change and belongs in the physical gate, with `under_floor_mm` 2.0 → 2.4 mm as the fix if it matters. | Reporting only the headline saving |
