# Decomposition – MM-SHO-001 V6.2

| Baustein | Source of truth | Rolle | Geschützte Schnittstelle |
|---|---|---|---|
| Freeform-Upper-Hülle | `generate_v6_2.py` + `parameters.yaml` | sichtbare flexible Haut | V6.1-Sohlen-/Lippenrand |
| Komfortkragen | derselbe parametrische Flächendomänenbau | geschlossene, gerundete freie Kante | Öffnungsplanform und 0,8-mm-Einengungsgrenze |
| Fuzzy-Shell-Variante | `fuzzy_shell_wall` | dünne Vollhülle | 1,4-mm-Basis, 2,6-mm-Kragenband |
| Infill-Envelope-Variante | `infill_envelope_wall` | dickes optionales Envelope | 4,5 mm nominal, 2,6 mm lokal am Kragen |
| Reinforcement-Frame | parametrische Teilflächendomäne | unterer Rahmen, Fersenzähler, Kragenring | separater Mittelschlitz und reguläre Vereinigung |
| Kragen-Coupon | aus aktueller Fuzzy-Shell abgeleitet | kleinster physischer Komfort-/Prozessnachweis | gleiche Randkonstruktion wie Voll-Upper |
| V6.1-Sohle/Lippe | `../barfussschuh_v6_1_fitfix/` | unveränderte externe Baugruppe | dichter PCHIP-Schnittstellenvergleich |

Links und rechts werden aus derselben linken parametrischen Quelle gespiegelt.
Es gibt keine Kaufteile oder Boolean-Integration mit der Sohle in dieser Phase.
