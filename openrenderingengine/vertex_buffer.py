import numpy as np
from OpenGL import GL


class VertexBuffer:
    def __init__(self, data):
        self._id = GL.glGenBuffers(1)
        self.set_data(data)

    def delete(self):
        GL.glDeleteBuffers(1, [self._id])

    def bind(self):
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._id)

    def unbind(self):
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def set_data(self, data):
        data = np.ascontiguousarray(data, dtype=np.float32)
        self.bind()
        GL.glBufferData(GL.GL_ARRAY_BUFFER, data.nbytes, data, GL.GL_DYNAMIC_DRAW)
