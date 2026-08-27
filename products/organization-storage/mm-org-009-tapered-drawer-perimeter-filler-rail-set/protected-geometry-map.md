# Protected geometry map

| Region | Protection rule | Reason |
|---|---|---|
| Rail underside | Preserve `z = 0` on both longitudinal walls and every rib. | Bed contact and drawer-bottom datum. |
| Organizer face | Preserve straight local `y = 0` face and configured clearance. | Fit datum. |
| Drawer-wall face | Preserve front/rear effective widths and linear taper. | Fit datum. |
| Top skin | Minimum 2.0 mm and no bridge bay over 12 mm. | Printability and handling stiffness. |
| Side/end walls | Minimum 2.25/2.40 mm. | Stable extrusion count and edge durability. |
| Cross-ribs | Minimum 1.80 mm; continuous wall-to-wall and bed-to-roof connection. | Roof support and one-body topology. |
| Lift scallops | Preserve root radius and at least 1.8 mm outer-wall reserve. | Removal access without sharp roots. |
| Gauge taper/notches | Preserve width law and countable notch sequence. | Measurement function. |

No lossy mesh simplification may move these regions. For this analytic CAD model, a sane direct tessellation is preferred over downstream decimation.
