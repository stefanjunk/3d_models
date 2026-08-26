# Integration der Muster in eigene Projekte

## Empfohlener Ablauf

1. Funktionsprinzip und passende Variante über Katalog oder `query_catalog.py` auswählen.
2. `print_plate.stl` unverändert drucken und reale Passung prüfen.
3. Einzelkörper aus `parts/` importieren oder `model.scad` als parametrische Quelle verwenden.
4. Nur Anschlussplatten, Länge, Breite und projektbezogene Befestigungen anpassen.
5. Funktionskritische Achsen, Kugeldurchmesser, Federstärken und Toleranzen als benannte Parameter erhalten.
6. Nach jeder Booleschen Vereinigung Bohrungen, Spalte und Bewegungsräume erneut messen.
7. Projektteil erneut drucken und zyklisch testen.

## STL-Import

Die Einzelkörper-STLs sind auf ihren jeweiligen Mindestpunkt `[0,0,0]` verschoben. `components.json` enthält die ursprüngliche Position auf der Druckplatte und die verwendete Translation. Für eine Montagevorschau ist `preview.png` maßgebend; für eine druckfertige Anordnung `print_plate.stl`.

## Parametrischer Import

OpenSCAD-Anwender können `library/fdm_mechanisms.scad` direkt mit `use` laden. Andere CAD-Systeme können die Einzelkörper importieren oder die Geometrie anhand der dokumentierten Parameter rekonstruieren. Für lasttragende Bauteile sollten Anschlussflächen und Lastpfade in einem B-Rep-System neu aufgebaut werden, während das Muster nur die Kinematik vorgibt.

## Was nicht blind skaliert werden sollte

- Spiel und Interferenz
- Federstegdicke
- Schrauben- und Muttertaschen
- Zahnmodul und Achsabstand
- Kugel-Pfannen-Verhältnis
- Gewindetiefe und -steigung
- Mindestwand um Lagerbohrungen

Eine uniforme Skalierung verändert diese Größen und kann die Funktion zerstören.
