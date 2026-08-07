# Kobra 3 Max articulated camera arm — v6 from original camera-model dimensions

This revision rebuilds the camera enclosure using **dimensions measured from the original two-part camera housing model**, instead of estimating the camera from a product photo.

## What changed from v5

The camera housing is now based on these measured functional dimensions from the original model:

- front-shell outer extents: **40.71 × 23.42 × 18.63 mm**
- useful PCB cavity: **32.60 × 15.17 mm**
- lens opening: **≈ Ø 14.95 mm**
- LED openings: **≈ Ø 5.35 mm**
- LED center spacing: **≈ 5.92 mm**
- lens-axis to LED-axis horizontal offset: **≈ 15.12 mm**

The new printable housing is still an **independent reconstruction**, not a mesh copy.

## Files

- `04_anycubic_camera_front_shell_FROM_ORIGINAL_MODEL.stl`
- `05_anycubic_camera_back_cover_with_ball_FROM_ORIGINAL_MODEL.stl`
- `06_anycubic_camera_fit_test_frame_FROM_ORIGINAL_MODEL.stl`

The arm kinematics remain:

`printer mount -> hinge 1 -> 150 mm arm -> hinge 2 -> 150 mm arm -> ball socket -> rear-cover ball -> two-part camera housing`

## Housing concept

- **front shell** with separate lens and LED openings
- **rear cover** with integrated ball on the back side
- friction-fit inner lip
- cable notch at the bottom
- small vent slots
- gentle internal compression pads
- front-shell PCB support ledges

## Recommended test order

1. print `08_printer_interface_fit_test_coupon.stl`
2. print `06_anycubic_camera_fit_test_frame_FROM_ORIGINAL_MODEL.stl`
3. check the camera fit and opening alignment
4. print `04...front_shell...` and `05...back_cover...`
5. then print the arms if the fit is good

## Printing

Recommended material: **black PETG**

- 0.20 mm layers
- 4 walls for housing
- 4–5 walls for arms
- 25–35% infill for arms
- 20–30% infill for housing

## Important note

Although the critical dimensions now come from the original camera model, your specific camera module may still have small PCB or connector tolerances. The fit-test frame is still the fastest way to validate the geometry before printing the full set.
