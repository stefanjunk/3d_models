# OpenQuad CF5 - Entwurfspaket

Ein parametrischer, modularer 5-Zoll-Quadcopter-Prototyp aus vier
10x10x1-mm-CFK-Vierkantrohren, PA-CF-Knoten und gaengiger 30,5-mm-Elektronik.

**Status: PRELIMINARY / NOT FLIGHT PROVEN.** Das Paket ist eine
Forschungs-/Fertigungsgrundlage, keine Flugfreigabe. Vor Fertigung und Flug sind
OpenSCAD-Render, Slicer-/Meshpruefung, Coupons, mechanische Proof-Tests,
instrumentierter Propulsionstest und eine qualifizierte Systempruefung Pflicht.

## Schnellorientierung

1. `docs/forschungsbericht.md` lesen und Entscheidung Hybrid vs. kommerzieller
   Carbonrahmen treffen.
2. `BOM/bom_budget_de.csv` gegen aktuelle EU-Bestaende aktualisieren.
3. `CAD/openquad_cf5.scad` in OpenSCAD oeffnen, `part` waehlen, F6 rendern und
   Einzel-STLs exportieren.
4. Zuerst `arm_fit_coupon` drucken; niemals direkt den gesamten Satz.
5. `analysis/validate_design.py` und `analysis/check_scad_sync.py` ausfuehren.
6. `configs/printing_and_assembly.md`, `wiring_and_setup.md` und
   `acceptance_test_plan.md` gateweise abarbeiten.

## Paketinhalt

| Pfad | Inhalt |
|---|---|
| `CAD/openquad_cf5.scad` | parametrische Baugruppe und sieben Exportteile |
| `CAD/parts_manifest.csv` | Teilezahl, Material und Orientierung |
| `analysis/validate_design.py` | Geometrie-, Massen-, Energie- und Rohr-Screening |
| `analysis/check_scad_sync.py` | Abgleich CAD-/Analyseparameter und Delimitercheck |
| `output/design_metrics.json` | maschinenlesbare Kennwerte |
| `output/validation_report.md` | automatisch erzeugte Checkzusammenfassung |
| `BOM/bom_budget_de.csv` | Komponenten, Preise, Status und Quellen |
| `configs/` | Druck, Montage, Verdrahtung, Software und Gate-Tests |
| `docs/forschungsbericht.md` | vollstaendige Recherche und Entwurfsbegruendung |
| `docs/sources.md` | Quellen-/Marktverzeichnis, Stand 13.08.2026 |
| `output/pdf/` | gerenderter deutscher Forschungsbericht |

## OpenSCAD-Partselektor

`assembly`, `hub_bottom`, `hub_top`, `battery_deck`, `motor_saddle`,
`motor_plate`, `retention_plug`, `arm_fit_coupon`, `print_layout`.

`print_layout` ist nur eine visuelle Uebersicht. Fuer reproduzierbare Slicer-
Jobs jedes Teil einzeln exportieren und vervielfaeltigen.

## Reproduzierbare Analyse

```bash
python3 analysis/validate_design.py
python3 analysis/check_scad_sync.py
```

Die aktuelle Laufzeitumgebung hatte weder OpenSCAD noch einen Slicer. Deshalb
liegen bewusst keine behaupteten STL-, Slicerzeit- oder belastbaren
Filamentmassenwerte vor. Die Vorabschaetzung fuer Druckteile ist 110-135 g; sie
muss durch den echten Slicer und eine Waage ersetzt werden.

## Lizenz und Fremdkomponenten

Die OpenQuad-CAD-Quelle traegt `SPDX-License-Identifier: CERN-OHL-P-2.0`.
Software, Referenzprojekte, Elektronikfirmware und Herstellerdaten behalten ihre
jeweiligen Lizenzen/Marken. Vor Weitergabe oder Verkauf die konkrete Lizenz- und
Komponentenlage erneut pruefen.
