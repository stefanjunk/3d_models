# Validierungsbericht – Kobra 3 Max Kamera-Whitebox DRAFT

## Gate-Ergebnis

`PASS` für den deklarierten digitalen DRAFT-Umfang. Von 63 aggregierten Prüfungen sind 56 `PASS`, sechs physische Prüfungen `REVIEW_REQUIRED` und der exakte Slicer-Preflight `NOT_RUN`. Das ist keine Release-, Kaufzuschnitt- oder Druckfreigabe.

## Umgebung

- OpenSCAD 2021.01 und Blender 5.2.0 LTS verfügbar;
- Python 3.11.15, Trimesh 4.4.1 und YAML-Unterstützung verfügbar;
- kein ausführbarer Orca-/Prusa-Slicer gefunden;
- `manifold3d` und `rtree` fehlen, waren für die deklarierten Meshprüfungen aber nicht erforderlich;
- keine Pakete installiert und keine Druckersteuerung ausgeführt.

## Quellen- und Maßvertrag

Der deterministische Vertrag prüft 19 Pflichtbedingungen und besteht vollständig. Geprüfte Quellen sind `design-spec.yaml`, `kobra3max_enclosure.scad`, `kobra3max_enclosure_complete.scad` und `camera_whitebox_dimensions.py`.

| Prüfung | Ergebnis |
|---|---:|
| seitlicher rechnerischer Abstand zum Keep-out, je Seite | 74,0 mm – PASS |
| vorderer/hinterer Abstand bei Zentrierung, je Seite | 33,5 mm – PASS |
| Höhenreserve | 107,0 mm – PASS |
| Haupttür | 740 × 880 mm – PASS |
| feste Servicezone | 140 mm – PASS |
| Kameragabel | 6,65 mm für 6,0-mm-Auge – PASS |
| M4-Gelenkloch | 4,5 mm – PASS |
| Kameraschnittstelle | 22,50 × 38,50 mm, Linse Ø14,30, LEDs Ø5,50 – PASS |
| geschützte Kameratiefe | 25,30 mm für 25,00-mm-Referenz – PASS |
| Kamerasitz-Spiel | 0,30 mm radial, Coupon vorhanden – PASS |
| Kugelgelenk | Ø11,00 mm / 0,28 mm nominal radial – PASS |
| optische Scheibe / Ausschnitt | 80 × 90 mm / 72 × 82 mm – PASS |
| Fensterrahmen im Servicefeld | 22 mm Seitenrand – PASS |
| Fensterscheibenneigung | 7° – PASS |
| Mesh-Imports im Projekt-CAD | 0 – PASS |
| vollständige Baugruppen-Subsysteme | Rahmen/Front/Kamera/Licht/Abluft vorhanden – PASS |
| Abstand Lüfterausschnitt zu hinterer/oberer Kante | 70 / 110 mm – PASS |
| Blenden-Einlassfläche gegenüber Ø114-mm-Lüfteröffnung | 96,9 % – PASS |

Die Tiefe bleibt der engste rechnerische Wert. Bettkabel und asymmetrische Bewegung sind vor dem Zuschnitt physisch zu messen.

## Fertigungsnetze

- 24/24 eindeutige DRAFT-STLs wasserdicht;
- 24/24 mit konsistenter Orientierung, positivem Volumen und genau einer Komponente;
- null Randkanten, nichtmannigfaltige Kanten, degenerierte oder doppelte Dreiecke;
- alle Teile passen bei Achsendrehung in 420 × 420 × 500 mm;
- 52.268 Dreiecke und 8,55 MiB über alle eindeutigen Dateien;
- größtes Netz: Dreifach-Socket-Coupon mit 13.066 Dreiecken und 2,28 MiB;
- größte Druckteilausdehnung: 280 mm;
- Mesh-Gesamtstatus: `PASS`.

## Fertigungsprüfung

- Druckreihenfolge, Orientierung und PETG-Startprofil sind dokumentiert;
- Kamera-, Kugel/Socket- und Gabelcoupons sind erzeugt;
- Supportfreiheit ist für die Standardorientierungen vorgesehen und im echten Slicer zu bestätigen;
- exakte Zeit, Material, Layerzahl, Support, Werkzeugpfade und Spitzenfluss: `NOT_RUN`.

## Physische Gates

`REVIEW_REQUIRED`:

1. originale Anycubic-Kamera im Passring und Gehäuse ohne Biegung, optische Abschattung oder Kabelquetschung;
2. Auswahl und 24-Stunden-Haltetest des 11-mm-Sockets;
3. vollständiger ausgeschalteter Bewegungs-/Kabelsweep des realen Druckers;
4. Türöffnung ohne Kollision mit Display, Kamera, Riegeln oder Kabeln;
5. Probeaufnahmen, Hintergrund, Fensterreflexe, Flimmern, Hotspots, Weißabgleich und Temperatur;
6. Zwei-Personen-Anheben, Griff-/Rahmenstabilität und Dachkassetten-Sicherung.

## Releaseblocker

- kein exakter Slicer-Preflight;
- keine physischen Passungs-, Bewegungs-, Licht-, Temperatur- und Handhabungsdaten;
- Fensterzentrum und endgültige Kamerahöhe noch nicht durch reales FOV bestätigt;
- finale JuSt-Innovation-Kennzeichnung ist bewusst noch nicht als letzte Geometrieänderung integriert;
- finale Nutzerfreigabe fehlt.

Maschinenlesbare Evidenz:

- `reports/environment.json`
- `reports/autonomy-validation.json`
- `reports/camera-whitebox-contract.json`
- `reports/validation-summary-draft.json`
