# Research validation — SKU-105

Accessed 2026-08-28. The gate is `PASS` for a digital-first, collection-specific storage cassette. Prices and marketplace counts are observations, not demand forecasts.

## Current demand and competition signals

- Etsy's current dongle-holder market page lists 42+ items and shows demand across wireless, USB, SD and device-specific holders. Most visible offers are single-device or connector-family products rather than a measured mixed drawer inventory: https://www.etsy.com/market/dongle_holder
- A current 12-slot 3D-printed USB holder is listed at USD 14.99, reports eight item reviews and emphasizes readable labels and custom fit, supporting paid interest in visible small-tech storage: https://www.etsy.com/listing/1487979942/usb-stick-flash-drive-organizer-holder
- A commercial Gridfinity holder stores seven USB-A dongles with approximately 6.1 mm between semi-loose slots for USD 5; this validates the job while leaving mixed envelope sizing and connector keep-outs open: https://www.draildiagnostics.com/draildiagnosticsstore/p/gridfinity-usb-dongle-organizer
- A free/simple USB, dongle and SD-card model is 77 x 116 x 15 mm with 29 downloads but only one like and no documented fit workflow, indicating crowded low-specificity supply: https://cults3d.com/en/3d-model/tool/usb-dongle-and-sd-card-holder
- German alternatives are mostly generic: Lens-Aid's EUR 17.99 travel hardcase uses mesh pockets for adapters and cards, while a German cable-sorter vendor describes the recurring problem of an entire drawer becoming cable storage. Neither maps a defined mixed collection to measured labelled cradles: https://www.lens-aid.de/products/technik-organizer-case-tasche-elektronik-kabel-reise and https://www.kabel-aufbewahren.de/

## Qualified problem signals

1. A 2026 keyboard user says boards without onboard receiver storage left them struggling to store dongles and built capacity for roughly 28: https://www.reddit.com/r/MechanicalKeyboards/comments/1oywsyw/usb_dongle_storage_solution/
2. A mixed legacy-adapter collector reports that labels and parts drawers avoid tipping out a catch-all box to find one adapter: https://www.reddit.com/r/VintageApple/comments/1kv5i80/dongles_organized_40_years_of_apple_dongles/
3. A small-computer user wanted microSD adapters visible at a glance and also carries a USB-C reader, supporting mixed card/adapter workflows: https://www.reddit.com/r/SBCGaming/comments/1jtznug/figured_out_a_use_for_all_my_spare_microsd_card/
4. A German home-tech discussion asks for a middle ground between a crushed drawer and dedicated archive boxes, explicitly giving bonus value to adapter storage: https://www.reddit.com/r/de_EDV/comments/z19rz4/suche_nach_guter_m%C3%B6glichkeitstipps_zur_privaten/
5. Another German discussion describes keeping obsolete connectors because the exact adapter is often needed later, including RS232 examples: https://www.reddit.com/r/de_EDV/comments/12o43jr/kabelkiste_ausd%C3%BCnnen/

## Standards and scope evidence

- USB-IF publishes current connector specifications and identifies connector geometry as an interoperability interface; this project uses generic measured envelopes and does not reproduce certified connector geometry or logos: https://www.usb.org/usb-type-cr-cable-and-connector-specification
- The SD Association gives standard SD as 32 x 24 x 2.1 mm and microSD as 11 x 15 x 1.0 mm. Those dimensions inform the measurement range only; this cassette does not claim media protection or SD certification: https://www.sdcard.org/developers/sd-standard-overview/capacity-sd-sdhc-sdxc-sduc/

## Decision

Proceed with a 220 x 160 mm, 20-position parametric cassette and a separate no-brand measurement card. Each item class owns its body, connector-keep-out and clearance values. The value proposition is a visible, numbered, collection-specific drawer map rather than another generic cable bag, one-size USB-A comb or copied branded accessory tray.

Limits: passive storage only; no energized devices, batteries, charging, waterproofing, ESD, data protection, connector certification or affiliation claim. Customer dimensions and later physical tests remain mandatory before release.
