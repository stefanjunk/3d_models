---
name: fdm-joints-and-fits
description: Use when a commercial FDM model contains clearance fits, press fits, bearing seats, heat-set inserts, captive nuts, screw joints, alignment pins, or printer-dependent hole compensation.
---

# FDM Joints And Fits

## Core Rule

Keep nominal purchased-part geometry separate from printer compensation. No
single hole offset is valid across 0.4/0.6/0.8 mm nozzles, PLA/PETG/specialist
materials, orientations, slicers, and customer printers.

## Workflow

1. Select the actual purchased component and record its dimensional source.
2. Build the nominal interface with `commercial-component-interfaces` or the
   pinned `cq-warehouse-commercial` skill.
3. State joint purpose, load direction, assembly/disassembly cycles, insertion
   method, retention requirement, and failure mode.
4. Generate a bore/shaft ladder with `scripts/generate_fit_coupon.py`.
5. Print the coupon in the actual material, nozzle class, orientation, and
   critical wall context.
6. Measure dimensions, insertion force, retention, torque or axial load as
   applicable, cracking, and dwell relaxation.
7. Store compensation in a process-specific manufacturing profile, not in a
   universal master dimension.

Heat-set insert holes must come from the selected insert manufacturer's
recommendation and require insertion plus pull-out/torque evidence matching
commercial claims. Captive nuts require tool access, anti-rotation geometry,
and assembly-order validation.

## Completion Gate

Every precision or retention joint is `COUPON_REQUIRED` until physical evidence
exists for the advertised process class. Digital fit is not physical fit.
