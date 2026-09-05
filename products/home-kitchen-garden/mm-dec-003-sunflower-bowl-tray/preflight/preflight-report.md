# Updated 3D-design preflight — MM-DEC-003 Sunflower Bowl / Tray

`MM-DEC-003 Sunflower Bowl / Tray | C2 (29.75/100) | R3 | K1 | Lane B | CONDITIONAL`

## Decision

Proceed with the selected fresh geometry-only Step1X run and the owner-confirmed
parametric disc foot. The Step1X body owns the sunflower form and must not be
repaired or parametrically reconstructed. Millimetre scale, Z orientation, the
80 × 6 mm foot, topology and slicer acceptance remain controlled downstream.

The product is restricted to decorative storage of dry, non-food items. Food
contact, liquid containment, outdoor, child-toy and structural claims are out of
scope. Physical and commercial release stay blocked.

## Interfaces

| Contract | Function | Evidence | Gate |
|---|---|---:|---|
| `IF-EXT-MEC-SUP-PLN-001` | 80 × 6 mm disc support and print seat | E3 owner-confirmed metadata | digital + physical |
| `IF-EXT-GEO-CON-VOLUME-001` | open depression for dry contents | E3 nominal | section + physical |
| `IF-HUM-GEO-CON-FREEFORM-001` | reachable rounded petal rim | E2 visual | mesh screen + physical |

## Hard gates

G0–G6 pass for a controlled digital prototype. This does not approve a physical
or commercial release. The exact process baseline is Kobra 3 Max, 0.4 mm nozzle,
0.20 mm layers and SUNLU PETG Black; yellow production filament remains
unqualified and requires a new complete profile and slice.

## Minimal next evidence

1. Archive a prompt-bound source image and a post-cleanup Step1X run at or after
   fork commit `f00dd46`.
2. Preserve the Step1X body, add only the 80 × 6 mm foot, and pass exact mesh,
   protected-region and supported slicer checks.
3. Print that candidate and pass rocking/tilt, dry-item handling, petal-edge and
   snag inspection before release.
