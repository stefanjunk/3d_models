# Modularer Schreibtisch-Organizer – 3D-Druck

Das Design orientiert sich am zuvor erzeugten Konzeptbild: modern, weich gerundet, mit dezenten horizontalen Rippen und einer Reihe frei umsortierbarer Module.

## Enthaltene Teile

- `drawer_housing.stl` – Gehäuse für zwei Schubladen
- `drawer.stl` – einzelne Schublade; **2× drucken**
- `cubby_module.stl` – großes offenes Ablagefach
- `shallow_tray_module.stl` – flache Ablageschale mit Trennsteg
- `divided_bin_module.stl` – unterteiltes Stifte-/Werkzeugfach
- `pen_cup_module.stl` – schmales, hohes Stiftefach
- `connector_fit_test.stl` – kleines Verbindungstestteil; **2× drucken**
- `modular_desk_organizer.scad` – vollständig parametrische OpenSCAD-Datei
- `generate_stl.py` – Python-Generator der mitgelieferten STL-Dateien

## Abmessungen

Die Standardmodule haben einen Grundkörper von etwa **96 × 96 mm**. Das hohe Stiftefach ist ca. **64 × 96 × 110 mm**. Die außenliegenden Steckführungen ragen ca. 4 mm heraus.

## Stecksystem

Jedes Modul besitzt rechts eine vertikale Schwalbenschwanz-Zunge und links eine außenliegende Gegenführung. Zwei benachbarte Module werden von oben ineinander geschoben. Dadurch lässt sich die Reihenfolge schnell ändern, ohne Schrauben, Kleber oder zusätzliche Verbinder.

In der SCAD-Datei steuert `FIT` die Passung. Standard: `0.35 mm` pro Seite. Für sehr präzise PLA-Drucker kann `0.25–0.30` passen; PETG oder leicht überextrudierende Drucker eher `0.35–0.45`.

**Empfehlung:** zuerst `connector_fit_test.stl` zweimal drucken und die Passung testen.

## Druckempfehlung

- Layerhöhe: 0,20 mm
- Düse: 0,4 mm
- Wände: 3–4
- Infill: 15–20 %
- Material: PLA/PLA+ für einfache Schreibtischnutzung; PETG für höhere Zähigkeit
- `drawer.stl`, `divided_bin_module.stl`, `pen_cup_module.stl`, `shallow_tray_module.stl`: Boden nach unten
- `drawer_housing.stl` und `cubby_module.stl`: vorzugsweise auf der Rückseite liegend drucken, sodass die große Frontöffnung nach oben zeigt. Je nach Slicer kann für die kleinen seitlichen Verbinder „Support nur vom Druckbett“ sinnvoll sein.

## OpenSCAD

Oben in `modular_desk_organizer.scad` kann `PART` gesetzt werden:

`layout`, `drawer_housing`, `drawer`, `cubby`, `shallow_tray`, `divided_bin`, `pen_cup`, `connector_test`

`TEXTURE = false` entfernt die Rippen und reduziert Druckzeit sowie Dateigröße.

## Hinweis zu den STL-Dateien

Die mitgelieferten STL-Dateien bestehen bei einigen Modulen aus mehreren sich berührenden bzw. überlappenden, jeweils geschlossenen Teilkörpern. Das ist für übliche FDM-Slicer wie OrcaSlicer, PrusaSlicer, Cura oder Anycubic Slicer in der Regel unproblematisch; beim Slicen werden die Volumenkörper gemeinsam verarbeitet. Die SCAD-Datei ist die sauberste parametrische Quelle, falls Maße oder Passungen geändert werden sollen.
