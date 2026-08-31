# R7 – lizenzgetrennte Analyse der Montage- und Aufstellprinzipien

Stand: 2026-08-31
Status: Anforderungen/Ideation, keine CAD-Ableitung

## Ausgangslage

Der R6-Fangkopf erfüllt die gewünschte kurze Fangstrecke grundsätzlich, sein physisches System ist aber ungünstig: Ein nicht real vermessenes Wiper-Schraubenpaar trägt einen separaten Adapter, der Fangkopf muss von oben in eine reibschlüssige Schwalbenschwanzführung gesetzt werden, und der Unterbehälter steht als zweites Objekt darunter. Entscheidend ist außerdem die vom Benutzer nachgereichte Kinematik: Der Purge-Wiper und damit die Auswurfquelle fahren während des Drucks entlang Z nach oben; Purge kann deshalb auf verschiedenen Z-Höhen entstehen. Ein stationärer Fangkopf oder Dock-Tower auf nur einer Höhe löst die Aufgabe nicht. Die reale Passung und alle Kollisions- und Purge-Tests sind weiterhin offen.

## Rechte- und Nutzungspolitik

Die Dateien unter `research/third-party/printer-workshop/` bleiben reine Betrachtungsquellen. Es wird kein Mesh importiert, kein Profil nachgezeichnet, kein Maß übernommen, kein Bild ausgeliefert und kein Fremdmodell in einem R7-Export eingebettet. Selbst Dateien mit Metadaten werden nicht als Rechtefreigabe für kommerzielle Ableitungen verstanden.

Der detaillierte Audit der vom Benutzer als passend bewerteten Meisech-3MF
steht in `REFERENCE-FIT-AUDIT-ANYCUBIC-POOP-CATCHER.md`. Die eingebetteten
Montagefotos und die Übereinstimmung des nominellen 17-mm-Lochachsenabstands mit
der unabhängigen Benutzermessung erhöhen die Evidenz für Seite, Orientierung
und direktes Zweischraubenprinzip. Sie ändern die Clean-Room-Grenze nicht.

| Lokale Datei | SHA-256 | Lokale Rechteinformation | Nur abstrahiertes Prinzip | Aus R7 ausgeschlossen |
|---|---|---|---|---|
| `Anycubic_Kobra_3_Max_Poop_catcher.3mf` | `ba353bf0d44328b406599fe770307c4221e9f29cc2d04447abcf688eba4df35d` | eingebettet: Designer `Meisech`, `BY-NC`; die bytegleiche `(1)`-Doppelkopie wurde am 31.08.2026 entfernt | Eine direkt am mitfahrenden Wiper verschraubte Fangzone reduziert Flugweg und Zwischeninterfaces. | Gehäuse, Schublade, Schraub-/Schlitzkontur, Lochbild, Perforation und alle Maße |
| `Poop+catcher+LBI3D.3mf` | `b431af0b8a3761aea82b5efc26330c35c6d6220c04a78e5ff3896f4b7d5aebcb` | eingebettet: `Standard Digital File License`; zusätzlich Verweis auf das BY-NC-Ursprungsmodell | Lokales Umlenken und entfernte Speicherkapazität sind zwei getrennte Funktionen. | sämtliche Remix-Geometrie, Kontakt-/Clipkonturen, Ausschnitte, Maße und Bilder |
| `Poopbin.3mf` | `b486e11cb3d1f25b52b150054153bad166f38108ee5658e5382aea66d037ef6f` | eingebettet: Designer `MrBaham`, `BY-NC-SA` | Eine große Standfläche kann die Maschine von Behälterlasten entkoppeln. | Behältersilhouette, hohe Rückwand, Seitenprofil, Radien, Maße und Bildmaterial |
| `poubelle+anycubic.3mf` | `a81e341d829760ccb0b1512e27e858d7510ed49a6ecfbfaef723a5d316bea6a7` | eingebettet: `MakerWorld Exclusive License`, als Remix mit BY-NC-SA-Verweis | Ein frei aufgestellter Behälter ist wartungsarm, braucht aber eine reproduzierbare Positionierung. | gesamte Remix-/Ursprungsgeometrie, Logo, Kontur und Maße |
| `poop-catcher.stl` | `85f011f784d0ae31484c3da0c564553c721d38be1b94724cc8420e94e6a4f399` | keine Lizenzmetadaten im STL; Rechte daher unbekannt | kein zusätzliches Prinzip erforderlich | vollständige Datei und jede geometrische Ableitung |
| `PURGE DIVERTER 2.STEP` | `7adbdf50de61c18f3e36f3ff52522d14573cfd10b23ad1666c58c88e641779c4` | keine verlässliche lokale Lizenz-/Urheberangabe | Eine offene Fallstrecke kann Fangfunktion und Speicherfunktion entkoppeln. | B-Rep, Flansch, Bohrungen, Rippen, Öffnungsform, Maße und Topologie |
| `ptfe_release.3mf` | `3b64f2b149dec0c15896c870fefed7f46c3a2c56952d87f0c1460c26e1eb7984` | keine Rechteangabe | für den Purge-Catcher nicht relevant | vollständig ausgeschlossen |

## Abstrahierte Lösungsräume

1. **Direkt verschraubter, mitfahrender Fangkopf:** bleibt im Bezugssystem der Auswurfquelle und ist kompakt, macht aber bewegte Masse, Schraubenlänge, Gewindeeingriff und Wiper-Ausrichtung kritisch.
2. **Aufgeschnappter Kurz-Umlenker:** sehr wenig Masse nahe am Auswurf, benötigt jedoch ein präzises, noch unbekanntes Gehäuseprofil und kann durch Wärme, Kriechen oder Montagekräfte ausfallen.
3. **Lose freistehende Großbox:** keine Maschinenlast und einfache Reinigung, aber keine gemeinsame Datumskette zwischen Auswurf, Fangzone und Behälter.
4. **Zweistufiges System:** Die kleine Fang-/Umlenkzone folgt der bewegten Auswurfquelle, während die große Speicherkapazität stationär bleibt. Der stationäre Einlauf muss die reale Landefläche über den gesamten freigegebenen Z-Bereich mit Reserve abdecken.

## Eigenständige R7-Richtung

R7 kombiniert nur das abstrakte zweistufige Funktionsprinzip mit einer neu konstruierten Mechanik:

- Ein leichter „Z-Rider“ aus Fangkopf und kurzem Abwärts-Umlenker fährt direkt mit dem Wiper und bleibt damit auf jeder Z-Höhe an der Purge-Quelle.
- Eine minimale, eigene Datumplatte nutzt das am realen Drucker mit 17 mm Mitte-Mitte-Abstand gemessene Wiper-Schraubenpaar; weder Kontaktprofile noch Maße aus Fremdmodellen werden übernommen. Die Übereinstimmung mit dem bisherigen R6-Parameter ist eine unabhängige Realbestätigung, keine Referenzübernahme.
- Der Fangkopf wird über zwei eigene Führungsdatums und eine positive Rastung mit sehr kurzem seitlichem oder schwenkendem Serviceweg gelöst; eine lange vertikale Entnahme entfällt.
- Der Umlenker führt offen und stetig nach unten, ohne Purge in einem Tower, Schlauch oder mitfahrenden Speicher zu sammeln.
- Ein großer stationärer Behälter steht darunter. Seine Einlaufkontur wird nicht aus Referenzgeometrie, sondern aus markierten realen Landepunkten bei niedriger, mittlerer und hoher Z-Position abgeleitet.

Damit entfallen der freistehende Dock-Tower aus Anforderungen `.1`, der vertikale R6-Schwalbenschwanz und jede Führung über die volle Z-Höhe. Die konkrete Geometrie wird erst nach Anforderungs- und Konzeptfreigabe erzeugt.

## Lokale Foto- und Maßevidenz

Sechs Originalfotos unter `Photos-1-001/` zeigen die reale Wiper-Baugruppe, die zwei vertikal angeordneten Schrauben und mehrere angelegte Maßstäbe. Die Rohdateien, Hashes, Pixelmaße, Datumsdefinitionen und Unsicherheitsgrenzen sind in `WIPER-PHOTO-MEASUREMENTS-R7.yaml` erfasst. Benutzerseitig gemessen wurden:

- 17 mm Mitte–Mitte zwischen oberer und unterer Wiper-Schraube;
- 10 mm von der unteren Schraube zur bezeichneten Purge-Ablageebene;
- 37 mm vom bezeichneten Schraubendatum zur horizontalen Purge-Wurfbahn;
- 40 mm von der Schraubenebene horizontal nach hinten bis zur Wiper-Ausdehnung.

Die Bilder stützen eine dünne frontseitige Schrauben-Datumplatte: Die Köpfe sind zugänglich, während direkt hinter und neben der Auflage bewegte bzw. wipernahe Bauteile liegen. Ein tief gehäuseumgreifender Clip oder langer vertikaler Schlitten würde mehr unbekannte Kontur und Kollisionsraum beanspruchen. Die Fotos ersetzen dennoch keinen rechtwinkligen Datums- oder Vollwegcoupon.

## Noch benötigte reale Evidenz

- Schraubenkopf-Durchmesser/-Höhe, Gewinde, Länge, Bauteildicke und verbleibender Gewindeeingriff.
- Rechtwinklige Bestätigung der 10-/37-/40-mm-Enddatums und explizite lokale X/Y-Zuordnung der 37-mm-Messung.
- Ergänzende Messwerte oder ein Konturcoupon für den freien Bauraum unmittelbar um die Schraubenebene.
- Vollständiger stromloser X/Y/Z-Bewegungsraum von Bett, Kopf, Kabeln, Wiper und geplanter Zusatzkontur.
- Gewogene bewegte Baugruppe und 100 Fangkopf-Entnahmezyklen mit Rastprüfung.
- Je mindestens drei beaufsichtigte Purge-Zyklen bei niedriger, mittlerer und hoher Z-Position; Landepunkte und Randreserve des stationären Behälters werden markiert.

Diese Analyse ist eine technische Clean-Room-Dokumentation, keine rechtliche Freigabe und keine Aussage zur Schutzfähigkeit oder Patentfreiheit.
