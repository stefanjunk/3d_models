# R7-C01 – Messcoupon für die Wiper-Schraubenschnittstelle

Dies ist **kein Purge-Umlenker**, sondern der freigegebene nächste
Datenerfassungsschritt. Der Coupon verwendet ausschließlich den am eigenen
Drucker gemessenen Schraubenmittenabstand von 17 mm. Es wurden weder Geometrie
noch Maße aus einer Drittanbieterdatei übernommen.

## Enthaltene Lehren

- elf einzelne Laschen mit jeweils zwei **geschlossenen Rundlöchern** im
  Abstand 17 mm; Lochdurchmesser 2,8 bis 4,8 mm in 0,2-mm-Schritten,
- offene Kopfbreitenlehre 4,5 bis 9,5 mm in 0,5-mm-Schritten,
- gedruckte 0–30-mm-Grobskala für einen Plausibilitätscheck der Schraubenlänge.

Die Durchmesser sind ein Messbereich und keine Annahme über M3, M4 oder einen
anderen Schraubenstandard. Alle Laschen sind 1,2 mm dick. Das Vollteil bleibt
gesperrt, bis Schaft/Gewinde, Kopf, Schraubenlänge, Auflagestapel und
Gewindeeingriff protokolliert und eine 17-mm-Lasche am stromlosen Drucker ohne
Zwang passend bestätigt wurde.

Die Laschen sind geometrisch codiert: 1 bis 11 kleine Kennbohrungen entsprechen
von links nach rechts Ø 2,8; 3,0; 3,2; 3,4; 3,6; 3,8; 4,0; 4,2; 4,4; 4,6
und 4,8 mm. Die Kopfkerben steigen von links nach rechts von 4,5 bis 9,5 mm.
Die beschriftete PNG-Übersicht bleibt beim Prüfen am besten geöffnet.

## Druckdateien

- `build/run-001/models/3mf/DRAFT-R7-C01-interface-measurement-coupon.3mf` –
  Anycubic-Projekt mit eingebettetem vorläufigem Kobra-3-Max-/PETG-Profil,
- `build/run-001/models/3mf/DRAFT-R7-C01-interface-measurement-coupon-core.3mf` –
  neutraler, standardkonformer Core-3MF-Export ohne Slicerprofile,
- `build/run-001/models/stl/DRAFT-R7-C01-interface-measurement-coupon.stl` –
  neutrales Fertigungsmesh,
- `build/run-001/models/step/DRAFT-R7-C01-interface-measurement-coupon.step` –
  exakte editierbare Übergabe,
- `build/run-001/previews/DRAFT-R7-C01-interface-measurement-coupon.png` –
  beschriftete Übersicht.

Vor dem Drucken im Anycubic-Projekt das tatsächlich eingelegte Filament
auswählen und die erste Schicht visuell prüfen. Der hinterlegte PETG-Datensatz
ist nur ein reproduzierbarer Slicer-Preflight, kein Nachweis der real
eingelegten Rolle.

## Sicherer Kaltpass-Test

1. Drucker vollständig ausschalten, Netzstecker ziehen und alle heißen Teile
   abkühlen lassen. Ursprünglichen Schrauben-/Wiper-Aufbau fotografieren und
   abstützen.
2. Zuerst nur **eine** Schraube lösen. Prüfen, ob sie weitere Wiper-Teile hält,
   und Schaft/Gewinde-Ø, Kopf-Ø, Kopfhöhe und Länge unter Kopf mit einem
   Messschieber erfassen. Die gedruckten Lehren dienen nur als funktionaler
   Quercheck.
3. Die einzelne Schraube nacheinander durch die Rundlöcher führen. Die kleinste
   Lasche notieren, durch die sie ohne Kraft und ohne Nacharbeit frei gleitet.
4. Nur wenn der Wiper sicher gehalten und die ursprüngliche Lage eindeutig ist,
   beide Schrauben für den kurzen Lochbildtest lösen. Die ausgewählte
   17-mm-Lasche muss plan anliegen; beide Schrauben müssen zwangfrei ansetzen,
   ohne Wiper oder Lasche zu biegen.
5. Einschraubtiefe beziehungsweise volle Umdrehungen bis zur Auflage im
   Originalzustand und mit 1,2-mm-Lasche vergleichen. Bei unbekanntem oder
   offensichtlich reduziertem Gewindeeingriff nicht festziehen und keine
   längere Ersatzschraube raten.
6. Coupon wieder entfernen, Originalzustand herstellen und Wiper-Ausrichtung
   prüfen. **Der Drucker darf mit montiertem Coupon weder eingeschaltet noch
   verfahren werden.**

Ergebnisse in `PHYSICAL-RESULTS-DE.md` eintragen. Erst danach wird die
Schraubenzone des bodenlosen Umlenkers parametrisch festgelegt.
