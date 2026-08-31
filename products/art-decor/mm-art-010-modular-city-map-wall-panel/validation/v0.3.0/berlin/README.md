# Berlin digital candidate evidence 0.3.0

Digital result: **PASS for frozen-source rebuild, eight closed color bodies,
two closed composites, portable four-material 3MF structure, mesh budgets,
three-change color topology and geometry-only Anycubic preflight. Human and
physical reviews remain open.**

The accepted model uses a 0.25 mm manufacturing mask derived from the frozen
EPSG:25833 OSM vectors. Each half is 299.875 × 400 × 4.6 mm and fits the
420 × 420 mm bed. Left/right composite triangle counts are 71,996 and 59,326.
The deliberate river/canal openings occupy 1.52% and 1.88% of their halves.

The portable 3MFs contain four named materials in touching Z-only bands. The
color estimator reports exactly three changes and no layer with more than one
active color. `slice-left-composite-r2.json` and
`slice-right-composite-r1.json` are exact-profile single-material composite
preflights: they validate geometry, bed fit and layer generation, not physical
ACE slots or purge behavior.

Final combined estimates from these two geometry runs are 201,493.97 mm
filament and 85,248 s. Do not treat them as a multicolor production estimate:
the destination-slicer project still needs explicit Bone White/Nardo
Grey/Black/Orange slot mapping, purge tower and tool/color preview review.
No printer upload or print start occurred.
