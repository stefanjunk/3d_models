# AI Provenance and Watermarking

Last researched: 2026-08-10.

## Contents

1. What provenance can and cannot prove
2. AI classification
3. Source and listing images
4. 3D file metadata
5. Visible geometry marks
6. Forensic geometry marks
7. Sidecars, hashes, and signatures
8. Disclosure wording
9. Verification and stripping tests
10. Release checklist

## 1. What Provenance Can and Cannot Prove

Provenance can link an artifact to a claimed workflow and reveal later changes. It cannot by itself prove:

- copyright ownership or human authorship;
- absence of copied content;
- patent/design/trademark clearance;
- product safety;
- that a missing marker means human creation;
- that an intact marker makes content true;
- that metadata will survive every converter, slicer, marketplace, or screenshot.

Use a layered system. Assume every single layer can be removed.

## 2. AI Classification

For each artifact, record AI role:

| Role | Example | Required trace |
|---|---|---|
| Ideation | Text suggestions or rough concept | Prompt/date, decisions, rejected ideas |
| Source image | ChatGPT concept or relief image | Original file/hash, provider terms, C2PA state, prompt, edits |
| Geometry generation | Text/image-to-3D or AI mesh | Service/model terms, input rights, raw output, human redesign |
| Code generation | OpenSCAD/CadQuery helper | Prompt/output, code review, dependency/license scan, tests |
| Editing | AI retopology, texture, repair | Before/after files, settings, human acceptance |
| Rendering | Synthetic listing scene | Disclosure classification, source assets, C2PA retention |
| Inspection | AI mesh/safety critique | Human verification; do not treat as certification |
| Documentation | Draft instructions/license summary | Human/legal review and source verification |

Use “AI-assisted” when humans materially engineer the final design. Use “AI-generated” for an artifact substantially determined by the model. Do not downplay a photorealistic synthetic image as “retouched” if it depicts an event/product photo that never existed.

## 3. Source and Listing Images

OpenAI currently uses C2PA metadata and SynthID on supported ChatGPT/Codex/API image generation. Coverage can vary. C2PA metadata can be stripped, and a watermark/fingerprint can be degraded; neither establishes truth or ownership.

Workflow:

1. Download and retain the original generated image without resaving.
2. Calculate SHA-256.
3. Inspect C2PA credentials with a trusted verifier and save a verification report/screenshot.
4. Record the prompt, date, product/account/tool, model if shown, and terms version.
5. Make edits on a copy.
6. Hash each material derivative.
7. Record the derivation from image to height map, vector, texture, profile, or CAD.
8. Preserve a visible disclosure near a photorealistic synthetic listing image when it could be mistaken for a real product photo.

Do not strip provider-applied labels to evade a rule or marketplace policy.

If an external image is used as AI input, the source register must explicitly say AI_INPUT=YES. Ordinary “display” or “stock photo” rights may be insufficient for model input and 3D derivation.

## 4. 3D File Metadata

### 3MF

3MF is an OPC/ZIP package. The Core specification permits metadata in the model and custom namespace-qualified metadata. A custom metadata entry with preserve="1" asks consumers to retain it; preservation is not guaranteed. The specification also supports package relationships and digital-signature mechanisms.

Use standard metadata names where appropriate:

- Title;
- Designer;
- Description;
- Copyright;
- LicenseTerms;
- CreationDate;
- ModificationDate.

Use a declared internal namespace for:

- ReleaseID;
- AIUse;
- ProvenanceManifest;
- ProjectID;
- SourceManifestHash.

The included embed_3mf_provenance.py script uses urn:commercial-3d-provenance:1.0. This is an internal namespace, not an official 3MF, C2PA, EU, or ISO standard. Record that fact.

Do not store private prompts, contracts, personal data, or confidential source URLs inside a customer-visible 3MF.

### STL

Binary STL has an 80-byte header that is inconsistently interpreted; ASCII STL comments are not durable structured metadata. Tools often rewrite both. Do not depend on STL metadata. Use:

- visible geometry mark;
- precise filename/version;
- sidecar provenance.json;
- SHA256SUMS/signature;
- README/license/notices.

### STEP and Native CAD

Use the file format’s standard product/author/security/classification properties when supported, plus custom project/release properties. Verify what survives export and re-import. Native CAD history is valuable internal evidence but can disclose confidential dimensions, sources, or supplier geometry; decide separately whether to ship it.

### G-code

Comments can include release ID, model hash, printer/profile, material, and warnings, but slicers and senders may strip them. Never place secrets in comments. Validate safety-critical commands and bind G-code to an exact machine configuration.

## 5. Visible Geometry Marks

Use an owned word mark, maker identifier, or neutral seller ID plus a short release/batch ID. Do not use:

- an OpenAI/ChatGPT logo or another party’s mark without permission;
- a CE mark unless legally required and conformity is complete;
- a recycling/material/certification mark without meeting its rules;
- an “AI” icon that falsely implies government approval.

Placement:

- choose a nonfunctional, low-stress, inspectable face;
- avoid mating surfaces, seals, threads, bearings, flexible hinges, calibrated flow paths, optical surfaces, electrical clearance, food-contact surfaces, skin-contact zones, medical surfaces, and crack initiators;
- keep it accessible after assembly if traceability requires;
- use raised or recessed geometry appropriate to manufacturing and cleaning;
- include a mark-placement drawing and test report.

FDM starting values for a 0.4 mm nozzle—not universal acceptance criteria:

- stroke width: approximately 0.6–0.8 mm or greater;
- relief/depth: approximately 0.4–0.6 mm or greater;
- character height: approximately 3–5 mm or greater;
- corner radius and spacing: at least one reliable extrusion path.

When the available safe region varies across products, use a small validated layout family instead of uniformly scaling one large mark. Preserve information in this order:

1. full: owned brand/logo, controlled domain or maker identifier, product/release ID, and version;
2. compact: the same identity rearranged into stacked lines at independently validated feature sizes;
3. micro: owned logo plus exact product/release ID and version, with the domain omitted only when larger variants do not fit and the domain remains in 3MF metadata and/or a provenance sidecar.

Select the most informative unscaled layout that fits at an approved rotation. Never remove the unique product/release ID or version, and validate each manufactured layout with its own slicer inspection and process-specific coupon. Treat QR/Data Matrix geometry as a separate validated option, not an automatic substitute for human-readable traceability.

Test at the worst approved orientation, layer height, material, machine, finishing, and scale. Resin, SLS/MJF, machining, molding, and larger nozzles need different limits.

Example OpenSCAD use:

    use <geometry-watermark.scad>

    union() {
      product_geometry();
      translate([x, y, z])
        rotate([0, 0, angle])
          provenance_mark("ACME-26A1", size=4, depth=0.5);
    }

For an engraved mark, subtract the mark from a sufficiently thick wall and rerun wall-thickness/stress checks.

## 6. Forensic Geometry Marks

Optional techniques:

- tiny documented parameter pattern in noncritical ornament;
- redundant release code on multiple internal/external faces;
- Data Matrix or QR geometry linked to a public verification page;
- mesh-level vertex/order fingerprint;
- controlled microtexture;
- randomized per-customer token.

Risks:

- remeshing, scaling, decimation, smoothing, repair, and screenshots remove marks;
- hidden fingerprints can create privacy/tracking duties;
- per-customer marks can create false accusations if collisions or leaks occur;
- stress concentrators and minimum-feature failures can create safety issues;
- a QR code can become stale or point to an insecure domain;
- a geometric fingerprint may be copied along with the model.

Use a privacy notice and access control for customer-specific codes. Validate false-positive/false-negative rates before relying on forensic conclusions.

## 7. Sidecars, Hashes, and Signatures

Minimum digital package:

- provenance.json;
- SHA256SUMS;
- THIRD-PARTY-NOTICES.md;
- AI-DISCLOSURE.md;
- outgoing licenses;
- public verification instructions.

Hash only final files. A SHA-256 value detects a changed byte sequence but does not identify the author. Sign the manifest or SHA256SUMS with a controlled organizational key:

- minisign or age-compatible signing;
- OpenPGP;
- Sigstore where organizational workflow and public logging are appropriate;
- an enterprise code-signing/document-signing service.

Record key owner, key ID, validity, revocation, timestamp, verification instructions, and rotation. Avoid embedding a private key in a repository or script.

C2PA is a provenance framework, not DRM. Its hashes/signatures can reveal tampering with a manifest, but complete manifest removal cannot always be prevented. Durable credentials can combine hard bindings with soft bindings such as fingerprints or watermarks.

## 8. Disclosure Wording

### Sold Design

> AI-assisted design. ChatGPT was used for [concept imagery/code drafting]. [Seller] made and verified the final geometry, dimensions, fit, print settings, and safety decisions. Release [ID]. See provenance.json.

Change this text to be accurate. Do not claim human verification of safety without documented tests.

### Synthetic Listing Render

> AI-generated product concept/render; not a photograph of a manufactured item.

Use near the image and in alt text/metadata where the channel supports it.

### Human-Only Final Geometry from AI Ideation

> AI was used during ideation. The released geometry was independently modeled and human reviewed.

Only use if the source/commit record supports independent modeling.

### No AI

Do not make a “No AI” claim unless the complete contributor, tool, plugin, and asset history supports it. Unknown is not no.

## 9. Verification and Stripping Tests

Before release:

1. Inspect original image C2PA and save result.
2. Export the final 3MF and re-open it as a ZIP/XML package.
3. Verify expected metadata fields and no private data.
4. Import/export through every supported slicer and CAD tool.
5. Record which metadata survives.
6. Render/slice the visible geometry mark and inspect minimum features.
7. Test print the mark at worst-case approved settings.
8. Verify all customer artifacts against SHA256SUMS.
9. Verify signature on a clean machine.
10. Scan QR/Data Matrix after finishing, aging, paint, or coating if used.
11. Confirm the public verification URL is controlled and durable.
12. Confirm listings show required visible disclosure after platform processing.

Any pipeline that strips metadata must be documented; keep the sidecar and visible mark.

## 10. Release Checklist

- AI roles classified per artifact.
- Provider terms and input rights recorded.
- Original generated image retained with hash/provenance state.
- Human contribution log complete.
- Voluntary/statutory/marketplace disclosure decision documented per market.
- Geometry mark uses only authorized marks and passes print/safety checks.
- 3MF/native metadata populated and stripped-metadata test complete.
- Sidecar manifest sanitized.
- Final hashes generated.
- Signature verified and key governance recorded.
- Listing renders distinguished from photographs.
- No watermark claim exceeds what the layer can prove.
