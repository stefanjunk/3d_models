# Entscheidungsprotokoll

- **Grundform:** regelmäßiges, flach oben/unten orientiertes Sechseck. Dadurch entsteht unten eine echte horizontale Stellfläche und die Zellen bilden ein lückenloses Wabengitter.
- **Größe:** 168 × 145,49 × 72 mm außen; das passt auf viele 220-mm-Druckbetten und bietet etwa 149,5 × 129,5 × 67,2 mm nutzbaren Innenraum.
- **Verbindung:** universelle U-Brücken statt fester männlicher/weiblicher Kanten. Jede der sechs Seiten bleibt wahlfrei; zwei Clips pro gemeinsamer Kante begrenzen Verdrehung.
- **Rückseite:** standardmäßig offen, damit die Wand sichtbar bleibt. `back_panel_enabled: true` erzeugt weiterhin eine geschlossene 4,8-mm-Rückwand.
- **Wandmontage:** zwei sichtbare, 6 mm dicke Ösen sitzen bei x = ±27 mm und y = 54 mm nahe am oberen Rahmen. Kreisauflage und tangentiale Aussteifungen führen die Last in den Rahmen; Schrauben und Dübel bleiben wand- und lastspezifische Kaufteile.
- **Cliprichtung:** U-Brücken werden vor der Wandmontage von hinten eingesetzt. Ihre 2,4-mm-Kappen werden durch gleich dicke Distanzscheiben hinter den Befestigungsösen ausgeglichen.
- **Textur:** 0,6-mm-Gravur aus einer 16-Bit-Höhenkarte. Die Maserung läuft auf Innen- und Außenwänden entlang der Tiefe und wird nicht pro Fläche neu gedreht. Rückseite und Passflächen bleiben glatt.
- **Repräsentation:** präzise Basis als B-Rep/STEP, dichte Holzoberfläche erst im finalen Dreiecksmesh. Dadurch bleibt die parametrische Basis editierbar und die Rastertextur überlastet den CAD-Featurebaum nicht.
- **Material:** PETG als belastbarere Standardannahme; Holzfill ist eine dekorative, abrasive und herstellerspezifische Variante, die neu kalibriert werden muss.
- **Revision 1.1:** offene Rückwand, rahmennahe Ösen, rückseitige Clipmontage und Wandabstandshalter digital umgesetzt. Status bleibt experimentell bis Slicer-, Clip-, Wand- und Kriechversuche mit dem tatsächlichen Druckprozess bestanden sind.
