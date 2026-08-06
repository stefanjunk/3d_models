# Validation Summary

## Automated Result

- Both default variants use a 9 x 18 cylindrical spanning tree with 161 edges and exactly one graph solution.
- The selected default maze has 92 solution steps, 57 turns, and 15 dead ends.
- All four exported STEP parts reload as valid, positive-volume, single-solid B-Reps.
- All four exported STL parts reload as watertight, consistently wound, positive-volume, single-body meshes with no degenerate or broken faces.
- Both print-oriented parts fit a 220 x 220 x 250 mm build volume.
- Declared 1.6 mm minimum walls and 0.8 mm minimum features pass the PLA/0.4 mm nozzle checks.
- The round follower has zero ideal-CAD overlap at every solution node and every edge midpoint in both maze modes, including a 200 mm cavity regression that automatically increases channel resolution.
- Multi-angle STL previews were inspected for both variants. The outer-maze cutaway uses exact triangle/plane clipping for visualization only.

## Residual Gate

No slicer is installed in this environment. The normal-based reports identify downward groove/follower faces that require slicer review. The maze-bearing samples have approximately 2.6% to 2.9% candidate overhang area; follower-only samples are below 0.01%.

Before a gift is locked inside:

1. Slice both STLs with the intended printer profile and inspect groove roofs, the follower, thin-wall detection, seams, and the first-layer rim.
2. Print a short difficulty-1 calibration pair with the same clearance settings.
3. Verify full travel through the maze, then adjust radial or follower clearance in 0.05 mm increments if needed.

Mesh validity does not prove printer-specific fit. PLA shrinkage, extrusion width, elephant foot, seam blobs, bridge sag, and layer ridges require a physical test.
