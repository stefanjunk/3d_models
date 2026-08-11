#!/usr/bin/env node

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import Module from 'manifold-3d';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(scriptDir, '..');

function parseArgs(argv) {
  const args = {
    parameters: path.join(projectRoot, 'parameters', 'geometry-r0.1.2.json'),
    draft: null,
    report: null,
  };
  for (let index = 0; index < argv.length; index += 1) {
    if (argv[index] === '--parameters') args.parameters = path.resolve(argv[++index]);
    else if (argv[index] === '--draft') args.draft = path.resolve(argv[++index]);
    else if (argv[index] === '--report') args.report = path.resolve(argv[++index]);
    else throw new Error(`Unknown argument: ${argv[index]}`);
  }
  return args;
}

function readBinaryStl(filePath) {
  const bytes = fs.readFileSync(filePath);
  const triangleCount = bytes.readUInt32LE(80);
  if (bytes.length !== 84 + triangleCount * 50) throw new Error('Invalid binary STL size');
  const positions = [];
  const indices = [];
  const vertexMap = new Map();
  for (let triangle = 0; triangle < triangleCount; triangle += 1) {
    const recordOffset = 84 + triangle * 50 + 12;
    for (let corner = 0; corner < 3; corner += 1) {
      const offset = recordOffset + corner * 12;
      const point = [
        bytes.readFloatLE(offset),
        bytes.readFloatLE(offset + 4),
        bytes.readFloatLE(offset + 8),
      ];
      const key = point.join(',');
      let index = vertexMap.get(key);
      if (index === undefined) {
        index = positions.length / 3;
        vertexMap.set(key, index);
        positions.push(...point);
      }
      indices.push(index);
    }
  }
  return {
    positions: new Float32Array(positions),
    indices: new Uint32Array(indices),
  };
}

function rotate2d([u, v], degrees) {
  const radians = (degrees * Math.PI) / 180;
  return [
    u * Math.cos(radians) - v * Math.sin(radians),
    u * Math.sin(radians) + v * Math.cos(radians),
  ];
}

function interpolate(first, second, fraction) {
  return first.map((value, index) => value + (second[index] - value) * fraction);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const parameters = JSON.parse(fs.readFileSync(args.parameters, 'utf8'));
  const draftPath = args.draft || path.join(
    projectRoot,
    'result',
    `polygonal-dice-tower-DRAFT-no-watermark-${parameters.revision}.stl`,
  );
  const reportPath = args.report || path.join(
    projectRoot,
    'reports',
    `dice-path-${parameters.revision}.json`,
  );

  const module = await Module();
  module.setup();
  const { Manifold, Mesh } = module;
  const imported = readBinaryStl(draftPath);
  const towerBody = new Manifold(new Mesh({
    numProp: 3,
    vertProperties: imported.positions,
    triVerts: imported.indices,
  }));
  if (towerBody.status() !== 'NoError') {
    throw new Error(`Draft import failed: ${towerBody.status()}`);
  }

  const {
    baffles,
    die,
    tower,
    entry,
    exit,
  } = parameters;
  const dieBody = Manifold.cube(
    [die.maximumEnvelope, die.maximumEnvelope, die.maximumEnvelope],
    true,
  );
  const halfDie = die.maximumEnvelope / 2;
  const slope = Math.tan((baffles.topSlopeDegrees * Math.PI) / 180);
  const collisionLimitMm3 = 0.02;
  const openingWaypoint = [die.openingWaypointRadius, die.openingWaypointTangential];
  const tests = [];

  function testPose(name, center, rotations, category) {
    const posedDie = dieBody.rotate(rotations).translate(center);
    const intersectionVolume = towerBody.intersect(posedDie).volume();
    tests.push({
      name,
      category,
      center,
      rotationsDegrees: rotations,
      intersectionVolumeMm3: intersectionVolume,
      passed: intersectionVolume <= collisionLimitMm3,
    });
  }

  function sampleSegment(name, first, second, steps, rotations, category) {
    for (let step = 0; step <= steps; step += 1) {
      const fraction = step / steps;
      testPose(`${name}-${step}`, interpolate(first, second, fraction), rotations, category);
    }
  }

  function topAt(level, u) {
    return level - slope * (u + tower.cavityRadius);
  }

  let entryLandingCenter;
  if (entry.mode === 'angled-round-lined-channel' || entry.mode === 'angled-lined-channel') {
    const direction = entry.clearEnd.map((value, index) => value - entry.clearStart[index]);
    const entryRotationX = (Math.atan2(-direction[1], direction[2]) * 180) / Math.PI;
    sampleSegment(
      'entry-channel',
      entry.clearStart,
      entry.pathExitCenter ?? entry.clearEnd,
      12,
      [entryRotationX, 0, 0],
      'entry-channel',
    );
    entryLandingCenter = entry.pathExitCenter ?? [
        tower.axisX,
        tower.axisY + entry.landingRearOffset,
        entry.clearEnd[2],
      ];
  } else {
    entryLandingCenter = [
      tower.axisX,
      tower.axisY + entry.centerRearOffset,
      entry.transitionBottomCenterZ,
    ];
    for (const centerZ of [185.0, 179.0, 177.5]) {
      testPose(
        `entry-shaft-z${centerZ}`,
        [tower.axisX, tower.axisY + entry.centerRearOffset, centerZ],
        [0, 0, 0],
        'entry-channel',
      );
    }
  }

  const topAngle = baffles.anglesTopDown[0];
  const topLandingLocal = rotate2d([0, entry.landingRearOffset ?? entry.centerRearOffset], -topAngle);
  const entryDirection = entry.clearEnd
    ? entry.clearEnd.map((value, index) => value - entry.clearStart[index])
    : [0, 0, 1];
  const entryRotationX = (Math.atan2(-entryDirection[1], entryDirection[2]) * 180) / Math.PI;
  for (let step = 0; step <= 6; step += 1) {
    const rotationX = entryRotationX * (1 - step / 6);
    testPose(
      `entry-orientation-transition-${step}`,
      entryLandingCenter,
      [rotationX, 0, 0],
      'entry-orientation-transition',
    );
  }
  const topLandingContactZ = topAt(baffles.levelsTopDown[0], topLandingLocal[0] - halfDie)
    + halfDie
    + 0.35;
  sampleSegment(
    'entry-to-first-baffle',
    entryLandingCenter,
    [entryLandingCenter[0], entryLandingCenter[1], topLandingContactZ],
    6,
    [0, 0, topAngle],
    'entry-drop',
  );

  for (let index = 0; index < baffles.count; index += 1) {
    const level = baffles.levelsTopDown[index];
    const angle = baffles.anglesTopDown[index];
    const landing = index === 0
      ? topLandingLocal
      : rotate2d(openingWaypoint, -baffles.rotationBetweenLevels);
    const destination = openingWaypoint;

    for (let step = 0; step <= 8; step += 1) {
      const fraction = step / 8;
      const u = landing[0] + (destination[0] - landing[0]) * fraction;
      const v = landing[1] + (destination[1] - landing[1]) * fraction;
      const highestSurfaceUnderDie = topAt(level, u - halfDie);
      const offset = rotate2d([u, v], angle);
      testPose(
        `baffle-${index + 1}-slide-${step}`,
        [
          tower.axisX + offset[0],
          tower.axisY + offset[1],
          highestSurfaceUnderDie + halfDie + 0.35,
        ],
        [0, 0, angle],
        'baffle-slide',
      );
    }

    if (index < baffles.count - 1) {
      const openingWorld = rotate2d(openingWaypoint, angle);
      const nextLanding = rotate2d(openingWaypoint, -baffles.rotationBetweenLevels);
      const nextContactZ = topAt(
        baffles.levelsTopDown[index + 1],
        nextLanding[0] - halfDie,
      ) + halfDie + 0.35;
      const openingCenterZ = topAt(level, openingWaypoint[0]) - baffles.plateThickness / 2;
      sampleSegment(
        `baffle-${index + 1}-drop`,
        [tower.axisX + openingWorld[0], tower.axisY + openingWorld[1], openingCenterZ],
        [tower.axisX + openingWorld[0], tower.axisY + openingWorld[1], nextContactZ],
        6,
        [0, 0, angle],
        'inter-baffle-drop',
      );
    }
  }

  const lowestLevel = baffles.levelsTopDown.at(-1);
  const lowestAngle = baffles.anglesTopDown.at(-1);
  const exitTransitionOffset = rotate2d(
    [exit.functionalClearanceStartRadius, 0],
    lowestAngle,
  );
  const exitTransitionStart = [
    tower.axisX + exitTransitionOffset[0],
    tower.axisY + exitTransitionOffset[1],
    exit.functionalClearanceStartZ,
  ];
  const exitTransitionEnd = [
    tower.axisX,
    exit.functionalClearanceEndY,
    exit.channelCenterZ,
  ];
  const exitMouth = [
    tower.axisX,
    exit.clearOuterY + halfDie + 1.0,
    exit.channelCenterZ,
  ];
  sampleSegment(
    'exit-ramp',
    exitTransitionStart,
    exitTransitionEnd,
    12,
    [0, 0, 0],
    'exit-ramp',
  );
  sampleSegment(
    'exit-channel',
    exitTransitionEnd,
    exitMouth,
    12,
    [0, 0, 0],
    'exit-channel',
  );

  const failures = tests.filter((test) => !test.passed);
  const categories = [...new Set(tests.map((test) => test.category))];
  const byCategory = Object.fromEntries(categories.map((category) => {
    const subset = tests.filter((test) => test.category === category);
    return [category, {
      count: subset.length,
      passed: subset.every((test) => test.passed),
      maximumIntersectionVolumeMm3: Math.max(
        ...subset.map((test) => test.intersectionVolumeMm3),
      ),
    }];
  }));
  const report = {
    geometryRevision: parameters.revision,
    testedFile: draftPath,
    dieEnvelopeMm: die.maximumEnvelope,
    method: 'oriented rigid 25 mm cube collision checks through the angled inlet, three staggered baffles, and rounded outlet channel',
    collisionLimitMm3,
    passed: failures.length === 0,
    totalPoses: tests.length,
    categorySummary: byCategory,
    failures,
    poses: tests,
    physicalTestStillRequired: true,
  };
  fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
  console.log(JSON.stringify(report, null, 2));
  if (failures.length > 0) process.exitCode = 2;
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
