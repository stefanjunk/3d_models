# Druckprofil – PETG, R1.4 DRAFT

## Zielprofil

| Einstellung | Startwert |
|---|---:|
| Verfahren | FDM/FFF |
| Material | Graphit-/Metalloptik-PETG |
| Düse | 0,40 mm |
| Schichthöhe | 0,20 mm |
| Linienbreite | 0,44 mm |
| Perimeter | mindestens 3 |
| obere/untere feste Schichten | mindestens 5 |
| Infill | 15–25 %, Gyroid oder Grid |
| Supports | aus |
| Orientierung | geschlossene Modulunterseite flach auf dem Bett |
| obere Flächen | monotonic, einheitliche Richtung je Modul |
| Naht | Rückseite oder unkritische Außenkante |
| Brim | optional 5–8 mm bei Warping |
| Elefantenfuß-Kompensation | 0,15–0,25 mm als Startwert |

Extruder- und Betttemperatur, Fluss, Kühlung und maximale Volumenrate müssen aus dem validierten Profil des konkreten PETG übernommen werden. Bei gefülltem Metalloptik-Filament die Abrasionshinweise des Herstellers beachten; gegebenenfalls eine verschleißfeste Düse verwenden.

## Reihenfolge der Qualifikation

1. Stahltextur-Coupon mit exakt diesem Profil drucken. Das mittlere Feld entspricht 100 % der R1.4-Tiefe; links/rechts liegen 75 % und 120 %.
2. Prüfen: keine scharfen Spitzen, keine schlecht schließenden Bahnen, angenehme Wandoberkante und ausreichende Reinigbarkeit.
3. Connectorpaar auf demselben Bett und in derselben XY-Ausrichtung wie die Modulverbinder drucken. Passung messen; `connectors.clearance` nur in 0,05-mm-Schritten verändern.
4. Eckcoupon an Front, Mitte und Rücken der realen Schublade prüfen.
5. Im Slicer die ersten drei Schichten, alle Innenwände, Griffnuten, Connectoren, glatten Keep-outs und die Unterseitenkennzeichnung kontrollieren.
6. Erst anschließend ein Hauptmodul drucken.

## Slicer-Prüfpunkte

- Keine Supports oder schwebenden Inseln.
- 3,2-mm-Wände werden lückenlos mit mehreren Linien erzeugt.
- Die flachen Dellen bleiben Vertiefungen und erzeugen keine losen Mikrosegmente.
- Wandwurzel-, Griff- und Connectorbereiche bleiben glatt.
- Wandoberseiten sind durchgehend geschlossen und angenehm verrundet; die Textur liegt innerhalb des glatten Randbands.
- Unterseitenkennzeichnung erscheint nur innerhalb der ersten 0,40 mm und verändert die Bettauflage nicht.
- Keine XY-Kompensation verändert die nominelle 0,30-mm-Connector-Freigabe unbeabsichtigt.

## Optischer Stahl-Look

- Ein metallisch-graphitfarbenes PETG liefert den größten Anteil der realistischen Wirkung.
- Monotone Top-Fill-Richtung unterstützt gebürstete Reflexe auf Fachböden.
- Auf senkrechten Wänden zunächst normale Perimeter verwenden. Eine zusätzliche Slicer-Rauheit/Fuzzy-Skin nur nach Coupon und sehr mild einsetzen; sie darf Connectoren, Wandoberseiten und Griffkanten nicht erreichen.
- Sub-Düsen-Kratzer werden nicht als CAD-Geometrie modelliert.

## Materialabschätzung

Die vier Hauptmodule plus Kamm besitzen im CAD zusammen 644,95 cm³ Festkörpervolumen. Der tatsächliche Filamentbedarf hängt von Wandgenerator, Infill, Überlappung, Fluss, Filamentdichte und Slicerprofil ab; der Slicerwert ist für die Rollenplanung maßgebend.
