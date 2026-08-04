# Forschungsbericht: Technische Konzepte für Spielzeug-Blaster

**Forschungsdatum:** 3. August 2026  
**Fokus:** Internationale Techniklandschaft, Schaumdarts, Schaumstoffbälle und nominelle 20-mm-Gummi-/TPR-/TPU-Bälle  
**Anwendungsfall:** Auswahl eines sicheren, überwiegend 3D-druckbaren Folgekonzepts  
**Konfidenz:** hoch für die technische Taxonomie und den regulatorischen Rahmen; mittel für die relative Verbreitung; niedrig bis mittel für exakte historische Produktzuordnungen und das 20-mm-Ballsegment

> Die Popularitätsangaben in diesem Bericht sind keine Marktanteile. Es wurde kein öffentlicher, auditierter Datensatz gefunden, der weltweite Verkäufe nach Antrieb, Zuführung und Projektilformat aufschlüsselt. Die Einordnung beruht deshalb auf Herstellerbreite, aktuellen Katalogen, Nachfüll- und Zubehörökosystemen, Produktkontinuität sowie unabhängiger Fachabdeckung.

## Kurzfassung

Die wichtigste technische Erkenntnis ist, dass Energiequelle, Energiespeicher, Projektilantrieb, Zuführung und Schussmodus getrennt betrachtet werden müssen. Ein elektrischer Blaster ist nicht automatisch ein Flywheel-Blaster: Ein Motor kann auch eine Feder-Kolben-Einheit spannen. Umgekehrt können Reibräder manuell angetrieben werden. Patente und aktuelle Produktlinien belegen diese Trennung deutlich [HOCH] (Kopman et al., 2020; Rehkemper et al., 2003; ZURU, o. D.).

In den vier untersuchten Herstellerfamilien besitzt der manuell gespannte Federkolben die breiteste beobachtete Präsenz. Motorisierte Schwungräder sind die stärkste beobachtete elektrische Alternative. Bei der Munition haben Full-Length-Schaumdarts das breiteste Katalog-, Nachfüll- und Zubehörökosystem. Half-Length-Darts sind im untersuchten 14+- und Hobbysegment prominent, aber eine weltweite Marktführerschaft ist nicht belegt. Trommeln beziehungsweise indexierte Kammern, Wechselmagazine und direktes Laden kommen alle häufig vor; wegen überlappender Kategorien und fehlender Verkaufszahlen gibt es hier keinen belastbaren universellen Sieger [MITTEL] (Buzz Bee Toys, 2025; Dart Zone, o. D.; Hasbro, o. D.-a; ZURU, o. D.).

Rival-artige Schaumrunden bilden ein eigenes Ökosystem. Sie dürfen nicht mit nominell 20 mm großen Gummi-, TPR- oder TPU-Bällen gleichgesetzt werden. Für 20-mm-Elastomerbälle wurde kein offener, herstellerübergreifender Blasterstandard mit Toleranzen, Masse, Shore-Härte und Zuführschnittstelle verifiziert. Ein gewählter Ball ist deshalb ein projektspezifisches Bauteil und muss chargenweise vermessen und geprüft werden [MITTEL].

Für einen konservativen 3D-Druck-Prototyp ist ein manuell gespannter, mechanisch im Hub begrenzter Federkolben ein sinnvoller Startkandidat. Das folgt aus seiner Prüfbarkeit, geringen Teilezahl und dem Verzicht auf Druckspeicher oder schnell rotierende gedruckte Teile. Es ist kein Nachweis, dass diese Architektur automatisch sicher oder normkonform ist. Die klinische Literatur dokumentiert ernste Augenverletzungen selbst durch kommerzielle Schaumprojektile; Schutzbrille, kein Zielen auf Gesicht und Augen sowie die Prüfung des vollständigen Systems bleiben erforderlich [MITTEL] (Cohen et al., 2023; Mandviwala & Sassani, 2021).

## 1. Technische Taxonomie

Ein Spielzeug-Blaster lässt sich zuverlässig mit fünf getrennten Fragen beschreiben:

1. Woher kommt die Energie: Handkraft, Feder, Elastomer, Batterie oder gespeicherter Druck?
2. Wo wird sie gespeichert: Feder, rotierendes Rad, Druckbehälter, elastische Blase oder gar nicht?
3. Wie erreicht sie das Projektil: Luftstoß, Reibkontakt, Flüssigkeitsstrom oder direkter mechanischer Impuls?
4. Wie wird das nächste Projektil bereitgestellt: direkt, über Kammern, Magazin, Gurt oder Hopper?
5. Wie wird ausgelöst: Einzelschuss, Slamfire, halbautomatisch oder automatisch?

Marketingbegriffe wie "motorized", "pump action" oder "automatic" beantworten jeweils nur einen Teil dieser Fragen. Sie dürfen nicht als vollständige Mechanismusbeschreibung verwendet werden [HOCH].

## 2. Die wichtigsten Antriebskonzepte

### 2.1 Manueller Federkolben

Eine Schraubenfeder speichert Energie. Beim Auslösen bewegt sie einen Kolben in einem Zylinder; der entstehende kurze Luftimpuls beschleunigt das Projektil. Die verbreitete Direct-Plunger-Variante besitzt einen relativ klaren Funktionspfad aus Feder, Kolben, Dichtung, Zylinder und Lauf. Beim Reverse Plunger bewegen sich nach Community-Terminologie konzentrische Rohrteile relativ zueinander; das spart Bauraum, erhöht aber Totraum, Reibung und Toleranzabhängigkeit [NIEDRIG] (Chung et al., 1997; Nerf Wiki contributors, o. D.-b).

Vorteile sind niedrige Teilezahl, keine Batterie, gute Prüfbarkeit, geringer Standby-Verbrauch und die Kompatibilität mit Einzelladung, Trommel oder Magazin. Typische Fehler sind verschlissene Dichtungen, beschädigte Fangflächen, Federermüdung, Gehäuserisse und Zuführstörungen. Für FDM ist das Konzept vergleichsweise geeignet, solange Feder, Achsen, hoch belastete Fangflächen und andere sicherheitskritische Einzelpunkte nicht unkritisch als spröde Druckteile ausgeführt werden.

**Beobachtete Verbreitung:** sehr breit in den vier untersuchten Herstellerfamilien [MITTEL].  
**3D-Druck-Eignung:** gut für Gehäuse, Führungen und Prototypen; eingeschränkt für Fänge und Federaufnahmen.  
**Empfehlung:** beste Ausgangsbasis für einen einfachen, energiebegrenzten Prototyp.

### 2.2 Direkte manuelle Luftverdrängung, HAMP

Hier bewegt die Hand den Kolben unmittelbar im Schusszug. Es gibt keine separate Schussfeder und keinen über mehrere Pumpbewegungen geladenen Drucktank. Die Teilezahl kann sehr klein sein; dafür hängt der Ausgangsimpuls stärker von Geschwindigkeit und Vollständigkeit der Handbewegung ab (Witzigreuter, 2009).

**Beobachtete Verbreitung:** historisch und nischig; weniger breit als Federkolben [NIEDRIG-MITTEL].  
**3D-Druck-Eignung:** gut, sofern Zylinder und Dichtung ausreichend glatt und reproduzierbar sind.  
**Empfehlung:** interessant für einen bewusst einfachen Demonstrator, aber weniger konsistent als ein mechanisch begrenzter Federkolben.

### 2.3 Motorisierte Schwungräder oder Flywheels

Ein oder mehrere rotierende Räder ziehen das Projektil ein und beschleunigen es durch Reibkontakt. Elektrische Varianten benötigen Motoren, Energieversorgung, abgeschirmte Räder und einen Pusher oder eine andere Vereinzelung. Patente belegen sowohl manuell angetriebene als auch motorisierte Varianten; "Flywheel" und "elektrisch" sind daher nicht synonym (Kopman et al., 2020; Rehkemper et al., 2003).

Vorteile sind schnelle Folgeschüsse, gute Automatisierbarkeit und die Trennung von Radhochlauf und Projektilvorschub. Nachteile sind Geräusch, Batteriemasse, Blockaden, Motor- und Schalterverschleiß sowie eine hohe Empfindlichkeit gegenüber Projektildurchmesser, Schaumsteifigkeit, Oberflächenreibung und Radspalt.

**Beobachtete Verbreitung:** stärkste elektrische Alternative im untersuchten Schaumdartsegment [MITTEL].  
**3D-Druck-Eignung:** mittel; Käfig und Kanäle sind druckbar, Räder, Wellen und Schutzgehäuse sind sicherheitskritisch.  
**Empfehlung:** geeignet für ein späteres motorisiertes Modell, nicht für den konservativsten ersten Prototyp.

### 2.4 Motorisierter Federkolben, AEB/AEG

Ein Motor und Getriebe spannen beziehungsweise takten einen Federkolben. Der eigentliche Schuss bleibt ein Feder-Kolben-Luft-Ereignis. Das verbindet elektrische Bedienung mit der Impulscharakteristik eines Springers, benötigt aber Synchronisation zwischen Getriebe, Fang, Kolben und Zuführung.

**Beobachtete Verbreitung:** vorhandenes, im Pro-/Hobbysegment neu sichtbares Konzept; nicht als breiter globaler Standard belegt [NIEDRIG-MITTEL].  
**3D-Druck-Eignung:** mittel bis niedrig wegen zyklischer Zahn-, Fang- und Führungslasten.  
**Empfehlung:** keine sinnvolle erste Architektur für dieses Projekt.

### 2.5 Starre Druckluftspeicher

Eine Pumpe oder Gasquelle lädt einen separaten Behälter; ein Ventil gibt die Energie beim Schuss frei. Das erlaubt die Trennung von langsamem Laden und schnellem Ausstoß, erhöht aber Teilezahl, Leckagerisiko, Alterung und regulatorische Komplexität (D’Andrade, 1996).

**Beobachtete Verbreitung:** historisch relevant, in der aktuellen Stichprobe deutlich schmaler als Federkolben und Flywheel [NIEDRIG].  
**3D-Druck-Eignung:** ungeeignet für den Druckbehälter.  
**Empfehlung:** ausschließen. Keine ungetesteten FDM-Druckbehälter oder Druckgaspatronen verwenden.

### 2.6 Elastische Luftblase

Eine flexible Blase speichert Druckluft und kann einen Luftstrom oder, nach Community-Dokumentation, einen wiederholten Kolbenzyklus versorgen [NIEDRIG] (Nerf Wiki contributors, o. D.-a). Vorteile sind schnelle Schussfolgen ohne Elektromotor; Nachteile sind Diffusion, Elastomeralterung, schwer reproduzierbare Ersatzteile und Ventilkomplexität.

**Beobachtete Verbreitung:** historische Speziallösung [NIEDRIG].  
**3D-Druck-Eignung:** niedrig; übliches TPU-Filament ist kein qualifizierter Ersatz für eine Druckblase.  
**Empfehlung:** nicht für dieses Projekt.

### 2.7 Sehne, Elastik oder direkter Impuls

Eine gespannte Schnur oder ein Elastomer überträgt Energie direkt auf das Projektil oder einen Träger. Das Konzept braucht keine Luftdichtung, verändert seine Kraft aber durch Alterung, Temperatur und Ersatzmaterial. Die äußere Bogenform eines Spielzeugs beweist nicht, dass im Inneren tatsächlich eine Sehne arbeitet (Lallier et al., 2016).

**Beobachtete Verbreitung:** Nische [NIEDRIG-MITTEL].  
**3D-Druck-Eignung:** mittel; Rahmen und Führungen sind druckbar, das energietragende Elastikelement sollte ein definiertes Standardteil sein.  
**Empfehlung:** nur sinnvoll, wenn die sichtbare Bogenmechanik Teil des gewünschten Spielmusters ist.

### 2.8 Benachbarte Systeme: Wasser und Gel

Wasserblaster bilden ein großes, saisonales Spielsegment, sind aber keine alternative Munition für einen Dart- oder Ballblaster. Gelkügelchen benötigen Hydration sowie eigene Zuführungs-, Alters- und Schutzkonzepte. Beide Systeme sollten als eigene Produktkategorien untersucht werden, nicht als weitere Antriebsstufe desselben Blasters.

## 3. Beliebteste Konzepte nach beobachteter Verbreitung

Antrieb, Projektil und Zuführung sind getrennte Dimensionen und werden deshalb nicht in eine gemeinsame Rangliste gezwungen.

### Antriebe

- **Breiteste beobachtete Präsenz:** manueller Federkolben über Hasbro/Nerf, X-Shot, Dart Zone und Buzz Bee [MITTEL].
- **Stärkste beobachtete elektrische Alternative:** motorisierte Flywheels im untersuchten Schaumdartsegment [MITTEL].
- **Neue beziehungsweise segmentabhängige Alternative:** motorisierte Federkolben/AEB [NIEDRIG-MITTEL].
- **Nischen und Speziallösungen:** HAMP, Druckspeicher, Luftblase und Sehnenantrieb [NIEDRIG-MITTEL].

### Projektile

- **Breitestes beobachtetes Ökosystem:** Full-Length-Schaumdarts [MITTEL-HOCH].
- **Prominent im untersuchten 14+- und Hobbysegment:** Half-Length-Darts [NIEDRIG-MITTEL].
- **Etabliertes proprietäres Ballökosystem:** Rival-artige Schaumrunden mit Magazinen und Hoppern [MITTEL].
- **Fragmentierte Spezialökosysteme:** Discs, große Raketen und proprietäre Dartformate [NIEDRIG].
- **Projektspezifische Forschungsmunition:** nominelle 20-mm-Gummi-/TPR-/TPU-Bälle; kein offener interoperabler Standard verifiziert [MITTEL].

### Zuführungen

- **Häufig wiederkehrend:** Direktladung, indexierte Kammern beziehungsweise Trommeln und Wechselmagazine. Eine belastbare Rangfolge untereinander ist nicht möglich [MITTEL].
- **Etabliert, aber projektilabhängig:** interne Magazine und Hopper [MITTEL].
- **Speziallösungen:** Gurt-, Hülsen- und Kettenzuführung mit höherem Teile- und Timingaufwand [NIEDRIG-MITTEL].

Diese Stufen beschreiben beobachtete Breite, nicht Qualität. Ein Nischenkonzept kann für einen bestimmten Spielzweck besser geeignet sein als ein Massenmarktkonzept.

## 4. Projektilkonzepte

### 4.1 Full-Length-Schaumdarts

Ein spezialisierter Händler nennt für das untersuchte Worker-SKU ungefähr 13 x 72 mm; dies ist ein SKU-bezogenes Marktmaß, keine offene Norm und kein garantiertes Grenzmaß [MITTEL] (Out of Darts, o. D.-b). Full-Length-Darts sind leicht zu greifen, axial gut führbar und in Trommeln, Magazinen sowie direkt geladenen Systemen verbreitet. Der längere Schaumkörper kann bei rauen Kanälen, hoher Magazinfederkraft oder langer Lagerung knicken und sich dauerhaft verformen (Hasbro, o. D.-a; Out of Darts, o. D.-b).

**Beste Verwendung:** massenmarktnahe, leicht beschaffbare Baseline.  
**Empfohlener Erst-Feed:** Einzelladung oder indexierte Trommel; Wechselmagazin als zweite Stufe.  
**Wichtige Einschränkung:** "Elite-kompatibel" ist ein Quasi-Standard, keine Garantie für jede Kombination aus Dart, Magazin, Verschluss und Lauf.

### 4.2 Half-Length-Schaumdarts

Zwei spezialisierte Händler nennen für untersuchte Worker-SKUs ungefähr 13 x 36 mm und 0,9 bis 1,0 g. Dies sind SKU-bezogene Marktmaße, keine offene Norm und keine garantierten Grenzmaße [MITTEL] (BlasterTECH, o. D.; Out of Darts, o. D.-a). Das kompakte Format ermöglicht kurze Magazine und definierte Zuführung, benötigt aber eigene Magazine oder Adapter. Kurze Darts können vor dem Verschluss leichter kippen, wenn Feed-Lippen und Pusher nicht exakt zusammenarbeiten.

**Beste Verwendung:** kompaktes 14+- oder Hobbydesign mit Wechselmagazin.  
**Vorteil:** kleines Magazin und gut kontrollierbarer Projektilsitz.  
**Nachteil:** höhere Zuführ- und Toleranzanforderung als bei einem einfachen Einzellader.

### 4.3 Rival-artige Schaumrunden

Die Kugelform braucht keine Längsorientierung und eignet sich für Hopper. Hasbro dokumentiert kompatible Rival-Runden, Wechselmagazine, interne Magazine, Hopper und Einzellader. Ein belastbares öffentliches Herstellergrenzmaß wurde nicht gefunden; widersprüchliche Sekundärmaße dürfen nicht als CAD-Nennmaß verwendet werden (Hasbro, o. D.-b).

**Beste Verwendung:** hoher loser Vorrat und schnelle Hopper-Nachladung.  
**Nachteil:** Brückenbildung, Ovalisierung, Reibungsänderung und proprietäre Geometrie.  
**Wichtig:** nicht mit einem 20-mm-Gummiball gleichsetzen.

### 4.4 20-mm-Gummi-, TPR- oder TPU-Bälle

Für diese Klasse wurde kein offener, herstellerübergreifender Blasterstandard verifiziert. Gleiches Nennmaß bedeutet nicht gleiche Funktion: Masse, Shore-Härte, Rückprall, Oberflächenreibung, Rundheit und Druckverformung verändern Projektilrückhaltung, Dichtung, Zuführung und Aufprall.

Ein geformter kommerzieller Ball mit kontrollierter Spezifikation ist die bessere Forschungsbasis als ein FDM-gedruckter TPU-Ball. Gedruckte Kugeln erhalten Nähte, Schichtanisotropie und streuende Masse. Wenn das 20-mm-System fortgeführt wird, sollte zunächst ein einzelner Ball-SKU festgelegt, chargenweise vermessen und nur in einer einfachen Einzelladung validiert werden.

## 5. Zuführkonzepte

### Direkt- oder Einzelladung

Niedrigste Teilezahl, beste Sichtbarkeit von Störungen und hohe Formatflexibilität. Die Schussfolge ist langsam. Für einen ersten konservativen Funktionsprototyp ist die Einzelladung ein gut prüfbarer Startkandidat [MITTEL]; daraus folgt kein Sicherheits- oder Konformitätsnachweis.

### Indexierte Trommel oder Kammerzylinder

Jedes Projektil besitzt eine eigene Kammer. Dadurch gibt es keinen langen Projektilstapel und keine separaten Magazine. Kritisch sind Indexierung, Fluchtung, Dichtung und Verschleiß der Rastung. Für Full-Length-Darts ist dies eine sehr plausible zweite Entwicklungsstufe.

### Herausnehmbares Kastenmagazin

Das Magazin ermöglicht schnellen Wechsel und kontrollierte Zuführung, benötigt aber passende Feed-Lippen, Follower, Feder und einen abgestimmten Pusher beziehungsweise Verschluss. Es ist besonders für Half-Length-Darts attraktiv. Die innere Oberfläche gedruckter Magazine muss glatt, maßhaltig und gegen Verzug geprüft sein.

### Internes Magazin oder Rohr

Weniger externe Schnittstellen und keine verlorenen Magazine. Blockaden sind dagegen schwerer zugänglich; Kapazität und Projektilformat sind stärker im Gehäuse festgelegt.

### Hopper

Ein Hopper ist ideal für runde, rollfähige, ausreichend nachgiebige Schaumprojektile. Der Behälter selbst ist einfach, die zuverlässige Vereinzelung jedoch nicht. Auslaufwinkel, Füllstand, Projektilkompression und Reibung bestimmen Brücken- und Doppelzufuhr. Ein Rival-Hopper darf nicht nur auf 20 mm skaliert werden.

### Gurt, Kette und Hülsen

Diese Konzepte bieten hohen Schauwert und Kapazität, erhöhen aber Toleranzketten, Teilezahl, Schmutzempfindlichkeit und Timingrisiko. Für ein erstes Modell sind sie schlechter als Direktladung, Trommel oder Magazin.

## 6. Vergleich für einen 3D-druckbaren Entwurf

| Konzept | Teile-/Integrationsaufwand | Dichtungsbedarf | Typische Hauptprobleme | FDM-Eignung | Einordnung |
|---|---:|---:|---|---|---|
| Manueller Federkolben | niedrig bis mittel | mittel | Fang, Federaufnahme, Dichtung, Gehäuseschlag | gut mit Standardteilen | bevorzugter Startkandidat |
| Direkte manuelle Luftverdrängung | niedrig | mittel | nutzerabhängige Konsistenz, Zylinderoberfläche | gut | einfacher Demonstrator |
| Motorisierte Flywheels | mittel | gering | Radspalt, Rundlauf, Rotorabdeckung, Elektrik | mittel | spätere motorisierte Variante |
| Motorisierter Federkolben | hoch | mittel | Getriebe, Fang, Timing, Zykluslast | mittel bis niedrig | nicht für MVP |
| Druckluftspeicher | hoch | hoch | Behälter, Ventile, Lecks, Klassifizierung | Behälter ungeeignet | ausschließen |
| Elastische Blase | hoch | hoch | Alterung, Diffusion, Ventile | niedrig | ausschließen |
| Sehne/Elastik | niedrig bis mittel | gering | Materialalterung, Anker, Ersatzmaterial | mittel | Spezialkonzept |

FFF-Teile sind keine homogenen Spritzgussteile. Orientierung, Poren, Schichthaftung, Geometrie, Temperatur und Prozessparameter verändern Festigkeit und Ermüdungsverhalten wesentlich [HOCH] (Shanmugam et al., 2021; Zohdi & Yang, 2021). Ein Filamentdatenblatt qualifiziert daher kein fertiges Sicherheitsbauteil.

Als Kandidaten eignen sich PLA+ beziehungsweise High-Speed-PLA+ für Passprototypen, äußere Abdeckungen, Lehren und nichtkritische Gehäusebereiche, PETG für zähere Gehäuse und Schutzabdeckungen sowie TPU für mechanisch gefangene Dämpfer, Kanten- und Griffauflagen [MITTEL] (eSUN, o. D.-a, o. D.-b; Prusa Research, o. D.). Diese Zuordnung muss mit dem tatsächlichen Druckprozess, der Geometrie und dem Materiallos qualifiziert werden. Primäre Federn, Achsen, Bolzen, hoch zyklische Fänge, mechanische Endanschläge und andere Einzelpunkt-Rückhaltesysteme sollten als qualifizierte Standard- oder Metallteile ausgeführt werden.

## 7. Empfehlung für dieses Projekt

### Pfad A: Schaumdart-Version

Die stärkste Kombination aus Marktanschluss, einfacher Beschaffung und beherrschbarer Mechanik ist ein manuell gespannter, mechanisch begrenzter Direct-Plunger mit kommerziellen Full-Length-Schaumdarts. Für den ersten Funktionsnachweis sollte er direkt oder einzeln geladen werden. Danach ist eine indexierte Trommel sinnvoll. Ein Wechselmagazin bringt erst dann Nutzen, wenn Projektilsitz, Luftpfad und Energievariation stabil sind.

Wenn bewusst ein 14+-Hobbysystem entwickelt werden soll, ist ein Half-Length-Dart mit passendem Wechselmagazin die kompaktere Alternative. Diese Entscheidung erhöht aber die Feed- und Toleranzarbeit und darf nicht allein aus Hobby-Popularität abgeleitet werden.

### Pfad B: bestehende 20-mm-Ball-Version

Das bestehende Ballmodell sollte als separates experimentelles Format erhalten bleiben. Dafür ist ein kommerziell geformter, weicher Ball einem gedruckten TPU-Ball vorzuziehen. Ein konkreter Ball-SKU muss festgelegt werden; Nennmaß allein reicht nicht. Zu erfassen sind Durchmesserverteilung, Masse, Rundheit, Shore-Härte, Rückprall, Langzeitverformung und Reibung.

Die Einzelladung ist zunächst richtig. Ein Hopper oder Magazin sollte erst folgen, wenn mehrere Chargen dasselbe Zuführverhalten zeigen. Rival-Geometrie ist kein direkter Ausgangspunkt, weil Rival-Runden aus stark nachgiebigem Schaum bestehen, während Nennmaß, Masse, Härte und Reibung des gewählten Elastomerballs projektspezifisch zu verifizieren sind [MITTEL].

### Entscheidung

Für einen neuen, breit anschlussfähigen Entwurf ist **Full-Length-Schaumdart + manueller Federkolben + Direktladung/Trommel** die belastbarste Baseline [MITTEL]. Für das existierende Modell kann **20-mm-Weichball + manueller Federkolben + Einzelladung** als Forschungszweig bestehen bleiben [NIEDRIG-MITTEL]. Ein gedruckter Druckspeicher, eine elastische Druckblase, ein ungekapseltes Flywheel oder FDM-gedruckte harte Munition werden nicht empfohlen.

## 8. Sicherheit und Normen

Für die USA verweist 16 CFR Part 1250 auf ASTM F963-23. In der EU gilt während des Übergangs die Richtlinie 2009/48/EG; die Verordnung (EU) 2025/2509 gilt im Wesentlichen ab 1. August 2030. ISO 8124-1:2022 mit Amendment 1:2025 enthält kategorieabhängige Anforderungen an mechanische Spielzeugsicherheit. Die vollständigen aktuellen Prüftabellen von ASTM, EN und ISO waren nicht frei in einer autorisierten, zitierbaren Fassung zugänglich. Deshalb nennt dieser Bericht bewusst keinen universellen Joule-Grenzwert (Electronic Code of Federal Regulations, 2026; European Parliament & Council, 2009, 2025; International Organization for Standardization, 2022).

Ein mechanischer Hubanschlag und eine definierte Feder sind nur erste Kontrollen. Fertiger Output hängt zusätzlich von Dichtung, Reibung, Projektilpassung, Temperatur, Verschleiß, Montagevariation und Ersatzprojektilen ab. Das komplette System muss mit Produktionsvarianten und nach vorhersehbarer Nutzung geprüft werden.

Schaum ist nicht gleich harmlos. Eine Fallserie mit elf Patienten dokumentierte unter anderem Hyphema, Glaukomkomplikationen und Verletzungen des hinteren Augenabschnitts. Ein weiterer Bericht beschreibt eine Netzhautablösung nach einem Schaumstoffballtreffer. Diese Daten bestimmen keine universelle Verletzungsschwelle, belegen aber ein glaubhaftes Risiko schwerer Augenverletzungen (Cohen et al., 2023; Mandviwala & Sassani, 2021).

## 9. Wissensentwicklung und Gegenprüfung

Die erste Arbeitshypothese war eine einfache Entwicklung von Feder über Druckluft zu Elektroantrieb. Patent- und Produktquellen widerlegten dieses lineare Modell: manuelle Flywheels, elektrische Kolbensysteme und pneumatisch getaktete Kolben existieren neben den verbreiteten Grundformen. Daraus entstand die getrennte Energiepfad-Taxonomie.

Die zweite Hypothese war, dass "runde Munition" eine gemeinsame Kategorie bilde. Offizielle Rival-Produktseiten und die erfolglose Suche nach einem 20-mm-Standard widerlegten dies. Form allein sagt wenig über Masse, Härte, Reibung und Zuführung aus.

Die dritte Hypothese war, präzise Popularitätsränge aus Katalogen ableiten zu können. Die adversariale Prüfung zeigte überlappende Feed-Kategorien, ungleiche Herstellerkataloge und fehlende SKU-Kodierung. Numerische Scores wurden deshalb verworfen. Übrig bleibt eine qualitative Verbreitungsstufung mit expliziter Stichprobenbegrenzung.

Die vierte Hypothese war, ein Federkolben könne als "sicherstes" Konzept bezeichnet werden. Dafür gibt es keine vergleichenden Fertigprodukttests. Die korrekte Aussage lautet: Er ist ein konservativer Startkandidat, weil Energiepfad und mechanische Begrenzungen gut inspizierbar sind und Druckbehälter sowie Rotoren vermieden werden.

## 10. Grenzen

Es fehlen öffentliche, auditierte globale Absatzdaten nach Technik. Die Herstellerstichprobe ist international sichtbar, aber foam-dart-lastig und deckt regionale asiatische, afrikanische, lateinamerikanische und nicht englisch dokumentierte Systeme nur schwach ab. Katalogzahlen sind Momentaufnahmen und nicht direkt zwischen Herstellerwebsites vergleichbar.

Für viele historische Modelle fehlen offizielle Innenansichten. Patente belegen technische Möglichkeiten, aber nicht, dass jede beanspruchte Variante verkauft wurde. Community-Teardowns sind nützlich, bleiben jedoch eine niedrigere Evidenzstufe.

Es wurden keine eigenen Projektile vermessen, keine Magazine zyklisch geprüft und keine Aufpralltests durchgeführt. Besonders für 20-mm-Bälle fehlen offene Toleranzen, Härten und Sicherheitsdaten. Der Bericht ersetzt weder eine Risikobeurteilung noch eine Konformitätsprüfung.

## Referenzen

BlasterTECH. (o. D.). *Worker Gen 3 plus HE 0.9g light Stefan 200x darts*. Abgerufen am 3. August 2026 von https://www.blastertech.com.au/product/worker-gen-3-plus-09g-stefan-200x-darts

Buzz Bee Toys. (2025). *Air Warriors*. https://buzzbeetoys.com/air-warriors-4/

Chung, C., Fouke, S., Handy, J., Benson, T., & Proch, N. (1997). *Air-powered projectile launcher* (U.S. Patent No. 5,653,215 A). United States Patent and Trademark Office. https://patents.google.com/patent/US5653215A/en

Cohen, S., Shiuey, E. J., Zur, D., Rachmiel, R., Kurtz, S., Mezad-Koursh, D., & Waisbourd, M. (2023). Ocular injury from foam dart (Nerf) blasters: A case series. *European Journal of Pediatrics, 182*(3), 1099-1103. https://doi.org/10.1007/s00431-022-04782-4

Dart Zone. (o. D.). *Blasters*. Abgerufen am 3. August 2026 von https://dartzoneblasters.com/collections/blasters

D’Andrade, B. M. (1996). *Safety nozzle for projectile shooting air gun* (U.S. Patent No. 5,529,050 A). United States Patent and Trademark Office. https://patents.google.com/patent/US5529050A/en

Electronic Code of Federal Regulations. (2026). *16 CFR Part 1250: Safety standard for toys*. https://www.ecfr.gov/current/title-16/chapter-II/subchapter-B/part-1250

eSUN. (o. D.-a). *PLA+HS*. Abgerufen am 3. August 2026 von https://www.esun3d.com/eplahs-product/

eSUN. (o. D.-b). *TPU-85A*. Abgerufen am 3. August 2026 von https://www.esun3d.com/eflex-tpu-87a-product/

European Parliament & Council. (2009). *Directive 2009/48/EC on the safety of toys*. https://eur-lex.europa.eu/eli/dir/2009/48/oj/eng

European Parliament & Council. (2025). *Regulation (EU) 2025/2509 on the safety of toys and repealing Directive 2009/48/EC*. https://eur-lex.europa.eu/eli/reg/2025/2509/oj/eng

Hasbro. (o. D.-a). *Nerf Elite 2.0 70-dart refill pack*. Abgerufen am 3. August 2026 von https://consumercare.hasbro.com/en-us/product/nerf-elite-2-0-70-dart-refill-pack-includes-70-official-nerf-elite-2-0-darts-compatible-with-all-nerf-elite-blasters/57E371EC-FECD-4513-85F1-736EAFDDE015

Hasbro. (o. D.-b). *Nerf Rival 50 Accu-Round refill*. Abgerufen am 3. August 2026 von https://consumercare.hasbro.com/en-us/product/nerf-rival-50-accu-round-refill-includes-50-nerf-rival-accu-rounds-the-most-accurate-nerf-rival-rounds/7D91EDB4-93AC-41F0-984B-8DC81B1497E7

International Organization for Standardization. (2022). *ISO 8124-1:2022, Safety of toys - Part 1: Safety aspects related to mechanical and physical properties*. https://www.iso.org/standard/80767.html

Kopman, V., Miller, C. D., & Victor, R. J. (2020). *Quick start projectile launcher and methods* (U.S. Patent No. 10,876,809 B1). United States Patent and Trademark Office. https://patents.google.com/patent/US10876809B1/en

Lallier, J. P., Nugent, D. M., Mermelstein, K. A., & Keska, T. W. (2016). *Toy launch apparatus with open top dart drum* (U.S. Patent No. 9,513,075 B2). United States Patent and Trademark Office. https://patents.google.com/patent/US9513075B2/en

Mandviwala, M. M., & Sassani, P. P. (2021). Traumatic retinal detachment caused by Nerf gun shot in a pediatric patient. *Retinal Cases & Brief Reports, 15*(5), 568-570. https://doi.org/10.1097/ICB.0000000000000853

Nerf Wiki contributors. (o. D.-a). *Air bladder*. Fandom MediaWiki API. https://nerf.fandom.com/api.php?action=query&prop=revisions&rvprop=content&rvslots=main&titles=Air_bladder&format=json

Nerf Wiki contributors. (o. D.-b). *Direct plunger and reverse plunger*. Fandom MediaWiki API. https://nerf.fandom.com/api.php?action=query&prop=revisions&rvprop=content&rvslots=main&titles=Direct_plunger%7CReverse_plunger&format=json

Out of Darts. (o. D.-a). *Worker HE standard-weight short darts 200-pack (1.0g)*. Abgerufen am 3. August 2026 von https://outofdarts.com/products/worker-he-standard-weight-short-darts-200-pack

Out of Darts. (o. D.-b). *Worker full-length darts 200-pack*. Abgerufen am 3. August 2026 von https://outofdarts.com/products/worker-full-length-foam-darts

Prusa Research. (o. D.). *Prusament PETG*. Abgerufen am 3. August 2026 von https://prusament.com/materials/prusament-petg/

Rehkemper, S., Rehkemper, J., Hannon, T., & Kratz, R. (2003). *Toy projectile launcher* (U.S. Patent No. 6,523,535 B2). United States Patent and Trademark Office. https://patents.google.com/patent/US6523535B2/en

Shanmugam, V., Das, O., Babu, K., Marimuthu, U., Veerasimman, A., Johnson, D. J., Neisiany, R. E., Hedenqvist, M. S., Ramakrishna, S., & Berto, F. (2021). Fatigue behaviour of FDM-3D printed polymers, polymeric composites and architected cellular materials. *International Journal of Fatigue, 143*, 106007. https://doi.org/10.1016/j.ijfatigue.2020.106007

Witzigreuter, J. D. (2009). *Manually powered projectile launcher* (U.S. Patent Application Publication No. 2009/0084372 A1). United States Patent and Trademark Office. https://patents.google.com/patent/US20090084372A1/en

Zohdi, N., & Yang, R. C. (2021). Material anisotropy in additively manufactured polymers and polymer composites: A review. *Polymers, 13*(19), 3368. https://doi.org/10.3390/polym13193368

ZURU. (o. D.). *XSHOT*. Abgerufen am 3. August 2026 von https://zurutoys.com/brands/xshot

## Anhang A: Suchstrategie

Vier parallele Themen wurden untersucht: Mechanik und Patente, Munition und Zuführung, beobachtete Marktbreite sowie Sicherheit und additive Fertigung. Jedes Thema durchlief eine Landschaftssuche, SIFT-Quellenprüfung, eine adversariale Gegenrecherche und eine Vertiefung mit Primär- oder Fachquellen. Bei verbleibenden Kernlücken wurde ein dritter Suchzyklus durchgeführt.

Repräsentative Suchbegriffe waren `toy blaster mechanism spring piston flywheel patent`, `foam dart full length half length dimensions`, `Nerf Rival round hopper magazine official`, `20mm TPR ball toy blaster`, `international toy blaster catalog spring flywheel`, `ASTM F963-23 projectile toys`, `EN 71-1 projectile kinetic energy`, `ISO 8124-1 projectile`, `foam dart ocular injury` und `FDM fatigue anisotropy PLA PETG TPU`.

## Anhang B: Quellenbewertung

Offizielle Rechtsportale und Normgeber wurden für Geltungsbereich, Ausgaben und Pflichten hoch gewichtet. Patente wurden als Primärbeleg für technische Konzepte, nicht als Verkaufs- oder Produktbeleg verwendet. Herstellerseiten wurden hoch für sichtbare Produktmerkmale, aber nur mittel oder niedrig für Leistungs- und Popularitätsbehauptungen gewichtet. Händlerdaten wurden für konkrete SKU-Maße genutzt, nicht als offene Industrienorm. Fach- und Communityseiten dienten zur Identifikation von Produktvarianten; nicht bestätigte Innenmechaniken wurden herabgestuft.

## Anhang C: Ausgeschlossene Evidenz

Kommerzielle Marktberichte mit präzisen Werten, aber nicht einsehbarer Methodik wurden ausgeschlossen. Dynamisch blockierte Händlerseiten wurden nicht für Zählungen verwendet. Widersprüchliche Rival- und Chaos-Durchmesser aus Suchtreffern wurden nicht als Konstruktionsmaße übernommen. Aktuelle numerische ASTM-, EN- und ISO-Grenzwerte wurden nicht aus inoffiziellen Zusammenfassungen übernommen. Hersteller-Superlative und unüberprüfte Community-Leistungsangaben wurden nicht als Popularitätsbeleg genutzt.

## Anhang D: Konfidenzübersicht

| Aussage | Konfidenz | Begründung |
|---|---|---|
| Energiequelle, Speicher, Wandler und Feed müssen getrennt klassifiziert werden | hoch | Patente und mehrere Produktarten liefern Gegenbeispiele zu vereinfachten Labels |
| Manueller Federkolben besitzt die breiteste Präsenz in der Herstellerstichprobe | mittel | vier Herstellerfamilien und lange technische Kontinuität, aber keine globalen Stückzahlen |
| Full-Length-Darts besitzen das breiteste beobachtete Ökosystem | mittel-hoch | Hersteller-, Nachfüll-, Feed- und Händlerbreite; keine offene Toleranznorm |
| Flywheels sind die stärkste beobachtete elektrische Alternative | mittel | aktuelle Produkte und Patentbelege, aber keine Absatzdaten |
| Half-Length-Darts sind im untersuchten 14+-Segment prominent | niedrig-mittel | starke Hobby- und Dart-Zone-Präsenz, aber keine vollständige globale SKU-Kodierung |
| Ein Feed-System ist weltweit eindeutig am beliebtesten | nicht belegt | Kategorien überlappen und Verkaufsdaten fehlen |
| Ein offener 20-mm-TPR-/TPU-Ballstandard existiert | nicht verifiziert | keine belastbare herstellerübergreifende Spezifikation gefunden |
| Federkolben ist automatisch sicher oder normkonform | nicht belegt | nur konservativer Startkandidat; vollständige Systemprüfung erforderlich |
| Schaumprojektile können schwere Augenverletzungen verursachen | mittel | Fallserie und Fallberichte ohne Populationsinzidenz |
| FFF-Bauteilverhalten ist prozess- und orientierungsabhängig | hoch | Reviews und experimentelle Werkstoffliteratur |
