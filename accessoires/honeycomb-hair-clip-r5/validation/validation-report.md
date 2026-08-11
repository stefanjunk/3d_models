# Validierungsbericht – Waben-Haarspange Revision 5

Datum: 2026-08-10  
Status: **digital bestanden / physisch noch nicht qualifiziert**

## Änderungsumfang

| Merkmal | Revision 5 | Nachweis |
|---|---:|---|
| Wabenraster | 17 Zellen, Reihenfolge 3 / 4 / 3 / 4 / 3 | Generatorparameter und CAD-Ansichten |
| vollständige / halbe Zellen | 14 / 3 | Feature-Audit; Halbzellen ausschließlich bei Z=0 |
| Nicht-Bett-Außenreihe | 3 vollständige Zellen | Generatorparameter und Draufsicht |
| Hexagon-Schlüsselweite | 10,0 mm | parametrische Quelle |
| nominale Fuge | 0,8 mm | tatsächliche Hex-Lattice-Abstände in der Quelle |
| Erhöhung über der Grundschale | 0,9 mm | parametrische Quelle |
| Zellorientierung | einheitlich, Spitzen entlang der Clip-Längsachse | Quell- und Feature-Audit |
| gedrehte Seitenreihe | entfernt | Quell- und Feature-Audit |
| Schulterblöcke über Gelenk/Verschluss | entfernt | Quell- und Renderprüfung |
| mittlere untere Schienenbreite | 12,5 mm | parametrische Quelle |
| Gelenk-/Clip-Endüberstand | 6,467 / 6,467 mm | parametrische Quelle und Feature-Audit |
| Raster-Längsskalierung | 0,957 | hält vollständige Endwaben innerhalb 65 mm |

Die sichtbare Hoch-Tief-Kontur entsteht aus vollständigen Zellen des einheitlichen Rasters, nicht aus gedrehten Zellen oder separaten Seitenblöcken. Die beiden versetzten Reihen enthalten jetzt je vier Zellen und kragen symmetrisch über Gelenk und Clip aus. Der dünne 2,4-mm-Schalenbogen verbindet weiterhin Gelenk und Fangkörper; die Rastbewegung liegt unterhalb der neuen Endwaben.

## Digitale Geometrieprüfung

| Prüfung | Ergebnis | Status |
|---|---:|---|
| Außenmaß inklusive Waben | 64,9346 × 24,1500 × 26,6000 mm | bestanden |
| zulässiger Längenbereich | 50–65 mm | bestanden |
| Manifold-Kernelstatus | `NoError` | bestanden |
| zusammenhängende Körper | 1 | bestanden |
| STL-Dreiecke | 1.784 | bestanden |
| offene / nicht-manifold Kanten | 0 / 0 | bestanden |
| degenerierte / doppelte Dreiecke | 0 / 0 | bestanden |
| Volumen | 8.472,89 mm³ | bestanden |
| PETG-Massenschätzung bei 1,27 g/cm³ | 10,76 g | bestanden; Ziel <20 g |
| 3MF-Einheit | Millimeter | bestanden |
| 3MF-Objekte / Build-Items | 1 / 1 | bestanden |
| Revision-5-Feature-Audit | alle 26 Prüfungen bestanden | bestanden |

Detailwerte stehen in `mesh-audit-clip-r5.json`, `mesh-audit-coupon-r5.json`, `3mf-audit-r5.json`, `revision5-feature-audit.json` und `output/generation-metrics.json`.

## Funktions- und Fertigungsprüfung

- Der Export bleibt offen und nicht eingerastet; es gibt keine verschmolzenen Rastflächen oder eingedruckte Dauerspannung.
- Die Hauptflexur bleibt 1,6 mm dick und 8,0 mm breit. Das vorhandene Screening ergibt bei 3,5 mm Vergleichsauslenkung etwa 1,87 % Wurzeldehnung.
- Die Rastzunge bleibt 1,6 mm dick. Das vorhandene Screening ergibt bei 1,0 mm Vergleichsauslenkung etwa 1,10 % Wurzeldehnung.
- Kamm, Flexur, Rastzunge, Anschlag und die drei halben Wabenzellen beginnen bei `Z = 0`.
- Die mittlere untere Schiene verjüngt sich zwischen X=11–16 mm von 22 auf 12,5 mm und wächst zwischen X=47–52 mm wieder auf 22 mm.
- Die äußerste vollständige Wabenreihe reicht von Z=16,6 bis 26,6 mm. Ihr Zellquerschnitt wird beim Seitendruck schichtweise aufgebaut; der Reliefhub in Y beträgt 0,9 mm.
- Die Endwaben reichen symmetrisch von X=-2,467 bis X=62,467 mm. Gegenüber den Schalenenden X=4 und X=56 ergibt das je 6,467 mm dekorativen Überstand.
- Der Clip-Fangkörper endet bei X=60,4 mm; die Wabenhülle endet bei X=62,467 mm. Die Entriegelungszunge bleibt von unten erreichbar.
- Die 0,8-mm-Fugen sind für eine 0,4-mm-Düse vorgesehen; tatsächliche Linienbreite und Gap-Fill-Verhalten hängen vom Slicerprofil ab.

Nicht durchgeführt: exakter Kobra-3-Max-Slicer-Dry-Run, G-Code-Prüfung, realer Testdruck, reale Rastbewegung und Tragetest.

## Noch erforderliche physische Akzeptanz

1. Rastcoupon 50 Zyklen ohne Weißbruch, Riss oder bleibende Setzung.
2. Vollclip öffnet und schließt, ohne den Hartanschlag zu überfahren.
3. Fugen bleiben nach dem Slicen offen; Halbzellen und vollständige Außenreihe erzeugen keine unerwünschten Supportinseln.
4. Alle Haar-/Hautkontaktkanten sind nach dem Entgraten stumpf und glatt.
5. 30 Minuten Halt am vorgesehenen Pferdeschwanz ohne schmerzhaftes Ziehen.
6. Nach 24 Stunden geschlossenem Zustand keine unzulässige PETG-Kriechverformung.

Bis diese Punkte bestanden und dokumentiert sind, bleibt das Modell `experimental` und nicht `qualified-local`.
