# Print, Buy, Integrate, Eliminate

| Function | Default | Escalate when |
|---|---|---|
| Custom enclosure, bracket, adapter, guide | PRINT | Temperature, fire, food, medical, or structural claims |
| Standard screw, nut, washer | BUY | Prototype-only low load may use printed surrogate |
| Precision shaft, dowel, axle | BUY | Only non-precision toy/visual use may print |
| Ball bearing | BUY | Printed rolling bearing is an experiment, never equivalent |
| Low-speed bushing | PRINT or BUY | Check wear, lubrication, clearance, replaceability |
| Heat-set insert or captive nut | BUY + INTEGRATE | Direct plastic thread only for low cycle/load |
| O-ring, belt, metal spring | BUY | Printed alternatives require a different qualified mechanism |
| Large low-speed gear | PRINT conditionally | Torque, wear, noise, lubrication, alignment, service life |
| Small/high-speed/high-load gear | BUY | Printed release requires specialist evidence |
| Snap-fit or flexure | INTEGRATE conditionally | Creep, cycles, temperature, anisotropy, user safety |

`NEEDS_TEST` blocks detailed release CAD until a coupon or experiment resolves
the decision. `ELIMINATE` must state which function absorbs the removed part.
