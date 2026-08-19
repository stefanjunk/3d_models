export const P = Object.freeze({
  meta: {
    project: "Regenwasser-Filterbrunnen fuer Pool",
    revision: 3,
    units: "mm",
    status: "DRAFT",
  },
  printer: {
    model: "Anycubic Kobra 3 Max",
    build: [420, 420, 500],
    edgeReserve: 5,
  },
  process: {
    material: "UV-stabilisiertes PETG",
    nozzle: 0.6,
    layerHeight: 0.28,
    nominalLineWidth: 0.66,
    waterWall: 4.8,
    minimumWall: 3.6,
    stlLinearTolerance: 0.12,
    stlAngularTolerance: 0.25,
  },
  hydraulics: {
    minimumFlowLph: 0,
    designFlowLph: 800,
    maximumFlowLph: 1200,
    maximumStaticHeadM: 1.2,
    hoseNominalID: 25,
  },
  common: {
    bodyOD: 300,
    bodyHeight: 280,
    bodyWall: 4.8,
    baseThickness: 6.0,
    nestedFootOD: 287,
    nestedOverlap: 12,
    topRimThickness: 8.4,
    lockAnglesDeg: [30, 150, 270],
    lockPadRadius: 11.5,
    lockPadCenterRadius: 149,
    lockPadHeight: 8,
    lockHoleDiameter: 6.4,
    assemblyClearanceRadial: 1.7,
  },
  stage1: {
    standpipeOD: 50,
    standpipeID: 40,
    standpipeWeirZ: 210,
    receiverCenterX: 105,
    receiverOuterRadius: 28,
    receiverInnerRadius: 24,
    receiverBottomZ: 228,
    receiverOverflowZ: 268,
    receiverSupportZ: 262,
    receiverSupportOuterRadius: 139,
    receiverSupportInnerRadius: 122,
    receiverSocketOD: 46,
    receiverSocketID: 41,
    receiverSocketBottomZ: 212,
    hoseGuideBottomZ: 264,
    hoseGuideTopZ: 315,
    hoseGuidePostOffsetY: 28,
    hoseGuidePostWidthX: 12,
    hoseGuidePostWidthY: 8,
    hoseEndReferenceZ: 283,
    inletDowncomerOD: 39.2,
    inletDowncomerID: 32,
    inletDowncomerTopZ: 234,
    inletDowncomerBottomZ: 137,
    inletNozzleAxisZ: 155,
    inletNozzleOD: 35.2,
    inletNozzleID: 28,
    inletNozzleStartY: -8,
    inletNozzleLength: 80,
    receiverPadRadius: 139,
    receiverPadZ: 258,
    receiverPadHeight: 5,
    sedimentFunnelOuterRadius: 138,
    sedimentFunnelInnerRadius: 35,
    sedimentFunnelBottomZ: 19,
    sedimentFunnelTopZ: 74,
    sedimentFunnelThicknessZ: 3.2,
    drainAxisZ: 18.5,
    drainPassageID: 25,
    drainTubeOD: 35,
    drainFlangeWidth: 60,
    drainFlangeHeight: 52,
  },
  stage2: {
    overflowStandpipeCenterRadius: 114,
    overflowStandpipeAngleDeg: 240,
    overflowStandpipeOD: 48,
    overflowStandpipeID: 40,
    overflowWeirZ: 230,
    dropTubeOD: 39.2,
    dropTubeID: 32,
    dropTubeBottomZ: 50,
    dropTubeTopZ: 274,
    lamellaPlateCount: 12,
    lamellaPlateWidth: 200,
    lamellaPlateLength: 120,
    lamellaPlateThickness: 2.4,
    lamellaGapNormal: 12,
    lamellaAngleDeg: 60,
    lamellaPackCenterZ: 151,
    lamellaRailThickness: 5,
    sedimentFloorLowZ: 18.5,
    sedimentFloorHighZ: 44.0,
    sedimentFloorRadius: 145.25,
    diffuserSupportZ: 45,
    drainAxisZ: 18.5,
    drainPassageID: 25,
    drainTubeOD: 35,
    drainFlangeWidth: 60,
    drainFlangeHeight: 52,
  },
  stage3: {
    baseFlangeOD: 330,
    basketBodyOD: 252,
    basketGuideOD: 287.2,
    basketHeight: 52,
    basketCount: 3,
    basketBottomZ: 40,
    basketWall: 4.8,
    mediaDiscDiameter: 242,
    distributorZ: 220,
    overflowWeirZ: 245,
    overflowWidth: 80,
    outletSlotWidth: 100,
    outletSlotHeight: 28,
    outletSlotBottomZ: 12,
    outletFlangeWidth: 140,
    outletFlangeHeight: 62,
    cascadeLength: 78,
    cascadeWidth: 120,
  },
  hardware: {
    moduleJointBolt: "M6 x 25 A2-70, washer and nyloc nut",
    moduleJointCount: 6,
    outletBolt: "M5 x 25 A2-70, washer and nyloc nut",
    outletBoltCount: 4,
    portBolt: "M5 x 20 A2-70, washer and nyloc nut",
    portBoltCountPerFlange: 4,
    drainValve: "DN25 / 1-inch full-port valve, corrosion resistant",
  },
  watermark: {
    enabled: true,
    assetId: "JSI-WM-001-R1",
    profile: "compact",
    depth: 0.4,
    uniformScale: 1.5,
    position: [65, 45],
    rotationDeg: 0,
    mirrorX: true,
    nominalEnvelope: [11.4232449531, 10],
    actualEnvelope: [17.1348674297, 15],
    safeRectangle: [70, 22],
    surface: "print-bed-facing underside",
    hostWallBefore: 6.0,
    hostWallAfter: 5.6,
  },
});

export function derived(p = P) {
  const outerR = p.common.bodyOD / 2;
  const innerR = outerR - p.common.bodyWall;
  const footR = p.common.nestedFootOD / 2;
  const footInnerR = footR - p.common.bodyWall;
  const stage2OutletAngle = (p.stage2.overflowStandpipeAngleDeg * Math.PI) / 180;
  const stage2OutletCenter = [
    p.stage2.overflowStandpipeCenterRadius * Math.cos(stage2OutletAngle),
    p.stage2.overflowStandpipeCenterRadius * Math.sin(stage2OutletAngle),
  ];
  const stage2AssemblyZ = p.common.bodyHeight - p.common.nestedOverlap;
  const stage1AssemblyZ = stage2AssemblyZ * 2;
  const bodyStackHeight = stage1AssemblyZ + p.common.bodyHeight;
  const assembledHeight = stage1AssemblyZ + Math.max(p.common.bodyHeight, p.stage1.hoseGuideTopZ);

  return {
    outerR,
    innerR,
    footR,
    footInnerR,
    stage2OutletCenter,
    stage2AssemblyZ,
    stage1AssemblyZ,
    bodyStackHeight,
    assembledHeight,
  };
}

export function assertParameters(p = P) {
  const d = derived(p);
  const failures = [];
  const require = (condition, message) => {
    if (!condition) failures.push(message);
  };

  require(p.common.bodyWall >= p.process.minimumWall, "body wall below minimum wall");
  require(p.common.bodyWall >= 7 * p.process.nominalLineWidth, "water wall should provide at least seven nominal lines");
  require(p.common.baseThickness >= p.common.bodyWall, "base must not be thinner than the water wall");
  require(d.innerR - d.footR >= p.common.assemblyClearanceRadial - 0.05, "nested radial clearance is too small");
  require(p.stage1.standpipeID >= 36, "stage 1 gravity standpipe is undersized");
  require(p.hydraulics.minimumFlowLph === 0, "revision 3 requires zero minimum flow");
  require(p.stage1.receiverOverflowZ < p.common.bodyHeight, "receiver overflow must spill into stage 1");
  require(p.stage1.hoseEndReferenceZ - p.stage1.receiverOverflowZ >= 15, "inlet air gap below 15 mm");
  require(
    p.stage1.receiverSocketID - p.stage1.inletDowncomerOD >= 1.2,
    "receiver/downcomer diametral clearance below 1.2 mm"
  );
  require(
    p.stage1.standpipeWeirZ - (p.stage1.inletNozzleAxisZ + p.stage1.inletNozzleID / 2) >= 40,
    "submerged inlet nozzle crown has less than 40 mm static cover"
  );
  require(
    p.stage1.sedimentFunnelInnerRadius - p.stage1.standpipeOD / 2 >= 10,
    "stage 1 annular sludge gap below 10 mm"
  );
  require(p.stage1.drainPassageID >= 25, "stage 1 drain clear diameter below 25 mm");
  require(p.stage2.overflowStandpipeID >= 36, "stage 2 gravity standpipe is undersized");
  require(p.stage2.drainPassageID >= 25, "stage 2 drain clear diameter below 25 mm");
  require(
    Math.atan2(p.stage2.sedimentFloorHighZ - p.stage2.sedimentFloorLowZ, 2 * d.innerR) * 180 / Math.PI >= 5,
    "stage 2 sediment floor slope below 5 degrees"
  );
  require(p.stage2.lamellaPlateCount >= 8, "lamella count below functional minimum");
  require(p.stage2.lamellaPlateThickness >= 4 * p.process.nozzle, "lamella plates require at least four nozzle widths");
  require(p.stage3.basketCount === 3, "approved media sequence requires exactly three baskets");
  require(p.stage3.baseFlangeOD <= p.printer.build[0] - 2 * p.printer.edgeReserve, "base flange exceeds build area reserve");
  require(p.common.bodyHeight <= p.printer.build[2] - 2 * p.printer.edgeReserve, "module height exceeds build height reserve");
  require(d.assembledHeight <= 1000, "assembled height exceeds approved maximum");
  require(p.watermark.depth >= 0.2 && p.watermark.depth <= 0.8, "watermark recess depth outside approved range");
  require(p.watermark.uniformScale >= 1.0, "watermark must not be scaled below the approved profile");
  require(p.watermark.hostWallAfter >= Math.max(1.2, p.watermark.depth + 2 * p.process.nozzle), "watermark residual wall below process-safe minimum");

  if (failures.length) {
    throw new Error(`Invalid parameters:\n- ${failures.join("\n- ")}`);
  }
  return d;
}
