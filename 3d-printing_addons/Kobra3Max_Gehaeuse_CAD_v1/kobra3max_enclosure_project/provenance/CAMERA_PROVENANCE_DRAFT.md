# Kamera-Provenienzprüfung – DRAFT

Stand: 2026-08-26  
Geltungsbereich: Kameraaufnahme, Kameragehäuse, Kugelgelenk und Anschluss an den Enclosure-Kameraschlitten

## Ergebnis

Die Original-Anycubic-Kamera wird als gekauftes Elektronikmodul behandelt und nicht mit ausgeliefert. Für das Enclosure-Projekt werden Kameragehäuse, Rückdeckel, Kugel, Gegenpfanne und Testcoupons neu und parametrisch konstruiert.

Es werden keine Meshflächen, Dreiecke, Booleans oder Codeblöcke aus den vorhandenen Kamera-Downloads oder dem älteren Kugelgelenk-Projekt übernommen. Anycubic-Logos und eine vermeintliche Herstellerfreigabe werden nicht verwendet.

## Belegter Anycubic-Bezug

Die [offizielle Anycubic-Produktseite](https://store.anycubic.com/products/live-view-camera) für die Live-View-Kamera nennt die Kobra-3-Max-Kompatibilität und verlinkt den Google-Drive-Ordner [Camera bracket model](https://drive.google.com/drive/folders/1yRrAcQf_eVz00oxu5j5eHwzXfnZUSOrS). Dessen Dateien `1.stl`, `2.stl` und `3.stl` stimmen per SHA-256 exakt mit den gleichnamigen lokalen Dateien unter `camera_mount/external/` überein.

Anycubic fordert auf der Produktseite zum Herunterladen und Drucken des passenden Halters auf. Eine ausdrückliche Erlaubnis zur Änderung oder digitalen Weiterverteilung der Originaldateien wurde weder dort noch in den verlinkten Dateien gefunden; die separat abrufbaren [Store-Nutzungsbedingungen](https://store.anycubic.com/policies/terms-of-service) enthalten dafür ebenfalls keine konkrete Lizenz. Deshalb bleiben diese Dateien reine interne Messreferenzen und werden nicht in das Projekt kopiert oder ausgeliefert.

## Zulässige Messnutzung im Projekt

Aus der offiziellen Referenz werden nur für die Passung erforderliche Maße festgehalten:

- Gehäusefront ohne seitliche Befestigungsfortsätze: 22,50 × 38,50 mm
- vollständige Referenzhülle von `2.stl`: 22,50 × 43,50 × 25,00 mm
- freie Innenkontur im mittleren Tiefenbereich: 19,30 × 35,30 mm
- Linsenöffnung: Ø 14,30 mm; Mittelpunkt bei X = 0,00 mm und Y = +5,57 mm relativ zur Gehäusefrontmitte
- zwei LED-Öffnungen: je Ø 5,50 mm; Mittelpunkte bei X = ±3,00 mm und Y = −8,83 mm
- vollständige Referenzhülle des Rückdeckels `3.stl`: 22,36 × 38,36 × 13,60 mm

Diese Werte beschreiben Funktionsschnittstellen und Sperrräume. Konturen, Radien, Rastnasen, Oberflächen und die äußere Form werden eigenständig gestaltet. Vor dem vollständigen Gehäusedruck muss ein sparsamer Passrahmen an der realen Kamera getestet werden.

## Ausgeschlossene Quellen und Werte

Das Archiv `Anycubic+Kobra+3+Max+Camera+Mount.zip` enthält keine belegte Lizenz oder authentifizierte Herstellerquelle. Die im älteren v6-Projekt verwendete Hüllgröße 40,71 × 23,42 × 18,63 mm lässt sich auf dieses Archiv zurückführen und ist nicht Teil des verifizierten offiziellen Anycubic-Maßsatzes.

Das Thingiverse-Archiv `Kobra 3 Camera Mount - 6687921.zip` enthält einen Hinweis auf eine nichtkommerzielle Lizenz ohne Bearbeitungen. Es wird vollständig ausgeschlossen.

## Umgesetzte neue Konstruktion und Lizenzumfang

Die eigenständig geschriebene OpenSCAD-Konstruktion ist in `kobra3max_enclosure.scad` umgesetzt. Ihr aktueller SHA-256 lautet `a695742ae88b7ad581236153dfff5e1946b3d82c51bf29f658751ce4cc11ffc7`. Sie enthält:

- zweiteiligem Schutzgehäuse für das vorhandene Kameramodul,
- freiem Sichtfeld für Linse und LEDs,
- zugentlastetem Kabelausgang,
- neu modellierter 11-mm-Kugel am Rückdeckel,
- neu modellierter Gegenpfanne am kurzen Adapter zum bestehenden 2020-Kameraschlitten,
- Kamera-Passrahmen und dreistufigem Kugelpfannen-Toleranzcoupon.

Zusätzlich sind ein 7°-Fensterkeil, eine matte innere Fensterblende und ein äußerer Klemmrahmen enthalten. Die Quelle enthält keinen `import()`-Aufruf. Der maschinenlesbare DRAFT-Vertrag prüft dies explizit und alle elf Kamera-/Fenster-STLs bestehen die deklarierte Topologieprüfung.

Die Projektlizenz CC BY 4.0 kann nur für die neu erstellten Projektdateien gewährt werden. Sie erteilt keine Rechte an Anycubic-Marken, Elektronik, Referenzdateien, Patenten oder eingetragenen Designs. Eine eigenständige Neumodellierung reduziert das Lizenzrisiko, ist aber keine Garantie der Schutzrechtsfreiheit und keine Rechtsberatung.

## Gate-Stand und Sperren vor Freigabe

- aktualisierte Anforderungen: am 2026-08-26 freigegeben,
- Kamera-Konzept: am 2026-08-26 freigegeben,
- Quellen-/Abhängigkeitsprüfung ohne Meshimport: digital bestanden,
- Kamera-/Fenster-Meshprüfung: digital bestanden,
- reale Kamera mit Passrahmen prüfen,
- Kugelpfannen-Coupon drucken und auswählen,
- physische Halte- und Temperaturprüfung bestehen.
