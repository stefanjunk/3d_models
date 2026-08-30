# Validierungszusammenfassung — R7-DRAFT-2

Status: **digitaler Maß- und Fertigungsentwurf bestanden; physische Freigabe blockiert**.

## Bestanden

- Alle vier Messwerte sind an benannte CAD-Beziehungen gebunden; Soll/Ist-Abweichung nominal 0,0 mm.
- Ausgewählter Fangkörper und Datumplatte sind jeweils ein gültiger Einzelkörper ohne harte Überschneidung.
- STL-Prüfung: wasserdicht, konsistente Orientierung, positives Volumen.
- Fünf Standard-Core-3MFs: gültige Struktur, wasserdicht, positives Volumen.
- Fünf native Anycubic-Projekt-3MFs wurden mit vollständigem Maschinen-, Prozess- und PETG-Profilsatz erzeugt.
- Alle fünf nativen Anycubic-Projekt-3MFs wurden anschließend mit `slice-anycubic-next` erfolgreich gesliced und analysiert.
- Bewegte CAD-Masse der balanced-Auswahl: 24,444 g bei Ziel ≤ 25 g.
- Deterministischer Messbindungs-Regressionscheck: PASS.

## Warnungen und offene Gates

- Anycubic Slicer Next meldet für Hauptkörper und Datumplatte einen möglichen frei schwebenden Überhang. Finale Orientierung, Support und Schichtansicht müssen manuell geprüft werden.
- Minimal-Core-3MFs werden vom Anycubic-Headless-Modus als leere Platte abgelehnt; die nativen Dateien im Unterordner `models/3mf/anycubic/` bestehen den Zielslicer-Lauf.
- Schraubenidentität, Kopfmaß, Länge und Gewindeeingriff: NOT_RUN.
- Lochbildlehre, Führungsspiel und 100 Rastzyklen: NOT_RUN.
- Stromloser Vollweg-Kollisionstest: NOT_RUN.
- Je drei Purge-Zyklen bei niedriger, mittlerer und hoher Z-Position: NOT_RUN.
- Ein stationärer Unterbehälter und seine reale Landefläche sind noch nicht umgesetzt.
- Kein Upload und kein Druckstart wurden ausgeführt.

Die Detailberichte liegen unter `build/current/reports/`; die physische Reihenfolge
steht in `../PRINT-CHECKLIST-DE.md`.
