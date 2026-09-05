# MM-ORG-043 — protected geometry map and optimization constraints

Written before any lightweighting variant was generated. Baseline master:
`source/tray.py` → `source/generated/coin-tray.stl`, 8032 triangles,
128.0 × 112.0 × 16.34 mm, CAD solid volume 143 979 mm³.

## Where the cost actually is

Unlike MM-ORG-042, this part does have a real infill core: the slab is 10.34 mm thick,
far more than two opposing wall stacks, and the G-code deposits 59 901 mm³ against a
143 979 mm³ solid — 42 %. So the bulk is genuinely sparse. The cost is in *skins*, not
in walls. Measured from the baseline G-code by feature:

| feature | filament mm | share | path mm |
|---|---:|---:|---:|
| internal solid infill | 9 506 | 47.5 % | 321 668 |
| inner wall | 3 347 | 16.7 % | 124 564 |
| internal bridge | 2 222 | 11.1 % | 84 667 |
| outer wall | 1 803 | 9.0 % | 49 739 |
| sparse infill | 1 392 | 7.0 % | 42 866 |
| bottom surface | 1 268 | 6.3 % | 29 845 |
| top surface | 197 | 1.0 % | 11 672 |
| brim / gap infill / custom | 297 | 1.5 % | 4 871 |

Nearly six filament metres in ten go into solid layers nobody ever sees. The driver is
structural: eight coin recesses are cut to **eight different depths** (6.21 to 8.34 mm),
so the slicer builds eight separate 1.2 mm top-shell stacks at eight different heights,
each bridged over sparse infill. On top of that, every solid layer covers the full
128 × 112 mm footprint minus the recesses.

Two consequences follow. Reducing the *footprint* scales every skin layer at once, and
reducing the *number of distinct recess floor planes* collapses the staggered stacks.

## Protected — no variant may change these

| region | why | source |
|---|---|---|
| recess diameter = EU coin nominal + `recess_clearance_mm` | eight fixed circulation-coin diameters | `parameters/tray.json`, source S47 |
| `recess_clearance_mm` = 0.40 mm `UNQUALIFIED_PROVISIONAL`, bound 0.50 mm | above half the 1.00 mm 2c→10c step the denominations cross-enter and sorting fails silently | `parameters/tray.json` |
| 2.0 mm under-floor beneath the deepest recess | minimum wall under a load-bearing pocket | `_check()` in source |
| 9 × 3 mm finger notch at every recess | single-finger coin retrieval | human interface |
| 2.0 mm perimeter rim standing 3.0 mm above the field | stops coins leaving the tray | function |
| rear entry ramp, 46 mm at 7.4° | pocket-emptying sweep; also the reason the part prints support-free | function + manufacturing |
| flat underside | desk seating, support-free printing | manufacturing |
| ≥ 1.35 mm between adjacent recesses | minimum wall | `_check()` in source |
| outer envelope ≤ 180 × 160 × 45 mm | planning ceiling | `parameters/tray.json` |

## Redundant bulk — removal candidates

| region | lever | risk |
|---|---|---|
| material between recesses, currently 4.85 mm | cell pitch 31 → 28 mm, taking the inter-recess wall to 1.85 mm | medium: still ≥ 1.35 mm minimum wall and no coin fit changes, but the footprint shrinks to 116 × 106 mm and the entry ramp narrows from 124 to 112 mm — a visible change |
| eight staggered recess floor planes | cut every recess to the deepest 8.34 mm | medium: small coins then sit up to 2.13 mm deeper; the full-depth finger notch still reaches them |
| 1.2 mm top and bottom shells | 1.2 → 0.8 mm (process) | medium: thinner skin over the sparse core under each recess floor |
| 0.20 mm layer height | 0.28 mm (process) | 81 → ~58 layers; unqualified process |

## Rejected before slicing

- **Hollowing the entry ramp.** A 2 mm sloped plate over an open cavity at 7.4° would
  need support underneath. Rule 9 runs the other way: eliminate supports geometrically,
  never introduce them. The ramp stays solid with sparse infill.
- **Open or windowed underside.** The pocket ceiling would become a bridged bottom
  surface spanning the whole field, trading cheap sparse infill for expensive bridging.
- **Raising sparse infill density.** It would add material, not remove it; the core is
  already at 5 %.
