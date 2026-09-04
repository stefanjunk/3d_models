# MM-ART-010 Berlin — DRAFT digital-candidate-r4

Die korrigierte Revision 0.5.3 bilanziert sämtliche erfassten Gewässer. Alle innerhalb des jeweiligen Ausschnitts druckbar erhaltenen Wasserflächen und Wasserlinien werden zu Durchbrüchen; Mindestbreiten, geschützte Funktionszonen und die freigegebenen lokal notwendigen 2-mm-Topologiestege sind im Accounting ausdrücklich dokumentiert. Sky Blue ist S-/U-Bahn sowie Stadtgrenze/Standortmarker zugeordnet. Alle vier nativen Anycubic-Projekte enthalten vier nichtleere Werkzeugkörper und wurden nativ gesliced. Ein Druck oder eine kommerzielle Freigabe wird damit noch nicht autorisiert.

| Modus / Hälfte | 3MF-Dreiecke | Native Layer | Werkzeugwechsel | Ergebnis |
|---|---:|---:|---:|---|
| `boundary_crop` left | 102,312 | 26 | 8 | PASS |
| `boundary_crop` right | 86,848 | 23 | 3 | PASS |
| `context_outline` left | 194,404 | 26 | 8 | PASS; GUI floating-region review |
| `context_outline` right | 199,708 | 23 | 3 | PASS; GUI floating-region review |

Die Öffnungsanteile liegen zwischen 6,86 % und 9,53 % je Hälfte und damit unter dem 12-%-Limit. Tegeler See bleibt mit 202,94 mm² (`boundary_crop`) beziehungsweise 262,56 mm² (`context_outline`) als echte Öffnung erhalten. Je nach Modus/Hälfte verbinden 56 bis 148 ausschließlich lokal erforderliche 2-mm-Stege abgetrennte Landinseln. Es gibt kein Rückraster, keine pauschalen Rippen und keine lokalen rückseitigen Rippen.

Alle Mesh-, 3MF-, Quellen-, Hash- und kanonischen Anycubic-Slice-Prüfungen bestehen. Die Kontextvariante erzeugt in beiden Hälften eine Anycubic-Warnung zu schwebenden Bereichen; diese muss vor dem Druck in der farbigen Layer-Vorschau bewertet werden. Physische Steg-/Handhabungs-/Wandtests, ACE/Purge, Licht-/Opazitätsprüfung, 2-m-Logoerkennung, Wasserzeichen und kommerzielle Freigabe bleiben offen.
