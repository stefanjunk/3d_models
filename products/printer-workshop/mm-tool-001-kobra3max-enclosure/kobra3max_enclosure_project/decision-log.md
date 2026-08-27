# Entscheidungsprotokoll – kameraoptimiertes Kobra-3-Max-Gehäuse

## 2026-08-25 – Anforderungsentwurf 1.1

- Der vorhandene Entwurf wurde als Basis beibehalten: 900 × 1050 × 900 mm außen, 860 × 1010 × 860 mm frei innen.
- Der bisherige Boden entfällt. Ein umlaufender unterer Rahmen bleibt als Versteifung und Aufsetzrand erforderlich.
- Für den Innenraum wird eine glatte, matte, neutralweiße Fläche als fotografisch wirksamere Basis empfohlen als durchgehend transluzentes Milchglas.
- Die tragenden Eck- und Randprofile werden nach außen verlegt. Innen sollen nur weiße, bündige oder weich ausgeführte Fugen sichtbar sein.
- Echtes Glas wird für die überstülpbare Haube wegen Masse, Bruchrisiko und Handhabung nicht empfohlen.
- Vollflächige LED-Wände bleiben eine optionale Versuchsstufe. Baseline ist ein außenliegendes diffuses Lichtdach mit getrennt dimmbaren Fülllichtern, weil es weniger Wärme und elektrische Komplexität erzeugt und die Form des Druckobjekts besser erkennen lässt.
- Die Kamera soll nicht an der Tür hängen. Empfohlen ist eine feste, schmale Kamera-/Servicesäule auf der Displayseite; Kameraelektronik möglichst außerhalb des warmen Innenraums.
- Produktionsgeometrie bleibt gesperrt, bis Kamera/FOV, Plattenmaterial und thermische Nutzung bestätigt und die Anforderungsversion ausdrücklich freigegeben sind.

## 2026-08-25 – Antworten und Anforderungsentwurf 1.2

- Hauptmotiv der Kamera ist das Druckobjekt; der vollständige Drucker ist nur Kontext. Dafür wird eine höhenverstellbare Kameraposition auf der festen Displayseite vorgesehen.
- Es sind noch keine Platten gekauft. Die günstige Baseline verwendet einseitig weiß beschichtete Hartfaser-/HDF-Platten für Seiten und Rückwand, klares PMMA für die Tür und opales PMMA beziehungsweise Polycarbonat nur als Dachdiffusor.
- Der Rahmen bleibt aus günstigen Holzleisten; Scharnierseite, Handgriffe und unterer Ring werden lokal verstärkt.
- Eine klare, links angeschlagene Tür und die regelbare Abluft sind bestätigt.
- Eine Zusatzheizung ist in Revision 1.2 ausdrücklich nicht enthalten. Eine spätere Nachrüstung erfordert eine neue thermische, elektrische und brandschutzbezogene Prüfung.
- Als Kamera wird bis zu einer Korrektur die bereits vorhandene Anycubic-Kamera mit dem vorhandenen 2 × 150-mm-Gelenkarm angenommen.

## 2026-08-25 – Anforderungsfreigabe

- Der Nutzer hat Anforderungsversion 1.2 ausdrücklich freigegeben.
- Die Konzeptphase ist geöffnet; Produktions-CAD und Fertigungsexporte bleiben bis zur Konzeptfreigabe gesperrt.

## 2026-08-25 – Konzepttafel v1

- Eine Konzepttafel mit Dreiviertelansicht und Explosions-/Schnittdarstellung wurde für Anforderungsversion 1.2 erzeugt.
- Sichtbar sind die bodenlose Haube, der untere Versteifungsring, außenliegender Holzrahmen, matte weiße Innenhaut, klare links angeschlagene Tür, feste Kameraposition auf der Displayseite, diffuses Lichtdach, Fülllichter, seitlich versetzte Abluft und Außengriffe.
- Die dargestellte Kameraform und kleinere Beschläge sind schematisch und nicht maßhaltig. Produktionsgeometrie wird daraus nicht abgeleitet; dafür gelten `design-spec.yaml`, vorhandene Kamera-Maße und spätere CAD-Prüfungen.
- Konzeptstatus bleibt bis zur ausdrücklichen Nutzerfreigabe `pending`.

## 2026-08-25 – Konzeptfreigabe

- Der Nutzer hat Konzepttafel v1 für Anforderungsversion 1.2 ausdrücklich freigegeben.
- Produktions-CAD, aktualisierte Zuschnittliste und DRAFT-Fertigungsexporte sind damit freigegeben.

## 2026-08-25 – Produktionsstand DRAFT

- Der alte Schienen-/Bodenaufbau bleibt unter `baseline_v1/` unverändert erhalten.
- Neu modelliert wurden Kameraschlitten für eine 2020-Schiene, Kameragabel-Testcoupon, Dachkassetten-Lokator und weiße Lüfter-Sichtblende.
- Metallband, Metallgriffe, 2020-Profil, LED-Wärmeverteiler und Verschraubungen bleiben Kaufteile.
- Alle 14 verwendeten STL-Dateien bestehen den deterministischen DRAFT-Meshaudit.
- Rechnerische Mindestabstände bestehen; die Tiefenreserve von 33,5 mm je Seite bei idealer Zentrierung erfordert zwingend die reale Bettkabelmessung.
- Gegenüber der alten dokumentierten Stückzahl sinken gedruckte Instanzen um 59,6 % und das CAD-Festvolumen um 40,4 %.
- Mesh-Vereinfachung ist bei maximal 5408 Dreiecken pro Datei nicht vorteilhaft.
- Release bleibt wegen fehlendem exaktem Slicer, physischer Tests und Kennzeichnung blockiert.

## 2026-08-26 – Kamera-Subsystem erneut geöffnet

- Der Nutzer fordert, die Original-Anycubic-Kamera nach den von Anycubic vorgegebenen Maßen einzupassen und Kameraaufnahme sowie Kugelgelenk innerhalb dieses Projekts neu zu konstruieren.
- Die drei im Produkt vendorten Dateien `products/printer-workshop/mm-tool-001-kobra3max-enclosure/vendor/camera-mount-reference/external/1.stl`, `2.stl` und `3.stl` wurden per SHA-256 mit dem von der offiziellen Anycubic-Kameraseite verlinkten Google-Drive-Ordner abgeglichen; alle drei stimmen bytegenau überein.
- Die Hüllgröße 40,71 × 23,42 × 18,63 mm des älteren v6-Kameraprojekts stammt nicht aus diesem offiziellen Dateisatz, sondern aus einem getrennten Archiv ohne belegte Lizenz. Sie ist als Anycubic-Vorgabe verworfen.
- Offizielle Referenz-STLs werden ausschließlich intern vermessen. Sie werden weder importiert noch verändert, kombiniert oder ausgeliefert.
- Die neue Konstruktion umfasst ein eigenständiges zweiteiliges Kameragehäuse, eine eigenständige 11-mm-Kugel, eine passende Gegenpfanne, einen kurzen Adapter zum vorhandenen 2020-Schlitten und sparsame Passcoupons.
- Der Enclosure-Entwurf außerhalb des Kamera-Subsystems bleibt unverändert. Die Kameraänderung erhöht die Anforderungsversion auf 1.3; Produktions-CAD für die Kamera bleibt bis zur erneuten Anforderungs- und Konzeptfreigabe gesperrt.

## 2026-08-26 – Kamera-Anforderungsfreigabe 1.3

- Der Nutzer hat die Kamera-Anforderungen 1.3 ausdrücklich freigegeben.
- Die lizenzgetrennte Maßkette, der vollständige Neuaufbau von Gehäuse und Kugelgelenk sowie die vorgeschriebenen Fit-Coupons sind damit bestätigt.
- Die Kamera-Konzeptphase ist geöffnet. Produktions-CAD und Fertigungsexporte des Kamera-Subsystems bleiben bis zur Konzeptfreigabe gesperrt.

## 2026-08-26 – Kamera-Konzepttafel v1

- Die maßbezogene Kamera-Konzepttafel wurde aus Anforderung 1.3 erstellt.
- Dargestellt sind die außenliegende 2020-Höhenschiene, der kurze M4-Hingeadapter, das neue 11-mm-Kugelgelenk, das neu aufzubauende zweiteilige Kameragehäuse, eine leicht geneigte Sichtscheibe mit matter weißer Innenblende und das diagonale Sichtfeld zum Druckobjekt.
- Die Kameraelektronik bleibt außerhalb des warmen Innenraums. Die eingebauten Kamera-LEDs bleiben aus; Dach- und Fülllicht übernehmen die Beleuchtung, um Scheibenreflexionen zu vermeiden.
- Die Tafel enthält die verifizierten Funktionsmaße, ist aber ausdrücklich kein Fertigungsmodell. Produktions-CAD bleibt bis zur ausdrücklichen Konzeptfreigabe gesperrt.

## 2026-08-26 – Kamera-Konzeptfreigabe und Gesamtgehäuseauftrag

- Der Nutzer hat Kamera-Konzept v1 ausdrücklich freigegeben.
- Zusätzlich soll das vollständige Gehäuse in derselben Produktionsphase erstellt werden.
- Die freigegebenen Gehäuseanforderungen aus Revision 1.2 und die Kameraergänzung 1.3 bilden gemeinsam den Produktionsvertrag: bodenlose Haube, außenliegender Rahmen, matte weiße Innenflächen, klare Tür, Lichtdach, Abluftblende, feste Servicesäule und außenliegende Kameraaufnahme.
- Produktions-CAD, DRAFT-Fertigungsexporte, vollständige Baugruppe, BOM/Zuschnitt und digitale Validierung sind damit geöffnet. Physische Pass-, Sichtfeld-, Temperatur- und Belastungstests sowie finale Releasefreigabe bleiben gesperrt.

## 2026-08-26 – Vollständige DRAFT-Implementierung 1.3

- `kobra3max_enclosure_complete.scad` bildet Rahmen, bodenlose Innenhaut, klare Tür, festes weißes Servicefeld, 7°-Kamerafenster, Lichtkassette, Fülllichter, außenliegende Kamera, Abluft und Drucker-Planungsraum als Gesamtbaugruppe ab.
- Das feste Frontfeld ist nicht länger durchsichtig: 3-mm-weißbeschichtete Hartfaserplatte erhält nur ein 72 × 82 mm großes optisches Fenster mit 80 × 90 × 2 mm Klarpaneel.
- Das neue Kameragehäuse verwendet ausschließlich die dokumentierten Anycubic-Schnittstellenmaße. Die Quelle enthält keinen Mesh-Import; die verifizierten Referenz-STLs werden nicht ausgeliefert.
- Neu sind Frontschale, ventilierter Rückdeckel mit 11-mm-Kugel, kurzer Socket-Arm, Passring, Kugelstift, Dreifach-Socket-Coupon, Fensterkeil, Innenblende und Klemmrahmen.
- Der komplette Build erzeugt 24 eindeutige DRAFT-STLs. Alle bestehen den Meshvertrag: wasserdicht, genau eine Komponente, positives Volumen, innerhalb Bauraum und Budgets.
- Der aggregierte DRAFT-Gate-Stand lautet 56 PASS, sechs REVIEW_REQUIRED und ein NOT_RUN. Slicer- und physische Gates blockieren weiterhin Release und finale Kennzeichnung.
