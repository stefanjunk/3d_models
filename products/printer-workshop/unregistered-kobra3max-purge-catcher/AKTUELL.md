# Aktueller Status

Es gibt derzeit **keine passende oder zum Druck empfohlene Vollteilfassung**.
R7-DRAFT-2 wurde am 30. August 2026 durch die Benutzerkorrektur „die Modelle
werden nicht passen“ verworfen. Die Dateien bleiben ausschließlich als
negative Entwicklungs- und Validierungsevidenz erhalten.

## Aktuelle eigene Fassung

Aktuell ist ausschließlich die Anforderungsversion
`0.7.0-requirements.5`: ein einteiliger, bodenloser Umlenker mit zwei direkt
integrierten Schraublöchern für die vorhandenen Wiper-Schrauben. Er wird fest
verschraubt und besitzt weder Adapterplatte noch Clip, Schlitten, Rastung oder
Schnellverschluss. Offene Wabenwände und das mittige eigene metriMade-Logo
bleiben geschützt.

Hierzu existiert noch **keine freigegebene Modell- oder 3MF-Datei**. Die
Anforderungen und das bemaßte Konzeptblatt `R7-REQ5-DWG-001` sind durch Stefan
freigegeben:

- [`R7-REQ5-DWG-001-dimensioned-concept.png`](drawings/R7-REQ5-DWG-001-dimensioned-concept.png)
- [`R7-REQ5-DWG-001-dimensioned-concept.svg`](drawings/R7-REQ5-DWG-001-dimensioned-concept.svg)
- [`R7-REQ5-DWG-001-dimensioned-concept.pdf`](drawings/R7-REQ5-DWG-001-dimensioned-concept.pdf)

Der erste zulässige Messcoupon `R7-C01` ist nun als digital geprüfter
DRAFT-Druckkandidat vorhanden. Er enthält elf getrennte 17-mm-Rundlochlaschen
von Ø 2,8 bis 4,8 mm, eine Kopfbreitenlehre von 4,5 bis 9,5 mm und eine
0–30-mm-Grobskala. Die Durchmesserserie ist ein Messbereich und keine Annahme
eines Schraubenstandards.

- [Anycubic-3MF mit eingebettetem Kobra-3-Max-/PETG-Profil](current/r7-interface-measurement-coupon-c01/build/run-001/models/3mf/DRAFT-R7-C01-interface-measurement-coupon.3mf)
- [neutraler Core-3MF](current/r7-interface-measurement-coupon-c01/build/run-001/models/3mf/DRAFT-R7-C01-interface-measurement-coupon-core.3mf)
- [beschriftete Coupon-Übersicht](current/r7-interface-measurement-coupon-c01/build/run-001/previews/DRAFT-R7-C01-interface-measurement-coupon.png)
- [Druck- und Kaltpass-Anleitung](current/r7-interface-measurement-coupon-c01/README-DE.md)
- [auszufüllendes physisches Ergebnis](current/r7-interface-measurement-coupon-c01/PHYSICAL-RESULTS-DE.md)

Der Anycubic-Zielslicer-Rücktest besteht mit 6 Schichten, ohne Slicerwarnung
und ohne Upload oder Druckstart. Vor dem Drucken muss das tatsächlich eingelegte
Filament gewählt und die erste Schicht visuell geprüft werden. Der Coupon darf
nur am ausgeschalteten, abgekühlten Drucker montiert werden und muss vor jedem
Einschalten oder Verfahren wieder entfernt sein.

Für den vollständigen Umlenker existiert weiterhin **keine Fertigungs-3MF**.
Sein Produktions-CAD bleibt bis zum ausgefüllten Schraubenvertrag, bestandenen
Kaltpass-Coupon und der eigenen Maschinenhüllkurvenprüfung gesperrt.

## Passende Drittanbieter-Referenz

Die vom Benutzer am 31. August 2026 als passend bewertete Referenz ist:

[`Anycubic_Kobra_3_Max_Poop_catcher.3mf`](../../../research/third-party/printer-workshop/Anycubic_Kobra_3_Max_Poop_catcher.3mf)

Sie ist **nicht unsere aktuelle Modellversion**. Die Datei ist ein unverändertes
Drittanbieterprojekt von `Meisech` mit eingebetteter Lizenzangabe `BY-NC`. Ihre
direkte Zweischraubenmontage und die montierte Lage am Kobra 3 Max dienen nur
als qualitative Fit-Evidenz. Ausschließlich die unabhängig am eigenen Drucker
gemessenen 17 mm werden als Lochachsenabstand verwendet. Geometrie, Konturen,
Bilder, Projektmetadaten und Maße der Fremddatei dürfen nicht in das eigene
Modell übernommen werden. Der
vollständige Befund steht in
[`REFERENCE-FIT-AUDIT-ANYCUBIC-POOP-CATCHER.md`](REFERENCE-FIT-AUDIT-ANYCUBIC-POOP-CATCHER.md).

Die folgende Datei darf nur zur Analyse des Fehlers geöffnet werden:

[`ANYCUBIC-R7-INSPECTION-measured-assembly-reference.3mf`](current/anycubic-kobra3max-purge-catcher-r7/build/current/models/3mf/anycubic/ANYCUBIC-R7-INSPECTION-measured-assembly-reference.3mf)

**Nicht drucken.** Die 17/10/37/40-mm-Leisten stimmen als interne CAD-Bezüge,
aber die reale Maschinenhüllkurve fehlt. Der Fehlerbericht steht in
[`FIT-FAILURE-ANALYSIS-R7-DRAFT-2.md`](FIT-FAILURE-ANALYSIS-R7-DRAFT-2.md).
