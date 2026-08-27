# Decision Log – Schubladen-Organizer

## 2026-08-21 – R1.5 prozedurale Walnussvariante

- Nutzerwunsch: eine feinkörnige, möglichst realistische Holzvariante als Alternative zur Stahloberfläche.
- Freigegeben: Anforderungen und Konzept für mattes walnussbraunes PETG, 0,4-mm-Düse, 0,20-mm-Schichten und 0,44-mm-Linienbreite.
- Repräsentation: deterministische Vektor-/CAD-Nuten und dreifache Astkonturen statt Rasterbild oder Heightmap. Damit existieren weder Bildstretching noch anisotrope Skalierung.
- Mapping: Böden global vorn–hinten; Wandflächen entlang der längsten Achse; Wandtops als geschützte Mittellinie.
- Detaillierung: 0,10–0,20 mm tiefe Nuten, drei sparsame Äste über vier Module; Mikrofasern werden durch Filament und Toolpath erzeugt.
- Schutz: Außenwände, Connectoren, Junctions, Griffnuten, Gussets, Wandwurzeln, Bettauflage, Kennzeichnung und 0,6-mm-Wandtop-Ränder bleiben glatt.
- Speicher: ein Modul je Prozess und ein Patch je Boolean-Stufe; gemessener Peak 164,75 MiB.
- Mesh: 27.374–40.384 Dreiecke pro Hauptmodul. Zusätzliche verlustbehaftete Decimation ist `not-beneficial`; exakte Schnittstellen und die flache Textur bleiben geschützt.
- Connectoren: Coupon-STLs byte-identisch zu R1.4. Die gemeldete reale Nichtpassung ist nicht behoben und bleibt physisch zu qualifizieren.
- Ergebnis: 9/9 STLs und 4-Objekt-3MF digital PASS; DRAFT wegen offener Coupon-, Slicer- und finaler Freigabe.

## 2026-08-21 – R1.4 Stahloberfläche als Basis

- Viermodule-Architektur 227 × 357 × 64 mm, lange Schraubendreherzone, separater 8-fach-Kamm und acht Hardwarefächer übernommen.
- Bildgravur bereits durch prozedurale Geometrie ersetzt; R1.5 übernimmt diesen bildfreien, aspekt-sicheren Ansatz.
- Connectorform, 0,30-mm-Nennfreigabe, 2,6-mm-Boden, 3,2-mm-Wände, Griffnuten und gerundete Wandknoten unverändert übernommen.
