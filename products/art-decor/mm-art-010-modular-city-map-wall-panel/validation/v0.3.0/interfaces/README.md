# Interface validation 0.3.0

Digital result: **PASS for source generation, closed meshes, build volume and
local headless slicing; PHYSICAL NOT RUN**.

The shared family source generated one watertight seam connector, one watertight
test anchor, one watertight lower standoff, one watertight upper hanger and one
coupon STL containing exactly 20 watertight components. The coupon envelope is
184 × 118 × 3 mm. `interface-calculation.json` records geometry-only strain
estimates and preserves the absence of a material allowable.

`slice-coupon-r1.json` is the intentionally preserved fail-closed run: relative
paths were not resolvable inside the slicer's isolated runtime and no G-code was
created. `slice-coupon-r2.json` is the successful rerun with absolute source and
profile paths and a fresh output directory. It used Anycubic Slicer Next 1.3.9.4,
Kobra 3 Max 0.4 mm, 0.20 mm Standard and Anycubic PLA Matte profiles. The output
has 15 layers, one tool, zero tool changes and a 1,771 s slicer estimate.

No printer upload or print start occurred. A human must still print the coupon,
record crack/whitening/seating observations, select the smallest passing
clearance and perform the documented destructive pull observation. The upper
hanger screw-head/keyhole shape is only an installer hardware envelope and has
no universal wall-anchor compatibility or load rating.
