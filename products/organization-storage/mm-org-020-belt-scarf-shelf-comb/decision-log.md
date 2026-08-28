# Decision log

## 2026-08-28 — select open-floor measured-roll architecture

Commercial bamboo/felt compartments and printable belt organizers validate visible rolled storage, but fixed cells risk buckle and fabric mismatch. Selected two brand-neutral measured-envelope presets with no closed floor and no copied competitor geometry.

## 2026-08-28 — isolate textile and connector uncertainty

Production fins use R1.4 leading noses and R1.2 top edges. A marked R0.6/R1.0/R1.4 textile coupon and a separate joint key move the highest-uncertainty physical interfaces into low-cost first prints.

## 2026-08-28 — clean isolated zero-area export facets conservatively

The first coupon STL contained a closed positive-volume main mesh plus eight isolated zero-area triangles at small compound fillets. The manufacturing exporter now removes only degenerate/duplicate facets and unreferenced vertices, then fails closed unless the result remains one watertight, winding-consistent positive volume. See `reports/mesh-facet-cleanup-iteration.json` and E0 candidate EXP-00016.

## 2026-08-28 — stop at digital print candidate

Exact-profile slicing is complete. Fabric snagging, fringe behavior, roll retention, connector fit, retrieval cycling, label adhesion and shelf sliding remain user-owned. No G-code was retained or sent to a printer.
