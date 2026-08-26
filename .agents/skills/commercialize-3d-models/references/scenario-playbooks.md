# Scenario Playbooks

Use these as examples, not shortcuts. Complete every release gate and adapt to product/market facts.

## Contents

1. ChatGPT image to relief
2. External photo to 3D model
3. Manufacturer CAD in an assembly
4. Community model remix
5. Parametric functional part
6. Sell the model file
7. Sell the physical print
8. Commissioned/client design
9. Add a future AI-to-3D tool
10. Stop examples

## 1. ChatGPT Image to Relief

### Flow

    prompt -> ChatGPT PNG -> cropped grayscale image -> height map
    -> OpenSCAD/CadQuery relief -> STL/3MF -> print/listing

### Evidence

- Record prompt, date, OpenAI product/account/terms version.
- Retain original PNG, C2PA/SynthID verification result, and hash.
- Clear every external prompt/reference image for commercial adaptation and AI input.
- Record crop, grayscale, levels, inversion, blur, and resolution settings.
- Link processed-image hash to CAD source/commit.
- Document human relief-depth mapping, boundary design, back thickness, smoothing, and print tests.
- Review output for recognizable characters, brands, people, products, and copied style elements.
- Add release ID geometry mark and 3MF/sidecar provenance.
- Label photorealistic synthetic listing images as renders, not photos.

### Default Decision

PASS only if input rights, OpenAI terms, similarity/IP review, human engineering, image provenance, outgoing license, and product/digital compliance are documented. Provider assignment alone is insufficient.

## 2. External Photo to 3D Model

### Required Permissions

- photographer copyright;
- commercial adaptation/3D reconstruction;
- AI input if an AI service is used;
- model/person release;
- property/location permission where relevant;
- depicted art/product/design/trademark clearance;
- contractual/site/museum terms;
- privacy and biometric lawful basis for people.

### Safer Alternatives

- commission a controlled photo shoot with written releases;
- photograph an owned generic object in an authorized location;
- use a documented CC0/public-domain source and clear other rights;
- create a new abstract design rather than reconstructing a protected object.

### Block

Block a downloaded social-media/search image, celebrity/child portrait, museum object, branded product, or confidential prototype without complete written evidence.

## 3. Manufacturer CAD in an Assembly

### Internal Engineering

Record supplier, official URL, part number/revision, model hash, terms snapshot, datasheet, and engineering-use permission. Use the model for fit only within those terms.

### Digital Release

If redistribution is not expressly allowed:

- remove official CAD from the released assembly;
- independently model only required interface/keep-out geometry;
- remove logos and nonfunctional/internal detail;
- label placeholder clearly;
- provide part number and official download URL;
- verify that the simplified interface does not copy a protected design more than necessary;
- run patent/design/trademark review.

### Physical Release

Retain invoice/authorized supplier, part/lot, ratings, declarations, incoming inspection, and assembly tests. Do not advertise the supplier as endorsing the finished product.

## 4. Community Model Remix

### Workflow

1. Authenticate item page, author, revision, exact license, archive, and hashes.
2. Check uploader plausibility and depicted third-party IP.
3. Confirm commercial use and adaptation.
4. Determine whether mesh repair, scaling, format conversion, supports, or combination is an adaptation.
5. Evaluate BY-SA/CERN-OHL/GPL or custom reciprocal obligations.
6. Obtain separate permission for NC/ND/no-redistribution restrictions.
7. Carry attribution and change history.
8. License only the rights the seller owns.

### Default Blocks

- no license;
- “personal use only”;
- CC NC;
- adapted CC ND;
- fan art or branded character without rights-holder license;
- supplier/community file whose terms conflict;
- uploader cannot credibly grant rights.

## 5. Parametric Functional Part

### Flow

    requirements -> independent dimensions -> parametric code/CAD
    -> prototype -> load/fit/environment tests -> release

### Evidence

- Record requirements source and interface measurements.
- Audit OpenSCAD/CadQuery libraries/code snippets.
- Document human parameterization and engineering tradeoffs.
- Search patents, registered designs, and replacement-part/trademark issues.
- Classify safety/product category.
- Establish material/process envelope and worst-case testing.
- Lock source commit, exports, hashes, print profile, and geometry mark.
- Use separate licenses for code, geometry, and docs.

### Patent Warning

Independent creation can defeat copying allegations but is not a defense to an in-force patent and may not defeat registered design rights. Escalate close fields.

## 6. Sell the Model File

### Customer Bundle

- final files and version/release ID;
- README with units, scale, compatibility, settings, validation, limits and warnings;
- proprietary commercial model license or selected open license;
- software/source/document licenses;
- third-party notices;
- AI disclosure and provenance manifest;
- SHA256SUMS/signature;
- support/update/correction policy.

### Checkout

- display license before purchase;
- capture affirmative assent;
- provide durable contract confirmation;
- implement EU digital-content withdrawal consent/acknowledgment where applicable;
- state tax/refund/conformity/support terms accurately;
- record customer/file version for defect notices.

### Product Liability

Design the file so reasonably expected fabrication is safe within the stated envelope. Avoid selling fixed G-code broadly. Plan withdrawal/correction for a defective version.

## 7. Sell the Physical Print

### Before Listing

- classify product/markets;
- complete risk assessment and required conformity route;
- qualify geometry/material/process/component supply;
- test worst cases and foreseeable misuse;
- establish batch traceability and inspection;
- add lawful labels/contact/instructions/warnings;
- confirm online-offer fields;
- obtain insurance and incident/recall process;
- clear packaging/EPR/tax/customs/export.

### Listing

Use real product photos for safety-relevant details where possible. If using synthetic renders, identify them and do not hide surface finish, layer lines, color variation, assembly, or scale.

## 8. Commissioned or Client Design

### Contract Before Work

- define client input warranties and evidence delivery;
- define seller background IP and reusable tools;
- allocate output ownership/license and filing rights;
- define AI/tool use, confidentiality, data retention, export and security;
- allocate product classification, testing, certifications, manufacturer role, technical file, insurance, complaints and recalls;
- require written approval for scope changes;
- define portfolio/publicity rights.

### Handoff

Do not hand over broader rights than third-party inputs permit. Provide dependency/notices schedule and identify restricted supplier CAD. A client acceptance does not release the designer from nonwaivable liability.

## 9. Add a Future AI-to-3D Tool

Before uploading any prompt/image/CAD:

- review account plan and commercial output terms;
- confirm input rights and confidentiality/data use;
- review model-weights license and third-party providers;
- record generated mesh provenance and non-uniqueness;
- test whether output includes training examples, brands, characters, signatures, or unsafe topology;
- preserve raw output and document human redesign;
- compare final mesh to raw output;
- update AI disclosure and destination-market matrix;
- do not upload unpublished patentable or export-controlled designs without approval.

## 10. Stop Examples

Immediately BLOCK:

- a Star Wars/Disney/game/anime figurine for commercial sale without a rights-holder license;
- a “non-commercial” STL used in a paid product;
- a supplier STEP embedded in a paid assembly with no redistribution clause;
- a scanned child/celebrity/person without an appropriate release and privacy basis;
- a climbing, lifting, medical, food-contact, toy, electrical, firearm, vehicle, or aircraft part without product-specific review;
- a model that closely implements an active patent/design without counsel;
- a CE logo applied to an unclassified novelty product;
- “AI-free” or “100% human” marketing when AI/tool history is incomplete;
- an altered final artifact after hashes and approval;
- a sanctioned/controlled technical-data destination or unknown end use.
