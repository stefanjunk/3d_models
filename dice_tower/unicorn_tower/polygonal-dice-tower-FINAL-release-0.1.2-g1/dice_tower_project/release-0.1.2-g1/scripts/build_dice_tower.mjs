#!/usr/bin/env node

import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import Module from 'manifold-3d';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(scriptDir, '..');

function parseArgs(argv) {
  const result = {
    parameters: path.join(projectRoot, 'parameters', 'geometry-r0.1.2.json'),
    quality: 'final',
  };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--parameters') result.parameters = path.resolve(argv[++i]);
    else if (argv[i] === '--quality') result.quality = argv[++i];
    else throw new Error(`Unknown argument: ${argv[i]}`);
  }
  if (!['preview', 'final'].includes(result.quality)) {
    throw new Error('--quality must be preview or final');
  }
  return result;
}

function ensureDirectories() {
  for (const relative of ['source', 'cutters', 'inserts', 'result', 'reports']) {
    fs.mkdirSync(path.join(projectRoot, relative), { recursive: true });
  }
}

function sha256(filePath) {
  return crypto.createHash('sha256').update(fs.readFileSync(filePath)).digest('hex');
}

function readBinaryStl(filePath, transform) {
  const bytes = fs.readFileSync(filePath);
  if (bytes.length < 84) throw new Error('STL is too short');
  const triangleCount = bytes.readUInt32LE(80);
  if (bytes.length !== 84 + triangleCount * 50) {
    throw new Error(`Expected ${84 + triangleCount * 50} STL bytes, found ${bytes.length}`);
  }

  const positions = [];
  const triangles = [];
  const vertexMap = new Map();
  for (let triangle = 0; triangle < triangleCount; triangle += 1) {
    const recordOffset = 84 + triangle * 50 + 12;
    for (let corner = 0; corner < 3; corner += 1) {
      const offset = recordOffset + corner * 12;
      const source = [
        bytes.readFloatLE(offset),
        bytes.readFloatLE(offset + 4),
        bytes.readFloatLE(offset + 8),
      ];
      const key = source.join(',');
      let index = vertexMap.get(key);
      if (index === undefined) {
        index = positions.length / 3;
        vertexMap.set(key, index);
        positions.push(...transform(source));
      }
      triangles.push(index);
    }
  }
  return {
    triangleCount,
    vertexCount: positions.length / 3,
    positions: new Float32Array(positions),
    triangles: new Uint32Array(triangles),
  };
}

function writeBinaryStl(manifold, filePath, label) {
  const mesh = manifold.getMesh();
  const triangleCount = mesh.triVerts.length / 3;
  const output = Buffer.alloc(84 + triangleCount * 50);
  output.fill(0);
  output.write(label.slice(0, 80), 0, 'ascii');
  output.writeUInt32LE(triangleCount, 80);

  for (let triangle = 0; triangle < triangleCount; triangle += 1) {
    const indices = [
      mesh.triVerts[triangle * 3],
      mesh.triVerts[triangle * 3 + 1],
      mesh.triVerts[triangle * 3 + 2],
    ];
    const points = indices.map((index) => [
      mesh.vertProperties[index * mesh.numProp],
      mesh.vertProperties[index * mesh.numProp + 1],
      mesh.vertProperties[index * mesh.numProp + 2],
    ]);
    const a = points[0];
    const b = points[1];
    const c = points[2];
    const ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
    const ac = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
    const normal = [
      ab[1] * ac[2] - ab[2] * ac[1],
      ab[2] * ac[0] - ab[0] * ac[2],
      ab[0] * ac[1] - ab[1] * ac[0],
    ];
    const length = Math.hypot(...normal) || 1;
    const offset = 84 + triangle * 50;
    for (let axis = 0; axis < 3; axis += 1) {
      output.writeFloatLE(normal[axis] / length, offset + axis * 4);
    }
    for (let corner = 0; corner < 3; corner += 1) {
      for (let axis = 0; axis < 3; axis += 1) {
        output.writeFloatLE(points[corner][axis], offset + 12 + (corner * 3 + axis) * 4);
      }
    }
  }
  fs.writeFileSync(filePath, output);
  return { filePath, triangleCount, sha256: sha256(filePath), sizeBytes: output.length };
}

function roundedRectangle(CrossSection, width, height, radius, segments = 32) {
  if (radius <= 0) return CrossSection.square([width, height], true);
  if (radius * 2 > Math.min(width, height)) throw new Error('Rounded rectangle radius is too large');
  let section = CrossSection.square([width - 2 * radius, height], true)
    .add(CrossSection.square([width, height - 2 * radius], true));
  for (const xSign of [-1, 1]) {
    for (const ySign of [-1, 1]) {
      section = section.add(
        CrossSection.circle(radius, segments).translate([
          xSign * (width / 2 - radius),
          ySign * (height / 2 - radius),
        ]),
      );
    }
  }
  return section;
}

function rotate2d([u, v], degrees) {
  const radians = (degrees * Math.PI) / 180;
  return [
    u * Math.cos(radians) - v * Math.sin(radians),
    u * Math.sin(radians) + v * Math.cos(radians),
  ];
}

function orientedRoundedPrism(CrossSection, start, end, width, height, radius, segments) {
  const direction = end.map((value, index) => value - start[index]);
  if (Math.abs(direction[0]) > 1e-8) {
    throw new Error('The current lined-channel implementation expects a Y/Z-plane centerline');
  }
  const length = Math.hypot(...direction);
  if (length <= 1e-8) throw new Error('Channel start and end must be different');
  const angleX = (Math.atan2(-direction[1], direction[2]) * 180) / Math.PI;
  return roundedRectangle(CrossSection, width, height, radius, segments)
    .extrude(length)
    .rotate([angleX, 0, 0])
    .translate(start);
}

function orientedCircularPrism(CrossSection, start, end, diameter, segments) {
  const direction = end.map((value, index) => value - start[index]);
  if (Math.abs(direction[0]) > 1e-8) {
    throw new Error('The current lined-channel implementation expects a Y/Z-plane centerline');
  }
  const length = Math.hypot(...direction);
  if (length <= 1e-8) throw new Error('Channel start and end must be different');
  const angleX = (Math.atan2(-direction[1], direction[2]) * 180) / Math.PI;
  return CrossSection.circle(diameter / 2, segments)
    .extrude(length)
    .rotate([angleX, 0, 0])
    .translate(start);
}

function archPrism(CrossSection, profile, innerY, outerY, segments) {
  if (innerY <= outerY) throw new Error('Arch prism innerY must be greater than outerY');
  return archSection(CrossSection, profile, segments)
    .extrude(innerY - outerY)
    .rotate([90, 0, 0])
    .translate([profile.axisX, innerY, 0]);
}

function readClosedDxfPolylines(filePath) {
  const lines = fs.readFileSync(filePath, 'utf8').split(/\r?\n/);
  const polygons = [];
  let polygon = null;
  let vertex = null;

  function finishVertex() {
    if (polygon && vertex && Number.isFinite(vertex.x) && Number.isFinite(vertex.y)) {
      polygon.push([vertex.x, vertex.y]);
    }
    vertex = null;
  }

  function finishPolygon() {
    finishVertex();
    if (polygon && polygon.length >= 3) polygons.push(polygon);
    polygon = null;
  }

  for (let index = 0; index + 1 < lines.length; index += 2) {
    const code = lines[index].trim();
    const value = lines[index + 1].trim();
    if (code === '0') {
      finishVertex();
      if (value === 'POLYLINE') {
        finishPolygon();
        polygon = [];
      } else if (value === 'VERTEX') {
        vertex = {};
      } else if (value === 'SEQEND') {
        finishPolygon();
      }
    } else if (vertex && code === '10') {
      vertex.x = Number(value);
    } else if (vertex && code === '20') {
      vertex.y = Number(value);
    }
  }
  finishPolygon();
  if (polygons.length === 0) throw new Error(`No closed POLYLINE entities found in ${filePath}`);
  return polygons;
}

function archSection(CrossSection, exit, segments) {
  const points = [
    [-exit.clearWidth / 2, exit.bottomZ],
    [exit.clearWidth / 2, exit.bottomZ],
    [exit.clearWidth / 2, exit.shoulderZ],
  ];
  for (let i = 1; i <= segments; i += 1) {
    const theta = (i / segments) * Math.PI;
    points.push([
      Math.cos(theta) * exit.archRadius,
      exit.shoulderZ + Math.sin(theta) * exit.archRadius,
    ]);
  }
  points.push([-exit.clearWidth / 2, exit.shoulderZ]);
  return new CrossSection([points], 'Positive');
}

function makeFloorRamp(Manifold, CrossSection, parameters, segments) {
  const { tower, floorRamp } = parameters;
  const radius = tower.cavityRadius + floorRamp.wallOverlap;
  const profile = new CrossSection([[
    [-radius, 0],
    [radius, 0],
    [radius, floorRamp.rearTopZ],
    [-radius, floorRamp.frontTopZ],
  ]], 'Positive');
  const prism = profile
    .extrude(2 * radius)
    .rotate([0, 90, 0])
    .rotate([90, 0, 0])
    .translate([-radius + tower.axisX, tower.axisY, 0]);
  const clip = Manifold.cylinder(45, radius, radius, segments)
    .translate([tower.axisX, tower.axisY, 0]);
  return prism.intersect(clip);
}

function makeBaffle(Manifold, CrossSection, parameters, level, angle, segments) {
  const { tower, baffles } = parameters;
  const radius = tower.cavityRadius;
  const overlapRadius = radius + baffles.wallOverlap;
  const openingEdge = radius - baffles.openingRadialWidth;
  const slope = Math.tan((baffles.topSlopeDegrees * Math.PI) / 180);
  const supportSlope = Math.tan((baffles.ribUndersideDegrees * Math.PI) / 180);
  const ribPlateEmbed = 0.35;
  const left = -overlapRadius - 0.5;

  const platePlan = CrossSection.circle(overlapRadius, segments).intersect(
    CrossSection.square([openingEdge - left, overlapRadius * 2 + 1], true)
      .translate([(left + openingEdge) / 2, 0]),
  );
  const topAt = (u) => level - slope * (u + radius);
  let plate = platePlan.extrude(baffles.plateThickness).warp((position) => {
    position[2] += topAt(position[0]) - baffles.plateThickness;
  });

  const ribs = [];
  for (const v of baffles.ribOffsets) {
    const outerV = Math.abs(v) + baffles.ribWidth / 2;
    const wallU = -Math.sqrt(Math.max(0, (radius + 0.8) ** 2 - outerV ** 2));
    const topWall = topAt(wallU) - baffles.plateThickness + ribPlateEmbed;
    const topEdge = topAt(openingEdge) - baffles.plateThickness + ribPlateEmbed;
    const bottomWall = topEdge - (openingEdge - wallU) * supportSlope;
    const ribProfile = new CrossSection([[
      [wallU, topWall],
      [wallU, bottomWall],
      [openingEdge, topEdge],
    ]], 'Positive');
    ribs.push(
      ribProfile
        .extrude(baffles.ribWidth)
        .rotate([90, 0, 0])
        .translate([0, v + baffles.ribWidth / 2, 0]),
    );
  }

  plate = Manifold.union([plate, ...ribs])
    .rotate([0, 0, angle])
    .translate([tower.axisX, tower.axisY, 0]);
  return plate;
}

function manifoldMetrics(manifold) {
  const components = manifold.decompose();
  const componentCount = components.length;
  for (const component of components) component.delete();
  return {
    status: manifold.status(),
    vertices: manifold.numVert(),
    triangles: manifold.numTri(),
    components: componentCount,
    genus: manifold.genus(),
    volumeMm3: manifold.volume(),
    surfaceAreaMm2: manifold.surfaceArea(),
    bounds: manifold.boundingBox(),
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  ensureDirectories();
  const parameters = JSON.parse(fs.readFileSync(args.parameters, 'utf8'));
  const sourcePath = path.resolve(path.dirname(args.parameters), parameters.source.path);
  const sourceHash = sha256(sourcePath);
  if (sourceHash !== parameters.source.sha256) {
    throw new Error(`Source checksum mismatch: ${sourceHash}`);
  }

  const module = await Module();
  module.setup();
  const { Manifold, Mesh, CrossSection } = module;
  const sourceMesh = readBinaryStl(sourcePath, ([x, y, z]) => [
    x * parameters.source.scale,
    -z * parameters.source.scale,
    (y - parameters.source.sourceMinY) * parameters.source.scale,
  ]);
  const source = new Manifold(new Mesh({
    numProp: 3,
    vertProperties: sourceMesh.positions,
    triVerts: sourceMesh.triangles,
  }));
  if (source.status() !== 'NoError') throw new Error(`Source manifold status: ${source.status()}`);

  const segments = args.quality === 'final' ? parameters.tower.circularSegments : 64;
  const { tower, entry, exit, baffles } = parameters;
  if (baffles.levelsTopDown.length !== baffles.count || baffles.anglesTopDown.length !== baffles.count) {
    throw new Error('Baffle level/angle arrays must match baffle count');
  }
  for (let i = 1; i < baffles.levelsTopDown.length; i += 1) {
    const separation = baffles.levelsTopDown[i - 1] - baffles.levelsTopDown[i];
    if (separation - baffles.plateThickness < baffles.minimumVerticalClearance) {
      throw new Error(`Baffle ${i} vertical clearance is below the specified minimum`);
    }
  }

  const cavity = Manifold.cylinder(
    tower.cavityTopZ - tower.cavityBottomZ,
    tower.cavityRadius,
    tower.cavityRadius,
    segments,
  ).translate([tower.axisX, tower.axisY, tower.cavityBottomZ]);
  const curveSegments = Math.max(24, Math.floor(segments / 4));
  let entryCutter;
  let entryTransitionCutter = null;
  let entryLiner = null;
  if (entry.mode === 'angled-round-lined-channel') {
    entryCutter = orientedCircularPrism(
      CrossSection,
      entry.clearStart,
      entry.clearEnd,
      entry.clearDiameter,
      curveSegments,
    );
    entryLiner = orientedCircularPrism(
      CrossSection,
      entry.linerStart,
      entry.linerEnd,
      entry.linerOuterDiameter,
      curveSegments,
    );
  } else if (entry.mode === 'angled-lined-channel') {
    entryCutter = orientedRoundedPrism(
      CrossSection,
      entry.clearStart,
      entry.clearEnd,
      entry.clearWidth,
      entry.clearHeight,
      entry.cornerRadius,
      curveSegments,
    );
    entryLiner = orientedRoundedPrism(
      CrossSection,
      entry.linerStart,
      entry.linerEnd,
      entry.linerOuterWidth,
      entry.linerOuterHeight,
      entry.linerCornerRadius,
      curveSegments,
    );
  } else {
    entryCutter = roundedRectangle(
      CrossSection,
      entry.clearWidth,
      entry.clearDepth,
      entry.cornerRadius,
      curveSegments,
    ).translate([tower.axisX, tower.axisY + entry.centerRearOffset])
      .extrude(entry.topZ - entry.bottomZ)
      .translate([0, 0, entry.bottomZ]);
    const topOpeningOffset = rotate2d(
      [parameters.die.openingWaypointRadius, parameters.die.openingWaypointTangential],
      baffles.anglesTopDown[0],
    );
    const transitionTop = Manifold.cube(
      [entry.transitionClearSize, entry.transitionClearSize, entry.transitionClearSize],
      true,
    ).translate([
      tower.axisX,
      tower.axisY + entry.centerRearOffset,
      entry.transitionTopCenterZ,
    ]);
    const transitionBottom = Manifold.cube(
      [entry.transitionClearSize, entry.transitionClearSize, entry.transitionClearSize],
      true,
    ).rotate([0, 0, baffles.anglesTopDown[0]]).translate([
      tower.axisX + topOpeningOffset[0],
      tower.axisY + topOpeningOffset[1],
      entry.transitionBottomCenterZ,
    ]);
    entryTransitionCutter = Manifold.hull([transitionTop, transitionBottom]);
  }

  let exitCutter;
  let exitTransitionCutter = null;
  let exitLiner = null;
  if (exit.mode === 'rounded-lined-channel') {
    exitCutter = archPrism(
      CrossSection,
      { ...exit, axisX: tower.axisX },
      exit.clearInnerY,
      exit.clearOuterY,
      curveSegments,
    );
    exitLiner = archPrism(
      CrossSection,
      {
        axisX: tower.axisX,
        clearWidth: exit.linerOuterWidth,
        bottomZ: exit.linerBottomZ,
        shoulderZ: exit.linerShoulderZ,
        archRadius: exit.linerArchRadius,
      },
      exit.linerInnerY,
      exit.linerOuterY,
      curveSegments,
    );
  } else {
    exitCutter = archPrism(
      CrossSection,
      { ...exit, axisX: tower.axisX },
      exit.innerY,
      exit.outerY,
      curveSegments,
    );
    const lowestBaffleAngle = baffles.anglesTopDown.at(-1);
    const lowestOpeningOffset = rotate2d(
      [parameters.die.openingWaypointRadius, parameters.die.openingWaypointTangential],
      lowestBaffleAngle,
    );
    const baffleSlope = Math.tan((baffles.topSlopeDegrees * Math.PI) / 180);
    const lowestNearEdgeU = parameters.die.openingWaypointRadius - parameters.die.maximumEnvelope / 2;
    const exitTransitionTopZ = baffles.levelsTopDown.at(-1)
      - baffleSlope * (lowestNearEdgeU + tower.cavityRadius)
      + parameters.die.maximumEnvelope / 2
      + 0.35;
    const exitTransitionTop = Manifold.cube(
      [exit.transitionClearSize, exit.transitionClearSize, exit.transitionClearSize],
      true,
    ).rotate([0, 0, lowestBaffleAngle]).translate([
      tower.axisX + lowestOpeningOffset[0],
      tower.axisY + lowestOpeningOffset[1],
      exitTransitionTopZ,
    ]);
    const exitTransitionBottom = Manifold.cube(
      [exit.transitionClearSize, exit.transitionClearSize, exit.transitionClearSize],
      true,
    ).translate([
      tower.axisX,
      exit.transitionPortalCenterY,
      exit.transitionPortalCenterZ,
    ]);
    exitTransitionCutter = Manifold.hull([exitTransitionTop, exitTransitionBottom]);
  }

  let entryFunctionalClearance = null;
  if (entry.pathExitCenter && entry.transitionClearanceRadius) {
    entryFunctionalClearance = Manifold.sphere(
      entry.transitionClearanceRadius,
      segments,
    ).translate(entry.pathExitCenter);
  }
  const cutterParts = [cavity, entryCutter, exitCutter];
  if (entryFunctionalClearance) cutterParts.push(entryFunctionalClearance);
  if (entryTransitionCutter) cutterParts.push(entryTransitionCutter);
  if (exitTransitionCutter) cutterParts.push(exitTransitionCutter);
  const cutters = Manifold.union(cutterParts);
  const linerParts = [entryLiner, exitLiner].filter(Boolean);
  const reinforcedSource = linerParts.length
    ? Manifold.union([source, ...linerParts])
    : source;
  const cutShell = reinforcedSource.subtract(cutters);
  const floorRamp = makeFloorRamp(Manifold, CrossSection, parameters, segments);
  const baffleParts = baffles.levelsTopDown.map((level, index) => makeBaffle(
    Manifold,
    CrossSection,
    parameters,
    level,
    baffles.anglesTopDown[index],
    segments,
  ));
  const buildVolumeClip = Manifold.cube([400, 400, 260]).translate([-200, -200, 0]);
  const baffleAssembly = Manifold.union(baffleParts).intersect(buildVolumeClip);
  let productionFloor = floorRamp;
  let productionBaffles = baffleAssembly;
  let exitFunctionalClearance = null;
  if (exit.mode === 'rounded-lined-channel' && exit.functionalClearanceSize) {
    const lowestAngle = baffles.anglesTopDown.at(-1);
    const clearanceStartOffset = rotate2d(
      [exit.functionalClearanceStartRadius, 0],
      lowestAngle,
    );
    const clearanceStart = Manifold.cube(
      [
        exit.functionalClearanceSize,
        exit.functionalClearanceSize,
        exit.functionalClearanceSize,
      ],
      true,
    ).rotate([0, 0, lowestAngle]).translate([
      tower.axisX + clearanceStartOffset[0],
      tower.axisY + clearanceStartOffset[1],
      exit.functionalClearanceStartZ,
    ]);
    const clearanceEnd = Manifold.cube(
      [
        exit.functionalClearanceSize,
        exit.functionalClearanceSize,
        exit.functionalClearanceSize,
      ],
      true,
    ).translate([
      tower.axisX,
      exit.functionalClearanceEndY,
      exit.channelCenterZ,
    ]);
    exitFunctionalClearance = Manifold.hull([clearanceStart, clearanceEnd]);
    productionFloor = productionFloor
      .subtract(exitCutter)
      .subtract(exitFunctionalClearance);
    productionBaffles = productionBaffles
      .subtract(exitCutter)
      .subtract(exitFunctionalClearance);
  }
  const functionalInsert = Manifold.union([productionFloor, productionBaffles])
    .intersect(buildVolumeClip);
  const combinedDraft = cutShell.add(functionalInsert);
  const draft = exitFunctionalClearance
    ? combinedDraft.subtract(exitFunctionalClearance)
    : combinedDraft;
  if (draft.status() !== 'NoError') throw new Error(`Draft manifold status: ${draft.status()}`);

  const watermark = parameters.watermark;
  const watermarkDxfPath = path.resolve(path.dirname(args.parameters), watermark.dxf);
  let watermarkSection = new CrossSection(readClosedDxfPolylines(watermarkDxfPath), 'EvenOdd');
  if (watermark.mirrorWorldXForReadableUnderside) watermarkSection = watermarkSection.mirror([0, 1]);
  watermarkSection = watermarkSection
    .scale(watermark.uniformScale)
    .rotate(watermark.rotationDegrees);
  const watermarkUnplacedBounds = watermarkSection.bounds();
  const watermarkUnplacedCenter = [
    (watermarkUnplacedBounds.min[0] + watermarkUnplacedBounds.max[0]) / 2,
    (watermarkUnplacedBounds.min[1] + watermarkUnplacedBounds.max[1]) / 2,
  ];
  watermarkSection = watermarkSection.translate([
    watermark.centerX - watermarkUnplacedCenter[0],
    watermark.centerY - watermarkUnplacedCenter[1],
  ]);
  const watermarkBounds = watermarkSection.bounds();
  const watermarkCutter = watermarkSection
    .extrude(watermark.depth + watermark.lowerBooleanOverlap)
    .translate([0, 0, watermark.localUndersideZ - watermark.lowerBooleanOverlap]);
  const watermarkedDraft = draft.subtract(watermarkCutter);
  if (watermarkedDraft.status() !== 'NoError') {
    throw new Error(`Watermarked draft manifold status: ${watermarkedDraft.status()}`);
  }

  const tag = parameters.revision;
  const outputs = [];
  outputs.push(writeBinaryStl(
    source,
    path.join(projectRoot, 'source', `polygonal-source-working-mm-${tag}.stl`),
    `JuSt Innovation source working mm ${tag}`,
  ));
  outputs.push(writeBinaryStl(
    cavity,
    path.join(projectRoot, 'cutters', `interior-cylinder-cutter-${tag}.stl`),
    `JuSt Innovation cavity cutter ${tag}`,
  ));
  outputs.push(writeBinaryStl(
    entryCutter,
    path.join(projectRoot, 'cutters', `rear-roof-entry-cutter-${tag}.stl`),
    `JuSt Innovation entry cutter ${tag}`,
  ));
  if (entryTransitionCutter) {
    outputs.push(writeBinaryStl(
      entryTransitionCutter,
      path.join(projectRoot, 'cutters', `entry-transition-cutter-${tag}.stl`),
      `JuSt Innovation entry transition cutter ${tag}`,
    ));
  }
  if (entryLiner) {
    outputs.push(writeBinaryStl(
      entryLiner,
      path.join(projectRoot, 'inserts', `rear-upper-entry-channel-liner-${tag}.stl`),
      `JuSt Innovation rear upper entry liner ${tag}`,
    ));
  }
  if (entryFunctionalClearance) {
    outputs.push(writeBinaryStl(
      entryFunctionalClearance,
      path.join(projectRoot, 'cutters', `entry-orientation-clearance-${tag}.stl`),
      `JuSt Innovation entry orientation clearance ${tag}`,
    ));
  }
  outputs.push(writeBinaryStl(
    exitCutter,
    path.join(projectRoot, 'cutters', `forecourt-exit-cutter-${tag}.stl`),
    `JuSt Innovation exit cutter ${tag}`,
  ));
  if (exitTransitionCutter) {
    outputs.push(writeBinaryStl(
      exitTransitionCutter,
      path.join(projectRoot, 'cutters', `exit-transition-cutter-${tag}.stl`),
      `JuSt Innovation exit transition cutter ${tag}`,
    ));
  }
  if (exitLiner) {
    outputs.push(writeBinaryStl(
      exitLiner,
      path.join(projectRoot, 'inserts', `front-exit-channel-liner-${tag}.stl`),
      `JuSt Innovation front exit liner ${tag}`,
    ));
  }
  if (exitFunctionalClearance) {
    outputs.push(writeBinaryStl(
      exitFunctionalClearance,
      path.join(projectRoot, 'cutters', `internal-exit-clearance-${tag}.stl`),
      `JuSt Innovation internal exit clearance ${tag}`,
    ));
  }
  outputs.push(writeBinaryStl(
    productionFloor,
    path.join(projectRoot, 'inserts', `sloped-floor-insert-${tag}.stl`),
    `JuSt Innovation floor insert ${tag}`,
  ));
  outputs.push(writeBinaryStl(
    productionBaffles,
    path.join(projectRoot, 'inserts', `${baffles.count}-baffle-insert-${tag}.stl`),
    `JuSt Innovation baffle insert ${tag}`,
  ));
  outputs.push(writeBinaryStl(
    draft,
    path.join(projectRoot, 'result', `polygonal-dice-tower-DRAFT-no-watermark-${tag}.stl`),
    `DRAFT JuSt Innovation dice tower no watermark ${tag}`,
  ));
  outputs.push(writeBinaryStl(
    watermarkCutter,
    path.join(projectRoot, 'cutters', `${watermark.assetId}-${watermark.variant}-cutter-${tag}.stl`),
    `JuSt Innovation ${watermark.assetId} cutter ${tag}`,
  ));
  outputs.push(writeBinaryStl(
    watermarkedDraft,
    path.join(projectRoot, 'result', `polygonal-dice-tower-DRAFT-watermarked-${tag}.stl`),
    `DRAFT JuSt Innovation watermarked dice tower ${tag}`,
  ));

  const report = {
    project: 'polygonal-dice-tower-functionalization',
    geometryRevision: parameters.revision,
    generatedAt: new Date().toISOString(),
    quality: args.quality,
    tools: {
      node: process.version,
      manifold3d: '3.5.1',
      booleanKernel: 'Manifold WASM',
    },
    source: {
      path: sourcePath,
      sha256: sourceHash,
      importedTriangles: sourceMesh.triangleCount,
      importedUniqueVertices: sourceMesh.vertexCount,
      metrics: manifoldMetrics(source),
    },
    operations: {
      cavity: manifoldMetrics(cavity),
      entryCutter: manifoldMetrics(entryCutter),
      ...(entryTransitionCutter
        ? { entryTransitionCutter: manifoldMetrics(entryTransitionCutter) }
        : {}),
      ...(entryLiner ? { entryLiner: manifoldMetrics(entryLiner) } : {}),
      ...(entryFunctionalClearance
        ? { entryFunctionalClearance: manifoldMetrics(entryFunctionalClearance) }
        : {}),
      exitCutter: manifoldMetrics(exitCutter),
      ...(exitTransitionCutter
        ? { exitTransitionCutter: manifoldMetrics(exitTransitionCutter) }
        : {}),
      ...(exitLiner ? { exitLiner: manifoldMetrics(exitLiner) } : {}),
      ...(exitFunctionalClearance
        ? { exitFunctionalClearance: manifoldMetrics(exitFunctionalClearance) }
        : {}),
      floorRamp: manifoldMetrics(productionFloor),
      baffleAssembly: manifoldMetrics(productionBaffles),
    },
    draft: manifoldMetrics(draft),
    watermark: {
      assetId: watermark.assetId,
      variant: watermark.variant,
      sourceDxf: watermarkDxfPath,
      uniformScale: watermark.uniformScale,
      mirroredWorldX: watermark.mirrorWorldXForReadableUnderside,
      rotationDegrees: watermark.rotationDegrees,
      boundsMm: watermarkBounds,
      depthMm: watermark.depth,
      centerMm: [watermark.centerX, watermark.centerY, watermark.localUndersideZ],
      cutter: manifoldMetrics(watermarkCutter),
    },
    watermarkedDraft: manifoldMetrics(watermarkedDraft),
    outputs,
  };
  fs.writeFileSync(
    path.join(projectRoot, 'reports', `build-metrics-${tag}.json`),
    `${JSON.stringify(report, null, 2)}\n`,
  );
  console.log(JSON.stringify(report, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
