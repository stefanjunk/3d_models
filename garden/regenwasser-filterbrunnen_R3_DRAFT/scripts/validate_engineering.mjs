#!/usr/bin/env node
/** Revision-3 interface and hydraulic plausibility checks. */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { P, assertParameters, derived } from "../src/parameters.mjs";

const currentFile = fileURLToPath(import.meta.url);
const projectRoot = path.resolve(path.dirname(currentFile), "..");
const metadataPath = path.resolve(
  projectRoot,
  process.argv[2] ?? "build/draft-r3/metadata/geometry-metadata.json"
);
const jsonPath = path.resolve(
  projectRoot,
  process.argv[3] ?? "build/draft-r3/metadata/engineering-validation.json"
);
const markdownPath = path.resolve(
  projectRoot,
  process.argv[4] ?? "build/draft-r3/metadata/engineering-validation.md"
);

const metadata = JSON.parse(fs.readFileSync(metadataPath, "utf8"));
const d = assertParameters(P);
const gravity = 9.80665;
const dischargeCoefficient = 0.62;

function round(value, digits = 2) {
  return Number(value.toFixed(digits));
}

function requiredHeadMm(flowLph, diameterMm, coefficient = dischargeCoefficient) {
  if (flowLph === 0) return 0;
  const flowM3s = flowLph / 3_600_000;
  const areaM2 = Math.PI * Math.pow(diameterMm / 2000, 2);
  return (Math.pow(flowM3s / (coefficient * areaM2), 2) / (2 * gravity)) * 1000;
}

function floorHeightAtX(xMm) {
  const low = P.stage2.sedimentFloorLowZ;
  const high = P.stage2.sedimentFloorHighZ;
  const radius = P.stage2.sedimentFloorRadius;
  return low + ((xMm + radius) / (2 * radius)) * (high - low);
}

const part = (key) => {
  const found = metadata.parts.find((candidate) => candidate.key === key);
  if (!found) throw new Error(`Missing metadata for ${key}`);
  return found;
};

const cassette = part("stage2_lamella_cassette");
const cassetteMinZ = cassette.designBoundsMm[0][2];
const cassetteMaxAbsX = Math.max(
  Math.abs(cassette.designBoundsMm[0][0]),
  Math.abs(cassette.designBoundsMm[1][0])
);
const floorBelowCassetteMaxZ = floorHeightAtX(cassetteMaxAbsX);

const stage1MaximumWaterZ = 219.5;
const nozzleHeadAtMaximumFlow = requiredHeadMm(
  P.hydraulics.maximumFlowLph,
  P.stage1.inletNozzleID
);
const predictedReceiverLevelAtMaximumFlow = stage1MaximumWaterZ + nozzleHeadAtMaximumFlow;
const receiverOverflowMargin = P.stage1.receiverOverflowZ - predictedReceiverLevelAtMaximumFlow;
const floorSlopeDeg =
  (Math.atan2(
    P.stage2.sedimentFloorHighZ - P.stage2.sedimentFloorLowZ,
    2 * P.stage2.sedimentFloorRadius
  ) *
    180) /
  Math.PI;

const checks = [
  {
    id: "flow-minimum",
    description: "Kein hydraulischer Mindestdurchfluss",
    actual: P.hydraulics.minimumFlowLph,
    criterion: "= 0 L/h",
    pass: P.hydraulics.minimumFlowLph === 0,
  },
  {
    id: "inlet-air-gap",
    description: "Freier Luftspalt Schlauchkante bis Becherrand",
    actual: round(P.stage1.hoseEndReferenceZ - P.stage1.receiverOverflowZ),
    unit: "mm",
    criterion: ">= 15 mm",
    pass: P.stage1.hoseEndReferenceZ - P.stage1.receiverOverflowZ >= 15,
  },
  {
    id: "receiver-downcomer-fit",
    description: "Diametrales Montagespiel Becher/Fallrohr",
    actual: round(P.stage1.receiverSocketID - P.stage1.inletDowncomerOD),
    unit: "mm",
    criterion: ">= 1.2 mm",
    pass: P.stage1.receiverSocketID - P.stage1.inletDowncomerOD >= 1.2,
  },
  {
    id: "nozzle-submergence",
    description: "Statische Ueberdeckung der 28-mm-Auslasskrone",
    actual: round(
      P.stage1.standpipeWeirZ -
        (P.stage1.inletNozzleAxisZ + P.stage1.inletNozzleID / 2)
    ),
    unit: "mm",
    criterion: ">= 40 mm",
    pass:
      P.stage1.standpipeWeirZ -
        (P.stage1.inletNozzleAxisZ + P.stage1.inletNozzleID / 2) >=
      40,
  },
  {
    id: "receiver-capacity",
    description: "Analytische Reserve bis Becher-Notueberlauf bei 1200 L/h",
    actual: round(receiverOverflowMargin),
    unit: "mm",
    criterion: ">= 5 mm",
    pass: receiverOverflowMargin >= 5,
    note: `Cd=${dischargeCoefficient}; erforderliche Differenzhoehe ${round(nozzleHeadAtMaximumFlow)} mm`,
  },
  {
    id: "stage1-sludge-gap",
    description: "Freier radialer Schlammweg am Trichter",
    actual: round(P.stage1.sedimentFunnelInnerRadius - P.stage1.standpipeOD / 2),
    unit: "mm",
    criterion: ">= 10 mm",
    pass: P.stage1.sedimentFunnelInnerRadius - P.stage1.standpipeOD / 2 >= 10,
  },
  {
    id: "stage1-drain",
    description: "Freier Ablassquerschnitt Stufe 1",
    actual: P.stage1.drainPassageID,
    unit: "mm",
    criterion: ">= 25 mm",
    pass: P.stage1.drainPassageID >= 25,
  },
  {
    id: "stage2-floor-slope",
    description: "Neigung Sedimentsammelboden Stufe 2",
    actual: round(floorSlopeDeg),
    unit: "deg",
    criterion: ">= 5 deg",
    pass: floorSlopeDeg >= 5,
  },
  {
    id: "stage2-lamella-clearance",
    description: "Konservativer Vertikalabstand Boden/Lamellenkassette",
    actual: round(cassetteMinZ - floorBelowCassetteMaxZ),
    unit: "mm",
    criterion: ">= 15 mm",
    pass: cassetteMinZ - floorBelowCassetteMaxZ >= 15,
    note: `Kassetten-Min-Z ${round(cassetteMinZ)} mm; Boden bei |X|=${round(cassetteMaxAbsX)} mm: ${round(floorBelowCassetteMaxZ)} mm`,
  },
  {
    id: "stage2-drain",
    description: "Freier Ablassquerschnitt Stufe 2",
    actual: P.stage2.drainPassageID,
    unit: "mm",
    criterion: ">= 25 mm",
    pass: P.stage2.drainPassageID >= 25,
  },
  {
    id: "assembly-height",
    description: "Montierte Gesamthoehe einschliesslich Schlauchhalter",
    actual: d.assembledHeight,
    unit: "mm",
    criterion: "<= 1000 mm",
    pass: d.assembledHeight <= 1000,
  },
];

const result = {
  project: P.meta,
  generatedAt: new Date().toISOString(),
  method: "parametric-interface-and-analytical-hydraulic-check",
  assumptions: {
    stage1MaximumWaterZMm: stage1MaximumWaterZ,
    dischargeCoefficient,
    note: "Analytische Plausibilisierung; kein Ersatz fuer Nass-, Schlamm- oder Langzeittest.",
  },
  calculations: {
    nozzleHeadAt1200LphMm: round(nozzleHeadAtMaximumFlow),
    receiverLevelAt1200LphMm: round(predictedReceiverLevelAtMaximumFlow),
    receiverOverflowMarginMm: round(receiverOverflowMargin),
    downcomerHeadAt1200LphMm: round(
      requiredHeadMm(P.hydraulics.maximumFlowLph, P.stage1.inletDowncomerID)
    ),
    stage2FloorSlopeDeg: round(floorSlopeDeg),
    stage2LamellaVerticalClearanceMm: round(cassetteMinZ - floorBelowCassetteMaxZ),
  },
  checks,
  overall: checks.every((check) => check.pass) ? "PASS" : "FAIL",
};

fs.mkdirSync(path.dirname(jsonPath), { recursive: true });
fs.writeFileSync(jsonPath, `${JSON.stringify(result, null, 2)}\n`, "utf8");

const rows = checks.map((check) => {
  const actual = `${check.actual}${check.unit ? ` ${check.unit}` : ""}`;
  const note = check.note ? check.note.replaceAll("|", "/") : "";
  return `| ${check.pass ? "PASS" : "FAIL"} | ${check.description} | ${actual} | ${check.criterion} | ${note} |`;
});
const markdown = `# Engineering-Pruefung · Revision 3 DRAFT

Gesamtergebnis: **${result.overall}**

| Status | Pruefung | Ist | Kriterium | Hinweis |
|---|---|---:|---:|---|
${rows.join("\n")}

Die hydraulische Kapazitaetsrechnung verwendet \(C_d=${dischargeCoefficient}\) und ist eine konservative analytische Plausibilisierung. Sie ersetzt nicht den Nasslauf bei 1.200 L/h, den Blockadeversuch des Fallrohrs oder die Schlamm-Spuelpruefung.
`;
fs.writeFileSync(markdownPath, markdown, "utf8");

console.log(JSON.stringify({ overall: result.overall, checks: checks.length, jsonPath, markdownPath }));
if (result.overall !== "PASS") process.exitCode = 1;
