# metriMade watermark validation report

Asset revision: `MM-WM-001-R1`  
Example identity: `metriMade.com` / `MM-ORG-001 · v0.1.0`  
Digital validation date: 2026-08-25  
Overall status: `DIGITAL_PASS_PHYSICAL_TEST_PENDING`

## Digital result

The generator requires an uppercase hyphenated product ID and a Semantic Versioning version. The negative test rejected `product-id=bad`, `version=1` as intended. The example exports contain outlined geometry with no live SVG text. OpenSCAD generated the SVG/DXF profile, mirrored underside cutter and recessed coupon from the same product-specific source.

| Artifact | Result | Measured evidence |
|---|---|---|
| Cutter STL | `PASS` | watertight; consistent winding; 34 separate engraving bodies; `62.27330 × 11.20001 × 0.40000 mm`; positive volume `99.96746 mm³` |
| Coupon STL | `PASS` | watertight; consistent winding; one body; `69.78900 × 18.80000 × 2.40000 mm`; positive volume `3046.41304 mm³` |
| Identity record | `PASS` | fixed domain `metriMade.com`; exact product ID `MM-ORG-001`; exact version display `v0.1.0` |
| SVG/DXF | `PASS` | closed manufacturing outlines exported from the same OpenSCAD profile; no live SVG text |
| Hashes | `PASS` | all example files pass `exports/examples/MM-ORG-001_v0.1.0/manifest.sha256` |

The 34 disconnected cutter bodies are intentional: separate logo planes and glyph islands form one Boolean cutting tool. Each body is closed; the cutter as loaded is watertight and has positive volume.

## Remaining release gate

Digital geometry does not prove first-layer legibility. Print the generated coupon with the exact intended printer, 0.40 mm nozzle, 0.20 mm layer profile, material/color and bed surface. Complete `physical-test-record.csv`, archive the slicer preview and confirm that domain, product ID and version are readable without guessing. Until then the asset remains a production candidate, not a released production watermark.
