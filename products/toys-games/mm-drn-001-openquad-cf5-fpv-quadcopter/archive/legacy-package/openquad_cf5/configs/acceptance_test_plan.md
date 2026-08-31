# OpenQuad CF5 - Gate-basierter Abnahmeplan

Ein numerischer CAD-Check ist **keine** Flugfreigabe. Vor Tests an einem
flugfaehigen Aufbau muss eine qualifizierte Person Lastpfade, Befestigung,
Propulsion, Elektrik, Steuerung und den konkreten Testort pruefen. Die Propeller
bleiben bis Gate 6 abgenommen.

## Gate 0 - Dokumente und Rueckverfolgbarkeit

- [ ] Komponenten, Firmwaretargets, Versionen, Serien-/Chargenangaben notiert
- [ ] LiPo, Motor, ESC, FC und Funkdatenblaetter gelesen
- [ ] Einsatz in EASA Open A3 bzw. andere Genehmigung geklaert
- [ ] Versicherung, Betreiberregistrierung, Kompetenznachweis und DIPUL-Zonen
      fuer Deutschland geprueft
- [ ] Abbruchkriterien und verantwortliche Testleitung festgelegt

## Gate 1 - Material- und Passcoupons

- [ ] Filamentcharge getrocknet und dokumentiert
- [ ] Kanalcoupon passt zum tatsaechlichen 10x10-mm-Rohr ohne Aufspreizen
- [ ] Drei identische Coupons gedruckt; Masse und Masse protokolliert
- [ ] Sichtpruefung ohne Layertrennung, Unterextrusion oder feuchtebedingte Poren
- [ ] Klemmdrehmoment schrittweise an Coupons ermittelt; Schlupf und erste
      Schaedigungsanzeige dokumentiert

Freigabe: reproduzierbarer Sitz und dokumentiertes Montagefenster. Bei weissem
Bruch, Knacken, bleibender Verformung oder Rohrabdruck: Konstruktion/Prozess
aendern, nicht staerker anziehen.

## Gate 2 - Mechanischer Rahmen ohne Elektronik

- [ ] Vier Arme 103,0 mm, Motorzentren 115,0 mm, Diagonale 230,0 mm
- [ ] Gegenueberliegende Motorzentren innerhalb 1,0 mm; Rahmen liegt verwindungsfrei
- [ ] Jede Motoraufnahme widersteht manuell gemessenem Torsionsmoment ohne Schlupf
- [ ] Qualifizierter Reviewer legt einen schrittweisen Proof-Load fest. Die im
      Rechenblatt verwendeten 15 N sind nur ein Rohr-Screening, keine Pruefvorgabe.
- [ ] Nach Proof-Load keine Risse, Lockerung, bleibende Setzung oder Armwanderung
- [ ] Gesamtmasse der gedruckten Teile liegt im Slicer-/Waagebudget; Schwerpunkt
      mit Akku nahe Rahmenzentrum

## Gate 3 - Elektrik ohne FC-Aktivierung

- [ ] Jede Loetstelle visuell und mit Durchgangs-/Kurzschlussmessung geprueft
- [ ] Akku- und Kondensatorpolaritaet zweimal unabhaengig bestaetigt
- [ ] Motorphasen ohne Kontakt zu Carbon, Schrauben oder scharfen Kanten
- [ ] Erster LiPo-Anschluss nur ueber elektronischen Smoke Stopper
- [ ] Kein ungewoehnlicher Strom, Geruch, Rauch oder heisses Bauteil

## Gate 4 - FC/Funk, weiterhin ohne Propeller

- [ ] Richtige Boardbewegung im Configurator; QUADX und FRONT-Markierung konsistent
- [ ] Motor-Wizard: Position und Drehrichtung aller vier Motoren korrekt
- [ ] Empfaenger: Kanalrichtung/-weg, Arming und Linkwarnungen korrekt
- [ ] Echte RX-Unterbrechung loest den geplanten Failsafe aus
- [ ] Runaway-Takeoff-Prevention aktiv; Arming-Flags verstanden
- [ ] Blackbox zeichnet Gyro, Motor und RPM/ESC-Telemetrie fehlerfrei auf
- [ ] 30-60 s niedrige/wechselnde Drehzahl ohne Propeller: keine lose Leitung,
      ungewoehnliche Vibration oder Ueberhitzung

## Gate 5 - Propulsion am gesicherten Pruefstand

Nur mit fachkundiger Aufsicht, Schutzabstand und geeigneter Einhausung. Keine
Person in Propellerebene.

- [ ] Exakte Motor/Prop/Akku-Kombination fuer Strom, Schub und Temperatur messen
- [ ] ESC-Marge gegen gemessenen, nicht beworbenen Strom bewerten
- [ ] Props dynamisch unauffaellig; keine beschaedigten Naben/Blaetter
- [ ] Nach Test Motorplatten, Schrauben und Armklemmung erneut markieren/pruefen

## Gate 6 - Erstschweben

- [ ] Rechtlich geeigneter, freier A3-Ort; Pilot, Beobachter und Abbruchzone fest
- [ ] Wind schwach, Akku voll/balanciert, Props neu, Schraubenmarken unveraendert
- [ ] Erstes Abheben nur 0,5-1 m, 10-20 s, kein Acro-Manoever
- [ ] Sofort landen bei Oszillation, Drift, heissem Motor, ungewoehnlichem Klang,
      Telemetriewarnung oder sichtbarer Strukturbewegung
- [ ] Danach vollstaendige Hand-/Sichtpruefung und Blackbox-Auswertung

## Gate 7 - Erweiterung

Erst nach mehreren fehlerfreien Basisfluegen: Output-Limit schrittweise anheben,
GPS montieren, GPS Rescue separat testen und FPV-System integrieren. Jede
Massen-/Steifigkeitsaenderung setzt relevante Gates zurueck.

## Mindest-Protokoll pro Flug

Datum/Ort, Wetter, Startmasse, Akku-ID, Props, Firmware/Config-Hash, Schrauben-
marken, Maximalstrom, verbrauchte mAh, Motor-/ESC-Temperatur, Auffaelligkeiten,
Blackbox-Dateiname und Freigabeentscheidung dokumentieren.
