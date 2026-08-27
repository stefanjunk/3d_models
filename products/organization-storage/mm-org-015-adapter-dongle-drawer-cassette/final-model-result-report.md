# MM-ORG-015 final digital model result

Revision `0.1.0-draft.1` is a fully parametric, regenerated and slicer-preflighted draft print candidate. The user-deferred physical gate remains open, so this is not a validated production release.

## Deliverables

| Artifact | Bounds (mm) | Topology | SHA-256 |
| --- | --- | --- | --- |
| Cassette STL | 220 × 160 × 8.4 | 1 watertight positive-volume component; 1,532 triangles | `eb4b7b656b635bf5e28ee35f75390ef4255ff5e277ba35feba68863a5e31aad0` |
| Measurement-card STL | 150 × 88 × 2 | 1 watertight positive-volume component; 556 triangles | `895baf143591c91ef6e3fa3fddf09640b61b68626f54ad55630aacbd089d91f8` |
| Two-object 3MF | cassette plus card | 2 watertight objects | `1e3eb2ae6181359c3a8eb5e869ce62fc7bca920dce199482b091a690cfb94062` |

Editable STEP masters for the cassette, measurement card and virtual assembly are in `exports/cad/`. The authoritative parameter source is `config/model-parameters.json`; `cad/build.py` regenerates manufacturing artifacts and evidence.

## Functional result

- Twenty independent item classes drive body size, connector reach/width and side/end clearances.
- Class-derived 3.2–6.0 mm rails locate bodies without hiding small items.
- Open through-base connector windows avoid using a connector as a locating or retention surface.
- Font-independent two-bar position codes require 29 analytic cutters for positions 01–20.
- A separate coarse gauge provides width notches, thickness notches and a 100 mm ruler; calipers remain authoritative.
- The cassette CAD volume is 95,972.99 mm3 versus 295,680 mm3 for its full bounding solid, a 67.54% reduction.

## Digital evidence

- Thirteen parameter tests: PASS.
- Parametric-source, mesh-generation and interface reports: PASS.
- STL audits: watertight, positive volume, consistent winding, zero boundary/nonmanifold edges and within bed/triangle budgets.
- 3MF structure: PASS with two build objects and millimetre units.
- Exact Anycubic Slicer Next 1.3.9.4 preflight using Kobra 3 Max / 0.4 mm / 0.20 mm Standard / Anycubic PLA: PASS, 42 layers, 14,701 s estimate, 92,786.41 mm3 extruded volume, 38,576.11 mm positive extrusion, 13.259 mm3/s peak flow, one tool and no native object warnings.
- Hash-bound approvals through print-candidate and aggregate draft project validation: PASS.

## Deferred gate

Physical fit with measured target items, surface marking, connector load avoidance, target-drawer closure, code readability and 250 cycles of the tightest position require the user's print. Watermarking, safety review and commercial release also remain blocked. No G-code was retained and no printer action was performed.
