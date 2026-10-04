import numpy as np

from .index_buffer import IndexBuffer
from .vertex_array import VertexArray
from .vertex_buffer import VertexBuffer
from .vertex_buffer_layout import VertexBufferLayout


class Mesh:
    """Vertex data laid out as (x, y, z, u, v) per vertex, plus triangle indices.

    GPU buffers are created lazily on first draw so meshes can be built before a GL context exists.
    """

    def __init__(self, vertices, indices):
        self.vertices = np.asarray(vertices, dtype=np.float32).reshape(-1, 5)
        self.indices = np.asarray(indices, dtype=np.uint32).ravel()
        self._va = self._vb = self._ib = None

    def bind(self):
        if self._va is None:
            self._va = VertexArray()
            self._vb = VertexBuffer(self.vertices)
            self._ib = IndexBuffer(self.indices)
            layout = VertexBufferLayout()
            layout.push(float, 3)
            layout.push(float, 2)
            self._va.add_buffer(self._vb, layout)
        self._va.bind()
        self._ib.bind()

    @property
    def index_count(self):
        return self.indices.size

    def delete(self):
        if self._va is not None:
            self._va.delete()
            self._vb.delete()
            self._ib.delete()
            self._va = self._vb = self._ib = None


def cube(size=1.0):
    h = size / 2.0
    vertices = np.array([
        -0.5, -0.5, -0.5,  0.0, 0.0,
         0.5, -0.5, -0.5,  1.0, 0.0,
         0.5,  0.5, -0.5,  1.0, 1.0,
        -0.5,  0.5, -0.5,  0.0, 1.0,

        -0.5, -0.5,  0.5,  0.0, 0.0,
         0.5, -0.5,  0.5,  1.0, 0.0,
         0.5,  0.5,  0.5,  1.0, 1.0,
        -0.5,  0.5,  0.5,  0.0, 1.0,

        -0.5,  0.5,  0.5,  1.0, 0.0,
        -0.5,  0.5, -0.5,  1.0, 1.0,
        -0.5, -0.5, -0.5,  0.0, 1.0,
        -0.5, -0.5,  0.5,  0.0, 0.0,

         0.5,  0.5,  0.5,  1.0, 0.0,
         0.5,  0.5, -0.5,  1.0, 1.0,
         0.5, -0.5, -0.5,  0.0, 1.0,
         0.5, -0.5,  0.5,  0.0, 0.0,

        -0.5, -0.5, -0.5,  0.0, 1.0,
         0.5, -0.5, -0.5,  1.0, 1.0,
         0.5, -0.5,  0.5,  1.0, 0.0,
        -0.5, -0.5,  0.5,  0.0, 0.0,

        -0.5,  0.5, -0.5,  0.0, 1.0,
         0.5,  0.5, -0.5,  1.0, 1.0,
         0.5,  0.5,  0.5,  1.0, 0.0,
        -0.5,  0.5,  0.5,  0.0, 0.0,
    ], dtype=np.float32).reshape(-1, 5)
    vertices[:, :3] *= 2.0 * h
    indices = [
         0,  1,  2,  2,  3,  0,
         4,  5,  6,  6,  7,  4,
         8,  9, 10, 10, 11,  8,
        12, 13, 14, 14, 15, 12,
        16, 17, 18, 18, 19, 16,
        20, 21, 22, 22, 23, 20,
    ]
    return Mesh(vertices, indices)


def plane(size=1.0):
    h = size / 2.0
    vertices = [
        -h, 0.0,  h,  0.0, 0.0,
         h, 0.0,  h,  1.0, 0.0,
         h, 0.0, -h,  1.0, 1.0,
        -h, 0.0, -h,  0.0, 1.0,
    ]
    return Mesh(vertices, [0, 1, 2, 2, 3, 0])
