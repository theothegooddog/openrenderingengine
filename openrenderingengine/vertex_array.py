import ctypes

from OpenGL import GL

from .vertex_buffer_layout import VertexBufferElement


class VertexArray:
    def __init__(self):
        self._id = GL.glGenVertexArrays(1)
        self.bind()

    def delete(self):
        GL.glDeleteVertexArrays(1, [self._id])

    def add_buffer(self, vb, layout):
        self.bind()
        vb.bind()
        offset = 0
        for i, element in enumerate(layout.elements):
            GL.glEnableVertexAttribArray(i)
            GL.glVertexAttribPointer(i, element.count, element.type, element.normalized,
                                     layout.stride, ctypes.c_void_p(offset))
            offset += element.count * VertexBufferElement.size_of_type(element.type)

    def bind(self):
        GL.glBindVertexArray(self._id)

    def unbind(self):
        GL.glBindVertexArray(0)
