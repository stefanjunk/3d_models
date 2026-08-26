# Decision Log – Schubladen-Organizer

## 2026-08-22 – R1.6 parametrische Oberflächen

- Nutzerwunsch: zusätzliche außergewöhnlich realistische Carbonoberfläche, ohne vollständiges Redesign; Stahl aus R1.4 und eine rebuildbare Nulltextur sollen wählbar sein.
- Architektur: neue R1.6-Arbeitskopie; R1.4 und R1.5 bleiben unverändert. Ein Selektor wählt `carbon`, `carbon-wave`, `micro-cast`, `walnut`, `steel` oder `plain`, ohne Konfigurationsdateien umzuschreiben.
- Carbonrepräsentation: prozedurale 2×2-Twill-Zellen mit ±45°-Richtung, linsenförmigem Profil und getrennten Over/Under-Tiefen. Kein Foto, keine Heightmap, keine modellierten Mikrofasern.
- Prozessmaßstab: 0,40-mm-Düse, 0,44-mm-Linienbreite, 0,20-mm-Schicht. Nominaler Pitch 2,60–3,15 mm; Relief 0,075–0,18 mm.
- Schutz: Außenwände, Connectoren, Junctions, Griffnuten, Gussets, Wandwurzeln, Bettauflage und Kennzeichnung bleiben glatt. Kernmaße, Layout, Kamm und Connectoren sind unverändert.
- Materialwirkung: dunkles Satinmaterial und gerichtete Top-Pfade tragen Farbe und Glanz. Carbonoptik ist keine Aussage über Laminatsteifigkeit.
- Freigabe: digitaler Mesh-/3MF-Build, Profil-Coupon, Ziel-Slicer-Prüfung, Connector-Coupon und Schubladen-Eckcoupon erforderlich; bis dahin DRAFT.

## 2026-08-22 – Referenzabgeleitete zweite Carbonvariante

- Referenz: `libraries/carbonfiber1.png`; der erste sinusförmige Linienansatz wurde als unzutreffend verworfen und ersetzt.
- `carbon-wave` verwendet jetzt gepaarte breite 0°/90°-Tow-Zellen in alternierenden 2×2-Blöcken. Der Blockwechsel bildet den diagonalen Geweberhythmus der Referenz; horizontale Tows sind tiefer und optisch dominanter.
- Drei flache Längsmodulationen pro breitem Tow liefern Bündel-Highlights, ohne einzelne Carbonfilamente oder eine fotografische Heightmap zu modellieren.
- Ein kleiner endlicher Tow-Randtiefgang vermeidet tangentiale Float32-Booleanflächen; alle fünf exportierten strukturierten Körper benötigten danach null Sliver-Kollapsreparaturen.
- Vollbuild: neun von neun STLs PASS, 3MF CRC PASS, Connector-Coupons byte-identisch zu R1.4, Peak-RSS 939,31 MiB.

## 2026-08-22 – Lochfreie Micro-Cast-Variante

- Anlass: Das geerbte `steel`-Profil wirkte auf horizontalen Topflächen durch seine subtraktiven Dimples unruhig und löchrig. `steel` bleibt für Rebuilds unverändert erhalten; die neue Lösung ist die zusätzliche Option `micro-cast`.
- Ein erster additiver Kandidat aus getrennten flachen Kuppen wurde am gerenderten Coupon als blasenartig verworfen.
- Die gewählte Repräsentation ist ein deterministisches, bandbegrenztes 1,60-mm-Feld aus gemeinsam verbundenen Mikrofacetten. Mehrskaliges Value Noise steuert nur die Knoten; zufällig wechselnde Facet-Diagonalen verhindern ein Schachbrettbild.
- Lochschutz: Boden und Innenwände werden ausschließlich additiv mit positiver Einbettung aufgebaut; konfigurierter Materialabtrag ist überall 0,00 mm. Wandoberseiten erhalten keine Geometrietextur und bleiben glatt.
- Maßstab: maximal 0,24 mm Erhebung am Boden und 0,20 mm an Innenwänden. Poren- beziehungsweise Sub-Linienbreiten-Detail bleibt mattem Filament und optionalem, lokal begrenztem Slicer-Finish vorbehalten.
- Vollbuild: neun von neun STLs PASS, 37.258–55.594 Dreiecke je Hauptmodul, 3MF CRC PASS, Connector-Coupons byte-identisch zu R1.4 und Peak-RSS 276,03 MiB.

## Geerbte Oberflächen

- `walnut` übernimmt den prozeduralen R1.5-Grain/Knot-Generator und seine Parameter.
- `steel` übernimmt den prozeduralen R1.4-Dimple-Generator und seine Parameter.
- `plain` schaltet alle optionale Oberflächengeometrie ab und dient als Regressionsbaseline.
