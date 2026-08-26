# Examples

`person-cylinder-job.json` demonstrates the critical anisotropic sampling case:

- physical patch: 80×40 mm;
- X pitch: 0.20 mm/px;
- Y pitch: 0.12 mm/px;
- `aspect_policy: preserve`;
- `fit_mode: contain`;
- square-pixel human preview enabled by the rebuild job.

The geometry raster's raw pixel aspect is not expected to equal the physical image aspect.

`desk-organizer-relief-acceptance.json` demonstrates the starting acceptance gate derived from the carbon-relief organizer: separate reference/manufacturing meshes, under 0.1% absolute volume change, at least 0.98 relief correlation, under 5% robust contrast loss, and RMS error no greater than 5% of nozzle diameter. Its numbers are illustrative measurements, not evidence for another model.
