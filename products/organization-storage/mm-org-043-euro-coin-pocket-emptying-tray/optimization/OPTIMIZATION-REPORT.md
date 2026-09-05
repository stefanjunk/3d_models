# MM-ORG-043 — FDM optimization report

Scope: reduce print time and deposited material on the coin tray while every coin recess,
the named clearance and the support-free entry ramp stay exactly as designed. All slices
are local, with the exact pinned machine and filament profiles. Nothing was uploaded and
no print was started.

## 1. Baseline identity

| item | value |
|---|---|
| model | `source/generated/coin-tray.stl`, 8032 triangles, 128.0 × 112.0 × 16.34 mm |
| source | `source/tray.py` (unchanged master) |
| printer | Anycubic Kobra 3 Max, 0.4 mm hardened steel nozzle |
| process | `0.20mm PETG Tool @AC K3 Max`, sha256 `fbe19c51…423a75e1` |
| filament | SUNLU PETG Black, `filament_max_volumetric_speed` 10 mm³/s |
| slicer | Anycubic Slicer Next 1.3.9.4 |
| orientation | flat underside down, no supports |
| time / material | 15 482 s (4 h 18 min) / 59 901 mm³ ≈ 76.1 g |
| layers / peak flow | 81 / 8.61 mm³/s |
| warnings | none |

## 2. Where the cost is — measured, not assumed

This part is the opposite case to MM-ORG-042. The 10.34 mm slab is far thicker than two
opposing wall stacks, so a genuine sparse core exists: the G-code deposits 42 % of the
CAD solid volume. The cost is therefore in *skins*, and the feature breakdown says so:
**internal solid infill alone is 47.5 % of all filament** (321 668 mm of path), with a
further 11.1 % in internal bridging. Walls together are 25.7 %.

The driver is that eight recesses are cut to **eight different depths** (6.21–8.34 mm),
so the slicer builds eight separate 1.2 mm top-shell stacks at eight different heights,
each bridged over sparse infill — and every solid layer spans the full 128 × 112 mm
footprint. Full table in `protected-geometry.md`.

Two levers follow directly: shrink the *footprint*, and reduce the *shell count*.

## 3. Candidates — one isolated lever family each

| id | lever family | change |
|---|---|---|
| A | process, layer height | 0.20 → 0.28 mm |
| A2 | process, shell count | top/bottom shell 1.2 → 0.8 mm at the qualified 0.20 mm layer |
| B1 | geometry | cell pitch 31 → 28 mm; inter-recess wall 4.85 → 1.85 mm; footprint 128 × 112 → 116 × 106 mm |
| B2 | geometry | B1 + every recess cut to the deepest 8.34 mm, collapsing eight floor planes into one |
| C | combined | B2 geometry + 0.28 mm layer |
| D1 | combined | B1 geometry + 0.8 mm shells (qualified layer height) |
| D2 | combined | B1 geometry + 0.28 mm layer |

## 4. Measured results

| candidate | time | Δ time | material | Δ material | layers | peak flow | warnings | supports |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 4 h 18 | — | 76.1 g | — | 81 | 8.61 | 0 | none |
| A layer 0.28 | 3 h 58 | −7.5 % | 78.6 g | **+3.3 %** | 58 | 8.30 | 0 | none |
| A2 thin shells | 3 h 54 | −9.2 % | 67.7 g | −11.0 % | 81 | 8.83 | 0 | none |
| B1 pitch | 3 h 49 | −10.9 % | 68.1 g | −10.4 % | 81 | 9.09 | 0 | none |
| B2 pitch + uniform depth | 3 h 43 | −13.5 % | 67.2 g | −11.7 % | 81 | 9.09 | 0 | none |
| C B2 + 0.28 | 3 h 22 | −21.6 % | 67.6 g | −11.2 % | 58 | 9.62 | 0 | none |
| **D1 B1 + thin shells** | **3 h 28** | **−19.1 %** | **60.8 g** | **−20.0 %** | 81 | 9.09 | 0 | none |
| D2 B1 + 0.28 | 3 h 29 | −18.7 % | 69.5 g | −8.6 % | 58 | 9.62 | 0 | none |

Three findings the summary alone would hide:

1. **A larger layer height costs material on this part.** At 0.28 mm the 1.2 mm bottom
   shell rounds up to 5 layers = 1.40 mm, so A deposits 3.3 % *more* than the baseline
   while saving 7.5 % time. Layer height is a time lever here, never a material lever.
2. **Uniform recess depth is not worth it.** B2 beats B1 by only 6 minutes and 0.9 g, and
   it costs real ergonomics: 1c, 2c and 5c coins would sit up to 2.13 mm deeper.
   Rejected on that ratio.
3. **The unqualified layer height buys almost nothing once the shells are thinned.** C is
   6 minutes faster than D1 but 6.8 g heavier, and it needs a layer height outside the
   calibration baseline. D1 keeps the qualified 0.20 mm layer and wins on material.

No `Support`, `Bridge` warning or overhang feature appears in any candidate; peak flow
stays below the filament's declared 10 mm³/s throughout.

## 5. Protected geometry — verified, not assumed

Recess diameters measured by sectioning each mesh at z = 4.8 mm and taking the X extent
of every interior loop (the Y extent also spans the 3 mm finger notch):

| variant | recesses | measured diameters (mm) |
|---|---|---|
| baseline | 8 | 16.65, 19.14, 20.15, 21.65, 22.65, 23.64, 24.65, 26.14 |
| B1 | 8 | identical |
| B2 | 8 | identical |

Nominal is coin diameter + 0.40 mm clearance; the ≤ 0.01 mm deviations are STL chord
error at `angularTolerance 0.1` and are present in the baseline too, so no variant
introduces a regression. The inter-recess wall goes 4.85 → 1.85 mm, still above the
1.35 mm minimum, and `_check()` in `source/tray_variants.py` fails the build if a pitch
ever violates it. `fdm_ci.py audit-mesh --profile release` returns PASS for both variant
meshes. The recess clearance stays `0.40 mm UNQUALIFIED_PROVISIONAL` in every candidate
and `hole-gauge-vertical` is unchanged.

## 6. Selection

- Unrestricted, the Pareto set is **{C, D1}**: C is 6 min faster, D1 is 6.8 g lighter.
- Under the qualified 0.20 mm layer height, the Pareto set is **D1 alone**.

**Recommended: D1** — 3 h 28 and 60.8 g, −19.1 % time and −20.0 % material, on the
qualified layer height. C's remaining 6 minutes are not worth qualifying a new layer
height for, and C would cost 6.8 g to get them.

D1 still needs the human `slicer-preflight` gate, because the 0.8 mm shell profile is not
the pinned `0.20mm PETG Tool @AC K3 Max` even though the layer height and nozzle are
unchanged.

## 7. Open items and residual uncertainty

- **Thinner floor under the deepest recess.** With 0.8 mm shells, the 2.0 mm under-floor
  beneath the 50c recess becomes 0.8 mm bottom + 0.8 mm top skin with roughly 0.4 mm of
  sparse infill between, where the baseline was fully solid. Coins impose almost no load,
  but this is a real change and belongs in the physical gate. If it is unwanted, raise
  `under_floor_mm` from 2.0 to 2.4 mm and re-slice.
- **The footprint shrinks** from 128 × 112 mm to 116 × 106 mm and the entry ramp narrows
  from 124 to 112 mm. Visible change → concept revision recorded in `design-spec.yaml`.
- **1.85 mm between recesses** instead of 4.85 mm. Above the minimum wall, but drop
  resistance when coins are tipped in is a physical property, not a slicer result.
- The recess clearance remains UNQUALIFIED; `hole-gauge-vertical` still has to be printed.

## 8. Artifact hashes

| artifact | sha256 |
|---|---|
| `source/tray_variants.py` | `f6e35b1a8814e6e3de6f725584c56780602ef94720b4bcf4a608de86c420f189` |
| `source/generated/variants/coin-tray-b1-pitch.stl` | `a33548d33d57bc4c3913e2a24ef075973b2e3b2b5e50ef7ab1b0f5031f637d75` |
| `source/generated/variants/coin-tray-b2-pitch-uniform-depth.stl` | `af0476473df124c87c2804158ce0d0fb35e3270369ae14f341ef86eae120a764` |
| `profiles/…/process-0p20-petg-thinshell-k3max-CANDIDATE.json` | `8e6eaf556f8b2e51b19dde62f8ee3cc23c3509c8493ef2df8982a5418dee73a9` |
| `profiles/…/process-0p28-petg-tool-k3max-CANDIDATE.json` | `3e7cd68375d3f3134f88bd1472dd729b37bb6e7354e1b1fef078b8d2d2022931` |
| `exports/v0.1.0/opt-d1-pitch-thinshell/plate_1.gcode` | `ca56b87487f2a3ea883c0bd116f516b3735ada86d5ff02de732566e700f81b8e` |
| `exports/v0.1.0/opt-c-combined/plate_1.gcode` | `7098ee3e2dce57c4370245789c1b230ad8d21ea2bd2b2fe8e478561ca13ac90b` |

Machine-readable: `variant-geometry.json`, `variant-comparison-input.json`,
`variant-comparison-input-qualified-layer.json`, `../reports/optimization/*.json`.
