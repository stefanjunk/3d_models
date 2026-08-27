# Hydraulische Plausibilisierung · Revision 3 DRAFT

Diese Rechnung ist eine analytische Vorprüfung, keine CFD- oder Leistungszusage. Reale Verluste hängen von Schlauchlänge, Bögen, Pumpe, Filtermedium, Verschmutzung und FDM-Oberfläche ab.

## Kein Mindestdurchfluss

Der offene Einlaufbecher beseitigt die frühere Annahme, der Zulauf müsse ständig gefüllt sein. Der 25-mm-Pumpenschlauch endet frei über dem Becher:

- bei 0 L/h steht das gefüllte System still; es gibt keinen Wassertransport;
- bei sehr kleinen Mengen tropft oder rinnt Wasser in den Becher und über das Fallrohr weiter;
- bei kleinen Mengen arbeitet Stufe 1 überwiegend als ruhiges Absetzbecken;
- mit steigendem Durchfluss wird der tangentiale Volumenwirbel stärker;
- der 15-mm-Luftspalt verhindert einen Rückwärtssiphon in den Pumpenschlauch.

Nach vollständiger Entleerung müssen Stufe 1 und Stufe 2 einmalig bis zu ihren Überläufen gefüllt werden. Erwartetes Anfüllvolumen bis zum ersten Wasser in Stufe 3: etwa 20–27 L. Das ist ein Startvolumen und keine Mindest-Durchflussrate.

## Querschnitte und Geschwindigkeiten

| Stelle | freier Querschnitt | 0 L/h | 400 L/h | 800 L/h | 1.200 L/h |
|---|---:|---:|---:|---:|---:|
| 28-mm-Tangentialauslass | 615,8 mm² | 0 | 0,180 m/s | 0,361 m/s | 0,541 m/s |
| 32-mm-Fallrohre | 804,2 mm² | 0 | 0,138 m/s | 0,276 m/s | 0,414 m/s |
| 40-mm-Klarwasserstandrohre | 1.256,6 mm² | 0 | 0,088 m/s | 0,177 m/s | 0,265 m/s |
| 100 × 28-mm-Kaskadenschlitz | 2.800 mm² | 0 | 0,040 m/s | 0,079 m/s | 0,119 m/s |

## Einlaufbecher und getauchter Auslass

Geometrische Höhen:

- Becherrand / sicherer Überlauf: Z=268 mm;
- minimale Schlauchunterkante: Z=283 mm → 15 mm Luftspalt;
- Tangentialauslassachse: Z=155 mm, Innen-Ø 28 mm;
- Krone der Innenöffnung: Z=169 mm;
- Standrohrkante Stufe 1: Z=210 mm → 41 mm statische Überdeckung der Öffnung.

Mit der vereinfachten Blendenformel und `Cd = 0,62` benötigt der 28-mm-Auslass etwa 4,32 mm Differenzhöhe bei 400 L/h, 17,28 mm bei 800 L/h und 38,87 mm bei 1.200 L/h. Für den ungünstigen angenommenen Stufe-1-Wasserstand Z=219,5 mm ergibt sich bei 1.200 L/h ein Becherwasserstand von Z=258,37 mm. Bis zum Überlaufrand bleiben rechnerisch **9,63 mm Reserve**. Das 32-mm-Fallrohr benötigt unter denselben Annahmen nur 22,78 mm; der 28-mm-Auslass ist die maßgebende Stelle.

Der Becher hat absichtlich einen offenen Notweg: Wird das Fallrohr blockiert oder reicht die reale Reserve wegen zusätzlicher Verluste nicht, läuft Wasser bei Z=268 mm kontrolliert direkt in Stufe 1. Ein Deckel oder eingetauchter Schlauch würde diese Sicherheitsfunktion und die Siphontrennung aufheben.

## Stufe 1 · Wirbel und Schlamm

Das seitlich getauchte 28-mm-Strahlrohr richtet den Zufluss tangential aus. Die Kammer erzeugt keinen Hochdruck-Hydrozyklon; bei 800 L/h ist ein langsamer Volumenwirbel zu erwarten. Grobe und dichtere Partikel wandern durch Schwerkraft zum Trichter. Das zentrale 40-mm-Standrohr zieht Wasser aus dem beruhigteren Innenbereich ab.

Der freie radiale Weg zwischen Ø50-mm-Standrohr und Trichteröffnung beträgt 10 mm. Unter dem Trichter führt der Boden zum eigenen DN25-Ablass. Grobschmutz wird bei gestoppter Pumpe durch kurzes Vollöffnen des externen Ventils ausgespült; die tatsächliche Austragbarkeit von 1–6-mm-Partikeln wird physisch geprüft.

## Stufe 2 · Lamellen und Sediment

Das Wasser fällt durch das 32-mm-Rohr zum Diffusor und steigt langsam durch die 60° geneigten Lamellen. Partikel, deren Sink- beziehungsweise Gleitbewegung die Aufwärtsströmung überwindet, treffen auf Lamellen, gleiten nach unten und fallen in den geschützten Sedimentraum. Zwölf Platten à 200 × 120 mm ergeben horizontal projiziert etwa 0,144 m². Die Flächenbelastung beträgt rund 5,56 m/h bei 800 L/h und 8,33 m/h bei 1.200 L/h.

Der integrierte Boden fällt um 5,02° zum eigenen DN25-Ablass. Der konservative vertikale Mindestabstand zur Kassette beträgt 18,72 mm. Sediment bleibt damit unterhalb der Lamellen und wird bei Pumpenstopp zum tiefen Ende gespült. Die geforderte Austragsleistung von mindestens 80 % einer definierten Testsandmasse ist ein physischer Annahmetest.

## Stufe 3, Notüberlauf und statische Last

Die Nutzfläche einer Ø242-mm-Medienscheibe beträgt etwa 0,0460 m². Daraus folgen etwa 17,39 m/h bei 800 L/h und 26,09 m/h bei 1.200 L/h. Filterwiderstand und Abscheidegrenze können ohne konkretes Medium und Verschmutzungszustand nicht garantiert werden.

Für den 80-mm-Notüberlauf liefert die vereinfachte Wehrformel `Q = 1,84 · b · h^(3/2)` etwa 13,2 mm Überfallhöhe bei 800 L/h und 17,2 mm bei 1.200 L/h. Die 35-mm-Öffnung bietet geometrische Reserve; der Blockadetest bleibt Pflicht.

Bei 1,2 m Prüfwassersäule entstehen etwa 11,8 kPa. Das System ist dennoch kein Druckbehälter: Schichtverbund, Naht, Poren, Kerben und Anschlüsse dominieren. Geschlossener oder pumpenseitig aufgestauter Betrieb ist verboten.

## Einregelung

Volumenstrom mit Behälter und Stoppuhr messen. 10 L entsprechen 45 s bei 800 L/h und 30 s bei 1.200 L/h. Die Pumpe über Bypass oder ein freies Regelventil einstellen, niemals durch Schließen eines Filter- oder Schlammablasses gegen den Behälter drücken.
