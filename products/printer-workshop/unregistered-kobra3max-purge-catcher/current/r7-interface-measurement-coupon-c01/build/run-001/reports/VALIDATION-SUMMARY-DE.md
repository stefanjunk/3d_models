# R7-C01 – Validierungsübersicht

Status: **digitaler DRAFT-Druckkandidat; physischer Test ausstehend**.

- 11 Lochbildlaschen, jeweils zwei geschlossene Rundlöcher, exakt 17 mm
  Mitte–Mitte; Ø 2,8 bis 4,8 mm, kein Schlitz.
- 13/13 erwartete Komponenten, wasserdicht und konsistent orientiert;
  0 Rand-, Nichtmanifold-, degenerierte oder duplizierte Flächen.
- Bauraum 174 × 73 × 1,2 mm; Modellvolumen 8625,26 mm³; nominell etwa
  10,95 g bei 1,27 g/cm³ PETG.
- Neutraler Core-3MF besteht die Standardstrukturprüfung.
- Native Anycubic-3MF besteht den Rückslice in Anycubic Slicer Next 1.3.9.4:
  6 Schichten, 1994 s Prognose, ein Werkzeug, keine native Warnung.
- Der Standard-3MF-Prüfer folgt dem ausgelagerten Anycubic-Objektteil nicht.
  Dieser Diagnose-Fail bleibt sichtbar; der identische native 3MF-Hash wird
  vom Zielslicer erfolgreich verarbeitet.
- Der erste Slice mit relativem Quellpfad scheiterte im isolierten
  Arbeitsverzeichnis. Der zweite, neue Lauf mit absolutem Pfad besteht.
- Keine Druckerübertragung und kein Druckstart wurden ausgeführt.

Noch offen: reale Schraubenmaße, Gewindeeingriff, Kaltpass der ausgewählten
17-mm-Lasche, vollständige Maschinenhüllkurve und jede Vollteilgeometrie.
