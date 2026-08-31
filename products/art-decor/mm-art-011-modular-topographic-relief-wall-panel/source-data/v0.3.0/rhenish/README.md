# Rheinisches Braunkohlerevier terrain source 0.3.0

The source is a 60 × 40 km metric crop covering the Inden, Hambach and
Garzweiler mining landscape in ETRS89 / UTM zone 32N (EPSG:25832), extent
`295000,5630000,355000,5670000`. It was requested from the official GeoBasis
NRW WCS coverage `nw_dgm` as a 1201 × 801 Float32 grid. Capabilities and
DescribeCoverage responses are frozen beside the crop.

- Exact request: `SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage&COVERAGEID=nw_dgm&FORMAT=image/tiff&SUBSET=x(295000,355000)&SUBSET=y(5630000,5670000)&SCALESIZE=x(1201),y(801)`
- Float32 crop: `rhenish-source-crop-float32.tif`
- Float32 SHA-256: `592b573ce436502ee49b66317a48f55baa1e8b7586c0b217e664a827f3bcf9fc`
- Elevation range: −324.9–294.96 m
- Immutable 16-bit master: `rhenish-height-master-16bit.tif`
- Master SHA-256: `48f11069173cc445cc7070e3e3eea1aee9b61071cf31a5129941fc399e798a6f`
- Physical mapping: 600 × 400 mm, 1200 × 800 cells, 0.5 mm sample pitch,
  50.8 PPI

GeoBasis NRW publishes its Open Data geobasis datasets under Datenlizenz
Deutschland – Zero 2.0. The source is used as a time-specific abstract terrain
artwork and not as a survey, navigation, stability or mining-safety dataset.
