# MM-ART-010 Berlin — DRAFT digital-candidate-r4

Alle vier nativen Anycubic-Projektdateien enthalten vier nichtleere Werkzeugkörper und wurden in Anycubic Slicer Next nativ gesliced. Das schließt insbesondere den früher gemeldeten Geometrieverlust der rechten 3MF-Datei. Ein Druck oder eine kommerzielle Freigabe wird damit nicht autorisiert.

| Modus / Hälfte | 3MF-Dreiecke | Native Layer | Werkzeugwechsel | Ergebnis |
|---|---:|---:|---:|---|
| `boundary_crop` left | 79,356 | 26 | 8 | Pass |
| `boundary_crop` right | 65,980 | 23 | 3 | Pass |
| `context_outline` left | 163,300 | 26 | 8 | Pass; Laufzeit- und GUI-Prüfung offen |
| `context_outline` right | 150,244 | 23 | 3 | Pass |

Die linken Hälften tragen das kanonische, gestapelte metriMade-Logo mit 54. × 57.176 mm am eingefrorenen Adresspunkt. Es liegt 0.6 mm erhaben in Sky Blue/Werkzeug 4 und hält mindestens 12.253 mm Abstand zu einer Lichtöffnung. Karten-, Teilungs-, Steckverbinder- und Lichtgeometrie wurden gegenüber der freigegebenen Basis nicht neu gestaltet.

Der separate 84 × 88 mm Coupon enthält die Originalgröße des Logos in Oak/Sky Blue, zwei nichtleere Körper auf den semantischen Werkzeugen 1 und 4 und wurde mit 15 Layern nativ gesliced. Die Erkennbarkeit aus 2 m ist noch **nicht** physisch geprüft.

Alle 49 deterministischen Prüfungen im hashgebundenen Entwurfsvertrag bestehen. Sieben Prüfungen bleiben `REVIEW_REQUIRED`: 2-m-Erkennung, ACE/Purge, die Anycubic-Warnung zu schwebenden Bereichen beim linken Umlandteil, dessen längere Slice-Laufzeit, Steckverbinder/Licht/Wandnachweis sowie Wasserzeichen/Rechte/Freigabe. Beim linken Umlandteil beendete erst der kontrollierte 1800-s-Wiederholungslauf den nativen Slice; die erste 900-s-Ausführung lief ins Zeitlimit.
