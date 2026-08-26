# Druckprofil – matte Walnussoptik, R1.5 DRAFT

## Startprofil

| Einstellung | Startwert |
|---|---:|
| Verfahren | FDM/FFF |
| Material | mattes walnussbraunes PETG |
| Düse | 0,40 mm |
| Schichthöhe | 0,20 mm |
| Linienbreite | 0,44 mm |
| Perimeter | mindestens 3 |
| obere/untere feste Schichten | mindestens 5 |
| Infill | 15–25 %, Gyroid oder Grid |
| Supports | aus |
| Orientierung | geschlossene Modulunterseite flach auf dem Bett |
| obere Flächen | monotonic, möglichst global vorn–hinten |
| senkrechte Wände | normale Perimeter; kein globales Fuzzy Skin |
| Brim | optional 5–8 mm bei Warping |
| Elefantenfuß-Kompensation | 0,15–0,25 mm Startwert |

Temperaturen, Fluss, Kühlung und maximale Volumenrate müssen aus dem validierten Profil des konkreten PETG stammen.

## Qualifikationsreihenfolge

1. Walnusscoupon drucken. Das mittlere Bodenfeld ist die freigegebene Geometrie; daneben liegen feinere und gröbere Varianten.
2. Auf geschlossene Bahnen, angenehme Wandoberkante, erkennbare Astkontur, geringe Staubaufnahme und gute Reinigbarkeit prüfen.
3. Connectorpaar auf demselben Bett und in der Modulorientierung drucken; Fügegefühl und Istmaße erfassen.
4. Eckcoupon an Front, Mitte und Rücken der Schublade testen.
5. In der 3MF die ersten drei Schichten, Texturnuten, Wandtops, Connectoren, Keep-outs und Kennzeichnung kontrollieren.
6. Erst danach ein Hauptmodul drucken.

## Slicer-Prüfpunkte

- Keine Supports, schwebenden Inseln oder verlorenen Textursegmente.
- 3,2-mm-Wände bleiben lückenlos.
- Nuten erscheinen als flache Vertiefungen, nicht als offene Spalten.
- Wandwurzeln, Griffnuten, Connectoren und 0,6-mm-Wandtop-Randband bleiben glatt.
- Unterseitenkennzeichnung liegt nur in den ersten 0,40 mm und lässt umliegende Bettauflage unverändert.
- Keine XY-Kompensation verändert die nominelle 0,30-mm-Connector-Freigabe unbeabsichtigt.

## Realistische Holzwirkung

- Farbe und matte Streuung des Filaments liefern den Mikrofasereindruck; die CAD-Geometrie bildet nur druckbare Langmaserung und sparsame Äste.
- Monotone Top-Pfade möglichst parallel zur globalen Y-Richtung ausrichten.
- Kein globales Fuzzy Skin: Es würde Connectoren, Griffkanten und Komfortflächen gefährden.
- Optional nach einem Materialtest sehr dünne dunkelbraune Wash und kompatiblen matten Klarlack verwenden.

## Materialabschätzung

Die vier Hauptmodule plus Kamm besitzen zusammen rund 644,2 cm³ CAD-Festkörpervolumen. Der reale Filamentbedarf hängt von Wandgenerator, Infill, Überlappung, Fluss und Materialdichte ab; maßgeblich ist die Ziel-Slicer-Schätzung.
