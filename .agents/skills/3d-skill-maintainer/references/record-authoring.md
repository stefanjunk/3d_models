# Record authoring

## Distill, do not summarize the chat

Preserve the raw trace separately. A lesson should contain the smallest scoped
explanation that can change a future decision. Include expected, actual,
mechanism hypothesis, alternatives, triggers, exclusions, transfer limits, and
source links.

For user feedback, preserve all three values:

1. what the system originally proposed;
2. what the user corrected;
3. what was accepted after verification.

Create an eval in the same phase if the correction is actionable. The eval
captures a general failure mode. For example, mirrored mounting holes produce a
coordinate-frame eval, not the rule “holes always go right.”

## Scope checklist

- feature type and geometry class;
- design parameters, named datums, constraints, and construction method;
- FFF process and exact printer/unit/firmware;
- manufacturer, product, variant, color, batch, conditioning;
- nozzle diameter/material/geometry/hotend/wear;
- orientation and environment;
- slicer/version/profile/hash;
- measurement method, resolution, uncertainty, and raw artifacts.

Use `unknown` or `null` for missing facts. Never infer a batch, firmware, nozzle
alloy, or profile hash.

## Negative results

Store failed or unacceptable approaches with their cause hypothesis and the
scope in which they failed. Do not promote an “avoid” rule until its explanation
has been tested. Rejected records remain linked and searchable.

## Source authority

For product-specific process bounds, prefer the exact physical product/batch
label over a broader family page when they conflict. Record both sources and the
conflict. Do not silently average ranges.
