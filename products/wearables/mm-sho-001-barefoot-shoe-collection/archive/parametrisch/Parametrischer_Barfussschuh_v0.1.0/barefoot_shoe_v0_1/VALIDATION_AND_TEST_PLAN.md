# Validierungs- und Testplan

## Digital bereits geprüft

Der Generator prüft für jede einzelne STL-Komponente:

- Einheiten und Bounding Box in Millimetern;
- Anzahl Punkte/Dreiecke;
- geschlossene Kanten: jede ungerichtete Kante exakt zweimal;
- keine Kante mit mehr als zwei angrenzenden Dreiecken;
- keine Dreiecke mit praktisch null Fläche;
- konsistente Orientierung und positives Volumen je Komponente;
- 3MF als gültiges ZIP-Paket mit Core-Modelldatei.

Diese Prüfung erkennt keine Materialfehler, versteckten Flächen-Selbstschnitt in jeder denkbaren Konfiguration oder falsche Slicer-Reparaturen. Das exakte Slicer-Projekt ist erst nach Angabe von Drucker, Slicer und TPU festlegbar.

## Abnahmereihenfolge

### G0 – Maße

- Papierausdruck der Einlagen-Schablone bei 100 %.
- 50-mm-Kontrollquadrat muss 50,0 mm messen.
- Im belasteten Stand: kein Zeh ragt über die Kontur; 9 mm Frontzugabe und etwa 3–4 mm seitliche Bewegungsreserve prüfen.
- Linken und rechten Fuß separat freigeben.

### G1 – Material- und Ösencoupon

Datei: `generated/test_coupons/tpu_lattice_and_eyelet_coupon.3mf`.

- Alle 3,2-mm-Bänder werden als zusammenhängende Pfade gesliced.
- Keine unverbundenen Inseln oder vom Slicer gelöschten Bänder.
- Öse nimmt 4-mm-Schnur ohne scharfe Innenkante auf.
- 100 kräftige manuelle Biegungen in beide Richtungen ohne Weißbruch, Delamination oder bleibenden Knick.
- Schnur schrittweise bis zur im Alltag erwarteten Handzugkraft belasten; keine Risse am Ring-/Gitterübergang. Wert protokollieren, nicht als allgemeine Traglast veröffentlichen.

### G2 – Sohlenprototyp

- Laufsohlenkontur, Innenlänge und Ballenstation mit Messschieber kontrollieren.
- 500 manuelle Vorfußbiegungen; Schichten und Rillenwurzeln beobachten.
- Trockengriff und Nassgriff auf ungefährlichen ebenen Testflächen vergleichen.
- 30 Minuten nur innen tragen; Druckstellen sofort markieren.
- Sohlenmasse und Dicke vor/nach kurzem Abriebtest dokumentieren.

### G3 – Textilvariante

- Probemuster aus billigem, ähnlich dehnbarem Stoff.
- Ferse darf beim Gehen nicht deutlich anheben; Zehen müssen aktiv spreizen können.
- Klebecoupon aus Original-TPU und Originalstoff nach vollständiger Aushärtung schälen und nass wiederholen.
- Erst danach endgültiges Obermaterial verkleben.

### G4 – gedruckte Netzvariante

- Slicer Schicht für Schicht an Zehenkuppel, Kehlkante, Ferse und Ösen prüfen.
- Support nur akzeptieren, wenn er durch die Netzöffnungen vollständig entfernbar ist.
- Innenfläche nach Supportentfernung auf scharfe Grate kontrollieren.
- Zunächst kurze Nutzung mit Socke; danach Haut, Nähte und Ösen kontrollieren.

### G5 – Nutzungserweiterung

- Tragezeit über mehrere Tage schrittweise erhöhen.
- Bei Schmerz, Taubheit, Scheuern, ungewöhnlicher Ermüdung oder Instabilität abbrechen und Ursache korrigieren.
- Outdoor, Laufen und nasse Oberflächen erst nach separaten Abrieb-, Haftungs- und Ermüdungstests.

## Noch offene Prozessdaten

Für eine endgültige 3MF-/Slicer-Freigabe werden benötigt:

- Druckermodell und nutzbarer Bauraum;
- Extruder (direkt/Bowden), Düse und Hotend;
- Slicer und Version;
- exaktes TPU-Produkt, Shore-Härte, Farbe und Trockenzustand;
- gemessener maximaler Volumenstrom;
- gewünschte Nutzung und Körpergewicht.
