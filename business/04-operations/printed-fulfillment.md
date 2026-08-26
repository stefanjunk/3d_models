# Printed product fulfillment

Printed products are part of the business model but are not enabled in the first transactional MVP.

## Readiness gate

Set `PRINT_FULFILLMENT_READY=true` only when at least one exact SKU/revision has:

- approved material, color, printer, nozzle, layer, wall/infill/support and post-process profile;
- capacity, lead-time and maximum-order assumptions;
- incoming material and machine-maintenance controls;
- first-article and batch QC with measurable accept/reject criteria;
- revision/batch/producer traceability on the object or packaging as appropriate;
- packaging, instructions, required manufacturer/product/safety information, shipping labels and returns address;
- shipping prices and services tested for every enabled country;
- defect, late-order, damage, return, withdrawal, complaint, recall and incident procedures;
- cost model including failure allowance, labor, packaging, payment, warranty/returns and taxes;
- product-liability/insurance decision and required legal review.

## Production traveler

Every order should resolve to a production traveler containing:

- order line, SKU, revision and approved variant;
- source/customer-file hash;
- printer, profile, material brand/type/color/lot and operator;
- start/end time, outcome, failure/reprint reason;
- measured critical dimensions and visual inspection result;
- post-processing and assembled/purchased component lot;
- package/label revision and shipping handoff.

## Custom dimensions

Customer dimensions are not sent directly to a printer. The server or operator validates units, ranges, feature rules, price, build volume and manufacturing feasibility; generates a frozen candidate; performs the required review; and links the approved variant to the order. Out-of-range requests become a quote/design case, not an unchecked checkout.

## Low-risk pilot

After digital launch, produce one standard launch SKU in Germany in a capped weekly quantity. Use it to validate actual labor, scrap, packaging, carrier damage, support and returns before adding custom printed products.

