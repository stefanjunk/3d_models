function faceOrientation (face, sorted) {
  const [a, b, c] = face
  const [x, y, z] = sorted
  return (
    (a === x && b === y && c === z) ||
    (a === y && b === z && c === x) ||
    (a === z && b === x && c === y)
  ) ? 1 : -1
}

function compactVertices (vertices, faces) {
  const used = new Set(faces.flat())
  const remap = new Map()
  const compacted = []
  for (const oldId of [...used].sort((left, right) => left - right)) {
    remap.set(oldId, compacted.length / 3)
    compacted.push(vertices[oldId * 3], vertices[oldId * 3 + 1], vertices[oldId * 3 + 2])
  }
  return {
    vertices: compacted,
    faces: faces.map(face => face.map(id => remap.get(id)))
  }
}

function assertClosedEdgeCounts (faces) {
  const counts = new Map()
  for (const [a, b, c] of faces) {
    for (const [left, right] of [[a, b], [b, c], [c, a]]) {
      const key = left < right ? `${left},${right}` : `${right},${left}`
      counts.set(key, (counts.get(key) ?? 0) + 1)
    }
  }
  const invalid = [...counts.entries()].filter(([, count]) => count !== 2)
  if (invalid.length > 0) {
    throw new Error(`Float32 export sanitation produced ${invalid.length} non-two-manifold edges`)
  }
}

export function sanitizeMeshForFloat32 (mesh) {
  if (!Number.isInteger(mesh.numVert) || !Number.isInteger(mesh.numTri) || mesh.numProp < 3) {
    throw new Error('invalid indexed mesh metadata')
  }
  if (mesh.vertProperties.length < mesh.numVert * mesh.numProp || mesh.triVerts.length < mesh.numTri * 3) {
    throw new Error('truncated indexed mesh arrays')
  }

  const vertexIds = new Map()
  const vertices = []
  const remap = new Uint32Array(mesh.numVert)
  for (let oldId = 0; oldId < mesh.numVert; oldId += 1) {
    const source = oldId * mesh.numProp
    const point = [
      Math.fround(mesh.vertProperties[source]),
      Math.fround(mesh.vertProperties[source + 1]),
      Math.fround(mesh.vertProperties[source + 2])
    ]
    if (!point.every(Number.isFinite)) throw new Error('non-finite Float32 export vertex')
    const key = point.join(',')
    let newId = vertexIds.get(key)
    if (newId === undefined) {
      newId = vertices.length / 3
      vertexIds.set(key, newId)
      vertices.push(...point)
    }
    remap[oldId] = newId
  }

  const faceGroups = new Map()
  let droppedZeroAreaTriangles = 0
  for (let triangle = 0; triangle < mesh.numTri; triangle += 1) {
    const face = [
      remap[mesh.triVerts[triangle * 3]],
      remap[mesh.triVerts[triangle * 3 + 1]],
      remap[mesh.triVerts[triangle * 3 + 2]]
    ]
    if (new Set(face).size !== 3) {
      droppedZeroAreaTriangles += 1
      continue
    }
    const sorted = [...face].sort((left, right) => left - right)
    const key = sorted.join(',')
    const group = faceGroups.get(key) ?? []
    group.push({ face, orientation: faceOrientation(face, sorted) })
    faceGroups.set(key, group)
  }

  const faces = []
  let canceledOppositeFacePairs = 0
  for (const [key, group] of faceGroups) {
    if (group.length === 1) {
      faces.push(group[0].face)
      continue
    }
    if (group.length === 2 && group[0].orientation === -group[1].orientation) {
      canceledOppositeFacePairs += 1
      continue
    }
    throw new Error(`ambiguous duplicate Float32 export face ${key} with ${group.length} occurrences`)
  }

  const compacted = compactVertices(vertices, faces)
  assertClosedEdgeCounts(compacted.faces)
  const vertProperties = Float32Array.from(compacted.vertices)
  const triVerts = Uint32Array.from(compacted.faces.flat())
  return {
    mesh: {
      numProp: 3,
      numVert: vertProperties.length / 3,
      numTri: triVerts.length / 3,
      vertProperties,
      triVerts
    },
    report: {
      policy: 'merge-exact-float32-vertices-and-cancel-exact-opposite-face-pairs-v1',
      source_vertices: mesh.numVert,
      manufacturing_vertices: vertProperties.length / 3,
      merged_float32_vertices: mesh.numVert - vertexIds.size,
      source_triangles: mesh.numTri,
      manufacturing_triangles: triVerts.length / 3,
      dropped_zero_area_triangles: droppedZeroAreaTriangles,
      canceled_opposite_face_pairs: canceledOppositeFacePairs
    }
  }
}
