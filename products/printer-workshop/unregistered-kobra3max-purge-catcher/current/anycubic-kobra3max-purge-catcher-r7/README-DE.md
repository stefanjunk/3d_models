# Anycubic Kobra 3 Max Purge Catcher — R7-DRAFT-2

Dies ist die einzige aktive Fassung des Projekts. R7-DRAFT-1 wurde verworfen,
weil mehrere Messwerte nur als Parameter vorhanden waren und die erzeugte
Geometrie deshalb nicht vollständig den Maßen entsprach.

## Alle Maße in einem Modell ansehen

Diese Datei zeigt Datumplatte, Catcher und alle vier Messbezüge gemeinsam in
ihren Einbaukoordinaten:

[`build/current/models/3mf/anycubic/ANYCUBIC-R7-INSPECTION-measured-assembly-reference.3mf`](build/current/models/3mf/anycubic/ANYCUBIC-R7-INSPECTION-measured-assembly-reference.3mf)

**Nur ansehen und nachmessen – nicht drucken.** Vier abgesetzte, nicht zur
Fertigungsgeometrie gehörende Maßleisten sind exakt 17, 10, 37 und 40 mm lang.
Sie machen die Bindung der Benutzermaße in einer einzigen 3MF sichtbar. Das
eigentliche Bauteil bleibt aus Montagegrund in Datumplatte und Fangkörper
getrennt. Auch der unter `build/current/slices/anycubic-project-inspection-assembly-absolute/`
erhaltene G-Code ist nur Validierungsevidenz und darf nicht gedruckt werden.

## Welche 3MF ist die aktuelle?

Für Anycubic Slicer Next ist diese Datei maßgeblich:

[`build/current/models/3mf/anycubic/ANYCUBIC-R7-purge-catcher-body.3mf`](build/current/models/3mf/anycubic/ANYCUBIC-R7-purge-catcher-body.3mf)

Sie enthält die ausgewählte **balanced**-Geometrie und die vollständigen
Profile für Anycubic Kobra 3 Max, 0,4-mm-Düse, 0,20-mm-Prozess und Anycubic
PETG. Ein frischer Headless-Slice mit Anycubic Slicer Next 1.3.9.4 war
erfolgreich: 310 Schichten, etwa 60 Minuten und 17.953,6 mm³ Extrusionsvolumen.

Der Slicer meldet am Hauptkörper weiterhin einen möglichen frei schwebenden
Überhang. Deshalb ist vor einem Druck eine menschliche Schicht-/Supportprüfung
Pflicht. Es wurde nichts zum Drucker hochgeladen oder gestartet.

## Eingebrachte Maße

Koordinatenursprung ist die Mitte der unteren Wiper-Schraube auf der
Schraubenauflagefläche.

| Messwert | CAD-Bindung | Soll/Ist |
|---|---|---:|
| 17 mm | unteres Rundloch zur Mitte des oberen Langlochs | 17,0 / 17,0 mm |
| 10 mm | untere Schraubenmitte zur Purge-Ebene Z = −10 mm innerhalb der geschlossenen Fangzone | 10,0 / 10,0 mm |
| 37 mm | Schraubenachse zur Fangmittel-Ebene X = 37 mm | 37,0 / 37,0 mm |
| 40 mm | Heckausdehnung des Wipers als geschützter Bereich Y = −40 mm; neue Geometrie bleibt bei Y ≥ 0 | 40,0 / 40,0 mm |

Die maschinenlesbare Prüfung steht in
[`build/current/reports/geometry-validation.json`](build/current/reports/geometry-validation.json),
die Maßgrafik in
[`build/current/previews/r7-measured-datums.png`](build/current/previews/r7-measured-datums.png).

## Dateien für die Prüf-Reihenfolge

1. [`ANYCUBIC-R7-mount-pattern-gauge.3mf`](build/current/models/3mf/anycubic/ANYCUBIC-R7-mount-pattern-gauge.3mf) — zuerst drucken; 17-mm-Lochbild prüfen.
2. [`ANYCUBIC-R7-slide-clearance-coupon.3mf`](build/current/models/3mf/anycubic/ANYCUBIC-R7-slide-clearance-coupon.3mf) — 0,20/0,30/0,40-mm-Führung vergleichen.
3. [`ANYCUBIC-R7-latch-cycle-coupon.3mf`](build/current/models/3mf/anycubic/ANYCUBIC-R7-latch-cycle-coupon.3mf) — Rastung und 100 Zyklen prüfen.
4. [`ANYCUBIC-R7-wiper-datum-plate.3mf`](build/current/models/3mf/anycubic/ANYCUBIC-R7-wiper-datum-plate.3mf) — erst nach Schraubenidentifikation und Lochbildfreigabe.
5. [`ANYCUBIC-R7-purge-catcher-body.3mf`](build/current/models/3mf/anycubic/ANYCUBIC-R7-purge-catcher-body.3mf) — erst nach Coupon- und Slicer-Vorschau-Freigabe.

Die Standard-Core-3MFs direkt unter `build/current/models/3mf/` sind formal
gültige Austauschdateien. Anycubic Slicer Next 1.3.9.4 erkannte diese
Minimalpakete im Headless-Modus jedoch als leere Platte. Für den Anycubic daher
nur die Dateien im Unterordner `anycubic/` verwenden; diese wurden im
Zielslicer erfolgreich geprüft.

## Stand und Grenzen

- CAD-BRep, STL-Meshes und Core-3MF-Topologie: PASS.
- Anycubic-Projektexport und erneuter Zielslicer-Lauf aller fünf Druck-3MFs: PASS.
- Kombinierte Maß-Prüf-3MF: Mesh, Core-3MF und Zielslicer-Import/Slice PASS; ausdrücklich keine Druckdatei.
- Bewegte CAD-Masse aus PETG-Dichte 1,27 g/cm³: 24,44 g; Ziel ≤ 25 g.
- Schraubengröße, Kopfmaß, Schraubenlänge und Gewindeeingriff: noch offen.
- Vollständige Bett-/Kopf-/Kabel-/Wiper-Kollision über den Maschinenweg: noch offen.
- Lochbild-, Führungs-, Rast-, Vollweg- und Purge-Tests: noch nicht physisch ausgeführt.
- Ein stationärer Unterbehälter ist in diesem Maß- und Interface-Entwurf noch nicht enthalten.
- Finale Kennzeichnung und Freigabe bleiben blockiert, bis die physischen Gates bestanden sind.

Der vollständige Prüfablauf steht in [`PRINT-CHECKLIST-DE.md`](PRINT-CHECKLIST-DE.md),
die Zusammenfassung in [`reports/VALIDATION-SUMMARY-DE.md`](reports/VALIDATION-SUMMARY-DE.md).

## Reproduzieren

Die parametrische Quelle ist `src/generate_r7_z_rider.py`, ihre maßgeblichen
Werte stehen in `params/r7-z-rider-draft2.json`. Der Generator schreibt nur in
einen neuen, leeren Ausgabeordner. Die Anycubic-Projekt-3MFs werden anschließend
mit `src/export_anycubic_3mf.py` aus den geprüften STL-Körpern und einem
vollständigen Maschinen-/Prozess-/Filamentprofilsatz erzeugt.
Die kombinierte Maßreferenz erzeugt
`src/export_measured_assembly_reference.py`; auch sie verweigert das
Überschreiben vorhandener Ausgabedateien.
