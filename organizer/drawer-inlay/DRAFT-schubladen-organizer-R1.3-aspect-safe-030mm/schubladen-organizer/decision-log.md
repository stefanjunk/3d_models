# Decision Log – Schubladen-Organizer

## 2026-08-11 – Anforderungen R0 freigegeben

- Nutzerfreigabe: „R0 freigeben“.
- Angenommene Standardwerte: Druckbett 220 × 220 mm, 0,4-mm-Düse, PETG.
- Schraubendreherzone: universelles 92 × 350-mm-Fach mit austauschbarem Kamm.
- Modularchitektur: vier Teile in einer 2×2-Teilung.
- Hardwarezone: exakt acht Fächer in zwei Spalten und vier Reihen.

## 2026-08-11 – Konzeptbild R0

- Erzeugungsmodus: integrierte Bildgenerierung, anschließend gezielte Bildkorrektur.
- Ergebnis: `concept-R0-v2.png`.
- Status: vom Nutzer mit „Konzept R0 freigegeben“ freigegeben.
- Darstellungsgrenze: Die Explosionsansicht zeigt acht Hardwarefächer eindeutig. In der perspektivischen Hauptansicht ist die vorderste Quertrennung optisch gedrängt. Für die Produktionsgeometrie gilt ausschließlich `design-spec.yaml`.

### Finaler Korrekturprompt

> Add the same shallow, FDM-printable industrial steel-plate relief language already visible on the compartment floors to the visible vertical wall bands: subtle rectangular plate seams and sparse small domed rivets on the inner wall faces and on the visible outer wall panels of both the assembled organizer and the exploded modules. Change only the surface relief on visible wall bands. Preserve exactly the composition, camera, four-module 2-by-2 architecture, one long screwdriver zone, removable comb, the eight-compartment hardware intent shown by the exploded modules, all compartment walls, finger scoops, connectors, gussets, proportions, graphite PETG material, floor relief, lighting, and background. Relief must remain shallow and printable. No text, labels, arrows, dimensions, logos, watermark, damage, rust, extra compartments, or geometry redesign.

## 2026-08-11 – Produktionskandidat R0 DRAFT

- Parametrische Grundgeometrie mit `manifold-3d` umgesetzt, weil in der lokalen Umgebung weder CadQuery/FreeCAD noch OpenSCAD oder Blender verfügbar waren.
- Baugruppe: 227 × 357 × 64 mm; vier einzeln auf 220 × 220 mm druckbare Module.
- Layout: 92-mm-Schraubendreherzone mit separatem Achtfach-Kamm; Hardwarezone 135 mm breit mit exakt 2 × 4 Fächern.
- Stabilität: 2,4-mm-Boden und -Trennwände, 2,8-mm-Außenwände, durchgehende Materialkreuzungen und Wurzelgussets.
- Verbinder: flache Puzzlelaschen mit 0,30 mm Nennspiel; separate Paarprobe erzeugt.
- Alle neun STL-Dateien bestehen die unabhängige Watertight-/Manifold-/Volumen-/Einzelkörperprüfung.

## 2026-08-11 – Austauschbares Höhenbildrelief

- Masterbild: `texture/steel-rivets-source.png`, eigens als nahtlose Graustufen-Displacement-Textur erzeugt.
- Fertigungskonvention: dunkle Plattenstöße werden 0,35 mm vertieft, helle Nieten 0,40 mm erhaben.
- Für robuste, speicherschonende Boolesche Operationen wird das 16-bit-Höhenbild über `src/vectorize_heightmap.py` in 1,5-mm-Rasterläufe umgewandelt.
- Das Relief kann über `config/relief-config.json` sowie `config/model-params.json` ausgetauscht, skaliert oder je Flächengruppe deaktiviert werden.
- Mindest-Reststärke an reliefierten Böden/Wänden: rechnerisch mindestens 2,0 mm.

## 2026-08-11 – Kennzeichnung und Freigabestatus

- Exakte kompakte JuSt-Innovation-DXF-Geometrie `JSI-WM-001-R1` als letzte Produktionsgeometrieänderung auf den vier druckbettseitigen Modulunterseiten vertieft.
- Kennzeichnungsmaß: 15,991 × 14,000 mm bei Skalierung 1,4; Tiefe 0,40 mm; Restboden 2,00 mm.
- Direkte Unterseitenansicht, Nahansicht, Querschnitt und geometrische Schichtsimulation dokumentiert.
- Die finale Freigabe bleibt blockiert, bis eine echte Slicer-Vorschau und vorzugsweise die Passungs-/Reliefcouponprüfung vorliegen. Alle Exporte bleiben deshalb als `DRAFT` benannt.

## 2026-08-11 – 3MF-Interoperabilität

- Die zuerst verwendete JSCAD-Verpackungsstufe ließ den 3MF-Core-XML-Namensraum weg.
- Die STL-Dreiecke waren davon nicht betroffen; nur der Container wurde ersetzt.
- `src/package_3mf.py` paketiert jetzt die validierten STL-Netze reproduzierbar mit Core-Namensraum, vier benannten Objekten, vier Build-Items und geprüfter Baugruppenhülle 227 × 357 × 64 mm.

## 2026-08-11 – Änderungsanforderung R1

- Nutzerwunsch 1: Die schmalen rechteckigen Ausschnitte der R0-DRAFT-Geometrie werden durch breitere, leicht gerundete Griffnuten entsprechend der Wirkung des Konzeptbilds ersetzt.
- Empfohlener Startwert: 22 mm Breite, 8 mm Tiefe, 4 mm unterer Rundungsradius; alle Werte extern parametrierbar.
- Nutzerwunsch 2: T- und Kreuzungsknoten der Trennwände werden nicht nur am Boden verstärkt, sondern über die volle Wandhöhe optisch und funktional verrundet.
- Empfohlener Startwert: 4,0 mm vertikaler Blendenradius und 5,5 mm Kreuzungshub; Wandstärke als 3,2-mm-Basisparameter mit getrennten Overrides für Außen- und Trennwände.
- Nutzerwunsch 3: Die Gravur wird deutlicher und das Heightmap-Motiv unregelmäßiger. Vorgesehen sind verschieden große und versetzte Platten, ungleichmäßige Nietnähte mit Lücken, einzelne Patchplatten und dezente Gebrauchsspuren statt eines schachbrettartigen Rasters.
- Empfohlene R1-Relieftiefen: bis 0,50 mm vertieft und 0,55 mm erhaben; 2,6-mm-Boden und 3,2-mm-Wände halten mindestens 2,0 mm Restmaterial.
- Gate-Status: R0-Konzept- und Kennzeichnungsfreigaben sind für R1 ungültig. Vor Texturbild und CAD ist die ausdrückliche R1-Anforderungsfreigabe erforderlich.

## 2026-08-11 – Anforderungen R1 freigegeben

- Nutzerfreigabe: „Anforderungen R1 freigeben.“
- Freigegebene Geometrieparameter: 22 × 8 mm breite U-Griffnuten mit 4-mm-Rundung, 4,0-mm-Vollhöhenblenden an Wandknoten, 5,5-mm-Kreuzungshub sowie 3,2-mm-Basiswandstärke mit getrennten Overrides.
- Freigegebene Reliefparameter: bis 0,50 mm vertieft und 0,55 mm erhaben, 180 × 180 mm physisches Mastermotiv, mindestens 0,9 mm druckbare Merkmalsbreite und mindestens 2,0 mm Restmaterial.
- Freigegebene Bildsprache: unterschiedlich große und versetzte Stahlplatten, unregelmäßige Nietnähte mit Lücken, vereinzelte Patchplatten und dezente Gebrauchsspuren ohne Rost oder scharfe Schäden.
- Gate-Status: Anforderungen R1 `approved`; Konzept R1 `pending`. Produktions-CAD und Fertigungsexporte bleiben bis zur Konzeptfreigabe gesperrt.

## 2026-08-11 – Konzept und Textur R1 erstellt

- Bildmodus: integrierte Bildgenerierung; das R0-Konzept diente als Geometrie-/Kompositionsreferenz, das neue R1-Masterbild als Reliefreferenz.
- Konzeptasset: `concept-R1.png` (1536 × 1024 px, SHA-256 `73c6226136488a0464909b1ef45f52e3f58eb859d0ac244be0f16364104064e5`).
- Texturasset: `texture/steel-rivets-source-R1.png` (1254 × 1254 px, SHA-256 `80bbcafabca8a649d09e9887da43daabcda4d39af9e1b260e2d1a36c0b1816ac`).
- Sichtprüfung: vier Module, acht Kleinteilfächer, eine lange Schraubendreherzone und ein separater Kamm bleiben erhalten. Breite U-Griffnuten, vollhohe gerundete Wandknoten und ein unregelmäßigeres Patch-/Nietrelief sind deutlich sichtbar.
- Heightmap-Quellenanalyse bei 180 × 180 mm: 0,1435 mm/px Quellabtastung, 2,75 Z-Schritte bei 0,55 mm und 0,20-mm-Schichten, keine subnominellen verbundenen Komponenten. Die Top-/Bottom-Kante ist unauffällig; die Left-/Right-Kante ist mit Verhältnis 1,64 noch stärker als lokale Nachbarvariation und wird deshalb erst nach Konzeptfreigabe in der Produktionsvorbereitung nahtkorrigiert.
- Konzeptdarstellung ist keine Maß- oder Druckbarkeitsprüfung. Verbindlich bleiben die Werte in `design-spec.yaml`.

### Finaler Prompt – R1-Texturmaster

> Use case: stylized-concept. Asset type: square grayscale displacement / height-map master for an FDM-printable industrial drawer-organizer surface. Create an organic, realistic-looking repaired steel plate and rivet relief pattern that does not resemble a checkerboard: differently sized staggered plates, a few overlapping repair patches, irregular rivet seams with varied spacing, occasional gaps and double rivets. Perfectly flat orthographic square, seamless intent, no frame. Medium gray plate fields, darker recessed seams and shallow dents, brighter rounded rivets and subtly raised patch edges. Broad printable features for a 0.4-mm nozzle at 180 × 180 mm. Black/dark means recessed, 50% gray neutral, white/bright raised. No lighting gradient, cast shadows, specular highlights, perspective, color, rust, holes, sharp damage, text, symbols, logos, screws, bolts, tread, checkerboard, evenly spaced rows or fine photographic noise.

### Finaler Prompt – R1-Konzeptblatt

> Use case: precise-object-edit. Image 1 defines the unchanged organizer architecture, camera and composition; Image 2 supplies only the irregular plate/rivet relief language. Update Image 1 for R1: use broad shallow U-shaped 22-mm access grooves with rounded 4-mm bottoms and soft transitions on the visible wall of every one of the eight small-parts compartments; add smooth tangential vertical blend columns at every T- and four-way wall junction from floor to wall top with fuller rounded crossing hubs; replace the regular plate/rivet treatment with varied staggered plates, patch plates and irregular rivet runs, visibly stronger yet shallow and FDM-printable on floors and visible wall bands. Preserve exactly four modules, exactly eight compartments in a 2 × 4 arrangement, one uninterrupted long screwdriver zone, one removable comb, proportions, wall heights, rounded outer corners, connectors, layout, camera, lighting and white background. No text, dimensions, labels, arrows, logos, watermark, rust, holes, tears, sharp damage, extra compartments, missing walls, accessories, exaggerated rivets, deep carvings or unsupported overhangs.

## 2026-08-11 – Konzept R1 freigegeben

- Nutzerfreigabe: „Konzept R1 freigeben“.
- Freigabebasis: `concept-R1.png`, `texture/steel-rivets-source-R1.png` und die Werte in `design-spec.yaml` Revision R1.
- Produktionsumfang: 22 × 8-mm-U-Griffnuten mit 4-mm-Bodenradius, vollhohe parametrierbare T-/Kreuzungsblenden, 3,2-mm-Basiswandstärke sowie die nahtkorrigierte 180 × 180-mm-R1-Heightmap.
- Gate-Status: Anforderungen R1 und Konzept R1 `approved`; R1-Produktionsgeometrie und digitale Regression dürfen beginnen. Die finale Freigabe bleibt bis zur geprüften DRAFT-Fassung und erneuten Kennzeichnungsstufe gesperrt.

## 2026-08-11 – Produktionskandidat R1 DRAFT

- Parametrierung umgesetzt: 2,6-mm-Boden, 3,2-mm-Basiswandstärke mit getrennten Außen-/Trennwand-Overrides, 22 × 8-mm-U-Griffnuten mit 4-mm-Bodenradius.
- Wandknoten umgesetzt: drei 5,5-mm-Kreuzungshubs und sechs 4,0-mm-T-Blenden, durchgehend von z = 2,6 bis 55,0 mm. Die glatten Knoten werden nach der Reliefstufe erneut vereinigt.
- Relief umgesetzt: R1-Master auf 180 × 180 mm abgebildet, 16 Bit, 0,30-mm-Bildpitch, 7-mm-Nahtüberblendung und 1,5-mm-Geometriepitch. Fertigungsmanifest: 703 Gravur- und 47 Erhöhungszellen in 377 Läufen.
- Tiefen umgesetzt: 0,50 mm Gravur und 0,55 mm Erhöhung auf Böden/Innenflächen; Außenflächen bleiben durch ein 0,35-mm-Rezessfeld innerhalb der Einbauhülle.
- Materialreserven: mindestens 2,10 mm am gravierten Boden und 2,20 mm an beidseitig reliefierten Wänden beziehungsweise unter der 0,40-mm-Unterseitenmarke.
- Digitale Regression: 9/9 STL-Dateien geschlossen, manifold, einteilig und volumenhaltig; Baugruppe 227 × 357 × 64 mm; R1-3MF enthält vier Objekte und vier Build-Items.
- Kennzeichnung: `JSI-WM-001-R1` compact, Skalierung 1,4, auf allen vier Hauptmodulen als letzte Geometrieänderung integriert. Eine echte Slicer-Vorschau fehlt weiterhin; deshalb bleiben Dateien und Freigabestatus `DRAFT`.

## 2026-08-12 – R1.1 Korrektur der 16-Bit-Reliefpipeline

- Nutzerbefund bestätigt: Die vorbereitete 16-Bit-Heightmap enthielt 34.988 unterschiedliche Werte, aber die alte Vektorisierung reduzierte sie mit zwei Schwellwerten auf nur drei Geometriezustände: Gravur, neutral und Erhöhung.
- Nutzerentscheidung: Volle 16 Bit verwenden und weitere Höhenquantisierung möglichst vermeiden; bei fehlender Materialreserve Emboss einsetzen oder Wandstärke erhöhen.
- Gate-Entscheidung: Keine neue Anforderungs- oder Konzeptfreigabe erforderlich, weil die Korrektur das bereits freigegebene kontinuierlich-tonale R1-Erscheinungsbild umsetzt und Außenmaß, Aufteilung, maximale Relieftiefen sowie Druckprozess unverändert lässt.
- Neue Repräsentation: `continuous-heightfield-u16`, 301 × 301 Geometriepunkte auf 180 × 180 mm, 0,60 mm Pitch, 90.601 unsigned-16-Bit-Samples und 19.740 unterschiedliche Höhenwerte. Median 33195 ist neutral; dunkler wird proportional bis 0,50 mm graviert, heller proportional bis 0,55 mm erhaben.
- Nicht verwendeter Versuch: 0,45-mm-Pitch überschritt beim Gesamtmodell den verfügbaren Manifold3D-WASM-Speicher. Entsprechend dem Heightmap-Workflow wurde nur die XY-Abtastung auf den feinsten stabilen Gesamtmodellwert 0,60 mm reduziert; die Höhenwerte blieben 16 Bit ohne Schwellwerte oder Klassen.
- Exportgrenze: Binär-STL speichert Koordinaten als Float32. Dadurch können unmittelbar benachbarte 16-Bit-Werte an großen Absolutkoordinaten zusammenfallen. Die Pipeline führt darüber hinaus keine gezielte Höhenquantisierung aus.
- STL-Nachweis: Die vier Module enthalten im Bodenrelief jeweils 36.329 bis 50.041 unterschiedliche Float32-Z-Werte. Alle neun STLs bestehen den unabhängigen Topologieaudit. Zwei Float32-kollabierte Mikro-Kanten wurden deterministisch lokal repariert; Außenmaße und sichtbare Reliefdaten blieben unverändert.
- Materialreserve: 2,10 mm unter maximaler Bodengravur und 2,20 mm an doppelseitig reliefierten Wänden. Eine Wandverdickung ist bei den freigegebenen 0,50/0,55-mm-Tiefen nicht nötig; Emboss ist bereits Teil der signierten Reliefabbildung.
- 3MF: `DRAFT-R1.1-organizer-continuous16-assembly.3mf`, vier benannte Objekte und Build-Items, Core-Namensraum und Hülle 227 × 357 × 64 mm geprüft.

## 2026-08-12 – R1.2 Ein-Befehl-Bildwechsel und 0,30-mm-Speicherumbau

- Nutzerentscheidung: Ein neues Texturbild soll mit einem einfachen Befehl verarbeitet werden; physische Größe, PPI, Geometriepitch, Mapping, Reliefhöhen und Ausgaben müssen aus Parameterdateien kommen. Die Geometrieabfolge soll für 0,30 mm speichereffizient werden.
- Gate-Entscheidung: Keine erneute Anforderungs-/Konzeptfreigabe, weil Aufteilung, Maße, Schnittstellen, Reliefmotivklasse, maximale Gravur/Erhöhung und Außenhülle unverändert bleiben. Der Stand bleibt `DRAFT`.
- Persistenter Job: `relief/organizer/relief-job.json` trennt registrierten 16-Bit-Quellmaster, 180 × 180-mm-Kachel, 900 × 900-Fertigungs-Heightmap bei 0,20 mm/Pixel (127 PPI), 7-mm-Nahtüberblendung, Mapping und Geometrieadapter.
- Einziger Anwenderbefehl: `python3 rebuild.py NEUES_BILD.png`. Registrierung, Build-Map, Metadaten/Hashes, kontinuierliches Manifest, vier Modulbuilds, Sliver-Reparatur, 3MF und vollständige Validierung laufen ohne weitere Bild-/PPI-/Reliefparameter. `python3 rebuild.py` baut aus dem registrierten Master erneut.
- Quellregistrierung: Aktuelles 1254 × 1254-RGB-Motiv als 16-Bit-Container registriert; effektive 176,95 PPI bei 180 mm. Herkunftspräzision bleibt ehrlich als 8 Bit dokumentiert. Für neue AI-Master verlangt `source-spec.json` 180 × 180 mm bei 300 PPI beziehungsweise mindestens 2126 × 2126 Pixel.
- Fertigungsasset: echte 16-Bit-PNG, 900 × 900, 35.062 verschiedene Tonwerte, 127 PPI, exakt passende X/Y-Ränder nach konfigurierter 7-mm-Nahtüberblendung.
- Geometrie: 601 × 601 Punkte bei 0,30 mm, 361.201 Samples und 26.115 verschiedene uint16-Werte; keine Schwellwerte oder Tiefenklassen. Exportierte Bodenbänder besitzen 124.027–165.112 verschiedene Float32-Z-Werte.
- Speicherabfolge: je ein Hauptmodul in einem eigenen Node/WASM-Prozess; innerhalb jedes Moduls je ein Boden-/Wandpatch gleichzeitig; blockweiser STL-Export; reparierte indexierte Mesh-Caches; direkt gestreamtes 3MF-ZIP/XML; je STL ein frischer Validatorprozess.
- Gemessene Modul-Peaks: Driver vorn 1258,9 MiB, Driver hinten 1452,6 MiB, Hardware vorn 2124,7 MiB, Hardware hinten 1879,6 MiB. Der Worst Case beträgt damit 2,075 GiB Peak-RSS statt des früher ungemessenen Gesamtmodell-Limits.
- Topologie: 9/9 STLs PASS. Driver vorn und Hardware vorn benötigten jeweils genau einen lokalen Mikro-Kantenkollaps; Driver hinten, Hardware hinten und Reliefcoupon blieben unverändert. Alle finalen Netze haben 0 Randkanten, 0 nicht-manifold Kanten, 0 Nullflächen, konsistente Orientierung, positives Volumen und je einen Körper.
- 3MF: `DRAFT-R1.2-organizer-rebuildable-030mm-assembly.3mf`, vier benannte Objekte/Build-Items, CRC und Core-Namensraum PASS, Hülle 227 × 357 × 64 mm.

## 2026-08-12 – R1.3 Korrektur des physischen Bildseitenverhältnisses

- Nutzerbefund bestätigt: R1.2 skalierte jedes Ersatzbild unmittelbar auf die fest konfigurierte 180 × 180-mm-/900 × 900-Pixel-Kachel. `steel1.png` mit 1536 × 1024 Pixeln wurde dadurch von 3:2 auf 1:1 anisotrop gestreckt.
- Vergleichsbasis: Heightmap-Relief-Workflow v2.2.0 mit physischem Seitenverhältnis als Invariante, Millimeter-Fit vor Rasterung, separatem Vorschauasset, hartem Pre-Geometry-Gate und 20-mm-Kreis-/Quadratdiagnose.
- Gate-Entscheidung: Keine neue Anforderungs-/Konzeptfreigabe, weil die Korrektur die bereits freigegebene Texturklasse korrekt abbildet und Außenmaß, Aufteilung, Schnittstellen, Reliefmotivklasse, maximale Gravur/Erhöhung und Druckprozess unverändert lässt. Der Stand bleibt `DRAFT`.
- Neue Registrierung: 1536 × 1024 Quadratpixel werden mit 180 mm Breitenanker als 180 × 120 mm registriert. Der effektive physische Pitch beträgt in beiden Achsen 0,1171875 mm, also 216,75 PPI isotrop.
- Neue Rasterung: Die Quelle wird einmalig und gleichmäßig auf 900 × 600 Pixel bei 0,20 mm/Pixel abgetastet, mit 7-mm-Randüberblendung periodisch gemacht und ohne Achsenstreckung in die 900 × 900-Zielmap wiederholt. Sichtbar sind 1,0 Wiederholungen in X und 1,5 in Y.
- Neuer Gate: `aspect_policy=preserve`, `allow_aspect_distortion=false`, Texturtoleranz 1,5 %. Quell-, platzierter und rekonstruierter physischer Aspekt betragen 1,5; Fehler 0,000000 %. `stretch` oder eine falsch proportionierte explizite Kachel bricht vor Geometrie ab.
- Diagnose: Der 20-mm-Test wird als 601 × 401-Geometriefeld bei exakt 0,30 × 0,30 mm abgetastet. Quadrat und Kreis messen rasterbedingt 19,8 × 20,1 mm; Kreiselliptizität 1,493 %, PASS innerhalb der 1,5-%-Texturtoleranz.
- Geometrie: Die echte 180 × 120-mm-Wiederholkachel wird als kontinuierliches 601 × 401-u16-Heightfield mit 241.001 Samples und 39.402 unterschiedlichen Werten an Manifold3D übergeben. Die 180 × 180-Zielmap wird nicht mehr als falsche Wiederholperiode verwendet.
- Speicher: Driver vorn 1276,1 MiB, Driver hinten 1494,6 MiB, Hardware vorn 2084,0 MiB, Hardware hinten 1929,3 MiB, Zubehör 216,1 MiB. Exakter Worst Case: 2083,953 MiB = 2,035 GiB = 2,185 GB dezimal.
- Topologie/3MF: 9/9 STLs PASS; nur Hardware vorn benötigte einen lokalen Mikro-Kantenkollaps. `DRAFT-R1.3-aspect-safe-030mm-assembly.3mf` enthält vier Objekte/Build-Items, CRC und Core-Namensraum PASS, Hülle 227 × 357 × 64 mm.
