# Validierungsbericht – Waben-Haarspange Revision 6 (Final Release)

## Ergebnis

Der final freigegebene Revision-6-Release wurde für vier Größen-Presets sowie die Parametergrenzen 65/7 und 105/18 mm erzeugt. Die digitale Geometrie-, Export-, Parametrik-, Waben-, Gelenk- und Kennzeichnungsprüfung ist bestanden. Der Status bleibt **experimentell**, weil noch kein realer PETG-Druck, Gelenkzyklus, Rastzyklus oder Tragetest vorliegt.

## Größenübersicht

| Preset | Exportmaß X × Y × Z | PETG-Masse geschätzt | Wabenfolge | Körper |
|---|---:|---:|---:|---:|
| Small | 67,94 × 30,92 × 28,60 mm | 12,80 g | 2 / 1 / 2 | 2 |
| Medium | 75,94 × 34,31 × 28,60 mm | 14,03 g | 2 / 1 / 2 | 2 |
| Large | 84,94 × 37,88 × 28,60 mm | 16,90 g | 3 / 2 / 3 | 2 |
| Extra Large | 95,94 × 42,79 × 28,60 mm | 18,76 g | 3 / 2 / 3 | 2 |

Alle Maße sind Mesh-Bounding-Boxes im offenen Druckzustand. Die 85/12-mm-Large-Variante ist der Standardkandidat.

## Gelenk und Rastung

- Topologie: zwei äußere Unterkamm-Laschen, eine mittlere Oberbogen-Hülse, ein mit dem Unterteil verbundener gefangener Zapfen
- Zapfen: 4,00 mm Durchmesser
- Radialspiel: 0,35 mm; Durchmesserspiel 0,70 mm
- Axialspiel: 0,40 mm je Seite der mittleren Lasche
- äußerer Laschenabschnitt: 7,60 mm
- mittlere Hülse: 8,00 mm
- Exportwinkel: −10°
- geprüfter Öffnungsanschlag: −31°
- geschlossene Endstellung: −3°
- nutzbarer Winkelbereich: 28°

Der starre Gelenk-/Kammkern wurde an 13 Winkeln je Preset geprüft und bleibt kollisionsfrei. Der Öffnungsanschlag besitzt nur am Endwinkel eine kleine geometrische Kontaktüberschneidung; einen Grad davor bleibt er frei. In der geschlossenen Endstellung überschneiden sich die beiden starren Körper nicht.

Die Rastzunge ist 20 mm lang und 1,6 mm dick. Für den nominalen 1,0-mm-Einrastweg ergibt die lineare Balkenabschätzung ungefähr 0,006 beziehungsweise 0,6 % Außenfaserdehnung. Das ist ein Screeningwert; die beabsichtigte Rastinterferenz während des letzten Schließwegs verlangt den physischen Coupon.

## Waben und Skalierung

- genau drei versetzte Querreihen in allen Größen
- Schlüsselweite ca. 18,533 mm aus 28,6-mm-Panzerbreite und 0,8-mm-Fuge abgeleitet
- eine Zellorientierung; keine um 90° gedrehte Seitenreihe
- halbe Zellen nur in der Druckbettreihe
- vollständige Zellen auf der Nicht-Bettseite
- symmetrische Hoch-Tief-Endkontur durch ganze Außenzellen
- Längszellzahl aus `clipLength` abgeleitet
- Small/Medium: 2 / 1 / 2; Large/XL: 3 / 2 / 3
- Large-Längsskalierung: ca. 0,9466; andere Presets verwenden 1,0

## Mesh- und 3MF-Prüfung

Für alle vier Produkt-STL sowie den Gelenk-/Rastcoupon gilt:

- erwartete Körperzahl: 2
- geschlossene Kantenstruktur: PASS
- positive Windung/Volumen: PASS
- offene oder nicht-manifold Kanten: 0
- degenerierte Dreiecke: 0
- doppelte Dreiecke: 0
- getrennte Quellkörper jeweils zusammenhängend: PASS

Alle vier 3MF-Dateien:

- ZIP-Struktur intakt
- Core-3MF-Modell vorhanden
- Einheit `millimeter`
- gültige Vertex-/Dreiecksindizes
- ein Build-Objekt mit zwei absichtlich getrennten Meshkomponenten

Einzelberichte liegen unter `validation/r6-final-audits/`. Der zusammengefasste Revisionscheck `revision6-final-feature-audit.json` enthält 132 bestandene Prüfungen.

## Parametergrenzen

Zusätzlich zu den Presets wurden erzeugt:

- Minimum: 65 mm Länge / 7 mm Bogenanstieg
- Maximum: 105 mm Länge / 18 mm Bogenanstieg

Beide Grenzmodelle besitzen zwei Bewegungskörper, drei Wabenreihen, positive Volumina und eine nicht überschneidende geschlossene Endstellung. Werte außerhalb dieser Bereiche werden von den Quellcode-Assertions abgewiesen.

## Kennzeichnung

Die exakte kompakte DXF-Kontur `JSI-WM-001-R1` wurde als letzte Geometrieänderung 0,40 mm tief in eine glatte vollständige Zentralwabe geschnitten. Die nominale Hülle beträgt 11,423 × 10,0 mm. Der gewählte sichere Bereich misst 15,6 × 14,0 mm; nomineller Randabstand mindestens 2,0 mm, Restwand 2,90 mm. Keine Wabenrille, Gelenk-, Rast- oder Haarfläche wird geschnitten.

Die sechs geometrischen 0,20-mm-STL-Querschnitte zeigen die Vertiefungsabschnitte in den geprüften Höhen. Eine exakte Anycubic-Slicer-/G-Code-Vorschau ist weiterhin profilabhängig und muss vor dem Druck kontrolliert werden.

## Druckbereitschaft

Geometrisch empfohlenes Startprofil:

- Anycubic Kobra 3 Max
- ungefülltes PETG
- 0,4-mm-Düse
- 0,20-mm-Schichten
- vier Wände
- 20–30 % Gyroid/Cubic
- große Seitenfläche auf `Z = 0`
- Support zunächst aus

Ein druckerspezifischer Slicer-Dry-Run wurde nicht durchgeführt. Besonders zu prüfen sind die erste Schicht, beide Axialspalte, der umlaufende 0,35-mm-Radialspalt, die Rastzunge, 0,8-mm-Wabenfugen und die Kennzeichnung.

## Offene physische Akzeptanztests

1. Coupon mit identischem PETG und Profil drucken.
2. Gelenk nach vollständigem Abkühlen ohne Schneiden oder Bohren lösen.
3. 100 Gelenkzyklen ohne Riss, Weißbruch oder unzulässiges Spiel.
4. 50 Rastzyklen ohne bleibende Verformung.
5. Vollclip entgraten; keine scharfen Haut-/Haarkanten.
6. Persönliche Größe 30 Minuten tragen, ohne schmerzhaftes Ziehen oder Druckstellen.
7. Erst nach gemessenen Ergebnissen von `experimental` zu `qualified-local` hochstufen.

## Einschränkungen

- Ein renderbares oder slicbares Mesh ist kein Nachweis für reale Passung oder Lebensdauer.
- PETG-Eigenschaften hängen vom konkreten Filament, Feuchte, Temperatur, Kühlung, Linienführung und Druckrichtung ab.
- Der lineare Rast-Screeningwert bildet große Verformung, Kriechen, Ermüdung und FDM-Anisotropie nicht vollständig ab.
- Hautverträglichkeit kann nicht aus dem Polymerfamiliennamen abgeleitet werden.
