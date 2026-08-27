# Concept-to-CAD correspondence

| Visible concept feature | Parametric CAD owner | Acceptance evidence |
|---|---|---|
| Precision, Soft and Lounge tray silhouettes | `tray_variants.*.corner_radius` | STEP/STL envelopes and preview |
| Open, clean item wells | `shell.wall`, `shell.floor`, `shell.rim_radius` | positive wall reserve and watertight mesh checks |
| Orange underside receiver bosses | `interface.receiver_*` | socket-center assertions and coupon |
| Removable bow-tie link | `interface.link_*` | connector mesh and nominal clearance calculation |
| Short socket roof bridge | `interface.socket_height` and `receiver_height` | bridge span reported; physical bridge test deferred |
| Three-module desktop arrangement | `assembly.layout` | assembled preview bounds |

No image-derived surface or hidden geometry is used. Exact dimensions live in the JSON parameter file.
