# Research Notes: Kobra 3 Max Filament Profiles

**Research dates:** 2026-08-01; EONO/GRATKIT update 2026-08-06; TPU/variable-layer update 2026-08-11; nozzle-material/ELEGOO update 2026-08-12

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
- Orca states that MVS varies with material, machine, nozzle diameter, and extruder setup. Most 0.8 mm recommendations therefore retain the current 0.4 mm profile MVS only as a conservative temporary cap, then require nozzle-specific flow, PA, and MVS calibration. GEEETECH 0.8 instead uses a modest 3.0 mm3/s uncalibrated estimate because the larger nozzle is expected to reduce pressure drop; this is not a measured material limit. The process speeds were checked with `flow = line width x layer height x speed` and do not exceed their listed caps.
- Slicer field locations: filament temperatures, flow ratio, pressure advance, MVS, and cooling are in the Filament preset; retraction overrides are under Filament > Setting Overrides; feature speeds and acceleration are under Process > Speed; line widths are under Process > Quality; hardware ceilings remain in Printer > Motion ability.

## Brass, Stainless, And Hardened-Steel Nozzles

- Scope is identical standard Kobra geometry and bore at 0.4 or 0.8 mm. CHT/high-flow internals, changed melt-zone lengths, ruby/carbide inserts, proprietary high-conductivity hardened alloys, and performance coatings are excluded because they can dominate the bulk-alloy effect.
- Representative thermal conductivity establishes direction only: C360 brass is about 116 W/(m K) at 20 C; 304 stainless is about 15 W/(m K) at 20 C and 18 at 200 C; hardened A2 tool steel is about 26 W/(m K) at 20 C and 27 at 200 C. Exact purchased alloys are often undisclosed.
- Bulk conductivity does not determine the indicated temperature correction. The sensor normally measures heater-block temperature, while nozzle contact, sensor placement, melt-zone length, bore finish, plating, polymer viscosity, heater power, and flow determine the polymer temperature and pressure.
- CNC Kitchen's controlled V6 PLA comparison found a quality hardened-steel nozzle differed noticeably from brass mainly below about 200 C; above that it did not require a hotter setting in that system. This is the strongest applied comparison but covers one hotend, PLA, and hardened steel rather than stainless or the Kobra.
- Prusa provides a conditional `+5` to `+10 C` troubleshooting range for steel nozzles. This is compatible with the controlled result when treated as a response to observed under-extrusion, not an automatic offset.
- No controlled identical-geometry stainless comparison or exact Kobra 3 Max steel MVS dataset was found. Stainless and hardened values therefore remain separate in the operational table even though both begin with the same commissioning policy.
- Temperature policy: begin at the brass profile temperature after a 5-minute heat soak. If representative high-flow lines are repeatably weak, matte, or under-extruded, try `+5 C` within the exact filament range and repeat MVS. Restore baseline and lower flow if extra heat worsens stringing, Silk sheen, degradation, or heat creep.
- MVS policy: enter 80% of the brass-profile MVS for a first untested steel print. This is a conservative commissioning safety margin, not a measured steel penalty. Run MVS separately for material, color, diameter, nozzle material, machine, extruder, and nozzle; keep 80-90% of the first repeatable quality or strength transition. A quality steel nozzle may recover the full brass result.
- Nozzle diameter and material remain independent variables. A larger outlet can reduce pressure, but it does not proportionally increase melt-zone length. At the same MVS, 0.8 mm paths move more slowly because their bead cross-section is larger.
- Primary sources: https://www.cnckitchen.com/blog/flow-rate-benchmarking-of-a-hotend, https://help.prusa3d.com/article/e3d-v6-nozzles_920168, https://help.prusa3d.com/article/under-extrusion_2007, https://alloys.copper.org/alloy/C36000, https://www.alleima.com/en/technical-center/material-datasheets/tube-and-pipe-seamless/alleima-3r12/, https://www.uddeholm.com/en/app/uploads/sites/216/productdb/api/tech_uddeholm-rigor_en.pdf, and https://e3d-online.com/pages/revo-high-flow-volumetric-flow-rate-calculator

## GEEETECH TPU 95A

- Official GEEETECH ranges: 200-230 C nozzle, 50-60 C bed, 20-30 mm/s main speed, 10-15 mm/s first layer, less than 1 mm retraction at 20-40 mm/s or disabled, 30-50% fan, and 50-60 C drying for 4-6 hours.
- Product: https://www.geeetech.com/products/tpu-3d-printer-filament-1-75mm-1kg-roll
- Printing guide: https://blog.geeetech.com/materials/tpu-filament-guide-how-to-print-with-tpu/
- Drying guide: https://blog.geeetech.com/materials/3d-printing-filament/why-tpu-filament-absorbs-moisture-easily-and-how-to-dry-it/
- Most relevant owner report: https://forum.drucktipps3d.de/forum/thread/39344-kobra-3-tpu-problem-im-extruder/
- The owner initially completed 8-hour and 6-hour prints, then GEEETECH 95A repeatedly escaped between the drive and idler rollers and wrapped around the extruder. Small, retract-heavy geometry was worse. Slowing, changing slicers, and changing retraction did not provide a durable fix. A clean/new hotend produced one provisional success.
- In a Kobra 3 Max discussion, a commenter using a smaller Kobra 3 reported about 25 mm/s as a practical ceiling and clogging above it. No nozzle diameter, layer height, or line width was stated, so this cannot establish a Max-specific MVS. The thread does support a short top-fed path: https://old.reddit.com/r/AnycubicOfficial/comments/1k4n3ou/any_tips_on_printing_tpu_on_anycubic_kobra_3_max/
- Derived 0.4 profile: 225 C, 50/45 C bed, flow 1.00, MVS 2.3 mm3/s at 0.20/0.24 and 1.6 mm3/s at 0.12, 0.5 mm retraction at 20 mm/s, wipe off, no layer-change retraction, and modest cooling. The 2.3 value comes from `0.45 x 0.20 x 25 = 2.25 mm3/s`, rounded up; it is not a measured volumetric-flow result. The 0.12 profile is experimental because Anycubic recommends 0.16-0.20 mm for TPU.
- Derived 0.8 profile: 225 C, flow 1.00, and 3.0 mm3/s as an uncalibrated engineering estimate. The larger nozzle normally reduces nozzle pressure but does not increase hotend melt length or remove TPU feed-path limits, so the value is not scaled by nozzle area. Calibrate from 2.0 to 5.0 mm3/s in 0.25 steps and retain 80-90% of the first repeatable surface, strength, slip, clicking, or filament-escape transition.

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
- The pinned Anycubic generic PETG base uses flow 0.96 and MVS 8 mm3/s; the exact Kobra 3 Max 0.4 child changes flow to 0.95 and retains MVS 8 mm3/s. The Max-specific Orca profile uses 0.8 mm retraction and PA 0.04.
- A SUNLU black owner used 250 C first layer and 245 C later with fan mostly off except overhangs: https://forum.bambulab.com/t/best-settings-for-sunlu-petg/33776?page=2#post_35
- Kobra 3 PETG owners reported near-flawless output at 250 C/100 C for two layers, then 240 C/80 C at 80 mm/s; this supports warmer/slower first layers but 100 C is too source-specific for a default: https://old.reddit.com/r/anycubic/comments/1exjpt8/petg_on_kobra_3/
- Kobra-family reports found poor layer adhesion above about 120 mm/s: https://forum.drucktipps3d.de/forum/thread/41778-anycubic-kobra-s1-sammelthread-slicer-profile-und-erkenntnisse/
- Derived profile: 245 C first layer, 250 C later, 75/70 C bed, flow 0.95, MVS 10 mm3/s, PA 0.040, 0.8 mm retraction at 30 mm/s, 35-65% normal fan, and 90-100% only for overhangs/bridges.

## ELEGOO Rapid PETG

- Exact product: plain, unfilled ELEGOO Rapid PETG, 1.75 mm, +/-0.02 mm, 1 kg, marketed for up to 600 mm/s. Product: https://www.elegoo.com/products/rapid-petg-filament-1-75mm-colored-1kg.js
- The exact Anycubic Slicer Next ELEGOO base uses 250 C nozzle, 70 C bed, 30-80% normal fan, 90% overhang fan, density 1.26, and 18 mm3/s MVS. The exact Orca system profile adds flow 0.99 and PA 0.052. These are product profiles, not Kobra-specific validation.
- ELEGOO machine profiles vary materially: Neptune 2 uses 10 mm3/s, Neptune 4 uses 18, and OrangeStorm Giga uses 34. This disproves treating 18 as a universal material constant.
- The exact Kobra standard-PETG references use flow 0.95/MVS 8 at 0.4 and flow 0.97/MVS 12 at 0.8. The Rapid PETG profile inherits those Kobra flow-ratio starts, retains ELEGOO's 250 C/70 C material baseline and a 75 C initial bed, and uses a derived 10 mm3/s 0.4 start between the exact Kobra standard-PETG cap and ELEGOO's higher system profiles.
- Derived 0.4 start: 250/250 C, 75/70 C bed, flow 0.95, MVS 10 mm3/s, PA disabled until a 0.025-0.060 sweep, 0.8 mm retraction at 30 mm/s, 30-80% normal fan, and 90% overhang/bridge fan.
- Derived 0.8 start: 250/250 C, 75/70 C bed, flow 0.97, temporary MVS 12 mm3/s, PA disabled until a 0.020-0.050 sweep, and the same direct-drive retraction. Unlock 14/16 mm3/s only if the measured failure point is at least about 16.5/18.8 mm3/s respectively.
- The advertised 600 mm/s would require about 54 mm3/s at a 0.45 x 0.20 mm path, far beyond the conservative Kobra profile. It is a product capability claim under unspecified geometry, not a process target.
- ELEGOO publishes no accessible exact drying cycle. Use 60 C for 6-8 h as a derived PETG start and extend for clear moisture symptoms; owner-tested lower-temperature cycles take longer.
- Plain Rapid PETG has no abrasive filler claim and can use brass. This conclusion does not apply to PETG-CF, PETG-GF, glow, metal-filled, or other filled variants.
- Exact German offer checked 2026-08-12: Alza white, 1 kg, EUR 13.49 incl. VAT, in stock >10: https://www.alza.de/elegoo-rapid-petg-1-75mm-1kg-cardboard-spool-white-d12389175.htm

## SUNLU PLA+ 2.0 High Speed

- Exact product identity: SUNLU High Speed PLA+ 2.0 / HSPLA Plus 2.0, not ordinary PLA+ 2.0 or the earlier High Speed PLA+ formulation.
- Official speed/temperature bands: 200-215 C at 50-150 mm/s, 215-230 C at 150-300 mm/s, and 230-260 C at 300-600 mm/s. Bed 50-65 C; retraction 0.8-1.2 mm at 30-40 mm/s; dry at 50 C for at least 4 hours.
- Product: https://store.sunlu.com/products/moq-6kg-high-speed-pla-2-0hspla-plus-2-0-high-speed-3d-printer-filament-1kg
- TDS testing used a 0.4 mm nozzle, 0.20 mm layer, 220 C nozzle, 55 C bed, and 100-220 mm/s: https://media.sunlu.com/prod/20260330/225ab1bc-a40a-435b-8d20-a2745303674b.pdf?filename=TDS
- Exact-product owner at 450 mm/s reported slight stringing, visible VFAs, about 5% worse finish, and about 35% less print time: https://www.reddit.com/r/3Dprinting/comments/1m1w03t/favorite_brand_of_filament/n3l70c2/
- Another owner found ordinary PLA+ 2.0 more consistent than the high-speed formulation: https://www.reddit.com/r/3Dprinting/comments/1otfuc0/quality_of_filament_recommendations/no5bcsn/
- The stock Kobra 3 Max high-speed PLA profile uses an 18 mm3/s MVS limit. Using the conservative rectangular check at 0.20 x 0.45 mm gives 200 mm/s before flow-ratio adjustment, far below the 600 mm/s motion claim.
- Derived profile: 220 C, 60/55 C bed, flow 0.97, MVS 18 mm3/s, PA 0.026, 0.8 mm retraction at 35 mm/s, 80-100% cooling, and lower outer/top speeds than infill.

## EONO Silk PLA Red / Gold / Blue

- Exact German listing: https://www.amazon.de/dp/B0B8YX4Y95?language=de_DE
- The listing confirms Red/Gold/Blue coextruded Silk PLA, 1.75 mm, 1 kg, vacuum packaging with desiccant, and Anycubic compatibility, but provides no EONO TDS or manufacturer print-temperature, speed, MVS, cooling, or drying values.
- Exact-color owner evidence on the Amazon page includes successful printing at 205-215 C with a 60 C bed. Another exact-color review reports tangling after roughly 100 m, conflicting with the listing's clean-winding claim; inspect the spool before unattended long prints.
- Anycubic's dual/tri-color Silk PLA is used only as a proxy envelope: 210-240 C, 55-56 C bed, and 8 mm3/s MVS. The exact pinned Kobra 3 Max Silk profile provides flow 0.96, 210 C, PA 0.04, and 13 mm3/s, but 13 mm3/s is not assumed for EONO without flow testing. EONO's exact-color owner evidence, rather than this proxy, supports the 60 C initial bed.
- Derived 0.4 mm start: 215/210 C nozzle, 60/55 C bed, flow 0.96, MVS 8 mm3/s, PA 0.040, 0.8 mm retraction at 30 mm/s, and 80-100% cooling after layer 1.
- Derived 0.8 mm safe start: 220/215 C nozzle, 60/55 C bed, flow 0.98, temporary MVS 8 mm3/s, PA disabled until calibrated, and 70-90% normal cooling. Lower outer-wall speed preserves gloss.
- No exact EONO drying cycle was found. Use 50-55 C for 4-6 hours only when moisture symptoms justify it, and verify dryer and cardboard-spool temperature tolerance.

## GRATKIT Silk PLA Blue / Purple / Black

- Exact German listing: https://www.amazon.de/dp/B0BWXQ2WZD?language=en_GB&th=1&psc=1
- Manufacturer page: https://gratkit.com/products/gratkit-silk-multi-color-pla-filament-1-75mm-coextrusion-pla-filament-1kg
- GRATKIT lists 200 +/-10 C nozzle temperature, adding 5 C for an all-metal hotend, 50 C on PEI or 60 C on glass, up to 350 mm/s, and direct-drive retraction of 2 mm at 40 mm/s. It simultaneously warns that Silk PLA melts more slowly than regular PLA and loses its silk texture at high speed; the 350 mm/s claim is therefore not used as a profile speed.
- GRATKIT describes Silk PLA as more brittle than regular PLA. A same-family Red/Gold/Purple owner/forum report identifies flow, retraction, filament twist, and inconsistent coextrusion orientation as possible causes of visible lines; the poster was not verified as official GRATKIT support and the colorway differs: https://forums.gratkit.com/d/65-tri-colour-silk-pla-lines
- The exact pinned Max Silk profile provides flow 0.96, 210 C, 13 mm3/s, PA 0.04, and full cooling. The custom profile starts at 10 mm3/s to preserve gloss and margin for batch variability.
- Derived 0.4 mm start: 215/210 C nozzle, 55/50 C bed, flow 0.96, MVS 10 mm3/s, PA 0.040, Kobra-safe 0.8 mm retraction at 30 mm/s rather than GRATKIT's aggressive generic 2 mm value, and 80-100% cooling after layer 1.
- Derived 0.8 mm safe start: 215/215 C nozzle, 55/50 C bed, flow 0.98, temporary MVS 10 mm3/s, PA disabled until calibrated, and 70-90% normal cooling. This stays at GRATKIT's documented all-metal-hotend ceiling rather than inheriting the generic Max PLA temperature.
- GRATKIT publishes no drying cycle. Use 45-50 C for 4-6 hours only for moisture symptoms or brittleness, then store sealed with desiccant.

## Variable Layer Height

- The user's core description is valid: Variable Layer Height assigns different layer heights along Z within one selected object, using finer layers for shallow slopes/curves and coarser layers where geometry permits. It is an object tool in `Prepare`, not a filament parameter.
- Orca documentation: https://github.com/OrcaSlicer/OrcaSlicer/wiki/prepare_variable_layer_height and https://github.com/OrcaSlicer/OrcaSlicer/wiki/quality_settings_layer_height
- Anycubic tool context: https://wiki.anycubic.com/en/software-and-app/new-page-anycubic-slicer-beta%28orca-version%29/anycubic-slicer-next-slicing-software-quick-start-guide
- Orca's generic 20-80% nozzle guideline gives 0.08-0.32 mm for 0.4 and 0.16-0.64 mm for 0.8, but it is not the exact Kobra 3 Max configuration. The pinned Anycubic Max 0.4 machine profile sets 0.08-0.28 mm; the referenced Orca Max 0.8 profile sets 0.16-0.56 mm.
- Current referenced Max fixed processes cover 0.08/0.12/0.16/0.20/0.24/0.28 for 0.4 and 0.20/0.24/0.32/0.40/0.48 for 0.8. A configured machine endpoint is not evidence that every material has a tuned process at that endpoint.
- Adaptive uses geometry and the machine bounds. `Quality / Speed` biases the accepted detail error; `Smooth` applies a Gaussian filter; radius is a dimensionless sample radius; and `Keep min` prevents smoothing from erasing fine regions. Manual editing uses the vertical layer profile.
- The first layer remains fixed. Configured line widths also remain fixed, while local volume per path length changes with actual layer height. MVS therefore limits coarse adaptive regions and can reduce their nominal speed advantage.
- Variable layer planes apply across the whole selected object at a given Z. Ordinary modifier meshes do not create an independent XY-local layer height; use a Height Range Modifier for a prescribed Z band.
- Adaptive uses the full layer-height limits in the active printer preset; Quality/Speed does not enforce a material/object window. The effective practical range is the intersection of machine, material, and object ranges. For repeatable enforcement, narrow Min/Max only in a separately named duplicate printer preset and set a separate VLH process's nominal layer height inside that range; the fixed initial layer remains independent. Otherwise manually constrain the generated profile and verify actual values in Preview.
- Current Orca and Anycubic source reject a genuinely variable layer profile with Organic/default tree support. The inherited `tree(auto)` plus `default` style counts as Organic; disable support or select Normal, Slim, Strong, or Hybrid support before slicing.
- The tool is material-agnostic, but useful working windows are not. TPU should avoid extreme minima and excessive layer changes; standard and Rapid PETG need finer overhang/hole-roof regions; High Speed PLA+ tolerates the broadest speed range after MVS calibration; Silk benefits from narrow or fixed hero-surface heights because transitions can appear as sheen bands.
- The fixed profiles in this guide set top/bottom minimum thickness to zero so layer counts are authoritative. A variable-height process must instead set or verify physical shell-thickness minima because a fixed number of layers no longer represents a fixed thickness. In vase mode, thickness fields are disabled and `Bottom shell layers` controls the processed base; sum the actual layer heights in Preview.
- Derived first-use windows are 0.12-0.24 mm for the 0.4 nozzle and 0.20-0.40 mm for the 0.8 nozzle, narrowed by material and object type in the main deliverable. The 0.8 nozzle can improve Z smoothness at 0.20-0.28 mm but cannot recover small XY detail lost to its approximately 0.82 mm bead width.

## Derived Profiles

- The deliverable uses 0.12 mm detail, 0.20 mm balanced, and 0.24 mm balanced profiles with the 0.4 mm nozzle. It adds 0.20 mm fine and 0.40 mm draft profiles with the 0.8 mm nozzle for all seven materials.
- The 0.4 mm rigid-filament profiles retain 3 walls, approximately 0.8-1.0 mm top/bottom thickness, aligned hidden seams, 15% gyroid infill, and 0.4 mm slope z-hop. The 0.8 mm variants use 2 walls because they are already about 1.64 mm thick.
- TPU uses 3 walls with the 0.4 mm nozzle and 2 walls with the 0.8 mm nozzle. It keeps gyroid but avoids supports, wipe, multi-object plates, and unnecessary retraction. GEEETECH uses no z-hop initially; SUNLU keeps z-hop optional.
- Feature speed and acceleration are intentionally lower for outer walls and top surfaces. MVS remains the hard sustained extrusion cap.
- The 0.8 mm profiles use the pinned Orca Max reference geometry: 0.82 mm feature widths, a 0.40 mm first layer, and a 0.16-0.56 mm machine layer range. Two walls are already about 1.64 mm thick; 0.20 mm layers use 5/4 top/bottom layers and 0.40 mm layers use 3/3 for roughly 0.8-1.2 mm shell coverage.
- Tri-color Silk PLA appearance depends on model rotation around Z and filament orientation through the extruder. Print an orientation cylinder before a large decorative model; slower outer walls improve gloss more predictably than headline high-speed settings.

## Limitations And Calibration

- These are evidence-based starting profiles, not universal optima. Spool moisture, pigment, ambient temperature, nozzle wear, and firmware/profile revisions change the result.
- Installed Anycubic Slicer Next presets must be checked because public repository and bundled/cloud profiles have differed.
- After every nozzle change, rerun bed leveling/Z offset checks, flow ratio, pressure advance, and MVS. Do not transfer a 0.4 mm PA value to 0.8 mm without validation.
- Calibration order: dry filament, verify first layer, temperature tower, flow ratio, pressure advance for rigid materials and only after stable extrusion for TPU, MVS test, PA recheck at representative flow, retraction, then dimensional coupon.
- Set MVS 10-20% below the first repeatable failure or surface transition in a flow test.
- For TPU, solve feed drag, hotend residue, and gear wrapping before increasing retraction or flow. Do not use ACE Pro for feeding.
- For brittle Silk PLA or questionable cardboard-spool winding, test direct external feeding before relying on ACE Pro for a long unattended print.
