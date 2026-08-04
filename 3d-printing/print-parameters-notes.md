# Research Notes: Kobra 3 Max Filament Profiles

**Research date:** 2026-08-01

## Evidence Rules
- First-party printer, slicer, and filament documentation establishes supported ranges.
- Directly retrieved owner reports may refine practical settings and common failure modes.
- Search snippets are discovery aids only and do not independently establish a recommendation.
- Recommendations must distinguish measured facts, recurring anecdotal experience, and derived starting values.
- Speeds are limited by material flow and feature type, not only the printer's advertised travel speed.

## Printer And Slicer

- Kobra 3 Max: 420 x 420 x 500 mm build volume, stock 0.4 mm nozzle, 300 C hotend limit, 90 C bed limit, 300 mm/s recommended speed, 600 mm/s maximum motion speed, and 10,000 mm/s2 maximum machine acceleration. Anycubic lists the nozzle as replaceable with 0.6 or 0.8 mm.
- The large moving bed makes surface quality more sensitive to acceleration than on the smaller Kobra 3. Max-specific profiles use roughly 5,000 mm/s2 default process acceleration rather than the smaller Kobra 3's 10,000 mm/s2.
- The toolhead uses short-distance extrusion and officially supports TPU 95A or harder. TPU must bypass ACE Pro and use the external spool path.
- Anycubic Slicer Next is based on OrcaSlicer. Material limits belong in the filament preset; feature speed, acceleration, line width, and shell settings belong in the process preset.
- Max volumetric speed is the primary sustained extrusion limit. A nominal 300 or 600 mm/s feature speed is reduced when line width x layer height x speed exceeds the filament MVS cap.
- Max-specific profile sources:
  - Printer: https://raw.githubusercontent.com/ANYCUBIC-3D/AnycubicSlicerNext/987a3c2bf9ed13934137326bfd522896c70e5101/resources/profiles/Anycubic/machine/Anycubic%20Kobra%203%20Max%200.4%20nozzle.json
  - 0.20 process: https://raw.githubusercontent.com/ANYCUBIC-3D/AnycubicSlicerNext/987a3c2bf9ed13934137326bfd522896c70e5101/resources/profiles/Anycubic/process/0.20mm%20Standard%20%40Anycubic%20Kobra%203%20Max%200.4%20nozzle.json
  - Current Orca Max profiles: https://github.com/OrcaSlicer/OrcaSlicer/pull/11586
- The pinned Anycubic bundle provides an exact `0.24mm Standard @Anycubic Kobra 3 Max 0.4 nozzle` process that inherits the 0.20 profile, changes layer and first-layer height to 0.24 mm, and overrides gap infill, inner wall, outer wall, and sparse infill speeds to 150, 150, 140, and 150 mm/s respectively. The material-specific table values replace those generic speeds.
- The pinned Anycubic tree does not contain a Max 0.8 profile. Pinned Orca commit `972dae22afdadc3251d05e10c2d6f00c35e6b83a` does contain an exact `Anycubic Kobra 3 Max 0.8 nozzle` machine profile plus 0.20, 0.24, 0.32, 0.40, and 0.48 mm processes. Its machine profile sets nozzle diameter 0.8 mm, minimum layer height 0.16 mm, and maximum layer height 0.56 mm; its 0.20 and 0.40 processes use a 0.40 mm first layer and 0.82 mm line widths.
- The pinned Orca JSON lacks Slicer Next's required profile-version field and is therefore a settings reference, not a promised import route. Slicer Next may also hide process compatibility editing. The deliverable therefore prefers native 0.8 bases and includes a complete visible-settings fallback from the exact Max 0.4 machine and 0.20 process, plus instructions to expose incompatible presets when dependency metadata cannot be edited.
- Orca states that MVS varies with material, machine, nozzle diameter, and extruder setup. The 0.8 mm recommendations therefore retain each proven 0.4 mm MVS only as a conservative temporary cap, then require nozzle-specific flow, PA, and MVS calibration. The process speeds were checked with `flow = line width x layer height x speed` and do not exceed those temporary caps.
- Slicer field locations: filament temperatures, flow ratio, pressure advance, MVS, and cooling are in the Filament preset; retraction overrides are under Filament > Setting Overrides; feature speeds and acceleration are under Process > Speed; line widths are under Process > Quality; hardware ceilings remain in Printer > Motion ability.

## GEEETECH TPU 95A

- Official GEEETECH ranges: 200-230 C nozzle, 50-60 C bed, 20-30 mm/s main speed, 10-15 mm/s first layer, less than 1 mm retraction at 20-40 mm/s or disabled, 30-50% fan, and 50-60 C drying for 4-6 hours.
- Product: https://www.geeetech.com/products/tpu-3d-printer-filament-1-75mm-1kg-roll
- Printing guide: https://blog.geeetech.com/materials/tpu-filament-guide-how-to-print-with-tpu/
- Drying guide: https://blog.geeetech.com/materials/3d-printing-filament/why-tpu-filament-absorbs-moisture-easily-and-how-to-dry-it/
- Most relevant owner report: https://forum.drucktipps3d.de/forum/thread/39344-kobra-3-tpu-problem-im-extruder/
- The owner initially completed 8-hour and 6-hour prints, then GEEETECH 95A repeatedly escaped between the drive and idler rollers and wrapped around the extruder. Small, retract-heavy geometry was worse. Slowing, changing slicers, and changing retraction did not provide a durable fix. A clean/new hotend produced one provisional success.
- Kobra 3 Max owners also reported about 25 mm/s as a practical reliable ceiling and better results with a short top-fed path: https://old.reddit.com/r/AnycubicOfficial/comments/1k4n3ou/any_tips_on_printing_tpu_on_anycubic_kobra_3_max/
- Derived profile: 225 C, 50/45 C bed, flow 1.00, MVS 2.3 mm3/s at 0.20 and 1.6 mm3/s at 0.12, 0.5 mm retraction at 20 mm/s, wipe off, no layer-change retraction, and modest cooling. The 0.12 profile is experimental because Anycubic recommends 0.16-0.20 mm for TPU.

## SUNLU TPU 95A

- Current official product bands: 190-210 C at 50-80 mm/s or 210-230 C at 80-120 mm/s, 50-60 C bed, 0.8-1.2 mm retraction, and 30-40 mm/s retraction speed.
- Product and TDS: https://www.sunlu.com/products/tpu-95a-flexible-filament and https://media.sunlu.com/prod/20260330/e8b9c06a-4b93-46cb-9532-d9deb185a7c8.pdf?filename=TDS
- Exact-product owner evidence is scarce for the Kobra 3 Max. Comparable direct-drive reports cluster around 205-225 C, 30-50 mm/s, 0-0.8 mm retraction, 30-50% normal fan, 3-4.5 mm3/s MVS, and flow 0.98-1.00.
- Bambu X1C owner profile: 200 C, 50-55 C bed, 4.5 mm3/s, 0.8 mm at 25 mm/s retraction, 30-50% normal fan, and 100% bridge fan: https://forum.bambulab.com/t/settings-for-sunlu-tpu/34584
- Bambu A1 owner found 50 C for 6 hours insufficient; 65 C for 12 hours improved the wet-filament symptoms. The same tuning used about 205 C, flow 0.99, and MVS 4 mm3/s, but an unusually aggressive 2 mm retraction should not be copied to the Kobra: https://old.reddit.com/r/FixMyPrint/comments/1uw2spm/issues_printing_tpu_honeycomb/
- Qidi owner found apparent clogs were feed-path drag; removing the PTFE tube enabled a 13-hour print: https://old.reddit.com/r/QidiTech3D/comments/1jzpg5s/q1_pro_tpu_issue_filament_feeding/
- Derived profile: 215 C first layer, 210 C later, 55/50 C bed, flow 0.98, MVS 3.2 mm3/s, PA 0.020 starting value, 0.8 mm retraction at 30 mm/s, wipe off on the Kobra, and 30-60% normal cooling depending on layer height. The recommended 55 C for 8-12 hours is a conservative compromise between the insufficient 50 C/6 h owner result and the successful but hotter 65 C/12 h cycle; use a calibrated dryer and let the spool cool before feeding.

## SUNLU PETG Black

- Current product-specific range: 240-260 C nozzle, 60-70 C bed, up to 300 mm/s marketing speed, 0.8-1.2 mm retraction, and 30-40 mm/s retraction speed.
- Product: https://www.sunlu.com/products/petg-3d-printing-filament
- SUNLU's generic guide recommends 60-65 C drying for 6-8 hours and 30-50% fan: https://www.sunlu.com/wiki/filament-usage-guide
- Current Anycubic generic PETG baseline uses flow 0.95 and MVS 10 mm3/s. The Max-specific Orca profile uses 0.8 mm retraction and PA 0.04.
- A SUNLU black owner used 250 C first layer and 245 C later with fan mostly off except overhangs: https://forum.bambulab.com/t/best-settings-for-sunlu-petg/33776?page=2#post_35
- Kobra 3 PETG owners reported near-flawless output at 250 C/100 C for two layers, then 240 C/80 C at 80 mm/s; this supports warmer/slower first layers but 100 C is too source-specific for a default: https://old.reddit.com/r/anycubic/comments/1exjpt8/petg_on_kobra_3/
- Kobra-family reports found poor layer adhesion above about 120 mm/s: https://forum.drucktipps3d.de/forum/thread/41778-anycubic-kobra-s1-sammelthread-slicer-profile-und-erkenntnisse/
- Derived profile: 245 C first layer, 250 C later, 75/70 C bed, flow 0.95, MVS 10 mm3/s, PA 0.040, 0.8 mm retraction at 30 mm/s, 35-65% normal fan, and 90-100% only for overhangs/bridges.

## SUNLU PLA+ 2.0 High Speed

- Exact product identity: SUNLU High Speed PLA+ 2.0 / HSPLA Plus 2.0, not ordinary PLA+ 2.0 or the earlier High Speed PLA+ formulation.
- Official speed/temperature bands: 200-215 C at 50-150 mm/s, 215-230 C at 150-300 mm/s, and 230-260 C at 300-600 mm/s. Bed 50-65 C; retraction 0.8-1.2 mm at 30-40 mm/s; dry at 50 C for at least 4 hours.
- Product: https://store.sunlu.com/products/moq-6kg-high-speed-pla-2-0hspla-plus-2-0-high-speed-3d-printer-filament-1kg
- TDS testing used a 0.4 mm nozzle, 0.20 mm layer, 220 C nozzle, 55 C bed, and 100-220 mm/s: https://media.sunlu.com/prod/20260330/225ab1bc-a40a-435b-8d20-a2745303674b.pdf?filename=TDS
- Exact-product owner at 450 mm/s reported slight stringing, visible VFAs, about 5% worse finish, and about 35% less print time: https://www.reddit.com/r/3Dprinting/comments/1m1w03t/favorite_brand_of_filament/n3l70c2/
- Another owner found ordinary PLA+ 2.0 more consistent than the high-speed formulation: https://www.reddit.com/r/3Dprinting/comments/1otfuc0/quality_of_filament_recommendations/no5bcsn/
- The stock Kobra 3 Max high-speed PLA profile uses an 18 mm3/s MVS limit. Using the conservative rectangular check at 0.20 x 0.45 mm gives 200 mm/s before flow-ratio adjustment, far below the 600 mm/s motion claim.
- Derived profile: 220 C, 60/55 C bed, flow 0.97, MVS 18 mm3/s, PA 0.026, 0.8 mm retraction at 35 mm/s, 80-100% cooling, and lower outer/top speeds than infill.

## Derived Profiles

- The deliverable uses 0.12 mm detail, 0.20 mm balanced, and 0.24 mm balanced profiles with the 0.4 mm nozzle. It adds 0.20 mm fine and 0.40 mm draft profiles with the 0.8 mm nozzle.
- The 0.4 mm rigid-filament profiles retain 3 walls, approximately 0.8-1.0 mm top/bottom thickness, aligned hidden seams, 15% gyroid infill, and 0.4 mm slope z-hop. The 0.8 mm variants use 2 walls because they are already about 1.64 mm thick.
- TPU uses 3 walls with the 0.4 mm nozzle and 2 walls with the 0.8 mm nozzle. It keeps gyroid but avoids supports, wipe, multi-object plates, and unnecessary retraction. GEEETECH uses no z-hop initially; SUNLU keeps z-hop optional.
- Feature speed and acceleration are intentionally lower for outer walls and top surfaces. MVS remains the hard sustained extrusion cap.
- The 0.8 mm profiles use the pinned Orca Max reference geometry: 0.82 mm feature widths, a 0.40 mm first layer, and a 0.16-0.56 mm machine layer range. Two walls are already about 1.64 mm thick; 0.20 mm layers use 5/4 top/bottom layers and 0.40 mm layers use 3/3 for roughly 0.8-1.2 mm shell coverage.

## Limitations And Calibration

- These are evidence-based starting profiles, not universal optima. Spool moisture, pigment, ambient temperature, nozzle wear, and firmware/profile revisions change the result.
- Installed Anycubic Slicer Next presets must be checked because public repository and bundled/cloud profiles have differed.
- After every nozzle change, rerun bed leveling/Z offset checks, flow ratio, pressure advance, and MVS. Do not transfer a 0.4 mm PA value to 0.8 mm without validation.
- Calibration order: dry filament, verify first layer, temperature tower, flow ratio, pressure advance for rigid materials and only after stable extrusion for TPU, MVS test, PA recheck at representative flow, retraction, then dimensional coupon.
- Set MVS 10-20% below the first repeatable failure or surface transition in a flow test.
- For TPU, solve feed drag, hotend residue, and gear wrapping before increasing retraction or flow. Do not use ACE Pro for feeding.
