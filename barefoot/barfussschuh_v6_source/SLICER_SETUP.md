# V6 Slicer Setup – TPU Upper

## Variante A – Infill-only Upper

Importiere als zwei Teile in exakt derselben Position:

1. `v6_upper_infill_envelope_left.stl`
2. `v6_upper_reinforcement_frame_left.stl`

### Envelope – Startwerte

Für OrcaSlicer / Anycubic-Slicer-Next-artige Profile:

- Wall loops: **0**, sofern die verwendete Version dies akzeptiert
- Top shell layers: **0**
- Bottom shell layers: **0**
- Sparse infill: **18–25 %**
- Pattern: **Gyroid** als erster Versuch
- Ensure vertical shell thickness: **None**
- Minimum sparse infill threshold: **0 / deaktiviert**
- TPU: bevorzugt 85A–90A; 95A zunächst niedriger in der Dichte testen
- 0,4-mm-Düse: guter Start für feinere offene Struktur
- Geschwindigkeit: konservativ, typischerweise etwa 15–25 mm/s bei sehr weichem TPU

Vor dem Schuh unbedingt `testcoupon_infill_only.stl` slicen und in der Layer-Vorschau kontrollieren:

- keine Außenwände am Envelope
- keine geschlossenen Deckschichten
- nur offene Infillbahnen

Der Verstärkungsrahmen bekommt normale Wände, z. B. 2–3 Perimeter.

Falls der Slicer Wall loops = 0 nicht sauber unterstützt, nicht blind drucken. Dann entweder einen einzelnen sehr dünnen Perimeter verwenden oder eine explizit modellierte Lattice-Version erzeugen.

## Variante B – Thin shell + Fuzzy Ripple

Importiere:

1. `v6_upper_fuzzy_shell_left.stl`
2. `v6_upper_reinforcement_frame_left.stl`

Start:

- Wall loops: 1
- Top/Bottom shells: 0
- Sparse infill: 0
- inner surface: ohne Fuzzy
- Fuzzy Skin Mode: **Contour**
- Fuzzy Skin Generator Mode: **Combined** als robuster Start
- Noise Type: **Ripple**
- Skin thickness: etwa **0,10–0,16 mm** bei 0,4-mm-Düse als vorsichtiger Start
- Point distance: etwa **0,7–1,0 mm**
- Fuzzy Skin auf erster Lage: aus

Die genaue Ripple-Zahl ist stark vom Umfang und der Slicer-Version abhängig. Zuerst einen Ausschnitt testen.

### Warum Combined statt starkem Displacement?

Ein starkes reines Displacement verschiebt die Bahn seitlich und kann die Wand schwächen. Combined behält das deutliche Muster, während die Wand dichter und mechanisch günstiger bleibt.

### Atmungsaktivität

Ripple/Fuzzy Skin macht eine geschlossene TPU-Haut **nicht** wirklich atmungsaktiv. Deshalb ist die Fuzzy-Variante als robustere, haptisch weichere Sockenschuh-Haut gedacht. Für echte Luftdurchlässigkeit ist der Infill-only-Modus besser.

## Sohle

`v6_sole_left.3mf` enthält vier benannte, überlappende Teile:

- organic_sole_body
- curved_textile_overlap_lip
- hex_tread
- hex_side_wrap

Alle vier mit demselben TPU drucken und als eine Assembly/Part-Gruppe behandeln. Nach dem Slicen kontrollieren, dass die überlappenden Volumina zu durchgängigen Extrusionsbahnen führen.
