# Druckprofil und Orientierung · Revision 2 DRAFT

## Startprofil

| Parameter | Startwert | Status |
|---|---:|---|
| Material | UV-stabilisiertes, blickdichtes PETG | freigegebene Materialklasse; konkrete Marke offen |
| Düse | 0,6 mm | Zielprozess |
| Schichthöhe | 0,28 mm | Zielprozess |
| Linienbreite | 0,66 mm nominal | Startwert, Arachne/variable Breite empfohlen |
| Perimeter | 7 | ergibt mindestens sieben Bahnen in der 4,8-mm-Wasserwand |
| Bodenstärke | 6,0 mm modelliert; mindestens 22 Bodenschichten | Slicer darf die modellierte Basis nicht aushöhlen |
| Infill | 20–25 % Gyroid, nur wo der Slicer tatsächlich Volumenkörper erkennt | Gehäusewände sind massiv modelliert |
| Außenwand | 30–35 mm/s | Startwert für Oberfläche und Dichtheit |
| übrige Perimeter | 40–45 mm/s | Startwert |
| maximaler Volumenstrom | 8 mm³/s bis zur Kalibrierung, danach höchstens 10 mm³/s | filamentspezifisch prüfen |
| Düse / Bett | 245 ±5 °C / 80 ±5 °C | nur Startbereich; Filamentdatenblatt hat Vorrang |
| Lüfter | 30–40 % nach den ersten Schichten; Brücken lokal höher | filamentspezifisch |
| Brim | 12–15 mm an den drei 280-mm-Gehäusen | gegen Ablösen und Kippfehler |
| Naht | rückseitig/weg von Ports und Wasserwegen | visuell und auf Dichtheit prüfen |

Filament nach Herstellerangabe trocknen; wenn der Hersteller nichts Abweichendes vorgibt, ist 60–65 °C für 4–6 Stunden ein vorsichtiger PETG-Startpunkt. Großteile zugfrei drucken. Ein geschlossener, heißer Bauraum ist für PETG nicht zwingend und darf die zulässige Umgebung des Druckers nicht überschreiten.

## Orientierung und Stützen

| Teil | gespeicherte STL-Lage | Stützstrategie |
|---|---|---|
| drei Gehäuse | Basis auf Bett | Stufe 1 lokal unter tangentialem Zulauf und Ablass; Stufe 3 lokal am 100-mm-Auslassdach; keine Vollflächenstütze im Behälter |
| Sedimenttrichter | invertiert | inneren Konus im Slicer prüfen; gegebenenfalls leicht lösbare organische Stützen nur innen |
| Lamellenkassette | um 30° auf die Seite gedreht, Lamellen annähernd vertikal | normalerweise stützarm; Griffbrücken prüfen |
| Fallrohr, Diffusor, Körbe, Verteiler | flach/axial wie exportiert | üblicherweise ohne Stütze |
| Kaskade und Schlauch-Auslaufadapter | Montageflansch flach auf Bett | üblicherweise ohne Stütze; Bohrungsbrücken prüfen |
| Tüllen, Blinddeckel, Coupon | Flansch/Basis auf Bett | ohne Stütze |

Stützen dürfen nicht in Dichtflächen, Zentrierbund, Lamellenspalte oder Kennzeichnungsvertiefung hineinwachsen. Für die drei großen Gehäuse sind ein sauber kalibriertes Bett, Z-Offset, Fluss, Pressure Advance und eine kontrollierte erste Schicht wichtiger als hohe Geschwindigkeit.

## Pflichtprüfungen im Slicer

- jedes Teil mit mindestens 5 mm Bett- und Höhenreserve;
- keine ausgelassene 2,4-mm-Lamelle, 3,2-mm-Gitterbahn oder M5/M6-Bohrung;
- geschlossene, kontinuierliche Wasserwand ohne versteckte Infill-Lücke;
- lokale Stützen erreichbar und entfernbar;
- erste zwei Kennzeichnungslagen zeigen alle Hexagon-, J- und S-Konturen ohne zugelaufene Lücken;
- Material- und Zeitabschätzung gegen verfügbare Spulen prüfen.

`profiles/Kobra3Max_PETG_0.6_DRAFT.ini` ist nur ein unvalidierter PrusaSlicer-kompatibler Startpunkt. Ein echtes Anycubic-/Orca-Profil des konkreten Druckers hat bei Maschinen-, Start-/End-G-Code- und Beschleunigungswerten Vorrang.

