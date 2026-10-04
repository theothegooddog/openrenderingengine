from dataclasses import dataclass

from OpenGL import GL

_SIZES = {
    GL.GL_FLOAT: 4,
    GL.GL_UNSIGNED_INT: 4,
    GL.GL_UNSIGNED_BYTE: 1,
}

_TYPES = {
    float: (GL.GL_FLOAT, GL.GL_FALSE),
    int: (GL.GL_UNSIGNED_INT, GL.GL_FALSE),
    bytes: (GL.GL_UNSIGNED_BYTE, GL.GL_TRUE),
}


@dataclass
class VertexBufferElement:
    type: int
    count: int
    normalized: bool

    @staticmethod
    def size_of_type(gl_type):
        return _SIZES.get(gl_type, 0)


class VertexBufferLayout:
    def __init__(self):
        self._elements = []
        self._stride = 0

    def push(self, py_type, count):
        """Push an attribute: `float` -> GL_FLOAT, `int` -> GL_UNSIGNED_INT, `bytes` -> GL_UNSIGNED_BYTE."""
        gl_type, normalized = _TYPES[py_type]
        self._elements.append(VertexBufferElement(gl_type, count, normalized))
        self._stride += VertexBufferElement.size_of_type(gl_type) * count

    @property
    def elements(self):
        return list(self._elements)

    @property
    def stride(self):
        return self._stride
