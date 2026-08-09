CADQUERY – MODULARER WABEN-SETZKASTEN
======================================

CadQuery-Version beim Test: 2.8.0

Wichtigste Parameter in honeycomb_cadquery.py
----------------------------------------------
SIDE_LENGTH = 115.47        # Seitenkantenlänge; ergibt ca. 200 mm flat-to-flat
DEPTH = 55.0                # Tiefe der Wabe zur Wand
WALL_THICKNESS = 4.5
CORNER_RADIUS = 4.0

Aufhängung
----------
Die Aufhängeösen liegen jetzt INNERHALB der Wabe, nahe den beiden oberen
schrägen Innenwänden und nur in den letzten 5 mm nahe der Wand.
Die Schrauben sind von vorne durch die offene Wabe erreichbar.
Es gibt zwei Varianten:
- wabe_mit_aufhaengung.*
- wabe_ohne_aufhaengung.*

Damit müssen nicht alle Waben an die Wand geschraubt werden.

Modulare Verbindung
--------------------
Jede der 6 Außenflächen besitzt rückseitig zwei verdeckte halbe
Schwalbenschwanz-Nuten. Wenn zwei Waben Seite an Seite liegen, bilden
die beiden Nuten zusammen einen Doppelschwalbenschwanz-Kanal.

Der separate Schlüssel:
- waben_verbinder.stl / .step

wird von der Rückseite eingeschoben. Standardmäßig werden 2 Schlüssel
pro gemeinsamer Wabenseite verwendet. Dadurch bleiben die Vorderseiten
sauber und die Verbindung sitzt nahe der Wand.

CONNECTORS_PER_FACE kann auf 1 gesetzt werden, wenn weniger Verbinder
genügen. CONNECTOR_CLEARANCE ist das Druckspiel und kann an den Drucker
angepasst werden.

Beispiel
--------
setzkasten_7_waben_preview.step enthält eine 7-Waben-Anordnung als
CAD-Vorschau. In der Script-Konfiguration besitzen nur zwei der sieben
Zellen Aufhängeösen. So wird das Prinzip demonstriert, mehrere Waben über
die Verbinder zu koppeln und deutlich weniger Wandbefestigungen zu nutzen.

Hinweis zur Belastung
---------------------
Für leichte Deko kann eine kleine Zahl gut verteilter Wandanker genügen.
Bei größeren oder schwer beladenen Arrays sollten zusätzliche Anker-Waben
verwendet werden. Die Verbinder ersetzen nicht die Tragfähigkeitsprüfung
von Schrauben, Dübeln, Wand und Druckmaterial.

Textur
------
Diese CadQuery-Version hält die konstruktive Geometrie bewusst als sauberes
BRep/STEP. Bitmap-/Heightmap-Holzgravuren sind für CadQuery-BRep-Booleans
vergleichsweise teuer. Sinnvoller ist: präzise Geometrie in CadQuery erzeugen
und die vorhandene Höhenkarte anschließend nur für den STL/Mesh-Export als
Textur-Postprocessing anwenden. Dadurch bleibt STEP klein und editierbar.
