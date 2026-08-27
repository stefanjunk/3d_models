import {
  Sketcher,
  makeBox,
  makeCylinder,
} from "replicad";
import { P, assertParameters, derived } from "./parameters.mjs";
import { applyUndersideWatermark } from "./watermark.mjs";

const EPS = 0.2;

export const deg = (angle) => (angle * Math.PI) / 180;

function fuseAll(shapes) {
  if (!shapes.length) throw new Error("fuseAll requires at least one shape");
  return shapes.slice(1).reduce((result, shape) => result.fuse(shape), shapes[0]);
}

function cutAll(shape, cutters) {
  return cutters.reduce((result, cutter) => result.cut(cutter), shape);
}

export function makeFrustum(radiusBottom, radiusTop, height, zBottom = 0) {
  if (height <= 0 || radiusBottom <= 0 || radiusTop <= 0) {
    throw new Error("Frustum dimensions must be positive");
  }
  return new Sketcher("XZ")
    .movePointerTo([0, zBottom])
    .lineTo([radiusBottom, zBottom])
    .lineTo([radiusTop, zBottom + height])
    .lineTo([0, zBottom + height])
    .close()
    .revolve([0, 0, 1]);
}

export function makeRevolvedProfile(points) {
  if (points.length < 3) throw new Error("Revolved profile needs three points");
  let sketch = new Sketcher("XZ").movePointerTo(points[0]);
  for (const point of points.slice(1)) sketch = sketch.lineTo(point);
  return sketch.close().revolve([0, 0, 1]);
}

export function makeRing(outerRadius, innerRadius, height, z = 0) {
  if (!(outerRadius > innerRadius && innerRadius >= 0 && height > 0)) {
    throw new Error("Invalid ring dimensions");
  }
  const outer = makeCylinder(outerRadius, height, [0, 0, z]);
  if (innerRadius === 0) return outer;
  return outer.cut(makeCylinder(innerRadius, height + 2 * EPS, [0, 0, z - EPS]));
}

function polarPoint(radius, angleDeg) {
  const a = deg(angleDeg);
  return [radius * Math.cos(a), radius * Math.sin(a)];
}

function rotatedBox(x0, x1, y0, y1, z0, z1, angleDeg, center = [0, 0, 0], axis = [0, 0, 1]) {
  return makeBox([x0, y0, z0], [x1, y1, z1]).rotate(angleDeg, center, axis);
}

function addModuleLockGeometry(body, { topReceivers = false, lowerTabs = false } = {}, p = P) {
  const c = p.common;
  const padSolids = [];
  const holeCutters = [];

  for (const angle of c.lockAnglesDeg) {
    const [cx, cy] = polarPoint(c.lockPadCenterRadius, angle);
    if (topReceivers) {
      const receiverZ = c.bodyHeight - c.lockPadHeight - 0.4;
      padSolids.push(
        makeCylinder(c.lockPadRadius, c.lockPadHeight + 0.4, [cx, cy, receiverZ])
      );
      holeCutters.push(
        makeCylinder(c.lockHoleDiameter / 2, c.lockPadHeight + 0.8, [cx, cy, receiverZ - EPS])
      );
    }
    if (lowerTabs) {
      const support = makeFrustum(6.0, c.lockPadRadius, c.nestedOverlap, 0).translate(cx, cy, 0);
      const pad = makeCylinder(c.lockPadRadius, c.lockPadHeight, [cx, cy, c.nestedOverlap]);
      padSolids.push(support, pad);
      holeCutters.push(
        makeCylinder(c.lockHoleDiameter / 2, c.nestedOverlap + c.lockPadHeight + 2 * EPS, [cx, cy, -EPS])
      );
    }
  }

  const withPads = padSolids.length ? body.fuse(fuseAll(padSolids)) : body;
  return holeCutters.length ? cutAll(withPads, holeCutters) : withPads;
}

function addTopRim(body, p = P) {
  const d = derived(p);
  const c = p.common;
  const reinforcementInnerR = d.outerR - c.topRimThickness;
  return body.fuse(
    makeRing(d.outerR + 0.01, reinforcementInnerR, 10, c.bodyHeight - 10)
  );
}

function makeBaseCup({ nestedFoot, baseFlangeOD = null, topReceivers, lowerTabs }, p = P) {
  const d = derived(p);
  const c = p.common;
  let outer;
  let cavityCutters;
  let innerAtBase;

  if (nestedFoot) {
    const lowerOuter = makeFrustum(d.footR, d.outerR, c.nestedOverlap, 0);
    const upperOuter = makeCylinder(d.outerR, c.bodyHeight - c.nestedOverlap, [0, 0, c.nestedOverlap - EPS]);
    outer = lowerOuter.fuse(upperOuter);

    const interpolation = c.baseThickness / c.nestedOverlap;
    innerAtBase = d.footInnerR + (d.innerR - d.footInnerR) * interpolation;
    const innerLower = makeFrustum(
      innerAtBase,
      d.innerR,
      c.nestedOverlap - c.baseThickness + EPS,
      c.baseThickness
    );
    const innerUpper = makeCylinder(
      d.innerR,
      c.bodyHeight - c.nestedOverlap + 2 * EPS,
      [0, 0, c.nestedOverlap - EPS]
    );
    cavityCutters = [innerLower, innerUpper];
  } else {
    outer = makeCylinder(d.outerR, c.bodyHeight);
    innerAtBase = d.innerR;
    cavityCutters = [
      makeCylinder(d.innerR, c.bodyHeight - c.baseThickness + 2 * EPS, [0, 0, c.baseThickness]),
    ];
  }

  let body = cutAll(outer, cavityCutters);

  const baseGusset = makeRevolvedProfile([
    [innerAtBase - 8, c.baseThickness],
    [innerAtBase, c.baseThickness],
    [innerAtBase, c.baseThickness + 8],
  ]);
  body = body.fuse(baseGusset);

  if (baseFlangeOD) {
    const flangeOuterR = baseFlangeOD / 2;
    body = body.fuse(makeRing(flangeOuterR, d.outerR - 5, 8, 0));
  }

  body = addTopRim(body, p);
  return addModuleLockGeometry(body, { topReceivers, lowerTabs }, p);
}

function flangeBoltCuttersY(centerX, faceY, centerZ, directionSign, flangeRadius = 22) {
  const cutters = [];
  const boltCircle = flangeRadius - 6;
  for (const angle of [90, 210, 330]) {
    const a = deg(angle);
    const x = centerX + boltCircle * Math.cos(a);
    const z = centerZ + boltCircle * Math.sin(a);
    const originY = directionSign > 0 ? faceY - 2 : faceY + 2;
    cutters.push(makeCylinder(2.7, 9, [x, originY, z], [0, directionSign, 0]));
  }
  return cutters;
}

function flangeBoltCuttersX(faceX, centerY, centerZ, directionSign, flangeRadius = 22) {
  const cutters = [];
  const boltCircle = flangeRadius - 6;
  for (const angle of [90, 210, 330]) {
    const a = deg(angle);
    const y = centerY + boltCircle * Math.cos(a);
    const z = centerZ + boltCircle * Math.sin(a);
    const originX = directionSign > 0 ? faceX - 2 : faceX + 2;
    cutters.push(makeCylinder(2.7, 9, [originX, y, z], [directionSign, 0, 0]));
  }
  return cutters;
}

function addDrainPort(body, s) {
  const tubeStartX = -120;
  const tubeLength = 60;
  const faceX = -180;
  const tube = makeCylinder(s.drainTubeOD / 2, tubeLength, [tubeStartX, 0, s.drainAxisZ], [-1, 0, 0]);
  const flange = makeBox(
    [faceX, -s.drainFlangeWidth / 2, 0],
    [faceX + 5, s.drainFlangeWidth / 2, s.drainFlangeHeight]
  );
  let result = body.fuse(tube).fuse(flange);
  const bore = makeCylinder(s.drainPassageID / 2, 65, [faceX - EPS, 0, s.drainAxisZ], [1, 0, 0]);
  result = result.cut(bore);
  const holes = [];
  for (const y of [-22, 22]) {
    for (const z of [8, 43]) {
      holes.push(makeCylinder(2.7, 8, [faceX - EPS, y, z], [1, 0, 0]));
    }
  }
  return cutAll(result, holes);
}

function addInternalSupportPads(body, radius, z, count = 3, padRadius = 9, padHeight = 4, angleOffset = 0) {
  const pads = [];
  for (let i = 0; i < count; i += 1) {
    const [x, y] = polarPoint(radius, angleOffset + (360 * i) / count);
    pads.push(makeCylinder(padRadius, padHeight, [x, y, z]));
  }
  return body.fuse(fuseAll(pads));
}

export function buildStage1Body(p = P) {
  assertParameters(p);
  const c = p.common;
  const s = p.stage1;
  let body = makeBaseCup({ nestedFoot: true, topReceivers: false, lowerTabs: true }, p);

  const standpipeOuter = makeCylinder(s.standpipeOD / 2, s.standpipeWeirZ - c.baseThickness, [0, 0, c.baseThickness]);
  body = body.fuse(standpipeOuter);
  body = body.cut(makeCylinder(s.standpipeID / 2, s.standpipeWeirZ + 2, [0, 0, -EPS]));

  const standpipeFoot = makeRing(s.standpipeOD / 2 + 7, s.standpipeID / 2, 5, c.baseThickness);
  body = body.fuse(standpipeFoot);
  body = addInternalSupportPads(body, 140.5, s.sedimentFunnelTopZ - 3, 3, 9, 4, 20);
  body = addInternalSupportPads(
    body,
    s.receiverPadRadius,
    s.receiverPadZ,
    3,
    9,
    s.receiverPadHeight,
    0
  );
  body = addDrainPort(body, s);
  return applyUndersideWatermark(body, p);
}

export function buildStage1InletReceiver(p = P) {
  const s = p.stage1;
  const cupHeight = s.receiverOverflowZ - s.receiverBottomZ;
  let cup = makeCylinder(
    s.receiverOuterRadius,
    cupHeight,
    [s.receiverCenterX, 0, s.receiverBottomZ]
  );
  cup = cup.cut(
    makeCylinder(
      s.receiverInnerRadius,
      cupHeight - 4 + EPS,
      [s.receiverCenterX, 0, s.receiverBottomZ + 4]
    )
  );

  const socket = makeRing(
    s.receiverSocketOD / 2,
    s.receiverSocketID / 2,
    s.receiverBottomZ - s.receiverSocketBottomZ,
    s.receiverSocketBottomZ
  ).translate(s.receiverCenterX, 0, 0);
  const supportRing = makeRing(
    s.receiverSupportOuterRadius,
    s.receiverSupportInnerRadius,
    5,
    s.receiverSupportZ
  );

  const posts = [];
  for (const yCenter of [-s.hoseGuidePostOffsetY, s.hoseGuidePostOffsetY]) {
    posts.push(
      makeBox(
        [
          s.receiverCenterX - s.hoseGuidePostWidthX / 2,
          yCenter - s.hoseGuidePostWidthY / 2,
          s.hoseGuideBottomZ,
        ],
        [
          s.receiverCenterX + s.hoseGuidePostWidthX / 2,
          yCenter + s.hoseGuidePostWidthY / 2,
          s.hoseGuideTopZ,
        ]
      )
    );
  }
  let receiver = cup.fuse(socket).fuse(supportRing).fuse(fuseAll(posts));

  const outletBore = makeCylinder(
    s.receiverSocketID / 2,
    s.receiverBottomZ - s.receiverSocketBottomZ + 6,
    [s.receiverCenterX, 0, s.receiverSocketBottomZ - EPS]
  );
  receiver = receiver.cut(outletBore);

  const tieSlots = [];
  for (const yCenter of [-s.hoseGuidePostOffsetY, s.hoseGuidePostOffsetY]) {
    for (const z of [291, 303]) {
      tieSlots.push(
        makeBox(
          [s.receiverCenterX - 9, yCenter - 2, z],
          [s.receiverCenterX + 9, yCenter + 2, z + 5]
        )
      );
    }
  }
  receiver = cutAll(receiver, tieSlots);

  const referenceTabs = fuseAll([
    makeBox(
      [s.receiverCenterX - 6, -24, s.hoseEndReferenceZ - 1],
      [s.receiverCenterX + 6, -20, s.hoseEndReferenceZ + 1]
    ),
    makeBox(
      [s.receiverCenterX - 6, 20, s.hoseEndReferenceZ - 1],
      [s.receiverCenterX + 6, 24, s.hoseEndReferenceZ + 1]
    ),
  ]);
  return receiver.fuse(referenceTabs);
}

export function buildStage1InletDowncomer(p = P) {
  const s = p.stage1;
  const tubeHeight = s.inletDowncomerTopZ - s.inletDowncomerBottomZ;
  let downcomer = makeCylinder(
    s.inletDowncomerOD / 2,
    tubeHeight,
    [s.receiverCenterX, 0, s.inletDowncomerBottomZ]
  );
  const nozzle = makeCylinder(
    s.inletNozzleOD / 2,
    s.inletNozzleLength,
    [s.receiverCenterX, s.inletNozzleStartY, s.inletNozzleAxisZ],
    [0, 1, 0]
  );
  downcomer = downcomer.fuse(nozzle);

  const verticalBore = makeCylinder(
    s.inletDowncomerID / 2,
    s.inletDowncomerTopZ - (s.inletNozzleAxisZ - 4) + EPS,
    [s.receiverCenterX, 0, s.inletNozzleAxisZ - 4]
  );
  const horizontalBore = makeCylinder(
    s.inletNozzleID / 2,
    s.inletNozzleLength + 3,
    [s.receiverCenterX, s.inletNozzleStartY - 1, s.inletNozzleAxisZ],
    [0, 1, 0]
  );
  downcomer = downcomer.cut(verticalBore.fuse(horizontalBore));
  const stopCollar = makeRing(22.5, s.inletDowncomerOD / 2, 2, s.receiverBottomZ + 4)
    .translate(s.receiverCenterX, 0, 0);
  return downcomer.fuse(stopCollar);
}

export function buildSedimentFunnel(p = P) {
  const s = p.stage1;
  const shell = makeRevolvedProfile([
    [s.sedimentFunnelInnerRadius, s.sedimentFunnelBottomZ],
    [s.sedimentFunnelOuterRadius, s.sedimentFunnelTopZ],
    [s.sedimentFunnelOuterRadius, s.sedimentFunnelTopZ + s.sedimentFunnelThicknessZ],
    [s.sedimentFunnelInnerRadius, s.sedimentFunnelBottomZ + s.sedimentFunnelThicknessZ],
  ]);
  const outerSeat = makeRing(
    s.sedimentFunnelOuterRadius + 2,
    s.sedimentFunnelOuterRadius - 4,
    6,
    s.sedimentFunnelTopZ - 1
  );
  const innerCollar = makeRing(
    s.sedimentFunnelInnerRadius + 4,
    s.sedimentFunnelInnerRadius,
    8,
    s.sedimentFunnelBottomZ
  );
  const pullTabs = fuseAll([
    makeBox([-10, s.sedimentFunnelOuterRadius - 8, s.sedimentFunnelTopZ], [10, s.sedimentFunnelOuterRadius + 1, s.sedimentFunnelTopZ + 18]),
    makeBox([-10, -s.sedimentFunnelOuterRadius - 1, s.sedimentFunnelTopZ], [10, -s.sedimentFunnelOuterRadius + 8, s.sedimentFunnelTopZ + 18]),
  ]);
  return shell.fuse(outerSeat).fuse(innerCollar).fuse(pullTabs);
}

export function stage2OverflowCenter(p = P) {
  return derived(p).stage2OutletCenter;
}

export function buildStage2Body(p = P) {
  assertParameters(p);
  const c = p.common;
  const s = p.stage2;
  const [x, y] = stage2OverflowCenter(p);
  let body = makeBaseCup({ nestedFoot: true, topReceivers: true, lowerTabs: true }, p);
  const d = derived(p);
  const floorProfile = new Sketcher("XZ")
    .movePointerTo([-d.innerR - 1, c.baseThickness - 2])
    .lineTo([d.innerR + 1, c.baseThickness - 2])
    .lineTo([d.innerR + 1, s.sedimentFloorHighZ])
    .lineTo([-d.innerR - 1, s.sedimentFloorLowZ])
    .close()
    .extrude(2 * d.innerR + 2)
    .translate(0, -d.innerR - 1, 0);
  const floorClip = makeCylinder(s.sedimentFloorRadius, 55, [0, 0, c.baseThickness - EPS]);
  body = body.fuse(floorProfile.intersect(floorClip));
  body = body.fuse(
    makeCylinder(
      s.overflowStandpipeOD / 2,
      s.overflowWeirZ - c.baseThickness + 2 * EPS,
      [x, y, c.baseThickness - EPS]
    )
  );
  body = body.cut(
    makeCylinder(s.overflowStandpipeID / 2, s.overflowWeirZ + 2, [x, y, -EPS])
  );
  body = body.fuse(
    makeRing(
      s.overflowStandpipeOD / 2 + 7,
      s.overflowStandpipeID / 2,
      5 + EPS,
      c.baseThickness - EPS
    ).translate(x, y, 0)
  );
  body = addInternalSupportPads(
    body,
    55,
    c.baseThickness - EPS,
    4,
    9,
    s.diffuserSupportZ - c.baseThickness + EPS,
    45
  );
  body = addDrainPort(body, s);
  return applyUndersideWatermark(body, p);
}

export function buildStage2DropTube(p = P) {
  const s = p.stage2;
  const length = s.dropTubeTopZ - s.dropTubeBottomZ;
  const tube = makeRing(s.dropTubeOD / 2, s.dropTubeID / 2, length, 0);
  const stopCollar = makeRing(23, s.dropTubeID / 2, 4, length - 6);
  return tube.fuse(stopCollar);
}

export function buildRadialGrid({ radius, hubRadius, thickness, spokeCount, spokeWidth, ringRadii = [], ringWidth = 4 }) {
  const components = [
    makeCylinder(hubRadius, thickness),
    makeRing(radius, radius - ringWidth, thickness, 0),
  ];
  for (const ringRadius of ringRadii) {
    components.push(makeRing(ringRadius + ringWidth / 2, ringRadius - ringWidth / 2, thickness, 0));
  }
  for (let i = 0; i < spokeCount; i += 1) {
    components.push(
      rotatedBox(-radius, radius, -spokeWidth / 2, spokeWidth / 2, 0, thickness, (360 * i) / spokeCount)
    );
  }
  return fuseAll(components);
}

export function buildStage2Diffuser(p = P) {
  return buildRadialGrid({
    radius: 60,
    hubRadius: 25,
    thickness: 4,
    spokeCount: 10,
    spokeWidth: 4,
    ringRadii: [42],
    ringWidth: 4,
  });
}

export function buildLamellaCassette(p = P) {
  const s = p.stage2;
  const angle = s.lamellaAngleDeg;
  const angleRad = deg(angle);
  const pitch = s.lamellaGapNormal + s.lamellaPlateThickness;
  const plates = [];
  const centerIndex = (s.lamellaPlateCount - 1) / 2;

  for (let i = 0; i < s.lamellaPlateCount; i += 1) {
    const normalOffset = (i - centerIndex) * pitch;
    const yShift = -Math.sin(angleRad) * normalOffset;
    const zShift = Math.cos(angleRad) * normalOffset;
    plates.push(
      makeBox(
        [-s.lamellaPlateWidth / 2, -s.lamellaPlateLength / 2, -s.lamellaPlateThickness / 2],
        [s.lamellaPlateWidth / 2, s.lamellaPlateLength / 2, s.lamellaPlateThickness / 2]
      )
        .rotate(angle, [0, 0, 0], [1, 0, 0])
        .translate(0, yShift, s.lamellaPackCenterZ + zShift)
    );
  }

  const railLength = (s.lamellaPlateCount - 1) * pitch + 18;
  const railAngle = angle + 90;
  const halfRailT = s.lamellaRailThickness / 2;
  const railX = s.lamellaPlateWidth / 2 - 1.5;
  for (const xCenter of [-railX, railX]) {
    plates.push(
      makeBox(
        [xCenter - halfRailT, -railLength / 2, -halfRailT],
        [xCenter + halfRailT, railLength / 2, halfRailT]
      )
        .rotate(railAngle, [0, 0, 0], [1, 0, 0])
        .translate(0, 0, s.lamellaPackCenterZ)
    );
  }

  const handleBottom = s.lamellaPackCenterZ + 38;
  const handleTop = s.overflowWeirZ + 15;
  const handleParts = [
    makeBox([-80, -5, handleBottom], [-72, 5, handleTop]),
    makeBox([72, -5, handleBottom], [80, 5, handleTop]),
    makeBox([-80, -5, handleTop - 4.5], [80, 5, handleTop + 4]),
  ];

  let cassette = fuseAll([...plates, ...handleParts]);
  cassette = cassette.cut(makeCylinder(s.dropTubeOD / 2 + 2, 250, [0, 0, 20]));
  const [overflowX, overflowY] = stage2OverflowCenter(p);
  cassette = cassette.cut(
    makeCylinder(s.overflowStandpipeOD / 2 + 2, 250, [overflowX, overflowY, 20])
  );
  return cassette;
}

function outletBoltCutters() {
  const cutters = [];
  for (const x of [-58, 58]) {
    for (const z of [10, 58]) {
      cutters.push(makeCylinder(3.2, 38, [x, -174, z], [0, 1, 0]));
    }
  }
  return cutters;
}

export function buildStage3Body(p = P) {
  assertParameters(p);
  const s = p.stage3;
  let body = makeBaseCup({
    nestedFoot: false,
    baseFlangeOD: s.baseFlangeOD,
    topReceivers: true,
    lowerTabs: false,
  }, p);

  const mountingHoles = [];
  for (const angle of [45, 135, 225, 315]) {
    const [x, y] = polarPoint(156, angle);
    mountingHoles.push(makeCylinder(4.5, 10, [x, y, -EPS]));
  }
  body = cutAll(body, mountingHoles);

  const basketShelf = makeRing(146, 119, 5.4, 34.8);
  body = body.fuse(basketShelf);
  body = addInternalSupportPads(body, 136, s.distributorZ - 4, 3, 10, 5, 30);

  const outletPad = makeBox(
    [-s.outletFlangeWidth / 2, -163, 4],
    [s.outletFlangeWidth / 2, -145, 66]
  );
  body = body.fuse(outletPad);
  body = body.cut(
    makeBox(
      [-s.outletSlotWidth / 2, -171, s.outletSlotBottomZ],
      [s.outletSlotWidth / 2, -139, s.outletSlotBottomZ + s.outletSlotHeight]
    )
  );
  body = cutAll(body, outletBoltCutters());

  const weirCut = makeBox(
    [-s.overflowWidth / 2, 140, s.overflowWeirZ],
    [s.overflowWidth / 2, 170, p.common.bodyHeight + 1]
  );
  body = body.cut(weirCut);
  const weirLip = makeBox(
    [-s.overflowWidth / 2 - 6, 144.8, s.overflowWeirZ - 5.2],
    [s.overflowWidth / 2 + 6, 165, s.overflowWeirZ + 0.2]
  );
  const weirSides = fuseAll([
    makeBox([-s.overflowWidth / 2 - 6, 144.8, s.overflowWeirZ - 5.2], [-s.overflowWidth / 2 + 0.2, 165, s.overflowWeirZ + 15]),
    makeBox([s.overflowWidth / 2 - 0.2, 144.8, s.overflowWeirZ - 5.2], [s.overflowWidth / 2 + 6, 165, s.overflowWeirZ + 15]),
  ]);
  body = body.fuse(weirLip).fuse(weirSides);
  return applyUndersideWatermark(body, p);
}

export function buildMediaBasket(p = P) {
  const s = p.stage3;
  const outerR = s.basketBodyOD / 2;
  const innerR = outerR - s.basketWall;
  const guideR = s.basketGuideOD / 2;
  const wall = makeRing(outerR, innerR, s.basketHeight - 4, 0);
  const topGuide = makeRing(guideR, innerR - 2, 4, s.basketHeight - 4);
  const bottomGrid = buildRadialGrid({
    radius: innerR,
    hubRadius: 14,
    thickness: 3.2,
    spokeCount: 12,
    spokeWidth: 3.6,
    ringRadii: [42, 78, 108],
    ringWidth: 3.6,
  });
  const fingerTabs = fuseAll([
    makeBox([-124, -14, s.basketHeight - 4.2], [-78, 14, s.basketHeight]),
    makeBox([78, -14, s.basketHeight - 4.2], [124, 14, s.basketHeight]),
  ]);
  return wall.fuse(topGuide).fuse(bottomGrid).fuse(fingerTabs);
}

export function buildStage3Distributor(p = P) {
  const grid = buildRadialGrid({
    radius: 130,
    hubRadius: 18,
    thickness: 4,
    spokeCount: 12,
    spokeWidth: 4,
    ringRadii: [45, 82, 116],
    ringWidth: 4,
  });
  const [impactX, impactY] = stage2OverflowCenter(p);
  return grid.fuse(makeCylinder(28, 4, [impactX, impactY, 0]));
}

function cutOutletAttachment(shape, p = P) {
  const s = p.stage3;
  let result = shape.cut(
    makeBox(
      [-s.outletSlotWidth / 2, -7, 8],
      [s.outletSlotWidth / 2, 2, 8 + s.outletSlotHeight]
    )
  );
  const cutters = [];
  for (const x of [-58, 58]) {
    for (const z of [6, 54]) {
      cutters.push(makeCylinder(3.2, 10, [x, -7, z], [0, 1, 0]));
    }
  }
  return cutAll(result, cutters);
}

export function buildCascadeSpout(p = P) {
  const s = p.stage3;
  const flange = makeBox([-70, -5, 0], [70, 0, 62]);
  const floor = makeBox([-s.cascadeWidth / 2, -s.cascadeLength, 8], [s.cascadeWidth / 2, -3, 13]);
  const sides = fuseAll([
    makeBox([-s.cascadeWidth / 2, -s.cascadeLength, 8], [-s.cascadeWidth / 2 + 5, -3, 42]),
    makeBox([s.cascadeWidth / 2 - 5, -s.cascadeLength, 8], [s.cascadeWidth / 2, -3, 42]),
  ]);
  return cutOutletAttachment(flange.fuse(floor).fuse(sides), p);
}

export function buildOutletHoseAdapter(p = P) {
  const s = p.stage3;
  const flange = makeBox([-70, -5, 0], [70, 0, 62]);
  const plenumOuter = makeBox([-55, -30, 7], [55, -4, 41]);
  const tube = makeCylinder(12.8, 38, [0, -26, 24], [0, -1, 0]);
  const barb1 = makeCylinder(14.1, 3.2, [0, -47, 24], [0, -1, 0]);
  const barb2 = makeCylinder(14.1, 3.2, [0, -58, 24], [0, -1, 0]);
  let adapter = flange.fuse(plenumOuter).fuse(tube).fuse(barb1).fuse(barb2);
  const plenumInner = makeBox([-50, -22, 11], [50, 1, 37]);
  const bore = makeCylinder(9, 48, [0, -20, 24], [0, -1, 0]);
  adapter = adapter.cut(plenumInner.fuse(bore));
  return cutOutletAttachment(adapter, p);
}

export function buildDrainSpigotFlange(p = P) {
  const s = p.stage1;
  let adapter = makeBox(
    [-s.drainFlangeWidth / 2, -s.drainAxisZ, 0],
    [s.drainFlangeWidth / 2, s.drainFlangeHeight - s.drainAxisZ, 5]
  );
  adapter = adapter.fuse(makeCylinder(16.4, 42, [0, 0, 5]));
  adapter = adapter.fuse(
    makeRevolvedProfile([[16.2, 14], [17.2, 17], [16.2, 19]])
  );
  adapter = adapter.fuse(
    makeRevolvedProfile([[16.2, 29], [17.2, 32], [16.2, 34]])
  );
  adapter = adapter.cut(makeCylinder(12.5, 50, [0, 0, -EPS]));
  const holes = [];
  for (const x of [-22, 22]) {
    for (const y of [8 - s.drainAxisZ, 43 - s.drainAxisZ]) {
      holes.push(makeCylinder(2.7, 7, [x, y, -EPS]));
    }
  }
  return cutAll(adapter, holes);
}

export function buildBlindPortPlate(p = P) {
  const s = p.stage1;
  let plate = makeBox(
    [-s.drainFlangeWidth / 2, -s.drainAxisZ, 0],
    [s.drainFlangeWidth / 2, s.drainFlangeHeight - s.drainAxisZ, 5]
  );
  const holes = [];
  for (const x of [-22, 22]) {
    for (const y of [8 - s.drainAxisZ, 43 - s.drainAxisZ]) {
      holes.push(makeCylinder(2.7, 7, [x, y, -EPS]));
    }
  }
  const handle = makeBox([-12, -4, 5], [12, 4, 18]);
  return cutAll(plate.fuse(handle), holes);
}

export function buildHoseFitCoupon() {
  const base = makeBox([-55, -20, 0], [55, 20, 4]);
  const diameters = [25.2, 25.6, 26.0];
  const centers = [-36, 0, 36];
  const posts = [];
  const cutters = [];
  diameters.forEach((diameter, index) => {
    const x = centers[index];
    posts.push(makeCylinder(diameter / 2, 30.2, [x, 0, 3.8]));
    posts.push(makeCylinder(diameter / 2 + 1.2, 3, [x, 0, 23]));
    cutters.push(makeCylinder(7, 34, [x, 0, 2]));
    for (let mark = 0; mark <= index; mark += 1) {
      posts.push(makeCylinder(1.2, 2.2, [x - 3 + mark * 3, -17, 3.8]));
    }
  });
  return cutAll(base.fuse(fuseAll(posts)), cutters);
}

export function buildDrainFitCoupon() {
  const base = makeBox([-55, -20, 0], [55, 20, 4]);
  const diameters = [32.4, 33.0, 33.6];
  const centers = [-36, 0, 36];
  const posts = [];
  const cutters = [];
  diameters.forEach((diameter, index) => {
    const x = centers[index];
    posts.push(makeCylinder(diameter / 2, 30.2, [x, 0, 3.8]));
    posts.push(makeCylinder(diameter / 2 + 0.9, 3, [x, 0, 23]));
    cutters.push(makeCylinder(12.5, 34, [x, 0, 2]));
    for (let mark = 0; mark <= index; mark += 1) {
      posts.push(makeCylinder(1.2, 2.2, [x - 3 + mark * 3, -17, 3.8]));
    }
  });
  return cutAll(base.fuse(fuseAll(posts)), cutters);
}

export function printOriented(shape, orientation = "as-designed") {
  let oriented = shape.clone();
  if (orientation === "lamella-side") {
    oriented = oriented.rotate(30, [0, 0, 0], [1, 0, 0]);
  } else if (orientation === "funnel-inverted") {
    oriented = oriented.rotate(180, [0, 0, 0], [1, 0, 0]);
  } else if (orientation === "outlet-flange-bed") {
    oriented = oriented.rotate(-90, [0, 0, 0], [1, 0, 0]);
  }
  const [min] = oriented.boundingBox.bounds;
  return oriented.translate(-min[0], -min[1], -min[2]);
}

export function makeAssemblyComponents(p = P) {
  const d = derived(p);
  const stage3 = buildStage3Body(p);
  const stage2 = buildStage2Body(p).translateZ(d.stage2AssemblyZ);
  const stage1 = buildStage1Body(p).translateZ(d.stage1AssemblyZ);
  const funnel = buildSedimentFunnel(p).translateZ(d.stage1AssemblyZ);
  const inletReceiver = buildStage1InletReceiver(p).translateZ(d.stage1AssemblyZ);
  const inletDowncomer = buildStage1InletDowncomer(p).translateZ(d.stage1AssemblyZ);
  const cassette = buildLamellaCassette(p).translateZ(d.stage2AssemblyZ);
  const dropTube = buildStage2DropTube(p).translateZ(d.stage2AssemblyZ + p.stage2.dropTubeBottomZ);
  const diffuser = buildStage2Diffuser(p).translateZ(d.stage2AssemblyZ + p.stage2.diffuserSupportZ);
  const baskets = [];
  for (let i = 0; i < p.stage3.basketCount; i += 1) {
    baskets.push(buildMediaBasket(p).translateZ(p.stage3.basketBottomZ + i * p.stage3.basketHeight));
  }
  const distributor = buildStage3Distributor(p).translateZ(p.stage3.distributorZ);
  const cascade = buildCascadeSpout(p).translate(0, -163, 4);
  return {
    stage3,
    stage2,
    stage1,
    funnel,
    inletReceiver,
    inletDowncomer,
    cassette,
    dropTube,
    diffuser,
    baskets,
    distributor,
    cascade,
  };
}
