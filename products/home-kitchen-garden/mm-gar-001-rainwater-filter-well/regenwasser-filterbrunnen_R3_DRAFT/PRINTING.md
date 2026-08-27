# Druckprofil und Orientierung · Revision 3 DRAFT

## Startprofil

| Parameter | Startwert | Status |
|---|---:|---|
| Material | UV-stabilisiertes, blickdichtes PETG | Materialklasse bestätigt; konkrete Marke offen |
| Düse | 0,6 mm | Zielprozess |
| Schichthöhe | 0,28 mm | Zielprozess |
| Linienbreite | 0,66 mm nominal | Arachne/variable Breite empfohlen |
| Perimeter | 7 | mindestens sieben Bahnen in 4,8-mm-Wasserwand |
| Bodenstärke | 6,0 mm modelliert; mindestens 22 Bodenschichten | nicht durch Infill ersetzen |
| Infill | 20–25 % Gyroid nur in massiven Zusatzkörpern | Gehäusewände sind massiv modelliert |
| Außenwand | 30–35 mm/s | Startwert |
| übrige Perimeter | 40–45 mm/s | Startwert |
| maximaler Volumenstrom | 8 mm³/s bis Kalibrierung, danach höchstens 10 mm³/s | filamentspezifisch |
| Düse / Bett | 245 ±5 °C / 80 ±5 °C | Filamentdatenblatt hat Vorrang |
| Lüfter | 30–40 % nach ersten Schichten; Brücken lokal höher | filamentspezifisch |
| Brim | 12–15 mm an den drei Gehäusen | gegen Ablösen und Kippfehler |
| Naht | weg von Ports und Wasserwegen | visuell und auf Dichtheit prüfen |

Filament nach Herstellerangabe trocknen; ohne abweichende Vorgabe sind 60–65 °C für 4–6 Stunden ein vorsichtiger PETG-Startpunkt. Großteile zugfrei drucken.

## Orientierung und Stützen

| Teil | gespeicherte STL-Lage | Stützstrategie |
|---|---|---|
| drei Gehäuse | Basis auf Bett | lokal unter beiden DN25-Portdächern; Stufe 3 zusätzlich am 100-mm-Auslass; keine Vollflächenstütze im Behälter |
| Schlammtrichter | invertiert | inneren Konus prüfen; nur erreichbare organische Stützen |
| offener Einlaufbecher | Aufnahme unten, Führungen oben | der 278-mm-Stützring liegt rund 50 mm über Bett und benötigt gezielte, vollständig entfernbare Stütze; vor Großdruck zwingend Slicer-Schnitt prüfen |
| Zulauf-Fallrohr | aufrecht | lokale Stütze unter Tangentialauslass und Anschlagkragen; Innenkanal freihalten |
| Lamellenkassette | um 30° auf die Seite | Lamellen annähernd vertikal; Griffbrücken prüfen |
| Stufe-2-Fallrohr, Diffusor, Körbe, Verteiler | flach/axial wie exportiert | üblicherweise ohne Stütze |
| Kaskade und optionaler Auslaufadapter | Montageflansch auf Bett | Bohrungsbrücken prüfen |
| DN25-Stutzen, Blinddeckel, Coupons | Flansch/Basis auf Bett | üblicherweise ohne Stütze |

Stützen dürfen nicht in Dichtflächen, Zentrierbund, Lamellenspalte, Fallrohrbohrungen oder Kennzeichnungsvertiefung hineinwachsen. Wenn der Einlaufbecher-Stützring im konkreten Slicer nicht sauber, sparsam und entfernbar unterstützt werden kann, ist der Druck abzubrechen und die Baugruppe vor einer Release-Freigabe in getrennten Ring und Becher aufzuteilen.

## Pflichtprüfungen im Slicer

- jedes Teil mit mindestens 5 mm Bett- und Höhenreserve;
- der Einlaufbecher-Stützring besitzt über 360° eine tragfähige, erreichbare Stützschnittstelle;
- der 28-mm-Tangentialauslass und beide 25-mm-Ablasspassagen bleiben vollständig frei;
- keine ausgelassene 2,4-mm-Lamelle, 3,2-mm-Gitterbahn oder M5/M6-Bohrung;
- kontinuierliche Wasserwand ohne versteckte Infill-Lücke;
- lokale Stützen sind nach dem Druck erreichbar;
- erste zwei Kennzeichnungslagen zeigen Hexagon-, J- und S-Kontur ohne zugelaufene Lücken;
- Material- und Zeitabschätzung gegen verfügbare Spulen prüfen.

`profiles/Kobra3Max_PETG_0.6_DRAFT.ini` ist nur ein unvalidierter PrusaSlicer-kompatibler Startpunkt. Das konkrete Anycubic-/Orca-Profil hat bei Maschinen-, Start-/End-G-Code- und Beschleunigungswerten Vorrang.
