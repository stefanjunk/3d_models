# Barfußschuh V6.1 – Upper Fit Fix

V6.1 korrigiert einen Fehler der ursprünglichen V6-Oberteile:

- Die untere Oberteilbreite wurde bisher aus einer unabhängigen Upper-Tabelle erzeugt.
- Dadurch war sie im Vorfuß typischerweise 6–11 mm schmaler als die vorgesehene Sohlen-/Lippen-Schnittstelle.
- Zusätzlich begann das alte Oberteil erst bei y≈5,25 mm und endete bei y≈266,35 mm. Dadurch entstanden sichtbare flache Abschlüsse vorne/hinten.

## Änderungen

1. Die unteren 10 mm des Oberteils werden jetzt direkt aus der Sohlenbreite und Sohlenmittellinie abgeleitet.
2. Pro Seite wird ein definierter Inset von 4,0 mm verwendet; das liegt innerhalb der TPU-Lippe.
3. Erst oberhalb dieses Anschlussbereichs blendet die Geometrie in den anatomischen Upper-Last über.
4. Ferse und Zehen schließen weich auslaufend statt durch die alten hohen planaren Endkappen.
5. Infill-envelope, Fuzzy-Shell und Reinforcement-Frame werden aus derselben Schnittstelle erzeugt.

## Was zuerst drucken?

Nicht sofort den kompletten Schuh.

1. Linke Sohle `v6_sole_left.3mf` slicen und Passform der Fußkontur prüfen.
2. Im Slicer einen 20–25 mm langen Ausschnitt im Vorfußbereich aus Sohle und gewünschtem V6.1-Upper erzeugen und als Interface-Test drucken.
3. Erst wenn der Upper sauber unter die Lippe passt, den vollständigen Upper drucken.

Empfohlener erster Upper: `v6_1_upper_fuzzy_shell_left.stl`, weil er weniger slicerabhängig ist als Infill-only.

Die Infill-only-Variante sollte erst nach dem Interface-Test folgen.

## Validierung

Alle drei korrigierten linken Oberteile sind:

- ein zusammenhängendes Mesh
- wasserdicht/manifold
- in Y bis an Ferse und Zehe geführt
- am unteren Anschluss aus der Sohlengeometrie abgeleitet

Details stehen in `VALIDATION_V6_1_UPPER.json`.
