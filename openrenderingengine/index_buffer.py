import numpy as np
from OpenGL import GL


class IndexBuffer:
    def __init__(self, data):
        self._id = GL.glGenBuffers(1)
        self._count = 0
        self.set_data(data)

    def delete(self):
        GL.glDeleteBuffers(1, [self._id])

    def bind(self):
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self._id)

    def unbind(self):
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)

    @property
    def count(self):
        return self._count

    def set_data(self, data):
        data = np.ascontiguousarray(data, dtype=np.uint32)
        self._count = data.size
        self.bind()
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, data.nbytes, data, GL.GL_DYNAMIC_DRAW)
