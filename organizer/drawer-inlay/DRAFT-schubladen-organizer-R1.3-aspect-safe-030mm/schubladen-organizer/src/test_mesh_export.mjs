import assert from 'node:assert/strict'
import test from 'node:test'

import { sanitizeMeshForFloat32 } from './mesh_export.mjs'

function mesh (vertices, faces) {
  return {
    numProp: 3,
    numVert: vertices.length,
    numTri: faces.length,
    vertProperties: Float64Array.from(vertices.flat()),
    triVerts: Uint32Array.from(faces.flat())
  }
}

test('Float32 export sanitation merges coincident vertices and cancels only an opposite internal face pair', () => {
  const input = mesh(
    [
      [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, -1],
      [0, 0, 0], [1, 0, 0], [0, 1, 0]
    ],
    [
      [0, 1, 3], [1, 2, 3], [2, 0, 3], [0, 2, 1],
      [5, 4, 6], [6, 4, 7], [7, 4, 5], [5, 6, 7]
    ]
  )
  const result = sanitizeMeshForFloat32(input)
  assert.equal(result.mesh.numVert, 5)
  assert.equal(result.mesh.numTri, 6)
  assert.equal(result.report.merged_float32_vertices, 3)
  assert.equal(result.report.canceled_opposite_face_pairs, 1)
  assert.equal(result.report.dropped_zero_area_triangles, 0)
})

test('Float32 export sanitation rejects same-orientation duplicate faces', () => {
  const input = mesh(
    [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
    [[0, 1, 2], [0, 1, 2]]
  )
  assert.throws(() => sanitizeMeshForFloat32(input), /ambiguous duplicate Float32 export face/)
})
