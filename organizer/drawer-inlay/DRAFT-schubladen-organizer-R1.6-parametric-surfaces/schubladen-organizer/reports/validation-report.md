# Validierungsbericht – R1.6 Micro-Cast (DRAFT)

## Ergebnis

Der profilselektierbare R1.6-Build wurde mit `--surface micro-cast` vollständig erzeugt. Alle neun STL-Dateien sind geschlossen, manifold, einteilig und positiv volumig. Die positionierte Vierobjekt-3MF besteht CRC- und Hüllenprüfung. Die Variante bleibt DRAFT, weil Linienmaskierung, Haptik, Reinigbarkeit, Connectorpassung und exakte Ziel-Slicer-Pfade physisch beziehungsweise im Ziel-Slicer geprüft werden müssen.

## Oberflächensystem

| Fläche | Facetten | Soll-Erhebung | beobachtete Erhebung | Materialabtrag |
|---|---:|---:|---:|---:|
| Innenböden | 19.630 | ≤ 0,24 mm | 0,231 mm | 0,00 mm |
| innere Wandflächen | 51.752 | ≤ 0,20 mm | 0,194 mm | 0,00 mm |
| Wandoberseiten | 0 | 0,00 mm | 0,000 mm | 0,00 mm |

- Repräsentation: `deterministic-additive-band-limited-micro-cast-facet-field`
- Seed: `160824`
- Raster: 1,60 mm; mehrskaliges kontinuierliches Höhenfeld mit gemeinsam genutzten Knoten
- Operation: ausschließlich additiv; 0,06 mm positive Einbettung in den Kern, keine eingeschnittenen Dimples oder Löcher
- Wandoberseiten: Geometrietextur deaktiviert und glatt
- Glatt geschützt: Außenwände, Connectoren, Junctions, Griffnuten, Gussets, Wandwurzeln, Bettauflage und Kennzeichnung
- Material-/Slicer-Anteil: mattes Filament und monotone Top-Pfade übernehmen Sub-Linienbreiten-Detail; optionales Ironing oder mildes Wand-Fuzzy-Skin erst nach Coupon

## Mesh- und Ressourcenprüfung

| Datei | Dreiecke | Ergebnis |
|---|---:|---|
| Driver vorn | 37.722 | PASS |
| Driver hinten | 37.258 | PASS |
| Hardware vorn | 55.594 | PASS |
| Hardware hinten | 47.230 | PASS |
| Oberflächencoupon | 3.756 | PASS |
| Kamm / Eckcoupon | 612 / 100 | PASS |
| Connector male / female | 152 / 144 | PASS |

Kein strukturiertes STL benötigte eine Sliver-Kollapsreparatur. Die Meshprüfung meldet für alle neun Dateien 0 Boundary-, Non-Manifold-, Winding-, Zero-Area- und Duplicate-Face-Fehler. Funktionsflächen wurden nicht global decimiert.

- Peak-RSS: 276,03 MiB
- Ziel: 1.536 MiB; Stop: 3.072 MiB
- Triangle-Review-Grenze: 1.000.000 je Modul
- größtes Modul: 55.594 Dreiecke

## Funktionsregression

- Baugruppenhülle: 227 × 357 × 64 mm
- Boden / Basiswand: 2,6 / 3,2 mm; durch den rein additiven Ansatz vollständig erhalten
- Connector-Nennfreigabe: 0,30 mm
- Male- und Female-Connector-Coupons: SHA-256 byte-identisch zu R1.4
- Organizerlayout, Fächer, Kamm, Griffnuten, Connectorgeometrie und geerbtes `steel`-Profil: nicht umkonstruiert

## Offene Freigabepunkte

1. `micro-cast`-Coupon in mattem Zielmaterial drucken und unter drei Lichtwinkeln mit einer glatten Referenz vergleichen.
2. Verringerte Kohärenz der Drucklinien, fehlende sichtbare Löcher, glatte Wandtops, Wischreinigung und Staubretention prüfen.
3. Optionales Topmost-Ironing als Coupon-A/B-Test prüfen; mildes Fuzzy Skin höchstens lokal an vertikalen Wänden testen.
4. Connectorpaar drucken und die bekannte reale Nichtpassung separat vermessen.
5. Eckcoupon in der realen Schublade und 3MF im Ziel-Slicer prüfen; erste drei Schichten, Wandpfade, Keep-outs und Kennzeichnung kontrollieren.
