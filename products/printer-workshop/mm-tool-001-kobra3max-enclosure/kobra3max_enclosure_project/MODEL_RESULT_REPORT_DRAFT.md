# Modellergebnis – Kobra 3 Max Kamera-Whitebox DRAFT

## Ergebnis und Status

Die vollständige bodenlose Kamera-Whitebox sowie das eigenständig neu konstruierte Gehäuse für die originale Anycubic Live View Camera sind parametrisch umgesetzt. Der digitale DRAFT-Vertrag besteht; Fertigung und Release bleiben bis zu Coupon-, FOV-, Bewegungs-, Tür-, Licht-, Temperatur-, Slicer- und Handhabungstests gesperrt.

## Konstruktionsumfang

- Körper 900 × 1050 × 900 mm, Lichtkassette bis ungefähr 960 mm Gesamthöhe;
- außenliegender 20 × 20 mm Holzrahmen mit unterem Ring;
- innen weiße Seiten-, Rück- und Serviceplatten, keine Bodenplatte;
- klare, links angeschlagene 740 × 880 × 4 mm Tür;
- opales Lichtdach mit sechs Dach- und zwei Fülllichtläufen;
- regelbare 120-mm-Abluft mit weißer innerer Sichtblende;
- außerhalb montierte, höhenverstellbare Kamera auf 2020-Profil;
- projektlokales zweiteiliges Kameragehäuse, kurzer M4-Arm und 11-mm-Kugelgelenk;
- kleines, um 7° geneigtes Kamerafenster mit matter weißer Innenblende.

## Maßgrundlage und Annahmen

- Drucker-Planungsraum: 706 × 940 × 753 mm; reale Bewegung noch zu messen.
- Rechnerischer Freiraum nach Wandhäuten: 854 × 1007 × 860 mm.
- Anycubic-Schnittstelle: Körperfront 22,50 × 38,50 mm, Linse Ø14,30 mm, zwei LEDs Ø5,50 mm.
- Kamerasitz: 0,30 mm radiales Startspiel; physischer Passring entscheidet.
- Kugel: Ø11,00 mm, 5-mm-Stiel; Socket-Coupon 0,15/0,28/0,40 mm radial.
- Kamerafenster: 80 × 90 × 2 mm über 72 × 82 mm Ausschnitt, nominal X=820/Z=590 mm.
- Kamera-FOV ist nicht offiziell aufgelöst und muss am gekauften Modul bestimmt werden.

## Herstellungsentscheidung

Kaufen/zuschneiden: Holzleisten, HDF/Hartfaserplatten, PMMA/PC, Metallscharnier, Gegenleiste, Griffe, Riegel, 2020-Profil, LED-Aluminiumprofile, LEDs, Netzteil/Dimmer, Lüfter und Standardverschraubungen. Drucken: nur projektbezogene Verbinder, Sichtblende, Kamera-, Gelenk- und Fensterteile.

Materialstartwert für Druckteile ist PETG mit 0,6-mm-Düse, 0,30-mm-Schicht, ungefähr 0,68-mm-Linie und vier Funktionswänden. Weiß sichtbare Innenbauteile werden mattweiß gedruckt; außenliegende Kamerateile dürfen dunkel sein.

## Dateien

- Gesamt-CAD: `kobra3max_enclosure_complete.scad`
- Druckteilquelle: `kobra3max_enclosure.scad`
- Bauvorschau: `preview/DRAFT/kobra3max_enclosure_complete.png`
- 24 Fertigungsnetze: `exports/DRAFT/STL/`
- Zuschnitt: `camera_whitebox_cut_list_DRAFT.txt`
- Stückliste: `BOM_CAMERA_WHITEBOX_DRAFT.md`
- Druckprofil: `PRINT_PROFILE_CAMERA_WHITEBOX_DRAFT.md`
- Validierung: `VALIDATION_CAMERA_WHITEBOX_DRAFT.md`
- Herkunft/Lizenz: `provenance/CAMERA_PROVENANCE_DRAFT.md`

## Digitale Evidenz

- 19/19 Maß-/Quellprüfungen PASS;
- 24/24 Netze wasserdicht, positiv orientiert und eine Komponente;
- keine Mesh-Imports in der Projektquelle;
- maximal 13.066 Dreiecke, 2,28 MiB und 280 mm Ausdehnung je Druckteil;
- alle Druckteile innerhalb 420 × 420 × 500 mm;
- aggregiert 56 PASS, sechs REVIEW_REQUIRED, ein NOT_RUN.

## Sicherheit und Grenzen

Die Haube ist groß und wird nur zu zweit an durchgeschraubten Metallgriffen gehoben. Sie ist kein Brandschutzschrank und keine Freigabe zum unbeaufsichtigten Drucken. Netzspannung, Netzteil und Dimmer bleiben außerhalb. Eine spätere Zusatzheizung ist nicht enthalten und öffnet die thermische, elektrische, Kamera-, LED- und Brandschutzprüfung vollständig neu.

## Nächster physischer Schritt

Nur die vier Coupons drucken und prüfen. Anschließend mit provisorischem Rahmen die reale Druckerbewegung und das Kamerabild aufnehmen. Erst wenn Fensterzentrum, Schienenhöhe und Socketwert bestätigt sind, dürfen die endgültigen Kamera-/Fensterteile und Platten zugeschnitten werden. Die finale Kennzeichnung bleibt die letzte geplante Geometrieänderung vor einer späteren Releasefreigabe.
