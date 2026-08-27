# MM-ORG-010 — Personalized Pen and Stationery Caddy

Parametric DRAFT implementation of portfolio SKU-018. The product combines three tall stationery wells, a small-item tray, a passive phone cradle and a removable personalized nameplate in a 150 x 120 x 128 mm default envelope.

The personalization is reproducible without installed fonts: `cad/build.py` owns a geometric 5x7 glyph set, German transliteration, a 16-character limit and a minimum-pixel check. Change `personalization.name` in `config/model-parameters.json`, then run the tests and build.

Expected outputs:

- STEP masters for chassis, plate registration and complete assembly;
- manufacturing STL files for chassis and flat-printed plate;
- two small production-clearance coupon STLs;
- a two-object millimetre 3MF print set;
- machine-readable topology, interface, optimization and build reports.

Digital checks do not authorize release. A local Kobra 3 Max / 0.4 mm / 0.20 mm / Anycubic PLA slice passes, but the physical test plan, canonical watermark and commercial approval remain blocked/deferred.
