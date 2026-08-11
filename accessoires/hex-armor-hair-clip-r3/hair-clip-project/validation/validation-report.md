# Validierungsbericht – Hexagon-Haarspange Revision 3

Datum: 2026-08-10  
Status: **digital bestanden / physisch noch nicht qualifiziert**

## Änderungsumfang

| Merkmal | Revision 3 | Nachweis |
|---|---:|---|
| vollständige obere Hexagone | 23 Zellen in 3 versetzten Reihen | Generatorparameter und CAD-Ansichten |
| vollständige Hexagone auf der Nicht-Bettseite | 8 Zellen | Generatorparameter und Seitenansicht |
| Hexagon-Schlüsselweite | 8,0 mm | parametrische Quelle |
| nominale Rille | 0,8 mm | parametrische Quelle; entspricht zwei 0,4-mm-Düsenbreiten |
| Erhöhung über der Grundschale | 0,9 mm | parametrische Quelle |
| Randabschluss | nur ganze Zellen, etwa 0,9–1,1 mm Überstand | STL-Grenzen gegenüber R2-Grundkörper |
| mittlere untere Schienenbreite | 12,5 mm | parametrische Quelle |
| Breite an Gelenk/Rastclip | 22,0 mm | parametrische Quelle |
| Mechanik | Flexur, Zähne, Rastzunge und Coupon funktional unverändert | Quellvergleich; nur untere ungenutzte Breitenzone geändert |

Die dritte obere Reihe ist absichtlich vollständig und erweitert die Armor-Hülle auf 25,6 mm. Der 22,0-mm-Strukturkörper bleibt unverändert breit. Die Zellen sind nicht an der Schalen- oder Endkontur abgeschnitten.

## Digitale Geometrieprüfung

| Prüfung | Ergebnis | Status |
|---|---:|---|
| Außenmaß inklusive Armor | 62,5848 × 26,0885 × 25,6000 mm | bestanden |
| zulässiger Längenbereich | 50–65 mm | bestanden |
| Manifold-Kernelstatus | `NoError` | bestanden |
| zusammenhängende Körper | 1 | bestanden |
| STL-Dreiecke | 2.564 | bestanden |
| offene / nicht-manifold Kanten | 0 / 0 | bestanden |
| degenerierte / doppelte Dreiecke | 0 / 0 | bestanden |
| Volumen | 9.402,52 mm³ | bestanden |
| PETG-Massenschätzung bei 1,27 g/cm³ | 11,94 g | bestanden; Ziel <20 g |
| 3MF-Einheit | Millimeter | bestanden |
| 3MF-Objekte / Build-Items | 1 / 1 | bestanden |
| Revision-3-Feature-Audit | alle 15 Prüfungen bestanden | bestanden |

Detailwerte stehen in `mesh-audit-clip-r3.json`, `mesh-audit-coupon-r3.json`, `3mf-audit-r3.json`, `revision3-feature-audit.json` und `output/generation-metrics.json`.

## Funktions- und Fertigungsprüfung

- Der Export bleibt offen und nicht eingerastet; es gibt keine verschmolzenen Rastflächen oder eingedruckte Dauerspannung.
- Die Hauptflexur bleibt 1,6 mm dick und 8,0 mm breit. Das frühere Screening ergab bei 3,5 mm Vergleichsauslenkung etwa 1,87 % Wurzeldehnung.
- Die Rastzunge bleibt 1,6 mm dick. Das frühere Screening ergab bei 1,0 mm Vergleichsauslenkung etwa 1,10 % Wurzeldehnung.
- Kamm, Flexur, Rastzunge, Anschlag und die erste Armor-Reihe beginnen bei `Z = 0`.
- Die mittlere untere Schiene verjüngt sich zwischen X=11–16 mm von 22 auf 12,5 mm und wächst zwischen X=47–52 mm wieder auf 22 mm.
- Die zusätzliche Außenseitenreihe liegt bei Z=21,55–22,90 mm. Ihre kurzen lokalen Auskragungen betragen ungefähr 2,8 mm und benötigen eine reale Layer-Vorschau.
- Die 0,8-mm-Rillen sind für eine 0,4-mm-Düse vorgesehen; tatsächliche Linienbreite und Gap-Fill-Verhalten hängen vom Slicerprofil ab.

Nicht durchgeführt: exakter Kobra-3-Max-Slicer-Dry-Run, G-Code-Prüfung, realer Testdruck, reale Rastbewegung und Tragetest.

## Noch erforderliche physische Akzeptanz

1. Rastcoupon 50 Zyklen ohne Weißbruch, Riss oder bleibende Setzung.
2. Vollclip öffnet und schließt, ohne den Hartanschlag zu überfahren.
3. Rillen bleiben nach dem Slicen offen und die Randhexagone werden ohne unerwünschte Supportinseln aufgebaut.
4. Alle Haar-/Hautkontaktkanten sind nach dem Entgraten stumpf und glatt.
5. 30 Minuten Halt am vorgesehenen Pferdeschwanz ohne schmerzhaftes Ziehen.
6. Nach 24 Stunden geschlossenem Zustand keine unzulässige PETG-Kriechverformung.

Bis diese Punkte bestanden und dokumentiert sind, bleibt das Modell `experimental` und nicht `qualified-local`.
