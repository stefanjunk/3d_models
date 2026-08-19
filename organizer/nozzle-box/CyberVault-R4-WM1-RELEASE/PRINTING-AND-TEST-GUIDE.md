# CyberVault R4 – Druck- und Prüfhinweise

Status: **Finaler Release `CYBERVAULT-R4-CAD-A-WM1`**. Die 0,35-mm-Düsenpassung sowie die grundlegende Funktion von Scharnier und Rastverschluss sind am geometrisch unveränderten R3-Interface physisch bestätigt. Das neue R4-Relief selbst ist noch nicht physisch geprüft; diese Nachweisgrenze bleibt trotz Release-Freigabe bestehen.

## Druckvorbereitung

1. Bevorzugt `exports/release/cyber_nozzle_case_R4.3mf` unverändert in Millimetern importieren. Alternativ das kombinierte Print-in-place-STL verwenden.
2. Ungefülltes PETG, 0,4-mm-Düse und 0,16-mm-Schichten einsetzen. Das beim bestandenen Passcoupon verwendete Fluss-, Temperatur-, First-Layer- und Elephant-Foot-Profil beibehalten.
3. Exakt zwei Modellobjekte beziehungsweise Meshkomponenten bestätigen. Modell nicht automatisch drehen.
4. Supports und durchgehenden Brim deaktivieren. Kein Material darf Scharnier-, Deckel- oder Rastspalten verbinden; optionale Mouse-Ears nur an scharnierfernen Außenkanten.
5. Die Schichtvorschau prüfen: Hauptgravuren am Deckel reichen über vier Schichten (0,64 mm), Sekundärgravuren über zwei (0,32 mm), Seitenvertiefungen maximal über drei (0,48 mm). Die 18 Wasserzeichenkonturen müssen in allen drei geprüften Unterseitenhöhen offen bleiben.

Die gravierte Deckelaußenseite liegt in der Print-in-place-Orientierung auf dem Druckbett. Eine saubere, nicht überquetschte erste Lage ist daher entscheidend für offene Linien, exakte Schrift und das Freibleiben der beweglichen Fugen.

## Nach dem Druck

- Vollständig auf Raumtemperatur abkühlen lassen.
- Scharnier von beiden Enden mit kleinen Winkeln lösen; kein Messer oder Schraubendreher in die Fugen treiben.
- Einmal langsam bis 180° öffnen und auf Scheuern prüfen.
- Rastverschluss zunächst 25-mal leer betätigen. Weiße Stresslinien, Risse oder bleibende Verformung sind Abbruchkriterien.
- Relief prüfen: `CYBERVAULT`, `NOZZLE ARRAY` und `QSW-12` müssen normal herum lesbar sein; Reaktorkern, Paneele, Seitenlinien und Rippen dürfen keine losen Inseln oder verschweißten Taschen zeigen.
- Alle zwölf kalten, gereinigten Düsen einsetzen. Gruppenbeschriftungen prüfen und den geschlossenen Kasten nur über einer gepolsterten Fläche vorsichtig umdrehen.

Für eine erweiterte lokale Qualifikation gelten 100 dokumentierte Scharnier-/Rastzyklen als Vorprüfung; Zielwert bleiben 1000 Zyklen. Ergebnisse zusammen mit Filament und Profil dokumentieren.

## Korrekturregeln

- Klemmt das Scharnier, zuerst Fluss, erste Lage und Elephant-Foot korrigieren. Freigänge nur in 0,05-mm-Schritten ändern und danach neu validieren.
- Ist die Rastkraft zu hoch, Rastarm nicht heiß nachformen; Armstärke beziehungsweise Untergriff parametrisch anpassen.
- Schließen Gravurlinien in der Vorschau, keine horizontale XY-Skalierung des Gesamtmodells verwenden. First-Layer-Kompensation und Linienbreite kalibrieren.
- Fehlt Reliefkontrast, zunächst Beleuchtung beziehungsweise optionale Farbfüllung testen; Relief nicht ohne erneute Restwand- und Kollisionsprüfung tiefer skalieren.

Nur vollständig abgekühlte Düsen lagern. PETG ist kein Hitzeschutz.
