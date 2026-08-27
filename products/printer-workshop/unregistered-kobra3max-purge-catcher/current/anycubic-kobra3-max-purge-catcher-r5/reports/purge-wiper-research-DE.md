# Purge-Wiper-Nachprüfung – Anycubic Kobra 3 Max Combo

Stand: 26.08.2026

## Belastbare Herstellerangaben

1. Die [offizielle Austausch-Anleitung](https://wiki.anycubic.com/en/fdm-3d-printer/kobra-3-max/purge-wiper-components-replace-guide) zeigt zwei außen zugängliche Befestigungsschrauben vertikal übereinander. Beim Einbau werden Positionierlöcher zur Blechaufnahme ausgerichtet und die Einheit eingeschoben und verschraubt. Eine bemaßte Zeichnung oder ein Lochabstand fehlt.
2. Die [offizielle Fehlerhilfe zum abnormalen Auswurf](https://wiki.anycubic.com/en/fdm-3d-printer/kobra-3-max/troubleshooting-abnormal-discharge-of-purge-wiper-material) fordert die Prüfung, ob der Auswerfer normal zurückfedert, und zeigt eine interne Zugfeder sowie das von Hand zu betätigende Paddel. Damit ist die dynamische, federbelastete Auswurfbewegung bestätigt.
3. Das [offizielle Kobra-3-Max/ACE-2-Pro-Nachrüstpaket](https://ca.anycubic.com/products/kobra-3-max-ace-2-pro-upgrade-bundle) nennt für den Purge Wiper zwei M3×7-Schrauben. Das beschreibt Serienhardware des Ersatzteils, nicht automatisch die erforderliche Länge mit einer zusätzlichen 3-mm-Druckplatte.

## Nicht veröffentlichte Daten

- kein offizieller Schraubenmittenabstand;
- keine bemaßte Einbauhülle oder Freiraumzeichnung;
- kein Hub-/Schwenkraum des Paddels;
- keine Fragmentgeschwindigkeit, Auswurfrichtungstoleranz oder Flugkurve.

Die im Anycubic-Shop bei anderen Purge-Wiper-Varianten auftauchenden 105 × 96 × 61 mm sind Verpackungsmaße und wurden ausdrücklich **nicht** als Kobra-3-Max-Bauteilmaße verwendet.

## R5-Ableitung

| Merkmal | R5-Wert | Evidenzstatus |
|---|---:|---|
| Schraubenanordnung | vertikales Paar | offizielle Bilder |
| Nenndistanz | 20,0 mm | grob bildabgeleitet, keine Spezifikation |
| einstellbarer Bereich | 16,2–23,8 mm | eigene zwei Langlöcher |
| Fangbereich | 62 × 44 mm | eigene kompakte Geometrie |
| Prallwand | 58 mm; obere Zone massiv | eigene Sicherheitsmarge |
| Fanghaube | 8 mm Einzug ab Z=46 mm | eigene, supportfreie Geometrie |
| freier Durchfall | 57 × 39 mm | eigene bodenlose Geometrie |
| Seitenhülle | echte Wabendurchbrüche | Benutzerwunsch; Feinfaden-Test offen |
| Orientierung von vorne | Schrauben/Wischer rechts, Prallwand links | offizielle Reparaturbilder und Frontansicht nachgeprüft |

Das beigefügte BY-NC-Beispiel bestätigte qualitativ ein seitliches Ohr am vertikalen Wischer-Schraubenpaar und nennt M3×10 als Empfehlung seines Autors. Weder dessen Mesh noch Maße oder Konturen wurden übernommen; M3×10 gilt ausdrücklich nicht als Herstellerangabe.

Die R5-Geometrie ist vollständig neu erzeugt. Der bildabgeleitete 20-mm-Wert ist nur ein Startpunkt für die beiliegende Messlehre. Erst bestandene Lehre, freie Paddelbewegung und drei beaufsichtigte Purge-Zyklen schließen die offenen physischen Gates.
