# Parametrische Waben-Haarspange – Revision 6

Revision 6 ist eine metallfreie PETG-Haarspangenfamilie mit unabhängig einstellbarer Länge und Bogenhöhe. Der bisherige Federbogen wurde durch ein echtes, gefangenes Print-in-Place-Drehgelenk ersetzt. Oberbogen und Unterkamm werden gemeinsam als zwei getrennte Körper gedruckt und bleiben nach dem Lösen des Gelenks unverlierbar verbunden.

Status: **final freigegebener, digital validierter Release; physisch weiterhin experimentell**. Gelenkfreigängigkeit, Rastkraft, PETG-Verschleiß und Tragekomfort sind noch nicht physisch qualifiziert.

## Standardvariante Large

- Sollparameter: 85 mm Länge und 12 mm Bogenanstieg
- Exportmaß: ca. 84,94 × 37,88 × 28,60 mm
- geschätzte PETG-Masse: ca. 16,90 g
- zwei getrennte, jeweils geschlossene Bewegungskörper
- 4,0-mm-Drehzapfen
- 0,35 mm Radialspiel / 0,70 mm Durchmesserspiel
- 0,40 mm Axialspiel auf jeder Seite der mittleren Lasche
- 28° geprüfter Drehbereich mit Öffnungsanschlag
- drei versetzte Wabenreihen mit der Folge 3 / 2 / 3
- Wabenschlüsselweite ca. 18,53 mm, Fuge 0,8 mm
- drei druckbettseitig halbierte und fünf vollständige Waben

## Größen-Presets

| Preset | Länge | Bogenanstieg | Wabenfolge längs |
|---|---:|---:|---:|
| `small` | 68 mm | 8 mm | 2 / 1 / 2 |
| `medium` | 76 mm | 10 mm | 2 / 1 / 2 |
| `large` | 85 mm | 12 mm | 3 / 2 / 3 |
| `extra_large` | 96 mm | 15 mm | 3 / 2 / 3 |

Der validierte Generierungsbereich beträgt 65–105 mm Länge und 7–18 mm Bogenanstieg. Länge und Wölbung sind unabhängig; Wandstärken, Gelenkpassungen und Rastzungendicke skalieren nicht.

## Wichtigste Dateien

- `output-r6-final/large/masculine-honeycomb-hair-clip-r6-large.3mf` – bevorzugte Large-Druckdatei in Millimetern
- `output-r6-final/large/masculine-honeycomb-hair-clip-r6-large.stl` – universelle Large-Druckdatei
- `output-r6-final/large/hair-clip-hinge-latch-coupon-r6.stl` – kombinierter Gelenk-/Rastcoupon
- `output-r6-final/{preset}/...` – weitere Größen
- `hair_clip.mjs` – parametrischer Manifold-3D-Quellcode
- `design-spec.yaml` – Anforderungen, Freigaben und Akzeptanzkriterien
- `validation/validation-report.md` – digitale Ergebnisse und offene physische Tests
- `renders/r6-release-candidate-overview.png` – Konzept-/CAD-Vergleich

## Parametrisch erzeugen

Voraussetzung ist eine aktuelle Node.js-Version. Die Abhängigkeiten sind in `package-lock.json` fixiert.

```bash
npm ci
node hair_clip.mjs --preset=large --output-dir=output-r6-final/large
node hair_clip.mjs --all-presets --output-dir=output-r6-final
```

Eigene Größe:

```bash
node hair_clip.mjs \
  --preset=large \
  --clip-length=90 \
  --arch-rise=14 \
  --output-dir=output-custom
```

Zusätzliche Passungsparameter:

- `--hinge-pin-diameter=4.0`
- `--hinge-radial-clearance=0.35`
- `--hinge-axial-clearance=0.40`
- `--preview` für reduzierte Kreisauflösung
- `--draft` für ausdrücklich als DRAFT markierte Diagnose-/Revisionsausgaben
- `--without-watermark` nur für diagnostische Vergleichsexporte; nicht für eine Produktfreigabe

Ungültige Werte werden vor der Geometrieerzeugung abgewiesen.

## Empfohlener Druckstartpunkt

- Drucker: Anycubic Kobra 3 Max
- Material: ungefülltes, trockenes PETG
- Düse: 0,4 mm
- Schichthöhe: 0,20 mm
- Linienbreite: etwa 0,45 mm gemäß kalibriertem Profil
- Wände: 4
- Deck-/Bodenschichten: 6 / 6
- Infill: 20–30 % Gyroid oder Cubic
- Support: zunächst aus; Gelenk- und Rastbereiche in der Layer-Vorschau prüfen
- Geschwindigkeit: konservativer Start um 40–45 mm/s
- Kühlung und Temperaturen: Profil des konkreten Filamentherstellers
- Brim: optional 3–5 mm bei unsicherer Seitenflächenhaftung

Die große Seitenfläche liegt bereits bei `Z = 0`. Die Gelenkachse steht vertikal. Das mittlere Lager, beide äußeren Laschen und der Zapfen werden mit umlaufendem Druckspalt gemeinsam aufgebaut.

## Verbindlicher Testablauf

1. Zuerst den kombinierten Coupon mit exakt demselben PETG, derselben Düse, Orientierung und demselben Profil drucken.
2. Nach vollständigem Abkühlen das Gelenk vorsichtig lösen; keine Klinge in den Lagerzwischenraum drücken.
3. Coupon mindestens 100-mal drehen und 50-mal rasten.
4. Bei Weißbruch, Rissen, verschmolzenem Lager, übermäßigem Spiel oder bleibender Verformung den Vollclip nicht drucken; stattdessen das passende Spiel neu kalibrieren.
5. Im Slicer den 0,35-mm-Radialspalt, die 0,40-mm-Axialspalte, die 0,8-mm-Wabenfugen und die 0,40-mm-Kennzeichnungsvertiefung Schicht für Schicht prüfen.
6. Vollclip drucken, Kontaktkanten entgraten und das Gelenk erst nach vollständigem Abkühlen bewegen.
7. Zunächst kurz tragen; akzeptiert ist die persönliche Größe erst nach 30 Minuten Halt ohne schmerzhaftes Ziehen oder Druckstellen.

## Digitale Verifikation

- vier Presets plus Randwerte 65/7 und 105/18 erzeugt
- 132 Regressionsprüfungen bestanden
- jedes Produkt-STL: zwei geschlossene, manifold Bewegungskörper
- Coupon-STL: zwei geschlossene, manifold Bewegungskörper
- keine offenen, nicht-manifold, doppelten oder degenerierten Dreiecke in den geprüften Kandidaten
- 3MF-Archive strukturell gültig und in Millimetern
- starrer Gelenk-/Kammkern über 28° kollisionsfrei
- geschlossene Endstellung ohne starre Körperüberschneidung
- beabsichtigte elastische Rastinterferenz nur während des letzten Schließwegs

Diese Prüfungen belegen Geometrie und Kinematik, nicht reale Druckfreigängigkeit, Rastkraft, Ermüdungslebensdauer oder Hautverträglichkeit.

## Kennzeichnung

Die exakte kompakte JuSt-Innovation-Kontur `JSI-WM-001-R1` ist 0,40 mm tief in die glatte Fläche einer vollständigen Zentralwabe eingelassen. Die druckbettseitigen Strukturstreifen sind für eine sichere 10-mm-Marke zu schmal; die gewählte Ausweichfläche schneidet keine Wabenrille oder Funktionsfläche. Der Release-Nachweis liegt unter `validation/watermark-evidence-r6.png`.

## Grenzen

- Print-in-Place-Passungen sind drucker-, Filament- und profilabhängig.
- Die 0,6-%-Rastdehnungsabschätzung ist nur ein linearer Screeningwert; große Verformung, FDM-Anisotropie, Kriechen und Ermüdung werden damit nicht vollständig beschrieben.
- Eine druckerspezifische Anycubic-G-Code-Vorschau und ein physischer Testdruck wurden nicht durchgeführt.
- Die Vorlage ist eine perspektivische Designreferenz; verdeckte Funktionsgeometrie ist eine dokumentierte technische Interpretation.
- Filamentmarketing allein belegt keine Haut- oder Medizinverträglichkeit. Bei Irritationen nicht weiterverwenden.
