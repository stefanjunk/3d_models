# Druckprofil – PETG, R1 DRAFT

## Zielprofil

| Einstellung | Ausgangswert |
|---|---:|
| Verfahren | FDM/FFF |
| Material | PETG |
| Düse | 0,40 mm |
| Schichthöhe | 0,20 mm |
| Linienbreite | 0,44 mm |
| Perimeter | mindestens 3 |
| obere/untere feste Schichten | mindestens 5 |
| Infill | 15–25 %, Gyroid oder Grid |
| Supports | aus |
| Druckorientierung | geschlossene Modulunterseite flach auf dem Bett |
| Nahtposition | Rückseite bzw. unkritische Außenkante |
| Brim | optional 5–8 mm bei Warping |
| Elefantenfuß-Kompensation | 0,15–0,25 mm als Startwert |

Extruder-, Betttemperatur, maximale Volumenrate, Kühlung und Fluss werden aus dem validierten Profil des konkreten PETG-Herstellers übernommen. Keine pauschale Temperatur ersetzt die Herstellerangabe und die eigene Kalibrierung.

## Reihenfolge der Qualifikation

1. Eckcoupon drucken und das reale Schubladenspiel an Front, Mitte und Rücken prüfen.
2. Verbinderpaar drucken. Es soll von Hand zusammengehen, ohne zu klemmen, darf im eingelegten Zustand aber nicht sichtbar klaffen. Bei Bedarf `connectors.clearance` in 0,05-mm-Schritten ändern.
3. Reliefcoupon drucken und die flachste gut erkennbare, noch gut reinigbare Stufe wählen.
4. Im Slicer die ersten drei Schichten, 3,2-mm-Wände, alle Verbinder, U-Griffnuten, glatten Wandknoten und die Unterseitenkennzeichnung kontrollieren.
5. Erst danach ein Hauptmodul drucken; anschließend Passung und Wandwurzelstabilität prüfen.

## Slicer-Prüfpunkte

- Außenmaß je Modul stimmt mit `reports/validation-report.md` überein.
- Keine automatisch erzeugten Supports oder schwebenden Inseln.
- 3,2-mm-Trennwände werden lückenlos mit mehreren Linien gefüllt.
- Plattenstöße bleiben Vertiefungen; Nieten werden als zusammenhängende Bahnen erzeugt.
- Unterseitenkennzeichnung ist in direkter Unterseitenansicht lesbar und in den ersten 0,40 mm vorhanden.
- Keine Kompensation vergrößert die 0,30-mm-Steckpassung ungewollt.

## Material- und Zeitabschätzung

Das geometrische Festkörpervolumen der vier R1-Module plus Kamm beträgt 622,42 cm³. Mit 1,27 g/cm³ ergibt das theoretisch etwa 790 g PETG bei vollständig massiv interpretiertem Modellvolumen. Slicerwert, Infillstrategie, Linienbreite, Filamentdichte und Fluss verändern den tatsächlichen Verbrauch; der Slicerwert ist für die Rolle maßgebend.
