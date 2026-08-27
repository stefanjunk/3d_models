# Kamera-Whitebox für den Anycubic Kobra 3 Max – DRAFT

## Ergebnis

Die vollständige parametrische Konstruktion beschreibt eine bodenlose, überstülpbare Fotohaube mit 900 × 1050 × 900 mm Außenmaß und einer abnehmbaren, etwa 60 mm hohen Lichtkassette. Seiten, Rückwand und das feste Frontfeld sind innen mattweiß; nur die links angeschlagene Haupttür und ein kleines geneigtes Kamerafenster sind klar.

Nach den 3-mm-Wandhäuten bleiben rechnerisch etwa 854 × 1007 × 860 mm frei. Der vorhandene konservative Drucker-Planungsraum von 706 × 940 × 753 mm ist geometrisch enthalten. Kabelbogen, Bettbewegung, Filamentweg und reale Außenkontur müssen trotzdem vor jedem Plattenzuschnitt am ausgeschalteten Drucker überprüft werden.

## Konstruktion

- außenliegender Rahmen aus 20 × 20 mm Holzleisten mit unterem Versteifungsring;
- 3-mm-Hartfaserplatte/HDF, einseitig weiß beschichtet, für Seiten, Rückwand und festes Frontfeld;
- klare 4-mm-PMMA-Tür, links angeschlagen, mit Metallscharnier und Gegenleiste;
- 80 × 90 × 2 mm klares Kamerafenster im festen Frontfeld, um 7° geneigt;
- opaler 3-mm-Dachdiffusor und abnehmbare Lichtkassette;
- sechs Dachlichtläufe und zwei getrennt dimmbare Fülllichtzonen, 5000 ± 500 K, CRI ≥ 95;
- originale Anycubic-Kamera außerhalb des Innenraums auf einer 500-mm-2020-Schiene;
- neu konstruiertes Kameragehäuse, kurzer Arm und 11-mm-Kugelgelenk ohne importierte Fremdgeometrie;
- 120-mm-Abluft rechts hinten/oben, innen von einer matten weißen Blende verdeckt;
- kein Boden und keine Zusatzheizung.

Vollflächige LED-Wände wurden verworfen. Die weißen Wände reflektieren Dach- und Fülllicht bereits; Leuchtwände wären teurer und wärmer, hätten mehr Fehlerstellen und würden nützliche Formschatten am Druckobjekt reduzieren.

## Zentrale Dateien

| Datei | Zweck |
|---|---|
| `kobra3max_enclosure_complete.scad` | vollständige parametrische Baugruppe |
| `camera_whitebox_assembly_preview.scad` | kompatibler Einstieg in die Gesamtansicht |
| `kobra3max_enclosure.scad` | parametrische Quelle aller Druckteile |
| `camera_whitebox_dimensions.py` | berechnet Zuschnitte für andere Körpermaße |
| `camera_whitebox_cut_list_DRAFT.txt` | Standardzuschnitt 900 × 1050 × 900 mm |
| `BOM_CAMERA_WHITEBOX_DRAFT.md` | Kauf-/Druckteil-Stückliste |
| `build_camera_whitebox_draft.sh` | erzeugt DRAFT-STLs und Gesamtvorschau |
| `design-spec.yaml` | Anforderungen, Maße und Freigabestatus |
| `provenance/CAMERA_PROVENANCE_DRAFT.md` | Herkunfts- und Lizenztrennung der Kamera |
| `baseline_v1/` | unveränderte Ausgangsversion |

## Empfohlene Bau- und Prüfsequenz

### 1. Nur Coupons drucken

Zuerst `DRAFT_camera_fit_frame_coupon.stl`, `DRAFT_camera_ball_test_pin.stl`, `DRAFT_camera_ball_socket_coupon.stl` und `DRAFT_camera_fork_fit_coupon.stl` drucken. Der Kameraring darf PCB/Gehäuse nicht biegen. Beim Dreifach-Socket stehen die Positionen von links nach rechts für 0,15, 0,28 und 0,40 mm radiales Spiel. Gewählt wird der kleinste Socket, der handverstellbar ist, die Kugel nicht beschädigt und die Kameraposition ohne Kriechen hält.

### 2. Reale Bewegungsgrenzen und Kamerablick prüfen

Drucker ausschalten, Bett und Druckkopf über den gesamten Bereich bewegen und Kabel, Filamentweg sowie Display mitmessen. Den 900 × 1050 × 900 mm großen Rahmen zunächst provisorisch markieren. Die Kamera auf der Displayseite ungefähr 590 mm über Tischhöhe positionieren und Probeaufnahmen von flachen, typischen und 400–450 mm hohen Objekten erstellen. Erst danach Fensterzentrum und Schienenposition endgültig bohren.

### 3. Bodenlosen Rahmen bauen

Unteren und oberen Rechteckrahmen aus je zwei 860-mm- und zwei 1010-mm-Leisten bauen. Vier 900-mm-Pfosten einsetzen, diagonal ausrichten und mit äußeren Eckverbindern verschrauben. Der untere Ring liegt später auf EPDM-Band, ist aber keine Bodenplatte. Die große Haube nur zu zweit an zwei durchgeschraubten Metallgriffen heben.

### 4. Weiße Innenhaut montieren

Seiten-, Rück- und Serviceplatte mit der weißen Seite nach innen gegen die inneren Rahmenflächen setzen. Mechanisch mit breiten Köpfen/Abdeckungen sichern; Klebstoff nur ergänzend verwenden. Matte weiße Kantenstreifen verhindern dunkle Linien. Die 250 × 170 mm große Lüfter-Serviceöffnung erst nach realer Markierung schneiden.

### 5. Tür montieren

Der 860-mm-Servicesteg sitzt 140 mm vor dem rechten Außenrand. Die 740 × 880 × 4 mm klare Tür deckt die linke Öffnung ab. Ein ungefähr 800 mm langes Metallscharnier und eine Aluminiumgegenleiste verteilen die Last. PMMA nicht punktförmig vorspannen. Oben und unten rechts je einen mechanischen Schnäpper vorsehen.

### 6. Kamerafenster und Kamera montieren

Im festen weißen Servicefeld ist nominal ein 72 × 82 mm Ausschnitt um den Punkt X=820/Z=590 mm vorgesehen. Der matte Innenrahmen verdeckt die Schnittkante. Außen halten 7°-Keil, 80 × 90 × 2 mm klare Scheibe, dünnes EPDM und Klemmrahmen das Fenster. Schrauben nur so anziehen, dass die Scheibe nicht verspannt wird.

Die 2020-Schiene sitzt außen. Schlitten und kurzer Arm verwenden ein M4-Gelenk; die neue Kamerarückseite trägt eine 11-mm-Kugel. Die Kamera blickt durch das Fenster in den Innenraum. Ihre integrierten LEDs bleiben für normale Aufnahmen aus, um Reflexe an Tür und Fenster zu vermeiden.

### 7. Lichtdach montieren

Den opalen Dachdiffusor auf der oberen Rahmenöffnung sichern. Die Dachkassette erhält sechs ungefähr 940 mm lange LED-Aluminiumprofile. Netzteil und Dreikanal-Dimmer bleiben außerhalb. Dach, linkes und rechtes Fülllicht getrennt einstellen. Mit der echten Kamera auf Banding, Hotspots, Doppelkonturen, Weißabgleich und Belichtungsstabilität prüfen.

### 8. Abluft und thermische Prüfung

Lüfter und Adapter sitzen außen rechts hinten/oben. Innen verdeckt die weiße Blende den dunklen Lüfter; ihre offene Seite zeigt nach unten. Während eines langen repräsentativen Drucks Temperaturen an Kamera, Dachdiffusor, LED-Profilen und Kabeln messen. Eine spätere Zusatzheizung ist nicht durch diese Revision freigegeben und erfordert eine neue Sicherheits- und Materialprüfung.

## Grenzen

- Alle Fertigungsdateien bleiben bis zu physischen Tests und finaler Freigabe `DRAFT`.
- Das Projekt ist kein Brandschutzschrank und keine Freigabe für unbeaufsichtigtes Drucken.
- Ein exakter lokaler Slicer-Preflight mit dem vorgesehenen Kobra-3-Max-PETG-Profil steht noch aus.
- Originalkamera, offizielle Referenz-STLs und fremde Archivdateien sind nicht Teil des auslieferbaren CAD-Pakets.
