# Finales Modellergebnis 0.1.2-g1

Der polygonale Würfelturm ist in der freigegebenen Form fertiggestellt und digital validiert. Das finale Fertigungsmesh ist byteidentisch mit dem ausdrücklich freigegebenen Wasserzeichenkandidaten; nach der Freigabe wurde keine Geometrie verändert.

## Modellergebnis

- 220 mm hoch, ca. 149,56 × 147,32 mm Außenhülle
- Einwurf hinten-oben: 45°, Ø 38 mm frei, 4 mm Kanalwand, 5,000 mm sichtbarer Überstand
- Auswurf vorne-unten: 40 × 33 mm frei, 4 mm Seiten/Krone, 8,000 mm sichtbarer Überstand
- Innenraum Ø 57 mm mit drei versetzten Fallstufen und geschlossenem Rampenboden
- Dachhorn und Rückwand außerhalb der Einwurfzone unverändert
- einteiliges, aufrecht druckbares Modell ohne eingeschlossene Innenstützen

## Verifikation und Druckbereitschaft

- Finales STL: 16.914 Dreiecke, ein zusammenhängender, wasserdichter Körper mit positivem Volumen
- 25-mm-Prüfwürfel: 94/94 digital geprüfte Positionen ohne unzulässige Kollision
- kleinste geprüfte Zylinderwand: 5,926 mm
- geschlossener Boden im Funktionsbereich: mindestens 24,000 mm
- Außenhaut außerhalb der freigegebenen Bearbeitungsbereiche: P95 0,0000023 mm zum Original
- passt in den 420 × 420 × 500 mm Bauraum des Anycubic Kobra 3 Max
- Baseline: PLA/PLA+, 0,4-mm-Düse, 0,20-mm-Schichten, Originalunterseite flach auf dem Druckbett

## Lieferumfang

- finales gekennzeichnetes STL
- reproduzierbare Parameter und Build-Skripte
- Original- und Arbeitsmesh, Funktionskörper und Wasserzeichenasset
- Konzept- und Produktionsansicht
- Topologie-, Geometrie-, Würfelweg- und Wasserzeichenprüfberichte
- Design-Spezifikation, Entscheidungsprotokoll, Release-Manifest und Prüfsummen

## Offene Nachweise

- Slicer-Layer-/G-Code-Prüfung mit dem tatsächlich verwendeten Profil
- je zehn reale Falltests mit D6, D12 und D20 bis maximal 25 mm; Ziel: keine Klemmer, kein Rücksprung aus dem Einwurf und vollständiger Auslauf in den Vorhof

## Kennzeichnung

- JuSt Innovation `JSI-WM-001-R1` compact, 0,40 mm vertieft auf der Unterseite: digital geprüft und freigegeben.

Nächster sinnvoller Schritt ist der Slicer-Check und anschließend ein erster vollständiger Testdruck für die realen Falltests.
