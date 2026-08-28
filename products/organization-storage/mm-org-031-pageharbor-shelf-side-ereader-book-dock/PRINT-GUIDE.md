# Print guide

1. Print the two gauge/key-comb pairs first, base down, without supports. Fit keys from left to right in ascending nominal thickness and choose the lowest repeatable sliding station.
2. Measure the real cased device and closed book with calipers at their thickest contact region; never infer case thickness from device marketing dimensions.
3. Set `selected_device_case_thickness_mm`, `selected_book_thickness_mm` and measured clearance in `config/model-parameters.json`, rebuild, and re-run all digital gates.
4. Reference profile: Anycubic Kobra 3 Max, 0.4 mm nozzle, PLA, selected layer height documented by the retained optimization report. Use at least three perimeters and four top/bottom layers; supports remain disabled.
5. Orient every part exactly as exported. Do not scale STLs in the slicer because scaling changes both fit gaps and protected sections.
6. Keep the 40 mm center region and rear cable route clear. This is only an access keepout—there is no charging, connector-fit or thermal-performance claim.
7. Complete `tests/physical-test-plan.md` before relying on the dock. No G-code is supplied or retained.
