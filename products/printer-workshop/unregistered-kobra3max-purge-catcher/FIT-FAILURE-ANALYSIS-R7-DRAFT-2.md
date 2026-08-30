# Fit-Fehleranalyse — R7-DRAFT-2

Status: **verworfen; nicht drucken oder montieren**

## Beobachtung

Der Benutzer bewertet die Maßgrafik `r7-measured-datums.png` als grundsätzlich
plausibel, stellt aber klar, dass die erzeugten Modelle nicht passen werden.
Eine konkrete Kollisionsstelle oder ein physischer Probedruck wurden in dieser
Korrektur noch nicht benannt.

## Digital nachweisbar

- Der Catcher belegt nominal `X=6..68`, `Y=2,4..46,4` und `Z=-36..26` mm.
- Die Datumplatte ist nominell 18 mm breit, 41 mm hoch und 2,4 mm dick; weitere
  Führungs- und Rastgeometrie ragt nach vorne.
- 17 mm steuern tatsächlich die beiden Schraubenmittelpunkte.
- 10 mm definieren nur `Z=-10` innerhalb der geschlossenen Fangzone
  `Z=-20..8`; an dieser Stelle existiert kein bestätigtes Maschinen-Gegenstück.
- 37 mm definieren die Mitte des 62 mm breiten Catchers. Dadurch werden ohne
  äußeren Hüllraumnachweis 31 mm auf jede Seite dieser interpretierten Mitte
  verteilt.
- 40 mm definieren lediglich eine Referenzebene bei `Y=-40`; sämtliche neue
  Geometrie wurde pauschal auf die andere Seite `Y>=0` gelegt.
- Alle Schrauben-, Slicer- und physischen Fit-Gates blieben `NOT_RUN`.

## Warum die vorherige Prüfung nicht genügt

Das CAD enthielt kein Modell und keinen vollständigen konservativen Keep-out
für Wiper-Schale, vorhandene Metallablage, Rollen, Kabel, Bett und Montageweg.
Eine Kollision konnte daher digital gar nicht erkannt werden. Nominale
Soll/Ist-Gleichheit innerhalb des Zubehörmodells ist nicht gleichbedeutend mit
Passung zur Maschine.

## Offene Ursachen – nicht auf Verdacht festlegen

1. Catcher liegt auf der falschen Seite oder ist gespiegelt/verdreht.
2. Catcher-Hüllkörper ist zu groß oder kollidiert mit vorhandener Ablage,
   Druckkopf, Rolle, Kabel oder Bett.
3. Datumplatte, Bohrungen, Schraubenköpfe oder Montageweg passen nicht.
4. Mehrere dieser Fehler treten gleichzeitig auf.

## Pflichtdaten vor einer neuen Revision

- eindeutige lokale Achsen und markierte Start-/Endpunkte der 10-/37-/40-mm-Maße;
- konkrete vom Benutzer erkannte Fehlpassung;
- Schraubengewinde, Kopf-Durchmesser/-Höhe, verfügbare Schraubenlänge,
  Auflagendicke und verbleibender Gewindeeingriff;
- freie X/Y/Z-Hüllkurve um Schrauben, Wiper, Metallablage, Rollen, Kabel und
  Bett inklusive Montageweg;
- zunächst eine flache Lochbild-/Umrisslehre, erst danach Catcher-CAD.

R7-DRAFT-2 bleibt als negative Evidenz erhalten. Aus diesem Bericht folgt noch
keine Ersatzgeometrie und keine allgemeine Regel für andere Drucker.
