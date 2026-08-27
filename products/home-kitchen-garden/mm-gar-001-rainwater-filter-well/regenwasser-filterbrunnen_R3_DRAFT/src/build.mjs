import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import {
  exportSTEP,
  makeCompound,
  measureVolume,
  setOC,
} from "replicad";
import { initOpenCascadeForNode } from "./oc-loader.mjs";
import { P, assertParameters, derived } from "./parameters.mjs";
import { watermarkOutlineMetadata } from "./watermark.mjs";
import {
  buildBlindPortPlate,
  buildCascadeSpout,
  buildDrainFitCoupon,
  buildDrainSpigotFlange,
  buildHoseFitCoupon,
  buildLamellaCassette,
  buildMediaBasket,
  buildOutletHoseAdapter,
  buildSedimentFunnel,
  buildStage1Body,
  buildStage1InletDowncomer,
  buildStage1InletReceiver,
  buildStage2Body,
  buildStage2Diffuser,
  buildStage2DropTube,
  buildStage3Body,
  buildStage3Distributor,
  printOriented,
} from "./geometry.mjs";

const currentFile = fileURLToPath(import.meta.url);
const projectRoot = path.resolve(path.dirname(currentFile), "..");
const outputRoot = path.join(projectRoot, "build", "draft-r3");
const stepDir = path.join(outputRoot, "step");
const stlDir = path.join(outputRoot, "stl");
const previewDir = path.join(outputRoot, "preview");
const previewComponentDir = path.join(previewDir, "components");
const metadataDir = path.join(outputRoot, "metadata");
const checkOnly = process.argv.includes("--check-only");

const partDefinitions = [
  {
    key: "stage1_vortex_body",
    name: "Stufe 1 Wirbelgehaeuse",
    quantity: 1,
    builder: buildStage1Body,
    orientation: "as-designed",
    primary: true,
  },
  {
    key: "stage1_sediment_funnel",
    name: "Stufe 1 Schlammtrichter",
    quantity: 1,
    builder: buildSedimentFunnel,
    orientation: "funnel-inverted",
  },
  {
    key: "stage1_inlet_receiver",
    name: "Stufe 1 offener Einlaufbecher mit Schlauchhalter",
    quantity: 1,
    builder: buildStage1InletReceiver,
    orientation: "as-designed",
  },
  {
    key: "stage1_inlet_downcomer",
    name: "Stufe 1 Zulauf-Fallrohr mit Tangentialauslass",
    quantity: 1,
    builder: buildStage1InletDowncomer,
    orientation: "as-designed",
  },
  {
    key: "stage2_lamella_body",
    name: "Stufe 2 Lamellengehaeuse",
    quantity: 1,
    builder: buildStage2Body,
    orientation: "as-designed",
    primary: true,
  },
  {
    key: "stage2_lamella_cassette",
    name: "Stufe 2 Lamellenkassette",
    quantity: 1,
    builder: buildLamellaCassette,
    orientation: "lamella-side",
  },
  {
    key: "stage2_drop_tube",
    name: "Fallrohr zur Lamellenunterseite",
    quantity: 1,
    builder: buildStage2DropTube,
    orientation: "as-designed",
  },
  {
    key: "stage2_diffuser",
    name: "Stufe 2 Stroemungsdiffusor",
    quantity: 1,
    builder: buildStage2Diffuser,
    orientation: "as-designed",
  },
  {
    key: "stage3_media_body",
    name: "Stufe 3 Medienfiltergehaeuse",
    quantity: 1,
    builder: buildStage3Body,
    orientation: "as-designed",
    primary: true,
  },
  {
    key: "stage3_media_basket",
    name: "Stufe 3 Medienkorb",
    quantity: 3,
    builder: buildMediaBasket,
    orientation: "as-designed",
  },
  {
    key: "stage3_distributor",
    name: "Stufe 3 Verteilerplatte",
    quantity: 1,
    builder: buildStage3Distributor,
    orientation: "as-designed",
  },
  {
    key: "cascade_spout",
    name: "Kaskadenauslauf",
    quantity: 1,
    builder: buildCascadeSpout,
    orientation: "outlet-flange-bed",
  },
  {
    key: "outlet_hose_adapter_25",
    name: "Optionaler 25-mm-Auslaufadapter",
    quantity: 1,
    builder: buildOutletHoseAdapter,
    orientation: "outlet-flange-bed",
  },
  {
    key: "drain_spigot_flange_dn25",
    name: "DN25-Ablassstutzen mit Flansch",
    quantity: 2,
    builder: buildDrainSpigotFlange,
    orientation: "as-designed",
  },
  {
    key: "blind_port_plate",
    name: "Blinddeckel fuer Ablassflansch",
    quantity: 2,
    builder: buildBlindPortPlate,
    orientation: "as-designed",
  },
  {
    key: "hose_fit_coupon_25",
    name: "Passcoupon fuer 25-mm-Schlauch",
    quantity: 1,
    builder: buildHoseFitCoupon,
    orientation: "as-designed",
    coupon: true,
  },
  {
    key: "drain_fit_coupon_dn25",
    name: "Passcoupon fuer DN25-Ablassschlauch",
    quantity: 1,
    builder: buildDrainFitCoupon,
    orientation: "as-designed",
    coupon: true,
  },
];

async function writeBlob(filePath, blob) {
  const bytes = Buffer.from(await blob.arrayBuffer());
  fs.writeFileSync(filePath, bytes);
  return bytes.length;
}

function cleanBounds(bounds) {
  return bounds.map((point) => point.map((value) => Number(value.toFixed(4))));
}

function dimensionsFromBounds(bounds) {
  return bounds[0].map((value, index) => Number((bounds[1][index] - value).toFixed(4)));
}

function addAssemblyShape(list, shape, name, color, alpha = 1) {
  list.push({ shape, name, color, alpha });
}

function buildAssembly(partShapes) {
  const d = derived(P);
  const assembly = [];
  addAssemblyShape(assembly, partShapes.stage3_media_body.clone(), "Stufe 3 Gehaeuse", "#475569");
  addAssemblyShape(
    assembly,
    partShapes.stage2_lamella_body.clone().translateZ(d.stage2AssemblyZ),
    "Stufe 2 Gehaeuse",
    "#334155"
  );
  addAssemblyShape(
    assembly,
    partShapes.stage1_vortex_body.clone().translateZ(d.stage1AssemblyZ),
    "Stufe 1 Gehaeuse",
    "#1e293b"
  );
  addAssemblyShape(
    assembly,
    partShapes.stage1_sediment_funnel.clone().translateZ(d.stage1AssemblyZ),
    "Schlammtrichter",
    "#d97706"
  );
  addAssemblyShape(
    assembly,
    partShapes.stage1_inlet_receiver.clone().translateZ(d.stage1AssemblyZ),
    "Einlaufbecher",
    "#7dd3fc"
  );
  addAssemblyShape(
    assembly,
    partShapes.stage1_inlet_downcomer.clone().translateZ(d.stage1AssemblyZ),
    "Tangential-Fallrohr",
    "#0284c7"
  );
  addAssemblyShape(
    assembly,
    partShapes.stage2_lamella_cassette.clone().translateZ(d.stage2AssemblyZ),
    "Lamellenkassette",
    "#38bdf8"
  );
  addAssemblyShape(
    assembly,
    partShapes.stage2_drop_tube.clone().translateZ(d.stage2AssemblyZ + P.stage2.dropTubeBottomZ),
    "Fallrohr",
    "#0ea5e9"
  );
  addAssemblyShape(
    assembly,
    partShapes.stage2_diffuser.clone().translateZ(d.stage2AssemblyZ + P.stage2.diffuserSupportZ),
    "Diffusor",
    "#0284c7"
  );
  for (let i = 0; i < P.stage3.basketCount; i += 1) {
    addAssemblyShape(
      assembly,
      partShapes.stage3_media_basket.clone().translateZ(P.stage3.basketBottomZ + i * P.stage3.basketHeight),
      `Medienkorb ${i + 1}`,
      ["#f59e0b", "#22c55e", "#a855f7"][i]
    );
  }
  addAssemblyShape(
    assembly,
    partShapes.stage3_distributor.clone().translateZ(P.stage3.distributorZ),
    "Verteilerplatte",
    "#f8fafc"
  );
  addAssemblyShape(
    assembly,
    partShapes.cascade_spout.clone().translate(0, -163, 4),
    "Kaskadenauslauf",
    "#64748b"
  );
  return assembly;
}

async function run() {
  const derivedValues = assertParameters(P);
  const oc = await initOpenCascadeForNode();
  setOC(oc);

  if (!checkOnly) {
    for (const directory of [stepDir, stlDir, previewDir, previewComponentDir, metadataDir]) {
      fs.mkdirSync(directory, { recursive: true });
    }
  }

  const partShapes = {};
  const metadata = {
    project: P.meta,
    generatedAt: new Date().toISOString(),
    cadKernel: "OpenCascade via replicad 0.23.1 / replicad-opencascadejs 0.23.0",
    parameters: P,
    derived: derivedValues,
    parts: [],
  };

  for (const definition of partDefinitions) {
    const shape = definition.builder(P);
    partShapes[definition.key] = shape;
    const designBounds = cleanBounds(shape.boundingBox.bounds);
    const oriented = printOriented(shape, definition.orientation);
    const printBounds = cleanBounds(oriented.boundingBox.bounds);
    const volumeMm3 = Number(measureVolume(shape).toFixed(2));
    const massEstimateG = Number((volumeMm3 * 0.00127).toFixed(1));
    const entry = {
      key: definition.key,
      name: definition.name,
      quantity: definition.quantity,
      primary: Boolean(definition.primary),
      coupon: Boolean(definition.coupon),
      designBoundsMm: designBounds,
      designDimensionsMm: dimensionsFromBounds(designBounds),
      printBoundsMm: printBounds,
      printDimensionsMm: dimensionsFromBounds(printBounds),
      printOrientation: definition.orientation,
      faces: shape.faces.length,
      volumeMm3,
      massEstimatePETGG: massEstimateG,
      watermarkIncluded: Boolean(definition.primary && P.watermark.enabled),
    };

    if (!checkOnly) {
      const stem = `DRAFT_R3_${definition.key}`;
      entry.step = path.relative(projectRoot, path.join(stepDir, `${stem}.step`));
      entry.stl = path.relative(projectRoot, path.join(stlDir, `${stem}.stl`));
      entry.stepBytes = await writeBlob(
        path.join(projectRoot, entry.step),
        exportSTEP([{ shape, name: definition.name }], { unit: "mm", modelUnit: "mm" })
      );
      entry.stlBytes = await writeBlob(
        path.join(projectRoot, entry.stl),
        oriented.blobSTL({
          tolerance: P.process.stlLinearTolerance,
          angularTolerance: P.process.stlAngularTolerance,
          binary: true,
        })
      );
    }
    metadata.parts.push(entry);
  }

  const assemblyShapes = buildAssembly(partShapes);
  metadata.assembly = {
    bodyDiameterMm: P.common.bodyOD,
    baseDiameterMm: P.stage3.baseFlangeOD,
    heightMm: derivedValues.assembledHeight,
    installedFootprintWithCascadeMm: [330, 406],
    componentCount: assemblyShapes.length,
  };
  metadata.watermark = P.watermark.enabled
    ? {
        ...P.watermark,
        ...watermarkOutlineMetadata(P),
        markedPrimaryParts: metadata.parts
          .filter((part) => part.watermarkIncluded)
          .map((part) => part.key),
      }
    : { enabled: false };

  if (!checkOnly) {
    const assemblyStepPath = path.join(stepDir, "DRAFT_R3_filterbrunnen_assembly.step");
    await writeBlob(
      assemblyStepPath,
      exportSTEP(assemblyShapes, { unit: "mm", modelUnit: "mm" })
    );
    metadata.assembly.step = path.relative(projectRoot, assemblyStepPath);

    metadata.assembly.components = [];
    for (let index = 0; index < assemblyShapes.length; index += 1) {
      const item = assemblyShapes[index];
      const slug = item.name
        .toLowerCase()
        .normalize("NFKD")
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/(^-|-$)/g, "");
      const componentPath = path.join(
        previewComponentDir,
        `${String(index + 1).padStart(2, "0")}_${slug}.stl`
      );
      await writeBlob(
        componentPath,
        item.shape.blobSTL({ tolerance: 0.45, angularTolerance: 0.5, binary: true })
      );
      metadata.assembly.components.push({
        name: item.name,
        color: item.color,
        alpha: item.alpha,
        path: path.relative(projectRoot, componentPath),
      });
    }

    const compound = makeCompound(assemblyShapes.map((item) => item.shape));
    const previewStlPath = path.join(previewDir, "DRAFT_R3_filterbrunnen_assembly_preview.stl");
    await writeBlob(
      previewStlPath,
      compound.blobSTL({
        tolerance: 0.35,
        angularTolerance: 0.45,
        binary: true,
      })
    );
    metadata.assembly.previewStl = path.relative(projectRoot, previewStlPath);

    const metadataPath = path.join(metadataDir, "geometry-metadata.json");
    fs.writeFileSync(metadataPath, `${JSON.stringify(metadata, null, 2)}\n`, "utf8");

    const generatedFiles = [];
    function filesRecursively(directory) {
      return fs.readdirSync(directory, { withFileTypes: true })
        .sort((left, right) => left.name.localeCompare(right.name))
        .flatMap((entry) => {
          const entryPath = path.join(directory, entry.name);
          return entry.isDirectory() ? filesRecursively(entryPath) : [entryPath];
        });
    }
    for (const directory of [stepDir, stlDir, previewDir]) {
      for (const filePath of filesRecursively(directory)) {
        const bytes = fs.readFileSync(filePath);
        generatedFiles.push({
          path: path.relative(projectRoot, filePath),
          bytes: bytes.length,
          sha256: crypto.createHash("sha256").update(bytes).digest("hex"),
        });
      }
    }
    const metadataBytes = fs.readFileSync(metadataPath);
    generatedFiles.push({
      path: path.relative(projectRoot, metadataPath),
      bytes: metadataBytes.length,
      sha256: crypto.createHash("sha256").update(metadataBytes).digest("hex"),
    });
    generatedFiles.sort((left, right) => left.path.localeCompare(right.path));
    fs.writeFileSync(
      path.join(metadataDir, "build-manifest.json"),
      `${JSON.stringify({ generatedAt: metadata.generatedAt, files: generatedFiles }, null, 2)}\n`,
      "utf8"
    );
  }

  console.log(JSON.stringify({
    status: "ok",
    checkOnly,
    parts: metadata.parts.length,
    assemblyComponents: metadata.assembly.componentCount,
    assembledHeightMm: metadata.assembly.heightMm,
    outputRoot: checkOnly ? null : outputRoot,
  }));
  process.exit(0);
}

run().catch((error) => {
  console.error(`BUILD_ERROR: ${error.message}`);
  process.exitCode = 1;
});
