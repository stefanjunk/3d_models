# Harz terrain source 0.3.0

The source is a 120 × 80 km metric crop centered on the Harz/Brocken in
ETRS89 / UTM zone 32N (EPSG:25832), extent
`553824.1565,5697857.4304,673824.1565,5777857.4304`. Six public Copernicus
DEM GLO-30 COG tiles were read by GDAL through their immutable tile paths and
resampled globally to 1201 × 801 Float32 samples before any panel split.

- Float32 crop: `harz-source-crop-float32.tif`
- Float32 SHA-256: `e9df5860108e6e953e4c267343d9d52de1efc4140a6688ac74a474d36f5d2e60`
- Elevation range: 10.661–1139.006 m
- Immutable 16-bit master: `harz-height-master-16bit.tif`
- Master SHA-256: `88e0bb153f72ed395396882268328b425b99a3c2fac6352be93083f0ebf841d4`
- Physical mapping: 600 × 400 mm, 1200 × 800 cells, 0.5 mm sample pitch,
  50.8 PPI

The Copernicus DEM is a digital surface model. Attribution notice for this
adapted work: produced using Copernicus WorldDEM-30 © DLR e.V. 2010–2014 and
© Airbus Defence and Space GmbH 2014–2018, provided under COPERNICUS by the
European Union and ESA; all rights reserved.

Official collection and license documentation are recorded in the project
source register. The terrain is used as an abstract artwork and not as a
survey, navigation or safety dataset.
