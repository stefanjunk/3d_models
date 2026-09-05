# AI Use and Provenance Statement — draft

Product: MM-DEC-003 Sunflower Bowl / Tray

Candidate: 0.2.0

Statement date: 2026-09-05

Release state: blocked; this is not yet customer-facing release copy

## Proposed disclosure

AI-assisted design. OpenAI `gpt-image 2.0` created the selected prompt-bound source image; a local geometry-only Step1X-3D fork generated the flower body; Codex assisted with requirements, uniform metric registration, the owner-confirmed 80 × 6 mm parametric disc foot, Boolean union, validation and evidence. The Step1X flower body was not repaired, simplified or parametrically reconstructed. The resulting candidate has passed automated topology, sampled thickness, protected-region and exact-profile headless slicer checks. Human final geometry, print, safety, IP and commercial release review is not complete. Synthetic renders are not photographs of a manufactured item.

## AI role register

| Artifact | Role | Provider/tool/version | Input | Human contribution/review | Original retained |
|---|---|---|---|---|---|
| prompt-bound PNG | design-reference generation | OpenAI Media Service API / gpt-image 2.0 | text prompt only | owner supplied product direction; no signed final review | yes; C2PA and SHA-256 retained |
| raw GLB | single-image geometry generation | owned Step1X-3D fork commit `4b6da92a56acb3a135b0493703470995c00c5e91` | registered PNG source | owner authorized regeneration; no signed final review | yes; exact run and runtime records retained |
| engineering scripts and reports | requirements, registration, disc-only Boolean, validation and documentation assistance | OpenAI Codex; exact model/version not exposed | product files and owner instruction | owner prohibited body repair and confirmed the disc; release approvals absent | yes in product source/history |
| diagnostic renders | synthetic geometry previews | Blender 5.2.0 LTS | candidate STL | visual inspection by Codex only | yes |

## Provenance layers

- Source-image copies and hashes: `01-sources/source-register.csv`.
- Step1X run record: `02-tools/evidence/ai-generation/fd4e92d04254-eafd0cc3-9604-4840-8aed-512cf7203124.json`.
- Runtime and cleanup attestation: `02-tools/evidence/step1x/runtime-profile-run-004.json` and `run-attestation-run-004.json`.
- Final digital candidate hash: `32c33f96c503dc104d881db8ac7194fafbfe7d169bd4abba1904c5899089c04e`.
- Geometry watermark: not yet placed; commercial release is blocked.
- Sidecar manifest: `provenance.json`.

## Human review status

The owner identified the licence concern, directed clean Step1X regeneration, prohibited model repair/parametric body reconstruction and authorized the real-print disc foot as the sole parametric addition. No named person has yet signed geometry, fit, print/process, safety/compliance, IP/similarity or business approval. AI-only visual expression and functional elements must not be represented as exclusively human-authored where law requires exclusion or disclosure.

AI provenance does not establish copyright, non-infringement, accuracy, safety, suitability or regulatory approval.
