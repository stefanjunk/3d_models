import { makeBox, measureVolume, setOC } from "replicad";
import { initOpenCascadeForNode } from "./oc-loader.mjs";
import {
  buildBlindPortPlate,
  buildCascadeSpout,
  buildHoseBarbFlange,
  buildHoseFitCoupon,
  buildLamellaCassette,
  buildMediaBasket,
  buildOutletHoseAdapter,
  buildSedimentFunnel,
  buildStage1Body,
  buildStage2Body,
  buildStage2Diffuser,
  buildStage2DropTube,
  buildStage3Body,
  buildStage3Distributor,
  makeFrustum,
} from "./geometry.mjs";

try {
  const oc = await initOpenCascadeForNode();
  setOC(oc);

  const shape = makeBox([0, 0, 0], [10, 20, 30]);
  const frustum = makeFrustum(8, 12, 20);
  const builders = {
    stage1: buildStage1Body,
    funnel: buildSedimentFunnel,
    stage2: buildStage2Body,
    lamella: buildLamellaCassette,
    dropTube: buildStage2DropTube,
    diffuser: buildStage2Diffuser,
    stage3: buildStage3Body,
    basket: buildMediaBasket,
    distributor: buildStage3Distributor,
    cascade: buildCascadeSpout,
    hoseOutlet: buildOutletHoseAdapter,
    hoseBarb: buildHoseBarbFlange,
    blind: buildBlindPortPlate,
    coupon: buildHoseFitCoupon,
  };
  const parts = {};
  for (const [name, builder] of Object.entries(builders)) {
    const part = builder();
    parts[name] = {
      bounds: part.boundingBox.bounds,
      faces: part.faces.length,
      volumeMm3: Math.round(measureVolume(part)),
    };
  }
  console.log(JSON.stringify({
    box: shape.boundingBox.bounds,
    frustum: frustum.boundingBox.bounds,
    parts,
  }));
} catch (error) {
  console.error(`PROBE_ERROR: ${error.message}`);
  process.exitCode = 1;
}
