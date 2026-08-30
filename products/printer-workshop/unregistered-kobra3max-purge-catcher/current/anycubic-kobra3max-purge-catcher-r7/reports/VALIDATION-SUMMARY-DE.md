# Validierungszusammenfassung — R7-DRAFT-2

Status: **REJECTED_BY_USER – interne Digitalprüfungen bestanden, realer Fit nicht nachgewiesen und vom Benutzer verneint**.

Die früheren PASS-Aussagen gelten nur für Topologie, Slicer-Import und intern
definierte CAD-Beziehungen. Sie dürfen nicht als Einbau- oder Druckfreigabe
interpretiert werden.

## Bestanden

- Alle vier Messwerte sind an benannte CAD-Beziehungen gebunden; Soll/Ist-Abweichung nominal 0,0 mm.
- Ausgewählter Fangkörper und Datumplatte sind jeweils ein gültiger Einzelkörper ohne harte Überschneidung.
- STL-Prüfung: wasserdicht, konsistente Orientierung, positives Volumen.
- Fünf Standard-Core-3MFs: gültige Struktur, wasserdicht, positives Volumen.
- Fünf native Anycubic-Projekt-3MFs wurden mit vollständigem Maschinen-, Prozess- und PETG-Profilsatz erzeugt.
- Alle fünf nativen Anycubic-Projekt-3MFs wurden anschließend mit `slice-anycubic-next` erfolgreich gesliced und analysiert.
- Die kombinierte Maßreferenz besteht den STL-Audit mit sechs wasserdichten Komponenten sowie Core-3MF-Prüfung und nativen Anycubic-Import/Slice. Sie ist `REFERENCE_ONLY_DO_NOT_PRINT`.
- Bewegte CAD-Masse der balanced-Auswahl: 24,444 g bei Ziel ≤ 25 g.
- Deterministischer Messbindungs-Regressionscheck: PASS.

## Warnungen und offene Gates

- Benutzerkorrektur vom 30. August 2026: Die Modelle werden nicht passen; R7-DRAFT-2 ist deshalb vollständig vom Druck zurückgezogen.
- Es existiert kein Modell der realen Wiper-Schale, Metallablage, Rollen, Kabel- und Bett-Hüllkurve. Der Zubehörkörper wurde nur gegen selbst definierte Referenzebenen geprüft.
- 37 mm wurden ohne bestätigten Endpunkt zur Catcher-Mitte, 40 mm zu einem einseitigen Referenz-Keep-out und 10 mm lediglich zu einer Ebene innerhalb einer 28 mm hohen Fangzone abstrahiert. Diese Beziehungen beweisen keinen Fit.

- Anycubic Slicer Next meldet für Hauptkörper und Datumplatte einen möglichen frei schwebenden Überhang. Finale Orientierung, Support und Schichtansicht müssen manuell geprüft werden.
- Die montierte Maßreferenz enthält absichtlich getrennte Maßleisten und schwebende Einbaugeometrie; ihre Slicer-Warnung bestätigt zusätzlich, dass sie nicht als Druckplatte zu verwenden ist.
- Minimal-Core-3MFs werden vom Anycubic-Headless-Modus als leere Platte abgelehnt; die nativen Dateien im Unterordner `models/3mf/anycubic/` bestehen den Zielslicer-Lauf.
- Schraubenidentität, Kopfmaß, Länge und Gewindeeingriff: NOT_RUN.
- Lochbildlehre, Führungsspiel und 100 Rastzyklen: NOT_RUN.
- Stromloser Vollweg-Kollisionstest: NOT_RUN.
- Je drei Purge-Zyklen bei niedriger, mittlerer und hoher Z-Position: NOT_RUN.
- Ein stationärer Unterbehälter und seine reale Landefläche sind noch nicht umgesetzt.
- Kein Upload und kein Druckstart wurden ausgeführt.

Die Detailberichte liegen unter `build/current/reports/`; die physische Reihenfolge
steht in `../PRINT-CHECKLIST-DE.md`.
