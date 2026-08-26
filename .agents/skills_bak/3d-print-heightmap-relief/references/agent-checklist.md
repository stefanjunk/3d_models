# Agent checklist

Before processing:
- [ ] classify image and surface;
- [ ] record source physical or square-pixel natural aspect;
- [ ] record target patch in millimetres;
- [ ] choose repeat vs single placement;
- [ ] set `aspect_policy=preserve` unless distortion is explicitly approved.

During processing:
- [ ] create/register a 16-bit source master;
- [ ] compute fit in millimetres, not raster pixels;
- [ ] calculate target X/Y pitch and PPI;
- [ ] generate target raster from the source master in one resampling pass;
- [ ] create a square-pixel preview when X/Y pitch differs;
- [ ] validate reconstructed physical aspect before geometry.
- [ ] estimate the uniform-grid triangle/file-size worst case over the actual displaced area;
- [ ] define `PASS`/`REVIEW`/`STOP` mesh budgets before the expensive Boolean;
- [ ] record peak-memory GiB, mesh-file MiB, and exact-slicer seconds budgets in the job;
- [ ] choose adaptive generation or a physical simplification tolerance rather than a triangle percentage.

Surface mapping:
- [ ] plane uses mm X/Y;
- [ ] cylinder uses `R*theta` arc length;
- [ ] rounded box uses accumulated perimeter arc length;
- [ ] sphere/ellipsoid subjects stay on bounded low-distortion patches;
- [ ] arbitrary UV mapping is checked for real surface distortion.

Before delivery:
- [ ] verify aspect error is within tolerance;
- [ ] verify circle/square diagnostic when mapping is uncertain;
- [ ] verify wall thickness and relief depth;
- [ ] compare unsimplified and candidate meshes for topology, protected faces, bidirectional error, relief amplitude, seams, and bed contact;
- [ ] retain separate reference/master and manufacturing mesh artifacts;
- [ ] gate volume change, relief-mask correlation, robust contrast loss, and nozzle-relative RMS error;
- [ ] record actual triangles/file size and the decision to simplify or retain the reference mesh;
- [ ] verify slicer appearance;
- [ ] run the separate exact-slicer gate and compare load/slice time and resulting toolpaths when resampling or simplification changed;
- [ ] provide the one-command source replacement/rebuild workflow.
