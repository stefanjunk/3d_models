# Palette measurement worksheet

For every palette, record the maximum dimensions while fully closed. Do not store customer photos with released product files.

| Palette ID | Closed face width (mm) | Closed face height (mm) | Maximum closed thickness by caliper (mm) | Hinge/protrusion note | Assigned clear lane (mm) |
|---|---:|---:|---:|---|---:|
| P01 | | | | | |
| P02 | | | | | |
| P03 | | | | | |
| P04 | | | | | |
| P05 | | | | | |
| P06 | | | | | |

Photo method:

1. Put a flat 100 mm scale in the same plane as the closed palette.
2. Take a directly overhead photo without portrait/perspective correction.
3. Enter the two scale endpoints and palette corners TL/TR/BR/BL in `assets/photo-capture-example.json` format.
4. Run `python tools/photo_dimension_capture.py INPUT --output OUTPUT`.
5. Retake if perspective skew exceeds 3%.
6. Measure maximum closed thickness separately with calipers and add at least 1.0 mm retrieval clearance.

After printing, record the chosen coupon slot (2.7/2.9/3.1 mm), actual insertion feel, any rocking, and surface marks.
