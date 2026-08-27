# Entwurfs-Ergebnis — MM-BTH-003 Revision 3.1

Das freigegebene Abflusssieb wurde als Revision `3.1.0-draft.1` vollständig modelliert und digital validiert. Die CAD-/Mesh- und lokalen Anycubic-Slicer-Next-Prüfungen sind ohne Fehler abgeschlossen; physische Coupon-, Passform- und Funktionsprüfungen sowie die finale menschliche Freigabe stehen noch aus.

## Modellergebnis

- Offizielle Bezeichnung: `MM-BTH-003` — **Linear Shower Drain Hair Trap**
- Nennmaß im Einbau: 945 × 65 × 21 mm
- 16 lose Einzelsegmente à 52,5 mm mit je einem Fänger
- 1 loses, 105 mm langes Doppelsegment mit zwei Fängern
- 17 Teile, 18 erhaltene Fänger, keine Verbinder
- Baugruppenreihenfolge: 8 Einzelsegmente, markiertes Doppelsegment, 8 Einzelsegmente
- Fertigungs-STLs stehen bereits +90° um die Baugruppen-Y-Achse auf einem vollständigen U-Profil-Ende.

![Markiertes Doppelsegment von der Abflussinnenseite](validation/previews/DRAFT-MM-BTH-003-3.1.0-draft.1-watermark-inner-side-render.png)

## Prüfung und Druckbereitschaft

- STEP-Reimport: ein gültiger Einzelkörper, ein gültiger markierter Doppelkörper und 17 gültige Baugruppenkörper.
- Alle vier Master-/Fertigungsmeshes sind wasserdicht, konsistent orientiert, positivvolumig und jeweils genau eine Komponente; keine Rand-, Nichtmanifold-, degenerierten oder doppelten Flächen.
- Anycubic Slicer Next 1.3.9.4: beide Fertigungs-STLs mit den lokalen Kobra-3-Max-Hardened-0,4-/PETG-Profilen erfolgreich geslicet; Supports deaktiviert.
- Einzelsegment: 262 Schichten, 18,64 g, 1 h 10 min 1 s. Doppelsegment: 525 Schichten, 36,71 g, 2 h 21 min 21 s.
- Hochrechnung für 16 + 1 Teile: 334,95 g und 21 h 1 min 37 s im Normalmodus.
- Der gespeicherte erste Layer zeigt das zusammenhängende U-Profil-Ende und den konfigurierten Außen-Brim. Ein gespeicherter Layer bei Z=52,44 mm enthält die modellierten Watermark-Konturen.

## Lieferdateien

- Parametrische Quelle: `build_shower_drain_hairtrap_v3.py`
- Einzelsegment STEP/STL: `exports/master/DRAFT-MM-BTH-003-3.1.0-draft.1-single-52p5mm-master.*`
- Markiertes Doppelsegment STEP/STL: `exports/master/DRAFT-MM-BTH-003-3.1.0-draft.1-double-105mm-marked-master.*`
- Baugruppenreferenz: `exports/master/DRAFT-MM-BTH-003-3.1.0-draft.1-17-part-assembly-reference.step`
- Fertigung: `exports/manufacturing/DRAFT-MM-BTH-003-3.1.0-draft.1-*-on-end.stl`
- Watermark-Coupon: `assets/metrimade-watermark/generated/MM-BTH-003_v3.1.0-draft.1/metrimade-watermark-MM-BTH-003-v3.1.0-draft.1-coupon-d040.stl`
- Slicerprofile: `profiles/anycubic-slicer-next/`
- Gesamtprüfung: `validation/project-validation-3.1.0-draft.1.json`

Eine 3MF-Freigabedatei und ein Release-Paket wurden bewusst noch nicht erzeugt, weil die physischen Gates offen sind.

## Offene Punkte

- Vollständige Layer-für-Layer-Sichtprüfung in der Anycubic-GUI.
- Watermark-Coupon mit dem dokumentierten PETG-Prozess drucken und beide Zeilen prüfen.
- Mindestens ein Einzel- und ein Doppelsegment drucken; Kanten, Stand, Verzug und Watermark beurteilen.
- Alle 17 Teile im realen Ablauf auf Gesamtlänge, Fugen, Wackeln und Schärfe prüfen.
- Wasserablauf, Haarfang und Reinigung praktisch testen.

## Kennzeichnung

- `MM-WM-001-R1` für `MM-BTH-003 · v3.1.0-draft.1`, 0,4 mm vertieft auf der inneren Seitenwand des Doppelsegments: digital PASS, physischer Coupon und menschliche Freigabe ausstehend.

Nächster Modellschritt: zuerst den enthaltenen Watermark-Coupon und danach je ein Einzel- und Doppelsegment mit dem dokumentierten Anycubic-PETG-Profil drucken und vermessen.
