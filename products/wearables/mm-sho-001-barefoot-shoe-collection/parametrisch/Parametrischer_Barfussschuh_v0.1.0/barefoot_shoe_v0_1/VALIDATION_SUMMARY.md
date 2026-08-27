# Digitale Validierungszusammenfassung – Revision 0.1.0

## Standardmodell

| Prüfkörper | Dreiecke | Komponenten | offene Kanten | nicht-manifold Kanten | degenerierte Dreiecke | geschlossen |
|---|---:|---:|---:|---:|---:|---|
| linke Sohle | 25.320 | 1 | 0 | 0 | 0 | ja |
| linker TPU-Netzoberschuh | 42.052 | 1 | 0 | 0 | 0 | ja |
| rechte Sohle | 25.320 | 1 | 0 | 0 | 0 | ja |
| rechter TPU-Netzoberschuh | 42.052 | 1 | 0 | 0 | 0 | ja |
| jede der 16 Ösen | 192 | 1 | 0 | 0 | 0 | ja |
| Netzcoupon | 2.676 | 1 | 0 | 0 | 0 | ja |
| Ösencoupon | 256 | 1 | 0 | 0 | 0 | ja |

## Abmessung, Volumen und Baufläche

- Sohlenlänge: 277,0 mm.
- maximale parametrische Konturbreite: 112,21 mm; 3D-Hüllbox inklusive Seitenwölbung: 118,42 mm.
- Sohlenvolumen: links 125,736 cm³, rechts 125,758 cm³.
- Voll-TPU-Geometrie inklusive Netz und Ösen: links 158,768 cm³, rechts 158,792 cm³.
- theoretische Vollmaterialmasse bei 1,20 g/cm³: etwa 151 g je Sohle bzw. 190 g je komplettem TPU-Schuh. Reale Slicermasse hängt von Extrusionsbreite, Skins, Infill und Filamentdichte ab.
- kleinste quadratische XY-Hüllkurve: ca. 227,83 mm bei 47° links beziehungsweise 43° rechts. Damit passt die Geometrie ohne Brim rechnerisch auf 250 × 250 mm, nicht auf 220 × 220 mm.

## Baugruppen-Überlappung

- 589 Netz-Vertices je Schuh liegen in der angenäherten Sohlenhülle; Mindestschwelle 100 bestanden.
- alle Ösen besitzen mindestens einen Netz-Vertex im Abstand 0,08–0,31 mm und zahlreiche Punkte innerhalb 1,5 mm; alle acht Überlappungs-Proxies je Seite bestanden.
- Diese Werte sind nur digitale Proxy-Prüfungen. Der Ziel-Slicer muss die vereinigten Schichtpfade weiterhin anzeigen.

## Formatprüfung

- 24 binäre STL-Dateien: Dateilänge entspricht jeweils exakt `84 + 50 × Dreieckzahl` Bytes.
- drei 3MF-Dateien als ZIP/XML geparst; beide Schuhe enthalten zehn Objekte und zehn Build-Items, der Coupon zwei und zwei.
- sechs SVG-Dateien als XML geparst; Maße sind in Millimetern hinterlegt.
- SHA-256 der vier mitgelieferten Originalbilder stimmt bytegenau mit den Anhängen überein.
- Parametertests für Fußlängen 230, 265 und 300 mm bestanden für beide Seiten; siehe `PARAMETRIC_RANGE_TESTS.md`.

## Noch nicht freigegeben

Kein kompatibler Ziel-Slicer und kein konkretes Drucker-/Filamentprofil wurden bereitgestellt. Deshalb sind noch offen:

- tatsächliche Druckzeit, Supportmasse, Retraktionen und Volumenstrom;
- endgültige Arachne-/Wandpfade in 3,2-mm-Gitterbändern;
- selbsttragendes Verhalten der gewölbten TPU-Netzschale;
- anatomische Passform, Druckstellen, Fersenhalt und Hautkomfort;
- Abrieb, Nassgriff, Verklebung und Langzeitermüdung.

Diese Punkte sind bewusst als physische Gates im `VALIDATION_AND_TEST_PLAN.md` festgelegt.
