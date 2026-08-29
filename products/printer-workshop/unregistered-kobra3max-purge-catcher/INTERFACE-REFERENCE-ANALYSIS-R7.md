# R7 – lizenzgetrennte Analyse der Montage- und Aufstellprinzipien

Stand: 2026-08-29
Status: Anforderungen/Ideation, keine CAD-Ableitung

## Ausgangslage

Der R6-Fangkopf erfüllt die gewünschte kurze Fangstrecke grundsätzlich, sein physisches System ist aber ungünstig: Ein unsicheres Wiper-Schraubenpaar trägt einen separaten Adapter, der Fangkopf muss von oben in eine reibschlüssige Schwalbenschwanzführung gesetzt werden, und der Unterbehälter steht als zweites, unabhängig auszurichtendes Objekt darunter. Die reale Passung und alle Kollisions- und Purge-Tests sind weiterhin offen.

## Rechte- und Nutzungspolitik

Die Dateien unter `research/third-party/printer-workshop/` bleiben reine Betrachtungsquellen. Es wird kein Mesh importiert, kein Profil nachgezeichnet, kein Maß übernommen, kein Bild ausgeliefert und kein Fremdmodell in einem R7-Export eingebettet. Selbst Dateien mit Metadaten werden nicht als Rechtefreigabe für kommerzielle Ableitungen verstanden.

| Lokale Datei | SHA-256 | Lokale Rechteinformation | Nur abstrahiertes Prinzip | Aus R7 ausgeschlossen |
|---|---|---|---|---|
| `Anycubic_Kobra_3_Max_Poop_catcher.3mf` und identische `(1)`-Kopie | `ba353bf0d44328b406599fe770307c4221e9f29cc2d04447abcf688eba4df35d` | eingebettet: Designer `Meisech`, `BY-NC` | Eine Fangzone nahe am Wiper reduziert den freien Flugweg. | Gehäuse, Schublade, Schraub-/Schlitzkontur, Lochbild, Perforation und alle Maße |
| `Poop+catcher+LBI3D.3mf` | `b431af0b8a3761aea82b5efc26330c35c6d6220c04a78e5ff3896f4b7d5aebcb` | eingebettet: `Standard Digital File License`; zusätzlich Verweis auf das BY-NC-Ursprungsmodell | Lokales Umlenken und entfernte Speicherkapazität sind zwei getrennte Funktionen. | sämtliche Remix-Geometrie, Kontakt-/Clipkonturen, Ausschnitte, Maße und Bilder |
| `Poopbin.3mf` | `b486e11cb3d1f25b52b150054153bad166f38108ee5658e5382aea66d037ef6f` | eingebettet: Designer `MrBaham`, `BY-NC-SA` | Eine große Standfläche kann die Maschine von Behälterlasten entkoppeln. | Behältersilhouette, hohe Rückwand, Seitenprofil, Radien, Maße und Bildmaterial |
| `poubelle+anycubic.3mf` | `a81e341d829760ccb0b1512e27e858d7510ed49a6ecfbfaef723a5d316bea6a7` | eingebettet: `MakerWorld Exclusive License`, als Remix mit BY-NC-SA-Verweis | Ein frei aufgestellter Behälter ist wartungsarm, braucht aber eine reproduzierbare Positionierung. | gesamte Remix-/Ursprungsgeometrie, Logo, Kontur und Maße |
| `poop-catcher.stl` | `85f011f784d0ae31484c3da0c564553c721d38be1b94724cc8420e94e6a4f399` | keine Lizenzmetadaten im STL; Rechte daher unbekannt | kein zusätzliches Prinzip erforderlich | vollständige Datei und jede geometrische Ableitung |
| `PURGE DIVERTER 2.STEP` | `7adbdf50de61c18f3e36f3ff52522d14573cfd10b23ad1666c58c88e641779c4` | keine verlässliche lokale Lizenz-/Urheberangabe | Eine offene Fallstrecke kann Fangfunktion und Speicherfunktion entkoppeln. | B-Rep, Flansch, Bohrungen, Rippen, Öffnungsform, Maße und Topologie |
| `ptfe_release.3mf` | `3b64f2b149dec0c15896c870fefed7f46c3a2c56952d87f0c1460c26e1eb7984` | keine Rechteangabe | für den Purge-Catcher nicht relevant | vollständig ausgeschlossen |

## Abstrahierte Lösungsräume

1. **Direkt verschraubter Hängebehälter:** kompakt und eindeutig positioniert, belastet aber Wiper-Hardware und macht Schraubenlänge, Gewindeeingriff und Wartung kritisch.
2. **Aufgeschnappter Kurz-Umlenker:** sehr wenig Masse nahe am Auswurf, benötigt jedoch ein präzises, noch unbekanntes Gehäuseprofil und kann durch Wärme, Kriechen oder Montagekräfte ausfallen.
3. **Lose freistehende Großbox:** keine Maschinenlast und einfache Reinigung, aber keine gemeinsame Datumskette zwischen Auswurf, Fangzone und Behälter.
4. **Zweistufiges System:** kleine Fangzone plus separate Speicherkapazität ist funktional sinnvoll; beide Stufen müssen jedoch von einem gemeinsamen, eigenen Träger ausgerichtet werden.

## Eigenständige R7-Richtung

R7 kombiniert nur das abstrakte zweistufige Funktionsprinzip mit einer neu konstruierten Mechanik:

- Eine breite Dockbasis steht auf der Arbeitsfläche und trägt alle Zubehörlasten.
- Eine schlanke, verrippte Rückensäule positioniert den weitgehend erhaltenen R6-Fangkopf.
- Drei austauschbare weiche Anschläge berühren ausschließlich stationäre Chassisflächen und stellen die Position wieder her, ohne zu klemmen.
- Ein eigener Innenbehälter fährt horizontal in das Dock und erhält eine formschlüssige Endlage unter der offenen Fallstrecke.
- Eine einmalige X/Z-Justage sitzt zwischen Mast und Fangkopf, nicht am Wiper.

Damit entfallen das Wiper-Schraubinterface, der vertikale R6-Schwalbenschwanz und die unabhängige Ausrichtung des Unterbehälters. Die konkrete Geometrie wird erst nach Anforderungs- und Konzeptfreigabe erzeugt.

## Noch benötigte reale Evidenz

- Foto mit Maßstab oder Messwerte für Tischfläche, Wiperhöhe und erreichbare stationäre Chassisflächen.
- Vollständiger stromloser Bewegungsraum von Bett, Kopf, Kabeln und Wiper.
- Verfügbarer Auszugsweg zum Entleeren des Innenbehälters.
- Fünf Neuaufstellungen mit Registrierungslehre, Stabilitätstest und mindestens drei beaufsichtigte Purge-Zyklen.

Diese Analyse ist eine technische Clean-Room-Dokumentation, keine rechtliche Freigabe und keine Aussage zur Schutzfähigkeit oder Patentfreiheit.
