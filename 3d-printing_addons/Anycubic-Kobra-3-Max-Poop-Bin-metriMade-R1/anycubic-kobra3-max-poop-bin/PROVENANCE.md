# Provenienz und Recherche — Revision R1

Stand: 2026-08-26

## Eigenständige Konstruktion

Die Geometrie wurde neu aus parametrischen Querschnitten, prozeduralen Voxelkörpern und dem vom Nutzer bereitgestellten Logo erzeugt. Es wurde kein Community-STL, kein fremdes CAD-Modell und keine fremde Mesh-Geometrie heruntergeladen, eingebettet, remixt oder nachgezeichnet.

Herstellerinformationen dienten ausschließlich als Fakten- und Schnittstellenreferenz:

- Anycubic Kobra 3 Max Produktseite: Bauraum 420 × 420 × 500 mm, Maschinenmaß 706 × 640 × 753 mm, Standarddüse 0,4 mm. <https://store.anycubic.com/products/kobra-3-max>
- Offizielle Purge-Wiper-Reparaturanleitung: zwei Befestigungsschrauben lösen; bei Montage Positionierbohrungen am Blech ausrichten und Schrauben festziehen. Ein Lochabstand wird nicht angegeben. <https://wiki.anycubic.com/en/fdm-3d-printer/kobra-3-max/purge-wiper-components-replace-guide>
- Offizielles ACE-2-Upgrade-Bundle: Purge Wiper für die Kobra-3-Max-Serie und zwei M3×7-Schrauben. <https://ca.anycubic.com/products/kobra-3-max-ace-2-pro-upgrade-bundle>
- Offizielle Fehlersuche zum Purge-Wiper-Auswurf, als Kontext für die Auswurfrichtung. <https://wiki.anycubic.com/en/fdm-3d-printer/kobra-3-max/troubleshooting-abnormal-discharge-of-purge-wiper-material>

Offizielle Produkt- und Reparaturbilder wurden nur visuell auf Einbaulage, Auswurfrichtung und das Vorhandensein der Befestigungspunkte geprüft. Sie sind nicht im Projektpaket enthalten.

## Nutzer-Asset

- Datei: `evidence/metrimade-lockup-horizontal-color.svg`
- SHA-256: `030602129f236af1fa2bfb9a016831be60be10acec82587b5d352f65824db2b5`
- Farben: Navy `#112431`, Teal `#08777D`, Aqua `#7FD5D3`, Sand `#C7AB82`
- Das SVG enthält Pfade statt einer externen Schriftdatei.
- Der zusätzliche Text `metrimade.com` wird mit einer im Generator definierten 5×7-Pixelschrift erzeugt.

Die Rechte am Logo und an der Marke werden vom Nutzer vorausgesetzt und wurden nicht unabhängig geprüft.

## Werkzeug- und AI-Hinweis

Konzeptzerlegung, parametrische Generatorlogik, Dokumentation und Prüfskripte wurden AI-unterstützt erstellt. Die exportierte Geometrie wurde lokal deterministisch aus der dokumentierten Quelle erzeugt. NumPy, Pillow und Matplotlib wurden als Werkzeuge verwendet; deren Code oder Assets werden nicht in die Geometrie eingebettet.

