# Personalisierungs-Assets

Eigene Bilder fuer das Header-Relief hier als unveraenderte Quelldatei ablegen. Empfohlen:

- PNG, 16-Bit-Graustufen fuer echte Hoeheninformation;
- natuerliches Seitenverhaeltnis passend zu `insert_width / insert_height`;
- keine eingebrannten Lichtreflexe oder Schatten, wenn diese nicht als Relief erscheinen sollen;
- klare Motive mit mindestens etwa 1,2 mm breiten sichtbaren Merkmalen fuer eine 0,6-mm-Duese.

`tools/generate_demo_heightmap.py` erzeugt ein deterministisches Testmotiv. Die Build-Pipeline schreibt daraus eine separate 16-Bit-Build-Masterdatei, Vorschau, Metadaten und ein wasserdichtes Relief-STL.
