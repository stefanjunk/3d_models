# Validierungszusammenfassung

Stand: Revision 1.1.2, Finalqualität 0,30 mm, Status `experimental`.

| Datei | Dreiecke | Körper | Druckmaß mm | Volumen cm³ | Ergebnis |
|---|---:|---:|---:|---:|---|
| Gehäuse | 1.467.224 | 1 | 320,00 × 148,80 × 230,00 | 984,0 | bestanden |
| Schublade | 239.554 | 1 | 315,13 × 225,25 × 65,20 | 323,6 | bestanden |
| Top-Sorter | 1.012.370 | 1 | 320,00 × 230,00 × 68,00 | 698,5 | bestanden |
| Passungscoupon | 160 | 6 | 96,80 × 75,00 × 12,00 | 22,9 | bestanden |
| Carbon-Coupon | 65.532 | 1 | 90,00 × 20,00 × 55,00 | 15,4 | bestanden |

Zusätzlich bestanden alle vier exportierten Gravur-Cutter und alle drei untexturierten Basiskörper dieselben Topologieprüfungen. Insgesamt wurden zwölf Binär-STLs unabhängig neu eingelesen.

Automatisch geprüft wurden:

- exakte Binär-STL-Länge und vollständiger Re-Import;
- keine offenen Randkanten oder nicht-manifold Kanten;
- konsistente Dreiecksorientierung und keine degenerierten Dreiecke;
- positive, plausible Volumina;
- erwartete Anzahl zusammenhängender Körper;
- Bauraumprüfung aller fünf Fertigungsdateien gegen 420 × 420 × 500 mm.

Die Heightmap-Verarbeitung ist dokumentiert als:

- 1024 × 1024 Pixel, 16-Bit-Graustufen als Master;
- 36 × 36 mm periodische Kachel;
- 120 × 120 periodische Fertigungssamples, entsprechend 0,30 mm;
- 0,32 mm maximale Gravurtiefe und 0,08 mm Boolean-Überlappung;
- kontinuierliche Oberflächenkoordinate statt unabhängiger Flächenrotation.

Beim Drawer-Boolean entstanden an einer internen, bereits vereinigten Überlappung drei geschlossene Mikrosplitter mit zusammen 0,10394 mm³. Der Build verwirft solche Komponenten nur unter einer harten Grenze von 0,20 mm³; der verbleibende Schubladenkörper wurde danach erneut als ein wasserdichter Körper validiert.

Noch offen:

- Slicerprüfung mit dem tatsächlichen Anycubic-/Orca-Profil;
- reale Passungsprobe auf dem konkreten Drucker und Filament;
- Sichtprüfung der senkrechten und bettseitigen Carbon-Gravur;
- Anti-Kipp-Test mit vorgesehener Beladung;
- Langzeitverschleiß der Schubladen.

Die maschinenlesbaren Einzelwerte stehen in `output/validation-report.json` und `output/build_manifest.json`.
