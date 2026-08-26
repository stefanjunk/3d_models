# ZEN KINTSUGI WAVE FIFO – Hybrid v2.0.0

## Ergebnis

Modulare, wandmontierte FIFO-Säule für **5 Rollen bis Ø 120 × 105 mm**. Der funktionskritische Schacht, die Wandbefestigung, Modulverbinder, Dovetailführung und Duftschale sind parametrisch. Die sichtbaren Dekore wurden aus den gelieferten GLB-Quellmeshes als geschlossene, flach rückseitige Druckkörper rekonstruiert.

- Grundkörper: ca. **140 × 121.0 × 664 mm**
- Höhe inklusive organischer Krone: ca. **735 mm**
- Prüfzylinder im CAD: **Ø 122 × 107 mm**
- Alle Herstellungsdateien: Millimeter

## Empfohlene Herstellungsroute

1. Zuerst `rail_coupon_male.stl` und `rail_coupon_female.stl` drucken und die Schiebepassung prüfen.
2. Seitenteile bevorzugt als `SIDE_PANEL_A_multicolor.3mf` beziehungsweise `SIDE_PANEL_B_multicolor.3mf` **flach mit der Rückseite auf dem Bett** drucken. Die Goldader ist ein eigener Farbkörper.
3. Körpermodule aufrecht drucken. Die organischen Frontapplikationen sind bereits mit den Mittelmodulen verschmolzen; die Krone ist mit dem Kronenmodul verschmolzen.
4. Seitenpaneel von oben in beide Führungen einschieben, bis der geschlossene Kanalboden am Schienenanfang stoppt. Paneele vor dem Stapeln der Module montieren.
5. Module mit je vier Pins verbinden und zusätzlich an der Wand verschrauben. Die Pins richten aus; die Schrauben tragen die Last.
6. Duftschale auf die rechte Dovetailschiene der Krone schieben. Nur trockene Duftsteine verwenden.

## Startprofil Anycubic Kobra 3 Max

- Düse: **0,6 mm**
- Schichthöhe: **0,30 mm**, organische Paneele optional 0,20–0,24 mm
- Linienbreite: **0,68 mm**
- Körper: PETG, 3 Wände; lokale Schienen/Verbinder 4 Wände
- Paneele: PETG oder PLA, 3 Wände; 10–15 % Gyroid genügt meist
- Gold: Silk-PLA als separater Farbkörper
- Duftschale: PETG oder Wood-PLA; keine offene Flamme, kein flüssiges Öl direkt einfüllen
- Stützen: Körper normalerweise ohne; Duftschalenrippen und Dovetaildach in der Vorschau kontrollieren

## Dateien

- `STL/body_*.stl`: funktionsfähige Module, organikbereit
- `STL/side_relief_*_slide_panel.stl`: flach druckbare ivory Paneele
- `STL/kintsugi_*_conformal.stl`: deckungsgleiche Goldkörper für Mehrfarbdruck
- `STL/kintsugi_*_flat_optional.stl`: optionale flache Klebevarianten
- `STL/crown_wave_flat_optional.stl` und `STL/front_applique_*_flat_optional.stl`: Ersatz-/Versuchsdekore
- `STL/scent_tray_hybrid.stl`: parametrischer Funktionskern plus organische Fassade
- `*_multicolor.3mf`: Paneel und Goldader als getrennte, registrierte Objektteile
- `ZEN_KINTSUGI_WAVE_5R_HYBRID_assembly.3mf`: komplette Baugruppe
- `raw_organic/*.glb`: unveränderte Quellen mit eingebetteten Texturen
- `relief_reference/*.stl`: unvereinfachte Referenz-Höhenhüllen vor Funktionsschnittstellen

## Wichtige Grenzen

Die eingebetteten GLB-Texturen sind visuelle Referenz und liegen unverändert im Rohordner. Normale FDM-3MF/STL-Dateien bilden Farbe nicht als Foto-Textur ab; Gold und Stein werden deshalb über getrennte Druckkörper/Filamente umgesetzt. Eine exakte Slicerzeit wurde nicht erfunden: Import, Schichtvorschau, kurze Segmente, Brücken und Materialverbrauch müssen im verwendeten Orca-/Anycubic-Slicer geprüft werden. Vor der Gesamtmontage sind Passcoupon und ein Mittelmodul als physischer Test empfohlen.
