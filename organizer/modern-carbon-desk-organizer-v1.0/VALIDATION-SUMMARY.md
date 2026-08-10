# Validierungszusammenfassung

Stand: Revision 1.0.0, Status `experimental`.

| Datei | Dreiecke | Körper | Druckmaß mm | Volumen cm³ | Ergebnis |
|---|---:|---:|---:|---:|---|
| Gehäuse | 18.446 | 1 | 320,68 × 148,80 × 230,00 | 982,3 | bestanden |
| Schublade | 386 | 1 | 316,00 × 224,50 × 65,20 | 320,8 | bestanden |
| Top-Sorter | 9.350 | 1 | 320,68 × 230,00 × 68,00 | 711,9 | bestanden |
| Passungscoupon | 160 | 6 | 96,80 × 75,00 × 12,00 | 22,9 | bestanden |
| Carbon-Coupon | 1.682 | 1 | 90,00 × 20,00 × 55,00 | 16,5 | bestanden |

Automatisch geprüft wurden:

- Binär-STL lässt sich vollständig neu einlesen.
- Keine offenen Randkanten oder nicht-manifold Kanten.
- Konsistente Dreiecksorientierung und keine degenerierten Dreiecke.
- Positive, plausible Volumina.
- Erwartete Anzahl zusammenhängender Körper.
- Jedes Fertigungs-STL passt in 420 × 420 × 500 mm.

Noch offen:

- Slicerprüfung mit dem tatsächlichen Anycubic-Slicerprofil.
- Reale Passungsprobe auf dem konkreten Drucker und Filament.
- Sichtprüfung der Carbon-Struktur als gedruckte senkrechte Wand.
- Anti-Kipp-Test mit der vorgesehenen Beladung.
- Langzeitverschleiß der Schubladen.

Die maschinenlesbaren Einzelwerte stehen in `output/validation-report.json`.
