# Druckprofil – ungefülltes warmbraunes PETG, R2 DRAFT

## Zielprofil

| Einstellung | Ausgangswert |
|---|---:|
| Verfahren | FDM/FFF |
| Material | ungefülltes warmbraunes PETG, matt oder seidenmatt |
| Düse | 0,40 mm |
| Schichthöhe | 0,20 mm |
| Linienbreite | 0,45 mm |
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
3. Holztexturcoupon drucken und Bodenstufen, 0,16-mm-Innenwandnut, 90°-Eckübergang und 0,20-mm-Topnut auf Erkennbarkeit, Haptik und Reinigung prüfen.
4. Im Slicer die ersten drei Schichten, 3,2-mm-Wände, alle Verbinder, U-Griffnuten, glatten Wandknoten und die geschützten Unterseiten kontrollieren. Der aktuelle R2-Kandidat ist absichtlich noch unmarkiert.
5. Erst danach ein Hauptmodul drucken; anschließend Passung und Wandwurzelstabilität prüfen.

## Slicer-Prüfpunkte

- Außenmaß je Modul stimmt mit `reports/validation-report.md` überein.
- Keine automatisch erzeugten Supports oder schwebenden Inseln.
- 3,2-mm-Trennwände werden lückenlos mit mehreren Linien gefüllt.
- 0,90-mm-Holznuten bleiben reine Vertiefungen; 0,20-mm-Boden-/Topnuten und 0,16-mm-Innenwandnuten werden nicht ausgelassen oder geschlossen.
- Außenflächen, Unterseiten, Verbinder, Passflächen, Griffnutradien und glatte Wandknoten bleiben ohne geometrische Maserung.
- Maserungsbahnen und Astkonturen erzeugen keine losen Inseln, fehlenden Wände oder problematischen Kurzsegmente.
- Keine Kompensation vergrößert die 0,30-mm-Steckpassung ungewollt.

## Material- und Zeitabschätzung

Das geometrische Festkörpervolumen der vier aktuellen R2-Module plus Kamm beträgt rund 642,21 cm³. Das ist kein Materialverbrauch: Wände, Top-/Bottom-Schichten und Infill werden erst im exakten Slicer in reale Extrusionspfade übersetzt. Zeit, Masse, Support, Kurzsegmente und Warnungen müssen deshalb aus dem gespeicherten Zielprofil ermittelt werden.
