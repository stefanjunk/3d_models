# Holz-Höhenkarte

- `wood-source-master.png` ist das unveränderte 1024 × 1024 Pixel große, nahtlos wiederholbare 16-Bit-Masterbild aus dem beigefügten Heightmap-Relief-Skill.
- `wood-heightmap-16bit.png` ist die für die Geometrie abgetastete 768 × 768 Pixel große 16-Bit-Ableitung.

Die Pixelzahl ist bewusst nicht direkt die Mesh-Auflösung. `parameters.json` legt eine physische Abtastung von 0,45 mm fest; das entspricht der nutzbaren Größenordnung eines detailorientierten 0,4-mm-FDM-Profils, ohne mehrere Millionen unnötige Rasterflächen in den CAD-Featurebaum zu laden.

Zum Austausch gegen ein eigenes Holzbild:

1. ein nahtloses, richtungsabhängiges Graustufenbild verwenden;
2. Licht/Schatten nicht ungeprüft als Tiefe interpretieren;
3. Knoten und unregelmäßige Bandabstände erhalten – reine Parallelstreifen wirken nicht wie Holz;
4. 16-Bit-PNG bevorzugen;
5. `texture.heightmap` in `parameters.json` ändern und zuerst den Texturcoupon erzeugen.
