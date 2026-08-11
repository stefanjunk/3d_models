# Validierungsbericht – Waben-Haarspange Revision 4

Datum: 2026-08-10  
Status: **digital bestanden / physisch noch nicht qualifiziert**

## Änderungsumfang

| Merkmal | Revision 4 | Nachweis |
|---|---:|---|
| Wabenraster | 15 Zellen in 5 versetzten Reihen | Generatorparameter und CAD-Ansichten |
| vollständige / halbe Zellen | 12 / 3 | Feature-Audit; Halbzellen ausschließlich bei Z=0 |
| Nicht-Bett-Außenreihe | 3 vollständige Zellen | Generatorparameter und Draufsicht |
| Hexagon-Schlüsselweite | 10,0 mm | parametrische Quelle |
| nominale Fuge | 0,8 mm | tatsächliche Hex-Lattice-Abstände in der Quelle |
| Erhöhung über der Grundschale | 0,9 mm | parametrische Quelle |
| Zellorientierung | einheitlich, Spitzen entlang der Clip-Längsachse | Quell- und Feature-Audit |
| gedrehte Seitenreihe | entfernt | Quell- und Feature-Audit |
| Schulterblöcke über Gelenk/Verschluss | entfernt | Quell- und Renderprüfung |
| mittlere untere Schienenbreite | 12,5 mm | parametrische Quelle |

Die sichtbare Hoch-Tief-Kontur entsteht aus den vollständigen Zellen der äußersten Reihe, nicht aus gedrehten Zellen oder separaten Seitenblöcken. Der dünne 2,4-mm-Schalenbogen wurde auf X=4–56 mm verlängert, damit Gelenk- und Fangkörper nach Entfernung der Schulterblöcke einteilig verbunden bleiben.

## Digitale Geometrieprüfung

| Prüfung | Ergebnis | Status |
|---|---:|---|
| Außenmaß inklusive Waben | 63,0266 × 24,1301 × 26,6000 mm | bestanden |
| zulässiger Längenbereich | 50–65 mm | bestanden |
| Manifold-Kernelstatus | `NoError` | bestanden |
| zusammenhängende Körper | 1 | bestanden |
| STL-Dreiecke | 1.678 | bestanden |
| offene / nicht-manifold Kanten | 0 / 0 | bestanden |
| degenerierte / doppelte Dreiecke | 0 / 0 | bestanden |
| Volumen | 8.313,62 mm³ | bestanden |
| PETG-Massenschätzung bei 1,27 g/cm³ | 10,56 g | bestanden; Ziel <20 g |
| 3MF-Einheit | Millimeter | bestanden |
| 3MF-Objekte / Build-Items | 1 / 1 | bestanden |
| Revision-4-Feature-Audit | alle 21 Prüfungen bestanden | bestanden |

Detailwerte stehen in `mesh-audit-clip-r4.json`, `mesh-audit-coupon-r4.json`, `3mf-audit-r4.json`, `revision4-feature-audit.json` und `output/generation-metrics.json`.

## Funktions- und Fertigungsprüfung

- Der Export bleibt offen und nicht eingerastet; es gibt keine verschmolzenen Rastflächen oder eingedruckte Dauerspannung.
- Die Hauptflexur bleibt 1,6 mm dick und 8,0 mm breit. Das vorhandene Screening ergibt bei 3,5 mm Vergleichsauslenkung etwa 1,87 % Wurzeldehnung.
- Die Rastzunge bleibt 1,6 mm dick. Das vorhandene Screening ergibt bei 1,0 mm Vergleichsauslenkung etwa 1,10 % Wurzeldehnung.
- Kamm, Flexur, Rastzunge, Anschlag und die drei halben Wabenzellen beginnen bei `Z = 0`.
- Die mittlere untere Schiene verjüngt sich zwischen X=11–16 mm von 22 auf 12,5 mm und wächst zwischen X=47–52 mm wieder auf 22 mm.
- Die äußerste vollständige Wabenreihe reicht von Z=16,6 bis 26,6 mm. Ihr Zellquerschnitt wird beim Seitendruck schichtweise aufgebaut; der Reliefhub in Y beträgt 0,9 mm.
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
