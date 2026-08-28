# MM-ORG-026 SignRail

Fully parametric digital candidate for SKU-014: a personalized 200 × 50 mm engraved insert held by two reusable 70-degree end stands. The font-safe workflow uses the repository-owned `MM-GRID-5X7-v1` glyph source for both live SVG proof and CAD; no installed font file is required.

```bash
python tools/live_text_preview.py
python cad/build.py
pytest -q
python cad/render_preview.py
```

Outputs include STEP masters, four unique watertight STLs, and a five-object 3MF with one insert, two stand instances, and the fit coupon pair. All remain draft artifacts pending physical and commercial/customer-proof gates. No G-code is retained and no printer action is included.
