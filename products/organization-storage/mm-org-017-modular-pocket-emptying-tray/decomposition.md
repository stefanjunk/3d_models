# Product decomposition

| Component | Source of truth | Registration/interface | Manufacturing output |
| --- | --- | --- | --- |
| Soft Arc module | JSON + CadQuery analytic rounded shell | Common left socket/right tab; shared ramp and mouth datums | STEP + STL |
| Clean Facet module | JSON + CadQuery eight-sided shell | Same functional interfaces | STEP + STL |
| Utility Rib module | JSON + CadQuery tight-radius shell and three fused rear ribs | Same functional interfaces | STEP + STL |
| Connector clearance gauge | JSON + CadQuery plate and three edge sockets | 0.15/0.25/0.35 mm female offsets; hole count identifies size | STEP + STL |
| Connector test key | JSON + CadQuery trapezoid and handling pad | Exact nominal male tab | STEP + STL |
| Connected virtual set | Compound of the three module masters at 56 mm pitch | Visual/assembly reference only | STEP |
| Print build set | Mesh objects and explicit bed transforms | Five independent objects, millimetre units | 3MF |

No organic mesh, heightmap, texture, purchased component or external artwork is required. STEP remains the editable interchange master, STL the manufacturing mesh, and JSON plus `cad/build.py` the authoritative parametric source.

Protected interfaces are the base datum, connector polygon, 56 mm pitch, ramp endpoints, front lip/mouth and minimum walls. Style edits may change only the exterior shell treatment and declared ribs.
