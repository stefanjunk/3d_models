# Berlin metropolitan OSM source snapshot — revision 0.4.0

The production context extent is a distortion-free 3:2 rectangle derived from
the approved minimum 12% Berlin margin. The vertical margin remains 12% per
side; the horizontal margin expands symmetrically to 26.6545805% per side so
the 70,194.169 × 46,796.112 m source extent fills 600 × 400 mm without crop,
stretching or letterboxing.

- Selected EPSG:25833 bounds: `357796.5793918899, 5794991.9300077595, 427990.7480931101, 5841788.04247524`
- Selected WGS84 bounds: `12.915122544462, 52.286863833626, 13.933841707589, 52.721180774853`
- Protective extraction WGS84 bounds: `12.90, 52.28, 13.95, 52.73`
- Working CRS: ETRS89 / UTM zone 33N (`EPSG:25833`)

## Frozen transport authority

- Provider data: Geofabrik OpenStreetMap Germany extract
- Provider filename identified by sidecar: `germany-260830.osm.pbf`
- Provider URL: `https://download.geofabrik.de/europe/germany/germany-260830.osm.pbf`
- Retrieval mirror: `https://ftp5.gwdg.de/pub/misc/openstreetmap/download.geofabrik.de/germany-latest.osm.pbf`
- Retrieved: 2026-09-01 (Europe/Berlin)
- Bytes: `4,828,999,134`
- Provider MD5: `67f6fe1597784796ebe0d36ac5fb990f`
- SHA-256: `505860193092ce58cc8e4bb7f3b657b5f7de5f6d329d2b1bed44561cdfa7da55`

The direct Brandenburg transport endpoint returned HTTP 502 or timed out and
produced no accepted artifact. The GWDG file is a mirror of the Geofabrik
Germany transport. Only the spatially bounded `metropolitan-lines-snapshot.gpkg`
and deterministic semantic GeoJSON derivatives are retained in the product;
the 4.8 GB Germany transport is a temporary verified build input.

`source/v0.4.0/berlin/extract_context_source.py` verifies byte count, provider
MD5 and SHA-256 before it accepts the PBF. It then freezes the bounded line
snapshot and derives major roads, accent roads, rail and river/canal layers in
EPSG:25833. `source-manifest.json` records exact commands by generator source,
feature counts, hashes and the fail-closed extent containment result.

Map data © OpenStreetMap contributors, available under the Open Database
License (ODbL) 1.0: <https://www.openstreetmap.org/copyright>. The extract was
distributed by Geofabrik GmbH and retrieved through the GWDG mirror. Physical
and digital release material must retain readable attribution; commercial and
share-alike treatment remains a separate final rights-review gate.
