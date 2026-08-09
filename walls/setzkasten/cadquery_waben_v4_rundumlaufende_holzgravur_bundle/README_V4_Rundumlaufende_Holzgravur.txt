CadQuery V4 – echte rundumlaufende Holzgravur

Neu in V4:
1. Höhere Auflösung
   - TEXTURE_HEIGHTMAP_PIXELS = 1024
   - TEXTURE_SUBDIVISIONS = 6

2. Holzgravur läuft wirklich rund um die Wabe
   - Die Maserung besitzt eine feste Vorzugsrichtung entlang der Wabentiefe (Z)
   - Die zweite Texturachse läuft kontinuierlich um den kompletten Umfang
   - Keine flächenweise Neuausrichtung mehr

3. Eckrundungen werden mit texturiert
   - Die Seiten-Textur wird nicht mehr nur auf die exakt planaren Flächen gelegt
   - Auch die gerundeten vertikalen Eckübergänge werden erfasst
   - Die Gravur wird entlang der Vertex-Normalen in das Material gedrückt

Wichtige technische Änderung:
- Für die Seitenflächen wird jetzt eine kontinuierliche Umfangs-UV-Abbildung benutzt.
- Die Gravur auf den Seiten (inkl. Eckrundungen) folgt damit einem durchgängigen,
  umlaufenden Mapping.

Dateien:
- honeycomb_cadquery_v4.py
- wood_wall_source.png
- wood_wall_engraving_heightmap_v4.png

Hinweis:
Die STL-Neuberechnung mit dieser sehr hohen Auflösung ist rechenintensiv.
Wenn gewünscht, können darauf basierend texturierte Export-STLs erzeugt werden.
