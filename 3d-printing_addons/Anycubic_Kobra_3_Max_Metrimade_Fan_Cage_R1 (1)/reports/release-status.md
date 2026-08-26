# Status des Druckkandidaten

- **Geometrie:** PASS im eingebauten deterministischen Voxel-/Kantencheck; alle vollständigen Varianten sind ein zusammenhängender Körper mit positivem Volumen, 0 Randkanten und 0 nicht-manifold Kanten.
- **3MF-Struktur:** PASS; Standardpaket, Referenzen, Millimeter-Einheit, vier Mesh-Objekte und Materialzuordnungen wurden erkannt. Der zweite Topologiecheck des Prüfers blieb mangels optionalem `trimesh`-Modul `NOT_RUN`; die gleichen Körper bestanden jedoch den unabhängigen eingebauten Kanten-/Volumencheck.
- **Slicer-Preflight:** offen; Anycubic Slicer Next ist in der Arbeitsumgebung nicht verfügbar.
- **Schnittstellenpassung:** REVIEW_REQUIRED; Anycubic veröffentlicht das Frontringmaß nicht. Fit-Probe D50/D52/D54 erforderlich.
- **Oberes Schriftzugschild:** REVIEW_REQUIRED; die 54 × 8.8 mm Fläche liegt außerhalb des angenommenen Ansaugkreises, ihre reale Freigängigkeit zur unbemaßten Frontschale muss geprüft werden.
- **Luftstrom/Temperatur:** REVIEW_REQUIRED; ca. 76.8 % projizierte Öffnung trotz perforierter Bildmarke ist keine Durchflussmessung.
- **Aussehen/Kamera:** REVIEW_REQUIRED; Testvideo bei realer Kameraeinstellung erforderlich.
- **Kommerzielle Markenfreigabe:** REVIEW_REQUIRED; das gelieferte Original-SVG ist integriert, rechtliche Freigabe und reale Filamentfarbtreue bleiben beim Projektinhaber.

Ergebnis: **druckbarer Prototyp-/Fit-Kandidat, keine physisch freigegebene Serienversion**.
