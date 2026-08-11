# Toolchain and Output Licenses

Last researched: 2026-08-10. Verify the installed version, plugins, cloud plan, and current official terms; a project register entry controls over this general guide.

## Contents

1. Tool-versus-output rule
2. Current core toolchain
3. AI and cloud services
4. Add-ons, libraries, and assets
5. Slicers, firmware, and manufacturing services
6. Adding a future tool
7. Distribution of tool code
8. Evidence and approval

## 1. Tool-Versus-Output Rule

Ask four separate questions:

1. May the business run this program/service under this exact plan?
2. Does the program/service claim or restrict rights in output?
3. Did the output copy or embed code, models, fonts, textures, templates, libraries, or other assets?
4. Is the business distributing the program, a modified program, plugin, macro, or linked library?

An open-source application license commonly governs the application and its redistribution, not ordinary user-created output. This is not universal. Bundled content, sample files, code generators, plugins, AI model licenses, cloud terms, and proprietary plans can create distinct output restrictions.

Record facts rather than saying “made with open source.”

## 2. Current Core Toolchain

### ChatGPT / OpenAI Image and Code Generation

Record:

- product/service and model/tool shown;
- workspace/account type and whether business terms apply;
- OpenAI terms effective date and official URL;
- prompt/input provenance and authorization;
- generated file, C2PA/SynthID state where supported, and SHA-256;
- human review, changes, and similarity search;
- third-party services invoked through the product and their terms.

Current EEA/Swiss/UK consumer terms assign output to the user as between the parties, require rights in input, warn that outputs may be non-unique, require human evaluation, and prohibit representing nonhuman output as human-generated. Business/API use can invoke separate services agreements and policies. Verify the terms applicable to the account, not whichever public page is most favorable.

Commercial permission from OpenAI does not:

- license a third party’s copyrighted or trademarked material in an output;
- establish statutory copyright;
- clear patents, designs, privacy, publicity, or product safety;
- transfer rights in external inputs;
- guarantee exclusivity or accuracy.

### OpenSCAD

OpenSCAD identifies itself as GPLv2 open-source software. Ordinary independently created model output is not made GPL merely because OpenSCAD rendered it. Audit:

- copied OpenSCAD modules and libraries;
- generated or vendored code;
- fonts and imported SVG/STL/DXF/height maps;
- whether OpenSCAD or modified binaries are redistributed;
- notices/source obligations for library code.

Keep the exact OpenSCAD version and build source. If the release includes an OpenSCAD source file that incorporates GPL code, analyze that source distribution separately from the resulting mesh.

### CadQuery

The official CadQuery project currently uses Apache License 2.0. Ordinary independently created geometry is not automatically Apache-licensed. Audit:

- copied Python/CadQuery libraries and examples;
- Python dependencies and generated documentation;
- imported models and fonts;
- retained copyright/NOTICE requirements if distributing code;
- Apache patent-license and termination provisions;
- standalone application packaging.

License Python source and geometry separately.

### FreeCAD

The official FreeCAD repository currently carries GNU LGPL terms. Ordinary user models are generally not thereby LGPL-licensed. Audit:

- workbenches, macros, Python modules, templates, icons, and examples;
- linked or embedded libraries;
- modified/distributed FreeCAD builds;
- imported proprietary CAD and translators;
- version-specific notices and license file.

Do not infer plugin compatibility from the FreeCAD application license.

### Blender

Blender is GPL-licensed, and Blender’s official FAQ states that artwork created with Blender is the creator’s property; commercial use of that artwork is allowed. Audit:

- add-ons/scripts and whether they are distributed;
- bundled or downloaded demo assets, HDRIs, textures, materials, brushes, fonts, rigs, and geometry nodes;
- render engine terms;
- external AI models or services;
- copied character meshes and marketplace assets;
- modified/distributed Blender builds.

The .blend file may contain embedded third-party data that an exported STL does not visibly reveal. Inventory the source file.

### File and Hardware Libraries

Record any OpenSCAD library, CadQuery helper, FreeCAD workbench, Blender add-on, font package, icon set, texture, material scan, fastener library, electronics footprint, or supplier CAD independently. Do not inherit the host tool’s license label.

## 3. AI and Cloud Services

For every AI or cloud service, review:

- acceptable-use and content policies;
- rights required in input;
- output ownership/license and non-uniqueness disclaimers;
- commercial plan restrictions;
- training/data-retention and confidentiality controls;
- region/data-transfer terms and subprocessors;
- prohibited regulated/high-impact or weapon uses;
- output provenance/labeling;
- indemnity eligibility and exclusions;
- third-party model/provider terms;
- account termination and post-termination output use.

Never upload supplier-confidential CAD, personal scans, export-controlled data, unpublished inventions, client IP, or trade secrets unless the agreement and security configuration authorize it.

If a locally run generative model is added, record:

- model weights license;
- code/runtime license;
- training-data statements and known restrictions;
- commercial/usage restrictions;
- output clauses;
- model version/hash;
- safety filters and provenance behavior.

A nominally open code license does not establish that model weights or training data have the same license.

## 4. Add-Ons, Libraries, and Assets

### High-Risk Labels

Block until reviewed:

- “personal use only”;
- “educational use”;
- “trial” or “evaluation”;
- “editorial use only”;
- “non-commercial”;
- “no derivatives”;
- “no redistribution”;
- “standard license” without the text;
- “free download”;
- an asset with no author/license;
- a marketplace license that permits rendered images but not 3D-printed merchandise;
- an asset license that prohibits use in another model/template or makes the asset extractable.

### Fonts

Check desktop use, web embedding, app embedding, editable embedding, logo/trademark use, product/merchandise use, and modification. Embossing glyph outlines into distributable geometry may be treated differently from rendering a text image.

### Textures and Height Maps

Check whether the license permits:

- physical merchandise;
- adaptation;
- use as a displacement/height field;
- redistribution when texture can be extracted from a source file;
- AI input;
- print-run and channel;
- attribution.

### Code and Macros

Use SPDX identifiers and preserve license/NOTICE files. Scan transitive dependencies. A snippet from a forum or AI response can reproduce licensed code; record origin and review distinctive blocks.

## 5. Slicers, Firmware, and Manufacturing Services

### Slicers

Record slicer name/version, profiles, plugins, post-processing scripts, output-format terms, and profile authors. Application licenses normally do not claim ordinary G-code, but a proprietary material/machine profile or copied start/end G-code can have separate terms.

Treat G-code as safety-relevant:

- verify target machine/firmware;
- inspect temperature, motion, tool-change, purge, fan, pause, and shutdown commands;
- do not sell generic G-code as universally safe;
- state exact machine/material/configuration;
- prefer selling model plus validated print profile unless fixed G-code is necessary.

### Firmware and Machine Files

If distributing firmware, configuration, macros, or machine definitions, audit those software licenses. A physical print does not require shipping firmware source merely because the printer firmware is GPL, but distribution of modified firmware can.

### Print Services and Marketplaces

Snapshot:

- ownership and license granted to the service;
- confidentiality and deletion;
- subcontractors and manufacturing region;
- prohibited content and regulated products;
- file retention/training;
- quality specifications and remedies;
- material traceability;
- liability allocation;
- marketplace AI and safety fields.

Do not rely on a print service’s acceptance as a conformity assessment.

## 6. Adding a Future Tool

Before using any new tool on a release:

1. Assign a unique tool ID and business owner.
2. Record official product name, vendor, version/build, installation source, and hash where practical.
3. Identify every governing document: software license, subscription/order form, terms, acceptable-use policy, content policy, privacy/DPA, model/asset terms, plugin terms.
4. Snapshot documents and record effective/retrieval dates.
5. Confirm commercial use for the business size, revenue, country, and use case.
6. Confirm input authorization and confidentiality.
7. Record output ownership/license, restrictions, provenance, and indemnity.
8. Inventory bundled assets and dependencies.
9. Determine obligations if code or a modified binary is distributed.
10. Review export, sanctions, privacy, security, and sector-use restrictions.
11. Run a representative output test for embedded metadata/assets.
12. Obtain tool-owner and IP/compliance approval.

Repeat this review on:

- major version or plan change;
- vendor acquisition or terms update;
- plugin/model change;
- new use category or target market;
- discovery of a security/license incident.

## 7. Distribution of Tool Code

When the product includes scripts, plugins, macros, a custom CAD application, or a modified tool:

- generate a software bill of materials;
- retain source/offers/notices required by reciprocal licenses;
- include attribution and LICENSES directory;
- verify dynamic/static linking and network-service clauses;
- verify patent clauses;
- separate proprietary credentials and data;
- run security and dependency-vulnerability review;
- license the software independently from geometry and docs.

Use SPDX expressions and documents when practicable. SPDX is ISO/IEC 5962:2021 and supports software, hardware, data, AI, and custom LicenseRef relationships.

## 8. Evidence and Approval

The tool register should include:

- tool ID;
- name/vendor/version/hash;
- purpose/design stage;
- application license;
- plan/tier;
- terms URLs and immutable snapshot paths;
- effective/retrieval date;
- commercial-use result;
- input confidentiality/AI rights;
- output restrictions;
- add-ons/assets/dependencies;
- distribution obligations;
- reviewer/date/status/notes.

Evidence hierarchy:

1. signed negotiated agreement/order form;
2. vendor’s official license/terms for exact version/plan;
3. official repository license at tagged release;
4. authenticated marketplace item license;
5. informal FAQ or community statement.

Resolve conflicts using counsel and contract precedence; do not silently choose the broadest statement.
