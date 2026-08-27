# Passungs- und Testplan

## Status

Alle Möbelkontakte in `config/defaults.json` sind `PROVISIONAL_UNVERIFIED`. Die digitalen Modelle dürfen deshalb nicht als garantiert passend oder belastbar angeboten werden.

## Schnittstellenvertrag je Möbelrevision

Mindestens dokumentieren:

- System, Artikelnummer, Land, Kaufdatum und erkennbare Revision
- lokales Koordinatensystem und Montage-/Entnahmerichtung
- Innenmaß, Materialstärke, Loch-/Draht-/Pfostenprofil und Messunsicherheit
- Funktionsspiel, Prozesskompensation und Montagezugabe jeweils separat
- Bewegungs- und Kollisionsräume von Tür, Auszug, Korb und Wandbefestigung
- zulässige Gegenstände und bewusst ausgeschlossene Lastfälle

## Couponfolge

1. **Maßcoupon:** Außenmaß oder Innenmaß mit 0,20/0,35/0,50 mm Spiel je Seite.
2. **Clipcoupon:** nur 30-50 mm der tatsächlichen Clip-/Pfostenschnittstelle.
3. **Oberflächencoupon:** reale Kontaktfläche mit TPU-Pad oder PETG auf Möbeloberfläche, 72 Stunden geklemmt.
4. **Lastcoupon:** gleiche Layerorientierung und Clipwurzel wie im Modell, zunächst mit ungefährlichem Prüfgewicht nahe dem Boden.
5. **Vollprototyp:** erst nach bestandenem Maß- und Clipcoupon.

## Produktgruppen

- **Schubladen/Trays 1, 2, 3, 12, 13:** Schließweg, Bodenfreiheit, Entnahme und Punktlast prüfen.
- **Regalraster 4, 6, 7, 14, 16, 18:** Kippen, Verzug, lange Brücken und Divider-Wurzel prüfen.
- **Lochwand/Rail 5, 8, 11, 17:** Clipvorspannung, Werkzeugentnahme und 100 Lastzyklen prüfen.
- **Draht-/Korbteile 10, 15:** Beschichtungsschutz, Drahtdurchmesser und Verrutschen prüfen.
- **Medien 9, 12:** Lüftungsraum und Temperatur im ungünstigsten Betrieb prüfen; keine Netzteile umschließen.
- **Klemmen 19, 20:** Möbelmarkierung, Kriechen, Klemmkraft und Kippverhalten prüfen.

## Abbruchkriterien

- sichtbare Möbelmarkierung, Riss oder bleibende Clipverformung
- Montage erfordert übermäßige Kraft oder Werkzeug
- Teil beeinflusst Anti-Kipp-Hardware, Wandmontage, Schubladenstopp oder Scharnier
- scharfe Kante, ungesicherte Spitze oder Gegenstand über Personen
- Temperaturverformung oder blockierte Gerätebelüftung
- Modell kann im Slicer nicht ohne unzugängliche Supports erzeugt werden
