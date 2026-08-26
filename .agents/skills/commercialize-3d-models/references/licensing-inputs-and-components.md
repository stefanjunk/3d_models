# Licensing Inputs and Components

Last researched: 2026-08-10.

## Contents

1. Rights by design stage
2. Permission vocabulary
3. Images, photos, scans, and AI inputs
4. 3D libraries and community models
5. Manufacturer and bought-part CAD
6. Open licenses
7. People and commissioned work
8. Dependency compatibility
9. Attribution and notices
10. Decision examples

## 1. Rights by Design Stage

| Stage | Typical inputs | Required evidence | Seller remains responsible for |
|---|---|---|---|
| Brief and ideation | Client requirements, prompts, sketches | Client authority, NDA, contributor terms | Avoiding confidential leakage, copying, unlawful instructions |
| Concept image | ChatGPT image, stock photo, own photo, external illustration | Provider terms plus source license/model/property releases | Input rights, similarity review, truthfulness, retained provenance |
| Image processing | Crop, trace, height map, texture, segmentation | Modification/derivative permission; AI-input permission if used | Whether processing is legally an adaptation; attribution/change notice |
| Parametric CAD | OpenSCAD/CadQuery code, sketches, dimensions | Contributor ownership; code/library licenses; tool plan | Human authorship record; patents/designs; copied code |
| Native/mesh editing | FreeCAD/Blender/native CAD, STL/OBJ/STEP | Model license; add-on/assets/fonts/textures | License compatibility; hidden embedded assets; provenance |
| Imported component | Supplier/library CAD, fastener, insert, electronics | Exact item terms; redistribution/manufacture permission; supplier proof | Patent/design/trademark/safety and version correctness |
| Export | STEP, STL, 3MF, OBJ, G-code | Rights for every contained element; exporter/plugin terms | Metadata/notices, format security, scale/tolerance accuracy |
| Listing | Render, photo, logo, copy | Image/font/brand rights; AI disclosure classification | Advertising accuracy, endorsement, privacy, marketplace rules |
| Digital sale | Files, presets, docs | Outgoing EULA/open license; consumer terms | Conformity, support, tax, export, product-file liability |
| Physical sale | Print, packaging, instructions | Manufacture/sale permission and conformity evidence | Safety, traceability, labels, insurance, recalls |

The seller owns the clearance decision. A tool provider, marketplace, upstream creator, supplier, AI assistant, slicer, or print service does not assume the seller’s non-infringement and product-compliance duties unless a specific enforceable agreement says so.

## 2. Permission Vocabulary

Record each permission independently as YES, NO, UNKNOWN, or NOT APPLICABLE:

- view/reference;
- download and retain;
- commercial internal use;
- modify/adapt;
- use as AI input;
- reproduce in an intermediate work;
- embed geometry in a native/editable file;
- redistribute source/native CAD;
- redistribute a derived mesh;
- manufacture;
- sell physical products;
- advertise with source images/marks;
- sublicense to customers or contractors;
- omit attribution;
- apply DRM/additional terms;
- patent license;
- trademark/brand permission;
- privacy/publicity/model/property release;
- access to updates and continued use after subscription ends.

UNKNOWN is not YES. “Royalty-free” usually means a pricing model, not an unlimited transfer of rights. “Free” describes price, not license.

## 3. Images, Photos, Scans, and AI Inputs

### ChatGPT-Generated Images

Retain:

- original downloaded file before editing;
- prompt and date;
- account/workspace and relevant OpenAI terms version;
- model/tool name if shown;
- C2PA metadata and SynthID signal where supported;
- human selection, rejection, edits, and engineering decisions;
- source-register row using a custom LicenseRef for the terms;
- similarity/trademark/character/person review.

OpenAI terms require the user to have rights and permissions for input and assign output to the user as between the parties. They also warn that output can be non-unique and must be evaluated. Do not treat generated content as a warranty.

When the image becomes a height map or geometry:

- hash both the original and processed image;
- record the processing command/settings;
- link the resulting CAD feature to the source ID;
- keep provider provenance on the original;
- assume image-to-heightmap-to-STL conversion will strip C2PA metadata;
- add the source relationship to the release manifest.

### Own Photos

“I took the photo” may establish photographer copyright but not all depicted rights. Record:

- who took it, when, where, and on whose equipment/time;
- employment/client assignment;
- person/model consent;
- property/location access restrictions;
- depicted art, logo, product design, architecture, or confidential prototype;
- RAW/original file hash and edit history.

### Third-Party Photos, Stock, Museums, and Social Media

Require the exact asset license and invoice/download proof. Confirm:

- commercial merchandise/product-design use is included;
- adaptation, vectorization, 3D reconstruction, texture extraction, and AI input are included;
- print-run, territory, channel, seat, and sublicensing limits;
- editorial-only, sensitive-use, logo, and resale/template restrictions;
- whether an “extended” merchandise license is required;
- model/property releases and whether the provider warrants them.

Do not treat a search engine, social post, museum web viewer, catalog image, or press photo as licensed merely because it is public.

### Scans and Photogrammetry

Clear:

- rights in the scanned object;
- rights in photos/scans used;
- museum/site/competition/contract terms;
- design/patent/trademark and cultural-heritage restrictions;
- people/background data captured;
- database rights in a scan collection;
- confidentiality and security restrictions.

A new scan can carry rights in capture/processing while still infringing rights in the underlying object.

### Public Domain and CC0

Verify the public-domain determination per target jurisdiction and preserve its source. CC0 is a rights-holder dedication/fallback license for copyright and related rights; it does not erase third-party patent, trademark, privacy, publicity, or moral rights. A Public Domain Mark is descriptive rather than a transfer by an owner. Record which one applies.

## 4. 3D Libraries and Community Models

For Thingiverse, Printables, MakerWorld, GrabCAD, GitHub, CGTrader, TurboSquid, Sketchfab, MyMiniFactory, or any future library:

- open the exact item page and exact license;
- capture the item revision, author identity, URL, download date, file hash, and page/terms snapshot;
- inspect included LICENSE, README, archive metadata, and per-file notices;
- check whether uploader ownership is credible and whether the model depicts another party’s product, character, logo, or design;
- distinguish platform-wide terms from item-specific license;
- verify commercial use, derivative permission, and digital/physical redistribution separately;
- verify whether remixes inherit attribution/share-alike;
- avoid files with no explicit license or contradictory labels;
- keep evidence even if the item later disappears.

Community upload does not prove the uploader owns the work. An item titled “official” is not official without an authenticated rights-holder source.

## 5. Manufacturer and Bought-Part CAD

### Default Rule

Use supplier CAD to design an assembly only if its terms permit that engineering use. Do not include it in a customer-delivered file unless its terms expressly permit redistribution in that form.

### Safer Digital Package

When redistribution is not granted:

- create an independently modeled interface envelope containing only necessary mounting, keep-out, mating, and clearance geometry;
- name it generically or by factual compatibility statement reviewed for trademark accuracy;
- remove supplier logos, decorative detail, internal geometry, and manufacturing data;
- provide the official part number and supplier download link;
- instruct the customer to obtain the official model directly;
- document independent measurements and public datasheets;
- preserve the license analysis showing why the supplier CAD was excluded.

This reduces copied expression and confidential detail but does not clear patents, designs, trademarks, or contractual restrictions.

### Physical Product Evidence

Retain:

- supplier legal name and authorized channel;
- part number, revision, datasheet, CAD revision, invoice, lot/serial;
- material and regulatory declarations;
- intended-use ratings and derating;
- safety certifications without implying they certify the final assembly;
- change/discontinuation notice monitoring;
- incoming inspection and counterfeit controls;
- written permission if branding appears in marketing.

### Standards and Fasteners

A standard dimension is not automatically free from:

- copyright/database rights in a standards document or CAD library;
- patents covering a particular implementation;
- trademark restrictions on certification marks;
- contractual restrictions on redistributing standards content.

Model necessary interface dimensions independently where appropriate and cite the standard number without copying protected tables or library files into the package.

## 6. Open Licenses

### Creative Commons Quick Matrix

| License | Commercial use | Adapt | Typical concern |
|---|---:|---:|---|
| CC0 1.0 | Yes | Yes | Other rights and provenance remain |
| CC BY 4.0 | Yes | Yes | Attribution, license link, change indication |
| CC BY-SA 4.0 | Yes | Yes | Adapted material must use compatible ShareAlike terms; no extra restrictions |
| CC BY-ND 4.0 | Yes, unadapted | No distribution of adaptations | Scaling, repair, conversion, combination may be an adaptation; BLOCK if uncertain |
| CC BY-NC 4.0 | No commercial use | Yes only noncommercially | BLOCK commercial release without separate permission |
| CC BY-NC-SA 4.0 | No commercial use | Yes only noncommercially | BLOCK commercial release without separate permission |
| CC BY-NC-ND 4.0 | No | No adaptations | BLOCK |

CC licenses cover copyright and certain similar rights the licensor controls. They do not grant patent, trademark, privacy, publicity, or endorsement rights. Version and ported jurisdiction matter; never record merely “Creative Commons.”

### CERN Open Hardware Licence v2

Use only the exact variant:

- CERN-OHL-P-2.0: permissive;
- CERN-OHL-W-2.0: weakly reciprocal;
- CERN-OHL-S-2.0: strongly reciprocal.

They are designed for hardware source and define obligations around source, notices, modifications, and products. Commercial use is possible, but reciprocal duties may require making corresponding source available. Read the actual text and compatibility guidance before mixing components.

### Software Licenses in CAD Code

If OpenSCAD/CadQuery/Blender scripts include third-party code:

- permissive MIT/BSD/Apache code generally needs notices; Apache also contains express patent terms and NOTICE mechanics;
- GPL/AGPL code can impose reciprocal source obligations on a combined/distributed program;
- LGPL obligations depend on linking/modification;
- proprietary snippets may prohibit reuse;
- a code license does not automatically license generated geometry, fonts, meshes, or trademarks.

Use SPDX expressions. When no standard identifier exists, assign an internal LicenseRef and keep the full text/snapshot.

## 7. People and Commissioned Work

### Contributor Agreement Minimum

Cover:

- deliverables and background IP schedule;
- assignment/license of copyright, designs, inventions, code, CAD, renders, docs, and modifications;
- right to manufacture, distribute files, sell products, sublicense customers/contractors, translate, advertise, and enforce;
- patent/design filing cooperation;
- moral-right consent/waiver where lawful;
- warranty of disclosed third-party inputs and license evidence;
- AI tools and input restrictions;
- confidentiality, security, personal data, open-source policy;
- payment, acceptance, termination, governing law, and signatures.

### Model/Person Release Minimum

Specify:

- identity and authority/guardian;
- captured material;
- 2D, 3D, scan, avatar, AI training/input, synthetic editing, product, advertising, and archive uses;
- commercial channels, territory, term, sublicensing, and compensation;
- sensitive-use exclusions;
- name/endorsement rules;
- privacy notice, lawful basis, retention, withdrawal/objection handling;
- contact and signature.

Use local counsel for biometric scans and minors.

## 8. Dependency Compatibility

Build a graph, not a flat list:

- node = source, asset, code library, component, or contributor;
- edge = copied, adapted, linked, embedded, combined, referenced, manufactured, or displayed;
- output = each separately distributed artifact.

Evaluate obligations per output. A proprietary STL, open OpenSCAD source, CC BY render, and trademarked product name can coexist only if notices and scopes make the separation clear.

Compatibility review questions:

1. Does the input allow commercial use?
2. Does it allow this transformation?
3. Does it allow redistribution in this artifact?
4. Must the adaptation or source be shared under the same/compatible license?
5. Would the planned EULA or DRM add a prohibited restriction?
6. Are attribution/source/offer requirements technically deliverable?
7. Are patent or trademark rights missing?
8. Can the seller truthfully grant the promised customer rights?

If any answer is unknown, do not issue the outgoing license yet.

## 9. Attribution and Notices

For each attribution item, preserve TASL:

- Title, if supplied;
- Author/attribution party;
- Source URL;
- License name/version and URL;
- copyright and disclaimer notices supplied;
- statement of changes and previous modifications.

Place notices:

- in THIRD-PARTY-NOTICES.md beside digital files;
- in source code headers or LICENSES directory when required;
- in product instructions/packaging or a durable online notice for physical products when the license or law requires;
- in listing credits if required by the source/platform terms.

Do not imply endorsement. Do not remove attribution just because geometry is hidden inside a mesh.

## 10. Decision Examples

### CC BY Relief Image to Proprietary STL

Potentially workable if:

- commercial use and adaptation are permitted;
- attribution/change notice ships with the STL;
- other depicted rights are cleared;
- proprietary customer terms do not purport to revoke the source license for the CC-covered material;
- the seller identifies which portions are third-party and which human contributions are separately licensed.

### CC BY-SA Mesh Remixed into a Proprietary Mesh

Usually incompatible with a proprietary no-redistribution license for the adapted material. Release under the applicable BY-SA terms, obtain a separate commercial license, or redesign without copying.

### CC BY-ND Image Converted to Height Map

Treat the conversion as an adaptation risk. BLOCK distribution without separate permission.

### Manufacturer STEP Model Inside a Paid Assembly

BLOCK unless exact supplier terms authorize redistribution. Ship an interface envelope and official download link instead.

### Photo of a Branded Toy Used to Generate a Similar Figurine

Photo permission alone is insufficient. Character, design, trademark/trade dress, and possibly publicity rights create a high infringement risk. Redesign independently or obtain licenses.

### “Free for Personal Use” Font Embossed in a Product

BLOCK commercial use. Obtain a commercial font license covering embedding/physical products or use a properly licensed alternative. Record the font file hash and terms.
