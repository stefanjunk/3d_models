# Berlin digital candidate evidence 0.3.0

Digital result: **PASS for frozen-source rebuild, eight closed color bodies,
two closed composites, mesh budgets, three-change color topology and native
Anycubic project-3MF import/slicing. The generic G-code analyzer still reports
a known false layer-count failure for the multicolor files; human and physical
reviews remain open.**

The accepted model uses a 0.25 mm manufacturing mask derived from the frozen
EPSG:25833 OSM vectors. Each half is 299.875 × 400 × 4.6 mm and fits the
420 × 420 mm bed. Left/right composite triangle counts are 71,996 and 59,326.
The deliberate river/canal openings occupy 1.52% and 1.88% of their halves.

The original standards-only 3MFs passed structural validation but Anycubic
Slicer Next 1.3.9.4 rejected both before loading their geometry. They are
retained under `fixtures/`. The replacement files are Anycubic-authored project
3MFs, centred on the configured build plate, with four named volumes assigned
to tools 0–3. Native slicing succeeds for both halves and generates non-empty
G-code with exactly three tool changes. The color estimator independently
reports exactly three changes and no layer with more than one active color.

`slice-left-anycubic-3mf-r1-review.json` and
`slice-right-anycubic-3mf-r1-review.json` verify 23 canonical layer changes,
23 unique Z values, matching header/footer counts, tools 0–3 and three changes.
The sibling adapter reports `FAIL` only because its current analyzer adds the
same 23 `;LAYER_CHANGE` markers to 19 supplemental `; layer #` comments and
therefore misreports 42 layers. The exact G-code remains unchanged and the
false failure is preserved rather than hidden.

The new multicolor project runs estimate 102,539.02 mm / 42,107 s left and
99,320.62 mm / 40,271 s right. Treat these as local candidate estimates, not a
physical production approval: Bone White/Nardo Grey/Black/Orange ACE slot
identity, purge tower and tool/color preview still require human GUI review.
No printer upload or print start occurred.
