# Imagegen prompting and Step1X input preparation

Read this reference only when creating, editing or accepting the single Step1X input plate.

## Target plate

Step1X is single-image-conditioned. Its paper describes training views spanning orthographic or roughly 35–100 mm perspective equivalents, moderate elevations/azimuths, background removal, centering and about 90% object occupancy. Match that distribution without cropping the silhouette.

Default plate:

- one semantic object or component;
- square transparent PNG, normally 1024×1024 for imagegen iteration;
- complete silhouette with about 5–10% clear margin;
- canonical three-quarter view at eye level or slightly above, with modest/near-orthographic perspective;
- stable front and up direction from the component brief;
- broad diffuse studio light, matte or low-specular surface, recoverable concavities;
- no ground plane, scenery, stand, hand, ruler, arrow, annotation, text, logo, watermark, cast shadow or neighbouring part.

Transparent PNG is preferred. In the current local runtime, meaningful alpha bypasses rembg/U2Net. This improves thin-edge control, removes a CPU stage and makes the exact model-dependency history simpler. Preserve the alpha channel; converting to RGB discards it.

## Prompt structure for `imagegen`

Use a concise visual brief in this order:

1. semantic identity and whether it is a whole object, component or preform;
2. primary volumes, proportions, silhouette and intentional negative spaces;
3. surface character and only physically meaningful detail;
4. view, projection, framing and orientation;
5. lighting/material for shape readability;
6. interface strategy and sacrificial stock;
7. explicit exclusions and unchanged constraints;
8. transparent-background output request.

Iterate with small, single-purpose edits. Generate several low/medium-quality variants when massing is uncertain; spend high quality only after the silhouette works. Re-state critical invariants on edits.

### Whole appearance-led object

```text
Create an original [object] as a single coherent product-form concept.
Primary form: [volumes/proportions]. Required silhouette/negative spaces: [list].
The hidden back should be deliberately simple and compatible with later engineering.
Canonical three-quarter view, object centered, fully visible, 8% clear margin,
minimal perspective, front=[direction], up=[direction].
Matte neutral material, broad diffuse studio lighting, readable concavities.
No text, logo, fastener details, scenery, stand, floor, cast shadow or extra object.
Isolated on a fully transparent background; clean alpha edge, no halo/checkerboard.
```

### Organic component with CAD-owned interface

```text
Create one isolated [component ID/name] for [appearance role].
Visible protected form: [silhouette, motif, negative spaces].
At [attachment side], add a simple thick sacrificial [root/collar/rear mass]
extending beyond the future trim plane; keep ornament out of that edit band.
Do not create a socket, key, screw hole, thread, snap, seal or mating surface.
Canonical three-quarter view with the attachment side readable, fully uncropped.
Matte clay, diffuse light, minimal perspective, transparent background.
No product body, neighbouring parts, text, logo, ruler, shadow or scenery.
```

### Sacrificial preform for Boolean/CAD post-processing

```text
Create a closed, thick, single-piece preform for [object/component].
Prioritize outer massing and the protected visible surfaces: [list].
Keep generous solid stock inside [future cavity/channel/hole/mount regions].
Do not depict or model those precise features; they will be cut parametrically.
Avoid thin sheets, floating pieces and deep texture noise below [print budget].
Canonical three-quarter view, centered and fully visible, matte clay,
broad diffuse lighting, transparent background, no shadow/scenery/text/logo.
```

## What not to prompt into the image

Do not rely on phrases such as “exactly 40 mm,” “M4 thread,” “0.25 mm clearance,” or “perfectly flat datum.” Image pixels cannot enforce metric constraints. Put those values in the component/interface contract and implement them later in CAD.

Avoid photorealistic microtexture for shape selection. Strong reflections, printed stripes, AO, cast shadows and texture seams can be mistaken for geometry. Use a separate appearance plate or texture pass only after clay geometry passes.

Do not create an unlabeled contact sheet of multiple views. The current Step1X endpoint accepts one image and may fuse the panels into one object. If extra evidence exists, use it for human/agent validation and choose one controlled input plate.

## Preprocess existing images

Preserve the original. Load `reconstruct-printable-3d-from-images` and use its deterministic preprocessor:

```bash
python /resolved/reconstruct-printable-3d-from-images/scripts/preprocess_image.py \
  evidence/source.png --output-dir evidence/source-preprocessed \
  --background alpha --padding-fraction 0.08 --max-side-px 2048
```

Use `subject-square.png` only after reviewing:

- alpha edge at thin appendages and holes;
- no foreground touches the image border;
- one expected subject/component;
- no halo, residual shadow or background island;
- correct EXIF orientation and handedness;
- the smallest required visible form has adequate pixels;
- no upscaling is misrepresented as new evidence.

If automatic masking is unreliable, edit the alpha mask explicitly with `imagegen` or a raster editor and preserve both the original and edited derivatives.

## Candidate acceptance order

1. semantic identity and component count;
2. handedness/symmetry and front/up intent;
3. massing and multi-view-plausible silhouette;
4. intentional negative spaces;
5. sacrificial seam reserve and keep-out compatibility;
6. absence of thin sheets, floaters and fused neighbours;
7. printable detail budget;
8. texture/albedo appearance.

Reject attractive texture on wrong geometry.

## Provenance to retain

Archive and hash:

- original source/reference images and rights record;
- full imagegen prompt and every edit instruction;
- image model/tool/version, account/terms context and generation timestamp;
- all candidate PNGs and selection/rejection decision;
- final Step1X plate with alpha intact;
- C2PA or other provider metadata before any conversion;
- preprocessing command and report.

The Step1X client can copy a prompt file and an image-generation record into the run directory with `--image-prompt-file` and `--input-record`.

## Primary sources

- [OpenAI image generation guide](https://developers.openai.com/api/docs/guides/image-generation)
- [OpenAI GPT Image prompting guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide)
- [Step1X-3D technical report](https://arxiv.org/abs/2505.07747)
