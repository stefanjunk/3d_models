# MM-ART-010 Berlin — DRAFT digital-candidate-r7

All four native Anycubic project files contain four non-empty tool bodies and slice in Anycubic Slicer Next. This closes the reported empty-geometry failure for the right project. It does not authorize a print or commercial release.

| Mode / half | 3MF triangles | Native layers | Tool changes | Result |
|---|---:|---:|---:|---|
| `boundary_crop` left | 80,248 | 24 | 8 | Pass |
| `boundary_crop` right | 65,980 | 23 | 3 | Pass |
| `context_outline` left | 164,384 | 26 | 8 | Pass; runtime review |
| `context_outline` right | 150,244 | 23 | 3 | Pass |

The left halves contain the 16.5 × 15.97 mm metriCreate marker at the frozen address and raise it 0.6 mm in Sky Blue/tool 4. A 0.5 mm Oak reveal separates it from the upper Mint/Midnight bodies. The marker remains at least 12.25 mm from a retained light aperture.

The generic standard-only 3MF checker reports the Anycubic `p:path` layout as missing geometry. That parser limitation is isolated in `3mf/berlin-boundary-crop-right-generic-3mf.json`; the vendor-aware geometry reports resolve those paths and the native slicer produces executable G-code from every project.

The `context_outline` left project exceeded the nominal 600 second slice target but completed inside the controlled 900 second retry. Physical marker readability, ACE mapping, purge, connectors, lighting appearance, watermark and release remain open human gates.
