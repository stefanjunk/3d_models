# Anycubic Kobra 3 Max Filament Settings

**Printer:** Stock Anycubic Kobra 3 Max  
**Nozzles:** 0.4 and 0.8 mm, each in brass, stainless steel, or conventional hardened steel with identical Kobra 3 Max geometry<br>
**Build plate:** Stock textured PEI  
**Slicer:** Anycubic Slicer Next, Advanced mode; field names checked against v2.3.0 commit `70931e5`  
**Profile goal:** Fast, reliable printing without sacrificing visible-wall and top-surface quality  
**Research dates:** 1 August 2026; EONO/GRATKIT update 6 August 2026; TPU/variable-layer update 11 August 2026; nozzle-material/ELEGOO update 12 August 2026

All profile tables below are **derived starting recommendations**, not manufacturer presets. Dry the filament and run the calibration sequence before treating any pressure-advance, flow, or maximum-volumetric-speed value as final. The 0.4 mm Kobra 3 Max values were checked against [Anycubic's pinned Max profile commit](https://github.com/ANYCUBIC-3D/AnycubicSlicerNext/commit/987a3c2bf9ed13934137326bfd522896c70e5101). The 0.8 mm geometry and fallback deltas were checked against the exact Max machine and process profiles in pinned [OrcaSlicer commit `972dae2`](https://github.com/OrcaSlicer/OrcaSlicer/commit/972dae22afdadc3251d05e10c2d6f00c35e6b83a), because the pinned Anycubic tree contains no Max 0.8 profile. Verify the values in your installed configuration bundle because bundled and cloud profiles can differ.

## Critical Setup

| Item | Configuration |
|---|---|
| Kobra 3 Max motion | Keep the stock machine ceilings. Control real print speed with feature speeds, acceleration, and filament maximum volumetric speed. The advertised 600 mm/s is not a useful universal process speed. |
| 0.8 mm hardware | Anycubic lists the Kobra 3 Max nozzle as expandable from the stock 0.4 mm to 0.6/0.8 mm. Use a Kobra 3 Max-compatible 0.8 mm nozzle or hotend, install it according to Anycubic's service guidance, then verify Z offset and bed leveling before printing. |
| Nozzle material | The filament table treats its existing values as the brass baseline and adds stainless- and hardened-steel commissioning values. Scope is identical standard-bore geometry only: no CHT/high-flow bores, ruby/carbide tips, proprietary high-conductivity alloys, coatings that claim brass-like flow, or changed hotends. Nozzle alloy alone does not justify transferring a calibrated MVS. |
| Steel-nozzle temperature | Start stainless and conventional hardened steel at the listed brass temperature. Heat-soak for 5 minutes and run a temperature/MVS test at representative flow. Try the listed `+5 deg C` fallback only for repeatable weak, matte, or under-extruded high-flow lines; return to the baseline and reduce MVS if extra heat worsens stringing, Silk sheen, degradation, or heat creep. |
| Steel-nozzle MVS | The stainless and hardened columns use 80% of the brass-profile MVS as an **uncalibrated commissioning safety policy**, not a measured steel penalty. Enter that value for the first test, then replace it with 80-90% of the actual nozzle/material failure transition. A quality steel nozzle may recover the full brass MVS. |
| 0.8 mm printer preset | Prefer the native `Anycubic Kobra 3 Max 0.8 nozzle` preset when the installed bundle exposes it. Otherwise follow the complete [0.8 mm manual fallback](#08-mm-manual-fallback); the pinned Orca JSON is a settings reference, not a directly importable Slicer Next 2.3.0 profile. A 0.4 preset with only its nozzle diameter changed is incomplete. Do not substitute the smaller Kobra 3 profile. |
| Nozzle-change calibration | A nozzle change invalidates nozzle-sensitive tuning. For every 0.8 mm material preset, start with PA disabled and the conservative MVS listed below; then calibrate flow ratio, PA, and MVS with the installed 0.8 mm nozzle before raising flow. |
| TPU feed | Do **not** feed TPU through ACE Pro. Use the shortest low-drag external path, ideally a top-mounted spool close to the toolhead. Follow Anycubic's instruction to loosen the extruder idler screw by half a turn before loading TPU. |
| TPU preparation | Purge old PLA/PETG completely. A clean nozzle or dedicated TPU hotend is useful if flexible filament buckles before the nozzle. Print one object at a time and avoid retract-heavy geometry. |
| PETG plate | Wash with dish soap, preheat the large bed for about 10 minutes, and let it cool before removal. Use a thin glue layer as a **release barrier** if PETG bonds too strongly. |
| ELEGOO Rapid PETG | Plain, unfilled Rapid PETG is not documented as abrasive and does not require steel. Its 600 mm/s product claim is not a Kobra process speed: use the listed 10/12 mm^3/s brass starts and unlock 14/16 mm^3/s only after nozzle-specific MVS and layer-strength tests. |
| Tri-color Silk PLA | Treat both coextruded Silk filaments as decorative materials. Inspect cardboard-spool winding and brittleness before a long print, test direct external feeding before relying on ACE Pro, and rotate the model around Z to choose which colors dominate each visible face. Slower outer walls preserve gloss better than headline high-speed settings. |
| Variable layer height | Apply it per selected object in `Prepare`, not in the filament preset. Use the exact printer preset's layer-height limits, keep the first layer fixed, and inspect `Layer height`, `Volumetric flow rate (mm³/s)`, `Speed`, overhang, support, and shell-thickness previews before printing. Organic/default tree supports cannot be sliced with a genuinely variable layer profile. |
| Pressure advance | Use one PA source only. Enabling PA in a filament preset replaces printer/auto-calibrated PA; commands are not additive and the last emitted command wins. Calibrate after flow ratio. |
| Profile inheritance | Use the exact Kobra 3 Max **printer** preset for the fitted nozzle. Unlisted filament/cooling fields inherit from the exact duplicated filament base in the preset index; unlisted process fields inherit from the exact duplicated process base. Only unchecked Setting Overrides inherit from the printer preset. Review all inherited values when the configuration bundle changes. |
| Setting Overrides | In Filament > Setting Overrides, check the override box for every listed retraction, wipe, and Z-hop value, including explicit `Off` and `0 mm`. An unchecked box inherits the printer value. |
| Configuration target | Slicer Next v2.3.0 field semantics at commit `70931e5321fa66966a5bfb251efca0e82307d427`, with 0.4 mm Kobra 3 Max profiles from Anycubic commit `987a3c2bf9ed13934137326bfd522896c70e5101` and 0.8 mm Max profiles from Orca commit `972dae22afdadc3251d05e10c2d6f00c35e6b83a`. Do not substitute a smaller Kobra 3 machine preset. |

## Where To Enter Values

| Slicer Next area | Values from this document |
|---|---|
| Filament > Filament | Nozzle-material-specific nozzle temperature and `Max volumetric speed`, plus bed temperatures, flow ratio, `Enable pressure advance`, and PA coefficient |
| Filament > Cooling | Initial no-cooling layers, full-fan layer, minimum/maximum fan with layer-time thresholds, bridge/overhang fan, cooling slowdown, and minimum speed |
| Filament > Setting Overrides | Retraction length/speed, deretraction speed, retract on layer change, wipe, wipe distance, Z-hop height, and Z-hop type; check each override box |
| Process > Quality | Layer height, line widths, `Walls printing order`, `Print infill first`, and seam position |
| Process > Strength | Wall loops, top/bottom shell layers and minimum thickness, sparse infill density, and sparse infill pattern |
| Process > Speed | Initial/feature/travel speeds and feature acceleration |
| Prepare > Variable layer height | Per-object adaptive or manual layer-height profile; `Quality / Speed`, `Adaptive`, `Smooth`, radius, `Keep min`, and the vertical edit bar |
| Printer > Extruder 1 > Size / Layer height limits | `Nozzle diameter` plus `Min` and `Max` layer height for the custom 0.8 mm printer preset |
| Printer > Motion ability | Leave the installed Kobra 3 Max machine ceilings unchanged |

## Preset Index

| Nozzle | Custom filament preset | Duplicate this exact filament base | Custom process preset | Duplicate this exact process base |
|---:|---|---|---|---|
| 0.4 mm | `GEEETECH TPU 95A - 0.20 Balanced` | `Anycubic TPU @Anycubic Kobra 3 Max 0.4 nozzle` | `0.20 Balanced - GEEETECH TPU 95A - K3M` | `0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `GEEETECH TPU 95A - 0.12 Detail Experimental` | `Anycubic TPU @Anycubic Kobra 3 Max 0.4 nozzle` | `0.12 Detail Experimental - GEEETECH TPU 95A - K3M` | `0.12mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `GEEETECH TPU 95A - 0.24 Balanced` | `Anycubic TPU @Anycubic Kobra 3 Max 0.4 nozzle` | `0.24 Balanced - GEEETECH TPU 95A - K3M` | `0.24mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU TPU 95A - 0.20 Balanced` | `Anycubic TPU @Anycubic Kobra 3 Max 0.4 nozzle` | `0.20 Balanced - SUNLU TPU 95A - K3M` | `0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU TPU 95A - 0.12 Detail Experimental` | `Anycubic TPU @Anycubic Kobra 3 Max 0.4 nozzle` | `0.12 Detail Experimental - SUNLU TPU 95A - K3M` | `0.12mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU TPU 95A - 0.24 Balanced` | `Anycubic TPU @Anycubic Kobra 3 Max 0.4 nozzle` | `0.24 Balanced - SUNLU TPU 95A - K3M` | `0.24mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU PETG Black Standard - 0.20 Balanced` | `Anycubic PETG @Anycubic Kobra 3 Max 0.4 nozzle` | `0.20 Balanced - SUNLU PETG Black Standard - K3M` | `0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU PETG Black Standard - 0.12 Detail` | `Anycubic PETG @Anycubic Kobra 3 Max 0.4 nozzle` | `0.12 Detail - SUNLU PETG Black Standard - K3M` | `0.12mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU PETG Black Standard - 0.24 Balanced` | `Anycubic PETG @Anycubic Kobra 3 Max 0.4 nozzle` | `0.24 Balanced - SUNLU PETG Black Standard - K3M` | `0.24mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `ELEGOO Rapid PETG - 0.20 Balanced` | `Anycubic PETG @Anycubic Kobra 3 Max 0.4 nozzle` | `0.20 Balanced - ELEGOO Rapid PETG - K3M` | `0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `ELEGOO Rapid PETG - 0.12 Detail` | `Anycubic PETG @Anycubic Kobra 3 Max 0.4 nozzle` | `0.12 Detail - ELEGOO Rapid PETG - K3M` | `0.12mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `ELEGOO Rapid PETG - 0.24 Balanced` | `Anycubic PETG @Anycubic Kobra 3 Max 0.4 nozzle` | `0.24 Balanced - ELEGOO Rapid PETG - K3M` | `0.24mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU High Speed PLA+ 2.0 - 0.20 Balanced` | `Anycubic PLA High Speed @Anycubic Kobra 3 Max 0.4 nozzle` | `0.20 Balanced - SUNLU HS PLA+ 2.0 - K3M` | `0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU High Speed PLA+ 2.0 - 0.12 Detail` | `Anycubic PLA High Speed @Anycubic Kobra 3 Max 0.4 nozzle` | `0.12 Detail - SUNLU HS PLA+ 2.0 - K3M` | `0.12mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `SUNLU High Speed PLA+ 2.0 - 0.24 Balanced` | `Anycubic PLA High Speed @Anycubic Kobra 3 Max 0.4 nozzle` | `0.24 Balanced - SUNLU HS PLA+ 2.0 - K3M` | `0.24mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `EONO Silk PLA Red-Gold-Blue - 0.20 Balanced` | `Anycubic PLA Silk @Anycubic Kobra 3 Max 0.4 nozzle` | `0.20 Balanced - EONO Silk R-Gold-B - K3M` | `0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `EONO Silk PLA Red-Gold-Blue - 0.12 Detail` | `Anycubic PLA Silk @Anycubic Kobra 3 Max 0.4 nozzle` | `0.12 Detail - EONO Silk R-Gold-B - K3M` | `0.12mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `EONO Silk PLA Red-Gold-Blue - 0.24 Balanced` | `Anycubic PLA Silk @Anycubic Kobra 3 Max 0.4 nozzle` | `0.24 Balanced - EONO Silk R-Gold-B - K3M` | `0.24mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `GRATKIT Silk PLA Blue-Purple-Black - 0.20 Balanced` | `Anycubic PLA Silk @Anycubic Kobra 3 Max 0.4 nozzle` | `0.20 Balanced - GRATKIT Silk BPB - K3M` | `0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `GRATKIT Silk PLA Blue-Purple-Black - 0.12 Detail` | `Anycubic PLA Silk @Anycubic Kobra 3 Max 0.4 nozzle` | `0.12 Detail - GRATKIT Silk BPB - K3M` | `0.12mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.4 mm | `GRATKIT Silk PLA Blue-Purple-Black - 0.24 Balanced` | `Anycubic PLA Silk @Anycubic Kobra 3 Max 0.4 nozzle` | `0.24 Balanced - GRATKIT Silk BPB - K3M` | `0.24mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` |
| 0.8 mm | `GEEETECH TPU 95A - N0.8 Safe Start` | `Anycubic TPU @Anycubic Kobra 3 Max 0.8 nozzle` | `0.20 Fine - GEEETECH TPU 95A - K3M N0.8` | `0.20mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | Reuse `GEEETECH TPU 95A - N0.8 Safe Start` | Existing custom preset | `0.40 Draft - GEEETECH TPU 95A - K3M N0.8` | `0.40mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | `SUNLU TPU 95A - N0.8 Safe Start` | `Anycubic TPU @Anycubic Kobra 3 Max 0.8 nozzle` | `0.20 Fine - SUNLU TPU 95A - K3M N0.8` | `0.20mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | Reuse `SUNLU TPU 95A - N0.8 Safe Start` | Existing custom preset | `0.40 Draft - SUNLU TPU 95A - K3M N0.8` | `0.40mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | `SUNLU PETG Black Standard - N0.8 Safe Start` | `Anycubic PETG @Anycubic Kobra 3 Max 0.8 nozzle` | `0.20 Fine - SUNLU PETG Black - K3M N0.8` | `0.20mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | Reuse `SUNLU PETG Black Standard - N0.8 Safe Start` | Existing custom preset | `0.40 Draft - SUNLU PETG Black - K3M N0.8` | `0.40mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | `ELEGOO Rapid PETG - N0.8 Safe Start` | `Anycubic PETG @Anycubic Kobra 3 Max 0.8 nozzle` | `0.20 Fine - ELEGOO Rapid PETG - K3M N0.8` | `0.20mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | Reuse `ELEGOO Rapid PETG - N0.8 Safe Start` | Existing custom preset | `0.40 Draft - ELEGOO Rapid PETG - K3M N0.8` | `0.40mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | `SUNLU High Speed PLA+ 2.0 - N0.8 Safe Start` | `Anycubic PLA @Anycubic Kobra 3 Max 0.8 nozzle` | `0.20 Fine - SUNLU HS PLA+ 2.0 - K3M N0.8` | `0.20mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | Reuse `SUNLU High Speed PLA+ 2.0 - N0.8 Safe Start` | Existing custom preset | `0.40 Draft - SUNLU HS PLA+ 2.0 - K3M N0.8` | `0.40mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | `EONO Silk PLA Red-Gold-Blue - N0.8 Safe Start` | `Anycubic PLA @Anycubic Kobra 3 Max 0.8 nozzle` | `0.20 Fine - EONO Silk R-Gold-B - K3M N0.8` | `0.20mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | Reuse `EONO Silk PLA Red-Gold-Blue - N0.8 Safe Start` | Existing custom preset | `0.40 Draft - EONO Silk R-Gold-B - K3M N0.8` | `0.40mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | `GRATKIT Silk PLA Blue-Purple-Black - N0.8 Safe Start` | `Anycubic PLA @Anycubic Kobra 3 Max 0.8 nozzle` | `0.20 Fine - GRATKIT Silk BPB - K3M N0.8` | `0.20mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |
| 0.8 mm | Reuse `GRATKIT Silk PLA Blue-Purple-Black - N0.8 Safe Start` | Existing custom preset | `0.40 Draft - GRATKIT Silk BPB - K3M N0.8` | `0.40mm Standard @Anycubic Kobra 3 Max 0.8 nozzle` |

If an exact process base is absent from the installed bundle, use these pinned files as settings references rather than importing them or substituting a smaller Kobra 3 preset: [Anycubic 0.12/0.4](https://raw.githubusercontent.com/ANYCUBIC-3D/AnycubicSlicerNext/987a3c2bf9ed13934137326bfd522896c70e5101/resources/profiles/Anycubic/process/0.12mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.4%20nozzle.json), [Anycubic 0.24/0.4](https://raw.githubusercontent.com/ANYCUBIC-3D/AnycubicSlicerNext/987a3c2bf9ed13934137326bfd522896c70e5101/resources/profiles/Anycubic/process/0.24mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.4%20nozzle.json), [Orca 0.20/0.8](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/972dae22afdadc3251d05e10c2d6f00c35e6b83a/resources/profiles/Anycubic/process/0.20mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.8%20nozzle.json), and [Orca 0.40/0.8](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/972dae22afdadc3251d05e10c2d6f00c35e6b83a/resources/profiles/Anycubic/process/0.40mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.8%20nozzle.json). For missing 0.8 bases, follow the manual fallback below.

The 0.8 mm filament-base names come from the pinned Orca Max bundle and may not appear in every Slicer Next installation. With the custom Max 0.8 printer selected, duplicate the visible Anycubic TPU, PETG, or PLA preset for that printer. If none is visible, create a custom copy from the corresponding 0.4 material, enter every filament/cooling/override value below, then set `Filament > Dependencies > Profile dependencies > Compatible printers` to the exact saved 0.8 printer-preset name. Do not leave a 0.4-only compatibility restriction attached.

The exact `Anycubic PLA Silk @Anycubic Kobra 3 Max 0.4 nozzle` base is present in the same pinned Orca commit. If Slicer Next does not expose it, duplicate the Max 0.4 standard PLA preset and enter every Silk filament, cooling, and retraction value below. For 0.8 mm, start from the listed generic Max PLA base because the pinned bundle has no dedicated Max 0.8 Silk preset.

## 0.8 mm Manual Fallback

Use this only when Slicer Next does not expose a native Max 0.8 preset. Slicer Next may hide process compatibility editing; enable `Show incompatible presets` in the preset selector when the copied process is not visible, and confirm the selected printer still reports a 0.8 mm nozzle before every slice.

### Printer Delta From The Max 0.4 Preset

Duplicate the exact Anycubic `Anycubic Kobra 3 Max 0.4 nozzle` printer preset and save it as `Anycubic Kobra 3 Max 0.8 nozzle`. Retain its 0-426 by 0-420 printable-area polygon, excluded 3 mm side borders that leave the effective X range at 3-423, 501 mm printable height, start/end G-code, acceleration, and jerk values. Change only the following visible fields:

| Slicer Next field | 0.8 mm fallback value |
|---|---:|
| Extruder 1 > Size > Nozzle diameter | 0.8 mm |
| Extruder 1 > Layer height limits > Min | 0.16 mm |
| Extruder 1 > Layer height limits > Max | 0.56 mm |
| Extruder 1 > Z-Hop > Only lift Z above | 0 mm |

The effective machine retraction defaults remain 0.8 mm length, 30 mm/s retract/de-retract, 1 mm travel threshold, layer-change retract on, wipe on at 1 mm, 0.4 mm `Slope` Z-hop, all surfaces, and `Only lift Z below = 499 mm`.

### Process Delta From The Max 0.4 Preset

For **both** manual 0.8 variants, duplicate the exact `0.20mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` process. Save one copy as the listed 0.20/N0.8 process and another as the listed 0.40/N0.8 process. After entering every speed, acceleration, quality, and strength value from the main tables, also set these 0.8-specific fields. A native 0.8 process inherits them; a copied 0.4 process does not.

| Slicer Next field | Both 0.8 processes |
|---|---:|
| Quality > Bridge flow ratio | 1.00 |
| Support > Don't support bridges | On |
| Strength > Detect thin wall | On |
| Quality > Elephant foot compensation | 0.10 mm |
| Quality > Extra perimeters on overhangs | On |
| Quality > X-Y hole compensation | 0 mm |
| Quality > Support line width | 0.82 mm |
| Strength > Top/Bottom solid infill/wall overlap | 15% |
| Speed > Gap infill | 50 mm/s |
| Quality > Seam scarf joint | None |
| Quality > Conditional scarf joint / Scarf joint for inner walls | On / On |
| Quality > Scarf length / Scarf start height / Scarf joint speed | 10 mm / 10% / 30 mm/s |

| Slicer Next field | 0.20 mm layer | 0.40 mm layer |
|---|---:|---:|
| Speed > Overhang `(10%, 25%)` | 0 mm/s, use normal wall speed | 50 mm/s |
| Speed > Overhang `[25%, 50%)` | 40 mm/s | 25 mm/s |
| Speed > Overhang `[50%, 75%)` | 15 mm/s | 15 mm/s |
| Speed > Overhang `[75%, 100%)` | 5 mm/s | 10 mm/s |
| Quality > Top surface flow ratio | 1.00 | 0.96 |

When an 0.8 filament preset was copied from a 0.4 base, first clear every retraction Setting Override checkbox. Then check and enter only the values explicitly listed in [Retraction And Lift Overrides](#retraction-and-lift-overrides); this prevents hidden 0.4-only lift limits from carrying over.

## Filament Presets

| Filament preset name | Nozzle | Brass temp: Initial / Other | Brass MVS | Stainless temp: Start; fallback | Stainless commissioning MVS | Hardened temp: Start; fallback | Hardened commissioning MVS | Textured PEI: Initial / Other | Flow ratio | Enable PA / PA | Drying |
|---|---:|---:|---:|---|---:|---|---:|---:|---:|---|---|
| GEEETECH TPU 95A - 0.20 Balanced | 0.4 mm | 225 / 225 deg C | 2.3 mm^3/s | 225/225; 230/230 deg C | 1.8 mm^3/s | 225/225; 230/230 deg C | 1.8 mm^3/s | 50 / 45 deg C | 1.00 | Off / 0 s initially | 50-55 deg C, 4-6 h; print from dryer if possible |
| GEEETECH TPU 95A - 0.24 Balanced | 0.4 mm | 225 / 225 deg C | 2.3 mm^3/s | 225/225; 230/230 deg C | 1.8 mm^3/s | 225/225; 230/230 deg C | 1.8 mm^3/s | 50 / 45 deg C | 1.00 | Off / 0 s initially | Same |
| GEEETECH TPU 95A - 0.12 Detail Experimental | 0.4 mm | 225 / 225 deg C | 1.6 mm^3/s | 225/225; 230/230 deg C | 1.3 mm^3/s | 225/225; 230/230 deg C | 1.3 mm^3/s | 50 / 45 deg C | 1.00 | Off / 0 s initially | Same; prove 0.20 mm reliability first |
| SUNLU TPU 95A - 0.20 Balanced | 0.4 mm | 215 / 210 deg C | 3.2 mm^3/s | 215/210; 220/215 deg C | 2.6 mm^3/s | 215/210; 220/215 deg C | 2.6 mm^3/s | 55 / 50 deg C | 0.98 | On / 0.020 s start | 55 deg C, 8-12 h; continue from a drybox |
| SUNLU TPU 95A - 0.24 Balanced | 0.4 mm | 215 / 210 deg C | 3.2 mm^3/s | 215/210; 220/215 deg C | 2.6 mm^3/s | 215/210; 220/215 deg C | 2.6 mm^3/s | 55 / 50 deg C | 0.98 | On / 0.020 s start | Same |
| SUNLU TPU 95A - 0.12 Detail Experimental | 0.4 mm | 215 / 210 deg C | 3.2 mm^3/s | 215/210; 220/215 deg C | 2.6 mm^3/s | 215/210; 220/215 deg C | 2.6 mm^3/s | 55 / 50 deg C | 0.98 | On / 0.020 s start | Same; prove 0.20 mm reliability first |
| SUNLU PETG Black Standard - 0.20 Balanced | 0.4 mm | 245 / 250 deg C | 10 mm^3/s | 245/250; 250/255 deg C | 8 mm^3/s | 245/250; 250/255 deg C | 8 mm^3/s | 75 / 70 deg C | 0.95 | On / 0.040 s start | 60-65 deg C, 6-8 h |
| SUNLU PETG Black Standard - 0.24 Balanced | 0.4 mm | 245 / 250 deg C | 10 mm^3/s | 245/250; 250/255 deg C | 8 mm^3/s | 245/250; 250/255 deg C | 8 mm^3/s | 75 / 70 deg C | 0.95 | On / 0.040 s start | Same |
| SUNLU PETG Black Standard - 0.12 Detail | 0.4 mm | 245 / 250 deg C | 10 mm^3/s | 245/250; 250/255 deg C | 8 mm^3/s | 245/250; 250/255 deg C | 8 mm^3/s | 75 / 70 deg C | 0.95 | On / 0.040 s start | Same |
| ELEGOO Rapid PETG - 0.20 Balanced | 0.4 mm | 250 / 250 deg C | 10 mm^3/s | 250/250; 255/255 deg C | 8 mm^3/s | 250/250; 255/255 deg C | 8 mm^3/s | 75 / 70 deg C | 0.95 | Off / 0 s initially | No exact cycle; 60 deg C, 6-8 h derived start |
| ELEGOO Rapid PETG - 0.24 Balanced | 0.4 mm | 250 / 250 deg C | 10 mm^3/s | 250/250; 255/255 deg C | 8 mm^3/s | 250/250; 255/255 deg C | 8 mm^3/s | 75 / 70 deg C | 0.95 | Off / 0 s initially | Same |
| ELEGOO Rapid PETG - 0.12 Detail | 0.4 mm | 250 / 250 deg C | 10 mm^3/s | 250/250; 255/255 deg C | 8 mm^3/s | 250/250; 255/255 deg C | 8 mm^3/s | 75 / 70 deg C | 0.95 | Off / 0 s initially | Same |
| SUNLU High Speed PLA+ 2.0 - 0.20 Balanced | 0.4 mm | 220 / 220 deg C | 18 mm^3/s | 220/220; 225/225 deg C | 14.4 mm^3/s | 220/220; 225/225 deg C | 14.4 mm^3/s | 60 / 55 deg C | 0.97 | On / 0.026 s start | 50 deg C for at least 4 h if exposed or stringing |
| SUNLU High Speed PLA+ 2.0 - 0.24 Balanced | 0.4 mm | 220 / 220 deg C | 18 mm^3/s | 220/220; 225/225 deg C | 14.4 mm^3/s | 220/220; 225/225 deg C | 14.4 mm^3/s | 60 / 55 deg C | 0.97 | On / 0.026 s start | Same |
| SUNLU High Speed PLA+ 2.0 - 0.12 Detail | 0.4 mm | 220 / 220 deg C | 18 mm^3/s | 220/220; 225/225 deg C | 14.4 mm^3/s | 220/220; 225/225 deg C | 14.4 mm^3/s | 60 / 55 deg C | 0.97 | On / 0.026 s start | Same |
| EONO Silk PLA Red-Gold-Blue - 0.20 Balanced | 0.4 mm | 215 / 210 deg C | 8 mm^3/s | 215/210; 220/215 deg C proxy max | 6.4 mm^3/s | 215/210; 220/215 deg C proxy max | 6.4 mm^3/s | 60 / 55 deg C | 0.96 | On / 0.040 s start | No exact cycle; 50-55 deg C for 4-6 h only if needed |
| EONO Silk PLA Red-Gold-Blue - 0.24 Balanced | 0.4 mm | 215 / 210 deg C | 8 mm^3/s | 215/210; 220/215 deg C proxy max | 6.4 mm^3/s | 215/210; 220/215 deg C proxy max | 6.4 mm^3/s | 60 / 55 deg C | 0.96 | On / 0.040 s start | Same |
| EONO Silk PLA Red-Gold-Blue - 0.12 Detail | 0.4 mm | 215 / 210 deg C | 8 mm^3/s | 215/210; 220/215 deg C proxy max | 6.4 mm^3/s | 215/210; 220/215 deg C proxy max | 6.4 mm^3/s | 60 / 55 deg C | 0.96 | On / 0.040 s start | Same |
| GRATKIT Silk PLA Blue-Purple-Black - 0.20 Balanced | 0.4 mm | 215 / 210 deg C | 10 mm^3/s | 215/210; 215/215 deg C ceiling | 8 mm^3/s | 215/210; 215/215 deg C ceiling | 8 mm^3/s | 55 / 50 deg C | 0.96 | On / 0.040 s start | No manufacturer cycle; 45-50 deg C for 4-6 h only if needed |
| GRATKIT Silk PLA Blue-Purple-Black - 0.24 Balanced | 0.4 mm | 215 / 210 deg C | 10 mm^3/s | 215/210; 215/215 deg C ceiling | 8 mm^3/s | 215/210; 215/215 deg C ceiling | 8 mm^3/s | 55 / 50 deg C | 0.96 | On / 0.040 s start | Same |
| GRATKIT Silk PLA Blue-Purple-Black - 0.12 Detail | 0.4 mm | 215 / 210 deg C | 10 mm^3/s | 215/210; 215/215 deg C ceiling | 8 mm^3/s | 215/210; 215/215 deg C ceiling | 8 mm^3/s | 55 / 50 deg C | 0.96 | On / 0.040 s start | Same |
| GEEETECH TPU 95A - N0.8 Safe Start | 0.8 mm | 225 / 225 deg C | 3.0 mm^3/s provisional | 225/225; 230/230 deg C | 2.4 mm^3/s | 225/225; 230/230 deg C | 2.4 mm^3/s | 50 / 45 deg C | 1.00 start | Off / 0 s until recalibrated | 50-55 deg C, 4-6 h; print from dryer if possible |
| SUNLU TPU 95A - N0.8 Safe Start | 0.8 mm | 215 / 210 deg C | 3.2 mm^3/s temporary | 215/210; 220/215 deg C | 2.6 mm^3/s | 215/210; 220/215 deg C | 2.6 mm^3/s | 55 / 50 deg C | 0.98 start | Off / 0 s until recalibrated | 55 deg C, 8-12 h; continue from a drybox |
| SUNLU PETG Black Standard - N0.8 Safe Start | 0.8 mm | 245 / 250 deg C | 10 mm^3/s temporary | 245/250; 250/255 deg C | 8 mm^3/s | 245/250; 250/255 deg C | 8 mm^3/s | 75 / 70 deg C | 0.95 start | Off / 0 s until recalibrated | 60-65 deg C, 6-8 h |
| ELEGOO Rapid PETG - N0.8 Safe Start | 0.8 mm | 250 / 250 deg C | 12 mm^3/s temporary | 250/250; 255/255 deg C | 9.6 mm^3/s | 250/250; 255/255 deg C | 9.6 mm^3/s | 75 / 70 deg C | 0.97 start | Off / 0 s until recalibrated | No exact cycle; 60 deg C, 6-8 h derived start |
| SUNLU High Speed PLA+ 2.0 - N0.8 Safe Start | 0.8 mm | 220 / 220 deg C | 18 mm^3/s temporary | 220/220; 225/225 deg C | 14.4 mm^3/s | 220/220; 225/225 deg C | 14.4 mm^3/s | 60 / 55 deg C | 0.97 start | Off / 0 s until recalibrated | 50 deg C for at least 4 h if exposed or stringing |
| EONO Silk PLA Red-Gold-Blue - N0.8 Safe Start | 0.8 mm | 220 / 215 deg C | 8 mm^3/s temporary | 220/215; 225/220 deg C proxy only | 6.4 mm^3/s | 220/215; 225/220 deg C proxy only | 6.4 mm^3/s | 60 / 55 deg C | 0.98 start | Off / 0 s until recalibrated | No exact cycle; 50-55 deg C for 4-6 h only if needed |
| GRATKIT Silk PLA Blue-Purple-Black - N0.8 Safe Start | 0.8 mm | 215 / 215 deg C | 10 mm^3/s temporary | 215/215; no hotter fallback | 8 mm^3/s | 215/215; no hotter fallback | 8 mm^3/s | 55 / 50 deg C | 0.98 start | Off / 0 s until recalibrated | No manufacturer cycle; 45-50 deg C for 4-6 h only if needed |

Each 0.24/0.4 process has a separately named filament preset with the same material values as its 0.20 counterpart, avoiding ambiguous `0.20` names in the slicer. Each 0.8 mm filament preset is shared by its 0.20 and 0.40 mm process variants.

The table row is the logical profile, not a claim that one saved preset can hold three nozzle materials simultaneously. Keep the listed preset name for brass. For steel, duplicate it and append `- SS Commissioning` or `- HS Commissioning`, then enter the matching temperature and MVS columns. After calibration, replace `Commissioning` with a date or `Calibrated`; do not overwrite a measured steel result with the generic 80% start.

Bulk conductivity explains why steel can develop a larger heater-to-bore gradient under flow, but it cannot calculate the required temperature offset. Representative values are about 116 W/(m K) for C360 brass at 20 deg C, 15-18 W/(m K) for 304 stainless at 20-200 deg C, and 26-27 W/(m K) for hardened A2 tool steel at 20-200 deg C. Sensor location, heater contact, melt-zone length, bore finish, plating, and polymer viscosity dominate the actual print correction. In CNC Kitchen's controlled V6/PLA comparison, quality hardened steel differed noticeably only below about 200 deg C; Prusa provides a conditional `+5` to `+10 deg C` troubleshooting range rather than proof of a universal offset. The conservative table therefore starts both steels at the brass temperature and exposes only a `+5 deg C` fallback within each filament's documented range.

`MVS` is maximum volumetric speed. It is the hard sustained-flow cap and matters more than the printer's headline speed. Most 0.8 mm rows deliberately reuse their current 0.4 mm caps only for safe first prints; those caps are profile values or derived starts, not measured nozzle-independent maxima. Orca states that MVS changes with nozzle diameter, so recalibrate every nozzle/material pair and keep 10-20% below the first repeatable failure or quality transition.

GEEETECH's `2.3 mm^3/s` 0.4 mm value is derived from `0.45 mm x 0.20 mm x 25 mm/s = 2.25 mm^3/s`, rounded up; it was not measured in a volumetric-flow test. The cited 25 mm/s comment concerned a Kobra 3, omitted nozzle/layer/line-width geometry, and cannot prove an MVS for the Max. A 0.8 mm nozzle normally lowers nozzle pressure, so `3.0 mm^3/s` is used here as a modest **uncalibrated engineering estimate**, not a manufacturer or owner result. At 225 deg C, dry filament, and a short top feed, calibrate GEEETECH 0.8 from `2.0` to `5.0 mm^3/s` in `0.25 mm^3/s` steps; stop for roughness, weak/matte extrusion, clicking, gear slip, or filament escape, then retain only 80-90% of the first repeatable transition.

The GEEETECH 45 deg C later bed, 25% minimum fan, PETG 75 deg C first-layer bed, SUNLU TPU 55 deg C/8-12 h drying cycle, and both Silk drying suggestions are derived Kobra/direct-drive starting values outside or between manufacturer bands. They are intentionally labeled recommendations, not manufacturer specifications.

PA sweep ranges are calibration instructions, not preset values: `0.00-0.04 s` for TPU, `0.025-0.060 s` for PETG and Rapid PETG with the 0.4 nozzle, `0.020-0.050 s` for Rapid PETG with the 0.8 nozzle, `0.015-0.045 s` for High Speed PLA+ 2.0, and `0.025-0.050 s` for Silk PLA. If printer auto-calibration is preferred, disable filament PA rather than entering a number.

## Retraction And Lift Overrides

Each material row applies to all listed layer heights and both nozzle sizes. Check every listed override box. These are starting values; retune only after flow and PA are stable with the fitted nozzle.

| Filament | Length | Retraction Speed | De-retraction Speed | Retract when change layer | Wipe while retracting | Wipe Distance | Z-hop height / Z-hop type |
|---|---:|---:|---:|---|---|---:|---|
| GEEETECH TPU 95A | 0.5 mm | 20 mm/s | 20 mm/s | Off | Off | 0 mm | 0 mm / Normal |
| SUNLU TPU 95A | 0.8 mm | 30 mm/s | 25 mm/s | Off | Off | 0 mm | 0 mm / Normal |
| SUNLU PETG Black Standard | 0.8 mm | 30 mm/s | 30 mm/s | On | On | 1 mm | 0.4 mm / Slope |
| ELEGOO Rapid PETG | 0.8 mm | 30 mm/s | 30 mm/s | On | On | 1 mm | 0.4 mm / Slope |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 35 mm/s | 35 mm/s | On | On | 1 mm | 0.4 mm / Slope |
| EONO Silk PLA Red-Gold-Blue | 0.8 mm | 30 mm/s | 30 mm/s | On | On | 1 mm | 0.4 mm / Slope |
| GRATKIT Silk PLA Blue-Purple-Black | 0.8 mm | 30 mm/s | 30 mm/s | On | On | 1 mm | 0.4 mm / Slope |

## Cooling Overrides

| Filament preset | No cooling for the first | Full fan speed at layer | Min fan speed threshold | Max fan speed threshold | Force cooling for overhangs and bridges | Overhangs and external bridges fan speed | Slow printing down for better layer cooling / Min print speed |
|---|---:|---:|---:|---:|---|---:|---|
| GEEETECH TPU 95A - 0.20 Balanced | 2 layers | 4 | 25% at 60 s | 35% at 15 s | On | 50% | On / 10 mm/s |
| GEEETECH TPU 95A - 0.24 Balanced | 2 layers | 4 | 25% at 60 s | 35% at 15 s | On | 50% | On / 10 mm/s |
| GEEETECH TPU 95A - 0.12 Detail Experimental | 2 layers | 4 | 30% at 60 s | 40% at 15 s | On | 50% | On / 8 mm/s |
| SUNLU TPU 95A - 0.20 Balanced | 2 layers | 4 | 30% at 60 s | 50% at 15 s | On | 100% | On / 20 mm/s |
| SUNLU TPU 95A - 0.24 Balanced | 2 layers | 4 | 30% at 60 s | 50% at 15 s | On | 100% | On / 20 mm/s |
| SUNLU TPU 95A - 0.12 Detail Experimental | 2 layers | 4 | 40% at 60 s | 60% at 15 s | On | 100% | On / 20 mm/s |
| SUNLU PETG Black Standard - 0.20 Balanced | 3 layers | 6 | 35% at 60 s | 55% at 15 s | On | 100% | On / 20 mm/s |
| SUNLU PETG Black Standard - 0.24 Balanced | 3 layers | 6 | 35% at 60 s | 55% at 15 s | On | 100% | On / 20 mm/s |
| SUNLU PETG Black Standard - 0.12 Detail | 3 layers | 6 | 40% at 60 s | 65% at 15 s | On | 100% | On / 20 mm/s |
| ELEGOO Rapid PETG - 0.20 Balanced | 5 layers | 6 | 30% at 60 s | 70% at 15 s | On | 90% | On / 20 mm/s |
| ELEGOO Rapid PETG - 0.24 Balanced | 5 layers | 6 | 30% at 60 s | 70% at 15 s | On | 90% | On / 20 mm/s |
| ELEGOO Rapid PETG - 0.12 Detail | 5 layers | 6 | 35% at 60 s | 80% at 15 s | On | 90% | On / 20 mm/s |
| SUNLU High Speed PLA+ 2.0 - 0.20 Balanced | 1 layer | 3 | 80% at 60 s | 100% at 12 s | On | 100% | On / 20 mm/s |
| SUNLU High Speed PLA+ 2.0 - 0.24 Balanced | 1 layer | 3 | 80% at 60 s | 100% at 12 s | On | 100% | On / 20 mm/s |
| SUNLU High Speed PLA+ 2.0 - 0.12 Detail | 1 layer | 3 | 80% at 60 s | 100% at 12 s | On | 100% | On / 20 mm/s |
| EONO Silk PLA Red-Gold-Blue - 0.20 Balanced | 1 layer | 3 | 80% at 60 s | 100% at 12 s | On | 100% | On / 20 mm/s |
| EONO Silk PLA Red-Gold-Blue - 0.24 Balanced | 1 layer | 3 | 80% at 60 s | 100% at 12 s | On | 100% | On / 20 mm/s |
| EONO Silk PLA Red-Gold-Blue - 0.12 Detail | 1 layer | 3 | 80% at 60 s | 100% at 12 s | On | 100% | On / 20 mm/s |
| GRATKIT Silk PLA Blue-Purple-Black - 0.20 Balanced | 1 layer | 3 | 80% at 60 s | 100% at 12 s | On | 100% | On / 20 mm/s |
| GRATKIT Silk PLA Blue-Purple-Black - 0.24 Balanced | 1 layer | 3 | 80% at 60 s | 100% at 12 s | On | 100% | On / 20 mm/s |
| GRATKIT Silk PLA Blue-Purple-Black - 0.12 Detail | 1 layer | 3 | 80% at 60 s | 100% at 12 s | On | 100% | On / 20 mm/s |
| GEEETECH TPU 95A - N0.8 Safe Start | 2 layers | 4 | 25% at 60 s | 35% at 15 s | On | 50% | On / 7 mm/s |
| SUNLU TPU 95A - N0.8 Safe Start | 2 layers | 4 | 30% at 60 s | 50% at 15 s | On | 100% | On / 9 mm/s |
| SUNLU PETG Black Standard - N0.8 Safe Start | 3 layers | 6 | 35% at 60 s | 55% at 15 s | On | 100% | On / 20 mm/s |
| ELEGOO Rapid PETG - N0.8 Safe Start | 5 layers | 6 | 30% at 60 s | 65% at 15 s | On | 90% | On / 20 mm/s |
| SUNLU High Speed PLA+ 2.0 - N0.8 Safe Start | 1 layer | 3 | 80% at 60 s | 100% at 12 s | On | 100% | On / 20 mm/s |
| EONO Silk PLA Red-Gold-Blue - N0.8 Safe Start | 1 layer | 3 | 70% at 60 s | 90% at 15 s | On | 100% | On / 15 mm/s |
| GRATKIT Silk PLA Blue-Purple-Black - N0.8 Safe Start | 1 layer | 3 | 70% at 60 s | 90% at 15 s | On | 100% | On / 15 mm/s |

The 0.24/0.4 cooling values match the corresponding 0.20/0.4 starting values. Each 0.8 cooling row serves both 0.20 and 0.40 mm processes; layer-time slowdown handles most geometry-dependent differences. The thresholds are derived starting values. Unlisted cooling fields inherit from the duplicated filament base in the preset index; inspect the sliced preview for unexpected slowdowns.

Both 0.12 mm TPU profiles are experimental. First complete a representative 0.20 mm print reliably; 0.12 mm greatly increases layer count, print duration, retraction opportunities, and exposure to feed drag. Fall back to 0.16 mm or 0.20 mm if extrusion becomes intermittent.

## Process Speeds

| Filament | Nozzle | Layer | Initial layer | Initial layer infill | Outer wall | Inner wall | Sparse infill | Internal solid infill | Top surface | External bridge | Travel |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GEEETECH TPU 95A | 0.4 mm | 0.12 mm | 12 mm/s | 15 mm/s | 18 mm/s | 24 mm/s | 25 mm/s | 20 mm/s | 16 mm/s | 12 mm/s | 160 mm/s |
| GEEETECH TPU 95A | 0.4 mm | 0.20 mm | 12 mm/s | 15 mm/s | 20 mm/s | 25 mm/s | 25 mm/s | 22 mm/s | 18 mm/s | 15 mm/s | 180 mm/s |
| GEEETECH TPU 95A | 0.4 mm | 0.24 mm | 12 mm/s | 15 mm/s | 20 mm/s | 21 mm/s | 21 mm/s | 20 mm/s | 18 mm/s | 15 mm/s | 180 mm/s |
| GEEETECH TPU 95A | 0.8 mm | 0.20 mm | 8 mm/s | 9 mm/s | 14 mm/s | 18 mm/s | 18 mm/s | 17 mm/s | 13 mm/s | 10 mm/s | 180 mm/s |
| GEEETECH TPU 95A | 0.8 mm | 0.40 mm | 7 mm/s | 8 mm/s | 7 mm/s | 9 mm/s | 9 mm/s | 8 mm/s | 6 mm/s | 5 mm/s | 160 mm/s |
| SUNLU TPU 95A | 0.4 mm | 0.12 mm | 20 mm/s | 20 mm/s | 30 mm/s | 45 mm/s | 50 mm/s | 40 mm/s | 30 mm/s | 20 mm/s | 180 mm/s |
| SUNLU TPU 95A | 0.4 mm | 0.20 mm | 20 mm/s | 20 mm/s | 25 mm/s | 35 mm/s | 35 mm/s | 30 mm/s | 25 mm/s | 20 mm/s | 180 mm/s |
| SUNLU TPU 95A | 0.4 mm | 0.24 mm | 20 mm/s | 20 mm/s | 25 mm/s | 29 mm/s | 29 mm/s | 28 mm/s | 25 mm/s | 20 mm/s | 180 mm/s |
| SUNLU TPU 95A | 0.8 mm | 0.20 mm | 8 mm/s | 9 mm/s | 16 mm/s | 19 mm/s | 19 mm/s | 18 mm/s | 16 mm/s | 14 mm/s | 180 mm/s |
| SUNLU TPU 95A | 0.8 mm | 0.40 mm | 8 mm/s | 9 mm/s | 8 mm/s | 9 mm/s | 9 mm/s | 9 mm/s | 7 mm/s | 7 mm/s | 160 mm/s |
| SUNLU PETG Black Standard | 0.4 mm | 0.12 mm | 30 mm/s | 35 mm/s | 65 mm/s | 90 mm/s | 100 mm/s | 80 mm/s | 45 mm/s | 22 mm/s | 250 mm/s |
| SUNLU PETG Black Standard | 0.4 mm | 0.20 mm | 30 mm/s | 35 mm/s | 80 mm/s | 110 mm/s | 110 mm/s | 90 mm/s | 55 mm/s | 25 mm/s | 250 mm/s |
| SUNLU PETG Black Standard | 0.4 mm | 0.24 mm | 30 mm/s | 35 mm/s | 80 mm/s | 90 mm/s | 90 mm/s | 85 mm/s | 50 mm/s | 25 mm/s | 250 mm/s |
| SUNLU PETG Black Standard | 0.8 mm | 0.20 mm | 20 mm/s | 25 mm/s | 45 mm/s | 60 mm/s | 60 mm/s | 50 mm/s | 40 mm/s | 25 mm/s | 250 mm/s |
| SUNLU PETG Black Standard | 0.8 mm | 0.40 mm | 20 mm/s | 25 mm/s | 25 mm/s | 30 mm/s | 30 mm/s | 28 mm/s | 20 mm/s | 18 mm/s | 230 mm/s |
| ELEGOO Rapid PETG | 0.4 mm | 0.12 mm | 30 mm/s | 35 mm/s | 65 mm/s | 90 mm/s | 100 mm/s | 80 mm/s | 45 mm/s | 25 mm/s | 250 mm/s |
| ELEGOO Rapid PETG | 0.4 mm | 0.20 mm | 30 mm/s | 35 mm/s | 80 mm/s | 100 mm/s | 100 mm/s | 90 mm/s | 55 mm/s | 25 mm/s | 250 mm/s |
| ELEGOO Rapid PETG | 0.4 mm | 0.24 mm | 30 mm/s | 35 mm/s | 75 mm/s | 80 mm/s | 80 mm/s | 75 mm/s | 50 mm/s | 25 mm/s | 250 mm/s |
| ELEGOO Rapid PETG | 0.8 mm | 0.20 mm | 20 mm/s | 25 mm/s | 50 mm/s | 70 mm/s | 70 mm/s | 65 mm/s | 40 mm/s | 25 mm/s | 250 mm/s |
| ELEGOO Rapid PETG | 0.8 mm | 0.40 mm | 20 mm/s | 25 mm/s | 28 mm/s | 35 mm/s | 35 mm/s | 32 mm/s | 22 mm/s | 18 mm/s | 230 mm/s |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.12 mm | 35 mm/s | 45 mm/s | 100 mm/s | 180 mm/s | 230 mm/s | 150 mm/s | 80 mm/s | 30 mm/s | 300 mm/s |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.20 mm | 35 mm/s | 45 mm/s | 120 mm/s | 180 mm/s | 200 mm/s | 160 mm/s | 80 mm/s | 30 mm/s | 300 mm/s |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.24 mm | 35 mm/s | 45 mm/s | 110 mm/s | 165 mm/s | 165 mm/s | 145 mm/s | 75 mm/s | 30 mm/s | 300 mm/s |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.20 mm | 25 mm/s | 35 mm/s | 75 mm/s | 105 mm/s | 105 mm/s | 95 mm/s | 60 mm/s | 30 mm/s | 300 mm/s |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.40 mm | 25 mm/s | 35 mm/s | 40 mm/s | 54 mm/s | 54 mm/s | 48 mm/s | 35 mm/s | 25 mm/s | 280 mm/s |
| EONO Silk PLA Red-Gold-Blue | 0.4 mm | 0.12 mm | 20 mm/s | 25 mm/s | 40 mm/s | 65 mm/s | 70 mm/s | 60 mm/s | 35 mm/s | 25 mm/s | 250 mm/s |
| EONO Silk PLA Red-Gold-Blue | 0.4 mm | 0.20 mm | 20 mm/s | 25 mm/s | 45 mm/s | 65 mm/s | 75 mm/s | 60 mm/s | 40 mm/s | 25 mm/s | 250 mm/s |
| EONO Silk PLA Red-Gold-Blue | 0.4 mm | 0.24 mm | 20 mm/s | 25 mm/s | 40 mm/s | 60 mm/s | 65 mm/s | 55 mm/s | 35 mm/s | 25 mm/s | 250 mm/s |
| EONO Silk PLA Red-Gold-Blue | 0.8 mm | 0.20 mm | 15 mm/s | 20 mm/s | 25 mm/s | 35 mm/s | 40 mm/s | 35 mm/s | 25 mm/s | 20 mm/s | 250 mm/s |
| EONO Silk PLA Red-Gold-Blue | 0.8 mm | 0.40 mm | 15 mm/s | 20 mm/s | 18 mm/s | 22 mm/s | 24 mm/s | 22 mm/s | 18 mm/s | 15 mm/s | 230 mm/s |
| GRATKIT Silk PLA Blue-Purple-Black | 0.4 mm | 0.12 mm | 20 mm/s | 25 mm/s | 45 mm/s | 75 mm/s | 85 mm/s | 70 mm/s | 40 mm/s | 25 mm/s | 250 mm/s |
| GRATKIT Silk PLA Blue-Purple-Black | 0.4 mm | 0.20 mm | 20 mm/s | 25 mm/s | 50 mm/s | 85 mm/s | 100 mm/s | 80 mm/s | 45 mm/s | 25 mm/s | 250 mm/s |
| GRATKIT Silk PLA Blue-Purple-Black | 0.4 mm | 0.24 mm | 20 mm/s | 25 mm/s | 45 mm/s | 75 mm/s | 90 mm/s | 70 mm/s | 40 mm/s | 25 mm/s | 250 mm/s |
| GRATKIT Silk PLA Blue-Purple-Black | 0.8 mm | 0.20 mm | 15 mm/s | 20 mm/s | 30 mm/s | 45 mm/s | 55 mm/s | 45 mm/s | 28 mm/s | 20 mm/s | 250 mm/s |
| GRATKIT Silk PLA Blue-Purple-Black | 0.8 mm | 0.40 mm | 15 mm/s | 20 mm/s | 22 mm/s | 28 mm/s | 30 mm/s | 28 mm/s | 22 mm/s | 15 mm/s | 230 mm/s |

For the 0.8 mm brass rows, the temporary rectangular flow ceilings at 0.82 mm line width are approximately `18/9 mm/s` for GEEETECH TPU at the provisional 3.0 mm^3/s cap, `20/10 mm/s` for SUNLU TPU, `61/30 mm/s` for SUNLU PETG, `73/36 mm/s` for ELEGOO Rapid PETG, `110/55 mm/s` for High Speed PLA+, `49/24 mm/s` for EONO Silk, and `61/30 mm/s` for GRATKIT Silk at 0.20/0.40 mm layers. Slicer Next reduces the listed feature speed when the selected filament preset's MVS is lower; this is how the same process table works with the steel commissioning presets. Confirm in Preview using `Volumetric flow rate (mm³/s)` because the slicer's rounded bead model can differ slightly from the rectangular check.

## Process Acceleration

| Filament | Nozzle | Layer | Normal printing | Initial layer | Outer wall | Inner wall | Sparse infill | Internal solid infill | Top surface | Bridge | Travel |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| GEEETECH TPU 95A | 0.4 mm | 0.12 mm | 1,000 | 400 | 600 | 900 | 1,200 | 700 | 500 | 400 | 2,500 |
| GEEETECH TPU 95A | 0.4 mm | 0.20 mm | 1,500 | 500 | 800 | 1,200 | 1,500 | 1,000 | 700 | 500 | 3,000 |
| GEEETECH TPU 95A | 0.4 mm | 0.24 mm | 1,500 | 500 | 800 | 1,200 | 1,500 | 1,000 | 700 | 500 | 3,000 |
| GEEETECH TPU 95A | 0.8 mm | 0.20 mm | 1,000 | 400 | 600 | 800 | 1,000 | 700 | 500 | 400 | 2,500 |
| GEEETECH TPU 95A | 0.8 mm | 0.40 mm | 700 | 300 | 400 | 600 | 700 | 500 | 350 | 300 | 2,000 |
| SUNLU TPU 95A | 0.4 mm | 0.12 mm | 1,000 | 500 | 600 | 900 | 1,000 | 800 | 600 | 600 | 3,000 |
| SUNLU TPU 95A | 0.4 mm | 0.20 mm | 1,000 | 500 | 600 | 1,000 | 1,000 | 800 | 600 | 600 | 3,000 |
| SUNLU TPU 95A | 0.4 mm | 0.24 mm | 1,000 | 500 | 600 | 1,000 | 1,000 | 800 | 600 | 600 | 3,000 |
| SUNLU TPU 95A | 0.8 mm | 0.20 mm | 1,000 | 500 | 600 | 900 | 1,000 | 800 | 600 | 500 | 2,500 |
| SUNLU TPU 95A | 0.8 mm | 0.40 mm | 800 | 400 | 500 | 700 | 800 | 600 | 500 | 400 | 2,200 |
| SUNLU PETG Black Standard | 0.4 mm | 0.12 mm | 2,500 | 500 | 900 | 2,000 | 2,500 | 1,800 | 800 | 1,000 | 5,000 |
| SUNLU PETG Black Standard | 0.4 mm | 0.20 mm | 3,000 | 500 | 1,200 | 2,500 | 3,000 | 2,000 | 1,000 | 1,200 | 6,000 |
| SUNLU PETG Black Standard | 0.4 mm | 0.24 mm | 2,800 | 500 | 1,100 | 2,300 | 2,800 | 2,000 | 1,000 | 1,200 | 5,500 |
| SUNLU PETG Black Standard | 0.8 mm | 0.20 mm | 2,500 | 500 | 900 | 2,000 | 2,500 | 1,800 | 800 | 1,000 | 5,000 |
| SUNLU PETG Black Standard | 0.8 mm | 0.40 mm | 2,000 | 500 | 800 | 1,600 | 2,000 | 1,500 | 700 | 800 | 4,500 |
| ELEGOO Rapid PETG | 0.4 mm | 0.12 mm | 2,500 | 500 | 900 | 2,000 | 2,500 | 1,800 | 800 | 1,000 | 5,000 |
| ELEGOO Rapid PETG | 0.4 mm | 0.20 mm | 3,000 | 500 | 1,200 | 2,500 | 3,000 | 2,000 | 1,000 | 1,200 | 6,000 |
| ELEGOO Rapid PETG | 0.4 mm | 0.24 mm | 2,800 | 500 | 1,100 | 2,300 | 2,800 | 2,000 | 1,000 | 1,200 | 5,500 |
| ELEGOO Rapid PETG | 0.8 mm | 0.20 mm | 2,500 | 500 | 900 | 2,000 | 2,500 | 1,800 | 800 | 1,000 | 5,000 |
| ELEGOO Rapid PETG | 0.8 mm | 0.40 mm | 2,000 | 500 | 800 | 1,600 | 2,000 | 1,500 | 700 | 800 | 4,500 |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.12 mm | 4,500 | 500 | 1,500 | 3,500 | 4,500 | 3,000 | 1,000 | 2,000 | 8,000 |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.20 mm | 5,000 | 500 | 2,000 | 4,000 | 5,000 | 3,500 | 1,000 | 2,500 | 8,000 |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.24 mm | 4,500 | 500 | 1,800 | 3,800 | 4,500 | 3,300 | 1,000 | 2,300 | 7,500 |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.20 mm | 4,000 | 500 | 1,500 | 3,200 | 4,000 | 2,800 | 900 | 1,800 | 7,000 |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.40 mm | 3,200 | 500 | 1,200 | 2,600 | 3,200 | 2,300 | 800 | 1,500 | 6,500 |
| EONO Silk PLA Red-Gold-Blue | 0.4 mm | 0.12 mm | 2,500 | 500 | 1,000 | 2,000 | 2,500 | 1,800 | 800 | 1,000 | 5,000 |
| EONO Silk PLA Red-Gold-Blue | 0.4 mm | 0.20 mm | 3,000 | 500 | 1,200 | 2,400 | 3,000 | 2,200 | 900 | 1,200 | 6,000 |
| EONO Silk PLA Red-Gold-Blue | 0.4 mm | 0.24 mm | 2,800 | 500 | 1,100 | 2,200 | 2,800 | 2,000 | 900 | 1,100 | 5,500 |
| EONO Silk PLA Red-Gold-Blue | 0.8 mm | 0.20 mm | 2,500 | 500 | 900 | 1,800 | 2,500 | 1,800 | 800 | 900 | 5,000 |
| EONO Silk PLA Red-Gold-Blue | 0.8 mm | 0.40 mm | 2,000 | 500 | 800 | 1,500 | 2,000 | 1,500 | 700 | 800 | 4,500 |
| GRATKIT Silk PLA Blue-Purple-Black | 0.4 mm | 0.12 mm | 2,500 | 500 | 1,000 | 2,000 | 2,500 | 1,800 | 800 | 1,000 | 5,000 |
| GRATKIT Silk PLA Blue-Purple-Black | 0.4 mm | 0.20 mm | 3,000 | 500 | 1,200 | 2,400 | 3,000 | 2,200 | 900 | 1,200 | 6,000 |
| GRATKIT Silk PLA Blue-Purple-Black | 0.4 mm | 0.24 mm | 2,800 | 500 | 1,100 | 2,200 | 2,800 | 2,000 | 900 | 1,100 | 5,500 |
| GRATKIT Silk PLA Blue-Purple-Black | 0.8 mm | 0.20 mm | 2,500 | 500 | 900 | 1,800 | 2,500 | 1,800 | 800 | 900 | 5,000 |
| GRATKIT Silk PLA Blue-Purple-Black | 0.8 mm | 0.40 mm | 2,000 | 500 | 800 | 1,500 | 2,000 | 1,500 | 700 | 800 | 4,500 |

Acceleration values are in `mm/s^2`. Lower outer/top acceleration is intentional on the Max's large moving bed.

## Quality And Line Width

| Filament | Nozzle | Layer height | Initial layer height | Default line width | Outer wall | Inner wall | Sparse infill | Internal solid infill | Top surface | Initial layer width | Walls printing order | Print infill first | Seam position |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| GEEETECH TPU 95A | 0.4 mm | 0.12 mm | 0.20 mm | 0.42 | 0.40 | 0.42 | 0.45 | 0.42 | 0.40 | 0.50 | Inner/Outer | Off | Aligned |
| GEEETECH TPU 95A | 0.4 mm | 0.20 mm | 0.20 mm | 0.45 | 0.42 | 0.45 | 0.45 | 0.45 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| GEEETECH TPU 95A | 0.4 mm | 0.24 mm | 0.24 mm | 0.45 | 0.42 | 0.45 | 0.45 | 0.45 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| GEEETECH TPU 95A | 0.8 mm | 0.20 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| GEEETECH TPU 95A | 0.8 mm | 0.40 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| SUNLU TPU 95A | 0.4 mm | 0.12 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU TPU 95A | 0.4 mm | 0.20 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU TPU 95A | 0.4 mm | 0.24 mm | 0.24 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU TPU 95A | 0.8 mm | 0.20 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| SUNLU TPU 95A | 0.8 mm | 0.40 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| SUNLU PETG Black Standard | 0.4 mm | 0.12 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU PETG Black Standard | 0.4 mm | 0.20 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU PETG Black Standard | 0.4 mm | 0.24 mm | 0.24 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU PETG Black Standard | 0.8 mm | 0.20 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| SUNLU PETG Black Standard | 0.8 mm | 0.40 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| ELEGOO Rapid PETG | 0.4 mm | 0.12 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| ELEGOO Rapid PETG | 0.4 mm | 0.20 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| ELEGOO Rapid PETG | 0.4 mm | 0.24 mm | 0.24 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| ELEGOO Rapid PETG | 0.8 mm | 0.20 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| ELEGOO Rapid PETG | 0.8 mm | 0.40 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.12 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.20 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.24 mm | 0.24 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.20 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.40 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| EONO Silk PLA Red-Gold-Blue | 0.4 mm | 0.12 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| EONO Silk PLA Red-Gold-Blue | 0.4 mm | 0.20 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| EONO Silk PLA Red-Gold-Blue | 0.4 mm | 0.24 mm | 0.24 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| EONO Silk PLA Red-Gold-Blue | 0.8 mm | 0.20 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| EONO Silk PLA Red-Gold-Blue | 0.8 mm | 0.40 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| GRATKIT Silk PLA Blue-Purple-Black | 0.4 mm | 0.12 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| GRATKIT Silk PLA Blue-Purple-Black | 0.4 mm | 0.20 mm | 0.20 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| GRATKIT Silk PLA Blue-Purple-Black | 0.4 mm | 0.24 mm | 0.24 mm | 0.42 | 0.42 | 0.45 | 0.45 | 0.42 | 0.42 | 0.50 | Inner/Outer | Off | Aligned |
| GRATKIT Silk PLA Blue-Purple-Black | 0.8 mm | 0.20 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |
| GRATKIT Silk PLA Blue-Purple-Black | 0.8 mm | 0.40 mm | 0.40 mm | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | 0.82 | Inner/Outer | Off | Aligned |

Line-width values are in `mm`. The 0.8 mm values match the pinned Orca Max 0.8 process geometry. Paint or rotate the aligned seam onto a hidden edge per model; seam painting is not a reusable preset field.

## Variable Layer Height

One selected object can use different layer heights along Z, allowing fine layers on shallow slopes and curved regions and coarse layers on simple regions. In `Prepare`, select the model and open `Variable layer height` from the object toolbar. `Adaptive` generates a profile from object geometry; the `Quality / Speed` control biases it toward finer or coarser layers. `Smooth` applies a Gaussian transition filter, and manual editing uses the vertical profile bar. This is a per-object geometry tool, not a filament setting and not a local XY-region setting. Every feature in that object at a given Z shares the resulting layer plane.

The configured machine limits, rather than nozzle diameter alone, constrain the adaptive tool. Orca's generic 20-80% guideline gives 0.08-0.32 mm for a 0.4 mm nozzle and 0.16-0.64 mm for a 0.8 mm nozzle, but those are not the Kobra 3 Max profile values. The exact pinned Max profiles are more conservative:

| Nozzle | Orca generic guideline | Kobra 3 Max configured adaptive range | Referenced fixed process heights | Recommended first working window |
|---:|---:|---:|---|---:|
| 0.4 mm | 0.08-0.32 mm | **0.08-0.28 mm** | 0.08, 0.12, 0.16, 0.20, 0.24, 0.28 mm in the source bundle; this guide provides 0.12/0.20/0.24 | **0.12-0.24 mm** |
| 0.8 mm | 0.16-0.64 mm | **0.16-0.56 mm** | 0.20, 0.24, 0.32, 0.40, 0.48 mm in the referenced Orca bundle; this guide provides 0.20/0.40 | **0.20-0.40 mm** |

The configured endpoints are technical profile bounds, not universal quality recommendations. Do not raise the machine limits just to obtain more adaptive range. Layers near 20% of nozzle diameter can show low-flow inconsistency and greatly increase layer count; coarse layers reduce overhang support and may become MVS-limited. The first layer remains controlled by `Initial layer height` and should stay at the value in the selected process.

### Choose And Enforce A Window

Select a window by intersection, not by choosing only one table: start with the configured machine range, intersect it with the material range, then intersect that result with the object-type range. Use the highest of the three minima and the lowest of the three maxima. For example, a detailed GEEETECH TPU object with a 0.8 mm nozzle resolves to `0.24-0.28 mm`; a large simple GRATKIT Silk object resolves to `0.32-0.40 mm`.

`Adaptive` normally uses the full Min/Max range of the active printer preset; the Quality/Speed slider does **not** enforce the practical windows below. Do not edit the stock printer preset. To enforce a reusable window, duplicate the exact nozzle-specific printer preset, save it with a clear name such as `Anycubic Kobra 3 Max 0.8 nozzle - VLH 0.24-0.32`, and narrow `Printer > Extruder 1 > Layer height limits > Min/Max`. Then duplicate the nearest process as a separate `VLH` process and set its nominal `Process > Quality > Layer height` **inside** that window, for example 0.28 mm for a 0.24-0.32 mm range; Slicer Next can reset an ordinary process height that falls outside the printer range. The separately configured Initial layer height may remain 0.40 mm for the 0.8 nozzle. Ensure the VLH process and filament remain compatible with the saved printer name. Alternatively, keep the stock preset, run Adaptive, manually constrain the vertical profile, and verify the actual minimum and maximum in Preview before printing; this is less repeatable. `Keep min` can preserve layers below the intended material floor if the machine bounds were not narrowed first.

Current Orca and Slicer Next reject slicing when a genuinely variable custom layer profile is combined with Organic/default tree supports. Before applying VLH, disable supports or choose Normal support or a non-Organic tree style such as Slim, Strong, or Hybrid. The common inherited combination `tree(auto)` plus `default` style counts as Organic and will fail validation.

### Adaptive Controls

| Goal | Suggested VLH nominal layer | Quality / Speed start | Smooth radius | Keep min | Review before printing |
|---|---|---|---:|---|---|
| Maximum Z detail | Lower third of the chosen intersection; always inside printer Min/Max | First third toward Quality; approximately 0.20-0.40 if numeric | 3-5 | On for the smoothing pass | Thin features, small islands, supports, total layer count |
| Balanced quality and time | Midpoint of the chosen intersection; always inside printer Min/Max | Near center; approximately 0.45-0.60 if numeric | 3-5 | On for the smoothing pass | Curves, overhangs, flow, speed, transition bands |
| Large simple object | Middle or upper third of the chosen intersection; always inside printer Min/Max | Speed-side two-thirds; approximately 0.65-0.80 if numeric | 5-7 | On, then manually coarsen simple spans | MVS slowdowns, wall texture, top/bottom thickness |

Radius is a profile-sample radius, not millimetres. A larger value spreads transitions over more layers. `Keep min` prevents smoothing from erasing already selected fine/detail regions. For manual edits, left-click makes an area finer, right-click makes it coarser, Shift+left resets toward the base height, Shift+right smooths, and the mouse wheel changes the edit width. Start with `Adaptive`, smooth once, then use manual edits only where the preview still shows obvious stepping or an unnecessarily fine vertical span.

### Practical Windows By Material

These are derived working windows inside the machine limits, not manufacturer presets. The Slicer tool itself is filament-agnostic, but flow stability, cooling, feed path, surface sheen, and layer adhesion are not.

| Material | 0.4 mm practical min-max | 0.8 mm practical min-max | Material-specific use of the endpoints |
|---|---:|---:|---|
| GEEETECH TPU 95A | **0.16-0.24 mm**; 0.12 experimental | **0.24-0.40 mm** | Prefer 0.16-0.20 and 0.24-0.32 for reliable flexible parts. Use 0.12 only with the 1.6 mm^3/s detail cap; use 0.40 only on simple thick regions. |
| SUNLU TPU 95A | **0.16-0.24 mm**; 0.12 experimental | **0.24-0.40 mm** | Thin layers multiply feed/retraction opportunities. Cyclic-flex parts favor no more than 0.32 mm with the 0.8 nozzle. |
| SUNLU PETG Black | **0.12-0.28 mm** | **0.20-0.48 mm** | Use 0.28/0.48 only on simple or near-vertical regions. Refine undersides, hole roofs, and overhangs because PETG is prone to sag and stringing. |
| ELEGOO Rapid PETG | **0.12-0.28 mm** | **0.20-0.48 mm** | Use 0.28/0.48 only after nozzle-material-specific MVS and layer-strength tests. Refine overhangs and hole roofs; Rapid flow does not remove PETG sag. |
| SUNLU High Speed PLA+ 2.0 | **0.12-0.28 mm** | **0.20-0.48 mm** | Best candidate for the coarse speed endpoints, but only after nozzle-specific MVS calibration; high material speed does not remove overhang limits. |
| EONO Silk PLA Red-Gold-Blue | **0.12-0.24 mm** | **0.20-0.40 mm** | Prefer a fixed or narrow band on uninterrupted showcase surfaces because height transitions can appear as sheen bands. No first-party EONO TDS was found. |
| GRATKIT Silk PLA Blue-Purple-Black | **0.12-0.24 mm** | **0.20-0.40 mm** | Prefer a fixed or narrow band for uniform gloss. GRATKIT warns that excessive speed removes the Silk texture; 0.48 mm remains experimental. |

### Windows By Object Type

| Object type | 0.4 mm recommended min-max | 0.8 mm recommended min-max | Selection guidance |
|---|---:|---:|---|
| Detailed figurines and organic curves | **0.12-0.18 mm** | **0.20-0.28 mm** | Use finer layers on heads, backs, shoulders, chins, ears, arches, and shallow slopes. Prefer the 0.4 nozzle for small faces, text, fingers, and accessories because variable height improves Z resolution, not the 0.8 nozzle's XY bead width. |
| General decorative models | **0.16-0.24 mm** | **0.24-0.32 mm** | Good default adaptive window. Coarsen low-curvature vertical spans, but inspect layer-line texture, seams, embedded detail, and transition bands. |
| Mechanical, fitted, threaded, or dimensional parts | **0.16-0.20 mm** | **0.20-0.32 mm** | Keep bores, threads, snap fits, bearing shoulders, mating Z faces, and bridge roofs in a fixed fine height range. Validate dimensions with a coupon. |
| Large simple boxes, organizers, brackets, and near-vertical shells | **0.20-0.28 mm** | **0.32-0.48 mm** | Best speed case. Refine fillets, chamfers, top curves, hole roofs, steep overhangs, and support contacts; tall Max prints still need conservative outer-wall acceleration. |
| Vases and lampshades | **0.20-0.28 mm** | **0.32-0.48 mm** | Broad speed range for ordinary PLA/PETG. Use a narrow or fixed range for Silk to avoid optical bands, and include the actual wide vase line in the MVS calculation. |
| Flexible TPU seals, bumpers, sleeves, and wearables | **0.16-0.24 mm** | **0.24-0.32 mm**; 0.40 simple only | Avoid extreme minima, supports, and frequent layer changes. Choose layer height and wall count together because thicker layers and extra walls alter flexibility and fatigue behavior. |

Perfectly vertical, featureless walls gain little Z-contour accuracy from thin layers, so adaptive slicing often makes them coarser. They are not quality-neutral: layer texture, sheen, seams, small openings, and transitions can still change. Bridges also remain governed by bridge flow, speed, and cooling; variable layer height is not a substitute for bridge calibration.

### Flow And Shell Safeguards

The active filament MVS still applies at every local height. Approximate screening uses `flow = line width x actual layer height x speed`; therefore a thicker adaptive layer may force the slicer to reduce speed. This is especially important for TPU: coarse layers reduce layer count, but they may not reduce extrusion time proportionally when the job is already flow-limited. Always inspect `Preview > Volumetric flow rate (mm³/s)` and `Preview > Speed` instead of assuming the Speed side of the adaptive slider produced the expected time saving.

The fixed-height profiles below intentionally set top/bottom minimum thickness to `0 mm` so their listed layer counts are authoritative. That is unsafe to assume for a variable-height job because four generated layers can represent very different physical thicknesses. Save a separate `VLH` process copy and set physical minimums before applying the tool:

| Object goal | 0.4 mm top/bottom minimum | 0.8 mm top/bottom minimum |
|---|---:|---:|
| Figurine or decorative shell | 0.8-1.0 mm | 1.0-1.2 mm |
| Mechanical shell print-quality start, not a structural rating | 1.0-1.2 mm | 1.2-1.6 mm |
| Large simple part | 1.0-1.2 mm | 1.2-1.6 mm |
| Vase mode | Top layers 0; start with 4-5 bottom layers and verify their summed 0.8-1.2 mm | Top layers 0; start with 3-4 bottom layers and verify their summed 1.2-1.6 mm |
| Flexible TPU part | 0.8-1.0 mm, adjusted for desired flex | 1.0-1.2 mm, adjusted for desired flex |

In vase mode, `Bottom shell layers` is the actionable control; the Bottom shell thickness field is disabled and cannot independently add enough layers. Sum the actual first N heights in Preview. For mechanical or structural parts, the table values are print-quality starting points only; load case, orientation, wall design, material condition, creep/fatigue behavior, and physical testing determine safety.

After slicing, complete one final VLH check: confirm the actual minimum/maximum in `Layer height`, ensure `Volumetric flow rate (mm³/s)` remains below MVS, inspect Speed and compare estimated time with the fixed-height slice, check overhangs/bridges/support contacts, confirm thin walls remain, and verify top closure plus physical top/bottom thickness. Use a Height Range Modifier when a specific Z band must stay at a fixed layer height; an ordinary modifier mesh does not create independent XY-local layer planes.

## Strength

For every **fixed-height** custom process below, explicitly set `Top shell thickness = 0 mm` and `Bottom shell thickness = 0 mm`. This does not apply to the separate `VLH` process copies described above, which require physical shell-thickness safeguards. For fixed-height profiles, zero makes the listed layer counts authoritative; otherwise an inherited 1 mm minimum can turn four 0.24 mm top layers into five.

| Filament | Nozzle | Layer | Wall loops | Top shell layers | Bottom shell layers | Sparse infill density | Sparse infill pattern |
|---|---:|---:|---:|---:|---:|---:|---|
| GEEETECH TPU 95A | 0.4 mm | 0.12 mm | 3 | 8 | 7 | 15% | Gyroid |
| GEEETECH TPU 95A | 0.4 mm | 0.20 mm | 3 | 5 | 4 | 15% | Gyroid |
| GEEETECH TPU 95A | 0.4 mm | 0.24 mm | 3 | 4 | 4 | 15% | Gyroid |
| GEEETECH TPU 95A | 0.8 mm | 0.20 mm | 2 | 5 | 4 | 15% | Gyroid |
| GEEETECH TPU 95A | 0.8 mm | 0.40 mm | 2 | 3 | 3 | 15% | Gyroid |
| SUNLU TPU 95A | 0.4 mm | 0.12 mm | 3 | 8 | 7 | 15% | Gyroid |
| SUNLU TPU 95A | 0.4 mm | 0.20 mm | 3 | 5 | 4 | 15% | Gyroid |
| SUNLU TPU 95A | 0.4 mm | 0.24 mm | 3 | 4 | 4 | 15% | Gyroid |
| SUNLU TPU 95A | 0.8 mm | 0.20 mm | 2 | 5 | 4 | 15% | Gyroid |
| SUNLU TPU 95A | 0.8 mm | 0.40 mm | 2 | 3 | 3 | 15% | Gyroid |
| SUNLU PETG Black Standard | 0.4 mm | 0.12 mm | 3 | 8 | 7 | 15% | Gyroid |
| SUNLU PETG Black Standard | 0.4 mm | 0.20 mm | 3 | 5 | 4 | 15% | Gyroid |
| SUNLU PETG Black Standard | 0.4 mm | 0.24 mm | 3 | 4 | 4 | 15% | Gyroid |
| SUNLU PETG Black Standard | 0.8 mm | 0.20 mm | 2 | 5 | 4 | 15% | Gyroid |
| SUNLU PETG Black Standard | 0.8 mm | 0.40 mm | 2 | 3 | 3 | 15% | Gyroid |
| ELEGOO Rapid PETG | 0.4 mm | 0.12 mm | 3 | 8 | 7 | 15% | Gyroid |
| ELEGOO Rapid PETG | 0.4 mm | 0.20 mm | 3 | 5 | 4 | 15% | Gyroid |
| ELEGOO Rapid PETG | 0.4 mm | 0.24 mm | 3 | 4 | 4 | 15% | Gyroid |
| ELEGOO Rapid PETG | 0.8 mm | 0.20 mm | 2 | 5 | 4 | 15% | Gyroid |
| ELEGOO Rapid PETG | 0.8 mm | 0.40 mm | 2 | 3 | 3 | 15% | Gyroid |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.12 mm | 3 | 7 | 7 | 15% | Gyroid |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.20 mm | 3 | 5 | 4 | 15% | Gyroid |
| SUNLU High Speed PLA+ 2.0 | 0.4 mm | 0.24 mm | 3 | 4 | 4 | 15% | Gyroid |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.20 mm | 2 | 5 | 4 | 15% | Gyroid |
| SUNLU High Speed PLA+ 2.0 | 0.8 mm | 0.40 mm | 2 | 3 | 3 | 15% | Gyroid |
| EONO Silk PLA Red-Gold-Blue | 0.4 mm | 0.12 mm | 3 | 7 | 7 | 15% | Gyroid |
| EONO Silk PLA Red-Gold-Blue | 0.4 mm | 0.20 mm | 3 | 5 | 4 | 15% | Gyroid |
| EONO Silk PLA Red-Gold-Blue | 0.4 mm | 0.24 mm | 3 | 4 | 4 | 15% | Gyroid |
| EONO Silk PLA Red-Gold-Blue | 0.8 mm | 0.20 mm | 2 | 5 | 4 | 15% | Gyroid |
| EONO Silk PLA Red-Gold-Blue | 0.8 mm | 0.40 mm | 2 | 3 | 3 | 15% | Gyroid |
| GRATKIT Silk PLA Blue-Purple-Black | 0.4 mm | 0.12 mm | 3 | 7 | 7 | 15% | Gyroid |
| GRATKIT Silk PLA Blue-Purple-Black | 0.4 mm | 0.20 mm | 3 | 5 | 4 | 15% | Gyroid |
| GRATKIT Silk PLA Blue-Purple-Black | 0.4 mm | 0.24 mm | 3 | 4 | 4 | 15% | Gyroid |
| GRATKIT Silk PLA Blue-Purple-Black | 0.8 mm | 0.20 mm | 2 | 5 | 4 | 15% | Gyroid |
| GRATKIT Silk PLA Blue-Purple-Black | 0.8 mm | 0.40 mm | 2 | 3 | 3 | 15% | Gyroid |

Use more walls, not just more infill, when strength is the priority. Two 0.82 mm walls are already about 1.64 mm thick; add a third only when the model needs it. Extra walls and infill make TPU parts less flexible. Avoid TPU supports where possible; they are difficult to remove.

## What Owners Reported

| Material | Online experience | How it changed this profile |
|---|---|---|
| GEEETECH TPU 95A | A Kobra 3 owner completed two long prints, then repeatedly had GEEETECH 95A wrap around the extruder rollers. Retract-heavy small geometry was worse; slower speed and slicer changes did not reliably cure it. [Forum thread](https://forum.drucktipps3d.de/forum/thread/39344-kobra-3-tpu-problem-im-extruder/) | Conservative 20-25 mm/s extrusion, short top feed, clean hotend, wipe off, no layer-change retract, and a stop-and-inspect rule for clicking. |
| GEEETECH TPU 95A | In a Kobra 3 Max discussion, one commenter reported 25 mm/s and clogging above it on a smaller Kobra 3; nozzle diameter, layer height, and line width were not stated. Other owners recommended a roughly six-inch top-fed tube. [Reddit](https://old.reddit.com/r/AnycubicOfficial/comments/1k4n3ou/any_tips_on_printing_tpu_on_anycubic_kobra_3_max/) | Supports a short feed path and a cautious linear-speed start, but does not establish Max-specific or nozzle-specific MVS. |
| SUNLU TPU 95A | An X1C owner improved stringing with 200 deg C, flow 1.0, 4.5 mm^3/s, 0.8 mm at 25 mm/s retraction, 30-50% fan, and 100% bridge fan. [Bambu forum](https://forum.bambulab.com/t/settings-for-sunlu-tpu/34584) | Supports moderate temperature, short retraction, and localized high bridge cooling. The Max profile remains slower and lower-flow. |
| SUNLU TPU 95A | An A1 owner found 50 deg C for 6 hours insufficient; 65 deg C for 12 hours improved wet-filament symptoms. [Reddit](https://old.reddit.com/r/FixMyPrint/comments/1uw2spm/issues_printing_tpu_honeycomb/) | The recommended 55 deg C for 8-12 hours is a conservative derived compromise; use a calibrated dryer and let the spool cool before feeding. |
| SUNLU TPU 95A | A Qidi owner found reducing MVS only delayed failure; removing the PTFE tube enabled a 13-hour print. [Reddit](https://old.reddit.com/r/QidiTech3D/comments/1jzpg5s/q1_pro_tpu_issue_filament_feeding/) | Feed drag must be fixed before treating the problem as a nozzle or speed issue. |
| SUNLU PETG Black | A direct color-match owner used 250 deg C first layer and 245 deg C later, with fan mostly off except for overhangs. [Bambu forum](https://forum.bambulab.com/t/best-settings-for-sunlu-petg/33776?page=2#post_35) | Supports 245-250 deg C and moderate normal cooling rather than full fan. |
| PETG on Kobra 3 | An owner reported nearly flawless output at 250/100 deg C for two layers, then 240/80 deg C and 80 mm/s; later users reported improvement. [Reddit](https://old.reddit.com/r/anycubic/comments/1exjpt8/petg_on_kobra_3/) | Confirms slower first layers and a warm bed, but 100 deg C is not used as a general default. |
| ELEGOO Rapid PETG | Exact first-party profiles use 250 deg C, 70 deg C bed, 30-80% normal fan, 90% overhang fan, density 1.26, and MVS values from 10 to 34 mm^3/s depending on printer; the generic Orca profile uses flow 0.99 and 18 mm^3/s. Owner reports reached higher flow on other hotends but also reported overhang globbing with insufficient fan. [Bambu owner thread](https://forum.bambulab.com/t/elegoo-rapid-petg-filament/48209) and [cooling report](https://forum.bambulab.com/t/elegoo-petg-rapid-suggestions/96245?page=3) | Uses 250 deg C and localized 90% fan, but conservative Kobra MVS starts of 10/12 mm^3/s, derived flow-ratio starts of 0.95/0.97, and PA disabled initially rather than copying another hotend's 18-24 mm^3/s result. |
| SUNLU High Speed PLA+ 2.0 | An exact-product owner at 450 mm/s reported slight stringing, visible VFAs, about 5% worse finish, and only about 35% shorter print time. [Reddit](https://www.reddit.com/r/3Dprinting/comments/1m1w03t/favorite_brand_of_filament/n3l70c2/) | Keeps visible walls at 100-120 mm/s; internal features use 180-200 mm/s at 0.20 mm and up to 230 mm/s at 0.12 mm. |
| EONO Silk PLA Red/Gold/Blue | Exact-color Amazon reviews report clean printing and layer bonding at 205-215 deg C with a 60 deg C bed, but another long-print review reports tangling after about 100 m. [Exact listing and reviews](https://www.amazon.de/dp/B0B8YX4Y95?language=de_DE) | Uses a moderate 210-215 deg C profile, conservative 8 mm^3/s MVS, and an inspect-or-respool rule before unattended long prints. |
| GRATKIT Silk PLA Blue/Purple/Black | A same-family Red/Gold/Purple owner/forum report linked visible lines to flow, retraction, filament twist, and inconsistent coextrusion orientation; the poster was not verified as official GRATKIT support and the colorway differs. [Owner/forum thread](https://forums.gratkit.com/d/65-tri-colour-silk-pla-lines) | Keeps Kobra retraction instead of the aggressive generic 2 mm recommendation, caps initial flow at 10 mm^3/s, and requires an orientation sample. |

## Calibration Order

| Step | Action | Keep or change the table value when... |
|---:|---|---|
| 0 | After fitting any different nozzle diameter or material, select the matching printer/filament preset, rerun leveling, verify Z offset with a first-layer patch, and run PID calibration if the printer/firmware supports or requires it. | The slicer reports the wrong nozzle diameter/material commissioning preset or an 0.8 initial-layer width other than 0.82 mm: stop and correct the preset before calibration. |
| 1 | Dry the spool and use the intended feed path. | Popping, bubbles, roughness, or fine stringing remain: dry again before tuning retraction. |
| 2 | Verify the first layer and bed cleanliness. | Large PETG parts lift: preheat longer, use 5-8 mm brim/mouse ears, then raise bed by 5 deg C if needed. |
| 3 | Run a temperature tower at representative flow after a 5-minute heat soak. Start steel at the brass temperature; test the listed `+5 deg C` fallback only if needed. | High-flow lines look matte/weak: try the allowed fallback. Excess gloss, ooze, changed Silk sheen, or heat creep: restore the brass temperature and lower MVS. |
| 4 | Calibrate flow ratio separately for each nozzle/material pair. | Change in 0.01 steps. Do not use flow to hide a partial clog or TPU feed drag. |
| 5 | Calibrate PA separately for each nozzle/material pair; only after stable TPU extrusion for TPU. | Corners bulge: PA may be low. Thin corners or gaps after direction changes: PA may be high. |
| 6 | Run maximum volumetric-flow calibration separately for every nozzle/material pair. | Set MVS 10-20% below the first repeatable roughness, gloss transition, under-extrusion, or layer-strength failure; after increasing MVS, revalidate PA at representative flow. |
| 7 | Tune retraction last. | TPU clicking/wrapping: set retraction to 0 before increasing it. Rigid-filament stringing after drying: adjust by 0.1 mm. |
| 8 | For tri-color Silk PLA, print a small vase-mode orientation cylinder and inspect spool feed. | Rotate the final model around Z to choose color-facing; respool or direct-feed if winding or brittleness is inconsistent. |
| 9 | Print a dimensional coupon. | Apply XY/hole compensation only from measured error, not another printer's profile. |

## Failure Corrections

| Symptom | First correction |
|---|---|
| TPU wraps around gears or extruder clicks | Stop immediately. Set retraction to 0, keep wipe and z-hop off, shorten the feed path, inspect idler pressure, and purge/clean the nozzle. For GEEETECH, reduce to 20 mm/s and 1.8 mm^3/s MVS. |
| TPU prints air after several hours | Check spool/tube drag and hotend residue. Do not assume a true nozzle clog. Let a warm spool cool before feeding if the drive wheel slips. |
| TPU strings | Dry again, avoid crossing walls, then lower nozzle 5 deg C. Increase retraction only after extrusion is mechanically reliable. |
| PETG strings or blobs | Dry, lower nozzle 5 deg C, verify flow, then test 0.9-1.0 mm retraction. |
| Standard PETG weak or matte at speed | Raise nozzle 5 deg C within the product range or reduce MVS from 10 to 8 mm^3/s; reduce normal fan by 10 percentage points. |
| ELEGOO Rapid PETG weak or matte at speed | Reduce MVS by 15-20%; then test 5 deg C hotter and 10 percentage points less normal fan. Unlock 14/16 mm^3/s only after a measured failure point of at least 16.5/18.8 mm^3/s. |
| PETG damages or locks to PEI | Lower first-layer nozzle/bed by 5 deg C, add a thin glue release layer, and wait for full cooling. |
| PLA+ rough/matte high-speed infill | Reduce MVS from 18 to 16 mm^3/s before lowering every feature speed. |
| PLA+ ringing or VFAs | Reduce outer wall to 80-100 mm/s and outer acceleration to 1,200-1,500 mm/s^2. |
| Silk PLA looks dull or loses color separation | Reduce outer-wall speed first; then raise nozzle temperature by 5 deg C only within that material's documented range. Do not exceed GRATKIT's 215 deg C all-metal-hotend ceiling. GRATKIT explicitly warns that high speed removes the silk texture. |
| Silk PLA snaps, binds, or forms unexplained vertical color lines | Inspect the cardboard spool and coextrusion orientation, dry only at the conservative material-specific cycle, test direct feeding, and replace or respool a crossed or inconsistently oriented roll. |
| Poor top surface | Lower top speed by 15-20 mm/s or add one top layer after flow is calibrated. |
| 0.8 mm profile under-extrudes | Confirm the 0.8 mm printer preset and 0.82 mm line widths, then lower MVS by 15%, inspect the nozzle/hotend, and run a temperature tower. Do not compensate by increasing flow ratio. |
| Steel nozzle under-extrudes versus brass | Verify identical geometry, installation, bore cleanliness, heat soak, and correct steel commissioning preset. Test the listed +5 deg C fallback, then lower MVS; do not assume conductivity ratios predict the correction. |
| 0.8 mm first layer is over-squished or detached | Recheck nozzle installation, leveling, and Z offset with the 0.40 mm first-layer height before changing bed temperature or flow. |

## Sources And Limits

### Product, Manufacturer, And Marketplace Sources

- [Anycubic Kobra 3 Max specifications](https://www.anycubic.com/products/kobra-3-max)
- [Anycubic Kobra 3 Max Combo specifications](https://www.anycubic.com/products/kobra-3-max-combo), including standard 0.4 mm and expandable 0.6/0.8 mm nozzle support
- [Anycubic Kobra 3 Max TPU guide](https://wiki.anycubic.com/en/fdm-3d-printer/kobra-3-max/tpu-printing-guide)
- [SUNLU TPU 95A product data](https://www.sunlu.com/products/tpu-95a-flexible-filament) and [TDS](https://media.sunlu.com/prod/20260330/e8b9c06a-4b93-46cb-9532-d9deb185a7c8.pdf?filename=TDS)
- [SUNLU standard PETG product data](https://www.sunlu.com/products/petg-3d-printing-filament) and [filament/drying guide](https://www.sunlu.com/wiki/filament-usage-guide)
- [ELEGOO Rapid PETG product data](https://www.elegoo.com/products/rapid-petg-filament-1-75mm-colored-1kg.js), [exact Anycubic Slicer Next ELEGOO base](https://github.com/ANYCUBIC-3D/AnycubicSlicerNext/blob/4f50fdc94ebbc798d57716c031be16f75b70c0a5/resources/profiles/Elegoo/filament/ELEGOO/Elegoo%20RAPID%20PETG%20%40base.json), and [Orca system profile](https://github.com/OrcaSlicer/OrcaSlicer/blob/43a83397d4e4e032edf0fca5258ccd0ab886a7d4/resources/profiles/OrcaFilamentLibrary/filament/Elegoo/Elegoo%20Rapid%20PETG%20%40System.json)
- [SUNLU High Speed PLA+ 2.0 product data](https://store.sunlu.com/products/moq-6kg-high-speed-pla-2-0hspla-plus-2-0-high-speed-3d-printer-filament-1kg) and [TDS](https://media.sunlu.com/prod/20260330/225ab1bc-a40a-435b-8d20-a2745303674b.pdf?filename=TDS)
- [GEEETECH TPU product data](https://www.geeetech.com/products/tpu-3d-printer-filament-1-75mm-1kg-roll), [printing guide](https://blog.geeetech.com/materials/tpu-filament-guide-how-to-print-with-tpu/), and [drying guide](https://blog.geeetech.com/materials/3d-printing-filament/why-tpu-filament-absorbs-moisture-easily-and-how-to-dry-it/)
- [EONO Red/Gold/Blue exact German product listing](https://www.amazon.de/dp/B0B8YX4Y95?language=de_DE); no first-party EONO TDS was found
- [GRATKIT Blue/Purple/Black exact German product listing](https://www.amazon.de/dp/B0BWXQ2WZD?language=en_GB&th=1&psc=1) and [GRATKIT Silk multi-color product data](https://gratkit.com/products/gratkit-silk-multi-color-pla-filament-1-75mm-coextrusion-pla-filament-1kg)
- [Anycubic dual/tri-color Silk PLA proxy data](https://store.anycubic.com/products/silk-pla-dual-tri-color-filament), used only where EONO publishes no exact technical range

### Slicer Behavior And Reference Profiles

- [Anycubic Slicer Next parameter guide](https://wiki.anycubic.com/en/software-and-app/new-page-anycubic-slicer-beta(orca-version)/parameter-settings)
- [Anycubic Slicer Next quick-start guide](https://wiki.anycubic.com/en/software-and-app/new-page-anycubic-slicer-beta%28orca-version%29/anycubic-slicer-next-slicing-software-quick-start-guide), used for the Prepare/object-tool context
- [Orca Variable Layer Height](https://github.com/OrcaSlicer/OrcaSlicer/wiki/prepare_variable_layer_height) and [layer-height guidance](https://github.com/OrcaSlicer/OrcaSlicer/wiki/quality_settings_layer_height), including adaptive/manual behavior and the generic 20-80% nozzle guideline
- [Current Anycubic Slicer Next validation source](https://github.com/ANYCUBIC-3D/AnycubicSlicerNext/blob/6103ed8b511609658d00d0538cc7f0609cdb57da/src/libslic3r/Print.cpp#L1163-L1173), which rejects variable layer height with Organic/default tree support
- [Current Orca Organic-support validation](https://github.com/OrcaSlicer/OrcaSlicer/blob/b422636740623f5513692e103fc8af4433acdbf6/src/libslic3r/Print.cpp#L1455-L1464), which applies the same restriction
- [Current Anycubic Slicer Next vase-mode field behavior](https://github.com/ANYCUBIC-3D/AnycubicSlicerNext/blob/6103ed8b511609658d00d0538cc7f0609cdb57da/src/slic3r/GUI/ConfigManipulation.cpp#L620-L621), which disables top/bottom thickness controls in vase mode
- [Current Anycubic Slicer Next spiral-bottom processing](https://github.com/ANYCUBIC-3D/AnycubicSlicerNext/blob/6103ed8b511609658d00d0538cc7f0609cdb57da/src/libslic3r/PrintObject.cpp#L1276-L1285), which caps the vase base by Bottom shell layers
- [Anycubic Slicer Next v2.3.0 commit `70931e5`](https://github.com/ANYCUBIC-3D/AnycubicSlicerNext/commit/70931e5321fa66966a5bfb251efca0e82307d427), used for field semantics; the repository publishes tags rather than GitHub releases
- [Anycubic Kobra 3 Max 0.4 mm machine profile, pinned commit](https://raw.githubusercontent.com/ANYCUBIC-3D/AnycubicSlicerNext/987a3c2bf9ed13934137326bfd522896c70e5101/resources/profiles/Anycubic/machine/Anycubic%20Kobra%203%20Max%200.4%20nozzle.json)
- [Anycubic Kobra 3 Max 0.20 mm process profile, pinned commit](https://raw.githubusercontent.com/ANYCUBIC-3D/AnycubicSlicerNext/987a3c2bf9ed13934137326bfd522896c70e5101/resources/profiles/Anycubic/process/0.20mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.4%20nozzle.json)
- [Anycubic Kobra 3 Max 0.24 mm / 0.4 mm process profile, pinned commit](https://raw.githubusercontent.com/ANYCUBIC-3D/AnycubicSlicerNext/987a3c2bf9ed13934137326bfd522896c70e5101/resources/profiles/Anycubic/process/0.24mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.4%20nozzle.json)
- [OrcaSlicer Kobra 3 Max merge commit `972dae2`](https://github.com/OrcaSlicer/OrcaSlicer/commit/972dae22afdadc3251d05e10c2d6f00c35e6b83a), a secondary profile reference
- [Orca Kobra 3 Max 0.8 mm machine profile](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/972dae22afdadc3251d05e10c2d6f00c35e6b83a/resources/profiles/Anycubic/machine/Anycubic%20Kobra%203%20Max%200.8%20nozzle.json)
- [Orca Kobra 3 Max 0.20 mm / 0.8 mm process](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/972dae22afdadc3251d05e10c2d6f00c35e6b83a/resources/profiles/Anycubic/process/0.20mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.8%20nozzle.json) and [0.40 mm / 0.8 mm process](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/972dae22afdadc3251d05e10c2d6f00c35e6b83a/resources/profiles/Anycubic/process/0.40mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.8%20nozzle.json)
- [Orca Kobra 3 Max PLA Silk 0.4 mm filament reference](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/972dae22afdadc3251d05e10c2d6f00c35e6b83a/resources/profiles/Anycubic/filament/Anycubic%20PLA%20Silk%20%40Anycubic%20Kobra%203%20Max%200.4%20nozzle.json)
- [Orca Kobra 3 Max generic PLA 0.8 mm filament reference](https://raw.githubusercontent.com/OrcaSlicer/OrcaSlicer/972dae22afdadc3251d05e10c2d6f00c35e6b83a/resources/profiles/Anycubic/filament/Anycubic%20PLA%20%40Anycubic%20Kobra%203%20Max%200.8%20nozzle.json)
- [Orca maximum volumetric-speed calibration](https://github.com/OrcaSlicer/OrcaSlicer/wiki/volumetric_speed_calib) and [pressure-advance calibration](https://github.com/OrcaSlicer/OrcaSlicer/wiki/pressure_advance_calib)

### Nozzle Material And Flow Sources

- [CNC Kitchen controlled hotend flow benchmark](https://www.cnckitchen.com/blog/flow-rate-benchmarking-of-a-hotend), including the finding that its quality hardened-steel V6 nozzle differed noticeably from brass mainly below 200 deg C
- [Prusa E3D V6 nozzle guidance](https://help.prusa3d.com/article/e3d-v6-nozzles_920168) and [under-extrusion troubleshooting](https://help.prusa3d.com/article/under-extrusion_2007), used as conditional steel temperature guidance rather than proof of a universal offset
- [Copper Development Association C36000 brass](https://alloys.copper.org/alloy/C36000), [Alleima 304 stainless](https://www.alleima.com/en/technical-center/material-datasheets/tube-and-pipe-seamless/alleima-3r12/), and [Uddeholm hardened A2/Rigor](https://www.uddeholm.com/en/app/uploads/sites/216/productdb/api/tech_uddeholm-rigor_en.pdf), used only to establish conductivity direction, not to calculate a temperature or MVS correction
- [E3D volumetric-flow guidance](https://e3d-online.com/pages/revo-high-flow-volumetric-flow-rate-calculator), which emphasizes filament, temperature, geometry, and complete-system dependence

### Owner Reports

- The directly retrieved owner evidence used to modify these profiles is linked row-by-row in [What Owners Reported](#what-owners-reported).

The strongest online experience evidence is material- and printer-specific for GEEETECH TPU, but exact SUNLU TPU 95A/Kobra 3 Max and ELEGOO Rapid PETG/Kobra 3 Max evidence is scarce. EONO has no retrieved first-party TDS, and neither requested Silk filament has an exact Kobra 3 Max 0.8 mm profile, so their values remain conservative derived starts. No controlled identical-geometry Kobra comparison was found for brass versus stainless or hardened steel; the steel MVS entries are commissioning policy values and must not be reported as material penalties. Reports from other modern direct-drive printers are therefore labeled as transferable experience rather than proof. Kobra 3 reports also transfer imperfectly to the Max because the Max has a much larger moving bed and lower quality-oriented process acceleration.
