# Berlin OSM source snapshot

- Transport URL: `https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf`
- Retrieved: 2026-08-31 (Europe/Berlin)
- Frozen local name: `berlin-snapshot.osm.pbf`
- Bytes: 99,132,753
- MD5: `f8abc6fea7f28079476afcb115171076` (matches the provider sidecar)
- SHA-256: `44878bac7391c7d1e9d86e583a0cbd9713a69d164ac47ad1e4ab7e7d374d407c`
- Source CRS: WGS 84 / EPSG:4326
- Derived working CRS: ETRS89 / UTM zone 33N / EPSG:25833

The failed attempt to retrieve the dated `berlin-260828.osm.pbf` returned HTTP
502 and produced no accepted source artifact. The provider's `latest` endpoint
was therefore used only as transport; this frozen file hash, not the moving URL,
is the build authority.

Derived GeoJSON layers were produced with GDAL/OGR 3.13.3: one Berlin
administrative boundary, major road lines, motorway/trunk accent lines,
rail/light-rail/subway lines and river/canal lines. Their hashes are recorded by
the Berlin build manifest.

Map data © OpenStreetMap contributors, available under the Open Database
License (ODbL) 1.0: <https://www.openstreetmap.org/copyright>.
The extract was distributed by Geofabrik GmbH. The physical artwork and its
digital release notes must retain readable attribution; commercial/share-alike
treatment remains a separate final rights-review gate.
