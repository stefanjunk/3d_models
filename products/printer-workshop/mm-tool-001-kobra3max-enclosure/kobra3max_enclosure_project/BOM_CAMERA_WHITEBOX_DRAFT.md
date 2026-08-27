# Stückliste – Kobra 3 Max Kamera-Whitebox DRAFT

Günstige Hybridbauweise: Großteile werden gekauft und zugeschnitten; nur passgenaue Verbinder, Kamera-, Fenster- und Lüfterteile werden gedruckt. Lieferantenartikel bleiben austauschbar, solange Maße, Temperaturfreigaben und elektrische Daten erfüllt sind.

## Rahmen und Platten

| Menge | Bauteil | Spezifikation | Herstellung |
|---:|---|---|---|
| ca. 18 m | gerade Holzleisten | 20 × 20 mm; trocken und verzugsarm | kaufen/zuschneiden |
| 2 | Seitenwand | 1050 × 900 × 3 mm, einseitig weiß beschichtete Hartfaserplatte | kaufen/zuschneiden |
| 1 | Rückwand | 900 × 900 × 3 mm, einseitig weiß beschichtete Hartfaserplatte | kaufen/zuschneiden |
| 1 | festes Front-/Servicefeld | 140 × 880 × 3 mm, einseitig weiß beschichtete Hartfaserplatte | kaufen/zuschneiden |
| 1 | Dachdiffusor | 860 × 1010 × 3 mm, opales PMMA oder Polycarbonat | kaufen/zuschneiden |
| 1 | Haupttür | 740 × 880 × 4 mm, klares PMMA | kaufen/zuschneiden |
| 1 | optisches Kamerafenster | 80 × 90 × 2 mm, klares optisch ruhiges PMMA oder PC | kaufen/zuschneiden |
| 1 | Lichtkassettendeckel | 852 × 1002 mm, leichte weiße Platte | kaufen/zuschneiden |
| nach Bedarf | weißes Fugen-/Kantenband | matt, temperaturgeeignet | kaufen |
| ca. 8 m | EPDM-Dichtband | geschlossenporig, ungefähr 10 × 2 mm | kaufen |

## Tür und Handhabung

| Menge | Bauteil | Spezifikation | Hinweis |
|---:|---|---|---|
| 1 | durchgehendes Metallband | ungefähr 800 mm, für 4-mm-PMMA mit Gegenleiste | nicht drucken |
| 1 | Gegenleiste | Aluminiumflachmaterial ungefähr 20 × 2 × 800 mm | verteilt die Türlast |
| 2 | Magnet-/Rollenschnäpper | mechanisch verschraubbar | oben und unten rechts |
| 1 | Türgriff | Metall, durchgeschraubt | breite Scheiben verwenden |
| 2 | Seitengriff | Metall, durchgeschraubt, mit Gegenplatte | Haube ausschließlich zu zweit heben |
| nach Bedarf | M4-Schrauben, Muttern, Scheiben | für PMMA nur mit breiter Lastverteilung | kaufen |

## Kamera und optisches Fenster

| Menge | Bauteil | Spezifikation | Hinweis |
|---:|---|---|---|
| 1 | originale Anycubic Live View Camera | gekauftes Modul für Kobra 3 Max | Elektronik/Kabel werden nicht weitergegeben |
| 1 | vertikale Schiene | 2020-T-Nut-Profil, 500 mm | außen am festen Servicefeld |
| 2–4 | T-Nut und Schraube | M5 passend zum Profil | kaufen |
| 1 zuerst | Gehäuse-Passring | `DRAFT_camera_fit_frame_coupon.stl` | realen Kamerasitz vor Gehäusedruck prüfen |
| 1 zuerst | Kugel-Teststift | `DRAFT_camera_ball_test_pin.stl` | zusammen mit dem Socket-Coupon drucken |
| 1 zuerst | Dreifach-Socket-Coupon | `DRAFT_camera_ball_socket_coupon.stl` | links/rechts: 0,15 / 0,28 / 0,40 mm radial |
| 1 | Kameraschlitten | `DRAFT_camera_2020_slider_fork.stl` | M5 an 2020, M4 am Armauge |
| 1 | kurzer Gelenkarm | `DRAFT_camera_short_socket_arm.stl` | 11-mm-Socket; Wert nach Coupon wählen |
| 1 | Kamerafrontschale | `DRAFT_camera_front_shell.stl` | Aperturen nach offiziellen Schnittstellenmaßen |
| 1 | Rückdeckel mit Kugel | `DRAFT_camera_back_cover_ball.stl` | belüftet, Kabelauslass nach unten |
| 2 | Gehäuseschraube | M2,5 × 20 mm, selbstschneidend für Kunststoff | durch interne Stege, nur leicht anziehen |
| 1 | matte Innenblende | `DRAFT_camera_window_inner_bezel.stl`, weißes PETG | verdeckt dunkle Schnittkanten |
| 1 | 7°-Fensterkeil | `DRAFT_camera_window_outer_wedge.stl` | außen |
| 1 | Fensterklemmrahmen | `DRAFT_camera_window_clamp_frame.stl` | außen, mit dünnem EPDM |
| 4 | Fensterschraube | M4 mit Scheiben und Sicherungsmuttern | Pane nicht verspannen |

Die Kamerageometrie ist projektlokal neu konstruiert. Fremde Referenz-STLs dienen ausschließlich als dokumentierte Maßquelle und werden weder importiert noch ausgeliefert.

## Beleuchtung und Elektrik

| Menge | Bauteil | Spezifikation | Hinweis |
|---:|---|---|---|
| ca. 6 m | Dach-LED | 24 V, 4500–5500 K, CRI ≥ 95 | hohe LED-Dichte oder COB bevorzugt |
| ca. 1,2 m | Fülllicht | gleiche Farbtemperatur/Farbwiedergabe wie Dach | zwei getrennte Zonen |
| 6 × ca. 940 mm | Dachprofil/Wärmeverteiler | Aluminiumprofil, ungefähr 17 × 8 mm oder Lieferantenclip | LED nicht direkt auf Holz/HDF kleben |
| 2 × 610 mm | opales LED-Profil | linkes/rechtes Fülllicht | keine sichtbaren LED-Punkte |
| optional | Profilclip | `DRAFT_led_profile_clip_17x8.stl` | erst an gekauftem Profil prüfen |
| 1 | Netzteil | extern, 24 V, ungefähr 100–120 W, mit Herstellerzulassung | Netzspannung außerhalb der Haube |
| 1 | Dreikanal-Dimmer | Dach/links/rechts, kameratauglich flimmerarm | Banding-Test Pflicht |
| 1 Satz | Sicherungen, Leitungen, Steckverbinder | passend zu Leistung und Herstellerangaben | Zugentlastung außerhalb der Kammer |

Flächen-LED-Wände sind nicht vorgesehen: Weiße Wände plus drei dimmbare Lichtzonen sind billiger, kühler, wartbarer und erzeugen brauchbarere Formschatten.

## Abluft

| Menge | Bauteil | Spezifikation | Hinweis |
|---:|---|---|---|
| 1 | regelbarer 120-mm-Lüfter | saugt nach außen | Herstellerdaten beachten |
| 1 | Serviceplatte | `DRAFT_service_panel_120_ports.stl` | rechte Seitenwand, hinten/oben |
| 1 | weiße Sichtblende | `DRAFT_exhaust_camera_baffle_120.stl` | innen, Öffnung nach unten |
| 1 | Schlauchadapter | `DRAFT_fan_adapter_120_to_100.stl` | nur bei 100-mm-Schlauch |
| 1 | Lüftergitter | `DRAFT_fan_guard_120.stl` | Berührungsschutz |

## Gedruckte Rahmenteile

| Menge | Datei | Funktion |
|---:|---|---|
| 8 | `DRAFT_corner_gusset_3way.stl` | äußere Rahmenecken |
| 2 | `DRAFT_flat_t_bracket.stl` | mittlere Dachleiste |
| 4 | `DRAFT_roof_cassette_corner_locator.stl` | positioniert die Lichtkassette |
| 1 | `DRAFT_exhaust_camera_baffle_120.stl` | weißer Hintergrund vor dem Lüfter |
| 6–8 | `DRAFT_panel_retainer_clip.stl` | hält den Dachdiffusor |
| 4 | `DRAFT_turn_clip.stl` plus Spacer | vertikale Sicherung der Lichtkassette |

## Nicht enthalten

- keine Bodenplatte;
- keine aktive Zusatzheizung;
- keine Netzspannungsinstallation in der Haube;
- keine Brandschutz- oder Unbeaufsichtigt-Drucken-Freigabe;
- keine Freigabe der Zuschnitte vor realem Bewegungsraum- und Kamera-FOV-Test.
