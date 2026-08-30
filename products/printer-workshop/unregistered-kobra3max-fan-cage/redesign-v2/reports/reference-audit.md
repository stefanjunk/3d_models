# Referenz-, Maß- und Lizenzprüfung

Stand: 2026-08-30
Zweck: technische Messreferenz und kommerzielle Eingangskontrolle; keine Rechtsberatung und keine Freedom-to-operate-Aussage.

## Ergebnis

Der bisherige runde Fan-Cage ist nicht der richtige geometrische Grundtyp für einen vollständigen Printhead-Cover. Die belastbare Kobra-3-Referenz ist eine 61,2 × 81,0 × 15,8 mm große, gebogene Vollfront mit vier seitlichen Rastzungen. Die Referenzen sind jedoch für den **Kobra 3/Combo**; der Projekteigentümer hat den **Kobra 3 Max** ausdrücklich als Ziel bestätigt. Die Maße dürfen deshalb nicht ungeprüft als Max-Schnittstelle verwendet werden.

Für den kommerziellen Neuaufbau wird keine lokale Fremdgeometrie übernommen. Der ursprüngliche Kobra-3-Grundkörper ist als CC BY 4.0 identifiziert und bleibt Messreferenz mit Attribution. Alle Dateien mit unklarer Lizenz, Fremdmarken, Franchise-Motiven, Fremdschrift oder bezahltem Skulpturasset sind als Produktionsinput ausgeschlossen.

## Lokale Dateien

| Datei | SHA-256 | gemessene Hülle W × H × D | Aufbau / Inhalt | Lizenz- und Produktentscheidung |
|---|---|---:|---|---|
| `Bambuzle v2.stl` | `ad41d8155dd9d678a8d2029e4f771bd0c6b841914c0b3e4a947f8322b7689ac6` | 61,200 × 80,966 × 15,914 mm | Grundschale plus mehrere Logo-/Dekorkörper; Bambu-artige Bildmarke | Quelle und Lizenz unbekannt; Fremdmarke; **ausgeschlossen** |
| `Kobra 3 Face plate .stl` | `8e15da36cfe0eb77e88927127eacb9e6f4daa712d9a805b16d2a575e24d2efa1` | 59,950 × 83,239 × 11,066 mm | abweichende Vollschale mit Logoöffnung | Quelle/Lizenz unbekannt; Markenform; **ausgeschlossen** |
| `Kobra3Logo.3mf` | `0a5a22fbe4e62908bc2600d76fd2e3365bedec551aca1ec9b249f383878cb68d` | Grundkörper 61,200 × 81,000 × 15,800 mm | `printheadcoverspare.stl`, `King_Cobra_Head_AM09_FDM.stl`, Textkörper `KOBRA 3` mit „Glaser Stencil D“ | 3MF-Felder `License`, `Designer`, `Origin` leer; Cobra-Mesh als kostenpflichtiges Fremdasset identifiziert, kein Kauf-/Redistributionsnachweis; **BLOCK / ausgeschlossen** |
| `Printheadcover.stl` | `9a48e8571d1379835e88ef012a87492ae033ce23eb7c3762efb16aa04fbf0ca7` | 61,270 × 80,494 × 14,873 mm | Vollschale; ein wasserdichter Hauptkörper plus zwei degenerierte Dreieckreste | Quelle/Lizenz unbekannt; **ausgeschlossen** |
| `k3-printheadcover-mando-v2.3mf` | `41d3b597e7f8b54ca717b037bbe45fc6e3c1e89625b566db53576dc11a9cca18` | 61,200 × 81,000 × 15,975 mm | Grundschale plus Mandalorian-Motiv | Cults-Seite nennt joss27 und den MakerOnline-Grundkörper, zeigt aber keine Lizenz; Franchise-/Charakterrisiko; **BLOCK / ausgeschlossen** |

## Zurückverfolgter Grundkörper

- Titel: `Anycubic Kobra 3 printhead cover`
- Urheber/Upload: DuckDoCad
- Quelle: https://www.makeronline.com/en/model/Anycubic%20Kobra%203%20printhead%20cover/16100.html
- Ursprungsdatei: `printheadcoverspare.stl`
- Veröffentlichungsdatum laut Seitenmetadaten: 2024-06-29
- Lizenzcode der Seite: `1`; die aktuelle MakerOnline-Oberfläche ordnet `1` `CC BY` / Creative Commons Attribution 4.0 zu.
- Erlaubnisumfang: kommerzielle Nutzung und Bearbeitung sind unter CC BY 4.0 grundsätzlich möglich; Namensnennung, Lizenzlink und Änderungskennzeichnung sind erforderlich. Patent-, Marken- und Designrechte werden dadurch nicht pauschal erteilt.
- Projektverwendung: bemaßte Referenz und Aufbauvergleich. Keine Dreiecke oder Flächen werden in den metriMade-CAD-Master importiert. Attribution bleibt vorsorglich im späteren Drittanbieterhinweis.

## Maßprotokoll des CC-BY-Grundkörpers

Koordinaten: X = Breite, Z = Höhe, Y = Tiefe von Rückseite/Clipseite zur sichtbaren Front.

| Merkmal | Messwert | Bedeutung / Sicherheit |
|---|---:|---|
| Gesamthülle | 61,200 × 81,000 × 15,800 mm | hohe Mesh-Messsicherheit; nur Kobra 3/Combo |
| zentrale Schalendicke | 2,000 mm | Schnitt in der Symmetrieebene, Außenfläche Y=15,8 / Innenfläche Y=13,8 |
| zentrale Frontabflachung | 35,284 mm | X=12,958 bis 48,242 mm |
| Wölbung Seitenansatz → Frontzentrum | 10,800 mm | Y=5,0 bis 15,8 mm |
| mittlere Taillenbreite | 49,226 mm | X=5,987 bis 55,213 mm |
| projizierte Frontfläche | 4313,274 mm² | Diagnosewert, keine Material-/Strömungsfreigabe |
| Meshvolumen | 9218,875 mm³ | Diagnosewert des Referenzkörpers |
| Rastzungen | 4 | links/rechts in zwei Höhenbändern |
| unteres Rastband | Z=7,8 bis 14,0 mm | 6,2 mm hoch |
| oberes Rastband | Z=67,2 bis 73,4 mm | 6,2 mm hoch |
| rückwärtige Rastreichweite ab Seitenwurzel | 5,073 mm | Y=0 bis ca. 5,073 mm im normierten Querschnitt |
| Haken-Tiefenband | Y=0,9 bis 2,5 mm | Referenzgeometrie; physischer Coupon erforderlich |
| äußerer Cliprand | 0,6 mm vom Hüllrand | symmetrisch links/rechts |

Der grundsätzliche Aufbau ist damit: ca. 2 mm starke, seitlich umgebogene Vollfront; vier paarweise angeordnete seitliche Rastzungen; keine zentrale Lüfterring-Klemmung. Logo/Dekor sitzen auf oder in der sichtbaren Front und sind von der Maschinenschnittstelle getrennt.

## Warum diese Maße nicht für Kobra 3 Max freigegeben sind

Die Referenzseite, Dateinamen und das Kobra-3-Benutzerhandbuch beziehen sich auf Kobra 3. Anycubic führt Kobra 3/Kobra 3 V2 und Kobra 3 Max als unterschiedliche Druckkopfbaugruppen mit unterschiedlichen Gewichten und Verpackungsmaßen. Daraus wird vorsichtig abgeleitet, dass die Abdeckungs-Schnittstelle nicht ohne reale Prüfung gleichgesetzt werden darf.

Für Max werden mindestens benötigt:

1. größte Breite, Höhe und Tiefe der Originalabdeckung;
2. Front- und Rückseitenfoto möglichst orthogonal mit Lineal im selben Tiefenniveau;
3. Anzahl, Breite, Höhe, Tiefe und vertikale Lage aller Rastnasen;
4. Seitenprofil der Schalenwölbung;
5. Fan-, Hotend-, Kabel-, Sensor- und Bewegungs-Keep-outs.

## Logoquelle

- Primär: `business/01-strategy/brand-assets/metrimade/exports/metrimade-mark-color.svg`
- SHA-256: `41f67ccf2df52c14ee03f4c5b61f877996c680ddafcf776b6fb4e15a0cda3554`
- Horizontaler Lockup: `business/01-strategy/brand-assets/metrimade/exports/metrimade-lockup-horizontal-color.svg`
- SHA-256: `030602129f236af1fa2bfb9a016831be60be10acec82587b5d352f65824db2b5`
- Status: repository-internes, vom Projektinhaber vorgegebenes Markenasset; formale Rechte-/Markeninhaberbestätigung bleibt ein menschliches kommerzielles Release-Gate.

## Quellen

- MakerOnline-Grundkörper: https://www.makeronline.com/en/model/Anycubic%20Kobra%203%20printhead%20cover/16100.html
- Mandalorian-Remix: https://cults3d.com/en/3d-model/tool/anycubic-kobra-3-print-head-cover-mandalorian
- King-Cobra-Fremdasset: https://www.artstation.com/marketplace/p/6NaOj/king-cobra-head-am09-3d-print-model
- Kobra-3-Benutzerhandbuch: https://wiki.anycubic.com/k3/anycubic_kobra_3_user_manual-en-v1.3.pdf
- Anycubic-Druckkopfbaugruppe / Modellvarianten: https://uk.anycubic.com/products/hotend-module
- CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
