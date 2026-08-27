# Cyber-Relief Revision 4

Die Fertigungsvorlagen werden reproduzierbar aus `pattern_geometry.json` mit
`generate_cyber_heightmaps.py` erzeugt. Die Deckelkarte ist eine bewusst
autorisierte zweistufige Liniengrafik und keine ungepruefte Bild-Luminanz:

- Weiss: 0,64 mm Hauptgravur.
- Mittelgrau: 0,32 mm Sekundaergravur.
- Schwarz: unveraenderte Deckelflaeche.

`cyber_side_tile_16bit.png` beschreibt die periodische 0,48-mm-Seitengravur.
`cyber_side_emboss_mask_16bit.png` trennt die 0,32-mm-Aussenrippe als eigene
Operation. Die umlaufenden Grundlinien treffen an der Naht identisch aufeinander;
die Naht liegt an der Scharnierseite.

Im editierbaren OpenCascade-Modell werden dieselben breiten, druckbaren Motive
analytisch als Vektor-/B-Rep-Geometrie erzeugt. Dadurch bleiben STEP-Export,
Mindestlinienbreiten und Boolesche Stabilitaet kontrollierbar. Die 16-Bit-Karten
sind die unabhaengige Mapping-, Dichte- und Aufloesungsreferenz.

Die Revision-4-Deckelkarte belegt rund 20,5 % der Pixel mit echten Gravurpfaden
und erreicht rund 85 % der dekorierbaren 5-mm-Zellen. Das bedeutet dichte
Flaechenverteilung ohne breite ausgeraeumte Taschen. Analyseberichte liegen in
`reports/cyber-lid-heightmap-analysis.json` und
`reports/cyber-side-heightmap-analysis.json`.
