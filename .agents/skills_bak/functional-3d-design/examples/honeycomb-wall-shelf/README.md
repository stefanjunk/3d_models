# Honeycomb wall shelf/display cell

This example demonstrates a **balanced-hybrid** decision: the custom honeycomb body is printed, while screws and wall anchors are purchased and selected for the real wall.

## Build

```bash
python model.py --out generated
```

Outputs include STEP and STL for the shelf and a keyhole-fit coupon.

## Design intent

- flat back on the build plate;
- no inaccessible support in the default orientation;
- thick perimeter and local mounting pads;
- two keyholes to resist rotation;
- editable screw-head/shank allowances;
- no invented wall-load rating.

Print and test the coupon with the **actual screw** before printing or mounting the shelf. Proof-test with nonvaluable ballast in a guarded area before displaying anything valuable.
