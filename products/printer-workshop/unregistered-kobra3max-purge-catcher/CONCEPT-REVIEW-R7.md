# R7 Konzeptprüfung – Z-Rider v1

## Freigabestatus

- Anforderungsrevision: `0.7.0-requirements.2`, durch Stefan am `2026-08-29T12:01:09+02:00` freigegeben
- Konzeptstatus: **menschliche Freigabe ausstehend**
- Produktions-CAD und Fertigungsexporte: **gesperrt bis zur Konzeptfreigabe**

## Konzeptartefakt

- Datei: `concepts/R7-concept-sheet-z-rider-v1.png`
- SHA-256: `3505742788b3c128aca81cdb9d23a67b083214ceec2067994d5b61ff59bf0e00`
- Raster: 1523 × 1032 px, sRGB, 8 Bit RGB
- Erzeugung: OpenAI `imagegen`, Modus `stylized-concept`
- Verwendung: ausschließlich System- und Formkonzept; nicht maßhaltig und nicht CAD-fähig

## Was das Bild zur Freigabe stellt

1. Ein kleiner Fangkopf sitzt im selben bewegten Z-Bezugssystem wie der Wiper und folgt der Purge-Quelle.
2. Eine dünne, einmal montierte Datumplatte nutzt das real gemessene vertikale Zwei-Schrauben-Datum.
3. Der Fangkopf ist für Reinigung über einen sehr kurzen geführten Serviceweg mit positiver Rastung abnehmbar.
4. Die Purge trifft in einer lokal geschlossenen Zone auf und wird über einen stetigen, unten vollständig offenen Weg direkt abgeleitet.
5. Nur Fangkopf und Umlenker bewegen sich; ein breiter Sammelbehälter bleibt stationär darunter.
6. Es gibt keinen Vollhöhen-Tower, Mast, Schlauch, langen Kanal oder mitfahrenden Speicherbehälter.

Die Darstellung übernimmt die geschützte Funktionssprache des eigenen R6-Fangkopfs – kurze Haube, geschlossene Trefferzone, offene Fallstrecke und zurückhaltende Wabenflächen – aber kein fremdes Montageprofil.

## Maßgebende Bezüge neben dem Bild

Diese Werte kommen aus der Benutzervermessung und `WIPER-PHOTO-MEASUREMENTS-R7.yaml`; sie wurden **nicht** aus dem Konzeptbild abgeleitet:

- Schraubenabstand vertikal, Mitte–Mitte: 17 mm
- Untere Schraubenmitte bis Purge-Ablageebene: 10 mm
- Schraubendatum bis horizontale Purge-Wurfbahn: 37 mm Seitenversatz
- Schraubenebene bis rückwärtige Wiper-Ausdehnung: 40 mm
- Ziel für die gesamte mitbewegte Baugruppe: höchstens 25 g; keine Herstellerlastfreigabe
- Fangkopf-Serviceweg: höchstens 15 mm linear äquivalent
- Zielreserve beim manuellen Vollwegtest: mindestens 5 mm
- Funktionsnachweis: je mindestens drei Purge-Zyklen bei niedriger, mittlerer und hoher Z-Position

## Bewusste Unschärfen

- Das Bild vereinfacht Wiper, Schraubenauflage und Druckerumgebung. Die reale Bauteilkontur bleibt durch Fotos, Realmaße und späteren Coupon maßgebend.
- Datumplatte, zwei Führungsstellen und Rastung sind nur als Prinzip gezeigt. Ihr Profil, ihre Entnahmerichtung und ihre Toleranzen werden erst nach Konzeptfreigabe konstruiert.
- Schraubengewinde, Kopfgeometrie, vorhandene Länge, Bauteildicke und verbleibender Gewindeeingriff sind noch zu messen.
- Bett-, Kopf-, Kabel- und Wiper-Keep-outs über den vollständigen X/Y/Z-Weg sind noch nicht belegt.
- Größe und Lage des stationären Behälters werden aus realen Flugbahnmarkierungen bei drei Z-Höhen abgeleitet.
- Das Explosionsdetail kann optisch wie ein gerader Abzug wirken; verbindlich ist nur ein kurzer seitlicher oder kleiner schwenkender Serviceweg, nicht die im Bild angedeutete Kinematik.

## Clean-Room-Provenienz

Als Bildreferenzen dienten ausschließlich:

- `Photos-1-001/PXL_20260829_093031316.jpg` – eigener realer Maschinen-/Wiper-Raumbezug; SHA-256 `bcdbbe46be9c37009c54c922e56da6956e8c4378c5d3192e16c5ffa5b7be60ce`
- `Photos-1-001/PXL_20260829_093122291.jpg` – eigenes reales Schraubendatum; SHA-256 `13283f27168d09dd7e5eefa777f4dc9cd60c44a63a9c62ecbd65f36700f4c01d`
- `Anycubic-Kobra-3-Max-Purge-Catcher-metriMade-R6/anycubic-kobra3-max-purge-catcher-r6/previews/catcher-r6-section.png` – eigener R6-Fangkopf als Funktions-/Formreferenz; SHA-256 `09ef0a595fc8fe9753f06533148de89a96fd9c567dc6c6bd446b05ca1ee4f934`

Die Dateien unter `research/third-party/printer-workshop` waren keine Bild- oder Geometrieeingabe. Von dort wurden nur bereits separat dokumentierte, abstrakte Funktionsprinzipien betrachtet.

## Finaler Bild-Prompt

```text
Use case: stylized-concept
Asset type: functional 3D-printable product concept sheet for design approval
Primary request: Create an original clean-room industrial-design concept sheet for the R7 purge catcher on the Anycubic Kobra 3 Max shown in the reference photos. The small capture head must mount directly to the real Z-moving purge-Wiper assembly and move with it. It catches the sideways-ejected purge locally and immediately redirects it downward into a large separate stationary bin below. This is a new design, not a copy of any third-party accessory.
Input images: Image 1 is the real printer and Wiper spatial reference; Image 2 is the real two-screw Wiper datum and nearby purge surface reference; Image 3 is our owned R6 functional catcher-body reference only, especially the closed upper impact chamber, short hood, open lower drop path, and smooth honeycomb side language.
Scene/backdrop: clean warm-white industrial design board, isolated printer subassembly, no workshop clutter
Subject: a compact charcoal-gray and muted teal FDM catcher attached by a very thin front datum plate under the two vertically aligned existing screw heads; a low-mass removable catcher using two short guidance points and a small positive latch; short service motion sideways or by a small pivot; smooth enclosed impact zone transitioning directly into a completely open downward outlet; stationary wide-mouth waste bin far below and not mechanically attached
Style/medium: precise polished 3D product visualization, realistic FDM plastic, clean technical concept rendering, plausible geometry
Composition/framing: one coherent landscape concept sheet with three visual zones: (1) dominant three-quarter installed close-up on the real Wiper, (2) compact exploded close-up showing thin fixed screw plate plus short-stroke removable catcher and latch, (3) cutaway showing an orange purge strand entering the impact wall and following a smooth curved path directly downward into the stationary bin; add a subtle ghosted low/mid/high vertical sequence of the same catcher moving with the Wiper to communicate Z motion
Lighting/mood: neutral studio lighting, high legibility, restrained engineering presentation
Color palette: printer parts dark gray and aluminum; proposed printed parts charcoal with muted teal accents; purge path orange
Materials/textures: matte PETG/FDM texture with smooth purge-contact surfaces; thin ribbed lightweight walls; smooth open honeycomb only where it does not obstruct flow
Constraints: preserve the recognizable real Wiper screw-face orientation from the photos; exactly two vertically aligned mounting screws; the catcher stays very close to the Wiper; only the small catcher/diverter moves; the storage bin is stationary; show open gravity fall; no dimensions, no safety claims, no words, no logos, no trademarks, no watermark
Avoid: any full-height tower, mast, hose, tube, long vertical dovetail, deep housing-wrapping clip, magnets, moving storage bin, drawer on the Wiper, bulky bracket, blocked outlet, contact with print bed or print head, copied third-party geometry, decorative fantasy shapes, illegible pseudo-text
```

## Erbetene Entscheidung

Freigabe bedeutet Zustimmung zur **Systemarchitektur und Formrichtung** dieses Blatts. Maße, Schraubeneingriff, Rastgeometrie, Kollisionen und Purge-Flugbahn bleiben danach ausdrücklich coupon- und testpflichtig.

Freigabeformulierung: `Konzept R7 Z-Rider v1 freigegeben.`
