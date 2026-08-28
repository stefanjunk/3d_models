# Print and physical-check guide

## Reference slicing

- Printer profile: Anycubic Kobra 3 Max, 0.4 mm nozzle
- Process: 0.20 mm Standard
- Material reference: Anycubic PLA
- Orientation: shelf-contact base down
- Supports: off
- Candidate 3MF: `exports/3mf/DRAFT-MM-ORG-020-belt-scarf-shelf-comb-0.1.0-draft.1.3mf`

The exact-profile digital preflight passed at 290 layers with one tool and no native object warnings. Its G-code was temporary and is not included.

## Recommended sequence

1. Print the R0.6/R1.0/R1.4 edge coupon and connector key first.
2. Pull smooth woven, knit and loose/fringed samples across every marked radius in both directions. Reject any radius that catches fibers or fringe.
3. Verify the connector key engages without whitening, fracture or excessive play. Adjust `default_clearance_mm` if needed, regenerate and re-audit.
4. Print only the preset whose `clear_slot_width_mm` exceeds the measured maximum roll diameter by at least 2 mm.
5. Test at least three representative items per preset for retention and 100 remove/replace cycles.
6. Check shelf sliding and label adhesion on the actual shelf finish.

This is a draft digital candidate, not a validated load-bearing or child-safety product.
