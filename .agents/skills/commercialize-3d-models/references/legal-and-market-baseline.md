# Legal and Market Baseline

Last researched: 2026-08-10. Treat this as issue-spotting, not legal advice. Re-open the primary sources in the source register before each release.

## Contents

1. Core distinctions
2. Copyright and AI authorship
3. Functional objects and overlapping rights
4. Patent, design, and trademark clearance
5. People, photos, scans, and confidential information
6. EU AI transparency
7. Other AI-transparency markets
8. Contract and consumer law
9. Ownership and contributor chain
10. Release escalation rules

## 1. Core Distinctions

Keep these questions separate:

| Question | What proves it | What it does not prove |
|---|---|---|
| May the seller use an input? | License, assignment, contract, exception, or public-domain analysis | That no patent, design, trademark, privacy, or publicity right applies |
| Does the seller own an output? | Employment/contract chain and tool-provider terms | Copyrightability, exclusivity, originality, or non-infringement |
| Is the output copyrightable? | Applicable law plus documented human expression | Freedom to operate under patent/design/trademark law |
| May a file be redistributed? | Express redistribution/sublicensing rights | Permission merely to inspect, reference, buy, or manufacture |
| May prints be sold? | Commercial manufacture/sale permission plus product compliance | Permission to redistribute source CAD |
| Is a product safe and marketable? | Classification, risk assessment, testing, conformity, labeling, traceability | IP ownership |
| Is it “AI labeled”? | Applicable provider/deployer rule plus marketplace terms | Ownership, truth, quality, or safety |

OpenAI’s assignment of output to the user “as between” the parties is an important contract right, but the current terms also say outputs may not be unique, require human review, require rights in inputs, and prohibit representing output as human-generated when it was not. Never convert that assignment into an unsupported statement that the result is exclusively copyrighted or cleared against third parties.

## 2. Copyright and AI Authorship

### United States

The U.S. Copyright Office’s AI copyrightability report concludes that copyright protects human-authored expression perceptible in an AI-assisted output, not material determined entirely by the machine. Prompts alone generally do not provide sufficient control. Human selection, arrangement, and creative modification can be protected to the extent of the human contribution.

For a U.S. registration:

- disclose more-than-de-minimis AI-generated material;
- exclude that material from the claim;
- identify the human-authored selection, arrangement, editing, code, or geometry being claimed;
- preserve a contribution log and versions supporting that statement.

Functional products are “useful articles.” Copyright generally protects only pictorial, graphic, or sculptural features that can be perceived separately from and exist independently of utilitarian aspects. Decorative sculpture, toys, characters, or artistic surface relief may have more protectable expression than a purely functional bracket, but every design needs its own analysis.

### European Union and Member States

EU copyright doctrine is human-centered and originality depends on the author’s own intellectual creation, while ownership, employee works, moral rights, and registration/evidence mechanisms vary by Member State. Do not assume a provider’s contract can create statutory copyright where local law does not.

The EU design regime is especially relevant to 3D products. Current EU design reform expressly addresses digital design files and acts such as creating, downloading, copying, sharing, or distributing media/software recording a protected design for the purpose of enabling a product to be made. Treat digital-file distribution as a design-right event, not only a copyright event.

### United Kingdom and Other Computer-Generated-Work Rules

UK Copyright, Designs and Patents Act section 9(3) says that for a computer-generated literary, dramatic, musical, or artistic work, the author is the person making the arrangements necessary for creation; section 178 defines “computer-generated.” The scope and reform of this rule remain debated. Some other countries use related statutory approaches. Do not generalize a UK outcome worldwide.

### Practical Protection Strategy

Where copyright is weak or uncertain:

- protect appearance with timely registered design/design-patent filings;
- protect functional inventions with patent/utility-model filings before public disclosure;
- protect the product name and source identifier with trademark registration and consistent use;
- protect nonpublic parameters, processes, and manufacturing know-how as trade secrets;
- use a customer contract to restrict file access and redistribution where enforceable;
- preserve human-authorship evidence and creation dates;
- do not overclaim rights in AI-only, functional, public-domain, or third-party portions.

## 3. Functional Objects and Overlapping Rights

A single object can simultaneously involve:

- copyright in expressive geometry, relief, code, documentation, and renders;
- patents or utility models in functional principles;
- registered/unregistered designs or design patents in appearance;
- trademarks in names, logos, source-identifying shape, or packaging;
- trade dress and passing-off/unfair-competition law;
- database rights in a curated library;
- trade secrets and contractual confidentiality;
- semiconductor, mask-work, cultural-property, or sector-specific rights in rare cases.

Buying or lawfully owning a physical object does not normally grant a right to scan it, reconstruct it, distribute a CAD file, or manufacture copies. An exhaustion/first-sale defense concerns the particular authorized copy and varies by right and jurisdiction; do not use it as a manufacturing license.

Reverse engineering may be allowed for some purposes in some countries, restricted by contract or other rights in others, and does not eliminate patents, designs, trademarks, or safety obligations. Obtain counsel before commercial cloning or interoperable spare-part releases where legal exceptions are central.

## 4. Patent, Design, and Trademark Clearance

### Before Public Disclosure

Stop publication, marketplace uploads, crowdfunding, customer demos without confidentiality, and public repositories if patent, utility-model, or registered-design protection may matter. Novelty grace periods differ and many markets do not forgive the owner’s early disclosure.

### Search Process

Record:

- search date, market, database, query, classification, image search, and filters;
- relevant result IDs, owners, status, priority/filing dates, expiry, families, and legal-event source;
- claim/design comparison and why it is relevant;
- search limitations and the reviewer;
- counsel opinion reference when commissioned.

Use WIPO PATENTSCOPE, EUIPO DesignView/TMview and EU design search, USPTO Patent Center/search and Trademark Search, and relevant national databases. A search is not a freedom-to-operate opinion. Patent claims, design scope, validity, ownership, expiry, prosecution history, equivalents, and country coverage require expertise.

### Escalate When

- a commercial product resembles an existing product in overall impression;
- the design solves a known technical problem in a crowded field;
- the product is a replacement, compatible accessory, spare part, or reverse-engineered interface;
- a brand, logo, character, distinctive shape, or trade dress appears;
- search results are close, ownership/status is unclear, or expected revenue/liability is material.

## 5. People, Photos, Scans, and Confidential Information

Copyright permission in a photo is not permission to exploit:

- a person’s likeness, portrait, voice, name, biometric characteristics, or endorsement;
- art, sculpture, packaging, trademarks, or product designs depicted in the photo;
- architecture or cultural heritage where local limits apply;
- an object photographed under museum, event, employment, NDA, site-access, or platform restrictions;
- personal data for an incompatible purpose.

For identifiable people:

- identify a lawful basis for processing and the commercial use;
- obtain a model release/consent where appropriate, specifying AI input, 3D derivation, editing, advertising, markets, duration, revocation handling, and sublicensing;
- apply heightened review to children, sensitive contexts, biometric identification, medical data, or sexual content;
- minimize stored personal data and restrict access;
- do not publish releases or identity documents in the customer bundle.

Under the EU GDPR, an identifiable photo can be personal data. Article 6 requires a lawful basis, and Article 9 imposes additional controls on special-category data, including biometric data used for unique identification. Member-State portrait, personality, employment, and copyright rules may add duties.

For scans or photos supplied by a client, obtain a warranty and evidence schedule rather than relying only on a statement that “it is mine.” If provenance cannot be verified, BLOCK.

## 6. EU AI Transparency

### Date and Roles

EU AI Act Article 50 transparency duties apply from 2 August 2026. Distinguish:

- provider: develops an AI system/model or has it developed and places it on the market or puts it into service under its name/trademark;
- deployer: uses an AI system under its authority in a professional context;
- downstream seller: may be a deployer, but does not become a provider merely by selling an output.

### Provider Marking

Article 50(2) addresses providers of AI systems generating synthetic audio, image, video, or text. Outputs must be marked in a machine-readable format and detectable as artificially generated or manipulated, subject to specified exceptions. Commission guidance notes narrow exclusions, including certain standard editing/assistive uses and some closed-loop industrial/product-development nonfinal outputs.

A CAD solid, mesh, STL, or 3MF is not expressly listed as audio, image, video, or text. Do not announce a categorical EU statutory label duty for every AI-assisted 3D model unless current Commission guidance, national enforcement, or counsel supports it.

Generated concept art, texture images, renders, and listing images are “image” outputs. Preserve provider provenance and assess whether any deployer disclosure rule applies.

### Deployer Disclosure

Professional deployers must disclose:

- deepfake image, audio, or video content;
- AI-generated/manipulated text published to inform the public on matters of public interest, unless an exception applies.

The Commission’s current FAQ treats deepfakes broadly as manipulated/generated content resembling existing persons, objects, places, entities, or events that would falsely appear authentic or truthful. A photorealistic listing render depicting a nonexistent physical product can therefore deserve a visible, accessible disclosure, especially if a buyer could mistake it for a product photo.

Use clear nearby wording, such as:

- “AI-generated concept image; not a photograph of the delivered product.”
- “AI-assisted product render; geometry and printability were human reviewed.”

Do not hide disclosure only inside a metadata file. For artistic, satirical, fictional, or analogous works, adapt disclosure so it does not hamper the work, but still verify the statutory conditions.

### Conservative Product Statement

When AI materially influenced the sold geometry, include this truthful voluntary statement even if no specific CAD-label rule is found:

> AI-assisted design. Human-reviewed and engineered by [seller]. See the provenance manifest for roles, version, and source records.

Keep it in the listing, README/instructions, 3MF metadata, and sidecar manifest. Put a short release ID on the object. Do not engrave a long legal statement on a safety-critical surface.

### EU Code and Icons

The Commission’s Code of Practice on marking and labelling AI-generated content is a voluntary compliance tool; the legal duties remain mandatory. EU disclosure icons are optional unless a later rule or marketplace requires them. Re-check the guidance and code version at release.

## 7. Other AI-Transparency Markets

Build a target-country matrix rather than treating the EU rule as universal.

### China

China’s Measures for Labelling AI-Generated Synthetic Content and mandatory national standard GB 45438-2025 took effect on 1 September 2025. They focus on network information service providers and explicit/implicit labels for generated/synthetic text, image, audio, video, virtual scenes, and related services. Determine whether the seller, marketplace, hosted configurator, or local distributor is a covered service provider and whether “virtual scene” reaches the offered content. Do not strip platform/provider labels.

### South Korea

South Korea’s AI Basic Act and official transparency guidelines include duties concerning AI-generated or manipulated outputs and use a risk/role-sensitive framework. Verify the operative guidance, local sales channel, and content type before release.

### California and United States

California SB 942, operative from 1 January 2026, primarily regulates large covered generative-AI providers and their detection, manifest, and latent-disclosure capabilities for image, video, and audio content. It is not a blanket label statute for every small seller or 3D file. U.S. federal/state consumer-protection, publicity, election, impersonation, advertising, and platform rules can still apply to deceptive synthetic media.

### Release Rule

For every market, record:

- regulated content modality;
- actor/role threshold;
- disclosure or machine-marking duty;
- required wording, placement, accessibility, and language;
- metadata-retention duty;
- exemptions;
- effective date and official source;
- owner and counsel decision.

## 8. Contract and Consumer Law

### Digital Files

A download can be digital content. In EU consumer sales, Directive (EU) 2019/770 addresses conformity and remedies for digital content/services. The Consumer Rights Directive conditions loss of the withdrawal right for immediately supplied non-tangible digital content on prior express consent, acknowledgment of loss, and contract confirmation. A “no refunds on digital files” sentence is not a substitute.

Customer terms should define:

- licensed files, version, permitted users/seats, backup copies, and contractor access;
- personal/commercial print rights and any quantity/SKU limits;
- whether modification is allowed;
- prohibition on file/source redistribution, resale, sharing, sublicensing, or model extraction where enforceable;
- trademark rights and rules for identifying authorized prints;
- support, updates, compatibility, instructions, known limits, and prohibited high-risk uses;
- price, taxes, renewal if any, withdrawal/refund flow, conformity remedies, warranty, liability, indemnity where lawful, governing law, and dispute terms;
- privacy, analytics, account, and takedown contact;
- precedence of mandatory consumer law.

Have counsel adapt these terms. Do not promise rights unavailable due to third-party components or uncertain AI copyright.

### Physical Products

Sale of a print is not a grant of reproduction/file rights unless the contract says so. Conversely, retaining IP does not reduce product-safety or defect liability. Document product description, conformity, warnings, warranty, traceability, returns, incidents, and recalls independently.

### Marketplaces

Snapshot the marketplace’s seller terms, digital-file rules, prohibited content, AI disclosure, commercial-license fields, fee/tax roles, refund rules, product-safety contact fields, and takedown procedure. Platform acceptance does not clear the product.

## 9. Ownership and Contributor Chain

For every human or entity:

- identify employer/employee/contractor/client status and governing law;
- obtain a signed assignment or sufficiently broad exclusive/nonexclusive license;
- cover pre-existing materials and list them as background IP;
- cover copyright, designs, inventions, code, documentation, renders, moral-right consents/waivers where lawful, and further-assurance duties;
- require disclosure and license proof for third-party inputs;
- include confidentiality and patent/design filing cooperation;
- record compensation and signature authority.

Do not assume payment transfers IP. Do not assume employment produces the same default ownership in every country.

## 10. Release Escalation Rules

BLOCK and obtain specialist advice for:

- unknown or contradictory license/ownership evidence;
- NC material, an adapted ND work, or incompatible reciprocal terms;
- restricted supplier CAD embedded in a distributed file;
- copied brand/character/product appearance or an unconsented identifiable person;
- close patent/design search results or a planned filing;
- deepfake, political/public-interest, biometric, child, intimate, or deceptive synthetic content;
- safety-critical, regulated, or child-facing products;
- weapons, controlled technology, sanctioned destinations/end users;
- a product incident, infringement notice, takedown, regulator contact, or dispute;
- use spanning markets whose mandatory terms cannot be reconciled.

A named business owner may accept ordinary commercial uncertainty only after engineering, IP, privacy, and compliance owners document the basis. No one may override an explicit legal prohibition, missing required license, failed safety test, or export-control block.
