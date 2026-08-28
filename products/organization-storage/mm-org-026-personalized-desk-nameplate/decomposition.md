# Decomposition

| Component | Source of truth | Build quantity | Interface |
|---|---|---:|---|
| Personalized insert | parameters + `gridfont.py` + `build.py` | 1 | 3.0 mm thickness, 70-degree stands |
| Angled end stand | parametric CAD | 2 identical | 3.4 mm open slot, symmetric centers ±78 mm |
| Angled slot gauge | same slot generator | 1 | 3.2/3.4/3.6 mm at 70 degrees |
| Insert fit key | same plate thickness | 1 | 3.0 mm exact thickness |
| Live proof | `live_text_preview.py` + same glyph source | digital | normalized name/title, font ID, layout, SVG hash |
| Font allowlist | project evidence file | digital | internal candidate approval; commercial review open |

No purchased components, system font, font binary, logo, icon, third-party mesh, or image-to-3D geometry is used.
