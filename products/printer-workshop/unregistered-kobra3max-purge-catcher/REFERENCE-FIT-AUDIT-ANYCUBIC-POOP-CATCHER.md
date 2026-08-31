# Fit-Audit der Drittanbieter-3MF

Stand: 2026-08-31
Status: starke externe Fit-Referenz, keine eigene oder kommerziell freigegebene Fertigungsgeometrie

## Geprüfte Datei

Der maschinenlesbare Befund steht in
`REFERENCE-FIT-AUDIT-ANYCUBIC-POOP-CATCHER.json`.

- Repository-Pfad: `research/third-party/printer-workshop/Anycubic_Kobra_3_Max_Poop_catcher.3mf`
- SHA-256: `ba353bf0d44328b406599fe770307c4221e9f29cc2d04447abcf688eba4df35d`
- Größe: 1.423.849 Byte
- 3MF-Anwendung: `BambuStudio-02.00.03.54`
- eingebetteter Titel: `Anycubic Kobra 3 Max version 1 Poop Catcher`
- Designer: `Meisech`, Benutzer-ID `487044581`
- Erstellungs-/Änderungsdatum: 2025-05-13
- eingebettete Lizenzangabe: `BY-NC`, ohne Versionsnummer oder vollständigen Lizenztext
- MakerWorld-Modellkennung: `DSM00000001326104`; Design-ID `US41f6be5deb5489`

Die zuvor vorhandene Datei mit dem Suffix `(1)` war bytegleich und wurde als
unnötige Doppelkopie entfernt. Die oben genannte, bereits getrackte Datei blieb
unverändert erhalten.

## Ergebnis

Diese Datei ist die bisher stärkste lokale Referenz für die reale Einbaulage.
Sie verwendet genau die zwei vertikal angeordneten Wiper-Schrauben, fährt mit
der Z-Achse mit und positioniert die Fangöffnung unmittelbar neben der
Purge-Ablage. Drei in der 3MF eingebettete Fotos zeigen den gedruckten Catcher
montiert an einem Anycubic Kobra 3 Max.

Die beiden vertikalen Befestigungsschlitze besitzen im Mesh denselben nominalen
17-mm-Achsabstand wie die unabhängige Benutzermessung `M-R7-001`. Damit werden
Schraubenpaar, physische Seite und grundsätzliche Orientierung wesentlich besser
belegt als durch R7-DRAFT-2. Das ist jedoch kein Recht, die fremde Schlitzkontur,
den Gehäuseumriss oder daraus abgelesene Maße in eine eigene Konstruktion zu
übernehmen.

Die Benutzerbewertung vom 31. August 2026 lautet: „this would fit perfectly“.
Sie wird als Fit-Evidenz für die Referenz und nicht als physischer Test unseres
eigenen Modells behandelt.

## Geometrie und Bauteile

| Bauteil | Außenmaß des eingebetteten Meshs | Dreiecke | Topologie |
|---|---:|---:|---|
| `Poop catcher.stl` | 74,092 × 38,975 × 120,000 mm | 46.960 | geschlossen, orientiert, positives Volumen; 34 degenerierte Facetten im unabhängigen Audit |
| `Drawer.stl` | 69,329 × 40,853 × 2,482 mm | 4.748 | geschlossen, orientiert, positives Volumen; keine degenerierten Facetten |

Der Hauptkörper ist ein mitfahrender, etwa 120 mm hoher Speicherbehälter mit
direkter Zweischraubenmontage. Die flache Bodenklappe wird separat gedruckt und
zum Entleeren herausgezogen. Ein drittes 25,6-mm-Würfelobjekt ist nur als
`support_enforcer` für die Klappenaufnahme markiert und kein Produktbauteil.

Diese Architektur unterscheidet sich entscheidend von R7-DRAFT-2:

- keine zusätzliche Maschinen-Datumplatte;
- kein eigener Schlitten oder Schnellverschluss zwischen Wiper und Catcher;
- keine frei interpretierte 62 × 44 × 62-mm-Fangbox vor dem Schraubendatum;
- integrierter, mitfahrender Speicher statt stationärem Unterbehälter;
- zwei längere Schrauben werden gemeinsam mit dem vorhandenen Purge-Wiper
  montiert; der eingebettete Beschreibungstext nennt `M3x10` als Empfehlung.

Das erklärt die bessere Passwahrscheinlichkeit: Die Anzahl unbekannter
Interfaces und die zusätzliche Hüllkurve werden stark reduziert.

## 3MF- und Mesh-Prüfung

Der Projektvalidator `fdm_ci.py validate-3mf --profile draft` meldet `FAIL`, weil
das Bambu-Studio-Paket seine Meshobjekte über die 3MF-Production-Erweiterung in
`3D/Objects/` referenziert. Der Core-Validator behandelt diese externen
Objekt-IDs als fehlend. Das ist ein Portabilitätsproblem des Projektcontainers,
nicht automatisch ein defektes Mesh.

Nach getrennter Extraktion bestehen Hauptkörper und Schublade den unabhängigen
Mesh-Audit auf Wasserdichtheit, konsistente Orientierung und positives Volumen.
Beim Hauptkörper bleiben 34 degenerierte Facetten als Reparatur-/Slicerhinweis.

## Druckprofil und Support

Die eingebetteten Einstellungen sind **nicht** für den Anycubic Kobra 3 Max:

- Druckerprofil: `Bambu Lab P1S 0.4 nozzle`;
- Prozess: `0.2mm layer, 2 walls, 50% infill`;
- das Beschreibungsfeld empfiehlt abweichend 100 % Infill für den Hauptkörper
  und 15 % für die Schublade;
- für die Klappenaufnahme ist ein manuell gesetzter Support-Enforcer enthalten.

Die Datei darf deshalb nicht mit ihren eingebetteten Maschinen- und
Prozessdaten an den Anycubic-Drucker gesendet werden. Für einen persönlichen
Test müssten die Produktmeshes in Anycubic Slicer Next mit einem vollständigen
Kobra-3-Max-Maschinen-, Prozess- und Filamentprofil neu gesliced und die
Klappenaufnahme visuell geprüft werden. Ein Upload oder Druckstart ist nicht
Teil dieses Audits.

## Rechte- und Designentscheidung

`BY-NC` kennzeichnet mindestens Namensnennung und nichtkommerzielle Nutzung;
die genaue Lizenzversion ist in der Datei nicht angegeben. Für das eigene
metriMade-Modell gelten deshalb weiterhin diese Grenzen:

- keine Übernahme oder Nachzeichnung des Meshs;
- keine Übernahme von Schlitz-, Gehäuse-, Klappen-, Loch- oder
  Perforationskonturen;
- keine Verwendung der Fremdmaße als CAD-Quelle;
- keine Weitergabe der eingebetteten Fotos oder Projektmetadaten in eigenen
  Exporten;
- nur das allgemeine Prinzip „direkt mit zwei vorhandenen Wiper-Schrauben,
  Fangöffnung unmittelbar an der Quelle, möglichst wenige Zwischeninterfaces“
  darf als Lösungsrichtung dienen.

Für eine eigene Konstruktion bleiben eine selbst vermessene Lochbildlehre, ein
eigener konservativer Umrisscoupon und ein stromloser Vollwegtest erforderlich.
Bis diese Nachweise vorliegen, bleibt R7 gesperrt und es gibt keine eigene zum
Druck empfohlene Fassung.
